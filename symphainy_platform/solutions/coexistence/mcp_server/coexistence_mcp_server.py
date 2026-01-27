"""
Coexistence MCP Server

Exposes Coexistence Solution capabilities as MCP Tools.
Tool naming convention: coexist_{action}

Examples:
- coexist_introduce_platform
- coexist_navigate_to_solution
- coexist_initiate_guide_agent
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional
from utilities import get_logger
from symphainy_platform.civic_systems.agentic.mcp_server_base import MCPServerBase


class CoexistenceMCPServer(MCPServerBase):
    """
    Coexistence MCP Server.
    
    Aggregates tools from all Coexistence journeys:
    - IntroductionJourney: coexist_introduce_platform, coexist_show_catalog, etc.
    - NavigationJourney: coexist_navigate_to_solution, coexist_get_context, etc.
    - GuideAgentJourney: coexist_initiate_guide_agent, coexist_send_message, etc.
    """
    
    def __init__(
        self,
        coexistence_solution,
        public_works: Optional[Any] = None,
        state_surface: Optional[Any] = None
    ):
        super().__init__(
            service_name="coexistence_mcp",
            realm_name="coexistence"
        )
        self.coexistence_solution = coexistence_solution
        self.public_works = public_works
        self.state_surface = state_surface
        self._registered_journeys = []
    
    async def initialize(self) -> bool:
        """Initialize MCP Server and register tools from all journeys."""
        try:
            self.logger.info("🌐 Initializing Coexistence MCP Server...")
            registered_count = 0
            
            journeys = self.coexistence_solution.get_journeys() if self.coexistence_solution else {}
            
            for journey_id, journey in journeys.items():
                try:
                    if hasattr(journey, 'get_soa_apis'):
                        soa_apis = journey.get_soa_apis()
                        
                        for api_name, api_def in soa_apis.items():
                            handler = api_def.get("handler")
                            if not handler:
                                continue
                            
                            # Use coexist_ prefix for all tools
                            tool_name = f"coexist_{api_name}"
                            
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
                                description=api_def.get("description", f"Coexistence: {api_name}")
                            )
                            
                            self.soa_api_registry[api_name] = tool_name
                            registered_count += 1
                        
                        self._registered_journeys.append(journey_id)
                        
                except Exception as e:
                    self.logger.error(f"Failed to process journey '{journey_id}': {e}")
                    continue
            
            # Also register solution-level APIs
            if self.coexistence_solution and hasattr(self.coexistence_solution, 'get_soa_apis'):
                for api_name, api_def in self.coexistence_solution.get_soa_apis().items():
                    handler = api_def.get("handler")
                    if handler:
                        tool_name = f"coexist_{api_name}"
                        
                        def create_tool_handler(handler_inner):
                            async def tool_handler(**parameters):
                                return await handler_inner(**parameters)
                            return tool_handler
                        
                        self.register_tool(
                            tool_name=tool_name,
                            handler=create_tool_handler(handler),
                            input_schema=api_def.get("input_schema", {}),
                            description=api_def.get("description", f"Coexistence: {api_name}")
                        )
                        self.soa_api_registry[api_name] = tool_name
                        registered_count += 1
            
            self.logger.info(f"🌐 Coexistence MCP Server initialized with {registered_count} tools")
            self.logger.info(f"   Registered journeys: {self._registered_journeys}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Coexistence MCP Server: {e}")
            return False
    
    def get_usage_guide(self) -> Dict[str, Any]:
        """Return usage guide for Coexistence MCP Server."""
        return {
            "server_name": "coexistence_mcp",
            "solution": "coexistence",
            "description": "Coexistence Solution - Platform Entry Point & Navigation",
            "registered_journeys": self._registered_journeys,
            "tools": list(self.soa_api_registry.values()),
            "soa_api_mappings": self.soa_api_registry,
            "capabilities": [
                "platform_introduction",
                "solution_navigation",
                "guide_agent_interaction"
            ],
            "usage_examples": [
                {
                    "tool": "coexist_introduce_platform",
                    "description": "Welcome a new user to the platform",
                    "example_parameters": {"user_name": "John"}
                },
                {
                    "tool": "coexist_show_catalog",
                    "description": "Show available solutions",
                    "example_parameters": {}
                },
                {
                    "tool": "coexist_initiate_guide_agent",
                    "description": "Start conversation with Guide Agent",
                    "example_parameters": {"current_pillar": "content"}
                },
                {
                    "tool": "coexist_navigate_to_solution",
                    "description": "Navigate to a specific solution",
                    "example_parameters": {"solution_id": "content_solution"}
                }
            ]
        }
