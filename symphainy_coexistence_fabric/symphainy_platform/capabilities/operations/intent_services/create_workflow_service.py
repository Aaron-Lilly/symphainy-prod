"""
Create Workflow Service (Platform SDK)

Creates optimized workflows.

Contract: docs/intent_contracts/journey_operations_workflow/intent_create_workflow.md
"""

from typing import Dict, Any
from datetime import datetime

from utilities import get_logger, generate_event_id

from symphainy_platform.civic_systems.platform_sdk import (
    PlatformIntentService,
    PlatformContext
)


class CreateWorkflowService(PlatformIntentService):
    """
    Create Workflow Service using Platform SDK.
    
    Creates optimized workflows using WorkflowOptimizationAgent.
    """
    
    def __init__(self, service_id: str = "create_workflow_service"):
        """Initialize Create Workflow Service."""
        super().__init__(service_id=service_id)
        self.logger = get_logger(self.__class__.__name__)
    
    async def execute(self, ctx: PlatformContext) -> Dict[str, Any]:
        """Execute create_workflow intent."""
        self.logger.info(f"Executing create_workflow: {ctx.execution_id}")
        
        workflow_description = ctx.intent.parameters.get("workflow_description")
        workflow_type = ctx.intent.parameters.get("workflow_type", "sequential")
        
        if not workflow_description:
            raise ValueError("workflow_description is required")
        
        # Create workflow via agent
        workflow = await self._create_via_agent(ctx, workflow_description, workflow_type)
        
        workflow_result = {
            "workflow_id": generate_event_id(),
            "workflow_description": workflow_description,
            "workflow_type": workflow_type,
            "workflow": workflow,
            "created_at": datetime.utcnow().isoformat()
        }
        
        self.logger.info(f"✅ Workflow created")
        
        return {
            "artifacts": {
                "workflow": workflow_result
            },
            "events": [{
                "type": "workflow_created",
                "event_id": generate_event_id(),
                "workflow_id": workflow_result["workflow_id"]
            }]
        }
    
    async def _create_via_agent(
        self,
        ctx: PlatformContext,
        description: str,
        workflow_type: str
    ) -> Dict[str, Any]:
        """Create workflow using WorkflowOptimizationAgent."""
        if ctx.reasoning and ctx.reasoning.agents:
            try:
                agent_result = await ctx.reasoning.agents.invoke(
                    "workflow_optimization_agent",
                    params={
                        "action": "create",
                        "description": description,
                        "type": workflow_type
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
            "steps": [],
            "type": workflow_type,
            "note": "Template workflow - invoke real agent for optimization"
        }
