"""
Test Workflow Management Journey

Tests:
- Journey structure
- Journey execution
- SOA API exposure
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class TestWorkflowManagementJourneyStructure:
    """Test WorkflowManagementJourney structure."""
    
    def test_journey_exists(self, operations_solution):
        """WorkflowManagementJourney should exist."""
        journey = operations_solution._journeys.get("workflow_management")
        assert journey is not None
    
    def test_has_compose_journey(self, operations_solution):
        """Should have compose_journey method."""
        journey = operations_solution._journeys.get("workflow_management")
        assert hasattr(journey, 'compose_journey')


class TestWorkflowManagementJourneyExecution:
    """Test WorkflowManagementJourney execution."""
    
    @pytest.mark.asyncio
    async def test_execute_journey(
        self, operations_solution, execution_context
    ):
        """Should execute journey successfully."""
        journey = operations_solution._journeys.get("workflow_management")
        
        # Journey requires one of: sop_id, bpmn_file_id, or workflow_spec
        result = await journey.compose_journey(
            journey_id="workflow_management",
            context=execution_context,
            journey_params={
                "sop_id": "test_sop_123"
            }
        )
        
        # Journey returns artifacts, events, and journey metadata
        assert "artifacts" in result
        assert "journey_execution_id" in result
    
    @pytest.mark.asyncio
    async def test_returns_artifacts(
        self, operations_solution, execution_context
    ):
        """Should return artifacts in result."""
        journey = operations_solution._journeys.get("workflow_management")
        
        # Journey requires one of: sop_id, bpmn_file_id, or workflow_spec
        result = await journey.compose_journey(
            journey_id="workflow_management",
            context=execution_context,
            journey_params={
                "workflow_spec": {
                    "name": "Test Workflow",
                    "steps": [{"step_id": "1", "name": "Step 1"}]
                }
            }
        )
        
        assert "artifacts" in result
        assert "workflow" in result["artifacts"]


class TestWorkflowManagementJourneySOAAPIs:
    """Test WorkflowManagementJourney SOA APIs."""
    
    def test_has_soa_apis(self, operations_solution):
        """Should expose SOA APIs."""
        journey = operations_solution._journeys.get("workflow_management")
        apis = journey.get_soa_apis()
        
        assert isinstance(apis, dict)
        assert len(apis) > 0
        assert "create_workflow" in apis
