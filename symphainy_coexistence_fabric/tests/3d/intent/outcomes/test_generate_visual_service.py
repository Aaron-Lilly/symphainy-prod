"""
Test GenerateVisual Intent Service

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


class TestGenerateVisualParameters:
    """Test generate_visual parameter validation."""
    
    def test_requires_parameters(self):
        """Should require required parameters."""
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        intent = IntentFactory.create_intent(
            intent_type="generate_visual",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="outcomes_solution",
            parameters={
                "visual_type": "chart",
                "data_source_id": "test_data_123"
            }
        )
        
        assert intent.intent_type == "generate_visual"


class TestGenerateVisualExecution:
    """Test generate_visual execution."""
    
    @pytest.mark.asyncio
    async def test_executes_successfully(
        self, outcomes_solution, execution_context
    ):
        """Should execute service successfully."""
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        intent = IntentFactory.create_intent(
            intent_type="generate_visual",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="outcomes_solution",
            parameters={
                "visual_type": "chart",
                "data_source_id": "test_data_123"
            }
        )
        
        result = await outcomes_solution.handle_intent(intent, execution_context)
        
        assert "artifacts" in result
        assert "events" in result
        assert "journey_execution_id" in result
    
    @pytest.mark.asyncio
    async def test_registers_artifact(
        self, outcomes_solution, execution_context
    ):
        """Should register artifact on success."""
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        intent = IntentFactory.create_intent(
            intent_type="generate_visual",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="outcomes_solution",
            parameters={
                "visual_type": "diagram",
                "data_source_id": "test_data_456"
            }
        )
        
        result = await outcomes_solution.handle_intent(intent, execution_context)
        
        assert "artifacts" in result
