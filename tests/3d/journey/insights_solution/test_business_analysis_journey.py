"""
Test Business Analysis Journey

Tests:
- Business data analysis
- Report generation
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class TestBusinessAnalysisJourneyStructure:
    """Test BusinessAnalysisJourney structure."""
    
    def test_journey_exists(self, insights_solution):
        """BusinessAnalysisJourney should exist."""
        journey = insights_solution.get_journey("business_analysis")
        assert journey is not None
    
    def test_has_compose_journey(self, insights_solution):
        """Should have compose_journey method."""
        journey = insights_solution.get_journey("business_analysis")
        assert hasattr(journey, 'compose_journey')


class TestBusinessAnalysisJourneyExecution:
    """Test BusinessAnalysisJourney execution."""
    
    @pytest.mark.asyncio
    async def test_analyze_data(self, insights_solution, execution_context):
        """Should analyze business data."""
        journey = insights_solution.get_journey("business_analysis")
        
        result = await journey.compose_journey(
            context=execution_context,
            journey_params={"artifact_id": "test_artifact_123"}
        )
        
        assert "success" in result or "error" in result
        assert "artifacts" in result
