"""Get Solution Status Service (Platform SDK)"""

from typing import Dict, Any
from datetime import datetime
from utilities import get_logger, generate_event_id
from symphainy_platform.civic_systems.platform_sdk import PlatformIntentService, PlatformContext


class GetSolutionStatusService(PlatformIntentService):
    """Get Solution Status Service using Platform SDK."""
    
    intent_type = "get_solution_status"
    
    def __init__(self, service_id: str = "get_solution_status_service"):
        super().__init__(service_id=service_id, intent_type="get_solution_status")
        self.logger = get_logger(self.__class__.__name__)
    
    async def execute(self, ctx: PlatformContext) -> Dict[str, Any]:
        self.logger.info(f"Executing get_solution_status: {ctx.execution_id}")
        
        solution_id = ctx.intent.parameters.get("solution_id")
        if not solution_id:
            raise ValueError("solution_id is required")
        
        status = {
            "solution_id": solution_id,
            "status": "active",
            "intents_registered": True,
            "mcp_server_running": True,
            "checked_at": datetime.utcnow().isoformat()
        }
        
        return {"artifacts": {"status": status}, "events": []}
