"""
Interpret Data Guided Service (Platform SDK)

Guided interpretation with user-provided constraints and questions.

Contract: docs/intent_contracts/journey_insights_data_interpretation/intent_interpret_data_guided.md
"""

from typing import Dict, Any, List
from datetime import datetime

from utilities import get_logger, generate_event_id

from symphainy_platform.civic_systems.platform_sdk import (
    PlatformIntentService,
    PlatformContext
)


class InterpretDataGuidedService(PlatformIntentService):
    """
    Interpret Data Guided Service using Platform SDK.
    
    Provides guided interpretation with user constraints:
    - Answer specific questions about the data
    - Focus analysis on user-specified areas
    - Validate user hypotheses
    
    Returns unavailable status if AI agent not available (no fake data).
    """
    
    intent_type = "interpret_data_guided"
    
    def __init__(self, service_id: str = "interpret_data_guided_service"):
        """Initialize Interpret Data Guided Service."""
        super().__init__(service_id=service_id, intent_type="interpret_data_guided")
        self.logger = get_logger(self.__class__.__name__)
    
    async def execute(self, ctx: PlatformContext) -> Dict[str, Any]:
        """
        Execute interpret_data_guided intent.
        
        Args:
            ctx: Platform context with intent and platform services
        
        Returns:
            Dict with guided interpretation results
        """
        self.logger.info(f"Executing interpret_data_guided: {ctx.execution_id}")
        
        parsed_file_id = ctx.intent.parameters.get("parsed_file_id")
        questions = ctx.intent.parameters.get("questions", [])
        focus_areas = ctx.intent.parameters.get("focus_areas", [])
        
        if not parsed_file_id:
            raise ValueError("parsed_file_id is required for guided interpretation")
        
        # Get parsed content
        parsed_content = await ctx.platform.get_parsed_file(
            parsed_file_id=parsed_file_id,
            tenant_id=ctx.tenant_id,
            session_id=ctx.session_id
        )
        
        if not parsed_content:
            raise ValueError(f"Parsed file not found: {parsed_file_id}")
        
        # Process guided interpretation via agent
        interpretation = await self._guided_interpret(ctx, parsed_content, questions, focus_areas)
        
        # Build interpretation result
        interpretation_result = {
            "interpretation_id": generate_event_id(),
            "parsed_file_id": parsed_file_id,
            "mode": "guided",
            "questions_answered": len(interpretation.get("answers", [])),
            "interpretation": interpretation,
            "interpreted_at": datetime.utcnow().isoformat()
        }
        
        self.logger.info(f"✅ Guided interpretation complete")
        
        return {
            "artifacts": {
                "interpretation": interpretation_result
            },
            "events": [{
                "type": "data_interpreted",
                "event_id": generate_event_id(),
                "mode": "guided"
            }]
        }
    
    async def _guided_interpret(
        self,
        ctx: PlatformContext,
        parsed_content: Dict[str, Any],
        questions: List[str],
        focus_areas: List[str]
    ) -> Dict[str, Any]:
        """Perform guided interpretation."""
        # Try to use BusinessAnalysisAgent for guided analysis
        if ctx.reasoning and ctx.reasoning.agents:
            try:
                agent_result = await ctx.reasoning.agents.invoke(
                    "business_analysis_agent",
                    params={
                        "action": "guided_analysis",
                        "content": parsed_content.get("content"),
                        "questions": questions,
                        "focus_areas": focus_areas
                    },
                    context={
                        "tenant_id": ctx.tenant_id,
                        "session_id": ctx.session_id
                    }
                )
                
                if agent_result.get("status") == "completed":
                    result = agent_result.get("result", {})
                    result["used_real_llm"] = True
                    return result
                    
            except Exception as e:
                self.logger.error(f"BusinessAnalysisAgent invocation failed: {e}")
                return {
                    "status": "error",
                    "error": str(e),
                    "questions_received": questions,
                    "used_real_llm": False
                }
        
        # Agent not available - return unavailable status (NO FAKE DATA)
        self.logger.warning("AI reasoning service not available for guided analysis")
        return {
            "status": "unavailable",
            "error": "AI reasoning service not configured",
            "questions_received": questions,
            "focus_areas_received": focus_areas,
            "used_real_llm": False,
            "note": "Guided analysis requires AI agent - please ensure reasoning service is configured"
        }
