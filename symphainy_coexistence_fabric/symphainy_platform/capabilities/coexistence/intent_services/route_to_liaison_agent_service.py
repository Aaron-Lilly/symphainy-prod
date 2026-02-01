"""
Route to Liaison Agent Service (Platform SDK)

Routes conversations from Guide Agent to specialized Liaison Agents.

Uses ctx.reasoning.agents.invoke() to call REAL liaison agents.

Contract: docs/intent_contracts/coexistence/intent_route_to_liaison_agent.md
"""

from typing import Dict, Any, Optional
from datetime import datetime

from utilities import get_logger, generate_event_id

from symphainy_platform.civic_systems.platform_sdk import (
    PlatformIntentService,
    PlatformContext
)


class RouteToLiaisonAgentService(PlatformIntentService):
    """
    Route to Liaison Agent Service using Platform SDK.
    
    Handles the `route_to_liaison_agent` intent:
    - Validates target domain
    - Creates handoff context
    - Attempts to invoke real liaison agent for initial greeting
    
    Uses ctx.reasoning.agents.invoke() for real agent handoffs.
    If agent unavailable, returns routing info with greeting_source="default".
    """
    
    intent_type = "route_to_liaison_agent"
    
    # Liaison agent mappings
    LIAISON_AGENTS = {
        "content": {
            "agent_id": "content_liaison_agent",
            "name": "Content Liaison Agent",
            "domain": "content",
            "solution": "content_solution",
            "capabilities": [
                "File upload assistance",
                "Content parsing guidance",
                "Embedding creation help",
                "File management support"
            ]
        },
        "insights": {
            "agent_id": "insights_liaison_agent",
            "name": "Insights Liaison Agent",
            "domain": "insights",
            "solution": "insights_solution",
            "capabilities": [
                "Data quality assessment",
                "Data interpretation guidance",
                "Lineage visualization help",
                "Relationship mapping support"
            ]
        },
        "operations": {
            "agent_id": "operations_liaison_agent",
            "name": "Operations Liaison Agent",
            "domain": "operations",
            "solution": "operations_solution",
            "capabilities": [
                "SOP generation assistance",
                "Workflow optimization guidance",
                "Coexistence analysis help",
                "Process documentation support"
            ]
        },
        "outcomes": {
            "agent_id": "outcomes_liaison_agent",
            "name": "Outcomes Liaison Agent",
            "domain": "outcomes",
            "solution": "outcomes_solution",
            "capabilities": [
                "Outcome synthesis assistance",
                "Roadmap generation guidance",
                "POC creation help",
                "Blueprint design support"
            ]
        }
    }
    
    def __init__(self, service_id: str = "route_to_liaison_agent_service"):
        """Initialize Route to Liaison Agent Service."""
        super().__init__(service_id=service_id, intent_type="route_to_liaison_agent")
        self.logger = get_logger(self.__class__.__name__)
    
    async def execute(self, ctx: PlatformContext) -> Dict[str, Any]:
        """
        Execute route_to_liaison_agent intent.
        
        Args:
            ctx: Platform context with intent and platform services
        
        Returns:
            Dict with handoff information and liaison greeting
        """
        self.logger.info(f"Executing route_to_liaison_agent: {ctx.execution_id}")
        
        guide_session_id = ctx.intent.parameters.get("guide_session_id")
        target_domain = ctx.intent.parameters.get("target_domain")
        handoff_context = ctx.intent.parameters.get("handoff_context", {})
        
        if not target_domain:
            raise ValueError("target_domain is required")
        
        if target_domain not in self.LIAISON_AGENTS:
            raise ValueError(f"Unknown domain: {target_domain}. Available: {list(self.LIAISON_AGENTS.keys())}")
        
        # Create handoff with real liaison agent
        handoff = await self._create_handoff(
            ctx=ctx,
            guide_session_id=guide_session_id,
            target_domain=target_domain,
            handoff_context=handoff_context
        )
        
        self.logger.info(f"✅ Routed to {target_domain} liaison agent")
        
        return {
            "artifacts": {
                "handoff": handoff
            },
            "events": [{
                "type": "routed_to_liaison",
                "event_id": generate_event_id(),
                "target_domain": target_domain,
                "liaison_agent": handoff.get("target_agent")
            }]
        }
    
    async def _create_handoff(
        self,
        ctx: PlatformContext,
        guide_session_id: Optional[str],
        target_domain: str,
        handoff_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create handoff to real liaison agent."""
        liaison = self.LIAISON_AGENTS[target_domain]
        liaison_session_id = generate_event_id()
        
        # Build handoff record
        handoff = {
            "handoff_id": generate_event_id(),
            "guide_session_id": guide_session_id,
            "liaison_session_id": liaison_session_id,
            "target_agent": liaison["agent_id"],
            "target_name": liaison["name"],
            "target_domain": target_domain,
            "target_solution": liaison["solution"],
            "handoff_context": handoff_context,
            "liaison_capabilities": liaison["capabilities"],
            "status": "completed",
            "handoff_at": datetime.utcnow().isoformat()
        }
        
        # Try to get greeting from real liaison agent
        liaison_greeting = await self._get_liaison_greeting(
            ctx=ctx,
            agent_id=liaison["agent_id"],
            handoff_context=handoff_context
        )
        handoff["liaison_greeting"] = liaison_greeting
        
        # Store handoff in state_surface
        if ctx.state_surface:
            try:
                await ctx.state_surface.set_state(
                    key=f"liaison_session:{liaison_session_id}",
                    value={
                        "liaison_session_id": liaison_session_id,
                        "agent_id": liaison["agent_id"],
                        "domain": target_domain,
                        "solution": liaison["solution"],
                        "handoff_context": handoff_context,
                        "created_at": datetime.utcnow().isoformat()
                    },
                    tenant_id=ctx.tenant_id
                )
            except Exception as e:
                self.logger.warning(f"Could not persist liaison session: {e}")
        
        return handoff
    
    async def _get_liaison_greeting(
        self,
        ctx: PlatformContext,
        agent_id: str,
        handoff_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get greeting from real liaison agent.
        
        Returns dict with greeting text and source indicator.
        """
        # Try to invoke real liaison agent for personalized greeting
        if ctx.reasoning and ctx.reasoning.agents:
            try:
                agent_result = await ctx.reasoning.agents.invoke(
                    agent_id,
                    params={
                        "action": "get_greeting",
                        "handoff_context": handoff_context
                    },
                    context={
                        "tenant_id": ctx.tenant_id,
                        "session_id": ctx.session_id
                    }
                )
                
                if agent_result.get("status") == "completed":
                    result = agent_result.get("result", {})
                    greeting = result.get("greeting") or result.get("response")
                    if greeting:
                        self.logger.info(f"✅ Got real greeting from {agent_id}")
                        return {
                            "text": greeting,
                            "source": "agent",
                            "agent_id": agent_id
                        }
                        
            except Exception as e:
                self.logger.warning(f"Could not get greeting from {agent_id}: {e}")
        
        # Default greetings (clearly marked as default, not fake agent responses)
        default_greetings = {
            "content_liaison_agent": "Hi! I'm the Content Liaison Agent. I specialize in file management and content processing. How can I help you with your files today?",
            "insights_liaison_agent": "Hello! I'm the Insights Liaison Agent. I specialize in data analysis and insights generation. What data would you like to explore?",
            "operations_liaison_agent": "Hi there! I'm the Operations Liaison Agent. I specialize in workflows, SOPs, and process optimization. What process would you like to work on?",
            "outcomes_liaison_agent": "Hello! I'm the Outcomes Liaison Agent. I specialize in strategic deliverables and roadmaps. What outcome are you looking to create?"
        }
        
        greeting_text = default_greetings.get(agent_id, f"Hello! I'm ready to assist you with {agent_id.replace('_', ' ')}.")
        
        return {
            "text": greeting_text,
            "source": "default",  # Clearly indicates this is NOT from AI
            "agent_id": agent_id,
            "note": "AI greeting unavailable - using default"
        }
