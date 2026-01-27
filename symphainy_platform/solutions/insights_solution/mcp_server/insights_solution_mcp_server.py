"""
Insights Solution MCP Server

Exposes Insights Solution SOA APIs as MCP Tools.
Tool naming: insights_{action}
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional
from utilities import get_logger
from symphainy_platform.civic_systems.agentic.mcp_server_base import MCPServerBase


class InsightsSolutionMCPServer(MCPServerBase):
    """Insights Solution MCP Server."""
    
    def __init__(self, solution, public_works: Optional[Any] = None, state_surface: Optional[Any] = None):
        super().__init__(service_name="insights_solution_mcp", realm_name="insights")
        self.solution = solution
        self.public_works = public_works
        self.state_surface = state_surface
        self._registered_journeys = []
    
    async def initialize(self) -> bool:
        try:
            self.logger.info("Initializing Insights Solution MCP Server...")
            registered_count = 0
            
            journeys = self.solution.get_journeys() if self.solution else {}
            
            for journey_id, journey in journeys.items():
                if hasattr(journey, 'get_soa_apis'):
                    soa_apis = journey.get_soa_apis()
                    for api_name, api_def in soa_apis.items():
                        handler = api_def.get("handler")
                        if handler:
                            tool_name = f"insights_{api_name}"
                            
                            def create_handler(h):
                                async def tool_handler(**params):
                                    return await h(**params)
                                return tool_handler
                            
                            self.register_tool(
                                tool_name=tool_name,
                                handler=create_handler(handler),
                                input_schema=api_def.get("input_schema", {}),
                                description=api_def.get("description", f"Insights: {api_name}")
                            )
                            self.soa_api_registry[api_name] = tool_name
                            registered_count += 1
                    
                    self._registered_journeys.append(journey_id)
            
            self.logger.info(f"Insights Solution MCP Server initialized with {registered_count} tools")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize: {e}")
            return False
    
    def get_usage_guide(self) -> Dict[str, Any]:
        return {
            "server_name": "insights_solution_mcp",
            "solution": "insights_solution",
            "registered_journeys": self._registered_journeys,
            "tools": list(self.soa_api_registry.values())
        }
