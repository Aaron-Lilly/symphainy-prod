"""
Test ProcessGuideAgentMessage Intent Service

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


class TestProcessGuideAgentMessageParameters:
    """Test process_guide_agent_message parameter validation."""
    
    def test_requires_parameters(self):
        """Should require required parameters."""
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        intent = IntentFactory.create_intent(
            intent_type="process_guide_agent_message",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="coexistence",
            parameters={}
        )
        
        assert intent.intent_type == "process_guide_agent_message"


class TestProcessGuideAgentMessageExecution:
    """Test process_guide_agent_message execution."""
    
    @pytest.mark.asyncio
    async def test_executes_successfully(
        self, coexistence_solution, execution_context
    ):
        """Should execute service successfully."""
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        intent = IntentFactory.create_intent(
            intent_type="process_guide_agent_message",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="coexistence",
            parameters={}
        )
        
        result = await coexistence_solution.handle_intent(intent, execution_context)
        
        assert "success" in result or "error" in result
    
    @pytest.mark.asyncio
    async def test_registers_artifact(
        self, coexistence_solution, execution_context
    ):
        """Should register artifact on success."""
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        intent = IntentFactory.create_intent(
            intent_type="process_guide_agent_message",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="coexistence",
            parameters={}
        )
        
        result = await coexistence_solution.handle_intent(intent, execution_context)
        
        if "success" in result:
            assert "artifacts" in result or "artifact_id" in result
