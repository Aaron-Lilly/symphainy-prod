"""
Optimize Process Service (Platform SDK)

Optimizes existing processes.

Contract: docs/intent_contracts/journey_operations_workflow/intent_optimize_process.md
"""

from typing import Dict, Any
from datetime import datetime

from utilities import get_logger, generate_event_id

from symphainy_platform.civic_systems.platform_sdk import (
    PlatformIntentService,
    PlatformContext
)


class OptimizeProcessService(PlatformIntentService):
    """
    Optimize Process Service using Platform SDK.
    
    Analyzes and optimizes existing processes.
    """
    
    def __init__(self, service_id: str = "optimize_process_service"):
        """Initialize Optimize Process Service."""
        super().__init__(service_id=service_id)
        self.logger = get_logger(self.__class__.__name__)
    
    async def execute(self, ctx: PlatformContext) -> Dict[str, Any]:
        """Execute optimize_process intent."""
        self.logger.info(f"Executing optimize_process: {ctx.execution_id}")
        
        process_id = ctx.intent.parameters.get("process_id")
        process_description = ctx.intent.parameters.get("process_description")
        optimization_goals = ctx.intent.parameters.get("optimization_goals", [])
        
        if not process_id and not process_description:
            raise ValueError("Either process_id or process_description is required")
        
        # Optimize via agent
        optimization = await self._optimize_via_agent(ctx, process_id, process_description, optimization_goals)
        
        optimization_result = {
            "optimization_id": generate_event_id(),
            "process_id": process_id,
            "optimization": optimization,
            "optimized_at": datetime.utcnow().isoformat()
        }
        
        self.logger.info(f"✅ Process optimization complete")
        
        return {
            "artifacts": {
                "optimization": optimization_result
            },
            "events": [{
                "type": "process_optimized",
                "event_id": generate_event_id()
            }]
        }
    
    async def _optimize_via_agent(
        self,
        ctx: PlatformContext,
        process_id: str,
        description: str,
        goals: list
    ) -> Dict[str, Any]:
        """Optimize using WorkflowOptimizationSpecialist."""
        if ctx.reasoning and ctx.reasoning.agents:
            try:
                agent_result = await ctx.reasoning.agents.invoke(
                    "workflow_optimization_specialist",
                    params={
                        "action": "optimize",
                        "process_id": process_id,
                        "description": description,
                        "goals": goals
                    },
                    context={
                        "tenant_id": ctx.tenant_id,
                        "session_id": ctx.session_id
                    }
                )
                
                if agent_result.get("status") == "completed":
                    return agent_result.get("result", {})
                    
            except Exception as e:
                self.logger.warning(f"Agent invocation failed: {e}")
        
        return {
            "recommendations": [],
            "potential_savings": "Analysis requires AI agent"
        }
