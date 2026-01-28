"""
Test ControlTower - Platform Command Center

Tests:
- Solution initialization
- Journey registration (4 journeys)
- Platform monitoring, Solution management
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class TestControlTowerInitialization:
    """Test ControlTower initialization."""
    
    def test_solution_has_correct_id(self, control_tower):
        """Solution should have correct ID."""
        assert control_tower.SOLUTION_ID == "control_tower"
    
    def test_solution_has_supported_intents(self, control_tower):
        """Solution should declare supported intents."""
        assert hasattr(control_tower, 'SUPPORTED_INTENTS')
        assert "compose_journey" in control_tower.SUPPORTED_INTENTS


class TestControlTowerJourneys:
    """Test ControlTower journeys."""
    
    def test_has_4_journeys(self, control_tower):
        """ControlTower should have 4 journeys."""
        journeys = control_tower.get_journeys()
        assert len(journeys) == 4
    
    def test_has_platform_monitoring_journey(self, control_tower):
        """Should have platform_monitoring journey."""
        journeys = control_tower.get_journeys()
        assert "platform_monitoring" in journeys
    
    def test_has_solution_management_journey(self, control_tower):
        """Should have solution_management journey."""
        journeys = control_tower.get_journeys()
        assert "solution_management" in journeys
    
    def test_has_developer_docs_journey(self, control_tower):
        """Should have developer_docs journey."""
        journeys = control_tower.get_journeys()
        assert "developer_docs" in journeys
    
    def test_has_solution_composition_journey(self, control_tower):
        """Should have solution_composition journey."""
        journeys = control_tower.get_journeys()
        assert "solution_composition" in journeys
    
    def test_each_journey_has_compose_journey(self, control_tower):
        """Each journey should have compose_journey method."""
        for journey_id, journey in control_tower.get_journeys().items():
            assert hasattr(journey, 'compose_journey')


class TestControlTowerHandleIntent:
    """Test ControlTower intent handling."""
    
    @pytest.mark.asyncio
    async def test_handle_compose_journey_monitoring(
        self, control_tower, execution_context, compose_journey_intent
    ):
        """Should handle platform_monitoring journey."""
        intent = compose_journey_intent(
            journey_id="platform_monitoring",
            journey_params={},
            solution_id="control_tower"
        )
        
        result = await control_tower.handle_intent(intent, execution_context)
        
        assert "success" in result
    
    @pytest.mark.asyncio
    async def test_handle_compose_journey_solution_management(
        self, control_tower, execution_context, compose_journey_intent
    ):
        """Should handle solution_management journey."""
        intent = compose_journey_intent(
            journey_id="solution_management",
            journey_params={"action": "list"},
            solution_id="control_tower"
        )
        
        result = await control_tower.handle_intent(intent, execution_context)
        
        assert "success" in result


class TestControlTowerMCPServer:
    """Test ControlTower MCP Server."""
    
    def test_initialize_mcp_server(self, control_tower):
        """Should initialize MCP server."""
        mcp_server = control_tower.initialize_mcp_server()
        assert mcp_server is not None
    
    @pytest.mark.asyncio
    async def test_mcp_tools_use_tower_prefix(self, control_tower):
        """MCP tools should use tower_ prefix."""
        mcp_server = control_tower.initialize_mcp_server()
        
        if hasattr(mcp_server, 'tools'):
            for tool in mcp_server.tools:
                if hasattr(tool, 'name'):
                    assert tool.name.startswith("tower_")


class TestControlTowerPlatformAccess:
    """Test ControlTower platform access capabilities."""
    
    def test_has_solution_registry_access(self, control_tower):
        """ControlTower should have solution registry access."""
        # ControlTower needs to list/manage solutions
        assert hasattr(control_tower, 'solution_registry') or \
               hasattr(control_tower, '_solution_registry')
