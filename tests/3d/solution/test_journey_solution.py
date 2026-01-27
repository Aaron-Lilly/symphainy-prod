"""
Test JourneySolution - Journey Realm Platform Solution

Tests:
- Solution initialization
- Journey registration (2 journeys)
- Workflow/SOP and Coexistence analysis
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class TestJourneySolutionInitialization:
    """Test JourneySolution initialization."""
    
    def test_solution_has_correct_id(self, journey_solution):
        """Solution should have correct ID."""
        assert journey_solution.SOLUTION_ID == "journey_solution"
    
    def test_solution_has_supported_intents(self, journey_solution):
        """Solution should declare supported intents."""
        assert hasattr(journey_solution, 'SUPPORTED_INTENTS')
        assert "compose_journey" in journey_solution.SUPPORTED_INTENTS


class TestJourneySolutionJourneys:
    """Test JourneySolution journeys."""
    
    def test_has_expected_journeys(self, journey_solution):
        """JourneySolution should have expected journeys."""
        journeys = journey_solution.get_journeys()
        
        expected = ["workflow_sop", "coexistence_analysis"]
        
        for journey_id in expected:
            assert journey_id in journeys, f"Missing journey: {journey_id}"
    
    def test_each_journey_has_compose_journey(self, journey_solution):
        """Each journey should have compose_journey method."""
        for journey_id, journey in journey_solution.get_journeys().items():
            assert hasattr(journey, 'compose_journey')


class TestJourneySolutionHandleIntent:
    """Test JourneySolution intent handling."""
    
    @pytest.mark.asyncio
    async def test_handle_compose_journey_workflow_sop(
        self, journey_solution, execution_context, compose_journey_intent
    ):
        """Should handle workflow_sop journey."""
        intent = compose_journey_intent(
            journey_id="workflow_sop",
            journey_params={},
            solution_id="journey_solution"
        )
        
        result = await journey_solution.handle_intent(intent, execution_context)
        
        assert "success" in result


class TestJourneySolutionMCPServer:
    """Test JourneySolution MCP Server."""
    
    @pytest.mark.asyncio
    async def test_initialize_mcp_server(self, journey_solution):
        """Should initialize MCP server."""
        mcp_server = await journey_solution.initialize_mcp_server()
        assert mcp_server is not None
