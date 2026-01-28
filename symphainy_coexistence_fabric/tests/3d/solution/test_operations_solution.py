"""
Test OperationsSolution - Operations Realm Platform Solution

Tests:
- Solution initialization
- Journey registration (4 journeys)
- Workflow and SOP capabilities
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class TestOperationsSolutionInitialization:
    """Test OperationsSolution initialization."""
    
    def test_solution_has_correct_id(self, operations_solution):
        """Solution should have correct ID."""
        assert operations_solution.SOLUTION_ID == "operations_solution"
    
    def test_solution_has_supported_intents(self, operations_solution):
        """Solution should declare supported intents."""
        assert hasattr(operations_solution, 'SUPPORTED_INTENTS')
        assert "compose_journey" in operations_solution.SUPPORTED_INTENTS


class TestOperationsJourneys:
    """Test OperationsSolution journeys."""
    
    def test_has_expected_journeys(self, operations_solution):
        """OperationsSolution should have expected journeys."""
        journeys = operations_solution.get_journeys()
        
        expected = [
            "workflow_management",
            "sop_management",
            "process_optimization",
            "coexistence_analysis"
        ]
        
        for journey_id in expected:
            assert journey_id in journeys, f"Missing journey: {journey_id}"
    
    def test_each_journey_has_compose_journey(self, operations_solution):
        """Each journey should have compose_journey method."""
        for journey_id, journey in operations_solution.get_journeys().items():
            assert hasattr(journey, 'compose_journey')


class TestOperationsHandleIntent:
    """Test OperationsSolution intent handling."""
    
    @pytest.mark.asyncio
    async def test_handle_compose_journey_workflow(
        self, operations_solution, execution_context, compose_journey_intent
    ):
        """Should handle workflow_management journey."""
        intent = compose_journey_intent(
            journey_id="workflow_management",
            journey_params={},
            solution_id="operations_solution"
        )
        
        result = await operations_solution.handle_intent(intent, execution_context)
        
        assert "success" in result
    
    @pytest.mark.asyncio
    async def test_handle_compose_journey_sop(
        self, operations_solution, execution_context, compose_journey_intent
    ):
        """Should handle sop_management journey."""
        intent = compose_journey_intent(
            journey_id="sop_management",
            journey_params={},
            solution_id="operations_solution"
        )
        
        result = await operations_solution.handle_intent(intent, execution_context)
        
        assert "success" in result


class TestOperationsMCPServer:
    """Test OperationsSolution MCP Server."""
    
    @pytest.mark.asyncio
    async def test_initialize_mcp_server(self, operations_solution):
        """Should initialize MCP server."""
        mcp_server = await operations_solution.initialize_mcp_server()
        assert mcp_server is not None
