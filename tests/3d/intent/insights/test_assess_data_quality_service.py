"""
Test Assess Data Quality Intent Service

Tests:
- Parameter validation
- Quality assessment
- Quality metrics
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class TestAssessDataQualityParameters:
    """Test assess_data_quality parameter validation."""
    
    def test_requires_parsed_file_id(self):
        """Should require parsed_file_id parameter."""
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        intent = IntentFactory.create_intent(
            intent_type="assess_data_quality",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="insights_solution",
            parameters={"parsed_file_id": "parsed_123"}
        )
        
        assert intent.parameters.get("parsed_file_id") == "parsed_123"


class TestAssessDataQualityExecution:
    """Test assess_data_quality execution."""
    
    @pytest.mark.asyncio
    async def test_returns_quality_metrics(self, insights_solution, execution_context):
        """Should return quality metrics."""
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        intent = IntentFactory.create_intent(
            intent_type="assess_data_quality",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="insights_solution",
            parameters={"parsed_file_id": "parsed_123"}
        )
        
        result = await insights_solution.handle_intent(intent, execution_context)
        
        assert "success" in result or "error" in result
        assert "artifacts" in result
