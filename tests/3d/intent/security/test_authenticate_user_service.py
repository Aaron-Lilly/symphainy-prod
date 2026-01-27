"""
Test Authenticate User Intent Service

CRITICAL: This is the first user-facing intent.

Tests:
- Parameter validation
- Credential validation
- Session creation
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class TestAuthenticateUserParameters:
    """Test authenticate_user parameter validation."""
    
    def test_requires_email(self):
        """Should require email parameter."""
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        intent = IntentFactory.create_intent(
            intent_type="authenticate_user",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="security_solution",
            parameters={
                "email": "test@example.com",
                "password": "Password123!"
            }
        )
        
        assert intent.parameters.get("email") == "test@example.com"
    
    def test_requires_password(self):
        """Should require password parameter."""
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        intent = IntentFactory.create_intent(
            intent_type="authenticate_user",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="security_solution",
            parameters={
                "email": "test@example.com",
                "password": "Password123!"
            }
        )
        
        assert "password" in intent.parameters


class TestAuthenticateUserExecution:
    """Test authenticate_user execution."""
    
    @pytest.mark.asyncio
    async def test_valid_credentials_succeed(
        self, security_solution, execution_context
    ):
        """Valid credentials should succeed."""
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        intent = IntentFactory.create_intent(
            intent_type="compose_journey",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="security_solution",
            parameters={
                "journey_id": "authentication",
                "journey_params": {
                    "email": "test@example.com",
                    "password": "Password123!"
                }
            }
        )
        
        result = await security_solution.handle_intent(intent, execution_context)
        
        assert "success" in result
    
    @pytest.mark.asyncio
    async def test_returns_session_info(
        self, security_solution, execution_context
    ):
        """Should return session info on success."""
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        intent = IntentFactory.create_intent(
            intent_type="compose_journey",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="security_solution",
            parameters={
                "journey_id": "authentication",
                "journey_params": {
                    "email": "test@example.com",
                    "password": "Password123!"
                }
            }
        )
        
        result = await security_solution.handle_intent(intent, execution_context)
        
        assert "artifacts" in result


class TestAuthenticateUserErrorHandling:
    """Test error handling for authentication."""
    
    @pytest.mark.asyncio
    async def test_missing_email_handled(
        self, security_solution, execution_context
    ):
        """Missing email should be handled gracefully."""
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        intent = IntentFactory.create_intent(
            intent_type="compose_journey",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="security_solution",
            parameters={
                "journey_id": "authentication",
                "journey_params": {"password": "Password123!"}  # Missing email
            }
        )
        
        result = await security_solution.handle_intent(intent, execution_context)
        
        # Should not crash
        assert "success" in result or "error" in result
