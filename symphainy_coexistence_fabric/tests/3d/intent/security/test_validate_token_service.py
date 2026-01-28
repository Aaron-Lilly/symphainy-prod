"""
Test ValidateToken Intent Service

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


class TestValidateTokenParameters:
    """Test validate_token parameter validation."""
    
    def test_requires_parameters(self):
        """Should require token parameter."""
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        # Required: token
        intent = IntentFactory.create_intent(
            intent_type="validate_token",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="security_solution",
            parameters={
                "token": "test_access_token_abc123"
            }
        )
        
        assert intent.intent_type == "validate_token"
        assert intent.parameters.get("token") == "test_access_token_abc123"


class TestValidateTokenExecution:
    """Test validate_token execution."""
    
    @pytest.mark.asyncio
    async def test_executes_successfully(
        self, security_solution, execution_context
    ):
        """Should execute service successfully."""
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        intent = IntentFactory.create_intent(
            intent_type="validate_token",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="security_solution",
            parameters={
                "token": "test_access_token_123"
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
            intent_type="validate_token",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="security_solution",
            parameters={
                "token": "test_access_token_456"
            }
        )
        
        result = await security_solution.handle_intent(intent, execution_context)
        
        # Services return artifacts containing validation result
        assert "artifacts" in result
