"""
Roadmap Generation Journey Orchestrator

Composes roadmap generation:
1. generate_roadmap - Generate solution roadmap
2. create_timeline - Create implementation timeline
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


class RoadmapGenerationJourney:
    """Roadmap Generation Journey Orchestrator."""
    
    JOURNEY_ID = "roadmap_generation"
    JOURNEY_NAME = "Roadmap Generation"
    
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
            roadmap_id = generate_event_id()
            
            roadmap_result = {
                "roadmap_id": roadmap_id,
                "solution_id": journey_params.get("solution_id"),
                "phases": [],
                "milestones": [],
                "dependencies": [],
                "estimated_duration": journey_params.get("duration", "12 weeks"),
                "created_at": self.clock.now_utc().isoformat()
            }
            
            semantic_payload = {
                "roadmap_id": roadmap_id,
                "solution_id": journey_params.get("solution_id"),
                "journey_execution_id": journey_execution_id
            }
            
            artifact = create_structured_artifact(
                result_type="roadmap",
                semantic_payload=semantic_payload,
                renderings={"roadmap": roadmap_result}
            )
            
            return {
                "success": True,
                "journey_id": self.journey_id,
                "journey_execution_id": journey_execution_id,
                "roadmap_id": roadmap_id,
                "artifacts": {"roadmap": artifact},
                "events": [{"type": "roadmap_generated", "roadmap_id": roadmap_id}]
            }
        except Exception as e:
            self.logger.error(f"Journey failed: {e}", exc_info=True)
            return {"success": False, "error": str(e), "journey_id": self.journey_id}
    
    def get_soa_apis(self) -> Dict[str, Dict[str, Any]]:
        return {
            "generate_roadmap": {
                "handler": self._handle_generate,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "solution_id": {"type": "string"},
                        "duration": {"type": "string"},
                        "user_context": {"type": "object"}
                    },
                    "required": ["solution_id"]
                },
                "description": "Generate solution roadmap"
            }
        }
    
    async def _handle_generate(self, **kwargs) -> Dict[str, Any]:
        user_context = kwargs.get("user_context", {})
        context = ExecutionContext(
            execution_id=generate_event_id(),
            tenant_id=user_context.get("tenant_id", "default"),
            session_id=user_context.get("session_id", generate_event_id()),
            solution_id="outcomes_solution"
        )
        return await self.compose_journey(context, kwargs)
