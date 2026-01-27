"""
Insights Realm MCP Server

Exposes Insights Orchestrator SOA APIs as MCP Tools for agent consumption.

UNIFIED PATTERN:
- Orchestrator defines SOA APIs via _define_soa_api_handlers()
- MCP Server automatically registers tools from SOA API definitions
- Agents use MCP Tools exclusively (never direct service access)
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional
from symphainy_platform.civic_systems.agentic.mcp_server_base import MCPServerBase


class InsightsRealmMCPServer(MCPServerBase):
    """
    Insights Realm MCP Server.
    
    Exposes Insights Orchestrator SOA APIs as MCP Tools.
    Tools are automatically registered from orchestrator's _define_soa_api_handlers().
    """
    
    def __init__(self, orchestrator):
        """
        Initialize Insights Realm MCP Server.
        
        Args:
            orchestrator: InsightsOrchestrator instance
        """
        super().__init__(
            service_name="insights_mcp",
            realm_name="insights"
        )
        self.orchestrator = orchestrator
    
    async def initialize(self) -> bool:
        """
        Initialize MCP Server and register tools from orchestrator SOA APIs.
        
        UNIFIED PATTERN: Automatically registers tools from _define_soa_api_handlers().
        
        Returns:
            True if initialization successful
        """
        try:
            self.logger.info("🔧 Initializing Insights Realm MCP Server...")
            
            # Get SOA API definitions from orchestrator
            if not hasattr(self.orchestrator, '_define_soa_api_handlers'):
                self.logger.warning(
                    f"⚠️ Orchestrator {self.orchestrator.__class__.__name__} does not define SOA APIs. "
                    f"No tools will be registered."
                )
                return True
            
            soa_apis = self.orchestrator._define_soa_api_handlers()
            
            if not soa_apis:
                self.logger.warning("⚠️ No SOA APIs defined by orchestrator. No tools will be registered.")
                return True
            
            # Register each SOA API as an MCP Tool
            registered_count = 0
            for api_name, api_def in soa_apis.items():
                try:
                    # Get handler from SOA API definition
                    handler = api_def.get("handler")
                    if not handler:
                        self.logger.warning(f"⚠️ SOA API '{api_name}' missing handler, skipping")
                        continue
                    
                    # Create tool name (realm prefix)
                    tool_name = f"insights_{api_name}"
                    
                    # Create async wrapper that calls the handler
                    def create_tool_handler(api_name_inner, handler_inner):
                        """Factory function to create tool handler with proper closure."""
                        async def tool_handler(**parameters):
                            """MCP tool handler that wraps SOA API handler."""
                            # Call orchestrator handler with parameters
                            if callable(handler_inner):
                                return await handler_inner(**parameters)
                            else:
                                raise ValueError(f"Handler for '{api_name_inner}' is not callable")
                        return tool_handler
                    
                    tool_handler = create_tool_handler(api_name, handler)
                    
                    # Get input schema from SOA API definition
                    input_schema = api_def.get("input_schema", {})
                    if not input_schema:
                        # Create minimal schema if not provided
                        input_schema = {
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    
                    # Register tool
                    self.register_tool(
                        tool_name=tool_name,
                        handler=tool_handler,
                        input_schema=input_schema,
                        description=api_def.get("description", f"Insights realm: {api_name}")
                    )
                    
                    # Track mapping
                    self.soa_api_registry[api_name] = tool_name
                    registered_count += 1
                    self.logger.info(f"✅ Registered MCP tool: {tool_name} (from SOA API: {api_name})")
                    
                except Exception as e:
                    self.logger.error(f"❌ Failed to register tool for SOA API '{api_name}': {e}")
                    continue
            
            self.logger.info(
                f"✅ Insights Realm MCP Server initialized with {registered_count} tools "
                f"(from {len(soa_apis)} SOA APIs)"
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Insights Realm MCP Server: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return False
    
    def get_usage_guide(self) -> Dict[str, Any]:
        """Return usage guide for Insights Realm MCP Server."""
        return {
            "server_name": "insights_mcp",
            "realm": "insights",
            "description": "Insights Realm MCP Server - exposes Insights Orchestrator capabilities",
            "tools": list(self.soa_api_registry.values()),
            "usage": "Agents use MCP tools to interact with Insights realm capabilities",
            "soa_api_mappings": self.soa_api_registry
        }
