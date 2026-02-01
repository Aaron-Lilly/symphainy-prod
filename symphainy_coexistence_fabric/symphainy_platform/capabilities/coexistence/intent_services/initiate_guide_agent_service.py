"""
Initiate Guide Agent Service (Platform SDK)

Starts a Guide Agent session for AI-assisted platform navigation.

Uses ctx.reasoning.agents.invoke() to call the REAL GuideAgent with LLM.

Contract: docs/intent_contracts/coexistence/intent_initiate_guide_agent.md

ARCHITECTURE: No fake fallbacks. If AI unavailable, session still created but
guidance_status indicates unavailability. Frontend can handle gracefully.
"""

from typing import Dict, Any, Optional
from datetime import datetime

from utilities import get_logger, generate_event_id

from symphainy_platform.civic_systems.platform_sdk import (
    PlatformIntentService,
    PlatformContext
)


class InitiateGuideAgentService(PlatformIntentService):
    """
    Initiate Guide Agent Service using Platform SDK.
    
    Handles the `initiate_guide_agent` intent:
    - Creates a guide session with session state
    - Invokes GuideAgent for initial journey guidance
    - Returns session info with available capabilities
    
    KEY: Uses ctx.reasoning.agents.invoke("guide_agent", ...) for real AI.
    No fake fallbacks - if AI unavailable, guidance_status indicates this.
    """
    
    intent_type = "initiate_guide_agent"
    
    def __init__(self, service_id: str = "initiate_guide_agent_service"):
        """Initialize Initiate Guide Agent Service."""
        super().__init__(service_id=service_id, intent_type="initiate_guide_agent")
        self.logger = get_logger(self.__class__.__name__)
    
    async def execute(self, ctx: PlatformContext) -> Dict[str, Any]:
        """
        Execute initiate_guide_agent intent.
        
        Args:
            ctx: Platform context with intent and platform services
        
        Returns:
            Dict with guide session info and initial guidance
        """
        self.logger.info(f"Executing initiate_guide_agent: {ctx.execution_id}")
        
        user_context = ctx.intent.parameters.get("user_context", {})
        initial_query = ctx.intent.parameters.get("initial_query")
        
        # Create Guide Agent session
        guide_session_id = generate_event_id()
        
        # Build session data
        session = {
            "guide_session_id": guide_session_id,
            "tenant_id": ctx.tenant_id,
            "platform_session_id": ctx.session_id,
            "status": "active",
            "created_at": datetime.utcnow().isoformat(),
            "capabilities": {
                "can_navigate": True,
                "can_explain": True,
                "can_handoff": True,
                "can_execute_tools": True,
                "uses_real_llm": True  # KEY: This is real AI now
            },
            "available_solutions": [
                "content_solution",
                "insights_solution",
                "operations_solution",
                "outcomes_solution"
            ],
            "context": user_context
        }
        
        # Get initial guidance from REAL GuideAgent via ctx.reasoning
        initial_guidance = None
        guidance_status = "unavailable"
        guidance_error = None
        
        if ctx.reasoning and ctx.reasoning.agents:
            try:
                # Invoke the real GuideAgent for journey guidance
                agent_result = await ctx.reasoning.agents.invoke(
                    "guide_agent",
                    params={
                        "action": "get_journey_guidance",
                        "user_state": user_context
                    },
                    context={
                        "tenant_id": ctx.tenant_id,
                        "session_id": ctx.session_id
                    }
                )
                
                if agent_result.get("status") == "completed":
                    initial_guidance = agent_result.get("result", {})
                    session["initial_guidance"] = initial_guidance
                    guidance_status = "available"
                    self.logger.info("✅ Got initial guidance from real GuideAgent")
                else:
                    guidance_error = agent_result.get("error", "Agent returned non-completed status")
                    self.logger.warning(f"GuideAgent invocation incomplete: {guidance_error}")
                    
            except Exception as e:
                guidance_error = str(e)
                self.logger.warning(f"Could not get initial guidance from GuideAgent: {e}")
        else:
            guidance_error = "Reasoning service not available"
            self.logger.warning("Reasoning service not available for initial guidance")
        
        # Record guidance status (NO FAKE DATA)
        session["guidance_status"] = guidance_status
        if guidance_error:
            session["guidance_error"] = guidance_error
        
        # Build greeting with real or fallback guidance
        greeting = self._build_greeting(initial_guidance)
        session["greeting"] = greeting
        
        # If there's an initial query, process it via real agent
        if initial_query:
            session["initial_query"] = initial_query
            session["ready_for_response"] = True
            
            # Process the initial query via GuideAgent
            if ctx.reasoning and ctx.reasoning.agents:
                try:
                    query_result = await ctx.reasoning.agents.invoke(
                        "guide_agent",
                        params={
                            "action": "process_chat_message",
                            "message": initial_query,
                            "session_id": guide_session_id
                        },
                        context={
                            "tenant_id": ctx.tenant_id,
                            "session_id": ctx.session_id
                        }
                    )
                    
                    if query_result.get("status") == "completed":
                        session["initial_response"] = query_result.get("result", {})
                        
                except Exception as e:
                    self.logger.warning(f"Could not process initial query: {e}")
        
        # Store session in state_surface
        if ctx.state_surface:
            try:
                await ctx.state_surface.set_state(
                    key=f"guide_session:{guide_session_id}",
                    value=session,
                    tenant_id=ctx.tenant_id
                )
            except Exception as e:
                self.logger.warning(f"Could not persist guide session: {e}")
        
        self.logger.info(f"✅ Guide Agent session initiated: {guide_session_id}")
        
        return {
            "artifacts": {
                "guide_session": session
            },
            "events": [{
                "type": "guide_agent_initiated",
                "event_id": generate_event_id(),
                "guide_session_id": guide_session_id,
                "guidance_status": guidance_status,
                "ai_available": guidance_status == "available"
            }]
        }
    
    def _build_greeting(self, guidance: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Build greeting with guidance-informed suggestions."""
        base_greeting = {
            "message": "Hello! I'm your Guide Agent, powered by AI. I can help you navigate the platform, understand its capabilities, and connect you with specialized agents for specific domains. What would you like to explore?",
            "suggested_prompts": [
                "What can this platform do?",
                "Help me upload and analyze a file",
                "I need to create an SOP",
                "Show me my data quality"
            ]
        }
        
        # Enhance greeting with journey guidance if available
        if guidance:
            recommended = guidance.get("recommended_pillar")
            if recommended:
                base_greeting["recommended_next"] = {
                    "pillar": recommended,
                    "action": guidance.get("recommended_action"),
                    "reasoning": guidance.get("reasoning")
                }
        
        return base_greeting
