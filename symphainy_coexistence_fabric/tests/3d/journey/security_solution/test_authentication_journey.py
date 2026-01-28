"""
Test Authentication Journey

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


class TestAuthenticationJourneyStructure:
    """Test AuthenticationJourney structure."""
    
    def test_journey_exists(self, security_solution):
        """AuthenticationJourney should exist."""
        journey = security_solution._journeys.get("authentication")
        assert journey is not None
    
    def test_has_compose_journey(self, security_solution):
        """Should have compose_journey method."""
        journey = security_solution._journeys.get("authentication")
        assert hasattr(journey, 'compose_journey')


class TestAuthenticationJourneyExecution:
    """Test AuthenticationJourney execution."""
    
    @pytest.mark.asyncio
    async def test_execute_journey(
        self, security_solution, execution_context
    ):
        """Should execute journey successfully."""
        journey = security_solution._journeys.get("authentication")
        
        # AuthenticateUserService requires email and password
        result = await journey.compose_journey(
            journey_id="authentication",
            context=execution_context,
            journey_params={
                "email": "test@example.com",
                "password": "Password123!"
            }
        )
        
        # Journey returns artifacts, events, and journey metadata
        assert "artifacts" in result
        assert "journey_execution_id" in result
    
    @pytest.mark.asyncio
    async def test_returns_artifacts(
        self, security_solution, execution_context
    ):
        """Should return artifacts in result."""
        journey = security_solution._journeys.get("authentication")
        
        # AuthenticateUserService requires email and password
        result = await journey.compose_journey(
            journey_id="authentication",
            context=execution_context,
            journey_params={
                "email": "user@example.com",
                "password": "SecurePass123!"
            }
        )
        
        assert "artifacts" in result


class TestAuthenticationJourneySOAAPIs:
    """Test AuthenticationJourney SOA APIs."""
    
    def test_has_soa_apis(self, security_solution):
        """Should expose SOA APIs."""
        journey = security_solution._journeys.get("authentication")
        apis = journey.get_soa_apis()
        
        assert isinstance(apis, dict)
        assert len(apis) > 0
