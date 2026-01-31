"""
SOP Chat Message Service (Platform SDK)

Processes messages in an interactive SOP generation session.

Contract: docs/intent_contracts/journey_operations_sop/intent_sop_chat_message.md
"""

from typing import Dict, Any
from datetime import datetime

from utilities import get_logger, generate_event_id

from symphainy_platform.civic_systems.platform_sdk import (
    PlatformIntentService,
    PlatformContext
)


class SOPChatMessageService(PlatformIntentService):
    """
    SOP Chat Message Service using Platform SDK.
    
    Processes messages in SOP generation conversation.
    Uses real SOPGenerationAgent for intelligent responses.
    """
    
    def __init__(self, service_id: str = "sop_chat_message_service"):
        """Initialize SOP Chat Message Service."""
        super().__init__(service_id=service_id)
        self.logger = get_logger(self.__class__.__name__)
    
    async def execute(self, ctx: PlatformContext) -> Dict[str, Any]:
        """Execute sop_chat_message intent."""
        self.logger.info(f"Executing sop_chat_message: {ctx.execution_id}")
        
        sop_session_id = ctx.intent.parameters.get("sop_session_id")
        message = ctx.intent.parameters.get("message")
        
        if not sop_session_id:
            raise ValueError("sop_session_id is required")
        if not message:
            raise ValueError("message is required")
        
        # Process message via SOPGenerationAgent
        response = await self._process_message(ctx, sop_session_id, message)
        
        response_result = {
            "message_id": generate_event_id(),
            "sop_session_id": sop_session_id,
            "user_message": message,
            "agent_response": response.get("response"),
            "sop_draft": response.get("sop_draft"),
            "completion_status": response.get("completion_status", "in_progress"),
            "processed_at": datetime.utcnow().isoformat()
        }
        
        self.logger.info(f"✅ SOP chat message processed")
        
        return {
            "artifacts": {
                "response": response_result
            },
            "events": [{
                "type": "sop_chat_message_processed",
                "event_id": generate_event_id(),
                "sop_session_id": sop_session_id
            }]
        }
    
    async def _process_message(
        self,
        ctx: PlatformContext,
        sop_session_id: str,
        message: str
    ) -> Dict[str, Any]:
        """Process message via SOPGenerationAgent."""
        if ctx.reasoning and ctx.reasoning.agents:
            try:
                agent_result = await ctx.reasoning.agents.invoke(
                    "sop_generation_agent",
                    params={
                        "action": "process_message",
                        "session_id": sop_session_id,
                        "message": message
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
            "response": "I understand. Please continue describing the process.",
            "completion_status": "in_progress"
        }
