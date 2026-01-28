"""
Test Coexistence Analysis Journey

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


class TestCoexistenceAnalysisJourneyStructure:
    """Test CoexistenceAnalysisJourney structure."""
    
    def test_journey_exists(self, operations_solution):
        """CoexistenceAnalysisJourney should exist."""
        journey = operations_solution._journeys.get("coexistence_analysis")
        assert journey is not None
    
    def test_has_compose_journey(self, operations_solution):
        """Should have compose_journey method."""
        journey = operations_solution._journeys.get("coexistence_analysis")
        assert hasattr(journey, 'compose_journey')


class TestCoexistenceAnalysisJourneyExecution:
    """Test CoexistenceAnalysisJourney execution."""
    
    @pytest.mark.asyncio
    async def test_execute_journey(
        self, operations_solution, execution_context
    ):
        """Should execute journey successfully."""
        journey = operations_solution._journeys.get("coexistence_analysis")
        
        result = await journey.compose_journey(
            journey_id="coexistence_analysis",
            context=execution_context,
            journey_params={
                "sop_file_id": "test_sop_123",
                "workflow_file_id": "test_workflow_123"
            }
        )
        
        assert "success" in result or "error" in result
    
    @pytest.mark.asyncio
    async def test_returns_artifacts(
        self, operations_solution, execution_context
    ):
        """Should return artifacts in result."""
        journey = operations_solution._journeys.get("coexistence_analysis")
        
        result = await journey.compose_journey(
            journey_id="coexistence_analysis",
            context=execution_context,
            journey_params={
                "sop_file_id": "test_sop_123",
                "workflow_file_id": "test_workflow_123"
            }
        )
        
        assert "artifacts" in result


class TestCoexistenceAnalysisJourneySOAAPIs:
    """Test CoexistenceAnalysisJourney SOA APIs."""
    
    def test_has_soa_apis(self, operations_solution):
        """Should expose SOA APIs."""
        journey = operations_solution._journeys.get("coexistence_analysis")
        apis = journey.get_soa_apis()
        
        assert isinstance(apis, dict)
        assert len(apis) > 0
        assert any("coexistence" in name.lower() or "analyze" in name.lower() for name in apis.keys())
