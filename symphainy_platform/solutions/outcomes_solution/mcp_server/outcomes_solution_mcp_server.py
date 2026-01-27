"""
Outcomes Solution MCP Server

Exposes Outcomes Solution SOA APIs as MCP Tools for agent consumption.
Journey orchestrators "provide" MCP tools through this solution server.

WHAT (MCP Server Role): I expose Outcomes Solution capabilities to agents
HOW (MCP Server Implementation): I collect SOA APIs from journeys and register as MCP tools

Key Principle: One MCP Server per Solution (not per realm/journey).
This prevents server sprawl while keeping tools organized.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, List, Optional
from utilities import get_logger
from symphainy_platform.civic_systems.agentic.mcp_server_base import MCPServerBase


class OutcomesSolutionMCPServer(MCPServerBase):
    """
    Outcomes Solution MCP Server.
    
    Aggregates MCP tools from all Outcomes Solution journeys:
    - OutcomeSynthesisJourney
    - RoadmapGenerationJourney
    - POCProposalJourney
    - BlueprintCreationJourney
    - SolutionCreationJourney
    - ArtifactExportJourney
    
    Tool naming convention: outcomes_{action}
    Example: outcomes_synthesize, outcomes_generate_roadmap
    """
    
    def __init__(
        self,
        solution,
        public_works: Optional[Any] = None,
        state_surface: Optional[Any] = None
    ):
        """
        Initialize Outcomes Solution MCP Server.
        
        Args:
            solution: OutcomesSolution instance
            public_works: Public Works Foundation Service
            state_surface: State Surface for artifact management
        """
        super().__init__(
            service_name="outcomes_solution_mcp",
            realm_name="outcomes"
        )
        self.solution = solution
        self.public_works = public_works
        self.state_surface = state_surface
        
        # Track registered journeys
        self._registered_journeys: List[str] = []
    
    async def initialize(self) -> bool:
        """
        Initialize MCP Server and register tools from all journeys.
        
        Collects SOA APIs from each journey orchestrator and registers
        them as MCP tools with appropriate prefixes.
        
        Returns:
            True if initialization successful
        """
        try:
            self.logger.info("Initializing Outcomes Solution MCP Server...")
            
            registered_count = 0
            
            # Register tools from each journey
            journeys = self.solution.get_journeys() if self.solution else {}
            
            for journey_id, journey in journeys.items():
                try:
                    # Get SOA APIs from journey
                    if hasattr(journey, 'get_soa_apis'):
                        soa_apis = journey.get_soa_apis()
                        
                        for api_name, api_def in soa_apis.items():
                            try:
                                handler = api_def.get("handler")
                                if not handler:
                                    continue
                                
                                # Create tool name with outcomes_ prefix
                                tool_name = f"outcomes_{api_name}"
                                
                                # Create tool handler wrapper
                                def create_tool_handler(handler_inner):
                                    async def tool_handler(**parameters):
                                        if callable(handler_inner):
                                            return await handler_inner(**parameters)
                                        else:
                                            raise ValueError(f"Handler is not callable")
                                    return tool_handler
                                
                                tool_handler = create_tool_handler(handler)
                                
                                # Get input schema
                                input_schema = api_def.get("input_schema", {
                                    "type": "object",
                                    "properties": {},
                                    "required": []
                                })
                                
                                # Register tool
                                self.register_tool(
                                    tool_name=tool_name,
                                    handler=tool_handler,
                                    input_schema=input_schema,
                                    description=api_def.get("description", f"Outcomes: {api_name}")
                                )
                                
                                # Track in SOA API registry
                                self.soa_api_registry[api_name] = tool_name
                                registered_count += 1
                                
                            except Exception as e:
                                self.logger.error(f"Failed to register tool '{api_name}': {e}")
                                continue
                        
                        self._registered_journeys.append(journey_id)
                        
                except Exception as e:
                    self.logger.error(f"Failed to process journey '{journey_id}': {e}")
                    continue
            
            # Also register solution-level SOA APIs if available
            if self.solution and hasattr(self.solution, 'get_soa_apis'):
                solution_apis = self.solution.get_soa_apis()
                
                for api_name, api_def in solution_apis.items():
                    try:
                        handler = api_def.get("handler")
                        if not handler:
                            continue
                        
                        tool_name = f"outcomes_{api_name}"
                        
                        def create_tool_handler(handler_inner):
                            async def tool_handler(**parameters):
                                if callable(handler_inner):
                                    return await handler_inner(**parameters)
                                else:
                                    raise ValueError(f"Handler is not callable")
                            return tool_handler
                        
                        tool_handler = create_tool_handler(handler)
                        
                        input_schema = api_def.get("input_schema", {
                            "type": "object",
                            "properties": {},
                            "required": []
                        })
                        
                        self.register_tool(
                            tool_name=tool_name,
                            handler=tool_handler,
                            input_schema=input_schema,
                            description=api_def.get("description", f"Outcomes: {api_name}")
                        )
                        
                        self.soa_api_registry[api_name] = tool_name
                        registered_count += 1
                        
                    except Exception as e:
                        self.logger.error(f"Failed to register solution API '{api_name}': {e}")
                        continue
            
            self.logger.info(f"Outcomes Solution MCP Server initialized with {registered_count} tools")
            self.logger.info(f"Registered journeys: {self._registered_journeys}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Outcomes Solution MCP Server: {e}")
            return False
    
    def get_usage_guide(self) -> Dict[str, Any]:
        """
        Return usage guide for this MCP server.
        
        Returns:
            Dict with server metadata and tool list
        """
        return {
            "server_name": "outcomes_solution_mcp",
            "solution": "outcomes_solution",
            "realm": "outcomes",
            "description": "Outcomes Solution MCP Server - provides tools for outcome synthesis, roadmap generation, POC creation, blueprint creation, solution creation, and artifact export",
            "tools": list(self.soa_api_registry.values()),
            "registered_journeys": self._registered_journeys,
            "naming_convention": "outcomes_{action}",
            "available_tools": {
                "outcomes_synthesize": "Synthesize outcomes from all pillars",
                "outcomes_generate_roadmap": "Generate strategic roadmap from goals",
                "outcomes_create_poc": "Create POC proposal from description",
                "outcomes_create_blueprint": "Create coexistence blueprint from workflow",
                "outcomes_create_solution": "Create platform solution from artifact",
                "outcomes_export_artifact": "Export artifact in various formats",
                "outcomes_compose_journey": "Invoke a journey by ID",
                "outcomes_get_journeys": "List all available journeys",
                "outcomes_get_journey_status": "Get journey execution status"
            },
            "usage_examples": [
                {
                    "tool": "outcomes_synthesize",
                    "description": "Synthesize outcomes from all pillars",
                    "parameters": {
                        "tenant_id": "tenant_123",
                        "session_id": "session_456"
                    }
                },
                {
                    "tool": "outcomes_generate_roadmap",
                    "description": "Generate a strategic roadmap",
                    "parameters": {
                        "goals": ["Migrate to cloud", "Improve data quality"],
                        "tenant_id": "tenant_123",
                        "session_id": "session_456"
                    }
                },
                {
                    "tool": "outcomes_create_poc",
                    "description": "Create a POC proposal",
                    "parameters": {
                        "description": "Data migration proof of concept",
                        "tenant_id": "tenant_123",
                        "session_id": "session_456"
                    }
                }
            ]
        }
    
    async def get_health_status(self) -> Dict[str, Any]:
        """
        Get health status of the MCP server.
        
        Returns:
            Dict with health status information
        """
        return {
            "status": "healthy",
            "server_name": "outcomes_solution_mcp",
            "registered_tools_count": len(self.soa_api_registry),
            "registered_journeys": self._registered_journeys,
            "solution_available": self.solution is not None,
            "public_works_available": self.public_works is not None,
            "state_surface_available": self.state_surface is not None
        }
