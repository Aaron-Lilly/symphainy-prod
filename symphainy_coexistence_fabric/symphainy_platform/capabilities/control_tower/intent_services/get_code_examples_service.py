"""Get Code Examples Service (Platform SDK)"""

from typing import Dict, Any
from datetime import datetime
from utilities import get_logger, generate_event_id
from symphainy_platform.civic_systems.platform_sdk import PlatformIntentService, PlatformContext


class GetCodeExamplesService(PlatformIntentService):
    """Get Code Examples Service using Platform SDK."""
    
    def __init__(self, service_id: str = "get_code_examples_service"):
        super().__init__(service_id=service_id)
        self.logger = get_logger(self.__class__.__name__)
    
    async def execute(self, ctx: PlatformContext) -> Dict[str, Any]:
        self.logger.info(f"Executing get_code_examples: {ctx.execution_id}")
        
        topic = ctx.intent.parameters.get("topic", "general")
        
        examples = [
            {
                "topic": topic,
                "title": "PlatformIntentService Example",
                "code": "class MyService(PlatformIntentService):\n    async def execute(self, ctx): ...",
            }
        ]
        
        return {"artifacts": {"examples": examples}, "events": []}
