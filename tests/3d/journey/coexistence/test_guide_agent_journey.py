"""
Test GuideAgent Journey - AI Assistant Journey

Tests:
- Initiate guide agent session
- Process user messages
- Route to liaison agents
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class TestGuideAgentJourneyStructure:
    """Test GuideAgentJourney structure."""
    
    def test_journey_exists(self, coexistence_solution):
        """GuideAgentJourney should exist."""
        journey = coexistence_solution.get_journey("guide_agent")
        assert journey is not None
    
    def test_has_journey_id(self, coexistence_solution):
        """Should have JOURNEY_ID attribute."""
        journey = coexistence_solution.get_journey("guide_agent")
        assert hasattr(journey, 'JOURNEY_ID')
        assert journey.JOURNEY_ID == "guide_agent"


class TestGuideAgentJourneyActions:
    """Test GuideAgentJourney actions."""
    
    @pytest.mark.asyncio
    async def test_initiate_action(
        self, coexistence_solution, execution_context
    ):
        """Should handle 'initiate' action."""
        journey = coexistence_solution.get_journey("guide_agent")
        
        result = await journey.compose_journey(
            context=execution_context,
            journey_params={"action": "initiate"}
        )
        
        assert "success" in result
    
    @pytest.mark.asyncio
    async def test_process_message_action(
        self, coexistence_solution, execution_context
    ):
        """Should handle 'process_message' action."""
        journey = coexistence_solution.get_journey("guide_agent")
        
        result = await journey.compose_journey(
            context=execution_context,
            journey_params={
                "action": "process_message",
                "message": "What can I do with this platform?"
            }
        )
        
        assert "success" in result
    
    @pytest.mark.asyncio
    async def test_route_to_liaison_action(
        self, coexistence_solution, execution_context
    ):
        """Should handle 'route_to_liaison' action."""
        journey = coexistence_solution.get_journey("guide_agent")
        
        result = await journey.compose_journey(
            context=execution_context,
            journey_params={
                "action": "route_to_liaison",
                "pillar_type": "content",
                "user_query": "Help me upload a file"
            }
        )
        
        assert "success" in result


class TestGuideAgentJourneySOAAPIs:
    """Test GuideAgentJourney SOA APIs."""
    
    def test_has_initiate_api(self, coexistence_solution):
        """Should have initiate_guide_agent API."""
        journey = coexistence_solution.get_journey("guide_agent")
        apis = journey.get_soa_apis()
        
        api_names = list(apis.keys())
        assert any("initiate" in name for name in api_names)
    
    def test_has_process_message_api(self, coexistence_solution):
        """Should have process message API."""
        journey = coexistence_solution.get_journey("guide_agent")
        apis = journey.get_soa_apis()
        
        api_names = list(apis.keys())
        assert any("process" in name or "message" in name for name in api_names)
    
    def test_has_route_to_liaison_api(self, coexistence_solution):
        """Should have route_to_liaison API."""
        journey = coexistence_solution.get_journey("guide_agent")
        apis = journey.get_soa_apis()
        
        api_names = list(apis.keys())
        assert any("route" in name or "liaison" in name for name in api_names)


class TestGuideAgentJourneyMCPIntegration:
    """Test GuideAgentJourney MCP integration."""
    
    def test_has_curator_reference(self, coexistence_solution):
        """Should have curator reference for tool discovery."""
        journey = coexistence_solution.get_journey("guide_agent")
        
        # Journey should have some form of curator access
        assert hasattr(journey, 'curator') or \
               hasattr(journey, '_curator') or \
               hasattr(journey, '_query_curator_for_mcp_tools')
    
    def test_has_mcp_tool_call_method(self, coexistence_solution):
        """Should have method to call MCP tools."""
        journey = coexistence_solution.get_journey("guide_agent")
        
        assert hasattr(journey, '_call_orchestrator_mcp_tool')
