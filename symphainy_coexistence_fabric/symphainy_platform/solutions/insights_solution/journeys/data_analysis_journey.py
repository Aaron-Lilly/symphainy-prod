"""
Data Analysis Journey Orchestrator

Composes data analysis journeys:
- Structured data analysis
- Unstructured data analysis

WHAT (Journey Role): I orchestrate data analysis
HOW (Journey Implementation): I compose analyze_*_data intents
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional
from utilities import get_logger, generate_event_id, get_clock
from symphainy_platform.runtime.execution_context import ExecutionContext


class DataAnalysisJourney:
    """Data Analysis Journey Orchestrator."""
    
    JOURNEY_ID = "data_analysis"
    JOURNEY_NAME = "Data Analysis"
    
    def __init__(self, public_works=None, state_surface=None):
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
        self.public_works = public_works
        self.state_surface = state_surface
        self.journey_id = self.JOURNEY_ID
        self.journey_name = self.JOURNEY_NAME
        self._structured_service = None
        self._unstructured_service = None
        self.telemetry_service = None
    
    async def compose_journey(
        self,
        context: ExecutionContext,
        journey_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Compose the data analysis journey."""
        journey_params = journey_params or {}
        
        self.logger.info(f"Composing journey: {self.journey_name}")
        
        journey_execution_id = generate_event_id()
        
        try:
            parsed_file_id = journey_params.get("parsed_file_id")
            if not parsed_file_id:
                raise ValueError("parsed_file_id is required for analysis")
            
            # Determine analysis type
            analysis_type = journey_params.get("analysis_type", "structured")
            
            if analysis_type == "unstructured":
                intent_service = await self._get_unstructured_service()
            else:
                intent_service = await self._get_structured_service()
            
            result = await intent_service.execute(context, journey_params)
            
            return {
                "success": True,
                "journey_id": self.journey_id,
                "journey_execution_id": journey_execution_id,
                "analysis_type": analysis_type,
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
    
    async def _get_structured_service(self):
        if not self._structured_service:
            from symphainy_platform.realms.insights.intent_services import (
                AnalyzeStructuredDataService
            )
            self._structured_service = AnalyzeStructuredDataService(
                public_works=self.public_works,
                state_surface=self.state_surface
            )
        return self._structured_service
    
    async def _get_unstructured_service(self):
        if not self._unstructured_service:
            from symphainy_platform.realms.insights.intent_services import (
                AnalyzeUnstructuredDataService
            )
            self._unstructured_service = AnalyzeUnstructuredDataService(
                public_works=self.public_works,
                state_surface=self.state_surface
            )
        return self._unstructured_service
    
    def get_soa_apis(self) -> Dict[str, Dict[str, Any]]:
        """Get SOA APIs provided by this journey."""
        return {
            "analyze_structured": {
                "handler": self._soa_analyze_structured,
                "description": "Analyze structured data",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "parsed_file_id": {"type": "string"},
                        "analysis_options": {"type": "object"},
                        "tenant_id": {"type": "string"},
                        "session_id": {"type": "string"}
                    },
                    "required": ["parsed_file_id", "tenant_id", "session_id"]
                }
            },
            "analyze_unstructured": {
                "handler": self._soa_analyze_unstructured,
                "description": "Analyze unstructured data",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "parsed_file_id": {"type": "string"},
                        "analysis_options": {"type": "object"},
                        "tenant_id": {"type": "string"},
                        "session_id": {"type": "string"}
                    },
                    "required": ["parsed_file_id", "tenant_id", "session_id"]
                }
            }
        }
    
    async def _soa_analyze_structured(
        self,
        parsed_file_id: str,
        tenant_id: str,
        session_id: str,
        analysis_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        execution_id = generate_event_id()
        context = ExecutionContext(
            execution_id=execution_id, tenant_id=tenant_id, session_id=session_id,
            intent=None, state_surface=self.state_surface
        )
        journey_params = {"parsed_file_id": parsed_file_id, "analysis_type": "structured"}
        if analysis_options:
            journey_params["analysis_options"] = analysis_options
        return await self.compose_journey(context, journey_params)
    
    async def _soa_analyze_unstructured(
        self,
        parsed_file_id: str,
        tenant_id: str,
        session_id: str,
        analysis_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        execution_id = generate_event_id()
        context = ExecutionContext(
            execution_id=execution_id, tenant_id=tenant_id, session_id=session_id,
            intent=None, state_surface=self.state_surface
        )
        journey_params = {"parsed_file_id": parsed_file_id, "analysis_type": "unstructured"}
        if analysis_options:
            journey_params["analysis_options"] = analysis_options
        return await self.compose_journey(context, journey_params)
