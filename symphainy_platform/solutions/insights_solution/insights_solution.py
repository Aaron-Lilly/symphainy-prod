"""
Insights Solution - Insights Realm Solution

Composes insights journeys for data analysis, quality assessment, and semantic discovery.

WHAT (Solution Role): I provide insights capabilities for the platform
HOW (Solution Implementation): I compose insights journeys and expose SOA APIs
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional
from utilities import get_logger, generate_event_id, get_clock
from symphainy_platform.runtime.intent_model import Intent, IntentFactory
from symphainy_platform.runtime.execution_context import ExecutionContext
from symphainy_platform.realms.utils.structured_artifacts import create_structured_artifact

from .journeys.business_analysis_journey import BusinessAnalysisJourney
from .journeys.data_quality_journey import DataQualityJourney


class InsightsSolution:
    """
    Insights Solution - Insights Realm Solution.
    
    Composes insights journeys:
    - BusinessAnalysisJourney
    - DataQualityJourney
    """
    
    SOLUTION_ID = "insights_solution"
    SOLUTION_NAME = "Insights Solution"
    
    SUPPORTED_INTENTS = [
        "compose_journey",
        "extract_structured_data",
        "analyze_patterns",
        "assess_data_quality",
        "generate_quality_report",
        "validate_schema",
        "map_relationships",
        "visualize_lineage"
    ]
    
    def __init__(self, public_works: Optional[Any] = None, state_surface: Optional[Any] = None):
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
        self.public_works = public_works
        self.state_surface = state_surface
        self.solution_id = self.SOLUTION_ID
        self.solution_name = self.SOLUTION_NAME
        
        self._journeys: Dict[str, Any] = {}
        self._initialize_journeys()
        
        self._mcp_server = None
    
    def _initialize_journeys(self):
        """Initialize all journey orchestrators."""
        self._journeys["business_analysis"] = BusinessAnalysisJourney(
            public_works=self.public_works,
            state_surface=self.state_surface
        )
        self._journeys["data_quality"] = DataQualityJourney(
            public_works=self.public_works,
            state_surface=self.state_surface
        )
        self.logger.info(f"Initialized {len(self._journeys)} journey orchestrators")
    
    def get_journeys(self) -> Dict[str, Any]:
        return self._journeys.copy()
    
    def get_journey(self, journey_id: str) -> Optional[Any]:
        return self._journeys.get(journey_id)
    
    async def initialize_mcp_server(self):
        if not self._mcp_server:
            from .mcp_server.insights_solution_mcp_server import InsightsSolutionMCPServer
            self._mcp_server = InsightsSolutionMCPServer(
                solution=self,
                public_works=self.public_works,
                state_surface=self.state_surface
            )
            await self._mcp_server.initialize()
        return self._mcp_server
    
    async def handle_intent(self, intent: Intent, context: ExecutionContext) -> Dict[str, Any]:
        intent_type = intent.intent_type
        self.logger.info(f"Handling intent: {intent_type}")
        
        if intent_type == "compose_journey":
            return await self._handle_compose_journey(intent, context)
        
        journey = self._find_journey_for_intent(intent_type)
        if journey:
            return await journey.compose_journey(context, intent.parameters)
        
        raise ValueError(f"Unknown intent type: {intent_type}")
    
    def _find_journey_for_intent(self, intent_type: str) -> Optional[Any]:
        intent_to_journey = {
            "extract_structured_data": "business_analysis",
            "analyze_patterns": "business_analysis",
            "assess_data_quality": "data_quality",
            "generate_quality_report": "data_quality",
            "validate_schema": "data_quality",
        }
        journey_id = intent_to_journey.get(intent_type)
        return self._journeys.get(journey_id) if journey_id else None
    
    async def _handle_compose_journey(self, intent: Intent, context: ExecutionContext) -> Dict[str, Any]:
        journey_id = intent.parameters.get("journey_id")
        journey_params = intent.parameters.get("journey_params", {})
        
        if not journey_id:
            raise ValueError("journey_id is required")
        
        journey = self._journeys.get(journey_id)
        if not journey:
            raise ValueError(f"Unknown journey: {journey_id}")
        
        return await journey.compose_journey(context, journey_params)
    
    def get_soa_apis(self) -> Dict[str, Dict[str, Any]]:
        return {
            "compose_journey": {
                "handler": self._handle_compose_journey_soa,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "journey_id": {"type": "string"},
                        "journey_params": {"type": "object"},
                        "user_context": {"type": "object"}
                    },
                    "required": ["journey_id"]
                },
                "description": "Compose and execute an insights journey"
            },
            "list_journeys": {
                "handler": self._handle_list_journeys_soa,
                "input_schema": {"type": "object", "properties": {}},
                "description": "List available insights journeys"
            }
        }
    
    async def _handle_compose_journey_soa(self, **kwargs) -> Dict[str, Any]:
        user_context = kwargs.get("user_context", {})
        context = ExecutionContext(
            execution_id=generate_event_id(),
            tenant_id=user_context.get("tenant_id", "default"),
            session_id=user_context.get("session_id", generate_event_id()),
            solution_id=self.solution_id
        )
        context.state_surface = self.state_surface
        
        intent = IntentFactory.create_intent(
            intent_type="compose_journey",
            tenant_id=context.tenant_id,
            session_id=context.session_id,
            solution_id=self.solution_id,
            parameters={"journey_id": kwargs.get("journey_id"), "journey_params": kwargs.get("journey_params", {})}
        )
        return await self._handle_compose_journey(intent, context)
    
    async def _handle_list_journeys_soa(self, **kwargs) -> Dict[str, Any]:
        return {
            "success": True,
            "solution_id": self.solution_id,
            "journeys": [{"journey_id": jid, "journey_name": getattr(j, 'JOURNEY_NAME', jid)} for jid, j in self._journeys.items()]
        }
