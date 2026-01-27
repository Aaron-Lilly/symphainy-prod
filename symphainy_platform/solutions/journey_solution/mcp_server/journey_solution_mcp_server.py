"""
Journey Solution MCP Server
Tool naming: journey_{action}
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional
from utilities import get_logger
from symphainy_platform.civic_systems.agentic.mcp_server_base import MCPServerBase


class JourneySolutionMCPServer(MCPServerBase):
    def __init__(self, solution, public_works: Optional[Any] = None, state_surface: Optional[Any] = None):
        super().__init__(service_name="journey_solution_mcp", realm_name="journey")
        self.solution = solution
        self._registered_journeys = []
    
    async def initialize(self) -> bool:
        try:
            self.logger.info("Initializing Journey Solution MCP Server...")
            registered_count = 0
            
            journeys = self.solution.get_journeys() if self.solution else {}
            for journey_id, journey in journeys.items():
                if hasattr(journey, 'get_soa_apis'):
                    for api_name, api_def in journey.get_soa_apis().items():
                        handler = api_def.get("handler")
                        if handler:
                            tool_name = f"journey_{api_name}"
                            def create_handler(h):
                                async def tool_handler(**p): return await h(**p)
                                return tool_handler
                            self.register_tool(tool_name, create_handler(handler), api_def.get("input_schema", {}), api_def.get("description", ""))
                            self.soa_api_registry[api_name] = tool_name
                            registered_count += 1
                    self._registered_journeys.append(journey_id)
            
            self.logger.info(f"Journey Solution MCP Server initialized with {registered_count} tools")
            return True
        except Exception as e:
            self.logger.error(f"Failed: {e}")
            return False
    
    def get_usage_guide(self) -> Dict[str, Any]:
        return {"server_name": "journey_solution_mcp", "journeys": self._registered_journeys, "tools": list(self.soa_api_registry.values())}
