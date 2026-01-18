"""
Artifact Retrieval Helper Functions

Helper functions for retrieving and validating artifacts and visuals in tests.
"""

import sys
import base64
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import httpx

# Test Configuration
RUNTIME_BASE_URL = "http://localhost:8000"
API_BASE_URL = "http://localhost:8001"

TEST_HEADERS = {
    "X-Test-Mode": "true",
    "X-Test-ID": "artifact_retrieval_tests"
}


async def get_artifact_by_id(
    artifact_id: str,
    tenant_id: str = "test_tenant",
    include_visuals: bool = False,
    token: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Retrieve artifact by ID from Runtime API.
    
    Args:
        artifact_id: Artifact ID
        tenant_id: Tenant ID
        include_visuals: If True, include full visual images
        token: Optional authentication token
    
    Returns:
        Optional[Dict]: Artifact data or None if not found
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        headers = {**TEST_HEADERS}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        response = await client.get(
            f"{RUNTIME_BASE_URL}/api/artifacts/{artifact_id}",
            params={
                "tenant_id": tenant_id,
                "include_visuals": str(include_visuals).lower()
            },
            headers=headers
        )
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return None
        else:
            print(f"⚠️ Artifact retrieval returned {response.status_code}: {response.text}")
            return None


async def get_visual_by_path(
    visual_path: str,
    tenant_id: str = "test_tenant",
    token: Optional[str] = None
) -> Optional[bytes]:
    """
    Retrieve visual image by storage path from Runtime API.
    
    Args:
        visual_path: GCS storage path of the visual
        tenant_id: Tenant ID
        token: Optional authentication token
    
    Returns:
        Optional[bytes]: Visual image bytes or None if not found
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        headers = {**TEST_HEADERS}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        response = await client.get(
            f"{RUNTIME_BASE_URL}/api/artifacts/visual/{visual_path}",
            params={"tenant_id": tenant_id},
            headers=headers
        )
        
        if response.status_code == 200:
            return response.content
        elif response.status_code == 404:
            return None
        else:
            print(f"⚠️ Visual retrieval returned {response.status_code}: {response.text}")
            return None


async def get_visual_base64_by_path(
    visual_path: str,
    tenant_id: str = "test_tenant",
    token: Optional[str] = None
) -> Optional[str]:
    """
    Retrieve visual image by storage path and return as base64 string.
    
    Args:
        visual_path: GCS storage path of the visual
        tenant_id: Tenant ID
        token: Optional authentication token
    
    Returns:
        Optional[str]: Base64-encoded image string or None if not found
    """
    visual_bytes = await get_visual_by_path(visual_path, tenant_id, token)
    if visual_bytes:
        return base64.b64encode(visual_bytes).decode()
    return None


def extract_artifact_id_from_execution_result(
    execution_result: Dict[str, Any],
    artifact_key: str
) -> Optional[str]:
    """
    Extract artifact_id from execution result.
    
    After materialization policy evaluation, artifacts have artifact_id references:
    - artifacts["workflow_artifact_id"] = "..."
    - artifacts["workflow_storage_path"] = "..."
    
    Args:
        execution_result: Execution result with artifacts
        artifact_key: Key of the artifact (e.g., "workflow", "sop")
    
    Returns:
        Optional[str]: Artifact ID or None if not found
    """
    artifacts = execution_result.get("artifacts", {})
    artifact_id_key = f"{artifact_key}_artifact_id"
    return artifacts.get(artifact_id_key)


def extract_storage_path_from_execution_result(
    execution_result: Dict[str, Any],
    artifact_key: str
) -> Optional[str]:
    """
    Extract storage_path from execution result.
    
    Args:
        execution_result: Execution result with artifacts
        artifact_key: Key of the artifact (e.g., "workflow", "sop")
    
    Returns:
        Optional[str]: Storage path or None if not found
    """
    artifacts = execution_result.get("artifacts", {})
    storage_path_key = f"{artifact_key}_storage_path"
    return artifacts.get(storage_path_key)


def extract_visual_path_from_artifact(
    artifact: Dict[str, Any],
    visual_key: str = "workflow_visual"
) -> Optional[str]:
    """
    Extract visual storage path from artifact.
    
    For structured artifacts, visuals are in renderings:
    - artifact["renderings"]["workflow_visual"]["storage_path"]
    
    For legacy artifacts, visuals are at top level:
    - artifact["workflow_visual"]["storage_path"]
    
    Args:
        artifact: Artifact dictionary
        visual_key: Key of the visual (e.g., "workflow_visual", "sop_visual")
    
    Returns:
        Optional[str]: Visual storage path or None if not found
    """
    # Try structured format first (renderings)
    if "renderings" in artifact:
        renderings = artifact["renderings"]
        if visual_key in renderings:
            visual = renderings[visual_key]
            if isinstance(visual, dict) and "storage_path" in visual:
                return visual["storage_path"]
    
    # Try legacy format (top level)
    if visual_key in artifact:
        visual = artifact[visual_key]
        if isinstance(visual, dict) and "storage_path" in visual:
            return visual["storage_path"]
    
    return None


async def verify_artifact_stored(
    artifact_id: str,
    tenant_id: str = "test_tenant",
    token: Optional[str] = None
) -> bool:
    """
    Verify that artifact is stored and retrievable.
    
    Args:
        artifact_id: Artifact ID
        tenant_id: Tenant ID
        token: Optional authentication token
    
    Returns:
        bool: True if artifact is stored and retrievable
    """
    artifact = await get_artifact_by_id(artifact_id, tenant_id, False, token)
    return artifact is not None


async def verify_visual_stored(
    visual_path: str,
    tenant_id: str = "test_tenant",
    token: Optional[str] = None
) -> bool:
    """
    Verify that visual is stored and retrievable.
    
    Args:
        visual_path: Visual storage path
        tenant_id: Tenant ID
        token: Optional authentication token
    
    Returns:
        bool: True if visual is stored and retrievable
    """
    visual = await get_visual_by_path(visual_path, tenant_id, token)
    return visual is not None


def validate_image_base64(image_base64: str) -> bool:
    """
    Validate that a base64 string is a valid image.
    
    Args:
        image_base64: Base64-encoded image string
    
    Returns:
        bool: True if valid image
    """
    try:
        # Decode base64
        image_bytes = base64.b64decode(image_base64)
        
        # Check PNG header
        if image_bytes[:8] == b'\x89PNG\r\n\x1a\n':
            return True
        
        # Check JPEG header
        if image_bytes[:2] == b'\xff\xd8':
            return True
        
        return False
    except Exception:
        return False
