"""
Test CheckEmailAvailability Intent Service

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


class TestCheckEmailAvailabilityParameters:
    """Test check_email_availability parameter validation."""
    
    def test_requires_parameters(self):
        """Should require email parameter."""
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        # Required: email
        intent = IntentFactory.create_intent(
            intent_type="check_email_availability",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="security_solution",
            parameters={
                "email": "newuser@example.com"
            }
        )
        
        assert intent.intent_type == "check_email_availability"
        assert intent.parameters.get("email") == "newuser@example.com"


class TestCheckEmailAvailabilityExecution:
    """Test check_email_availability execution."""
    
    @pytest.mark.asyncio
    async def test_executes_successfully(
        self, security_solution, execution_context
    ):
        """Should execute service successfully."""
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        intent = IntentFactory.create_intent(
            intent_type="check_email_availability",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="security_solution",
            parameters={
                "email": "check@example.com"
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
            intent_type="check_email_availability",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="security_solution",
            parameters={
                "email": "another@example.com"
            }
        )
        
        result = await security_solution.handle_intent(intent, execution_context)
        
        # Services return artifacts containing availability result
        assert "artifacts" in result
