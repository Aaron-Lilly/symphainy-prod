"""
Test Synthesize Outcome Intent Service

Tests:
- Parameter validation
- Outcome synthesis
- Cross-pillar aggregation
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class TestSynthesizeOutcomeParameters:
    """Test synthesize_outcome parameter validation."""
    
    def test_accepts_artifact_ids(self):
        """Should accept artifact_ids parameter."""
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        intent = IntentFactory.create_intent(
            intent_type="synthesize_outcome",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="outcomes_solution",
            parameters={
                "artifact_ids": ["artifact_1", "artifact_2"],
                "synthesis_type": "comprehensive"
            }
        )
        
        assert "artifact_ids" in intent.parameters


class TestSynthesizeOutcomeExecution:
    """Test synthesize_outcome execution."""
    
    @pytest.mark.asyncio
    async def test_returns_synthesis_result(
        self, outcomes_solution, execution_context
    ):
        """Should return synthesis result."""
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        intent = IntentFactory.create_intent(
            intent_type="compose_journey",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="outcomes_solution",
            parameters={
                "journey_id": "outcome_synthesis",
                "journey_params": {
                    "artifact_ids": ["artifact_1", "artifact_2"]
                }
            }
        )
        
        result = await outcomes_solution.handle_intent(intent, execution_context)
        
        assert "success" in result or "error" in result
        assert "artifacts" in result
