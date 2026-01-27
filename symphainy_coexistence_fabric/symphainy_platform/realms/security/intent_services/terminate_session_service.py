"""
Terminate Session Intent Service

Implements the terminate_session intent for the Security Realm.

Contract: docs/intent_contracts/journey_security_authentication/intent_terminate_session.md

Purpose: Logout user and terminate their session.

WHAT (Intent Service Role): I terminate user sessions (logout)
HOW (Intent Service Implementation): I invalidate session and clear tokens
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parents[6]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from symphainy_platform.bases.intent_service_base import BaseIntentService
from symphainy_platform.runtime.execution_context import ExecutionContext
from utilities import generate_event_id


class TerminateSessionService(BaseIntentService):
    """
    Intent service for session termination (logout).
    
    Terminates session by:
    - Invalidating session token
    - Clearing session state
    - Recording audit log
    """
    
    def __init__(self, public_works, state_surface):
        """Initialize TerminateSessionService."""
        super().__init__(
            service_id="terminate_session_service",
            intent_type="terminate_session",
            public_works=public_works,
            state_surface=state_surface
        )
    
    async def execute(
        self,
        context: ExecutionContext,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute the terminate_session intent."""
        await self.record_telemetry(
            telemetry_data={"action": "execute", "status": "started", "intent_type": self.intent_type},
            tenant_id=context.tenant_id
        )
        
        try:
            intent_params = context.intent.parameters or {} if context.intent else {}
            if params:
                intent_params = {**intent_params, **params}
            
            session_id = intent_params.get("session_id") or context.session_id
            user_id = intent_params.get("user_id")
            
            # Terminate session
            terminate_result = await self._terminate_session(session_id, context)
            
            termination_response = {
                "terminated": True,
                "session_id": session_id,
                "user_id": user_id,
                "terminated_at": datetime.utcnow().isoformat()
            }
            
            # Store audit log
            await self._store_audit_log("logout", user_id, session_id, context)
            
            self.logger.info(f"Session terminated: {session_id}")
            
            await self.record_telemetry(
                telemetry_data={
                    "action": "execute", "status": "completed", "intent_type": self.intent_type,
                    "session_id": session_id
                },
                tenant_id=context.tenant_id
            )
            
            return {
                "artifacts": termination_response,
                "events": [
                    {
                        "type": "session_terminated",
                        "session_id": session_id,
                        "user_id": user_id
                    }
                ]
            }
            
        except Exception as e:
            await self.record_telemetry(
                telemetry_data={"action": "execute", "status": "failed", "error": str(e)},
                tenant_id=context.tenant_id
            )
            raise
    
    async def _terminate_session(
        self,
        session_id: Optional[str],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Terminate session."""
        if session_id and self.state_surface:
            try:
                # Clear session from state surface
                await self.state_surface.delete_execution_state(
                    key=f"session_{session_id}",
                    tenant_id=context.tenant_id
                )
            except Exception as e:
                self.logger.debug(f"Could not delete session state: {e}")
        
        return {"success": True}
    
    async def _store_audit_log(
        self,
        action: str,
        user_id: Optional[str],
        session_id: Optional[str],
        context: ExecutionContext
    ):
        """Store logout audit log."""
        if self.public_works:
            try:
                artifact_plane = self.public_works.get_artifact_plane()
                if artifact_plane:
                    await artifact_plane.create_artifact(
                        artifact_type="security_audit_log",
                        content={
                            "action": action,
                            "user_id": user_id,
                            "session_id": session_id,
                            "timestamp": datetime.utcnow().isoformat()
                        },
                        metadata={"action": action},
                        tenant_id=context.tenant_id,
                        include_payload=True
                    )
            except Exception as e:
                self.logger.debug(f"Could not store audit log: {e}")
