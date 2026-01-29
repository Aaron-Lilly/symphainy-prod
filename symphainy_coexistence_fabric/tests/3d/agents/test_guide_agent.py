"""
Test GuideAgent - Platform AI Assistant

CRITICAL: GuideAgent is the primary user-facing AI.

Tests:
- MCP tool discovery via Curator
- MCP tool invocation
- Liaison Agent handoff
- Conversation management
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class TestGuideAgentInitialization:
    """Test GuideAgent initialization."""
    
    def test_guide_agent_journey_exists(self, coexistence_solution):
        """GuideAgentJourney should exist in CoexistenceSolution."""
        journeys = coexistence_solution.get_journeys()
        assert "guide_agent" in journeys
    
    def test_guide_agent_has_compose_journey(self, coexistence_solution):
        """GuideAgentJourney should have compose_journey method."""
        journey = coexistence_solution.get_journey("guide_agent")
        assert hasattr(journey, 'compose_journey')


class TestGuideAgentMCPToolDiscovery:
    """Test GuideAgent MCP tool discovery."""
    
    @pytest.mark.asyncio
    async def test_query_curator_for_mcp_tools(self, coexistence_solution, mock_curator):
        """GuideAgent should discover MCP tools via Curator."""
        journey = coexistence_solution.get_journey("guide_agent")
        
        if hasattr(journey, '_query_curator_for_mcp_tools'):
            tools = await journey._query_curator_for_mcp_tools()
            
            # Should return list of tools
            assert isinstance(tools, list)
        else:
            # Journey should have curator reference
            assert hasattr(journey, 'curator') or hasattr(journey, '_curator')
    
    @pytest.mark.asyncio
    async def test_discovers_tools_from_all_solutions(self, mock_curator):
        """Should discover tools from all platform solutions."""
        tools = await mock_curator.get_all_mcp_tools()
        
        # Should have tools from multiple solutions
        solution_prefixes = {t["tool_name"].split("_")[0] for t in tools}
        
        expected_prefixes = {"coexist", "content", "insights", "ops", "outcomes", "security", "tower"}
        assert len(solution_prefixes & expected_prefixes) >= 5, \
            "Should discover tools from at least 5 solutions"


class TestGuideAgentMCPToolInvocation:
    """Test GuideAgent MCP tool invocation."""
    
    @pytest.mark.asyncio
    async def test_call_orchestrator_mcp_tool_method_exists(self, coexistence_solution):
        """GuideAgent should have MCP tool invocation method."""
        journey = coexistence_solution.get_journey("guide_agent")
        
        assert hasattr(journey, '_call_orchestrator_mcp_tool'), \
            "GuideAgentJourney should have _call_orchestrator_mcp_tool method"
    
    @pytest.mark.asyncio
    async def test_call_mcp_tool_returns_result(
        self, coexistence_solution, execution_context
    ):
        """Calling MCP tool should return result."""
        journey = coexistence_solution.get_journey("guide_agent")
        
        if hasattr(journey, '_call_orchestrator_mcp_tool'):
            result = await journey._call_orchestrator_mcp_tool(
                tool_name="content_upload",
                params={"file_name": "test.txt"},
                context=execution_context
            )
            
            # Should return dict with result or error
            assert isinstance(result, dict)
            assert "result" in result or "error" in result or "status" in result


class TestGuideAgentLiaisonHandoff:
    """Test GuideAgent to Liaison Agent handoff."""
    
    @pytest.mark.asyncio
    async def test_route_to_liaison_agent_method_exists(self, coexistence_solution):
        """GuideAgent should have Liaison routing method."""
        journey = coexistence_solution.get_journey("guide_agent")
        
        assert hasattr(journey, '_route_to_liaison_agent'), \
            "GuideAgentJourney should have _route_to_liaison_agent method"

    @pytest.mark.asyncio
    async def test_route_to_liaison_requires_target_pillar(
        self, coexistence_solution, execution_context
    ):
        """Probe: journey contract requires target_pillar (canonical param)."""
        journey = coexistence_solution.get_journey("guide_agent")
        result = await journey._route_to_liaison_agent(
            context=execution_context,
            params={"target_pillar": "content"},
            journey_execution_id="probe_exec_123",
        )
        assert result.get("success") is True
        assert "artifacts" in result and "liaison_agent_activation" in result.get("artifacts", {})

    @pytest.mark.asyncio
    async def test_route_to_liaison_with_context(
        self, coexistence_solution, execution_context
    ):
        """Should route to Liaison with conversation context."""
        journey = coexistence_solution.get_journey("guide_agent")
        if not hasattr(journey, '_route_to_liaison_agent'):
            pytest.skip("journey has no _route_to_liaison_agent")
        result = await journey._route_to_liaison_agent(
            context=execution_context,
            params={
                "target_pillar": "content",
                "routing_reason": "User requested specialist assistance",
                "context_to_share": {
                    "conversation_history": [
                        {"role": "user", "content": "Help me upload a file"},
                        {"role": "assistant", "content": "I'll route you to the Content specialist."},
                    ],
                    "user_query": "Upload my document",
                },
            },
            journey_execution_id="test_exec_123",
        )
        assert result.get("success") is True
        assert "artifacts" in result and "liaison_agent_activation" in result.get("artifacts", {})
    
    @pytest.mark.asyncio
    async def test_share_context_to_agent_method_exists(self, coexistence_solution):
        """GuideAgent should have context sharing method."""
        journey = coexistence_solution.get_journey("guide_agent")
        
        # Should have method to share context
        assert hasattr(journey, '_share_context_to_agent'), \
            "GuideAgentJourney should have _share_context_to_agent method"


class TestGuideAgentConversation:
    """Test GuideAgent conversation management."""
    
    @pytest.mark.asyncio
    async def test_initiate_guide_agent(
        self, coexistence_solution, execution_context
    ):
        """Should be able to initiate GuideAgent session."""
        result = await coexistence_solution.get_journey("guide_agent").compose_journey(
            context=execution_context,
            journey_params={
                "action": "initiate"
            }
        )
        
        assert "success" in result
        assert "journey_id" in result
    
    @pytest.mark.asyncio
    async def test_process_guide_agent_message(
        self, coexistence_solution, execution_context
    ):
        """Should be able to process user message."""
        result = await coexistence_solution.get_journey("guide_agent").compose_journey(
            context=execution_context,
            journey_params={
                "action": "process_message",
                "message": "What can this platform do?"
            }
        )
        
        assert "success" in result


class TestGuideAgentSOAAPIs:
    """Test GuideAgent SOA APIs."""
    
    def test_guide_agent_exposes_soa_apis(self, coexistence_solution):
        """GuideAgentJourney should expose SOA APIs."""
        journey = coexistence_solution.get_journey("guide_agent")
        
        assert hasattr(journey, 'get_soa_apis')
        apis = journey.get_soa_apis()
        assert len(apis) > 0
    
    def test_has_initiate_api(self, coexistence_solution):
        """Should have initiate_guide_agent API."""
        journey = coexistence_solution.get_journey("guide_agent")
        apis = journey.get_soa_apis()
        
        # Should have initiate or similar API
        api_names = list(apis.keys())
        assert any("initiate" in name for name in api_names)
    
    def test_has_process_message_api(self, coexistence_solution):
        """Should have process_message API."""
        journey = coexistence_solution.get_journey("guide_agent")
        apis = journey.get_soa_apis()
        
        # Should have process_message or similar API
        api_names = list(apis.keys())
        assert any("process" in name or "message" in name for name in api_names)
