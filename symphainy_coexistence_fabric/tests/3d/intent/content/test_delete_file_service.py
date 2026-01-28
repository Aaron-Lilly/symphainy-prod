"""
Test DeleteFile Intent Service

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


class TestDeleteFileParameters:
    """Test delete_file parameter validation."""
    
    def test_requires_parameters(self):
        """Should require file_id parameter."""
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        intent = IntentFactory.create_intent(
            intent_type="delete_file",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="content_solution",
            parameters={
                "file_id": "test_file_123"
            }
        )
        
        assert intent.intent_type == "delete_file"
        assert intent.parameters.get("file_id") == "test_file_123"


class TestDeleteFileExecution:
    """Test delete_file execution."""
    
    @pytest.mark.asyncio
    async def test_executes_successfully(
        self, content_solution, execution_context
    ):
        """Should execute service successfully."""
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        intent = IntentFactory.create_intent(
            intent_type="delete_file",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="content_solution",
            parameters={
                "artifact_id": "test_artifact_123"
            }
        )
        
        result = await content_solution.handle_intent(intent, execution_context)
        
        assert "artifacts" in result
        assert "events" in result
        assert "journey_execution_id" in result
    
    @pytest.mark.asyncio
    async def test_registers_artifact(
        self, content_solution, execution_context
    ):
        """Should register artifact on success."""
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        intent = IntentFactory.create_intent(
            intent_type="delete_file",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="content_solution",
            parameters={
                "artifact_id": "test_artifact_456"
            }
        )
        
        result = await content_solution.handle_intent(intent, execution_context)
        
        assert "artifacts" in result
        assert "delete_result" in result["artifacts"]
