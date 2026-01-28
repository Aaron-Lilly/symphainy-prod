"""
Test CoexistenceSolution - Platform Entry Point

Tests:
- Solution initialization
- Journey registration
- SOA API exposure
- compose_journey intent handling
- MCP Server initialization
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class TestCoexistenceSolutionInitialization:
    """Test CoexistenceSolution initialization."""
    
    def test_solution_has_correct_id(self, coexistence_solution):
        """Solution should have correct ID."""
        assert coexistence_solution.SOLUTION_ID == "coexistence"
    
    def test_solution_has_correct_name(self, coexistence_solution):
        """Solution should have correct name."""
        assert coexistence_solution.SOLUTION_NAME == "Coexistence Solution"
    
    def test_solution_has_supported_intents(self, coexistence_solution):
        """Solution should declare supported intents."""
        assert hasattr(coexistence_solution, 'SUPPORTED_INTENTS')
        assert "compose_journey" in coexistence_solution.SUPPORTED_INTENTS


class TestCoexistenceJourneys:
    """Test CoexistenceSolution journeys."""
    
    def test_has_3_journeys(self, coexistence_solution):
        """CoexistenceSolution should have 3 journeys."""
        journeys = coexistence_solution.get_journeys()
        assert len(journeys) == 3
    
    def test_has_introduction_journey(self, coexistence_solution):
        """Should have introduction journey."""
        journeys = coexistence_solution.get_journeys()
        assert "introduction" in journeys
    
    def test_has_navigation_journey(self, coexistence_solution):
        """Should have navigation journey."""
        journeys = coexistence_solution.get_journeys()
        assert "navigation" in journeys
    
    def test_has_guide_agent_journey(self, coexistence_solution):
        """Should have guide_agent journey."""
        journeys = coexistence_solution.get_journeys()
        assert "guide_agent" in journeys
    
    def test_get_journey_by_id(self, coexistence_solution):
        """Should be able to get journey by ID."""
        journey = coexistence_solution.get_journey("introduction")
        assert journey is not None
        assert hasattr(journey, 'compose_journey')


class TestCoexistenceSOAAPIs:
    """Test CoexistenceSolution SOA APIs."""
    
    def test_exposes_soa_apis(self, coexistence_solution):
        """Solution should expose SOA APIs."""
        apis = coexistence_solution.get_soa_apis()
        assert len(apis) > 0
    
    def test_has_compose_journey_api(self, coexistence_solution):
        """Should have compose_journey SOA API."""
        apis = coexistence_solution.get_soa_apis()
        assert "compose_journey" in apis
    
    def test_compose_journey_api_has_handler(self, coexistence_solution):
        """compose_journey API should have handler."""
        apis = coexistence_solution.get_soa_apis()
        api = apis["compose_journey"]
        assert "handler" in api
        assert callable(api["handler"]) or hasattr(api["handler"], '__call__')
    
    def test_compose_journey_api_has_input_schema(self, coexistence_solution):
        """compose_journey API should have input schema."""
        apis = coexistence_solution.get_soa_apis()
        api = apis["compose_journey"]
        assert "input_schema" in api
        
        schema = api["input_schema"]
        assert "properties" in schema
        assert "journey_id" in schema["properties"]


class TestCoexistenceHandleIntent:
    """Test CoexistenceSolution intent handling."""
    
    @pytest.mark.asyncio
    async def test_handle_compose_journey_intent(
        self, coexistence_solution, execution_context, compose_journey_intent
    ):
        """Should handle compose_journey intent."""
        intent = compose_journey_intent(
            journey_id="introduction",
            solution_id="coexistence"
        )
        
        result = await coexistence_solution.handle_intent(intent, execution_context)
        
        assert "success" in result
        assert "journey_id" in result
        assert "artifacts" in result
        assert "events" in result
    
    @pytest.mark.asyncio
    async def test_compose_journey_returns_artifacts(
        self, coexistence_solution, execution_context, compose_journey_intent
    ):
        """compose_journey should return artifacts."""
        intent = compose_journey_intent(
            journey_id="introduction",
            journey_params={"action": "introduce"},
            solution_id="coexistence"
        )
        
        result = await coexistence_solution.handle_intent(intent, execution_context)
        
        assert "artifacts" in result
        # Artifacts may be empty dict or populated
        assert isinstance(result["artifacts"], dict)
    
    @pytest.mark.asyncio
    async def test_invalid_journey_id_raises_error(
        self, coexistence_solution, execution_context, compose_journey_intent
    ):
        """Invalid journey_id should raise error."""
        intent = compose_journey_intent(
            journey_id="nonexistent_journey",
            solution_id="coexistence"
        )
        
        with pytest.raises(ValueError) as exc_info:
            await coexistence_solution.handle_intent(intent, execution_context)
        
        assert "Unknown journey" in str(exc_info.value)


class TestCoexistenceMCPServer:
    """Test CoexistenceSolution MCP Server."""
    
    def test_initialize_mcp_server(self, coexistence_solution):
        """Should be able to initialize MCP server."""
        mcp_server = coexistence_solution.initialize_mcp_server()
        assert mcp_server is not None
    
    def test_mcp_server_has_tools(self, coexistence_solution):
        """MCP server should have registered tools."""
        mcp_server = coexistence_solution.initialize_mcp_server()
        
        # Check tools are registered
        if hasattr(mcp_server, 'tools'):
            assert len(mcp_server.tools) > 0
    
    @pytest.mark.asyncio
    async def test_get_mcp_server_returns_same_instance(self, coexistence_solution):
        """get_mcp_server should return same instance."""
        server1 = await coexistence_solution.initialize_mcp_server()
        server2 = coexistence_solution.get_mcp_server()
        
        assert server1 is server2
