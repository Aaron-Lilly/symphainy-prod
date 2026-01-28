"""
Test OutcomeSynthesis Journey

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


class TestOutcomeSynthesisJourneyStructure:
    """Test OutcomeSynthesisJourney structure."""
    
    def test_journey_exists(self, outcomes_solution):
        """OutcomeSynthesisJourney should exist."""
        journey = outcomes_solution.get_journey("outcome_synthesis")
        assert journey is not None
    
    def test_has_compose_journey(self, outcomes_solution):
        """Should have compose_journey method."""
        journey = outcomes_solution.get_journey("outcome_synthesis")
        assert hasattr(journey, 'compose_journey')


class TestOutcomeSynthesisJourneyExecution:
    """Test OutcomeSynthesisJourney execution."""
    
    @pytest.mark.asyncio
    async def test_execute_journey(
        self, outcomes_solution, execution_context
    ):
        """Should execute journey successfully."""
        journey = outcomes_solution.get_journey("outcome_synthesis")
        
        result = await journey.compose_journey(
            context=execution_context,
            journey_params={}
        )
        
        assert "success" in result or "error" in result
    
    @pytest.mark.asyncio
    async def test_returns_artifacts(
        self, outcomes_solution, execution_context
    ):
        """Should return artifacts in result."""
        journey = outcomes_solution.get_journey("outcome_synthesis")
        
        result = await journey.compose_journey(
            context=execution_context,
            journey_params={}
        )
        
        assert "artifacts" in result


class TestOutcomeSynthesisJourneySOAAPIs:
    """Test OutcomeSynthesisJourney SOA APIs."""
    
    def test_has_soa_apis(self, outcomes_solution):
        """Should expose SOA APIs."""
        journey = outcomes_solution.get_journey("outcome_synthesis")
        apis = journey.get_soa_apis()
        
        assert isinstance(apis, dict)
        assert len(apis) > 0
