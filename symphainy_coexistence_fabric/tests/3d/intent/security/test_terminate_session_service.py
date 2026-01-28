"""
Test TerminateSession Intent Service

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


class TestTerminateSessionParameters:
    """Test terminate_session parameter validation."""
    
    def test_requires_parameters(self):
        """Should accept session_id parameter."""
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        # session_id can be provided or uses context session
        intent = IntentFactory.create_intent(
            intent_type="terminate_session",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="security_solution",
            parameters={
                "session_id": "session_to_terminate"
            }
        )
        
        assert intent.intent_type == "terminate_session"


class TestTerminateSessionExecution:
    """Test terminate_session execution."""
    
    @pytest.mark.asyncio
    async def test_executes_successfully(
        self, security_solution, execution_context
    ):
        """Should execute service successfully."""
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        intent = IntentFactory.create_intent(
            intent_type="terminate_session",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="security_solution",
            parameters={
                "session_id": "session_to_terminate"
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
            intent_type="terminate_session",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="security_solution",
            parameters={}  # Uses context session_id
        )
        
        result = await security_solution.handle_intent(intent, execution_context)
        
        # Services return artifacts containing termination result
        assert "artifacts" in result
