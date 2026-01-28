"""
Test GenerateSOPFromChat Intent Service

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


class TestGenerateSOPFromChatParameters:
    """Test generate_sop_from_chat parameter validation."""
    
    def test_requires_parameters(self):
        """Should accept optional parameters."""
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        # sop_topic and initial_context are optional
        intent = IntentFactory.create_intent(
            intent_type="generate_sop_from_chat",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="operations_solution",
            parameters={
                "sop_topic": "Test SOP Topic"
            }
        )
        
        assert intent.intent_type == "generate_sop_from_chat"
        assert intent.parameters.get("sop_topic") == "Test SOP Topic"


class TestGenerateSOPFromChatExecution:
    """Test generate_sop_from_chat execution."""
    
    @pytest.mark.asyncio
    async def test_executes_successfully(
        self, operations_solution, execution_context
    ):
        """Should execute service successfully."""
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        intent = IntentFactory.create_intent(
            intent_type="generate_sop_from_chat",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="operations_solution",
            parameters={
                "sop_topic": "New Process Documentation"
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
            intent_type="generate_sop_from_chat",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="operations_solution",
            parameters={
                "sop_topic": "Quality Assurance Process"
            }
        )
        
        result = await operations_solution.handle_intent(intent, execution_context)
        
        # Services return artifacts containing chat session info
        assert "artifacts" in result
        assert "session" in result["artifacts"]
