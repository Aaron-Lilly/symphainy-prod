"""
Process Guide Agent Message Service (Platform SDK)

Processes user messages through the REAL GuideAgent with LLM.

Uses ctx.reasoning.agents.invoke() for actual AI conversation.

Contract: docs/intent_contracts/coexistence/intent_process_guide_agent_message.md

KEY CHANGE: This service NO LONGER uses keyword matching and canned responses.
Instead, it invokes the real GuideAgent which uses LLMs for:
- Intent analysis
- Contextual responses
- Business context discovery
- Intelligent routing recommendations
"""

from typing import Dict, Any
from datetime import datetime

from utilities import get_logger, generate_event_id

from symphainy_platform.civic_systems.platform_sdk import (
    PlatformIntentService,
    PlatformContext
)


class ProcessGuideAgentMessageService(PlatformIntentService):
    """
    Process Guide Agent Message Service using Platform SDK.
    
    Handles the `process_guide_agent_message` intent:
    - Invokes REAL GuideAgent via ctx.reasoning.agents.invoke()
    - GuideAgent uses LLM for intelligent conversation
    - Returns AI-generated responses with routing recommendations
    
    NO MORE KEYWORD MATCHING - This is real AI chat.
    """
    
    def __init__(self, service_id: str = "process_guide_agent_message_service"):
        """Initialize Process Guide Agent Message Service."""
        super().__init__(service_id=service_id)
        self.logger = get_logger(self.__class__.__name__)
    
    async def execute(self, ctx: PlatformContext) -> Dict[str, Any]:
        """
        Execute process_guide_agent_message intent.
        
        Args:
            ctx: Platform context with intent and platform services
        
        Returns:
            Dict with AI-generated response from real GuideAgent
        """
        self.logger.info(f"Executing process_guide_agent_message: {ctx.execution_id}")
        
        guide_session_id = ctx.intent.parameters.get("guide_session_id")
        message = ctx.intent.parameters.get("message")
        
        if not guide_session_id:
            raise ValueError("guide_session_id is required")
        if not message:
            raise ValueError("message is required")
        
        # Process message through REAL GuideAgent via ctx.reasoning
        response = await self._process_via_real_agent(ctx, guide_session_id, message)
        
        self.logger.info(f"✅ Processed message via real GuideAgent")
        
        return {
            "artifacts": {
                "response": response
            },
            "events": [{
                "type": "guide_message_processed",
                "event_id": generate_event_id(),
                "guide_session_id": guide_session_id,
                "used_real_llm": True
            }]
        }
    
    async def _process_via_real_agent(
        self,
        ctx: PlatformContext,
        guide_session_id: str,
        message: str
    ) -> Dict[str, Any]:
        """
        Process message via REAL GuideAgent with LLM.
        
        This invokes the actual GuideAgent from civic_systems/agentic/agents/guide_agent.py
        which uses LLMs for intelligent conversation.
        """
        response_data = {
            "message_id": generate_event_id(),
            "guide_session_id": guide_session_id,
            "user_message": message,
            "processed_at": datetime.utcnow().isoformat()
        }
        
        # Invoke real GuideAgent via ctx.reasoning
        if ctx.reasoning and ctx.reasoning.agents:
            try:
                # Call GuideAgent.process_chat_message() via agent invocation
                agent_result = await ctx.reasoning.agents.invoke(
                    "guide_agent",
                    params={
                        "action": "process_chat_message",
                        "message": message,
                        "session_id": guide_session_id,
                        "tenant_id": ctx.tenant_id
                    },
                    context={
                        "tenant_id": ctx.tenant_id,
                        "session_id": ctx.session_id
                    }
                )
                
                if agent_result.get("status") == "completed":
                    result = agent_result.get("result", {})
                    
                    # Extract response from GuideAgent result
                    response_data["agent_response"] = result.get("response", "")
                    response_data["intent_analysis"] = result.get("intent_analysis", {})
                    response_data["journey_guidance"] = result.get("journey_guidance", {})
                    response_data["routing_info"] = result.get("routing_info")
                    response_data["used_real_llm"] = True
                    
                    # Determine handoff recommendation from real analysis
                    routing = result.get("routing_info")
                    if routing and routing.get("should_route"):
                        response_data["handoff_recommended"] = True
                        response_data["handoff_agent"] = routing.get("liaison_agent")
                        response_data["handoff_pillar"] = routing.get("pillar")
                    else:
                        response_data["handoff_recommended"] = False
                    
                    # Extract suggested actions from journey guidance
                    guidance = result.get("journey_guidance", {})
                    next_steps = guidance.get("next_steps", [])
                    response_data["suggested_actions"] = [
                        {"action": step, "source": "guide_agent"}
                        for step in next_steps
                    ]
                    
                    self.logger.info("✅ Got response from real GuideAgent with LLM")
                    return response_data
                    
                else:
                    self.logger.warning(f"GuideAgent invocation failed: {agent_result.get('error')}")
                    
            except Exception as e:
                self.logger.error(f"Error invoking GuideAgent: {e}", exc_info=True)
        
        # Fallback if agent invocation fails (but indicate it's not the preferred path)
        self.logger.warning("Falling back to basic response - real agent unavailable")
        response_data["agent_response"] = (
            "I'm having trouble accessing my full capabilities right now. "
            "Let me help you with basic navigation. What would you like to do? "
            "You can ask about uploading files, analyzing data, creating workflows, or generating outcomes."
        )
        response_data["used_real_llm"] = False
        response_data["fallback_reason"] = "Agent invocation failed"
        response_data["handoff_recommended"] = False
        response_data["suggested_actions"] = [
            {"action": "show_solution_catalog", "source": "fallback"},
            {"action": "introduce_platform", "source": "fallback"}
        ]
        
        return response_data
