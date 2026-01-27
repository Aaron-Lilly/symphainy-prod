"""
Authenticate User Intent Service

Implements the authenticate_user intent for the Security Realm.

Contract: docs/intent_contracts/journey_security_authentication/intent_authenticate_user.md

Purpose: Authenticate user credentials and return authentication result.

WHAT (Intent Service Role): I authenticate user credentials
HOW (Intent Service Implementation): I use Security Guard SDK via Public Works
    to validate credentials and return auth tokens

Architecture:
- Wraps Security Guard SDK infrastructure
- Uses auth_abstraction from Public Works
- Returns structured authentication result
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


class AuthenticateUserService(BaseIntentService):
    """
    Intent service for user authentication.
    
    Authenticates user credentials and returns:
    - Access token
    - Refresh token
    - User info (id, email, roles, permissions)
    - Tenant context
    """
    
    def __init__(self, public_works, state_surface):
        """Initialize AuthenticateUserService."""
        super().__init__(
            service_id="authenticate_user_service",
            intent_type="authenticate_user",
            public_works=public_works,
            state_surface=state_surface
        )
    
    async def execute(
        self,
        context: ExecutionContext,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute the authenticate_user intent."""
        await self.record_telemetry(
            telemetry_data={"action": "execute", "status": "started", "intent_type": self.intent_type},
            tenant_id=context.tenant_id
        )
        
        try:
            intent_params = context.intent.parameters or {} if context.intent else {}
            if params:
                intent_params = {**intent_params, **params}
            
            email = intent_params.get("email")
            password = intent_params.get("password")
            
            if not email or not password:
                raise ValueError("email and password are required for authentication")
            
            # Get auth abstraction from Public Works
            auth_result = await self._authenticate(email, password)
            
            if not auth_result.get("success"):
                self.logger.warning(f"Authentication failed for {email}")
                return {
                    "artifacts": {
                        "authenticated": False,
                        "error": auth_result.get("error", "Authentication failed")
                    },
                    "events": [
                        {
                            "type": "authentication_failed",
                            "email": email,
                            "reason": auth_result.get("error", "Invalid credentials")
                        }
                    ]
                }
            
            # Build authentication response
            auth_response = {
                "authenticated": True,
                "access_token": auth_result.get("access_token"),
                "refresh_token": auth_result.get("refresh_token"),
                "user": {
                    "id": auth_result.get("user_id"),
                    "email": auth_result.get("email", email),
                    "roles": auth_result.get("roles", []),
                    "permissions": auth_result.get("permissions", [])
                },
                "tenant_id": auth_result.get("tenant_id"),
                "authenticated_at": datetime.utcnow().isoformat()
            }
            
            # Store audit log in Artifact Plane
            await self._store_audit_log("authenticate", email, True, context)
            
            self.logger.info(f"User authenticated: {email}")
            
            await self.record_telemetry(
                telemetry_data={
                    "action": "execute", "status": "completed", "intent_type": self.intent_type,
                    "user_id": auth_result.get("user_id")
                },
                tenant_id=context.tenant_id
            )
            
            return {
                "artifacts": auth_response,
                "events": [
                    {
                        "type": "user_authenticated",
                        "user_id": auth_result.get("user_id"),
                        "tenant_id": auth_result.get("tenant_id")
                    }
                ]
            }
            
        except Exception as e:
            await self.record_telemetry(
                telemetry_data={"action": "execute", "status": "failed", "error": str(e)},
                tenant_id=context.tenant_id
            )
            raise
    
    async def _authenticate(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate using Public Works auth abstraction."""
        if self.public_works:
            try:
                # Try to get Security Guard SDK
                security_guard_sdk = getattr(self.public_works, 'security_guard_sdk', None)
                if security_guard_sdk:
                    result = await security_guard_sdk.authenticate({
                        "email": email,
                        "password": password
                    })
                    if result:
                        return {
                            "success": True,
                            "user_id": result.user_id,
                            "email": result.email,
                            "tenant_id": result.tenant_id,
                            "roles": result.roles,
                            "permissions": result.permissions,
                            "access_token": result.execution_contract.get("access_token"),
                            "refresh_token": result.execution_contract.get("refresh_token")
                        }
                
                # Fallback to auth_abstraction directly
                auth_abstraction = self.public_works.get_auth_abstraction()
                if auth_abstraction:
                    result = await auth_abstraction.authenticate({
                        "email": email,
                        "password": password
                    })
                    if result and result.get("success"):
                        return result
            except Exception as e:
                self.logger.warning(f"Authentication via Public Works failed: {e}")
        
        return {"success": False, "error": "Authentication service unavailable"}
    
    async def _store_audit_log(
        self,
        action: str,
        email: str,
        success: bool,
        context: ExecutionContext
    ):
        """Store authentication audit log."""
        if self.public_works:
            try:
                artifact_plane = self.public_works.get_artifact_plane()
                if artifact_plane:
                    await artifact_plane.create_artifact(
                        artifact_type="security_audit_log",
                        content={
                            "action": action,
                            "email": email,
                            "success": success,
                            "timestamp": datetime.utcnow().isoformat(),
                            "ip_address": context.metadata.get("ip_address") if context.metadata else None
                        },
                        metadata={"action": action, "success": success},
                        tenant_id=context.tenant_id,
                        include_payload=True
                    )
            except Exception as e:
                self.logger.debug(f"Could not store audit log: {e}")
