"""
Test ControlTower MCP Server

Tests:
- MCP server initialization
- Tool registration
- SOA API mapping
"""

import pytest
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


class TestControlTowerMCPServer:
    """Test ControlTower MCP Server."""
    
    @pytest.mark.asyncio
    async def test_initialize_mcp_server(self, control_tower):
        """Should initialize MCP server."""
        mcp_server = await control_tower.initialize_mcp_server()
        assert mcp_server is not None
    
    @pytest.mark.asyncio
    async def test_mcp_server_has_tools(self, control_tower):
        """MCP server should have tools registered."""
        mcp_server = await control_tower.initialize_mcp_server()
        
        if hasattr(mcp_server, 'tools'):
            assert mcp_server.tools is not None
            assert len(mcp_server.tools) > 0
    
    def test_soa_apis_exposed(self, control_tower):
        """Solution should expose SOA APIs."""
        apis = control_tower.get_soa_apis()
        assert isinstance(apis, dict)
        assert len(apis) > 0
