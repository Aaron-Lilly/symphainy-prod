"""
Synthesize Outcome Service (Platform SDK)

Synthesizes insights into strategic outcomes using OutcomesSynthesisAgent.
"""

from typing import Dict, Any
from datetime import datetime

from utilities import get_logger, generate_event_id

from symphainy_platform.civic_systems.platform_sdk import (
    PlatformIntentService,
    PlatformContext
)


class SynthesizeOutcomeService(PlatformIntentService):
    """
    Synthesize Outcome Service using Platform SDK.
    
    Returns unavailable status if AI agent not available (no fake data).
    """
    
    intent_type = "synthesize_outcome"
    
    def __init__(self, service_id: str = "synthesize_outcome_service"):
        super().__init__(service_id=service_id, intent_type="synthesize_outcome")
        self.logger = get_logger(self.__class__.__name__)
    
    async def execute(self, ctx: PlatformContext) -> Dict[str, Any]:
        """Execute synthesize_outcome intent."""
        self.logger.info(f"Executing synthesize_outcome: {ctx.execution_id}")
        
        insight_ids = ctx.intent.parameters.get("insight_ids", [])
        outcome_type = ctx.intent.parameters.get("outcome_type", "strategic")
        
        # Synthesize via OutcomesSynthesisAgent
        outcome = await self._synthesize_via_agent(ctx, insight_ids, outcome_type)
        
        return {
            "artifacts": {
                "outcome": {
                    "outcome_id": generate_event_id(),
                    "insight_ids": insight_ids,
                    "outcome_type": outcome_type,
                    "outcome": outcome,
                    "synthesized_at": datetime.utcnow().isoformat()
                }
            },
            "events": [{"type": "outcome_synthesized", "event_id": generate_event_id()}]
        }
    
    async def _synthesize_via_agent(self, ctx, insight_ids, outcome_type):
        if ctx.reasoning and ctx.reasoning.agents:
            try:
                result = await ctx.reasoning.agents.invoke(
                    "outcomes_synthesis_agent",
                    params={"action": "synthesize", "insight_ids": insight_ids, "type": outcome_type},
                    context={"tenant_id": ctx.tenant_id, "session_id": ctx.session_id}
                )
                if result.get("status") == "completed":
                    return result.get("result", {})
            except Exception as e:
                self.logger.error(f"Agent failed: {e}")
                return {"status": "error", "error": str(e)}
        
        # Agent not available - return unavailable status (NO FAKE DATA)
        self.logger.warning("AI reasoning service not available for outcome synthesis")
        return {
            "status": "unavailable",
            "error": "AI reasoning service not configured",
            "note": "Outcome synthesis requires AI agent - please ensure reasoning service is configured"
        }
