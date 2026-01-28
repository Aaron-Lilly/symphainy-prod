"""
Test SOP Management Journey

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


class TestSOPManagementJourneyStructure:
    """Test SOPManagementJourney structure."""
    
    def test_journey_exists(self, operations_solution):
        """SOPManagementJourney should exist."""
        journey = operations_solution._journeys.get("sop_management")
        assert journey is not None
    
    def test_has_compose_journey(self, operations_solution):
        """Should have compose_journey method."""
        journey = operations_solution._journeys.get("sop_management")
        assert hasattr(journey, 'compose_journey')


class TestSOPManagementJourneyExecution:
    """Test SOPManagementJourney execution."""
    
    @pytest.mark.asyncio
    async def test_execute_journey(
        self, operations_solution, execution_context
    ):
        """Should execute journey successfully."""
        journey = operations_solution._journeys.get("sop_management")
        
        # GenerateSOPService requires workflow_id
        result = await journey.compose_journey(
            journey_id="sop_management",
            context=execution_context,
            journey_params={
                "workflow_id": "test_workflow_123"
            }
        )
        
        # Journey returns artifacts, events, and journey metadata
        assert "artifacts" in result
        assert "journey_execution_id" in result
    
    @pytest.mark.asyncio
    async def test_returns_artifacts(
        self, operations_solution, execution_context
    ):
        """Should return artifacts in result."""
        journey = operations_solution._journeys.get("sop_management")
        
        # GenerateSOPService requires workflow_id
        result = await journey.compose_journey(
            journey_id="sop_management",
            context=execution_context,
            journey_params={
                "workflow_id": "test_workflow_123"
            }
        )
        
        assert "artifacts" in result
        assert "sop" in result["artifacts"]


class TestSOPManagementJourneySOAAPIs:
    """Test SOPManagementJourney SOA APIs."""
    
    def test_has_soa_apis(self, operations_solution):
        """Should expose SOA APIs."""
        journey = operations_solution._journeys.get("sop_management")
        apis = journey.get_soa_apis()
        
        assert isinstance(apis, dict)
        assert len(apis) > 0
        assert any("sop" in name.lower() for name in apis.keys())
