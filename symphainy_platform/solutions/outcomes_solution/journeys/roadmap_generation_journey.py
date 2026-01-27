"""
Roadmap Generation Journey Orchestrator

Composes the roadmap generation journey:
1. Validate goals input
2. Execute generate_roadmap intent
3. Store roadmap in Artifact Plane
4. Return roadmap artifact reference

WHAT (Journey Role): I orchestrate strategic roadmap generation
HOW (Journey Implementation): I compose generate_roadmap intent

Key Principle: Journey orchestrators compose intent services into journeys.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional, List
from utilities import get_logger, generate_event_id, get_clock
from symphainy_platform.runtime.execution_context import ExecutionContext


class RoadmapGenerationJourney:
    """
    Roadmap Generation Journey Orchestrator.
    
    Journey Flow:
    1. Validate goals (required)
    2. Execute generate_roadmap intent
    3. Store roadmap artifact
    4. Return roadmap reference
    
    Provides MCP Tools:
    - outcomes_generate_roadmap: Generate strategic roadmap from goals
    """
    
    JOURNEY_ID = "roadmap_generation"
    JOURNEY_NAME = "Roadmap Generation"
    
    def __init__(
        self,
        public_works: Optional[Any] = None,
        state_surface: Optional[Any] = None
    ):
        """
        Initialize Roadmap Generation Journey.
        
        Args:
            public_works: Public Works Foundation Service
            state_surface: State Surface for artifact management
        """
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
        self.public_works = public_works
        self.state_surface = state_surface
        
        self.journey_id = self.JOURNEY_ID
        self.journey_name = self.JOURNEY_NAME
        
        self._intent_service = None
        self.telemetry_service = None
    
    async def compose_journey(
        self,
        context: ExecutionContext,
        journey_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Compose the roadmap generation journey.
        
        Args:
            context: Execution context
            journey_params: Journey parameters including:
                - goals: List of business goals (required)
                - timeline_months: Optional timeline in months
                - priority_focus: Optional priority focus area
        
        Returns:
            Journey result with roadmap artifact
        """
        journey_params = journey_params or {}
        
        self.logger.info(f"Composing journey: {self.journey_name}")
        
        await self._ensure_telemetry()
        
        journey_execution_id = generate_event_id()
        await self._record_telemetry({
            "action": "journey_started",
            "journey_id": self.journey_id,
            "journey_execution_id": journey_execution_id
        }, context.tenant_id)
        
        try:
            # Validate required parameters
            goals = journey_params.get("goals", [])
            if not goals:
                raise ValueError("goals is required for roadmap generation")
            
            # Get intent service
            intent_service = await self._get_intent_service()
            
            # Execute generate_roadmap intent
            result = await intent_service.execute(context, journey_params)
            
            # Build journey result
            journey_result = self._build_journey_result(
                intent_result=result,
                journey_execution_id=journey_execution_id
            )
            
            await self._record_telemetry({
                "action": "journey_completed",
                "journey_id": self.journey_id,
                "journey_execution_id": journey_execution_id,
                "goals_count": len(goals)
            }, context.tenant_id)
            
            return journey_result
            
        except Exception as e:
            self.logger.error(f"Journey failed: {e}", exc_info=True)
            
            await self._record_telemetry({
                "action": "journey_failed",
                "journey_id": self.journey_id,
                "journey_execution_id": journey_execution_id,
                "error": str(e)
            }, context.tenant_id)
            
            return {
                "success": False,
                "error": str(e),
                "journey_id": self.journey_id,
                "journey_execution_id": journey_execution_id,
                "artifacts": {},
                "events": [{"type": "journey_failed", "journey_id": self.journey_id, "error": str(e)}]
            }
    
    async def _get_intent_service(self):
        """Get or create the intent service."""
        if not self._intent_service:
            from symphainy_coexistence_fabric.symphainy_platform.realms.outcomes.intent_services import (
                GenerateRoadmapService
            )
            self._intent_service = GenerateRoadmapService(
                public_works=self.public_works,
                state_surface=self.state_surface
            )
        return self._intent_service
    
    def _build_journey_result(
        self,
        intent_result: Dict[str, Any],
        journey_execution_id: str
    ) -> Dict[str, Any]:
        """Build journey result from intent result."""
        return {
            "success": True,
            "journey_id": self.journey_id,
            "journey_execution_id": journey_execution_id,
            "artifacts": intent_result.get("artifacts", {}),
            "events": [
                {"type": "journey_completed", "journey_id": self.journey_id, "journey_execution_id": journey_execution_id},
                *intent_result.get("events", [])
            ]
        }
    
    def get_soa_apis(self) -> Dict[str, Dict[str, Any]]:
        """Get SOA APIs provided by this journey."""
        return {
            "generate_roadmap": {
                "handler": self._soa_generate_roadmap,
                "description": "Generate strategic roadmap from business goals",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "goals": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of business goals"
                        },
                        "timeline_months": {
                            "type": "integer",
                            "description": "Timeline in months"
                        },
                        "priority_focus": {
                            "type": "string",
                            "description": "Priority focus area"
                        },
                        "tenant_id": {"type": "string", "description": "Tenant identifier"},
                        "session_id": {"type": "string", "description": "Session identifier"}
                    },
                    "required": ["goals", "tenant_id", "session_id"]
                }
            }
        }
    
    async def _soa_generate_roadmap(
        self,
        goals: List[str],
        tenant_id: str,
        session_id: str,
        timeline_months: Optional[int] = None,
        priority_focus: Optional[str] = None
    ) -> Dict[str, Any]:
        """SOA API: Generate roadmap."""
        execution_id = generate_event_id()
        
        context = ExecutionContext(
            execution_id=execution_id,
            tenant_id=tenant_id,
            session_id=session_id,
            intent=None,
            state_surface=self.state_surface
        )
        
        journey_params = {"goals": goals}
        if timeline_months:
            journey_params["timeline_months"] = timeline_months
        if priority_focus:
            journey_params["priority_focus"] = priority_focus
        
        return await self.compose_journey(context, journey_params)
    
    async def _ensure_telemetry(self):
        if not self.telemetry_service and self.public_works:
            try:
                self.telemetry_service = self.public_works.get_telemetry_service()
            except Exception:
                pass
    
    async def _record_telemetry(self, telemetry_data: Dict[str, Any], tenant_id: str):
        if self.telemetry_service:
            try:
                await self.telemetry_service.record({"journey_id": self.journey_id, "tenant_id": tenant_id, **telemetry_data})
            except Exception:
                pass
