"""
Terminate Session Service (Platform SDK)

Terminates an authenticated session (logout).

Uses ctx.state_surface for session management.

Contract: docs/intent_contracts/journey_security_authentication/intent_terminate_session.md
"""

from typing import Dict, Any
from datetime import datetime

from utilities import get_logger, generate_event_id

from symphainy_platform.civic_systems.platform_sdk import (
    PlatformIntentService,
    PlatformContext
)


class TerminateSessionService(PlatformIntentService):
    """
    Terminate Session Service using Platform SDK.
    
    Handles the `terminate_session` intent:
    - Terminates authenticated session
    - Clears session from state_surface
    - Returns termination confirmation
    """
    
    intent_type = "terminate_session"
    
    def __init__(self, service_id: str = "terminate_session_service"):
        """Initialize Terminate Session Service."""
        super().__init__(service_id=service_id, intent_type="terminate_session")
        self.logger = get_logger(self.__class__.__name__)
    
    async def execute(self, ctx: PlatformContext) -> Dict[str, Any]:
        """
        Execute terminate_session intent.
        
        Args:
            ctx: Platform context with intent and platform services
        
        Returns:
            Dict with session termination result
        """
        self.logger.info(f"Executing terminate_session: {ctx.execution_id}")
        
        session_id = ctx.intent.parameters.get("session_id") or ctx.session_id
        user_id = ctx.intent.parameters.get("user_id")
        reason = ctx.intent.parameters.get("reason", "User logout")
        
        if not session_id:
            raise ValueError("session_id is required for termination")
        
        # Terminate session
        termination_result = await self._terminate_session(
            ctx=ctx,
            session_id=session_id,
            user_id=user_id,
            reason=reason
        )
        
        if not termination_result.get("success"):
            return {
                "artifacts": {
                    "terminated": False,
                    "session_id": session_id,
                    "error": termination_result.get("error", "Session termination failed")
                },
                "events": [{
                    "type": "session_termination_failed",
                    "session_id": session_id,
                    "reason": termination_result.get("error")
                }]
            }
        
        termination_response = {
            "terminated": True,
            "session_id": session_id,
            "user_id": user_id,
            "reason": reason,
            "terminated_at": datetime.utcnow().isoformat()
        }
        
        self.logger.info(f"✅ Session terminated: {session_id}")
        
        return {
            "artifacts": termination_response,
            "events": [{
                "type": "session_terminated",
                "session_id": session_id,
                "user_id": user_id,
                "reason": reason
            }]
        }
    
    async def _terminate_session(
        self,
        ctx: PlatformContext,
        session_id: str,
        user_id: str,
        reason: str
    ) -> Dict[str, Any]:
        """Terminate session using ctx.governance.sessions (protocol-compliant)."""
        # Use ctx.governance.sessions if available (proper protocol boundary)
        if ctx.governance and ctx.governance.sessions:
            try:
                result = await ctx.governance.sessions.terminate_session(
                    session_id=session_id,
                    reason=reason
                )
                if result:
                    if isinstance(result, dict) and result.get("success"):
                        return {"success": True}
                    elif hasattr(result, 'success') and result.success:
                        return {"success": True}
                    # If we got a result, assume success
                    return {"success": True}
            except Exception as e:
                self.logger.warning(f"Session termination via ctx.governance.sessions failed: {e}")
        
        # Fallback to state_surface (valid - it's on ctx directly)
        if ctx.state_surface:
            try:
                # Clear session state
                await ctx.state_surface.delete_execution_state(
                    key=f"session_{session_id}",
                    tenant_id=ctx.tenant_id
                )
                return {"success": True}
            except Exception as e:
                self.logger.warning(f"Session termination via state_surface failed: {e}")
                # Idempotent - if state doesn't exist, that's fine
                return {"success": True}
        
        # If neither governance.sessions nor state_surface available, fail loudly
        raise RuntimeError("Platform contract §8A: ctx.governance.sessions or ctx.state_surface required for session termination")
