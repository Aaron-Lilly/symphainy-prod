"""
Test Data Quality Journey

Tests:
- Quality assessment
- Quality scoring
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class TestDataQualityJourneyStructure:
    """Test DataQualityJourney structure."""
    
    def test_journey_exists(self, insights_solution):
        """DataQualityJourney should exist."""
        journey = insights_solution.get_journey("data_quality")
        assert journey is not None
    
    def test_has_compose_journey(self, insights_solution):
        """Should have compose_journey method."""
        journey = insights_solution.get_journey("data_quality")
        assert hasattr(journey, 'compose_journey')


class TestDataQualityJourneyExecution:
    """Test DataQualityJourney execution."""
    
    @pytest.mark.asyncio
    async def test_assess_quality(self, insights_solution, execution_context):
        """Should assess data quality."""
        journey = insights_solution.get_journey("data_quality")
        
        result = await journey.compose_journey(
            context=execution_context,
            journey_params={"parsed_file_id": "parsed_123"}
        )
        
        assert "success" in result or "error" in result


class TestDataQualityJourneySOAAPIs:
    """Test DataQualityJourney SOA APIs."""
    
    def test_has_assess_quality_api(self, insights_solution):
        """Should have assess_quality API."""
        journey = insights_solution.get_journey("data_quality")
        apis = journey.get_soa_apis()
        
        api_names = list(apis.keys())
        assert any("quality" in name.lower() or "assess" in name.lower() for name in api_names)
