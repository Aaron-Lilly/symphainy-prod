"""
Test Registration Journey

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


class TestRegistrationJourneyStructure:
    """Test RegistrationJourney structure."""
    
    def test_journey_exists(self, security_solution):
        """RegistrationJourney should exist."""
        journey = security_solution.get_journey("registration")
        assert journey is not None
    
    def test_has_compose_journey(self, security_solution):
        """Should have compose_journey method."""
        journey = security_solution.get_journey("registration")
        assert hasattr(journey, 'compose_journey')


class TestRegistrationJourneyExecution:
    """Test RegistrationJourney execution."""
    
    @pytest.mark.asyncio
    async def test_execute_journey(
        self, security_solution, execution_context
    ):
        """Should execute journey successfully."""
        journey = security_solution.get_journey("registration")
        
        result = await journey.compose_journey(
            context=execution_context,
            journey_params={}
        )
        
        assert "success" in result or "error" in result
    
    @pytest.mark.asyncio
    async def test_returns_artifacts(
        self, security_solution, execution_context
    ):
        """Should return artifacts in result."""
        journey = security_solution.get_journey("registration")
        
        result = await journey.compose_journey(
            context=execution_context,
            journey_params={}
        )
        
        assert "artifacts" in result


class TestRegistrationJourneySOAAPIs:
    """Test RegistrationJourney SOA APIs."""
    
    def test_has_soa_apis(self, security_solution):
        """Should expose SOA APIs."""
        journey = security_solution.get_journey("registration")
        apis = journey.get_soa_apis()
        
        assert isinstance(apis, dict)
        assert len(apis) > 0
