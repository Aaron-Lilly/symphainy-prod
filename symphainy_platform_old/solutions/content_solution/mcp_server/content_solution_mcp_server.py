"""
Content Solution MCP Server

Exposes Content Solution SOA APIs as MCP Tools for agent consumption.
Journey orchestrators "provide" MCP tools through this solution server.

WHAT (MCP Server Role): I expose Content Solution capabilities to agents
HOW (MCP Server Implementation): I collect SOA APIs from journeys and register as MCP tools

Key Principle: One MCP Server per Solution (not per realm/journey).
This prevents server sprawl while keeping tools organized.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, List, Optional
from utilities import get_logger
from symphainy_platform.civic_systems.agentic.mcp_server_base import MCPServerBase


class ContentSolutionMCPServer(MCPServerBase):
    """
    Content Solution MCP Server.
    
    Aggregates MCP tools from all Content Solution journeys:
    - FileUploadMaterializationJourney
    - FileParsingJourney (future)
    - DeterministicEmbeddingJourney (future)
    - FileManagementJourney (future)
    
    Tool naming convention: content_{journey_short_name}_{action}
    Example: content_upload_file, content_save_materialization
    """
    
    def __init__(
        self,
        solution,
        public_works: Optional[Any] = None,
        state_surface: Optional[Any] = None
    ):
        """
        Initialize Content Solution MCP Server.
        
        Args:
            solution: ContentSolution instance
            public_works: Public Works Foundation Service
            state_surface: State Surface for artifact management
        """
        super().__init__(
            service_name="content_solution_mcp",
            realm_name="content"
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
            self.logger.info("🔧 Initializing Content Solution MCP Server...")
            
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
                                
                                # Create tool name with content_ prefix
                                tool_name = f"content_{api_name}"
                                
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
                                    description=api_def.get("description", f"Content: {api_name}")
                                )
                                
                                # Track in SOA API registry
                                self.soa_api_registry[api_name] = tool_name
                                registered_count += 1
                                
                            except Exception as e:
                                self.logger.error(f"❌ Failed to register tool '{api_name}': {e}")
                                continue
                        
                        self._registered_journeys.append(journey_id)
                        
                except Exception as e:
                    self.logger.error(f"❌ Failed to process journey '{journey_id}': {e}")
                    continue
            
            # Also register solution-level SOA APIs if available
            if self.solution and hasattr(self.solution, 'get_soa_apis'):
                solution_apis = self.solution.get_soa_apis()
                
                for api_name, api_def in solution_apis.items():
                    try:
                        handler = api_def.get("handler")
                        if not handler:
                            continue
                        
                        tool_name = f"content_{api_name}"
                        
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
                            description=api_def.get("description", f"Content: {api_name}")
                        )
                        
                        self.soa_api_registry[api_name] = tool_name
                        registered_count += 1
                        
                    except Exception as e:
                        self.logger.error(f"❌ Failed to register solution API '{api_name}': {e}")
                        continue
            
            self.logger.info(f"✅ Content Solution MCP Server initialized with {registered_count} tools")
            self.logger.info(f"   Registered journeys: {self._registered_journeys}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to initialize Content Solution MCP Server: {e}")
            return False
    
    def get_usage_guide(self) -> Dict[str, Any]:
        """
        Return usage guide for this MCP server.
        
        Returns:
            Dict with server metadata and tool list
        """
        return {
            "server_name": "content_solution_mcp",
            "solution": "content_solution",
            "realm": "content",
            "description": "Content Solution MCP Server - Provides content management capabilities",
            "registered_journeys": self._registered_journeys,
            "tools": list(self.soa_api_registry.values()),
            "soa_api_mappings": self.soa_api_registry,
            "capabilities": [
                "file_upload",
                "file_materialization",
                "artifact_management"
            ],
            "usage_examples": [
                {
                    "tool": "content_upload_and_materialize",
                    "description": "Upload and materialize a file in one step",
                    "example_parameters": {
                        "file_content": "<base64 encoded file>",
                        "file_name": "example.pdf",
                        "content_type": "unstructured",
                        "file_type": "pdf"
                    }
                },
                {
                    "tool": "content_upload_file",
                    "description": "Upload a file (creates PENDING artifact)",
                    "example_parameters": {
                        "file_content": "<base64 encoded file>",
                        "file_name": "data.csv",
                        "content_type": "structured",
                        "file_type": "csv"
                    }
                },
                {
                    "tool": "content_save_materialization",
                    "description": "Save materialization (PENDING → READY)",
                    "example_parameters": {
                        "artifact_id": "<artifact_id from upload>"
                    }
                }
            ]
        }
    
    async def get_health_status(self) -> Dict[str, Any]:
        """
        Get health status of the MCP server.
        
        Returns:
            Dict with health status
        """
        base_status = await super().get_health_status()
        
        return {
            **base_status,
            "solution": "content_solution",
            "registered_journeys": self._registered_journeys,
            "journey_count": len(self._registered_journeys)
        }
