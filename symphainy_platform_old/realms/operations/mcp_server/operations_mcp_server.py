"""
Operations Realm MCP Server

Exposes Operations Orchestrator SOA APIs as MCP Tools for agent consumption.

NOTE: Migrated from JourneyRealmMCPServer as part of realm naming cleanup.
"Journey" is reserved for platform journeys (intent sequences),
"Operations" is the realm for SOPs, workflows, and coexistence analysis.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any
from symphainy_platform.civic_systems.agentic.mcp_server_base import MCPServerBase


class OperationsRealmMCPServer(MCPServerBase):
    """Operations Realm MCP Server."""
    
    def __init__(self, orchestrator):
        """Initialize Operations Realm MCP Server."""
        super().__init__(
            service_name="operations_mcp",
            realm_name="operations"
        )
        self.orchestrator = orchestrator
    
    async def initialize(self) -> bool:
        """Initialize MCP Server and register tools from orchestrator SOA APIs."""
        try:
            self.logger.info("🔧 Initializing Operations Realm MCP Server...")
            
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
                    
                    tool_name = f"operations_{api_name}"
                    
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
                        description=api_def.get("description", f"Operations realm: {api_name}")
                    )
                    
                    self.soa_api_registry[api_name] = tool_name
                    registered_count += 1
                    
                except Exception as e:
                    self.logger.error(f"❌ Failed to register tool '{api_name}': {e}")
                    continue
            
            self.logger.info(f"✅ Operations Realm MCP Server initialized with {registered_count} tools")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Operations Realm MCP Server: {e}")
            return False
    
    def get_usage_guide(self) -> Dict[str, Any]:
        """Return usage guide."""
        return {
            "server_name": "operations_mcp",
            "realm": "operations",
            "description": "Operations Realm MCP Server - SOPs, Workflows, Coexistence Analysis",
            "tools": list(self.soa_api_registry.values()),
            "soa_api_mappings": self.soa_api_registry
        }
