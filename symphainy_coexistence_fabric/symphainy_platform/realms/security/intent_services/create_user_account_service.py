"""
Create User Account Intent Service

Implements the create_user_account intent for the Security Realm.

Contract: docs/intent_contracts/journey_security_registration/intent_create_user_account.md

Purpose: Register a new user account.

WHAT (Intent Service Role): I create new user accounts
HOW (Intent Service Implementation): I use Security Guard SDK via Public Works
    to register users and return auth tokens
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


class CreateUserAccountService(BaseIntentService):
    """
    Intent service for user registration.
    
    Creates new user account and returns:
    - Access token
    - Refresh token
    - User info (id, email, roles, permissions)
    - Tenant context
    """
    
    def __init__(self, public_works, state_surface):
        """Initialize CreateUserAccountService."""
        super().__init__(
            service_id="create_user_account_service",
            intent_type="create_user_account",
            public_works=public_works,
            state_surface=state_surface
        )
    
    async def execute(
        self,
        context: ExecutionContext,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute the create_user_account intent."""
        await self.record_telemetry(
            telemetry_data={"action": "execute", "status": "started", "intent_type": self.intent_type},
            tenant_id=context.tenant_id
        )
        
        try:
            intent_params = context.intent.parameters or {} if context.intent else {}
            if params:
                intent_params = {**intent_params, **params}
            
            name = intent_params.get("name")
            email = intent_params.get("email")
            password = intent_params.get("password")
            
            if not email or not password:
                raise ValueError("email and password are required for registration")
            
            # Register user
            register_result = await self._register_user(name, email, password)
            
            if not register_result.get("success"):
                self.logger.warning(f"Registration failed for {email}")
                return {
                    "artifacts": {
                        "registered": False,
                        "error": register_result.get("error", "Registration failed")
                    },
                    "events": [
                        {
                            "type": "registration_failed",
                            "email": email,
                            "reason": register_result.get("error", "Registration failed")
                        }
                    ]
                }
            
            # Build registration response
            register_response = {
                "registered": True,
                "access_token": register_result.get("access_token"),
                "refresh_token": register_result.get("refresh_token"),
                "user": {
                    "id": register_result.get("user_id"),
                    "email": register_result.get("email", email),
                    "name": name,
                    "roles": register_result.get("roles", ["user"]),
                    "permissions": register_result.get("permissions", ["read", "write"])
                },
                "tenant_id": register_result.get("tenant_id"),
                "registered_at": datetime.utcnow().isoformat()
            }
            
            # Store audit log
            await self._store_audit_log("register", email, True, context)
            
            self.logger.info(f"User registered: {email}")
            
            await self.record_telemetry(
                telemetry_data={
                    "action": "execute", "status": "completed", "intent_type": self.intent_type,
                    "user_id": register_result.get("user_id")
                },
                tenant_id=context.tenant_id
            )
            
            return {
                "artifacts": register_response,
                "events": [
                    {
                        "type": "user_registered",
                        "user_id": register_result.get("user_id"),
                        "tenant_id": register_result.get("tenant_id")
                    }
                ]
            }
            
        except Exception as e:
            await self.record_telemetry(
                telemetry_data={"action": "execute", "status": "failed", "error": str(e)},
                tenant_id=context.tenant_id
            )
            raise
    
    async def _register_user(self, name: str, email: str, password: str) -> Dict[str, Any]:
        """Register user using Public Works auth abstraction."""
        if self.public_works:
            try:
                # Try Security Guard SDK first
                security_guard_sdk = getattr(self.public_works, 'security_guard_sdk', None)
                if security_guard_sdk:
                    result = await security_guard_sdk.register_user({
                        "email": email,
                        "password": password,
                        "user_metadata": {"name": name, "full_name": name}
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
                
                # Fallback to auth_abstraction
                auth_abstraction = self.public_works.get_auth_abstraction()
                if auth_abstraction:
                    result = await auth_abstraction.register_user({
                        "email": email,
                        "password": password,
                        "user_metadata": {"name": name, "full_name": name}
                    })
                    if result and result.get("success"):
                        return result
            except Exception as e:
                self.logger.warning(f"Registration via Public Works failed: {e}")
        
        return {"success": False, "error": "Registration service unavailable"}
    
    async def _store_audit_log(
        self,
        action: str,
        email: str,
        success: bool,
        context: ExecutionContext
    ):
        """Store registration audit log."""
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
                            "timestamp": datetime.utcnow().isoformat()
                        },
                        metadata={"action": action},
                        tenant_id=context.tenant_id,
                        include_payload=True
                    )
            except Exception as e:
                self.logger.debug(f"Could not store audit log: {e}")
