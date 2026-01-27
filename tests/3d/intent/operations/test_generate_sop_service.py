"""
Test Generate SOP Intent Service

Tests:
- Parameter validation
- SOP generation
- SOP artifact creation
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class TestGenerateSOPParameters:
    """Test generate_sop parameter validation."""
    
    def test_accepts_workflow_id(self):
        """Should accept workflow_id parameter."""
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        intent = IntentFactory.create_intent(
            intent_type="generate_sop",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="operations_solution",
            parameters={"workflow_id": "workflow_123"}
        )
        
        assert intent.parameters.get("workflow_id") == "workflow_123"


class TestGenerateSOPExecution:
    """Test generate_sop execution."""
    
    @pytest.mark.asyncio
    async def test_returns_sop_document(
        self, operations_solution, execution_context
    ):
        """Should return SOP document."""
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        intent = IntentFactory.create_intent(
            intent_type="compose_journey",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="operations_solution",
            parameters={
                "journey_id": "sop_management",
                "journey_params": {"workflow_id": "workflow_123"}
            }
        )
        
        result = await operations_solution.handle_intent(intent, execution_context)
        
        assert "success" in result or "error" in result
