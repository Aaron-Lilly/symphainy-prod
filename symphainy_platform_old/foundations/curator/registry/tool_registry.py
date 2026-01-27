"""
Tool Registry

Manages MCP tool registration and discovery.

WHAT (Service Role): I manage MCP tool registration and discovery
HOW (Service Implementation): I maintain an MCP tool registry
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from utilities import get_logger, get_clock


class ToolRegistry:
    """
    Tool Registry - Central MCP tool registration and discovery.
    
    Manages MCP tools for agent-to-service access.
    """
    
    def __init__(self):
        """Initialize Tool Registry."""
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
        
        # MCP tool registry
        # Key: tool_name, Value: Dict with tool_definition, server_name, realm, etc.
        self.mcp_tool_registry: Dict[str, Dict[str, Any]] = {}
        
        # MCP server registry
        # Key: server_name, Value: Dict with server_instance, tools, realm, etc.
        self.mcp_server_registry: Dict[str, Dict[str, Any]] = {}
        
        self.logger.info("Tool Registry initialized")
    
    async def register_mcp_tool(
        self,
        tool_name: str,
        tool_definition: Dict[str, Any],
        server_name: Optional[str] = None,
        realm: Optional[str] = None
    ) -> bool:
        """
        Register an MCP tool.
        
        Args:
            tool_name: Name of the MCP tool
            tool_definition: Tool definition (input_schema, description, etc.)
            server_name: Optional MCP server name
            realm: Optional realm
        
        Returns:
            bool: True if registration successful
        """
        try:
            self.mcp_tool_registry[tool_name] = {
                "tool_name": tool_name,
                "tool_definition": tool_definition,
                "server_name": server_name,
                "realm": realm,
                "registered_at": self.clock.now_iso(),
                "status": "active"
            }
            
            self.logger.info(f"MCP tool registered: {tool_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register MCP tool: {e}", exc_info=True)
            return False
    
    async def get_tool(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        Get tool by name.
        
        Args:
            tool_name: Name of the tool
        
        Returns:
            Optional[Dict[str, Any]]: Tool registration or None if not found
        """
        return self.mcp_tool_registry.get(tool_name)
    
    async def list_tools(
        self,
        realm: Optional[str] = None,
        server_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List tools with optional filters.
        
        Args:
            realm: Optional realm filter
            server_name: Optional server name filter
        
        Returns:
            List[Dict[str, Any]]: List of tool registrations
        """
        tools = list(self.mcp_tool_registry.values())
        
        if realm:
            tools = [t for t in tools if t.get("realm") == realm]
        
        if server_name:
            tools = [t for t in tools if t.get("server_name") == server_name]
        
        return tools
    
    async def register_mcp_server(
        self,
        server_name: str,
        server_instance: Any,
        tools: List[str],
        realm: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Register an MCP server.
        
        Args:
            server_name: Name of the MCP server
            server_instance: MCP server instance
            tools: List of tool names provided by this server
            realm: Optional realm
            metadata: Optional metadata
        
        Returns:
            bool: True if registration successful
        """
        try:
            self.mcp_server_registry[server_name] = {
                "server_name": server_name,
                "server_instance": server_instance,
                "tools": tools,
                "realm": realm,
                "metadata": metadata or {},
                "registered_at": self.clock.now_iso(),
                "status": "active"
            }
            
            self.logger.info(f"MCP server registered: {server_name} with {len(tools)} tools")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register MCP server: {e}", exc_info=True)
            return False
    
    async def get_server(self, server_name: str) -> Optional[Dict[str, Any]]:
        """
        Get MCP server by name.
        
        Args:
            server_name: Name of the server
        
        Returns:
            Optional[Dict[str, Any]]: Server registration or None if not found
        """
        return self.mcp_server_registry.get(server_name)
    
    async def deregister_tool(self, tool_name: str) -> bool:
        """
        Deregister an MCP tool.
        
        Args:
            tool_name: Name of the tool
        
        Returns:
            bool: True if deregistration successful
        """
        try:
            if tool_name not in self.mcp_tool_registry:
                self.logger.warning(f"Tool not found: {tool_name}")
                return False
            
            del self.mcp_tool_registry[tool_name]
            self.logger.info(f"MCP tool deregistered: {tool_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to deregister tool: {e}", exc_info=True)
            return False
    
    async def deregister_server(self, server_name: str) -> bool:
        """
        Deregister an MCP server.
        
        Args:
            server_name: Name of the server
        
        Returns:
            bool: True if deregistration successful
        """
        try:
            if server_name not in self.mcp_server_registry:
                self.logger.warning(f"Server not found: {server_name}")
                return False
            
            # Deregister all tools from this server
            server = self.mcp_server_registry[server_name]
            tools = server.get("tools", [])
            for tool_name in tools:
                if tool_name in self.mcp_tool_registry:
                    del self.mcp_tool_registry[tool_name]
            
            del self.mcp_server_registry[server_name]
            self.logger.info(f"MCP server deregistered: {server_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to deregister server: {e}", exc_info=True)
            return False
