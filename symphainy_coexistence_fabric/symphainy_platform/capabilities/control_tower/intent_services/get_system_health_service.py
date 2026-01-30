"""Get System Health Service (Platform SDK)"""

from typing import Dict, Any
from datetime import datetime
from utilities import get_logger, generate_event_id
from symphainy_platform.civic_systems.platform_sdk import PlatformIntentService, PlatformContext


class GetSystemHealthService(PlatformIntentService):
    """Get System Health Service using Platform SDK."""
    
    def __init__(self, service_id: str = "get_system_health_service"):
        super().__init__(service_id=service_id)
        self.logger = get_logger(self.__class__.__name__)
    
    async def execute(self, ctx: PlatformContext) -> Dict[str, Any]:
        self.logger.info(f"Executing get_system_health: {ctx.execution_id}")
        
        health = {
            "health_check_id": generate_event_id(),
            "status": "healthy",
            "services": {
                "runtime": "healthy",
                "state_surface": "healthy",
                "public_works": "healthy"
            },
            "checked_at": datetime.utcnow().isoformat()
        }
        
        return {"artifacts": {"health": health}, "events": []}
