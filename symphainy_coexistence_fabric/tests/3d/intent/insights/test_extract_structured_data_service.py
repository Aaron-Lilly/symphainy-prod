"""
Test ExtractStructuredData Intent Service

NOTE: The extract_structured_data intent is NOT currently implemented in InsightsSolution.
These tests document expected behavior but are skipped until implemented.

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


class TestExtractStructuredDataParameters:
    """Test extract_structured_data parameter validation."""
    
    def test_requires_parameters(self):
        """Should require artifact_id parameter."""
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        intent = IntentFactory.create_intent(
            intent_type="extract_structured_data",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="insights_solution",
            parameters={
                "artifact_id": "test_artifact_123",
                "extraction_schema": {"fields": ["name", "date"]}
            }
        )
        
        assert intent.intent_type == "extract_structured_data"
        assert intent.parameters.get("artifact_id") == "test_artifact_123"


class TestExtractStructuredDataExecution:
    """Test extract_structured_data execution."""
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Intent 'extract_structured_data' not implemented in InsightsSolution")
    async def test_executes_successfully(
        self, insights_solution, execution_context
    ):
        """Should execute service successfully."""
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        intent = IntentFactory.create_intent(
            intent_type="extract_structured_data",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="insights_solution",
            parameters={
                "artifact_id": "test_artifact_123",
                "extraction_schema": {"fields": ["name", "date"]}
            }
        )
        
        result = await insights_solution.handle_intent(intent, execution_context)
        
        assert "artifacts" in result
        assert "events" in result
    
    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Intent 'extract_structured_data' not implemented in InsightsSolution")
    async def test_registers_artifact(
        self, insights_solution, execution_context
    ):
        """Should register artifact on success."""
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        intent = IntentFactory.create_intent(
            intent_type="extract_structured_data",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="insights_solution",
            parameters={
                "artifact_id": "test_artifact_456"
            }
        )
        
        result = await insights_solution.handle_intent(intent, execution_context)
        
        assert "artifacts" in result
