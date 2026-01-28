"""
Test Data Analysis Journey (Business Analysis)

Tests:
- Data analysis execution
- Analysis artifact generation

Note: The business_analysis journey was renamed to data_analysis in the platform overhaul.
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class TestBusinessAnalysisJourneyStructure:
    """Test DataAnalysisJourney structure (formerly BusinessAnalysis)."""
    
    def test_journey_exists(self, insights_solution):
        """DataAnalysisJourney should exist."""
        # Journey was renamed from business_analysis to data_analysis
        journey = insights_solution._journeys.get("data_analysis")
        assert journey is not None
    
    def test_has_compose_journey(self, insights_solution):
        """Should have compose_journey method."""
        journey = insights_solution._journeys.get("data_analysis")
        assert hasattr(journey, 'compose_journey')


class TestBusinessAnalysisJourneyExecution:
    """Test DataAnalysisJourney execution."""
    
    @pytest.mark.asyncio
    async def test_analyze_data(self, insights_solution, execution_context):
        """Should analyze data."""
        journey = insights_solution._journeys.get("data_analysis")
        
        result = await journey.compose_journey(
            context=execution_context,
            journey_params={"artifact_id": "test_artifact_123"}
        )
        
        # Journey returns artifacts and journey metadata
        assert "artifacts" in result
        assert "journey_execution_id" in result
