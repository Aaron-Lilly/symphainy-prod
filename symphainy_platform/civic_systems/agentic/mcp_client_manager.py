"""
MCP Client Manager - Manage MCP Client Connections to Realm MCP Servers

Manages connections to realm MCP servers and provides tool discovery/execution.

WHAT (Agentic System Role): I manage MCP client connections for agents
HOW (Implementation): I connect to realm MCP servers and execute tools

Key Principle: Agents use MCP tools (not direct service calls) for all realm interactions.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional, List
from utilities import get_logger


class MCPClientManager:
    """
    MCP Client Manager - Manages MCP client connections to realm MCP servers.
    
    Provides:
    - Server discovery
    - Tool discovery
    - Tool execution
    - Connection management
    """
    
    def __init__(self, public_works: Optional[Any] = None):
        """
        Initialize MCP Client Manager.
        
        Args:
            public_works: Optional Public Works Foundation Service
        """
        self.logger = get_logger(self.__class__.__name__)
        self.public_works = public_works
        self._servers: Dict[str, Any] = {}  # server_name -> MCP Server instance
        self._initialized = False
    
    async def initialize(self) -> bool:
        """
        Initialize MCP Client Manager and discover servers.
        
        Returns:
            True if initialization successful
        """
        if self._initialized:
            return True
        
        try:
            # Discover available MCP servers
            server_names = await self.discover_servers()
            
            # Connect to each server
            for server_name in server_names:
                await self.connect_to_server(server_name)
            
            self._initialized = True
            self.logger.info(f"✅ MCP Client Manager initialized with {len(self._servers)} servers")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize MCP Client Manager: {e}", exc_info=True)
            return False
    
    async def discover_servers(self) -> List[str]:
        """
        Discover available MCP servers.
        
        Returns:
            List of server names
        """
        # Known realm MCP servers
        # NOTE: "operations_mcp" replaces old "journey_mcp"
        # "Journey" is now reserved for platform journeys (intent sequences)
        # "Operations" is the realm for SOPs, workflows, coexistence analysis
        realm_servers = [
            "insights_mcp",
            "content_mcp",
            "operations_mcp",
            "outcomes_mcp"
        ]
        
        # TODO: In future, discover dynamically from service registry
        # For now, return known servers
        
        self.logger.info(f"Discovered {len(realm_servers)} MCP servers")
        return realm_servers
    
    async def connect_to_server(self, server_name: str) -> bool:
        """
        Connect to an MCP server.
        
        Args:
            server_name: Server name (e.g., "insights_mcp")
        
        Returns:
            True if connection successful
        """
        if server_name in self._servers:
            self.logger.debug(f"Already connected to {server_name}")
            return True
        
        try:
            # Import realm MCP servers dynamically
            if server_name == "insights_mcp":
                from symphainy_platform.realms.insights.mcp_server.insights_mcp_server import (
                    InsightsRealmMCPServer
                )
                # Get orchestrator from public_works or create new
                # For now, create a placeholder - will be properly initialized by realm
                server = InsightsRealmMCPServer(orchestrator=None)
                await server.initialize()
                self._servers[server_name] = server
                
            elif server_name == "content_mcp":
                from symphainy_platform.realms.content.mcp_server.content_mcp_server import (
                    ContentRealmMCPServer
                )
                server = ContentRealmMCPServer(orchestrator=None)
                await server.initialize()
                self._servers[server_name] = server
                
            elif server_name == "operations_mcp":
                from symphainy_platform.realms.operations.mcp_server.operations_mcp_server import (
                    OperationsRealmMCPServer
                )
                server = OperationsRealmMCPServer(orchestrator=None)
                await server.initialize()
                self._servers[server_name] = server
                
            elif server_name == "outcomes_mcp":
                from symphainy_platform.realms.outcomes.mcp_server.outcomes_mcp_server import (
                    OutcomesRealmMCPServer
                )
                server = OutcomesRealmMCPServer(orchestrator=None)
                await server.initialize()
                self._servers[server_name] = server
                
            else:
                self.logger.warning(f"Unknown MCP server: {server_name}")
                return False
            
            self.logger.info(f"✅ Connected to MCP server: {server_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to {server_name}: {e}", exc_info=True)
            return False
    
    async def register_server(self, server_name: str, server: Any) -> bool:
        """
        Register an MCP server.
        
        Args:
            server_name: Server identifier
            server: MCP server instance
        
        Returns:
            True if registered successfully
        """
        try:
            self._servers[server_name] = server
            self.logger.info(f"✅ Registered MCP server: {server_name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to register MCP server {server_name}: {e}")
            return False
    
    async def discover_tools(self) -> List[Dict[str, Any]]:
        """
        Discover all available tools from registered MCP servers.
        
        Returns:
            List of tool metadata dictionaries
        """
        all_tools = []
        for server_name, server in self._servers.items():
            try:
                tools = server.get_tool_list()
                for tool in tools:
                    if isinstance(tool, str):
                        # If tool is just a name, create metadata dict
                        all_tools.append({
                            "name": tool,
                            "server_name": server_name
                        })
                    else:
                        # If tool is already a dict, add server_name
                        tool["server_name"] = server_name
                        all_tools.append(tool)
            except Exception as e:
                self.logger.error(f"Failed to discover tools from {server_name}: {e}")
        return all_tools
    
    async def list_all_tools(self) -> List[Dict[str, Any]]:
        """
        List all tools from all registered servers.
        
        Returns:
            List of tool metadata dictionaries
        """
        return await self.discover_tools()
    
    async def get_tool_list(self, server_name: str) -> List[str]:
        """
        Get list of tools from a server.
        
        Args:
            server_name: Server name
        
        Returns:
            List of tool names
        """
        if server_name not in self._servers:
            await self.connect_to_server(server_name)
        
        server = self._servers.get(server_name)
        if not server:
            return []
        
        try:
            return server.get_tool_list()
        except Exception as e:
            self.logger.error(f"Failed to get tool list from {server_name}: {e}")
            return []
    
    async def execute_tool(
        self,
        server_name: str,
        tool_name: str,
        parameters: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a tool via MCP.
        
        Args:
            server_name: Server name (e.g., "insights_mcp")
            tool_name: Tool name (e.g., "insights_extract_structured_data")
            parameters: Tool parameters
            user_context: User context (tenant_id, session_id, solution_id)
        
        Returns:
            Tool execution result
        """
        if server_name not in self._servers:
            connected = await self.connect_to_server(server_name)
            if not connected:
                return {
                    "success": False,
                    "error": f"Failed to connect to server: {server_name}"
                }
        
        server = self._servers.get(server_name)
        if not server:
            return {
                "success": False,
                "error": f"Server not found: {server_name}"
            }
        
        try:
            # Execute tool via MCP server
            result = await server.execute_tool(
                tool_name=tool_name,
                parameters=parameters,
                user_context=user_context
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to execute tool {tool_name} on {server_name}: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_connected_servers(self) -> List[str]:
        """
        Get list of connected server names.
        
        Returns:
            List of server names
        """
        return list(self._servers.keys())
    
    def is_connected(self, server_name: str) -> bool:
        """
        Check if connected to a server.
        
        Args:
            server_name: Server name
        
        Returns:
            True if connected
        """
        return server_name in self._servers
