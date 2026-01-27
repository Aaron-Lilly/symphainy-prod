"""
MCP Server Base - Simplified Base Class for Realm MCP Servers

Base class for MCP servers that expose realm SOA APIs as MCP tools.
Follows the unified pattern from old codebase but simplified for current architecture.

WHAT (Base Role): I provide MCP server functionality for realm services
HOW (Base Implementation): I register SOA APIs as MCP tools and handle tool execution
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
from utilities import get_logger


class MCPServerBase(ABC):
    """
    Base class for all MCP servers in the platform.
    
    Provides:
    - Tool registration and management
    - Tool discovery and metadata
    - Tool execution with validation
    - Standard MCP server lifecycle management
    """
    
    def __init__(self, service_name: str, realm_name: str):
        """
        Initialize MCP Server Base.
        
        Args:
            service_name: Service name (e.g., "insights_mcp")
            realm_name: Realm name (e.g., "insights")
        """
        self.service_name = service_name
        self.realm_name = realm_name
        self.logger = get_logger(f"MCP:{service_name}")
        
        # Tool registry: {tool_name: {handler, input_schema, description}}
        self.tools: Dict[str, Dict[str, Any]] = {}
        self.soa_api_registry: Dict[str, str] = {}  # {api_name: tool_name}
        
        self.logger.info(f"Initialized MCP Server: {service_name} (realm: {realm_name})")
    
    def register_tool(
        self,
        tool_name: str,
        handler: Any,
        input_schema: Dict[str, Any],
        description: str
    ) -> None:
        """
        Register a tool.
        
        Args:
            tool_name: Tool name (e.g., "insights_extract_structured_data")
            handler: Tool handler function (async)
            input_schema: JSON Schema for tool input
            description: Tool description
        """
        if not tool_name:
            raise ValueError("Tool name is required")
        if not handler:
            raise ValueError("Tool handler is required")
        if not input_schema:
            raise ValueError("Tool input_schema is required")
        
        self.tools[tool_name] = {
            "handler": handler,
            "input_schema": input_schema,
            "description": description
        }
        
        self.logger.info(f"✅ Registered MCP tool: {tool_name}")
    
    def get_tool(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get tool by name."""
        return self.tools.get(tool_name)
    
    def get_tool_list(self) -> List[str]:
        """Get list of all registered tool names."""
        return list(self.tools.keys())
    
    def get_registered_tools(self) -> Dict[str, Any]:
        """Get all registered tools with metadata."""
        return {
            tool_name: {
                "description": tool_info["description"],
                "input_schema": tool_info["input_schema"]
            }
            for tool_name, tool_info in self.tools.items()
        }
    
    async def execute_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a tool.
        
        Args:
            tool_name: Tool name
            parameters: Tool parameters
            user_context: Optional user context (tenant_id, user_id, etc.)
        
        Returns:
            Tool execution result
        """
        tool = self.get_tool(tool_name)
        if not tool:
            raise ValueError(f"Tool not found: {tool_name}")
        
        handler = tool["handler"]
        
        # Add user_context to parameters if provided
        if user_context:
            parameters["user_context"] = user_context
        
        try:
            # Execute handler
            if callable(handler):
                result = await handler(**parameters)
                return result
            else:
                raise ValueError(f"Tool handler is not callable: {tool_name}")
        except Exception as e:
            self.logger.error(f"Tool execution failed: {tool_name}: {e}", exc_info=True)
            raise
    
    @abstractmethod
    async def initialize(self) -> bool:
        """
        Initialize MCP server.
        
        Should:
        - Get SOA APIs from orchestrator
        - Register tools from SOA API definitions
        - Return True if successful
        
        Returns:
            True if initialization successful
        """
        pass
    
    @abstractmethod
    def get_usage_guide(self) -> Dict[str, Any]:
        """
        Return usage guide for this MCP server.
        
        Returns:
            Dict with server metadata and tool list
        """
        pass
    
    async def get_health_status(self) -> Dict[str, Any]:
        """
        Get health status.
        
        Returns:
            Dict with health status
        """
        return {
            "status": "healthy",
            "service_name": self.service_name,
            "realm": self.realm_name,
            "tools_registered": len(self.tools),
            "tools": self.get_tool_list()
        }
