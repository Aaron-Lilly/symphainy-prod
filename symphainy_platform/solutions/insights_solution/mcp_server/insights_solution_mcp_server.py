"""
Insights Solution MCP Server

Exposes Insights Solution SOA APIs as MCP Tools for agent consumption.

WHAT (MCP Server Role): I expose Insights Solution capabilities to agents
HOW (MCP Server Implementation): I collect SOA APIs from journeys and register as MCP tools

Key Principle: One MCP Server per Solution (not per realm/journey).
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, List, Optional
from utilities import get_logger
from symphainy_platform.civic_systems.agentic.mcp_server_base import MCPServerBase


class InsightsSolutionMCPServer(MCPServerBase):
    """
    Insights Solution MCP Server.
    
    Aggregates MCP tools from all Insights Solution journeys:
    - DataQualityJourney
    - DataInterpretationJourney
    - DataAnalysisJourney
    - LineageVisualizationJourney
    - RelationshipMappingJourney
    
    Tool naming convention: insights_{action}
    Example: insights_assess_quality, insights_analyze_structured
    """
    
    def __init__(
        self,
        solution,
        public_works: Optional[Any] = None,
        state_surface: Optional[Any] = None
    ):
        super().__init__(
            service_name="insights_solution_mcp",
            realm_name="insights"
        )
        self.solution = solution
        self.public_works = public_works
        self.state_surface = state_surface
        self._registered_journeys: List[str] = []
    
    async def initialize(self) -> bool:
        """Initialize MCP Server and register tools from all journeys."""
        try:
            self.logger.info("Initializing Insights Solution MCP Server...")
            
            registered_count = 0
            journeys = self.solution.get_journeys() if self.solution else {}
            
            for journey_id, journey in journeys.items():
                try:
                    if hasattr(journey, 'get_soa_apis'):
                        soa_apis = journey.get_soa_apis()
                        
                        for api_name, api_def in soa_apis.items():
                            try:
                                handler = api_def.get("handler")
                                if not handler:
                                    continue
                                
                                tool_name = f"insights_{api_name}"
                                
                                def create_tool_handler(handler_inner):
                                    async def tool_handler(**parameters):
                                        if callable(handler_inner):
                                            return await handler_inner(**parameters)
                                        raise ValueError("Handler is not callable")
                                    return tool_handler
                                
                                tool_handler = create_tool_handler(handler)
                                
                                input_schema = api_def.get("input_schema", {
                                    "type": "object", "properties": {}, "required": []
                                })
                                
                                self.register_tool(
                                    tool_name=tool_name,
                                    handler=tool_handler,
                                    input_schema=input_schema,
                                    description=api_def.get("description", f"Insights: {api_name}")
                                )
                                
                                self.soa_api_registry[api_name] = tool_name
                                registered_count += 1
                                
                            except Exception as e:
                                self.logger.error(f"Failed to register tool '{api_name}': {e}")
                        
                        self._registered_journeys.append(journey_id)
                        
                except Exception as e:
                    self.logger.error(f"Failed to process journey '{journey_id}': {e}")
            
            # Register solution-level SOA APIs
            if self.solution and hasattr(self.solution, 'get_soa_apis'):
                solution_apis = self.solution.get_soa_apis()
                
                for api_name, api_def in solution_apis.items():
                    try:
                        handler = api_def.get("handler")
                        if not handler:
                            continue
                        
                        tool_name = f"insights_{api_name}"
                        
                        def create_tool_handler(handler_inner):
                            async def tool_handler(**parameters):
                                if callable(handler_inner):
                                    return await handler_inner(**parameters)
                                raise ValueError("Handler is not callable")
                            return tool_handler
                        
                        tool_handler = create_tool_handler(handler)
                        
                        input_schema = api_def.get("input_schema", {
                            "type": "object", "properties": {}, "required": []
                        })
                        
                        self.register_tool(
                            tool_name=tool_name,
                            handler=tool_handler,
                            input_schema=input_schema,
                            description=api_def.get("description", f"Insights: {api_name}")
                        )
                        
                        self.soa_api_registry[api_name] = tool_name
                        registered_count += 1
                        
                    except Exception as e:
                        self.logger.error(f"Failed to register solution API '{api_name}': {e}")
            
            self.logger.info(f"Insights Solution MCP Server initialized with {registered_count} tools")
            self.logger.info(f"Registered journeys: {self._registered_journeys}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Insights Solution MCP Server: {e}")
            return False
    
    def get_usage_guide(self) -> Dict[str, Any]:
        """Return usage guide for this MCP server."""
        return {
            "server_name": "insights_solution_mcp",
            "solution": "insights_solution",
            "realm": "insights",
            "description": "Insights Solution MCP Server - provides tools for data quality assessment, interpretation, analysis, lineage visualization, and relationship mapping",
            "tools": list(self.soa_api_registry.values()),
            "registered_journeys": self._registered_journeys,
            "naming_convention": "insights_{action}",
            "available_tools": {
                "insights_assess_quality": "Assess data quality for a parsed file",
                "insights_interpret_self_discovery": "Self-discovery interpretation",
                "insights_interpret_guided": "Guided interpretation with guide",
                "insights_analyze_structured": "Analyze structured data",
                "insights_analyze_unstructured": "Analyze unstructured data",
                "insights_visualize_lineage": "Visualize data lineage (Your Data Mash)",
                "insights_map_relationships": "Map entity relationships",
                "insights_compose_journey": "Invoke a journey by ID",
                "insights_get_journeys": "List all available journeys"
            },
            "usage_examples": [
                {
                    "tool": "insights_assess_quality",
                    "description": "Assess data quality",
                    "parameters": {
                        "parsed_file_id": "file_123",
                        "tenant_id": "tenant_123",
                        "session_id": "session_456"
                    }
                },
                {
                    "tool": "insights_analyze_structured",
                    "description": "Analyze structured data",
                    "parameters": {
                        "parsed_file_id": "file_123",
                        "tenant_id": "tenant_123",
                        "session_id": "session_456"
                    }
                }
            ]
        }
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get health status of the MCP server."""
        return {
            "status": "healthy",
            "server_name": "insights_solution_mcp",
            "registered_tools_count": len(self.soa_api_registry),
            "registered_journeys": self._registered_journeys,
            "solution_available": self.solution is not None,
            "public_works_available": self.public_works is not None,
            "state_surface_available": self.state_surface is not None
        }
