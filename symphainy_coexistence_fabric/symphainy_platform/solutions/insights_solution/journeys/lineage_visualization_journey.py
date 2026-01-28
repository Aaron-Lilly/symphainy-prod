"""
Lineage Visualization Journey Orchestrator

Composes the lineage visualization journey ("Your Data Mash"):
1. Build lineage graph from session artifacts
2. Generate visualization configuration
3. Return lineage data for display

WHAT (Journey Role): I orchestrate lineage visualization
HOW (Journey Implementation): I compose visualize_lineage intent
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional
from utilities import get_logger, generate_event_id, get_clock
from symphainy_platform.runtime.execution_context import ExecutionContext


class LineageVisualizationJourney:
    """Lineage Visualization Journey Orchestrator."""
    
    JOURNEY_ID = "lineage_visualization"
    JOURNEY_NAME = "Lineage Visualization (Your Data Mash)"
    
    def __init__(self, public_works=None, state_surface=None):
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
        """Compose the lineage visualization journey."""
        journey_params = journey_params or {}
        
        self.logger.info(f"Composing journey: {self.journey_name}")
        
        journey_execution_id = generate_event_id()
        
        try:
            intent_service = await self._get_intent_service()
            result = await intent_service.execute(context, journey_params)
            
            return {
                "success": True,
                "journey_id": self.journey_id,
                "journey_execution_id": journey_execution_id,
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
    
    async def _get_intent_service(self):
        if not self._intent_service:
            from symphainy_platform.realms.insights.intent_services import (
                VisualizeLineageService
            )
            self._intent_service = VisualizeLineageService(
                public_works=self.public_works,
                state_surface=self.state_surface
            )
        return self._intent_service
    
    def get_soa_apis(self) -> Dict[str, Dict[str, Any]]:
        """Get SOA APIs provided by this journey."""
        return {
            "visualize_lineage": {
                "handler": self._soa_visualize_lineage,
                "description": "Visualize data lineage (Your Data Mash)",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "session_id": {"type": "string"},
                        "artifact_id": {"type": "string", "description": "Optional specific artifact"},
                        "tenant_id": {"type": "string"}
                    },
                    "required": ["tenant_id", "session_id"]
                }
            }
        }
    
    async def _soa_visualize_lineage(
        self,
        tenant_id: str,
        session_id: str,
        artifact_id: Optional[str] = None
    ) -> Dict[str, Any]:
        execution_id = generate_event_id()
        context = ExecutionContext(
            execution_id=execution_id, tenant_id=tenant_id, session_id=session_id,
            intent=None, state_surface=self.state_surface
        )
        journey_params = {}
        if artifact_id:
            journey_params["artifact_id"] = artifact_id
        return await self.compose_journey(context, journey_params)
