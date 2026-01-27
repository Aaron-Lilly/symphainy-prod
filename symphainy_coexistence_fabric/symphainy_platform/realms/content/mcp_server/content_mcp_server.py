"""
Content Realm MCP Server

Exposes Content Orchestrator SOA APIs as MCP Tools for agent consumption.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any
from symphainy_platform.civic_systems.agentic.mcp_server_base import MCPServerBase


class ContentRealmMCPServer(MCPServerBase):
    """Content Realm MCP Server."""
    
    def __init__(self, orchestrator):
        """Initialize Content Realm MCP Server."""
        super().__init__(
            service_name="content_mcp",
            realm_name="content"
        )
        self.orchestrator = orchestrator
    
    async def initialize(self) -> bool:
        """Initialize MCP Server and register tools from orchestrator SOA APIs."""
        try:
            self.logger.info("🔧 Initializing Content Realm MCP Server...")
            
            if not hasattr(self.orchestrator, '_define_soa_api_handlers'):
                self.logger.warning("⚠️ Orchestrator does not define SOA APIs.")
                return True
            
            soa_apis = self.orchestrator._define_soa_api_handlers()
            
            if not soa_apis:
                self.logger.warning("⚠️ No SOA APIs defined.")
                return True
            
            registered_count = 0
            for api_name, api_def in soa_apis.items():
                try:
                    handler = api_def.get("handler")
                    if not handler:
                        continue
                    
                    tool_name = f"content_{api_name}"
                    
                    def create_tool_handler(api_name_inner, handler_inner):
                        async def tool_handler(**parameters):
                            if callable(handler_inner):
                                return await handler_inner(**parameters)
                            else:
                                raise ValueError(f"Handler for '{api_name_inner}' is not callable")
                        return tool_handler
                    
                    tool_handler = create_tool_handler(api_name, handler)
                    input_schema = api_def.get("input_schema", {
                        "type": "object",
                        "properties": {},
                        "required": []
                    })
                    
                    self.register_tool(
                        tool_name=tool_name,
                        handler=tool_handler,
                        input_schema=input_schema,
                        description=api_def.get("description", f"Content realm: {api_name}")
                    )
                    
                    self.soa_api_registry[api_name] = tool_name
                    registered_count += 1
                    
                except Exception as e:
                    self.logger.error(f"❌ Failed to register tool '{api_name}': {e}")
                    continue
            
            self.logger.info(f"✅ Content Realm MCP Server initialized with {registered_count} tools")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Content Realm MCP Server: {e}")
            return False
    
    def get_usage_guide(self) -> Dict[str, Any]:
        """Return usage guide."""
        return {
            "server_name": "content_mcp",
            "realm": "content",
            "description": "Content Realm MCP Server",
            "tools": list(self.soa_api_registry.values()),
            "soa_api_mappings": self.soa_api_registry
        }
