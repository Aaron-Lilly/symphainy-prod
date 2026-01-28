"""
Insights Solution - Insights Realm Platform Solution

The top-level solution that composes insights journeys, exposes SOA APIs,
and wires up with the frontend via Experience SDK.

WHAT (Solution Role): I provide insights capabilities for the platform
HOW (Solution Implementation): I compose insights journeys and expose SOA APIs

Key Principle: The platform runs Solutions; Solutions run systems.
Solutions bind domain services to external systems.

Architecture:
- InsightsSolution composes journey orchestrators
- Each journey orchestrator provides SOA APIs
- InsightsSolutionMCPServer aggregates and exposes all SOA APIs as MCP tools
- compose_journey intent allows invoking journeys programmatically

Naming Convention:
- Realm: Insights Realm
- Solution: InsightsSolution (platform construct)
- Artifacts: insights_* prefix
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional, List
from utilities import get_logger, generate_event_id, get_clock
from symphainy_platform.runtime.intent_model import Intent, IntentFactory
from symphainy_platform.runtime.execution_context import ExecutionContext
from symphainy_platform.civic_systems.platform_sdk.solution_model import Solution
from symphainy_platform.civic_systems.platform_sdk.solution_builder import SolutionBuilder

# Import journey orchestrators
from .journeys.data_quality_journey import DataQualityJourney
from .journeys.data_interpretation_journey import DataInterpretationJourney
from .journeys.data_analysis_journey import DataAnalysisJourney
from .journeys.lineage_visualization_journey import LineageVisualizationJourney
from .journeys.relationship_mapping_journey import RelationshipMappingJourney
from .journeys.business_analysis_journey import BusinessAnalysisJourney


class InsightsSolution:
    """
    Insights Solution - Insights Realm Platform Solution.
    
    Composes insights journeys:
    - DataQualityJourney: Assess data quality
    - DataInterpretationJourney: Self-discovery and guided interpretation
    - DataAnalysisJourney: Structured and unstructured data analysis
    - LineageVisualizationJourney: Visualize data lineage
    - RelationshipMappingJourney: Map entity relationships
    
    Exposes SOA APIs:
    - compose_journey: Invoke a journey by ID
    - get_journeys: List available journeys
    - get_journey_status: Get journey execution status
    
    Supports compose_journey intent pattern for programmatic journey invocation.
    """
    
    SOLUTION_ID = "insights_solution"
    SOLUTION_NAME = "Insights Solution"
    
    SUPPORTED_INTENTS = [
        "compose_journey",
        "assess_data_quality",
        "interpret_data_self_discovery",
        "interpret_data_guided",
        "analyze_structured_data",
        "analyze_unstructured_data",
        "visualize_lineage",
        "map_relationships",
        "extract_structured_data"  # Extract structured data from unstructured content
    ]
    
    def __init__(
        self,
        public_works: Optional[Any] = None,
        state_surface: Optional[Any] = None
    ):
        """Initialize Insights Solution."""
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
        self.public_works = public_works
        self.state_surface = state_surface
        
        self.solution_id = self.SOLUTION_ID
        self.solution_name = self.SOLUTION_NAME
        
        self._journeys: Dict[str, Any] = {}
        self._initialize_journeys()
        
        self._solution_model = self._build_solution_model()
        self._mcp_server = None
        self.telemetry_service = None
    
    def _initialize_journeys(self):
        """Initialize all journey orchestrators."""
        self._journeys["data_quality"] = DataQualityJourney(
            public_works=self.public_works,
            state_surface=self.state_surface
        )
        
        self._journeys["data_interpretation"] = DataInterpretationJourney(
            public_works=self.public_works,
            state_surface=self.state_surface
        )
        
        self._journeys["data_analysis"] = DataAnalysisJourney(
            public_works=self.public_works,
            state_surface=self.state_surface
        )
        
        self._journeys["lineage_visualization"] = LineageVisualizationJourney(
            public_works=self.public_works,
            state_surface=self.state_surface
        )
        
        self._journeys["relationship_mapping"] = RelationshipMappingJourney(
            public_works=self.public_works,
            state_surface=self.state_surface
        )
        
        self._journeys["business_analysis"] = BusinessAnalysisJourney(
            public_works=self.public_works,
            state_surface=self.state_surface
        )
        
        self.logger.info(f"Initialized {len(self._journeys)} journey orchestrators")
    
    def _build_solution_model(self) -> Solution:
        """Build formal Solution model."""
        builder = SolutionBuilder(solution_id=self.solution_id)
        
        builder.with_context(
            goals=[
                "Assess data quality across parsing, data, and source dimensions",
                "Interpret data through self-discovery and guided methods",
                "Analyze structured and unstructured data for business insights",
                "Visualize data lineage and relationship graphs"
            ],
            constraints=[
                "All operations via intents (no direct API calls)",
                "All artifacts registered in Artifact Plane",
                "No backward compatibility - follow current patterns only"
            ],
            risk="Low"
        )
        
        builder.add_domain_binding(
            domain="insights",
            system_name="artifact_storage",
            adapter_type="artifact_plane_adapter",
            adapter_config={"artifact_prefix": "insights_"}
        )
        
        builder.register_intents(self.SUPPORTED_INTENTS)
        
        builder.with_metadata({
            "solution_name": self.SOLUTION_NAME,
            "version": "1.0.0",
            "journeys": list(self._journeys.keys())
        })
        
        return builder.build()
    
    def get_journeys(self) -> Dict[str, Any]:
        """Get all journey orchestrators."""
        return self._journeys.copy()
    
    def get_journey(self, journey_id: str) -> Optional[Any]:
        """Get a specific journey orchestrator."""
        return self._journeys.get(journey_id)
    
    async def initialize_mcp_server(self):
        """Initialize MCP server."""
        if not self._mcp_server:
            from .mcp_server.insights_solution_mcp_server import InsightsSolutionMCPServer
            
            self._mcp_server = InsightsSolutionMCPServer(
                solution=self,
                public_works=self.public_works,
                state_surface=self.state_surface
            )
            await self._mcp_server.initialize()
        
        return self._mcp_server
    
    def get_mcp_server(self):
        """Get MCP server instance."""
        return self._mcp_server
    
    async def handle_intent(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Handle intent by routing to appropriate journey or handler."""
        intent_type = intent.intent_type
        
        self.logger.info(f"Handling intent: {intent_type}")
        
        await self._ensure_telemetry()
        
        if intent_type == "compose_journey":
            return await self._handle_compose_journey(intent, context)
        
        journey = self._find_journey_for_intent(intent_type)
        if journey:
            return await journey.compose_journey(context, intent.parameters)
        
        raise ValueError(f"Unknown intent type: {intent_type} (Solution: {self.solution_id})")
    
    def _find_journey_for_intent(self, intent_type: str) -> Optional[Any]:
        """Find the journey that handles a given intent type."""
        intent_to_journey = {
            "assess_data_quality": "data_quality",
            "interpret_data_self_discovery": "data_interpretation",
            "interpret_data_guided": "data_interpretation",
            "analyze_structured_data": "data_analysis",
            "analyze_unstructured_data": "data_analysis",
            "visualize_lineage": "lineage_visualization",
            "map_relationships": "relationship_mapping",
            "extract_structured_data": "business_analysis",
        }
        
        journey_id = intent_to_journey.get(intent_type)
        if journey_id:
            return self._journeys.get(journey_id)
        
        return None
    
    async def _handle_compose_journey(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Handle compose_journey intent."""
        journey_id = intent.parameters.get("journey_id")
        journey_params = intent.parameters.get("journey_params", {})
        
        if not journey_id:
            raise ValueError("journey_id is required for compose_journey intent")
        
        journey = self._journeys.get(journey_id)
        if not journey:
            available = list(self._journeys.keys())
            raise ValueError(f"Unknown journey: {journey_id}. Available: {available}")
        
        self.logger.info(f"Composing journey: {journey_id}")
        
        return await journey.compose_journey(context, journey_params)
    
    def get_soa_apis(self) -> Dict[str, Dict[str, Any]]:
        """Get solution-level SOA APIs."""
        return {
            "compose_journey": {
                "handler": self._soa_compose_journey,
                "description": "Invoke an insights journey by ID",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "journey_id": {
                            "type": "string",
                            "enum": list(self._journeys.keys())
                        },
                        "journey_params": {"type": "object"},
                        "tenant_id": {"type": "string"},
                        "session_id": {"type": "string"}
                    },
                    "required": ["journey_id", "tenant_id", "session_id"]
                }
            },
            "get_journeys": {
                "handler": self._soa_get_journeys,
                "description": "List all available insights journeys",
                "input_schema": {"type": "object", "properties": {}, "required": []}
            }
        }
    
    async def _soa_compose_journey(
        self,
        journey_id: str,
        tenant_id: str,
        session_id: str,
        journey_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """SOA API: Compose journey by ID."""
        execution_id = generate_event_id()
        
        context = ExecutionContext(
            execution_id=execution_id,
            tenant_id=tenant_id,
            session_id=session_id,
            intent=None,
            state_surface=self.state_surface
        )
        
        journey = self._journeys.get(journey_id)
        if not journey:
            return {"success": False, "error": f"Unknown journey: {journey_id}"}
        
        try:
            return await journey.compose_journey(context, journey_params or {})
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _soa_get_journeys(self) -> Dict[str, Any]:
        """SOA API: Get all available journeys."""
        journeys_info = []
        
        for journey_id, journey in self._journeys.items():
            journeys_info.append({
                "journey_id": journey_id,
                "journey_name": getattr(journey, 'JOURNEY_NAME', journey_id),
                "description": getattr(journey, '__doc__', '').split('\n')[0].strip() if getattr(journey, '__doc__', None) else ''
            })
        
        return {"success": True, "solution_id": self.solution_id, "journeys": journeys_info}
    
    def get_experience_sdk_config(self) -> Dict[str, Any]:
        """Get Experience SDK configuration for frontend integration."""
        return {
            "solution_id": self.solution_id,
            "solution_name": self.solution_name,
            "supported_intents": self.SUPPORTED_INTENTS,
            "available_journeys": list(self._journeys.keys()),
            "mcp_server_available": self._mcp_server is not None,
            "soa_apis": list(self.get_soa_apis().keys())
        }
    
    async def _ensure_telemetry(self):
        """Ensure telemetry service is initialized."""
        if not self.telemetry_service and self.public_works:
            try:
                self.telemetry_service = self.public_works.get_telemetry_service()
            except Exception:
                pass
