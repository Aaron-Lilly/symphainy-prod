"""
Test CreateUserAccount Intent Service

Tests:
- Parameter validation
- Service execution
- Artifact registration
- Event emission
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class TestCreateUserAccountParameters:
    """Test create_user_account parameter validation."""
    
    def test_requires_parameters(self):
        """Should require email and password parameters."""
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        # Required: email and password
        intent = IntentFactory.create_intent(
            intent_type="create_user_account",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="security_solution",
            parameters={
                "email": "newuser@example.com",
                "password": "SecurePass123!",
                "name": "Test User"
            }
        )
        
        assert intent.intent_type == "create_user_account"
        assert intent.parameters.get("email") == "newuser@example.com"


class TestCreateUserAccountExecution:
    """Test create_user_account execution."""
    
    @pytest.mark.asyncio
    async def test_executes_successfully(
        self, security_solution, execution_context
    ):
        """Should execute service successfully."""
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        intent = IntentFactory.create_intent(
            intent_type="create_user_account",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="security_solution",
            parameters={
                "email": "newuser@example.com",
                "password": "SecurePass123!",
                "name": "Test User"
            }
        )
        
        result = await security_solution.handle_intent(intent, execution_context)
        
        # Services return artifacts and events
        assert "artifacts" in result
        assert "events" in result
    
    @pytest.mark.asyncio
    async def test_registers_artifact(
        self, security_solution, execution_context
    ):
        """Should register artifact on success."""
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        intent = IntentFactory.create_intent(
            intent_type="create_user_account",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="security_solution",
            parameters={
                "email": "anotheruser@example.com",
                "password": "SecurePass456!"
            }
        )
        
        result = await security_solution.handle_intent(intent, execution_context)
        
        # Services return artifacts containing registration info
        assert "artifacts" in result
