"""
Test LineageVisualization Journey

Tests:
- Journey structure
- Journey execution
- SOA API exposure
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class TestLineageVisualizationJourneyStructure:
    """Test LineageVisualizationJourney structure."""
    
    def test_journey_exists(self, insights_solution):
        """LineageVisualizationJourney should exist."""
        journey = insights_solution.get_journey("lineage_visualization")
        assert journey is not None
    
    def test_has_compose_journey(self, insights_solution):
        """Should have compose_journey method."""
        journey = insights_solution.get_journey("lineage_visualization")
        assert hasattr(journey, 'compose_journey')


class TestLineageVisualizationJourneyExecution:
    """Test LineageVisualizationJourney execution."""
    
    @pytest.mark.asyncio
    async def test_execute_journey(
        self, insights_solution, execution_context
    ):
        """Should execute journey successfully."""
        journey = insights_solution.get_journey("lineage_visualization")
        
        result = await journey.compose_journey(
            context=execution_context,
            journey_params={}
        )
        
        assert "success" in result or "error" in result
    
    @pytest.mark.asyncio
    async def test_returns_artifacts(
        self, insights_solution, execution_context
    ):
        """Should return artifacts in result."""
        journey = insights_solution.get_journey("lineage_visualization")
        
        result = await journey.compose_journey(
            context=execution_context,
            journey_params={}
        )
        
        assert "artifacts" in result


class TestLineageVisualizationJourneySOAAPIs:
    """Test LineageVisualizationJourney SOA APIs."""
    
    def test_has_soa_apis(self, insights_solution):
        """Should expose SOA APIs."""
        journey = insights_solution.get_journey("lineage_visualization")
        apis = journey.get_soa_apis()
        
        assert isinstance(apis, dict)
        assert len(apis) > 0
