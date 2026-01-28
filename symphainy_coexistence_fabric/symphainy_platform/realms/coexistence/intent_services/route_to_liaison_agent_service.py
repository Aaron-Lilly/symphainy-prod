"""
Route to Liaison Agent Intent Service

Implements the route_to_liaison_agent intent for the Coexistence Realm.

Purpose: Route a conversation from Guide Agent to a specialized
Liaison Agent for a specific domain.

WHAT (Intent Service Role): I route conversations to Liaison Agents
HOW (Intent Service Implementation): I establish handoff context and
    transfer the conversation to the appropriate specialist
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

project_root = Path(__file__).resolve().parents[4]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from symphainy_platform.bases.intent_service_base import BaseIntentService
from symphainy_platform.runtime.execution_context import ExecutionContext
from utilities import generate_event_id


class RouteToLiaisonAgentService(BaseIntentService):
    """
    Intent service for routing to Liaison Agents.
    
    Handles:
    - Context transfer from Guide Agent
    - Liaison Agent session creation
    - Handoff acknowledgment
    """
    
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
            ],
            "greeting": "Hi! I'm the Content Liaison Agent. I specialize in file management and content processing. How can I help you with your files today?"
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
            ],
            "greeting": "Hello! I'm the Insights Liaison Agent. I specialize in data analysis and insights generation. What data would you like to explore?"
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
            ],
            "greeting": "Hi there! I'm the Operations Liaison Agent. I specialize in workflows, SOPs, and process optimization. What process would you like to work on?"
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
            ],
            "greeting": "Hello! I'm the Outcomes Liaison Agent. I specialize in strategic deliverables and roadmaps. What outcome are you looking to create?"
        }
    }
    
    def __init__(self, public_works, state_surface):
        """Initialize RouteToLiaisonAgentService."""
        super().__init__(
            service_id="route_to_liaison_agent_service",
            intent_type="route_to_liaison_agent",
            public_works=public_works,
            state_surface=state_surface
        )
    
    async def execute(
        self,
        context: ExecutionContext,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute the route_to_liaison_agent intent."""
        await self.record_telemetry(
            telemetry_data={"action": "execute", "status": "started"},
            tenant_id=context.tenant_id
        )
        
        try:
            intent_params = context.intent.parameters or {} if context.intent else {}
            if params:
                intent_params = {**intent_params, **params}
            
            guide_session_id = intent_params.get("guide_session_id")
            target_domain = intent_params.get("target_domain")
            handoff_context = intent_params.get("handoff_context", {})
            
            if not target_domain:
                raise ValueError("target_domain is required")
            
            if target_domain not in self.LIAISON_AGENTS:
                raise ValueError(f"Unknown domain: {target_domain}. Available: {list(self.LIAISON_AGENTS.keys())}")
            
            # Create handoff
            handoff = await self._create_handoff(
                guide_session_id,
                target_domain,
                handoff_context,
                context
            )
            
            await self.record_telemetry(
                telemetry_data={"action": "execute", "status": "success", "target_domain": target_domain},
                tenant_id=context.tenant_id
            )
            
            return {
                "success": True,
                "handoff": handoff,
                "timestamp": datetime.utcnow().isoformat(),
                "events": [
                    {
                        "event_id": generate_event_id(),
                        "event_type": "routed_to_liaison",
                        "timestamp": datetime.utcnow().isoformat(),
                        "target_domain": target_domain
                    }
                ]
            }
            
        except ValueError as e:
            return {"success": False, "error": str(e), "error_code": "INVALID_DOMAIN"}
        except Exception as e:
            self.logger.error(f"Failed to route: {e}")
            return {"success": False, "error": str(e)}
    
    async def _create_handoff(
        self,
        guide_session_id: Optional[str],
        target_domain: str,
        handoff_context: Dict,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Create a handoff to a Liaison Agent."""
        liaison = self.LIAISON_AGENTS[target_domain]
        liaison_session_id = generate_event_id()
        
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
            "liaison_greeting": liaison["greeting"],
            "status": "completed",
            "handoff_at": datetime.utcnow().isoformat()
        }
        
        # Store handoff in state surface if available
        if self.state_surface:
            try:
                await self.state_surface.set_state(
                    key=f"liaison_session:{liaison_session_id}",
                    value={
                        "liaison_session_id": liaison_session_id,
                        "agent_id": liaison["agent_id"],
                        "domain": target_domain,
                        "solution": liaison["solution"],
                        "handoff_context": handoff_context,
                        "created_at": datetime.utcnow().isoformat()
                    },
                    tenant_id=context.tenant_id
                )
            except Exception as e:
                self.logger.warning(f"Could not persist liaison session: {e}")
        
        return handoff
