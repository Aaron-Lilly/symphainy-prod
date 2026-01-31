"""
Create Blueprint Service (Platform SDK)

Creates architectural blueprints using BlueprintCreationAgent.
"""

from typing import Dict, Any
from datetime import datetime

from utilities import get_logger, generate_event_id

from symphainy_platform.civic_systems.platform_sdk import (
    PlatformIntentService,
    PlatformContext
)


class CreateBlueprintService(PlatformIntentService):
    """Create Blueprint Service using Platform SDK."""
    
    def __init__(self, service_id: str = "create_blueprint_service"):
        super().__init__(service_id=service_id)
        self.logger = get_logger(self.__class__.__name__)
    
    async def execute(self, ctx: PlatformContext) -> Dict[str, Any]:
        """Execute create_blueprint intent."""
        self.logger.info(f"Executing create_blueprint: {ctx.execution_id}")
        
        outcome_id = ctx.intent.parameters.get("outcome_id")
        blueprint_type = ctx.intent.parameters.get("blueprint_type", "technical")
        
        # Generate via BlueprintCreationAgent
        blueprint = await self._create_via_agent(ctx, outcome_id, blueprint_type)
        
        return {
            "artifacts": {
                "blueprint": {
                    "blueprint_id": generate_event_id(),
                    "outcome_id": outcome_id,
                    "blueprint_type": blueprint_type,
                    "blueprint": blueprint,
                    "created_at": datetime.utcnow().isoformat()
                }
            },
            "events": [{"type": "blueprint_created", "event_id": generate_event_id()}]
        }
    
    async def _create_via_agent(self, ctx, outcome_id, blueprint_type):
        if ctx.reasoning and ctx.reasoning.agents:
            try:
                result = await ctx.reasoning.agents.invoke(
                    "blueprint_creation_agent",
                    params={"action": "create", "outcome_id": outcome_id, "type": blueprint_type},
                    context={"tenant_id": ctx.tenant_id, "session_id": ctx.session_id}
                )
                if result.get("status") == "completed":
                    return result.get("result", {})
            except Exception as e:
                self.logger.warning(f"Agent failed: {e}")
        return {"components": [], "architecture": {}, "note": "Blueprint requires AI agent"}
