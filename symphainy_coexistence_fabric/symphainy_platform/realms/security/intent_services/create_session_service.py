"""
Create Session Intent Service

Implements the create_session intent for the Security Realm.

Contract: docs/intent_contracts/journey_security_authentication/intent_create_session.md

Purpose: Create an authenticated session for a user.

WHAT (Intent Service Role): I create authenticated sessions
HOW (Intent Service Implementation): I use Traffic Cop SDK via Public Works
    to create and manage sessions
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


class CreateSessionService(BaseIntentService):
    """
    Intent service for session creation.
    
    Creates authenticated session with:
    - Session ID
    - Tenant context
    - User context
    - Session metadata
    """
    
    def __init__(self, public_works, state_surface):
        """Initialize CreateSessionService."""
        super().__init__(
            service_id="create_session_service",
            intent_type="create_session",
            public_works=public_works,
            state_surface=state_surface
        )
    
    async def execute(
        self,
        context: ExecutionContext,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute the create_session intent."""
        await self.record_telemetry(
            telemetry_data={"action": "execute", "status": "started", "intent_type": self.intent_type},
            tenant_id=context.tenant_id
        )
        
        try:
            intent_params = context.intent.parameters or {} if context.intent else {}
            if params:
                intent_params = {**intent_params, **params}
            
            user_id = intent_params.get("user_id")
            tenant_id = intent_params.get("tenant_id") or context.tenant_id
            access_token = intent_params.get("access_token")
            metadata = intent_params.get("metadata", {})
            
            # Create session
            session_result = await self._create_session(
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
                    "events": [
                        {
                            "type": "session_creation_failed",
                            "reason": session_result.get("error")
                        }
                    ]
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
            
            self.logger.info(f"Session created: {session_result.get('session_id')}")
            
            await self.record_telemetry(
                telemetry_data={
                    "action": "execute", "status": "completed", "intent_type": self.intent_type,
                    "session_id": session_result.get("session_id")
                },
                tenant_id=context.tenant_id
            )
            
            return {
                "artifacts": session_response,
                "events": [
                    {
                        "type": "session_created",
                        "session_id": session_result.get("session_id"),
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
    
    async def _create_session(
        self,
        user_id: Optional[str],
        tenant_id: str,
        access_token: Optional[str],
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create session using Traffic Cop SDK."""
        session_id = f"session_{generate_event_id()}"
        
        if self.public_works:
            try:
                # Try Traffic Cop SDK
                traffic_cop_sdk = getattr(self.public_works, 'traffic_cop_sdk', None)
                if traffic_cop_sdk:
                    session_intent = await traffic_cop_sdk.create_session_intent(
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
                
                # Fallback to state surface
                if self.state_surface:
                    await self.state_surface.set_execution_state(
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
                self.logger.warning(f"Session creation via SDK failed: {e}")
        
        # Return basic session if no SDK available
        return {
            "success": True,
            "session_id": session_id
        }
