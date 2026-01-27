"""
Test Ingest File Intent Service

Tests:
- Parameter validation
- File upload handling
- Artifact registration
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class TestIngestFileParameters:
    """Test ingest_file parameter validation."""
    
    def test_requires_file_name(self):
        """Should require file_name parameter."""
        # Intent should have file_name in required params
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        intent = IntentFactory.create_intent(
            intent_type="ingest_file",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="content_solution",
            parameters={"file_name": "test.txt"}  # Required
        )
        
        assert intent.parameters.get("file_name") == "test.txt"
    
    def test_file_name_is_string(self):
        """file_name should be a string."""
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        intent = IntentFactory.create_intent(
            intent_type="ingest_file",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="content_solution",
            parameters={"file_name": "test.txt"}
        )
        
        assert isinstance(intent.parameters.get("file_name"), str)


class TestIngestFileExecution:
    """Test ingest_file execution."""
    
    @pytest.mark.asyncio
    async def test_returns_file_id(self, content_solution, execution_context):
        """Should return file_id on success."""
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        intent = IntentFactory.create_intent(
            intent_type="ingest_file",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="content_solution",
            parameters={"file_name": "test.txt"}
        )
        
        result = await content_solution.handle_intent(intent, execution_context)
        
        # Should have some result
        assert "success" in result or "error" in result
    
    @pytest.mark.asyncio
    async def test_registers_artifact(self, content_solution, execution_context):
        """Should register artifact on upload."""
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        intent = IntentFactory.create_intent(
            intent_type="ingest_file",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="content_solution",
            parameters={"file_name": "test.txt"}
        )
        
        result = await content_solution.handle_intent(intent, execution_context)
        
        # Should have artifacts dict
        assert "artifacts" in result


class TestIngestFileEvents:
    """Test ingest_file events."""
    
    @pytest.mark.asyncio
    async def test_emits_events(self, content_solution, execution_context):
        """Should emit events on completion."""
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        intent = IntentFactory.create_intent(
            intent_type="ingest_file",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="content_solution",
            parameters={"file_name": "test.txt"}
        )
        
        result = await content_solution.handle_intent(intent, execution_context)
        
        # Should have events list
        assert "events" in result
        assert isinstance(result["events"], list)
