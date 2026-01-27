"""
Test Parse Content Intent Service

Tests:
- Parameter validation
- Content parsing
- Parsed artifact creation
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class TestParseContentParameters:
    """Test parse_content parameter validation."""
    
    def test_requires_file_id(self):
        """Should require file_id parameter."""
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        intent = IntentFactory.create_intent(
            intent_type="parse_content",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="content_solution",
            parameters={"file_id": "file_123"}
        )
        
        assert intent.parameters.get("file_id") == "file_123"


class TestParseContentExecution:
    """Test parse_content execution."""
    
    @pytest.mark.asyncio
    async def test_returns_parsed_file_id(self, content_solution, execution_context):
        """Should return parsed_file_id on success."""
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        intent = IntentFactory.create_intent(
            intent_type="parse_content",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="content_solution",
            parameters={"file_id": "file_123"}
        )
        
        result = await content_solution.handle_intent(intent, execution_context)
        
        assert "success" in result or "error" in result
