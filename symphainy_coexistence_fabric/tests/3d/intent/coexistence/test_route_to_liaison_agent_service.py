"""
Test RouteToLiaisonAgent Intent Service

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


class TestRouteToLiaisonAgentParameters:
    """Test route_to_liaison_agent parameter validation."""
    
    def test_requires_parameters(self):
        """Should require target_pillar parameter."""
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        intent = IntentFactory.create_intent(
            intent_type="route_to_liaison_agent",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="coexistence",
            parameters={
                "target_pillar": "content",
                "routing_reason": "User needs file upload assistance"
            }
        )
        
        assert intent.intent_type == "route_to_liaison_agent"
        assert intent.parameters.get("target_pillar") == "content"


class TestRouteToLiaisonAgentExecution:
    """Test route_to_liaison_agent execution."""
    
    @pytest.mark.asyncio
    async def test_executes_successfully(
        self, coexistence_solution, execution_context
    ):
        """Should execute service successfully."""
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        intent = IntentFactory.create_intent(
            intent_type="route_to_liaison_agent",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="coexistence",
            parameters={
                "target_pillar": "content",
                "routing_reason": "User needs file upload assistance"
            }
        )
        
        result = await coexistence_solution.handle_intent(intent, execution_context)
        
        assert "artifacts" in result
        assert "events" in result
        assert "journey_execution_id" in result
    
    @pytest.mark.asyncio
    async def test_registers_artifact(
        self, coexistence_solution, execution_context
    ):
        """Should register artifact on success."""
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        intent = IntentFactory.create_intent(
            intent_type="route_to_liaison_agent",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="coexistence",
            parameters={
                "target_pillar": "insights",
                "routing_reason": "User needs data analysis help"
            }
        )
        
        result = await coexistence_solution.handle_intent(intent, execution_context)
        
        assert "artifacts" in result
        assert "liaison_agent_activation" in result["artifacts"]
