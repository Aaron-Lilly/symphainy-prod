"""
Generate SOP From Chat Service (Platform SDK)

Interactive SOP generation through chat conversation.

Contract: docs/intent_contracts/journey_operations_sop/intent_generate_sop_from_chat.md
"""

from typing import Dict, Any
from datetime import datetime

from utilities import get_logger, generate_event_id

from symphainy_platform.civic_systems.platform_sdk import (
    PlatformIntentService,
    PlatformContext
)


class GenerateSOPFromChatService(PlatformIntentService):
    """
    Generate SOP From Chat Service using Platform SDK.
    
    Initiates interactive SOP generation session.
    """
    
    def __init__(self, service_id: str = "generate_sop_from_chat_service"):
        """Initialize Generate SOP From Chat Service."""
        super().__init__(service_id=service_id)
        self.logger = get_logger(self.__class__.__name__)
    
    async def execute(self, ctx: PlatformContext) -> Dict[str, Any]:
        """Execute generate_sop_from_chat intent."""
        self.logger.info(f"Executing generate_sop_from_chat: {ctx.execution_id}")
        
        initial_description = ctx.intent.parameters.get("initial_description", "")
        
        # Create SOP generation session
        sop_session_id = generate_event_id()
        
        session = {
            "sop_session_id": sop_session_id,
            "status": "active",
            "initial_description": initial_description,
            "conversation_history": [],
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Get initial guidance from agent
        if ctx.reasoning and ctx.reasoning.agents:
            try:
                agent_result = await ctx.reasoning.agents.invoke(
                    "sop_generation_agent",
                    params={
                        "action": "start_interactive",
                        "initial_description": initial_description
                    },
                    context={
                        "tenant_id": ctx.tenant_id,
                        "session_id": ctx.session_id
                    }
                )
                
                if agent_result.get("status") == "completed":
                    result = agent_result.get("result", {})
                    session["initial_guidance"] = result.get("guidance", "Let's create your SOP. Describe the process you want to document.")
                    session["questions"] = result.get("questions", [])
                    
            except Exception as e:
                self.logger.warning(f"Agent invocation failed: {e}")
        
        if "initial_guidance" not in session:
            session["initial_guidance"] = "Let's create your SOP. Please describe the process you want to document, including key steps and responsibilities."
        
        # Store session
        if ctx.state_surface:
            await ctx.state_surface.set_state(
                key=f"sop_session:{sop_session_id}",
                value=session,
                tenant_id=ctx.tenant_id
            )
        
        self.logger.info(f"✅ SOP chat session created: {sop_session_id}")
        
        return {
            "artifacts": {
                "sop_session": session
            },
            "events": [{
                "type": "sop_chat_initiated",
                "event_id": generate_event_id(),
                "sop_session_id": sop_session_id
            }]
        }
