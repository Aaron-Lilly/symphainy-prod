#!/usr/bin/env python3
"""
Visual Generation Capability Deep Dive Test

Tests that visual generation ACTUALLY WORKS:
- Execution completes successfully
- Artifact is created and stored
- Artifact contains actual data (not placeholder)
- Visual is generated (if applicable)
- Visual is valid image (if applicable)
- Artifact is retrievable by artifact_id

⚠️ CRITICAL: When fixing failures, NO FALLBACKS, NO MOCKS, NO CHEATS.
Fix root causes, don't work around issues.

Priority: 🔴 CRITICAL - Phase 1
"""
import sys
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import shared helpers
from tests.integration.capabilities.capability_test_helpers import (
    get_valid_token,
    submit_intent,
    poll_execution_status,
    validate_artifact_created_and_meaningful,
    validate_visual_artifact,
    print_test,
    print_success,
    print_error,
    print_warning,
    print_info
)


async def test_create_workflow_completion():
    """
    Test that create_workflow actually completes and produces valid artifacts.
    
    NO MOCKS, NO FALLBACKS, NO CHEATS.
    """
    print_test("Visual Generation - Full Execution Completion")
    
    # 1. Get valid authentication token
    token = await get_valid_token("create")
    if not token:
        print_error("Could not get valid token")
        return False
    
    # 2. Submit intent with real parameters
    print_info("Step 1: Submitting create_workflow intent")
    result = await submit_intent(
        token=token,
        intent_type="create_workflow",
        parameters={'workflow_file_path': '/test/workflow_visual.bpmn', 'workflow_type': 'bpmn', 'tenant_id': 'test_tenant'}
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
    
    # 4. Validate artifacts exist and are meaningful
    print_info("Step 3: Validating workflow artifact exists and contains actual data")
    artifacts = status.get("artifacts", {})
    
    is_valid, artifact_id, artifact_data = await validate_artifact_created_and_meaningful(
        artifacts,
        "workflow",
        "test_tenant",
        token,
        expected_data_indicators=['workflow', 'bpmn']
    )
    
    if not is_valid:
        return False
    
    # 5. Validate visual artifacts (if applicable)
    visual_key = "workflow_visual"
    print_info(f"Step 4: Validating {visual_key} (if generated)")
    
    visual_valid = await validate_visual_artifact(
        artifacts,
        visual_key,
        "test_tenant",
        token,
        required=False  # Visuals may not be implemented for all capabilities
    )
    
    if not visual_valid:
        return False
    
    print_success("✅ Visual Generation - Full Execution Completion: PASSED")
    return True


async def main():
    """Run all visual generation capability tests."""
    print("\n" + "="*70)
    print("Visual Generation Capability Deep Dive Tests")
    print("="*70)
    print("\n⚠️  CRITICAL: When tests fail, fix root causes.")
    print("   NO FALLBACKS, NO MOCKS, NO CHEATS.")
    print("="*70)
    
    results = {
        "create_workflow": False,
    }
    
    # Run tests
    try:
        results["create_workflow"] = await test_create_workflow_completion()
    except Exception as e:
        print_error(f"Test execution error: {e}")
        import traceback
        traceback.print_exc()
    
    # Summary
    print("\n" + "="*70)
    print("Test Results Summary")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v is True)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print_success("\n🎉 All visual generation capability tests passed!")
        return 0
    else:
        print_error(f"\n⚠️  {total - passed} test(s) failed")
        print_error("   Fix root causes - NO FALLBACKS, NO MOCKS, NO CHEATS")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
