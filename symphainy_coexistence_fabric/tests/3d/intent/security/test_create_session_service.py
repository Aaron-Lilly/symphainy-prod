"""
Test CreateSession Intent Service

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


class TestCreateSessionParameters:
    """Test create_session parameter validation."""
    
    def test_requires_parameters(self):
        """Should accept optional parameters for session creation."""
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        # user_id and access_token are optional but useful
        intent = IntentFactory.create_intent(
            intent_type="create_session",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="security_solution",
            parameters={
                "user_id": "test_user_123"
            }
        )
        
        assert intent.intent_type == "create_session"
        assert intent.parameters.get("user_id") == "test_user_123"


class TestCreateSessionExecution:
    """Test create_session execution."""
    
    @pytest.mark.asyncio
    async def test_executes_successfully(
        self, security_solution, execution_context
    ):
        """Should execute service successfully."""
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        intent = IntentFactory.create_intent(
            intent_type="create_session",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="security_solution",
            parameters={
                "user_id": "test_user_123"
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
            intent_type="create_session",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="security_solution",
            parameters={
                "user_id": "test_user_456",
                "metadata": {"source": "test"}
            }
        )
        
        result = await security_solution.handle_intent(intent, execution_context)
        
        # Services return artifacts containing session info
        assert "artifacts" in result
