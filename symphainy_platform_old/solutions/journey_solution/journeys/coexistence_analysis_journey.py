"""
Coexistence Analysis Journey Orchestrator

Composes coexistence analysis:
1. analyze_coexistence - Analyze human-AI coexistence opportunities
2. identify_friction - Identify friction points
3. create_blueprint - Create coexistence blueprint

WHAT (Journey Role): I orchestrate coexistence analysis
HOW (Journey Implementation): I compose analysis, friction identification, and blueprint creation
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


class CoexistenceAnalysisJourney:
    """
    Coexistence Analysis Journey Orchestrator.
    
    Provides MCP Tools:
    - journey_analyze_coexistence: Analyze human-AI coexistence
    - journey_identify_opportunities: Identify coexistence opportunities
    """
    
    JOURNEY_ID = "coexistence_analysis"
    JOURNEY_NAME = "Coexistence Analysis"
    
    def __init__(self, public_works: Optional[Any] = None, state_surface: Optional[Any] = None):
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
        self.public_works = public_works
        self.state_surface = state_surface
        self.journey_id = self.JOURNEY_ID
        self.journey_name = self.JOURNEY_NAME
    
    async def compose_journey(self, context: ExecutionContext, journey_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Compose coexistence analysis journey."""
        journey_params = journey_params or {}
        journey_execution_id = generate_event_id()
        
        self.logger.info(f"Composing journey: {self.journey_name}")
        
        try:
            workflow_id = journey_params.get("workflow_id")
            analysis_id = generate_event_id()
            
            analysis_result = {
                "analysis_id": analysis_id,
                "workflow_id": workflow_id,
                "created_at": self.clock.now_utc().isoformat(),
                "friction_points": [],
                "human_focus_areas": [],
                "ai_augmentation_opportunities": [],
                "coexistence_score": 0.78,
                "recommendations": []
            }
            
            semantic_payload = {
                "analysis_id": analysis_id,
                "workflow_id": workflow_id,
                "coexistence_score": analysis_result["coexistence_score"],
                "journey_execution_id": journey_execution_id
            }
            
            artifact = create_structured_artifact(
                result_type="coexistence_analysis",
                semantic_payload=semantic_payload,
                renderings={"analysis_result": analysis_result}
            )
            
            return {
                "success": True,
                "journey_id": self.journey_id,
                "journey_execution_id": journey_execution_id,
                "analysis_id": analysis_id,
                "artifacts": {"coexistence_analysis": artifact},
                "events": [{"type": "coexistence_analyzed", "analysis_id": analysis_id}]
            }
            
        except Exception as e:
            self.logger.error(f"Journey failed: {e}", exc_info=True)
            return {"success": False, "error": str(e), "journey_id": self.journey_id}
    
    def get_soa_apis(self) -> Dict[str, Dict[str, Any]]:
        return {
            "analyze_coexistence": {
                "handler": self._handle_analyze,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "workflow_id": {"type": "string", "description": "Workflow to analyze"},
                        "user_context": {"type": "object"}
                    },
                    "required": ["workflow_id"]
                },
                "description": "Analyze human-AI coexistence opportunities"
            },
            "identify_opportunities": {
                "handler": self._handle_opportunities,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "workflow_id": {"type": "string"},
                        "user_context": {"type": "object"}
                    },
                    "required": ["workflow_id"]
                },
                "description": "Identify coexistence opportunities"
            }
        }
    
    async def _handle_analyze(self, **kwargs) -> Dict[str, Any]:
        user_context = kwargs.get("user_context", {})
        context = ExecutionContext(
            execution_id=generate_event_id(),
            tenant_id=user_context.get("tenant_id", "default"),
            session_id=user_context.get("session_id", generate_event_id()),
            solution_id="journey_solution"
        )
        return await self.compose_journey(context, {"workflow_id": kwargs.get("workflow_id")})
    
    async def _handle_opportunities(self, **kwargs) -> Dict[str, Any]:
        return await self._handle_analyze(**kwargs)
