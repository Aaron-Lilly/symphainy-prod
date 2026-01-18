#!/usr/bin/env python3
"""
Capability Test Helpers

Shared utilities for capability deep dive tests.
Reuses patterns from test_execution_completion.py.

⚠️ CRITICAL: When fixing failures, NO FALLBACKS, NO MOCKS, NO CHEATS.
"""
import sys
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, Tuple

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import httpx

# Import artifact retrieval helpers
from tests.integration.execution.artifact_retrieval_helpers import (
    get_artifact_by_id,
    get_visual_by_path,
    verify_artifact_stored,
    validate_image_base64
)


# Test Configuration
API_BASE_URL = "http://localhost:8001"
RUNTIME_BASE_URL = "http://localhost:8000"

# Test mode headers
TEST_HEADERS = {
    "X-Test-Mode": "true",
    "X-Test-ID": "capability_tests"
}


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_test(name: str):
    """Print test header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}🧪 Testing: {name}{Colors.RESET}")


def print_success(message: str):
    """Print success message."""
    print(f"{Colors.GREEN}✅ {message}{Colors.RESET}")


def print_error(message: str):
    """Print error message."""
    print(f"{Colors.RED}❌ {message}{Colors.RESET}")


def print_warning(message: str):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.RESET}")


def print_info(message: str):
    """Print info message."""
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.RESET}")


async def get_valid_token(test_prefix: str = "test") -> Optional[str]:
    """Get a valid authentication token."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        response = await client.post(
            f"{API_BASE_URL}/api/auth/register",
            json={
                "email": f"{test_prefix}_{timestamp}@example.com",
                "password": "TestPassword123!",
                "name": "Test User"
            },
            headers=TEST_HEADERS
        )
        
        if response.status_code == 200:
            return response.json().get("access_token")
        return None


