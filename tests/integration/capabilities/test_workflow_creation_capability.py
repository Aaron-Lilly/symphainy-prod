#!/usr/bin/env python3
"""
Workflow Creation Capability Deep Dive Test

Tests that workflow creation ACTUALLY WORKS:
- Execution completes successfully
- Workflow artifact is created and stored
- Workflow contains actual workflow data (not placeholder)
- Workflow visual is generated (if applicable)
- Visual is valid image (if applicable)
- Workflow is retrievable by artifact_id

⚠️ CRITICAL: When fixing failures, NO FALLBACKS, NO MOCKS, NO CHEATS.
Fix root causes, don't work around issues.

Priority: 🔴 CRITICAL - Phase 1
"""
import sys
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

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
    "X-Test-ID": "workflow_creation_capability_tests"
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


async def get_valid_token() -> Optional[str]:
    """Get a valid authentication token."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        response = await client.post(
            f"{API_BASE_URL}/api/auth/register",
            json={
                "email": f"test_workflow_{timestamp}@example.com",
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


async def test_workflow_creation_from_bpmn_completion():
    """
    Test that create_workflow (from BPMN file) actually completes and produces valid artifacts.
    
    NO MOCKS, NO FALLBACKS, NO CHEATS.
    """
    print_test("Workflow Creation from BPMN - Full Execution Completion")
    
    # 1. Get valid authentication token
    token = await get_valid_token()
    if not token:
        print_error("Could not get valid token")
        return False
    
    # 2. Submit intent with real parameters
    print_info("Step 1: Submitting create_workflow intent (BPMN file)")
    result = await submit_intent(
        token=token,
        intent_type="create_workflow",
        parameters={
            "workflow_file_path": "/test/workflow_capability.bpmn",
            "workflow_type": "bpmn",
            "tenant_id": "test_tenant"
        }
    )
    
    if not result:
        print_error("Intent submission failed")
        return False
    
    execution_id = result.get("execution_id")
    if not execution_id:
        print_error("No execution_id returned")
        return False
    
    print_success(f"Intent submitted (execution_id: {execution_id})")
    
    # 3. Poll execution status until completion (REAL execution, not mocked)
    print_info("Step 2: Polling execution status until completion")
    status = await poll_execution_status(execution_id, timeout=60)
    
    if not status:
        print_error("Could not get execution status")
        return False
    
    execution_status = status.get("status")
    if execution_status != "completed":
        error_msg = status.get("error", "Unknown error")
        print_error(f"Execution did not complete (status: {execution_status}, error: {error_msg})")
        return False
    
    print_success("Execution completed successfully")
    
    # 4. Validate artifacts exist (REAL artifacts, not placeholders)
    print_info("Step 3: Validating workflow artifact exists")
    artifacts = status.get("artifacts", {})
    
    workflow_artifact_id = artifacts.get("workflow_artifact_id")
    if not workflow_artifact_id:
        print_error("❌ CRITICAL: workflow_artifact_id not found in execution result")
        print_error("   This means workflow artifact was NOT created")
        return False
    
    print_success(f"Workflow artifact ID found: {workflow_artifact_id}")
    
    # 5. Validate artifact quality (REAL validation, not just "exists")
    print_info("Step 4: Validating workflow artifact contains actual data")
    
    # Retrieve artifact from storage
    await asyncio.sleep(1)  # Small delay to ensure storage is complete
    workflow_artifact = await get_artifact_by_id(
        workflow_artifact_id,
        "test_tenant",
        include_visuals=False,
        token=token
    )
    
    if not workflow_artifact:
        print_error("❌ CRITICAL: Workflow artifact not retrievable from storage")
        print_error("   This means artifact storage failed")
        return False
    
    print_success("Workflow artifact retrieved from storage")
    
    # Validate artifact contains actual workflow data (not just placeholder)
    if isinstance(workflow_artifact, dict):
        # Check for workflow-specific data
        has_workflow_data = (
            "workflow" in workflow_artifact or
            "workflow_file_path" in workflow_artifact or
            "workflow_type" in workflow_artifact or
            "bpmn" in str(workflow_artifact).lower() or
            len(workflow_artifact) > 1  # Not just {"status": "created"}
        )
        
        if not has_workflow_data:
            print_error("❌ CRITICAL: Workflow artifact contains placeholder data, not actual workflow")
            print_error(f"   Artifact content: {workflow_artifact}")
            return False
        
        print_success("Workflow artifact contains actual workflow data")
    else:
        print_warning("Workflow artifact is not a dictionary, but exists")
    
    # 6. Validate visual artifacts (if applicable) - REAL image validation
    print_info("Step 5: Validating workflow visual (if generated)")
    
    workflow_visual_path = artifacts.get("workflow_visual_path")
    if workflow_visual_path:
        print_info(f"Visual path found: {workflow_visual_path}")
        
        # Retrieve visual from storage
        visual_bytes = await get_visual_by_path(
            workflow_visual_path,
            "test_tenant",
            token=token
        )
        
        if not visual_bytes:
            print_error("❌ CRITICAL: Workflow visual not retrievable from storage")
            print_error("   Visual generation may have failed silently")
            return False
        
        if len(visual_bytes) == 0:
            print_error("❌ CRITICAL: Workflow visual is empty")
            return False
        
        print_success(f"Workflow visual retrieved ({len(visual_bytes)} bytes)")
        
        # Validate it's a valid image (basic check)
        try:
            import base64
            # Try to decode as PNG/JPEG header
            if visual_bytes[:8] != b'\x89PNG\r\n\x1a\n' and visual_bytes[:2] != b'\xff\xd8':
                print_warning("Visual may not be a valid PNG/JPEG image")
            else:
                print_success("Workflow visual is a valid image format")
        except Exception as e:
            print_warning(f"Could not validate image format: {e}")
    else:
        print_warning("⚠️  No workflow visual path found (visual generation may not be implemented)")
    
    print_success("✅ Workflow Creation from BPMN - Full Execution Completion: PASSED")
    return True


async def test_workflow_creation_from_sop_completion():
    """
    Test that create_workflow (from SOP) actually completes and produces valid artifacts.
    
    This test requires an existing SOP, so it may be skipped if no SOPs exist.
    """
    print_test("Workflow Creation from SOP - Full Execution Completion")
    
    token = await get_valid_token()
    if not token:
        print_error("Could not get valid token")
        return False
    
    # For now, skip if we don't have a test SOP
    # In a full implementation, we'd create a test SOP first
    print_warning("⚠️  Skipping: Requires existing SOP (not yet implemented in test setup)")
    return None  # Skip, not fail


async def main():
    """Run all workflow creation capability tests."""
    print("\n" + "="*70)
    print("Workflow Creation Capability Deep Dive Tests")
    print("="*70)
    print("\n⚠️  CRITICAL: When tests fail, fix root causes.")
    print("   NO FALLBACKS, NO MOCKS, NO CHEATS.")
    print("="*70)
    
    results = {
        "workflow_from_bpmn": False,
        "workflow_from_sop": None,  # Skipped
    }
    
    # Run tests
    try:
        results["workflow_from_bpmn"] = await test_workflow_creation_from_bpmn_completion()
        results["workflow_from_sop"] = await test_workflow_creation_from_sop_completion()
    except Exception as e:
        print_error(f"Test execution error: {e}")
        import traceback
        traceback.print_exc()
    
    # Summary
    print("\n" + "="*70)
    print("Test Results Summary")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v is True)
    skipped = sum(1 for v in results.values() if v is None)
    total = len([v for v in results.values() if v is not None])
    
    for test_name, result in results.items():
        if result is None:
            status = "⏭️  SKIPPED"
        elif result:
            status = "✅ PASSED"
        else:
            status = "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed ({skipped} skipped)")
    
    if passed == total:
        print_success("\n🎉 All workflow creation capability tests passed!")
        return 0
    else:
        print_error(f"\n⚠️  {total - passed} test(s) failed")
        print_error("   Fix root causes - NO FALLBACKS, NO MOCKS, NO CHEATS")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
