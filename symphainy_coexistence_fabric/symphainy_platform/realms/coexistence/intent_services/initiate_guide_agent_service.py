"""
Initiate Guide Agent Intent Service

Implements the initiate_guide_agent intent for the Coexistence Realm.

Purpose: Start a Guide Agent session for AI-assisted platform navigation.

WHAT (Intent Service Role): I initiate Guide Agent sessions
HOW (Intent Service Implementation): I create a session context and
    return initial guidance with available capabilities
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

project_root = Path(__file__).resolve().parents[6]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from symphainy_platform.bases.intent_service_base import BaseIntentService
from symphainy_platform.runtime.execution_context import ExecutionContext
from utilities import generate_event_id


class InitiateGuideAgentService(BaseIntentService):
    """
    Intent service for initiating Guide Agent sessions.
    
    Creates a session with:
    - Session ID for tracking
    - Initial context and capabilities
    - Suggested conversation starters
    """
    
    def __init__(self, public_works, state_surface):
        """Initialize InitiateGuideAgentService."""
        super().__init__(
            service_id="initiate_guide_agent_service",
            intent_type="initiate_guide_agent",
            public_works=public_works,
            state_surface=state_surface
        )
    
    async def execute(
        self,
        context: ExecutionContext,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute the initiate_guide_agent intent."""
        await self.record_telemetry(
            telemetry_data={"action": "execute", "status": "started"},
            tenant_id=context.tenant_id
        )
        
        try:
            intent_params = context.intent.parameters or {} if context.intent else {}
            if params:
                intent_params = {**intent_params, **params}
            
            user_context = intent_params.get("user_context", {})
            initial_query = intent_params.get("initial_query")
            
            # Create Guide Agent session
            guide_session_id = generate_event_id()
            session = await self._create_guide_session(
                guide_session_id,
                context.tenant_id,
                context.session_id,
                user_context,
                initial_query
            )
            
            await self.record_telemetry(
                telemetry_data={"action": "execute", "status": "success", "guide_session_id": guide_session_id},
                tenant_id=context.tenant_id
            )
            
            return {
                "success": True,
                "guide_session": session,
                "timestamp": datetime.utcnow().isoformat(),
                "events": [
                    {
                        "event_id": generate_event_id(),
                        "event_type": "guide_agent_initiated",
                        "timestamp": datetime.utcnow().isoformat(),
                        "guide_session_id": guide_session_id
                    }
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Failed to initiate guide agent: {e}")
            return {"success": False, "error": str(e)}
    
    async def _create_guide_session(
        self,
        guide_session_id: str,
        tenant_id: str,
        session_id: str,
        user_context: Dict,
        initial_query: Optional[str]
    ) -> Dict[str, Any]:
        """Create a Guide Agent session."""
        session = {
            "guide_session_id": guide_session_id,
            "tenant_id": tenant_id,
            "platform_session_id": session_id,
            "status": "active",
            "created_at": datetime.utcnow().isoformat(),
            "capabilities": {
                "can_navigate": True,
                "can_explain": True,
                "can_handoff": True,
                "can_execute_tools": True
            },
            "available_solutions": [
                "content_solution",
                "insights_solution",
                "operations_solution",
                "outcomes_solution"
            ],
            "available_liaison_agents": [
                {"agent": "ContentLiaisonAgent", "domain": "content"},
                {"agent": "InsightsLiaisonAgent", "domain": "insights"},
                {"agent": "OperationsLiaisonAgent", "domain": "operations"},
                {"agent": "OutcomesLiaisonAgent", "domain": "outcomes"}
            ],
            "greeting": {
                "message": "Hello! I'm your Guide Agent. I can help you navigate the platform, understand its capabilities, and connect you with specialized agents for specific domains.",
                "suggested_prompts": [
                    "What can this platform do?",
                    "Help me upload and analyze a file",
                    "I need to create an SOP",
                    "Show me my data quality"
                ]
            },
            "context": user_context
        }
        
        # If there's an initial query, include initial response context
        if initial_query:
            session["initial_query"] = initial_query
            session["ready_for_response"] = True
        
        # Store session in state surface if available
        if self.state_surface:
            try:
                await self.state_surface.set_state(
                    key=f"guide_session:{guide_session_id}",
                    value=session,
                    tenant_id=tenant_id
                )
            except Exception as e:
                self.logger.warning(f"Could not persist guide session: {e}")
        
        return session
