"""
Test OutcomesSolution - Outcomes Realm Platform Solution

Tests:
- Solution initialization
- Journey registration (6 journeys)
- POC, Roadmap, Blueprint capabilities
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class TestOutcomesSolutionInitialization:
    """Test OutcomesSolution initialization."""
    
    def test_solution_has_correct_id(self, outcomes_solution):
        """Solution should have correct ID."""
        assert outcomes_solution.SOLUTION_ID == "outcomes_solution"
    
    def test_solution_has_supported_intents(self, outcomes_solution):
        """Solution should declare supported intents."""
        assert hasattr(outcomes_solution, 'SUPPORTED_INTENTS')
        assert "compose_journey" in outcomes_solution.SUPPORTED_INTENTS


class TestOutcomesJourneys:
    """Test OutcomesSolution journeys."""
    
    def test_has_expected_journeys(self, outcomes_solution):
        """OutcomesSolution should have expected journeys."""
        journeys = outcomes_solution.get_journeys()
        
        expected = [
            "outcome_synthesis",
            "roadmap_generation",
            "poc_proposal",
            "blueprint_creation",
            "solution_creation",
            "artifact_export"
        ]
        
        for journey_id in expected:
            assert journey_id in journeys, f"Missing journey: {journey_id}"
    
    def test_each_journey_has_compose_journey(self, outcomes_solution):
        """Each journey should have compose_journey method."""
        for journey_id, journey in outcomes_solution.get_journeys().items():
            assert hasattr(journey, 'compose_journey')


class TestOutcomesHandleIntent:
    """Test OutcomesSolution intent handling."""
    
    @pytest.mark.asyncio
    async def test_handle_compose_journey_poc(
        self, outcomes_solution, execution_context, compose_journey_intent
    ):
        """Should handle poc_proposal journey."""
        intent = compose_journey_intent(
            journey_id="poc_proposal",
            journey_params={},
            solution_id="outcomes_solution"
        )
        
        result = await outcomes_solution.handle_intent(intent, execution_context)
        
        assert "success" in result
    
    @pytest.mark.asyncio
    async def test_handle_compose_journey_roadmap(
        self, outcomes_solution, execution_context, compose_journey_intent
    ):
        """Should handle roadmap_generation journey."""
        intent = compose_journey_intent(
            journey_id="roadmap_generation",
            journey_params={},
            solution_id="outcomes_solution"
        )
        
        result = await outcomes_solution.handle_intent(intent, execution_context)
        
        assert "success" in result


class TestOutcomesMCPServer:
    """Test OutcomesSolution MCP Server."""
    
    @pytest.mark.asyncio
    async def test_initialize_mcp_server(self, outcomes_solution):
        """Should initialize MCP server."""
        mcp_server = await outcomes_solution.initialize_mcp_server()
        assert mcp_server is not None


class TestOutcomesExperienceSDK:
    """Test Outcomes Solution Experience SDK integration."""
    
    def test_has_experience_sdk_config(self, outcomes_solution):
        """Should have Experience SDK config."""
        if hasattr(outcomes_solution, 'get_experience_sdk_config'):
            config = outcomes_solution.get_experience_sdk_config()
            
            assert "solution_id" in config
            assert "supported_intents" in config
            assert "available_journeys" in config
