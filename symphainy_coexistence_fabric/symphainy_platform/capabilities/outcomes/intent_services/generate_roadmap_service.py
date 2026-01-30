"""
Generate Roadmap Service (Platform SDK)

Generates strategic roadmaps using RoadmapGenerationAgent.
"""

from typing import Dict, Any
from datetime import datetime

from utilities import get_logger, generate_event_id

from symphainy_platform.civic_systems.platform_sdk import (
    PlatformIntentService,
    PlatformContext
)


class GenerateRoadmapService(PlatformIntentService):
    """Generate Roadmap Service using Platform SDK."""
    
    def __init__(self, service_id: str = "generate_roadmap_service"):
        super().__init__(service_id=service_id)
        self.logger = get_logger(self.__class__.__name__)
    
    async def execute(self, ctx: PlatformContext) -> Dict[str, Any]:
        """Execute generate_roadmap intent."""
        self.logger.info(f"Executing generate_roadmap: {ctx.execution_id}")
        
        outcome_id = ctx.intent.parameters.get("outcome_id")
        timeframe = ctx.intent.parameters.get("timeframe", "12_months")
        
        # Generate via RoadmapGenerationAgent
        roadmap = await self._generate_via_agent(ctx, outcome_id, timeframe)
        
        return {
            "artifacts": {
                "roadmap": {
                    "roadmap_id": generate_event_id(),
                    "outcome_id": outcome_id,
                    "timeframe": timeframe,
                    "roadmap": roadmap,
                    "generated_at": datetime.utcnow().isoformat()
                }
            },
            "events": [{"type": "roadmap_generated", "event_id": generate_event_id()}]
        }
    
    async def _generate_via_agent(self, ctx, outcome_id, timeframe):
        if ctx.reasoning and ctx.reasoning.agents:
            try:
                result = await ctx.reasoning.agents.invoke(
                    "roadmap_generation_agent",
                    params={"action": "generate", "outcome_id": outcome_id, "timeframe": timeframe},
                    context={"tenant_id": ctx.tenant_id, "session_id": ctx.session_id}
                )
                if result.get("status") == "completed":
                    return result.get("result", {})
            except Exception as e:
                self.logger.warning(f"Agent failed: {e}")
        return {"phases": [], "milestones": [], "note": "Roadmap requires AI agent"}
