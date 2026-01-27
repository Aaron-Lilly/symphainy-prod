"""
POC Proposal Journey Orchestrator

Composes the POC proposal journey:
1. Validate description input
2. Execute create_poc intent
3. Store POC proposal in Artifact Plane
4. Return POC artifact reference

WHAT (Journey Role): I orchestrate POC proposal creation
HOW (Journey Implementation): I compose create_poc intent

Key Principle: Journey orchestrators compose intent services into journeys.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional
from utilities import get_logger, generate_event_id, get_clock
from symphainy_platform.runtime.execution_context import ExecutionContext


class POCProposalJourney:
    """
    POC Proposal Journey Orchestrator.
    
    Journey Flow:
    1. Validate description (required)
    2. Execute create_poc intent
    3. Store POC artifact
    4. Return POC reference
    
    Provides MCP Tools:
    - outcomes_create_poc: Create POC proposal from description
    """
    
    JOURNEY_ID = "poc_proposal"
    JOURNEY_NAME = "POC Proposal"
    
    def __init__(
        self,
        public_works: Optional[Any] = None,
        state_surface: Optional[Any] = None
    ):
        """Initialize POC Proposal Journey."""
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
        Compose the POC proposal journey.
        
        Args:
            context: Execution context
            journey_params: Journey parameters including:
                - description: POC description (required)
                - scope: Optional scope definition
                - timeline_weeks: Optional timeline in weeks
        
        Returns:
            Journey result with POC artifact
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
            description = journey_params.get("description")
            if not description:
                raise ValueError("description is required for POC proposal")
            
            # Get intent service
            intent_service = await self._get_intent_service()
            
            # Execute create_poc intent
            result = await intent_service.execute(context, journey_params)
            
            # Build journey result
            journey_result = self._build_journey_result(
                intent_result=result,
                journey_execution_id=journey_execution_id
            )
            
            await self._record_telemetry({
                "action": "journey_completed",
                "journey_id": self.journey_id,
                "journey_execution_id": journey_execution_id
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
                CreatePOCService
            )
            self._intent_service = CreatePOCService(
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
            "create_poc": {
                "handler": self._soa_create_poc,
                "description": "Create POC proposal from description",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "string",
                            "description": "POC description"
                        },
                        "scope": {
                            "type": "string",
                            "description": "POC scope definition"
                        },
                        "timeline_weeks": {
                            "type": "integer",
                            "description": "Timeline in weeks"
                        },
                        "tenant_id": {"type": "string", "description": "Tenant identifier"},
                        "session_id": {"type": "string", "description": "Session identifier"}
                    },
                    "required": ["description", "tenant_id", "session_id"]
                }
            }
        }
    
    async def _soa_create_poc(
        self,
        description: str,
        tenant_id: str,
        session_id: str,
        scope: Optional[str] = None,
        timeline_weeks: Optional[int] = None
    ) -> Dict[str, Any]:
        """SOA API: Create POC proposal."""
        execution_id = generate_event_id()
        
        context = ExecutionContext(
            execution_id=execution_id,
            tenant_id=tenant_id,
            session_id=session_id,
            intent=None,
            state_surface=self.state_surface
        )
        
        journey_params = {"description": description}
        if scope:
            journey_params["scope"] = scope
        if timeline_weeks:
            journey_params["timeline_weeks"] = timeline_weeks
        
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
