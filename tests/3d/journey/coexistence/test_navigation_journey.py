"""
Test Navigation Journey - Solution Navigation

Tests:
- Navigate to solution
- Get solution context
- Establish solution context
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class TestNavigationJourneyStructure:
    """Test NavigationJourney structure."""
    
    def test_journey_exists(self, coexistence_solution):
        """NavigationJourney should exist."""
        journey = coexistence_solution.get_journey("navigation")
        assert journey is not None
    
    def test_has_journey_id(self, coexistence_solution):
        """Should have JOURNEY_ID attribute."""
        journey = coexistence_solution.get_journey("navigation")
        assert hasattr(journey, 'JOURNEY_ID')
        assert journey.JOURNEY_ID == "navigation"
    
    def test_has_solution_routes(self, coexistence_solution):
        """Should have SOLUTION_ROUTES mapping."""
        journey = coexistence_solution.get_journey("navigation")
        assert hasattr(journey, 'SOLUTION_ROUTES')


class TestNavigationJourneyActions:
    """Test NavigationJourney actions."""
    
    @pytest.mark.asyncio
    async def test_navigate_action(
        self, coexistence_solution, execution_context
    ):
        """Should handle 'navigate' action."""
        journey = coexistence_solution.get_journey("navigation")
        
        result = await journey.compose_journey(
            context=execution_context,
            journey_params={
                "action": "navigate",
                "solution_id": "content_solution"
            }
        )
        
        assert "success" in result
    
    @pytest.mark.asyncio
    async def test_get_context_action(
        self, coexistence_solution, execution_context
    ):
        """Should handle 'get_context' action."""
        journey = coexistence_solution.get_journey("navigation")
        
        result = await journey.compose_journey(
            context=execution_context,
            journey_params={
                "action": "get_context",
                "solution_id": "content_solution"
            }
        )
        
        assert "success" in result
    
    @pytest.mark.asyncio
    async def test_establish_context_action(
        self, coexistence_solution, execution_context
    ):
        """Should handle 'establish_context' action."""
        journey = coexistence_solution.get_journey("navigation")
        
        result = await journey.compose_journey(
            context=execution_context,
            journey_params={
                "action": "establish_context",
                "solution_id": "content_solution",
                "context_data": {"current_file": "test.txt"}
            }
        )
        
        assert "success" in result


class TestNavigationJourneySOAAPIs:
    """Test NavigationJourney SOA APIs."""
    
    def test_has_navigate_to_solution_api(self, coexistence_solution):
        """Should have navigate_to_solution API."""
        journey = coexistence_solution.get_journey("navigation")
        apis = journey.get_soa_apis()
        
        api_names = list(apis.keys())
        assert any("navigate" in name for name in api_names)
    
    def test_has_get_solution_context_api(self, coexistence_solution):
        """Should have get_solution_context API."""
        journey = coexistence_solution.get_journey("navigation")
        apis = journey.get_soa_apis()
        
        api_names = list(apis.keys())
        assert any("context" in name for name in api_names)
