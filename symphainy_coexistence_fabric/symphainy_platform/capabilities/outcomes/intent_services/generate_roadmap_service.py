"""
Generate Roadmap Service (Platform SDK)

Attempts to generate strategic roadmaps using RoadmapGenerationAgent.

HONESTY NOTE: This service is currently a PARLOR TRICK.
- It attempts to invoke roadmap_generation_agent via ctx.reasoning.agents
- If agent is unavailable or fails, it returns an EMPTY roadmap structure
- The returned structure has no real content without a working agent

Infrastructure Requirements:
- ctx.reasoning.agents must be wired
- roadmap_generation_agent must be registered and instantiable
- LLM adapter must be configured with valid API key
"""

from typing import Dict, Any
from datetime import datetime

from utilities import get_logger, generate_event_id

from symphainy_platform.civic_systems.platform_sdk import (
    PlatformIntentService,
    PlatformContext
)


class GenerateRoadmapService(PlatformIntentService):
    """
    Generate Roadmap Service using Platform SDK.
    
    CURRENT STATUS: PARLOR TRICK
    - Returns empty structure if agent unavailable
    - No fallback logic beyond template
    """
    
    intent_type = "generate_roadmap"
    
    def __init__(self, service_id: str = "generate_roadmap_service"):
        super().__init__(service_id=service_id, intent_type="generate_roadmap")
        self.logger = get_logger(self.__class__.__name__)
    
    async def execute(self, ctx: PlatformContext) -> Dict[str, Any]:
        """
        Execute generate_roadmap intent.
        
        NOTE: This will return an empty roadmap if AI infrastructure is not available.
        """
        self.logger.info(f"Executing generate_roadmap: {ctx.execution_id}")
        
        outcome_id = ctx.intent.parameters.get("outcome_id")
        timeframe = ctx.intent.parameters.get("timeframe", "12_months")
        
        # Attempt to generate via RoadmapGenerationAgent
        roadmap, used_agent = await self._generate_via_agent(ctx, outcome_id, timeframe)
        
        return {
            "artifacts": {
                "roadmap": {
                    "roadmap_id": generate_event_id(),
                    "outcome_id": outcome_id,
                    "timeframe": timeframe,
                    "roadmap": roadmap,
                    "generated_via": "agent" if used_agent else "fallback_template",
                    "has_real_content": used_agent,
                    "generated_at": datetime.utcnow().isoformat()
                }
            },
            "events": [{
                "type": "roadmap_generated",
                "event_id": generate_event_id(),
                "generated_via": "agent" if used_agent else "fallback_template"
            }]
        }
    
    async def _generate_via_agent(self, ctx, outcome_id, timeframe) -> tuple[Dict[str, Any], bool]:
        """
        Attempt to generate roadmap via AI agent.
        
        Returns:
            Tuple of (roadmap_dict, used_agent_bool)
        """
        if ctx.reasoning and ctx.reasoning.agents:
            try:
                result = await ctx.reasoning.agents.invoke(
                    "roadmap_generation_agent",
                    params={"action": "generate", "outcome_id": outcome_id, "timeframe": timeframe},
                    context={"tenant_id": ctx.tenant_id, "session_id": ctx.session_id}
                )
                if result.get("status") == "completed":
                    self.logger.info("✅ Roadmap generated via AI agent")
                    return result.get("result", {}), True
            except Exception as e:
                self.logger.warning(f"Agent invocation failed: {e}")
        
        # FALLBACK: Return empty template - THIS IS A PARLOR TRICK
        self.logger.warning("⚠️ Returning empty roadmap template - AI infrastructure not available")
        return {
            "phases": [],
            "milestones": [],
            "dependencies": [],
            "note": "EMPTY TEMPLATE: AI agent required for real roadmap generation"
        }, False
