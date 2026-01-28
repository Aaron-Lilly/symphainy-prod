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
        """Should require message parameter."""
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        intent = IntentFactory.create_intent(
            intent_type="process_guide_agent_message",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="coexistence",
            parameters={
                "message": "What can this platform do?",
                "chat_session_id": "chat_test_session"
            }
        )
        
        assert intent.intent_type == "process_guide_agent_message"
        assert intent.parameters.get("message") == "What can this platform do?"


class TestProcessGuideAgentMessageExecution:
    """Test process_guide_agent_message execution."""
    
    @pytest.mark.asyncio
    async def test_executes_successfully(
        self, coexistence_solution, execution_context
    ):
        """Should execute service successfully after initiating guide agent."""
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        # First, initiate the guide agent to create a chat session
        init_intent = IntentFactory.create_intent(
            intent_type="initiate_guide_agent",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="coexistence",
            parameters={
                "chat_session_id": "chat_test_session_msg_1"
            }
        )
        
        init_result = await coexistence_solution.handle_intent(init_intent, execution_context)
        assert "artifacts" in init_result
        
        # Now process a message in that session
        message_intent = IntentFactory.create_intent(
            intent_type="process_guide_agent_message",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="coexistence",
            parameters={
                "message": "What can this platform do?",
                "chat_session_id": "chat_test_session_msg_1"
            }
        )
        
        result = await coexistence_solution.handle_intent(message_intent, execution_context)
        
        assert "artifacts" in result
        assert "events" in result
        assert "journey_execution_id" in result
    
    @pytest.mark.asyncio
    async def test_registers_artifact(
        self, coexistence_solution, execution_context
    ):
        """Should register artifact on success."""
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        # First, initiate the guide agent to create a chat session
        init_intent = IntentFactory.create_intent(
            intent_type="initiate_guide_agent",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="coexistence",
            parameters={
                "chat_session_id": "chat_test_session_msg_2"
            }
        )
        
        await coexistence_solution.handle_intent(init_intent, execution_context)
        
        # Now process a message in that session
        message_intent = IntentFactory.create_intent(
            intent_type="process_guide_agent_message",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="coexistence",
            parameters={
                "message": "Help me understand data analysis",
                "chat_session_id": "chat_test_session_msg_2"
            }
        )
        
        result = await coexistence_solution.handle_intent(message_intent, execution_context)
        
        assert "artifacts" in result
        assert "guide_agent_response" in result["artifacts"]
