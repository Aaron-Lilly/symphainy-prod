"""
Validation Tests for Auth Abstraction

Tests that Auth abstraction:
1. Returns raw data (not business objects)
2. Has no business logic (no tenant creation, role extraction)
3. Works with adapter
4. Is swappable
"""

import pytest
from typing import Dict, Any
from symphainy_platform.foundations.public_works.abstractions.auth_abstraction import AuthAbstraction
from symphainy_platform.foundations.public_works.adapters.supabase_adapter import SupabaseAdapter
from symphainy_platform.foundations.public_works.protocols.auth_protocol import SecurityContext


@pytest.fixture
async def supabase_adapter():
    """Create Supabase adapter for testing."""
    import os
    return SupabaseAdapter(
        url=os.getenv("SUPABASE_URL", "https://test.supabase.co"),
        anon_key=os.getenv("SUPABASE_ANON_KEY", "test-anon-key"),
        service_key=os.getenv("SUPABASE_SERVICE_KEY", "test-service-key")
    )


@pytest.fixture
async def auth_abstraction(supabase_adapter):
    """Create Auth abstraction with Supabase adapter."""
    return AuthAbstraction(supabase_adapter=supabase_adapter)


@pytest.mark.unit
@pytest.mark.foundations
@pytest.mark.asyncio
class TestAuthAbstractionValidation:
    """Validation tests for Auth abstraction."""
    
    async def test_authenticate_returns_raw_data(self, auth_abstraction):
        """
        Test that authenticate returns raw data (not SecurityContext).
        
        After refactoring, authenticate should return Dict[str, Any],
        not SecurityContext (which is business logic).
        """
        # This test will FAIL if abstraction still returns SecurityContext
        # After refactoring, it should return raw Dict
        result = await auth_abstraction.authenticate({
            "email": "test@example.com",
            "password": "test_password"
        })
        
        # Should return raw data structure
        assert result is not None
        assert isinstance(result, dict)  # Raw data, not SecurityContext
        assert "user_id" in result or "id" in result
        assert "email" in result
        
        # Should NOT return SecurityContext (business logic)
        assert not isinstance(result, SecurityContext)
    
    async def test_authenticate_no_tenant_creation(self, auth_abstraction, mocker):
        """
        Test that authenticate does NOT create tenant.
        
        After refactoring, tenant creation should be removed from abstraction.
        """
        # Mock the adapter to track calls
        mock_create_tenant = mocker.patch.object(
            auth_abstraction.supabase,
            'create_tenant',
            return_value={"success": False, "error": "Should not be called"}
        )
        
        # Try to authenticate
        result = await auth_abstraction.authenticate({
            "email": "test@example.com",
            "password": "test_password"
        })
        
        # Should NOT call create_tenant
        mock_create_tenant.assert_not_called()
    
    async def test_validate_token_returns_raw_data(self, auth_abstraction):
        """
        Test that validate_token returns raw data.
        
        After refactoring, validate_token should return Dict[str, Any],
        not SecurityContext.
        """
        # Use a valid test token (or mock)
        result = await auth_abstraction.validate_token("test_token")
        
        # Should return raw data
        assert result is not None
        assert isinstance(result, dict)  # Raw data, not SecurityContext
        assert "user_id" in result or "id" in result
        
        # Should NOT return SecurityContext
        assert not isinstance(result, SecurityContext)
    
    async def test_validate_token_no_role_extraction(self, auth_abstraction, mocker):
        """
        Test that validate_token does NOT extract roles/permissions.
        
        After refactoring, role extraction should be removed from abstraction.
        """
        # Mock adapter to return user data
        mock_get_user = mocker.patch.object(
            auth_abstraction.supabase,
            'validate_token_local',
            return_value={
                "success": True,
                "user": {
                    "id": "test_user_id",
                    "email": "test@example.com",
                    "user_metadata": {}
                }
            }
        )
        
        result = await auth_abstraction.validate_token("test_token")
        
        # Should return raw data without role extraction
        assert result is not None
        # Should NOT have roles/permissions extracted (that's Security Guard's job)
        assert "roles" not in result or result.get("roles") == []
        assert "permissions" not in result or result.get("permissions") == []
    
    async def test_refresh_token_returns_raw_data(self, auth_abstraction):
        """
        Test that refresh_token returns raw data.
        """
        result = await auth_abstraction.refresh_token("test_refresh_token")
        
        # Should return raw data
        assert result is not None
        assert isinstance(result, dict)
        assert "user_id" in result or "id" in result
        
        # Should NOT return SecurityContext
        assert not isinstance(result, SecurityContext)


@pytest.mark.contract
@pytest.mark.foundations
class TestAuthAbstractionProtocolCompliance:
    """Test that Auth abstraction complies with protocol."""
    
    def test_implements_authentication_protocol(self, auth_abstraction):
        """Test that Auth abstraction implements AuthenticationProtocol."""
        from symphainy_platform.foundations.public_works.protocols.auth_protocol import AuthenticationProtocol
        
        # Check that AuthAbstraction implements the protocol
        assert isinstance(auth_abstraction, AuthenticationProtocol)
    
    def test_has_required_methods(self, auth_abstraction):
        """Test that Auth abstraction has all required methods."""
        assert hasattr(auth_abstraction, 'authenticate')
        assert hasattr(auth_abstraction, 'validate_token')
        assert hasattr(auth_abstraction, 'refresh_token')
    
    def test_method_signatures_match_protocol(self, auth_abstraction):
        """Test that method signatures match protocol."""
        import inspect
        from symphainy_platform.foundations.public_works.protocols.auth_protocol import AuthenticationProtocol
        
        # Check authenticate signature
        protocol_sig = inspect.signature(AuthenticationProtocol.authenticate)
        impl_sig = inspect.signature(auth_abstraction.authenticate)
        
        # Parameters should match (except 'self')
        protocol_params = list(protocol_sig.parameters.keys())
        impl_params = list(impl_sig.parameters.keys())
        
        # Should have same parameters (excluding 'self')
        assert set(protocol_params) == set(impl_params)


@pytest.mark.swappability
@pytest.mark.foundations
@pytest.mark.asyncio
class TestAuthAbstractionSwappability:
    """Test that Auth abstraction is swappable."""
    
    async def test_works_with_supabase_adapter(self, supabase_adapter):
        """Test that Auth abstraction works with Supabase adapter."""
        auth_abstraction = AuthAbstraction(supabase_adapter=supabase_adapter)
        
        # Should initialize without error
        assert auth_abstraction is not None
        assert auth_abstraction.supabase == supabase_adapter
    
    async def test_can_swap_to_auth0_adapter(self, mocker):
        """Test that Auth abstraction can work with Auth0 adapter (mock)."""
        # Create mock Auth0 adapter (same interface as Supabase adapter)
        mock_auth0_adapter = mocker.Mock()
        mock_auth0_adapter.sign_in_with_password = mocker.AsyncMock(
            return_value={
                "success": True,
                "user": {"id": "auth0_user_id", "email": "test@example.com"}
            }
        )
        
        # Create Auth abstraction with Auth0 adapter
        auth_abstraction = AuthAbstraction(supabase_adapter=mock_auth0_adapter)
        
        # Should work with Auth0 adapter
        result = await auth_abstraction.authenticate({
            "email": "test@example.com",
            "password": "test_password"
        })
        
        # Should return same structure (adapter-agnostic)
        assert result is not None
        assert "user_id" in result or "id" in result