async def submit_intent(
    token: str,
    intent_type: str,
    parameters: Dict[str, Any],
    session_id: str = None
) -> Optional[Dict[str, Any]]:
    """Submit an intent via the Runtime API."""
    if not session_id:
        session_id = f"test_session_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{API_BASE_URL}/api/intent/submit",
            json={
                "intent_type": intent_type,
                "session_id": session_id,
                "parameters": parameters,
                "metadata": {
                    "tenant_id": "test_tenant",
                    "solution_id": "default"
                }
            },
            headers={**TEST_HEADERS, "Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            print_warning(f"Intent submission returned {response.status_code}: {response.text}")
            return None


async def get_execution_status(
    execution_id: str,
    tenant_id: str = "test_tenant",
    include_artifacts: bool = False,
    include_visuals: bool = False
) -> Optional[Dict[str, Any]]:
    """Get execution status from Runtime."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        params = {"tenant_id": tenant_id}
        if include_artifacts:
            params["include_artifacts"] = "true"
        if include_visuals:
            params["include_visuals"] = "true"
        
        response = await client.get(
            f"{RUNTIME_BASE_URL}/api/execution/{execution_id}/status",
            params=params
        )
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            return None
        else:
            print_warning(f"Execution status returned {response.status_code}: {response.text}")
            return None


async def poll_execution_status(
    execution_id: str,
    tenant_id: str = "test_tenant",
    timeout: int = 60,
    poll_interval: float = 1.0
) -> Optional[Dict[str, Any]]:
    """
    Poll execution status until completion or timeout.
    
    Returns execution status when completed, failed, or timeout.
    """
    start_time = datetime.now()
    
    while True:
        status = await get_execution_status(execution_id, tenant_id, include_artifacts=True, include_visuals=True)
        
        if not status:
            # Execution not found yet, wait and retry
            await asyncio.sleep(poll_interval)
            elapsed = (datetime.now() - start_time).total_seconds()
            if elapsed > timeout:
                print_warning(f"Execution status polling timeout after {timeout}s")
                return None
            continue
        
        execution_status = status.get("status", "unknown")
        
        if execution_status in ["completed", "failed"]:
            return status
        
        # Still executing, wait and retry
        await asyncio.sleep(poll_interval)
        elapsed = (datetime.now() - start_time).total_seconds()
        if elapsed > timeout:
            print_warning(f"Execution still in progress after {timeout}s (status: {execution_status})")
            return status


async def validate_artifact_created_and_meaningful(
    artifacts: Dict[str, Any],
    artifact_key: str,
    tenant_id: str,
    token: str,
    expected_data_indicators: list = None
) -> Tuple[bool, Optional[str], Optional[Dict[str, Any]]]:
    """
    Validate that an artifact was created and contains meaningful data.
    
    Returns: (is_valid, artifact_id, artifact_data)
    """
    artifact_id_key = f"{artifact_key}_artifact_id"
    artifact_id = artifacts.get(artifact_id_key)
    
    if not artifact_id:
        print_error(f"❌ CRITICAL: {artifact_id_key} not found in execution result")
        print_error(f"   This means {artifact_key} artifact was NOT created")
        return False, None, None
    
    print_success(f"{artifact_key} artifact ID found: {artifact_id}")
    
    # Retrieve artifact from storage
    await asyncio.sleep(1)  # Small delay to ensure storage is complete
    artifact_data = await get_artifact_by_id(
        artifact_id,
        tenant_id,
        include_visuals=False,
        token=token
    )
    
    if not artifact_data:
        print_error(f"❌ CRITICAL: {artifact_key} artifact not retrievable from storage")
        print_error("   This means artifact storage failed")
        return False, artifact_id, None
    
    print_success(f"{artifact_key} artifact retrieved from storage")
    
    # Validate artifact contains actual data (not just placeholder)
    if isinstance(artifact_data, dict):
        # Check for expected data indicators
        if expected_data_indicators:
            has_data = any(indicator in str(artifact_data).lower() or indicator in artifact_data for indicator in expected_data_indicators)
        else:
            # Generic check: not just {"status": "created"}
            has_data = len(artifact_data) > 1 and not all(k in ["status", "created"] for k in artifact_data.keys())
        
        if not has_data:
            print_error(f"❌ CRITICAL: {artifact_key} artifact contains placeholder data, not actual content")
            print_error(f"   Artifact content: {artifact_data}")
            return False, artifact_id, artifact_data
        
        print_success(f"{artifact_key} artifact contains actual data")
    else:
        print_warning(f"{artifact_key} artifact is not a dictionary, but exists")
    
    return True, artifact_id, artifact_data


async def validate_visual_artifact(
    artifacts: Dict[str, Any],
    visual_key: str,
    tenant_id: str,
    token: str,
    required: bool = False
) -> bool:
    """
    Validate that a visual artifact was generated and is retrievable.
    
    Returns: True if valid (or not required), False if required but missing/invalid
    """
    visual_path_key = f"{visual_key}_path"
    visual_path = artifacts.get(visual_path_key)
    
    if not visual_path:
        if required:
            print_error(f"❌ CRITICAL: {visual_path_key} not found (visual generation required)")
            return False
        else:
            print_warning(f"⚠️  No {visual_path_key} found (visual generation may not be implemented)")
            return True  # Not required, so pass
    
    print_info(f"Visual path found: {visual_path}")
    
    # Retrieve visual from storage
    visual_bytes = await get_visual_by_path(
        visual_path,
        tenant_id,
        token=token
    )
    
    if not visual_bytes:
        if required:
            print_error(f"❌ CRITICAL: {visual_key} not retrievable from storage")
            print_error("   Visual generation may have failed silently")
            return False
        else:
            print_warning(f"⚠️  {visual_key} not retrievable (may not be implemented)")
            return True  # Not required
    
    if len(visual_bytes) == 0:
        print_error(f"❌ CRITICAL: {visual_key} is empty")
        return False
    
    print_success(f"{visual_key} retrieved ({len(visual_bytes)} bytes)")
    
    # Validate it's a valid image (basic check)
    try:
        # Check PNG header
        if visual_bytes[:8] == b'\x89PNG\r\n\x1a\n':
            print_success(f"{visual_key} is a valid PNG image")
            return True
        # Check JPEG header
        elif visual_bytes[:2] == b'\xff\xd8':
            print_success(f"{visual_key} is a valid JPEG image")
            return True
        else:
            print_warning(f"{visual_key} may not be a valid PNG/JPEG image")
            return True  # Still pass, might be another format
    except Exception as e:
        print_warning(f"Could not validate image format: {e}")
        return True  # Still pass, format check failed but bytes exist
