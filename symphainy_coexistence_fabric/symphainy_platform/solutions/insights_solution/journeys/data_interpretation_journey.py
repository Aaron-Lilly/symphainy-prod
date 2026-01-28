"""
Data Interpretation Journey Orchestrator

Composes data interpretation journeys:
- Self-discovery: AI-driven semantic discovery
- Guided: Guide-based semantic discovery

WHAT (Journey Role): I orchestrate data interpretation
HOW (Journey Implementation): I compose interpret_data_* intents
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional
from utilities import get_logger, generate_event_id, get_clock
from symphainy_platform.runtime.execution_context import ExecutionContext


class DataInterpretationJourney:
    """Data Interpretation Journey Orchestrator."""
    
    JOURNEY_ID = "data_interpretation"
    JOURNEY_NAME = "Data Interpretation"
    
    def __init__(self, public_works=None, state_surface=None):
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
        self.public_works = public_works
        self.state_surface = state_surface
        self.journey_id = self.JOURNEY_ID
        self.journey_name = self.JOURNEY_NAME
        self._self_discovery_service = None
        self._guided_service = None
        self.telemetry_service = None
    
    async def compose_journey(
        self,
        context: ExecutionContext,
        journey_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Compose the data interpretation journey."""
        journey_params = journey_params or {}
        
        self.logger.info(f"Composing journey: {self.journey_name}")
        
        journey_execution_id = generate_event_id()
        
        try:
            parsed_file_id = journey_params.get("parsed_file_id")
            if not parsed_file_id:
                raise ValueError("parsed_file_id is required for interpretation")
            
            # Determine interpretation type
            guide_id = journey_params.get("guide_id")
            
            if guide_id:
                # Guided interpretation
                intent_service = await self._get_guided_service()
            else:
                # Self-discovery interpretation
                intent_service = await self._get_self_discovery_service()
            
            result = await intent_service.execute(context, journey_params)
            
            return {
                "success": True,
                "journey_id": self.journey_id,
                "journey_execution_id": journey_execution_id,
                "interpretation_type": "guided" if guide_id else "self_discovery",
                "artifacts": result.get("artifacts", {}),
                "events": [
                    {"type": "journey_completed", "journey_id": self.journey_id},
                    *result.get("events", [])
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Journey failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "journey_id": self.journey_id,
                "journey_execution_id": journey_execution_id,
                "artifacts": {},
                "events": [{"type": "journey_failed", "journey_id": self.journey_id, "error": str(e)}]
            }
    
    async def _get_self_discovery_service(self):
        if not self._self_discovery_service:
            from symphainy_platform.realms.insights.intent_services import (
                InterpretDataSelfDiscoveryService
            )
            self._self_discovery_service = InterpretDataSelfDiscoveryService(
                public_works=self.public_works,
                state_surface=self.state_surface
            )
        return self._self_discovery_service
    
    async def _get_guided_service(self):
        if not self._guided_service:
            from symphainy_platform.realms.insights.intent_services import (
                InterpretDataGuidedService
            )
            self._guided_service = InterpretDataGuidedService(
                public_works=self.public_works,
                state_surface=self.state_surface
            )
        return self._guided_service
    
    def get_soa_apis(self) -> Dict[str, Dict[str, Any]]:
        """Get SOA APIs provided by this journey."""
        return {
            "interpret_self_discovery": {
                "handler": self._soa_interpret_self_discovery,
                "description": "Self-discovery interpretation",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "parsed_file_id": {"type": "string"},
                        "discovery_options": {"type": "object"},
                        "tenant_id": {"type": "string"},
                        "session_id": {"type": "string"}
                    },
                    "required": ["parsed_file_id", "tenant_id", "session_id"]
                }
            },
            "interpret_guided": {
                "handler": self._soa_interpret_guided,
                "description": "Guided interpretation with guide",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "parsed_file_id": {"type": "string"},
                        "guide_id": {"type": "string"},
                        "tenant_id": {"type": "string"},
                        "session_id": {"type": "string"}
                    },
                    "required": ["parsed_file_id", "guide_id", "tenant_id", "session_id"]
                }
            }
        }
    
    async def _soa_interpret_self_discovery(
        self,
        parsed_file_id: str,
        tenant_id: str,
        session_id: str,
        discovery_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        execution_id = generate_event_id()
        context = ExecutionContext(
            execution_id=execution_id, tenant_id=tenant_id, session_id=session_id,
            intent=None, state_surface=self.state_surface
        )
        journey_params = {"parsed_file_id": parsed_file_id}
        if discovery_options:
            journey_params["discovery_options"] = discovery_options
        return await self.compose_journey(context, journey_params)
    
    async def _soa_interpret_guided(
        self,
        parsed_file_id: str,
        guide_id: str,
        tenant_id: str,
        session_id: str
    ) -> Dict[str, Any]:
        execution_id = generate_event_id()
        context = ExecutionContext(
            execution_id=execution_id, tenant_id=tenant_id, session_id=session_id,
            intent=None, state_surface=self.state_surface
        )
        journey_params = {"parsed_file_id": parsed_file_id, "guide_id": guide_id}
        return await self.compose_journey(context, journey_params)
