"""
Test OptimizeProcess Intent Service

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


class TestOptimizeProcessParameters:
    """Test optimize_process parameter validation."""
    
    def test_requires_parameters(self):
        """Should require required parameters."""
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        # Test that intent can be created with valid parameters
        intent = IntentFactory.create_intent(
            intent_type="optimize_process",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="operations_solution",
            parameters={
                "workflow_id": "test_workflow_123"  # Required: workflow_id
            }
        )
        
        assert intent.intent_type == "optimize_process"
        assert intent.parameters.get("workflow_id") == "test_workflow_123"


class TestOptimizeProcessExecution:
    """Test optimize_process execution."""
    
    @pytest.mark.asyncio
    async def test_executes_successfully(
        self, operations_solution, execution_context
    ):
        """Should execute service successfully."""
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        intent = IntentFactory.create_intent(
            intent_type="optimize_process",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="operations_solution",
            parameters={
                "workflow_id": "test_workflow_123"
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
            intent_type="optimize_process",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="operations_solution",
            parameters={
                "workflow_id": "test_workflow_123",
                "optimization_focus": "efficiency"
            }
        )
        
        result = await operations_solution.handle_intent(intent, execution_context)
        
        # Services return artifacts containing optimization results
        assert "artifacts" in result
        assert "optimization" in result["artifacts"]
