"""
Create Solution Service (Platform SDK)

Creates platform solutions from outcomes.
"""

from typing import Dict, Any
from datetime import datetime

from utilities import get_logger, generate_event_id

from symphainy_platform.civic_systems.platform_sdk import (
    PlatformIntentService,
    PlatformContext
)


class CreateSolutionService(PlatformIntentService):
    """Create Solution Service using Platform SDK."""
    
    intent_type = "create_solution"
    
    def __init__(self, service_id: str = "create_solution_service"):
        super().__init__(service_id=service_id, intent_type="create_solution")
        self.logger = get_logger(self.__class__.__name__)
    
    async def execute(self, ctx: PlatformContext) -> Dict[str, Any]:
        """Execute create_solution intent."""
        self.logger.info(f"Executing create_solution: {ctx.execution_id}")
        
        solution_name = ctx.intent.parameters.get("solution_name")
        outcome_ids = ctx.intent.parameters.get("outcome_ids", [])
        
        if not solution_name:
            raise ValueError("solution_name is required")
        
        solution = {
            "solution_id": generate_event_id(),
            "solution_name": solution_name,
            "outcome_ids": outcome_ids,
            "status": "draft",
            "created_at": datetime.utcnow().isoformat()
        }
        
        return {
            "artifacts": {"solution": solution},
            "events": [{"type": "solution_created", "event_id": generate_event_id()}]
        }
