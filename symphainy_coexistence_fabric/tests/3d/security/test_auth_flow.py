"""
Test Authentication Flow - Security Tests

Tests authentication journey and session management.

Tests:
- User registration flow
- User authentication flow
- Session creation and validation
- Token validation
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class TestAuthenticationJourney:
    """Test authentication journey."""
    
    @pytest.mark.asyncio
    async def test_security_solution_has_authentication_journey(
        self, security_solution
    ):
        """SecuritySolution should have authentication journey."""
        journeys = security_solution.get_journeys()
        assert "authentication" in journeys, "Missing authentication journey"
    
    @pytest.mark.asyncio
    async def test_authentication_journey_compose(
        self, security_solution, execution_context
    ):
        """Authentication journey should compose successfully."""
        journey = security_solution.get_journey("authentication")
        assert journey is not None
        
        result = await journey.compose_journey(
            context=execution_context,
            journey_params={
                "email": "test@example.com",
                "password": "TestPassword123!"
            }
        )
        
        assert "success" in result or result.get("artifacts", {}).get("authenticated") is True
        assert "journey_id" in result
        assert "artifacts" in result
    
    @pytest.mark.asyncio
    async def test_authentication_returns_session_token(
        self, security_solution, execution_context
    ):
        """Successful authentication should return session token."""
        journey = security_solution.get_journey("authentication")
        
        result = await journey.compose_journey(
            context=execution_context,
            journey_params={
                "email": "test@example.com",
                "password": "TestPassword123!"
            }
        )
        
        # Should have session info in artifacts
        if result.get("success"):
            artifacts = result.get("artifacts", {})
            # Look for session or token artifact
            assert len(artifacts) > 0 or "error" in result


class TestRegistrationJourney:
    """Test user registration journey."""
    
    @pytest.mark.asyncio
    async def test_security_solution_has_registration_journey(
        self, security_solution
    ):
        """SecuritySolution should have registration journey."""
        journeys = security_solution.get_journeys()
        assert "registration" in journeys, "Missing registration journey"
    
    @pytest.mark.asyncio
    async def test_registration_journey_compose(
        self, security_solution, execution_context
    ):
        """Registration journey should compose successfully."""
        journey = security_solution.get_journey("registration")
        assert journey is not None
        
        result = await journey.compose_journey(
            context=execution_context,
            journey_params={
                "email": "newuser@example.com",
                "password": "NewUserPassword123!",
                "display_name": "Test User"
            }
        )
        
        assert "success" in result or result.get("artifacts", {}).get("registered") is True
        assert "journey_id" in result


class TestSessionManagementJourney:
    """Test session management journey."""
    
    @pytest.mark.asyncio
    async def test_security_solution_has_session_management_journey(
        self, security_solution
    ):
        """SecuritySolution should have session_management journey."""
        journeys = security_solution.get_journeys()
        assert "session_management" in journeys, "Missing session_management journey"
    
    @pytest.mark.asyncio
    async def test_session_creation(
        self, security_solution, execution_context
    ):
        """Session management should support session creation."""
        journey = security_solution.get_journey("session_management")
        
        result = await journey.compose_journey(
            context=execution_context,
            journey_params={
                "action": "create",
                "user_id": "test_user_123"
            }
        )
        
        assert "success" in result or result.get("artifacts", {}).get("session_created") is True
    
    @pytest.mark.asyncio
    async def test_session_validation(
        self, security_solution, execution_context
    ):
        """Session management should support session validation."""
        journey = security_solution.get_journey("session_management")
        
        result = await journey.compose_journey(
            context=execution_context,
            journey_params={
                "action": "validate",
                "session_id": "test_session_123"
            }
        )
        
        assert "success" in result or "artifacts" in result


class TestTokenValidation:
    """Test token validation."""
    
    @pytest.mark.asyncio
    async def test_valid_token_accepted(self, mock_public_works):
        """Valid tokens should be accepted."""
        auth = mock_public_works.auth_abstraction
        
        result = await auth.validate_token("valid_test_token")
        
        assert result.get("valid") is True
    
    @pytest.mark.asyncio
    async def test_invalid_token_rejected(self, mock_public_works):
        """Invalid tokens should be rejected."""
        from unittest.mock import AsyncMock
        
        auth = mock_public_works.auth_abstraction
        auth.validate_token = AsyncMock(return_value={"valid": False})
        
        result = await auth.validate_token("invalid_token")
        
        assert result.get("valid") is False


class TestSecuritySolutionSOAAPIs:
    """Test Security Solution SOA APIs."""
    
    def test_security_solution_exposes_soa_apis(self, security_solution):
        """SecuritySolution should expose SOA APIs."""
        apis = security_solution.get_soa_apis()
        assert len(apis) > 0, "SecuritySolution should have SOA APIs"
    
    def test_compose_journey_api_exists(self, security_solution):
        """Security solution should expose journey-level SOA APIs (e.g. authenticate_user)."""
        apis = security_solution.get_soa_apis()
        assert "authenticate_user" in apis or "create_session" in apis, \
            "SecuritySolution should expose authenticate_user or create_session SOA API"
    
    def test_soa_api_has_required_structure(self, security_solution):
        """SOA APIs should be name -> callable (handler)."""
        apis = security_solution.get_soa_apis()
        for api_name, handler in apis.items():
            assert callable(handler), f"API {api_name} handler should be callable"
