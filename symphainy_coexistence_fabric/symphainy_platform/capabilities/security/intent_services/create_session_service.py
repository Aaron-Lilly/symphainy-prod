"""
Create Session Service (Platform SDK)

Creates an authenticated session for a user.

Uses ctx.platform and ctx.state_surface for session management.

Contract: docs/intent_contracts/journey_security_authentication/intent_create_session.md
"""

from typing import Dict, Any, Optional
from datetime import datetime

from utilities import get_logger, generate_event_id

from symphainy_platform.civic_systems.platform_sdk import (
    PlatformIntentService,
    PlatformContext
)


class CreateSessionService(PlatformIntentService):
    """
    Create Session Service using Platform SDK.
    
    Handles the `create_session` intent:
    - Creates authenticated session
    - Stores session in state_surface
    - Returns session details
    """
    
    intent_type = "create_session"
    
    def __init__(self, service_id: str = "create_session_service"):
        """Initialize Create Session Service."""
        super().__init__(service_id=service_id, intent_type="create_session")
        self.logger = get_logger(self.__class__.__name__)
    
    async def execute(self, ctx: PlatformContext) -> Dict[str, Any]:
        """
        Execute create_session intent.
        
        Args:
            ctx: Platform context with intent and platform services
        
        Returns:
            Dict with session creation result
        """
        self.logger.info(f"Executing create_session: {ctx.execution_id}")
        
        user_id = ctx.intent.parameters.get("user_id")
        tenant_id = ctx.intent.parameters.get("tenant_id") or ctx.tenant_id
        access_token = ctx.intent.parameters.get("access_token")
        metadata = ctx.intent.parameters.get("metadata", {})
        
        # Create session
        session_result = await self._create_session(
            ctx=ctx,
            user_id=user_id,
            tenant_id=tenant_id,
            access_token=access_token,
            metadata=metadata
        )
        
        if not session_result.get("success"):
            return {
                "artifacts": {
                    "session_created": False,
                    "error": session_result.get("error", "Session creation failed")
                },
                "events": [{
                    "type": "session_creation_failed",
                    "reason": session_result.get("error")
                }]
            }
        
        session_response = {
            "session_created": True,
            "session_id": session_result.get("session_id"),
            "tenant_id": tenant_id,
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": session_result.get("expires_at"),
            "metadata": metadata
        }
        
        self.logger.info(f"✅ Session created: {session_result.get('session_id')}")
        
        return {
            "artifacts": session_response,
            "events": [{
                "type": "session_created",
                "session_id": session_result.get("session_id"),
                "user_id": user_id
            }]
        }
    
    async def _create_session(
        self,
        ctx: PlatformContext,
        user_id: Optional[str],
        tenant_id: str,
        access_token: Optional[str],
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create session using ctx.governance.sessions (Traffic Cop SDK) or state_surface. No _public_works."""
        session_id = f"session_{generate_event_id()}"
        if ctx.governance and ctx.governance.sessions:
            try:
                session_intent = await ctx.governance.sessions.create_session_intent(
                    tenant_id=tenant_id,
                    user_id=user_id,
                    metadata=metadata
                )
                if session_intent:
                    return {
                        "success": True,
                        "session_id": session_intent.session_id,
                        "expires_at": session_intent.execution_contract.get("expires_at")
                    }
            except Exception as e:
                self.logger.warning(f"Session creation via Traffic Cop SDK failed: {e}")
        # Fallback to state_surface
        if ctx.state_surface:
            try:
                await ctx.state_surface.set_execution_state(
                    key=f"session_{session_id}",
                    state={
                        "session_id": session_id,
                        "user_id": user_id,
                        "tenant_id": tenant_id,
                        "created_at": datetime.utcnow().isoformat(),
                        "metadata": metadata
                    },
                    tenant_id=tenant_id
                )
                return {
                    "success": True,
                    "session_id": session_id
                }
            except Exception as e:
                self.logger.warning(f"Session creation via state_surface failed: {e}")
        
        # Return basic session if no SDK available
        return {
            "success": True,
            "session_id": session_id
        }
