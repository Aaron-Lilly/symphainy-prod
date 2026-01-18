#!/usr/bin/env python3
"""
Materialization Policy + Artifact Storage Integration Tests

Tests that materialization policy evaluation leads to actual artifact storage
in GCS/Supabase. This validates the complete flow:
1. Policy evaluation (PERSIST/DISCARD)
2. Artifact storage when policy=PERSIST
3. Artifact retrieval by artifact_id
4. MVP override behavior

Priority: 🔴 CRITICAL - Validates materialization policy → storage integration
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
    verify_artifact_stored,
    validate_image_base64
)


# Test Configuration
API_BASE_URL = "http://localhost:8001"
RUNTIME_BASE_URL = "http://localhost:8000"

# Test mode headers
TEST_HEADERS = {
    "X-Test-Mode": "true",
    "X-Test-ID": "materialization_policy_integration_tests"
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
                "email": f"test_matpol_{timestamp}@example.com",
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
    timeout: int = 30,
    poll_interval: float = 1.0
) -> Optional[Dict[str, Any]]:
    """
    Poll execution status until completion or timeout.
    
    Returns execution status when completed, failed, or timeout.
    """
    start_time = datetime.now()
    
    while True:
        status = await get_execution_status(execution_id, tenant_id)
        
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


async def test_mvp_override_workflow_persist():
    """
    Test that MVP override (PERSIST) stores workflow artifacts.
    
    This validates:
    1. Materialization policy evaluates to PERSIST (MVP override)
    2. Artifact is stored in GCS/Supabase
    3. artifact_id is returned in execution result
    4. Artifact is retrievable by artifact_id
    """
    print_test("MVP Override - Workflow Artifact Persistence")
    
    token = await get_valid_token()
    if not token:
        print_error("Could not get valid token")
        return False
    
    # Step 1: Submit workflow creation intent
    print_info("Step 1: Submitting create_workflow intent")
    result = await submit_intent(
        token=token,
        intent_type="create_workflow",
        parameters={
            "workflow_file_path": "/test/workflow_matpol.bpmn",
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
    
    # Step 2: Poll until completion
    print_info("Step 2: Polling execution status until completion")
    status = await poll_execution_status(execution_id, timeout=30)
    
    if not status:
        print_error("Could not get execution status")
        return False
    
    if status.get("status") != "completed":
        print_warning(f"Execution not completed (status: {status.get('status')})")
        return False
    
    print_success("Execution completed successfully")
    
    # Step 3: Verify artifact_id is present (indicates policy=PERSIST and storage occurred)
    print_info("Step 3: Verifying artifact_id reference (policy evaluation → storage)")
    artifacts = status.get("artifacts", {})
    workflow_artifact_id = artifacts.get("workflow_artifact_id")
    
    if not workflow_artifact_id:
        print_error("❌ CRITICAL: workflow_artifact_id not found!")
        print_error("   This means materialization policy did NOT store the artifact")
        print_error("   Expected: MVP override should make workflow artifacts PERSIST")
        return False
    
    print_success(f"✅ Artifact stored (artifact_id: {workflow_artifact_id})")
    print_info("   Materialization policy evaluated to PERSIST and storage occurred")
    
    # Step 4: Verify artifact is retrievable from storage
    print_info("Step 4: Verifying artifact is retrievable from GCS/Supabase")
    await asyncio.sleep(1)  # Small delay to ensure storage is complete
    
    retrieved_artifact = await get_artifact_by_id(
        workflow_artifact_id,
        "test_tenant",
        include_visuals=False,
        token=token
    )
    
    if not retrieved_artifact:
        print_error("❌ CRITICAL: Artifact not retrievable by artifact_id!")
        print_error("   This means storage to GCS/Supabase failed")
        return False
    
    print_success("✅ Artifact retrieved successfully from storage")
    print_info("   Storage integration (GCS + Supabase) working correctly")
    
    # Step 5: Validate artifact structure
    print_info("Step 5: Validating artifact structure")
    if isinstance(retrieved_artifact, dict):
        # Check for structured format (semantic_payload + renderings)
        if "semantic_payload" in retrieved_artifact or "renderings" in retrieved_artifact:
            print_success("✅ Artifact has structured format")
        elif "workflow" in retrieved_artifact or "workflow_file_path" in retrieved_artifact:
            print_success("✅ Artifact has workflow data")
        else:
            print_warning("⚠️  Artifact structure unexpected, but artifact exists")
    
    print_success("✅ MVP Override - Workflow Artifact Persistence: PASSED")
    return True


async def test_materialization_policy_end_to_end():
    """
    Test complete end-to-end flow: Policy Evaluation → Storage → Retrieval.
    
    This validates the entire materialization policy integration:
    1. Intent execution generates artifacts
    2. Materialization policy evaluates (PERSIST/DISCARD)
    3. Artifacts stored when policy=PERSIST
    4. Artifacts retrievable by artifact_id
    5. Artifact structure is correct
    """
    print_test("Materialization Policy - End-to-End Integration")
    
    token = await get_valid_token()
    if not token:
        print_error("Could not get valid token")
        return False
    
    # Step 1: Submit intent
    print_info("Step 1: Submitting intent")
    result = await submit_intent(
        token=token,
        intent_type="create_workflow",
        parameters={
            "workflow_file_path": "/test/workflow_e2e.bpmn",
            "workflow_type": "bpmn",
            "tenant_id": "test_tenant"
        }
    )
    
    if not result or not result.get("execution_id"):
        print_error("Intent submission failed")
        return False
    
    execution_id = result.get("execution_id")
    print_success(f"Intent submitted (execution_id: {execution_id})")
    
    # Step 2: Wait for completion
    print_info("Step 2: Waiting for execution completion")
    status = await poll_execution_status(execution_id, timeout=30)
    
    if not status or status.get("status") != "completed":
        print_warning("Execution did not complete")
        return False
    
    print_success("Execution completed")
    
    # Step 3: Verify policy evaluation occurred (artifact_id present = PERSIST)
    print_info("Step 3: Verifying materialization policy evaluation")
    artifacts = status.get("artifacts", {})
    workflow_artifact_id = artifacts.get("workflow_artifact_id")
    
    if not workflow_artifact_id:
        print_error("❌ Materialization policy did NOT store artifact!")
        print_error("   Expected: MVP override should make workflow PERSIST")
        return False
    
    print_success("✅ Materialization policy evaluated to PERSIST")
    print_info(f"   artifact_id: {workflow_artifact_id}")
    
    # Step 4: Verify storage occurred (artifact retrievable)
    print_info("Step 4: Verifying artifact storage in GCS/Supabase")
    await asyncio.sleep(1)
    
    stored = await verify_artifact_stored(workflow_artifact_id, "test_tenant", token)
    if not stored:
        print_error("❌ Artifact storage verification failed!")
        return False
    
    print_success("✅ Artifact stored in GCS/Supabase")
    
    # Step 5: Verify retrieval works
    print_info("Step 5: Verifying artifact retrieval")
    retrieved = await get_artifact_by_id(
        workflow_artifact_id,
        "test_tenant",
        include_visuals=False,
        token=token
    )
    
    if not retrieved:
        print_error("❌ Artifact retrieval failed!")
        return False
    
    print_success("✅ Artifact retrieved successfully")
    
    # Step 6: Validate artifact structure
    print_info("Step 6: Validating artifact structure")
    if isinstance(retrieved, dict) and (len(retrieved) > 0):
        print_success("✅ Artifact structure valid")
    else:
        print_warning("⚠️  Artifact structure unexpected")
    
    print_success("✅ Materialization Policy - End-to-End Integration: PASSED")
    return True


async def main():
    """Run all materialization policy integration tests."""
    print("\n" + "="*70)
    print("Materialization Policy + Artifact Storage Integration Tests")
    print("="*70)
    
    results = {
        "mvp_override_workflow": False,
        "end_to_end": False,
    }
    
    # Run tests
    try:
        results["mvp_override_workflow"] = await test_mvp_override_workflow_persist()
        results["end_to_end"] = await test_materialization_policy_end_to_end()
    except Exception as e:
        print_error(f"Test execution error: {e}")
        import traceback
        traceback.print_exc()
    
    # Summary
    print("\n" + "="*70)
    print("Test Results Summary")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print_success("\n🎉 All materialization policy integration tests passed!")
        return 0
    else:
        print_error(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
