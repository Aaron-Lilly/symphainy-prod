"""
POC Creation Journey Orchestrator

Composes POC creation:
1. create_poc - Create proof-of-concept proposal
2. generate_poc_details - Generate detailed POC specification
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional
from utilities import get_logger, generate_event_id, get_clock
from symphainy_platform.runtime.execution_context import ExecutionContext
from symphainy_platform.realms.utils.structured_artifacts import create_structured_artifact


class POCCreationJourney:
    """POC Creation Journey Orchestrator."""
    
    JOURNEY_ID = "poc_creation"
    JOURNEY_NAME = "POC Creation"
    
    def __init__(self, public_works: Optional[Any] = None, state_surface: Optional[Any] = None):
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
        self.public_works = public_works
        self.state_surface = state_surface
        self.journey_id = self.JOURNEY_ID
        self.journey_name = self.JOURNEY_NAME
    
    async def compose_journey(self, context: ExecutionContext, journey_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        journey_params = journey_params or {}
        journey_execution_id = generate_event_id()
        
        self.logger.info(f"Composing journey: {self.journey_name}")
        
        try:
            poc_id = generate_event_id()
            
            poc_result = {
                "poc_id": poc_id,
                "title": journey_params.get("title", "Proof of Concept"),
                "description": journey_params.get("description", ""),
                "objectives": journey_params.get("objectives", []),
                "scope": journey_params.get("scope", {}),
                "timeline": journey_params.get("timeline", "4-6 weeks"),
                "success_criteria": [],
                "created_at": self.clock.now_utc().isoformat()
            }
            
            semantic_payload = {
                "poc_id": poc_id,
                "title": poc_result["title"],
                "journey_execution_id": journey_execution_id
            }
            
            artifact = create_structured_artifact(
                result_type="poc_proposal",
                semantic_payload=semantic_payload,
                renderings={"poc": poc_result}
            )
            
            return {
                "success": True,
                "journey_id": self.journey_id,
                "journey_execution_id": journey_execution_id,
                "poc_id": poc_id,
                "artifacts": {"poc": artifact},
                "events": [{"type": "poc_created", "poc_id": poc_id}]
            }
        except Exception as e:
            self.logger.error(f"Journey failed: {e}", exc_info=True)
            return {"success": False, "error": str(e), "journey_id": self.journey_id}
    
    def get_soa_apis(self) -> Dict[str, Dict[str, Any]]:
        return {
            "create_poc": {
                "handler": self._handle_create,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "objectives": {"type": "array"},
                        "user_context": {"type": "object"}
                    },
                    "required": ["title"]
                },
                "description": "Create POC proposal"
            }
        }
    
    async def _handle_create(self, **kwargs) -> Dict[str, Any]:
        user_context = kwargs.get("user_context", {})
        context = ExecutionContext(
            execution_id=generate_event_id(),
            tenant_id=user_context.get("tenant_id", "default"),
            session_id=user_context.get("session_id", generate_event_id()),
            solution_id="outcomes_solution"
        )
        return await self.compose_journey(context, kwargs)
