"""
Create POC Service (Platform SDK)

Creates Proof of Concept using POCGenerationAgent.
"""

from typing import Dict, Any
from datetime import datetime

from utilities import get_logger, generate_event_id

from symphainy_platform.civic_systems.platform_sdk import (
    PlatformIntentService,
    PlatformContext
)


class CreatePOCService(PlatformIntentService):
    """Create POC Service using Platform SDK."""
    
    def __init__(self, service_id: str = "create_poc_service"):
        super().__init__(service_id=service_id)
        self.logger = get_logger(self.__class__.__name__)
    
    async def execute(self, ctx: PlatformContext) -> Dict[str, Any]:
        """Execute create_poc intent."""
        self.logger.info(f"Executing create_poc: {ctx.execution_id}")
        
        outcome_id = ctx.intent.parameters.get("outcome_id")
        poc_scope = ctx.intent.parameters.get("scope", "minimal")
        
        # Generate via POCGenerationAgent
        poc = await self._create_via_agent(ctx, outcome_id, poc_scope)
        
        return {
            "artifacts": {
                "poc": {
                    "poc_id": generate_event_id(),
                    "outcome_id": outcome_id,
                    "scope": poc_scope,
                    "poc": poc,
                    "created_at": datetime.utcnow().isoformat()
                }
            },
            "events": [{"type": "poc_created", "event_id": generate_event_id()}]
        }
    
    async def _create_via_agent(self, ctx, outcome_id, scope):
        if ctx.reasoning and ctx.reasoning.agents:
            try:
                result = await ctx.reasoning.agents.invoke(
                    "poc_generation_agent",
                    params={"action": "generate", "outcome_id": outcome_id, "scope": scope},
                    context={"tenant_id": ctx.tenant_id, "session_id": ctx.session_id}
                )
                if result.get("status") == "completed":
                    return result.get("result", {})
            except Exception as e:
                self.logger.warning(f"Agent failed: {e}")
        return {"components": [], "effort": "TBD", "note": "POC requires AI agent"}
