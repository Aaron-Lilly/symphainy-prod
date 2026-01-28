"""
Test ValidateAuthorization Intent Service

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


class TestValidateAuthorizationParameters:
    """Test validate_authorization parameter validation."""
    
    def test_requires_parameters(self):
        """Should require action parameter."""
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        # Required: action
        intent = IntentFactory.create_intent(
            intent_type="validate_authorization",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="security_solution",
            parameters={
                "action": "read",
                "resource": "files"
            }
        )
        
        assert intent.intent_type == "validate_authorization"
        assert intent.parameters.get("action") == "read"


class TestValidateAuthorizationExecution:
    """Test validate_authorization execution."""
    
    @pytest.mark.asyncio
    async def test_executes_successfully(
        self, security_solution, execution_context
    ):
        """Should execute service successfully."""
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        intent = IntentFactory.create_intent(
            intent_type="validate_authorization",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="security_solution",
            parameters={
                "action": "read",
                "resource": "files"
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
            intent_type="validate_authorization",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="security_solution",
            parameters={
                "action": "write",
                "resource": "workflows"
            }
        )
        
        result = await security_solution.handle_intent(intent, execution_context)
        
        # Services return artifacts containing authorization result
        assert "artifacts" in result
