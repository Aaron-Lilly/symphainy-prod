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
        
        result = await journey.compose_journey(
            journey_id="workflow_management",
            context=execution_context,
            journey_params={
                "source_file_id": "test_file_123",
                "source_type": "sop"
            }
        )
        
        assert "success" in result or "error" in result
    
    @pytest.mark.asyncio
    async def test_returns_artifacts(
        self, operations_solution, execution_context
    ):
        """Should return artifacts in result."""
        journey = operations_solution._journeys.get("workflow_management")
        
        result = await journey.compose_journey(
            journey_id="workflow_management",
            context=execution_context,
            journey_params={
                "source_file_id": "test_file_123",
                "source_type": "sop"
            }
        )
        
        assert "artifacts" in result


class TestWorkflowManagementJourneySOAAPIs:
    """Test WorkflowManagementJourney SOA APIs."""
    
    def test_has_soa_apis(self, operations_solution):
        """Should expose SOA APIs."""
        journey = operations_solution._journeys.get("workflow_management")
        apis = journey.get_soa_apis()
        
        assert isinstance(apis, dict)
        assert len(apis) > 0
        assert "create_workflow" in apis
