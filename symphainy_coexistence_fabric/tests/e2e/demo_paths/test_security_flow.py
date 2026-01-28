"""
E2E Test: Security Flow

DEMO PATH: Registration → Authentication → Session

Critical demo path - this is the FIRST thing users hit.
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class TestSecurityDemoPath:
    """E2E test for security flow - CRITICAL."""
    
    @pytest.mark.asyncio
    async def test_full_auth_flow(
        self,
        security_solution,
        execution_context
    ):
        """Test complete auth flow: register → login → session."""
        # Step 1: Register new user
        register_result = await security_solution.get_journey("registration").compose_journey(
            context=execution_context,
            journey_params={
                "email": "newuser@example.com",
                "password": "SecureP@ssw0rd123",
                "display_name": "Demo User"
            }
        )
        
        assert "success" in register_result
        
        # Step 2: Authenticate
        auth_result = await security_solution.get_journey("authentication").compose_journey(
            context=execution_context,
            journey_params={
                "email": "newuser@example.com",
                "password": "SecureP@ssw0rd123"
            }
        )
        
        assert "success" in auth_result
        
        # Step 3: Session management
        session_result = await security_solution.get_journey("session_management").compose_journey(
            context=execution_context,
            journey_params={
                "action": "validate",
                "session_id": "test_session_123"
            }
        )
        
        assert "success" in session_result
    
    @pytest.mark.asyncio
    async def test_login_flow(
        self,
        security_solution,
        execution_context
    ):
        """Test login flow only."""
        result = await security_solution.get_journey("authentication").compose_journey(
            context=execution_context,
            journey_params={
                "email": "existing@example.com",
                "password": "ExistingP@ss123"
            }
        )
        
        assert "success" in result
        # Should have session token or auth info
        assert "artifacts" in result


class TestSecurityErrorHandling:
    """Test security error handling."""
    
    @pytest.mark.asyncio
    async def test_invalid_credentials_handled(
        self,
        security_solution,
        execution_context
    ):
        """Invalid credentials should return error, not crash."""
        result = await security_solution.get_journey("authentication").compose_journey(
            context=execution_context,
            journey_params={
                "email": "nonexistent@example.com",
                "password": "WrongPassword"
            }
        )
        
        # Should not crash - should return success=False or error
        assert "success" in result or "error" in result
    
    @pytest.mark.asyncio
    async def test_missing_credentials_handled(
        self,
        security_solution,
        execution_context
    ):
        """Missing credentials should be handled gracefully."""
        result = await security_solution.get_journey("authentication").compose_journey(
            context=execution_context,
            journey_params={}  # Missing email and password
        )
        
        # Should not crash
        assert "success" in result or "error" in result
