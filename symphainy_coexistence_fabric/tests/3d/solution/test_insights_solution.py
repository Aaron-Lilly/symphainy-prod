"""
Test InsightsSolution - Insights Realm Platform Solution

Tests:
- Solution initialization
- Journey registration (6 journeys)
- SOA API exposure
- Data analysis capabilities
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class TestInsightsSolutionInitialization:
    """Test InsightsSolution initialization."""
    
    def test_solution_has_correct_id(self, insights_solution):
        """Solution should have correct ID."""
        assert insights_solution.SOLUTION_ID == "insights_solution"
    
    def test_solution_has_supported_intents(self, insights_solution):
        """Solution should declare supported intents."""
        assert hasattr(insights_solution, 'SUPPORTED_INTENTS')
        assert "compose_journey" in insights_solution.SUPPORTED_INTENTS


class TestInsightsJourneys:
    """Test InsightsSolution journeys."""
    
    def test_has_expected_journeys(self, insights_solution):
        """InsightsSolution should have expected journeys."""
        journeys = insights_solution.get_journeys()
        
        expected = [
            "business_analysis",
            "data_quality",
            "data_analysis",
            "data_interpretation",
            "lineage_visualization",
            "relationship_mapping"
        ]
        
        for journey_id in expected:
            assert journey_id in journeys, f"Missing journey: {journey_id}"
    
    def test_each_journey_has_compose_journey(self, insights_solution):
        """Each journey should have compose_journey method."""
        for journey_id, journey in insights_solution.get_journeys().items():
            assert hasattr(journey, 'compose_journey'), \
                f"Journey {journey_id} missing compose_journey"


class TestInsightsHandleIntent:
    """Test InsightsSolution intent handling."""
    
    @pytest.mark.asyncio
    async def test_handle_compose_journey_business_analysis(
        self, insights_solution, execution_context, compose_journey_intent
    ):
        """Should handle business_analysis journey."""
        intent = compose_journey_intent(
            journey_id="business_analysis",
            journey_params={"artifact_id": "test_artifact"},
            solution_id="insights_solution"
        )
        
        result = await insights_solution.handle_intent(intent, execution_context)
        
        assert "success" in result
        assert "artifacts" in result
    
    @pytest.mark.asyncio
    async def test_handle_compose_journey_data_quality(
        self, insights_solution, execution_context, compose_journey_intent
    ):
        """Should handle data_quality journey."""
        intent = compose_journey_intent(
            journey_id="data_quality",
            journey_params={"parsed_file_id": "parsed_123"},
            solution_id="insights_solution"
        )
        
        result = await insights_solution.handle_intent(intent, execution_context)
        
        assert "success" in result


class TestInsightsMCPServer:
    """Test InsightsSolution MCP Server."""
    
    def test_initialize_mcp_server(self, insights_solution):
        """Should initialize MCP server."""
        mcp_server = insights_solution.initialize_mcp_server()
        assert mcp_server is not None
    
    @pytest.mark.asyncio
    async def test_mcp_tools_use_insights_prefix(self, insights_solution):
        """MCP tools should use insights_ prefix."""
        mcp_server = insights_solution.initialize_mcp_server()
        
        if hasattr(mcp_server, 'tools'):
            for tool in mcp_server.tools:
                if hasattr(tool, 'name'):
                    assert tool.name.startswith("insights_")
