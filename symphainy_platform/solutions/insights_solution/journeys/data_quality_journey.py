"""
Data Quality Journey Orchestrator

Composes the data quality journey:
1. Validate parsed_file_id
2. Execute assess_data_quality intent
3. Return quality assessment report

WHAT (Journey Role): I orchestrate data quality assessment
HOW (Journey Implementation): I compose assess_data_quality intent
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional
from utilities import get_logger, generate_event_id, get_clock
from symphainy_platform.runtime.execution_context import ExecutionContext


class DataQualityJourney:
    """Data Quality Journey Orchestrator."""
    
    JOURNEY_ID = "data_quality"
    JOURNEY_NAME = "Data Quality Assessment"
    
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
        """Compose the data quality journey."""
        journey_params = journey_params or {}
        
        self.logger.info(f"Composing journey: {self.journey_name}")
        
        journey_execution_id = generate_event_id()
        
        try:
            parsed_file_id = journey_params.get("parsed_file_id")
            if not parsed_file_id:
                raise ValueError("parsed_file_id is required for quality assessment")
            
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
            from symphainy_coexistence_fabric.symphainy_platform.realms.insights.intent_services import (
                AssessDataQualityService
            )
            self._intent_service = AssessDataQualityService(
                public_works=self.public_works,
                state_surface=self.state_surface
            )
        return self._intent_service
    
    def get_soa_apis(self) -> Dict[str, Dict[str, Any]]:
        """Get SOA APIs provided by this journey."""
        return {
            "assess_quality": {
                "handler": self._soa_assess_quality,
                "description": "Assess data quality for a parsed file",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "parsed_file_id": {"type": "string", "description": "Parsed file ID"},
                        "source_file_id": {"type": "string", "description": "Source file ID"},
                        "parser_type": {"type": "string", "description": "Parser type"},
                        "tenant_id": {"type": "string"},
                        "session_id": {"type": "string"}
                    },
                    "required": ["parsed_file_id", "tenant_id", "session_id"]
                }
            }
        }
    
    async def _soa_assess_quality(
        self,
        parsed_file_id: str,
        tenant_id: str,
        session_id: str,
        source_file_id: Optional[str] = None,
        parser_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """SOA API: Assess quality."""
        execution_id = generate_event_id()
        
        context = ExecutionContext(
            execution_id=execution_id,
            tenant_id=tenant_id,
            session_id=session_id,
            intent=None,
            state_surface=self.state_surface
        )
        
        journey_params = {"parsed_file_id": parsed_file_id}
        if source_file_id:
            journey_params["source_file_id"] = source_file_id
        if parser_type:
            journey_params["parser_type"] = parser_type
        
        return await self.compose_journey(context, journey_params)
