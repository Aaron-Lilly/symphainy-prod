"""
Test CreateWorkflow Intent Service

Tests:
- Parameter validation
- Service execution
- Artifact registration
- Event emission
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class TestCreateWorkflowParameters:
    """Test create_workflow parameter validation."""
    
    def test_requires_parameters(self):
        """Should require required parameters."""
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        # Test that intent can be created with valid parameters
        intent = IntentFactory.create_intent(
            intent_type="create_workflow",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="operations_solution",
            parameters={
                "sop_id": "test_sop_123"  # Required: one of sop_id, bpmn_file_id, or workflow_spec
            }
        )
        
        assert intent.intent_type == "create_workflow"
        assert intent.parameters.get("sop_id") == "test_sop_123"


class TestCreateWorkflowExecution:
    """Test create_workflow execution."""
    
    @pytest.mark.asyncio
    async def test_executes_successfully(
        self, operations_solution, execution_context
    ):
        """Should execute service successfully."""
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        intent = IntentFactory.create_intent(
            intent_type="create_workflow",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="operations_solution",
            parameters={
                "sop_id": "test_sop_123"  # Required: one of sop_id, bpmn_file_id, or workflow_spec
            }
        )
        
        result = await operations_solution.handle_intent(intent, execution_context)
        
        # Services return artifacts and events, not success
        assert "artifacts" in result
        assert "events" in result
    
    @pytest.mark.asyncio
    async def test_registers_artifact(
        self, operations_solution, execution_context
    ):
        """Should register artifact on success."""
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        intent = IntentFactory.create_intent(
            intent_type="create_workflow",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="operations_solution",
            parameters={
                "workflow_spec": {
                    "name": "Test Workflow",
                    "steps": [
                        {"step_id": "1", "name": "Step 1"},
                        {"step_id": "2", "name": "Step 2"}
                    ]
                }
            }
        )
        
        result = await operations_solution.handle_intent(intent, execution_context)
        
        # Services return artifacts containing the workflow
        assert "artifacts" in result
        assert "workflow" in result["artifacts"]
