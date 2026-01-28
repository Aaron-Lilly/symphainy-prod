"""
Test AnalyzeCoexistence Intent Service

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


class TestAnalyzeCoexistenceParameters:
    """Test analyze_coexistence parameter validation."""
    
    def test_requires_parameters(self):
        """Should require required parameters."""
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        # Test that intent can be created with valid parameters
        intent = IntentFactory.create_intent(
            intent_type="analyze_coexistence",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="operations_solution",
            parameters={
                "workflow_id": "test_workflow_123"  # Required: at least one of workflow_id or sop_id
            }
        )
        
        assert intent.intent_type == "analyze_coexistence"
        assert intent.parameters.get("workflow_id") == "test_workflow_123"


class TestAnalyzeCoexistenceExecution:
    """Test analyze_coexistence execution."""
    
    @pytest.mark.asyncio
    async def test_executes_successfully(
        self, operations_solution, execution_context
    ):
        """Should execute service successfully."""
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        intent = IntentFactory.create_intent(
            intent_type="analyze_coexistence",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="operations_solution",
            parameters={
                "workflow_id": "test_workflow_123"
            }
        )
        
        result = await operations_solution.handle_intent(intent, execution_context)
        
        # Services return artifacts and events, not success
        assert "artifacts" in result
        assert "events" in result
    
    @pytest.mark.asyncio
    async def test_registers_artifact(
        self, operations_solution, execution_context
    ):
        """Should register artifact on success."""
        from symphainy_platform.runtime.intent_model import IntentFactory
        
        intent = IntentFactory.create_intent(
            intent_type="analyze_coexistence",
            tenant_id="test_tenant",
            session_id="test_session",
            solution_id="operations_solution",
            parameters={
                "sop_id": "test_sop_123"  # Can also use sop_id instead of workflow_id
            }
        )
        
        result = await operations_solution.handle_intent(intent, execution_context)
        
        # Services return artifacts containing analysis results
        assert "artifacts" in result
        assert "analysis" in result["artifacts"]
