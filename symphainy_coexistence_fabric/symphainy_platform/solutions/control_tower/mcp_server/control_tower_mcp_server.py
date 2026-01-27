"""
Control Tower MCP Server

Exposes Control Tower capabilities as MCP Tools.
Tool naming convention: tower_{action}

Examples:
- tower_get_platform_stats
- tower_list_solutions
- tower_get_docs
- tower_compose_solution
"""

import sys
from pathlib import Path


def _find_project_root() -> Path:
    """Find project root by searching for pyproject.toml."""
    current = Path(__file__).resolve().parent
    for parent in [current] + list(current.parents):
        if (parent / "pyproject.toml").exists():
            return parent
    # Fallback for when running from different locations
    return Path(__file__).resolve().parents[3] if len(Path(__file__).resolve().parents) > 3 else Path.cwd()


project_root = _find_project_root()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional
from utilities import get_logger
from symphainy_platform.civic_systems.agentic.mcp_server_base import MCPServerBase


class ControlTowerMCPServer(MCPServerBase):
    """
    Control Tower MCP Server.
    
    Aggregates tools from all Control Tower journeys:
    - PlatformMonitoringJourney: tower_get_platform_stats, tower_get_execution_metrics, etc.
    - SolutionManagementJourney: tower_list_solutions, tower_manage_solution, etc.
    - DeveloperDocsJourney: tower_get_docs, tower_get_patterns, etc.
    - SolutionCompositionJourney: tower_get_templates, tower_compose_solution, etc.
    """
    
    def __init__(
        self,
        control_tower,
        public_works: Optional[Any] = None,
        state_surface: Optional[Any] = None
    ):
        super().__init__(
            service_name="control_tower_mcp",
            realm_name="control_tower"
        )
        self.control_tower = control_tower
        self.public_works = public_works
        self.state_surface = state_surface
        self._registered_journeys = []
    
    async def initialize(self) -> bool:
        """Initialize MCP Server and register tools from all journeys."""
        try:
            self.logger.info("🗼 Initializing Control Tower MCP Server...")
            registered_count = 0
            
            journeys = self.control_tower.get_journeys() if self.control_tower else {}
            
            for journey_id, journey in journeys.items():
                try:
                    if hasattr(journey, 'get_soa_apis'):
                        soa_apis = journey.get_soa_apis()
                        
                        for api_name, api_def in soa_apis.items():
                            handler = api_def.get("handler")
                            if not handler:
                                continue
                            
                            # Use tower_ prefix for all tools
                            tool_name = f"tower_{api_name}"
                            
                            def create_tool_handler(handler_inner):
                                async def tool_handler(**parameters):
                                    if callable(handler_inner):
                                        return await handler_inner(**parameters)
                                    raise ValueError("Handler is not callable")
                                return tool_handler
                            
                            self.register_tool(
                                tool_name=tool_name,
                                handler=create_tool_handler(handler),
                                input_schema=api_def.get("input_schema", {}),
                                description=api_def.get("description", f"Control Tower: {api_name}")
                            )
                            
                            self.soa_api_registry[api_name] = tool_name
                            registered_count += 1
                        
                        self._registered_journeys.append(journey_id)
                        
                except Exception as e:
                    self.logger.error(f"Failed to process journey '{journey_id}': {e}")
                    continue
            
            # Also register solution-level APIs
            if self.control_tower and hasattr(self.control_tower, 'get_soa_apis'):
                for api_name, api_def in self.control_tower.get_soa_apis().items():
                    handler = api_def.get("handler")
                    if handler:
                        tool_name = f"tower_{api_name}"
                        
                        def create_tool_handler(handler_inner):
                            async def tool_handler(**parameters):
                                return await handler_inner(**parameters)
                            return tool_handler
                        
                        self.register_tool(
                            tool_name=tool_name,
                            handler=create_tool_handler(handler),
                            input_schema=api_def.get("input_schema", {}),
                            description=api_def.get("description", f"Control Tower: {api_name}")
                        )
                        self.soa_api_registry[api_name] = tool_name
                        registered_count += 1
            
            self.logger.info(f"🗼 Control Tower MCP Server initialized with {registered_count} tools")
            self.logger.info(f"   Registered journeys: {self._registered_journeys}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Control Tower MCP Server: {e}")
            return False
    
    def get_usage_guide(self) -> Dict[str, Any]:
        """Return usage guide for Control Tower MCP Server."""
        return {
            "server_name": "control_tower_mcp",
            "solution": "control_tower",
            "description": "Control Tower - Platform Command Center",
            "registered_journeys": self._registered_journeys,
            "tools": list(self.soa_api_registry.values()),
            "soa_api_mappings": self.soa_api_registry,
            "capabilities": [
                "platform_monitoring",
                "solution_management",
                "developer_documentation",
                "solution_composition"
            ],
            "usage_examples": [
                {
                    "tool": "tower_get_dashboard",
                    "description": "Get full Control Tower dashboard",
                    "example_parameters": {}
                },
                {
                    "tool": "tower_list_solutions",
                    "description": "List all deployed solutions",
                    "example_parameters": {}
                },
                {
                    "tool": "tower_get_patterns",
                    "description": "Get implementation patterns",
                    "example_parameters": {"pattern_type": "architecture"}
                },
                {
                    "tool": "tower_compose_solution",
                    "description": "Create a new solution from template",
                    "example_parameters": {
                        "template_id": "content_processing",
                        "solution_name": "My Custom Solution"
                    }
                }
            ]
        }
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get health status of Control Tower MCP Server."""
        base_status = await super().get_health_status()
        
        return {
            **base_status,
            "solution": "control_tower",
            "registered_journeys": self._registered_journeys,
            "journey_count": len(self._registered_journeys)
        }
