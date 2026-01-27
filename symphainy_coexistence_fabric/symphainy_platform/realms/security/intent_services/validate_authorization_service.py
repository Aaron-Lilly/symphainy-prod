"""
Validate Authorization Intent Service

Implements the validate_authorization intent for the Security Realm.

Contract: docs/intent_contracts/journey_security_authentication/intent_validate_authorization.md

Purpose: Check if user has permission to perform an action on a resource.

WHAT (Intent Service Role): I validate user authorization
HOW (Intent Service Implementation): I use Security Guard SDK to check permissions
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


class ValidateAuthorizationService(BaseIntentService):
    """
    Intent service for authorization validation.
    
    Checks if user has permission for:
    - Specific action (read, write, delete, etc.)
    - Specific resource (file, workflow, etc.)
    """
    
    def __init__(self, public_works, state_surface):
        """Initialize ValidateAuthorizationService."""
        super().__init__(
            service_id="validate_authorization_service",
            intent_type="validate_authorization",
            public_works=public_works,
            state_surface=state_surface
        )
    
    async def execute(
        self,
        context: ExecutionContext,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute the validate_authorization intent."""
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
            action = intent_params.get("action")
            resource = intent_params.get("resource")
            
            if not action:
                raise ValueError("action is required for authorization validation")
            
            # Validate authorization
            auth_result = await self._validate_authorization(
                user_id=user_id,
                tenant_id=tenant_id,
                action=action,
                resource=resource
            )
            
            authorization_response = {
                "authorized": auth_result.get("authorized", False),
                "user_id": user_id,
                "tenant_id": tenant_id,
                "action": action,
                "resource": resource,
                "roles": auth_result.get("roles", []),
                "permissions": auth_result.get("permissions", []),
                "checked_at": datetime.utcnow().isoformat()
            }
            
            self.logger.info(
                f"Authorization check: user={user_id}, action={action}, "
                f"authorized={auth_result.get('authorized')}"
            )
            
            await self.record_telemetry(
                telemetry_data={
                    "action": "execute", "status": "completed", "intent_type": self.intent_type,
                    "authorized": auth_result.get("authorized")
                },
                tenant_id=context.tenant_id
            )
            
            return {
                "artifacts": authorization_response,
                "events": [
                    {
                        "type": "authorization_checked",
                        "user_id": user_id,
                        "action": action,
                        "authorized": auth_result.get("authorized")
                    }
                ]
            }
            
        except Exception as e:
            await self.record_telemetry(
                telemetry_data={"action": "execute", "status": "failed", "error": str(e)},
                tenant_id=context.tenant_id
            )
            raise
    
    async def _validate_authorization(
        self,
        user_id: Optional[str],
        tenant_id: str,
        action: str,
        resource: Optional[str]
    ) -> Dict[str, Any]:
        """Validate authorization using Security Guard SDK."""
        if self.public_works:
            try:
                security_guard_sdk = getattr(self.public_works, 'security_guard_sdk', None)
                if security_guard_sdk:
                    result = await security_guard_sdk.authorize(
                        user_id=user_id,
                        tenant_id=tenant_id,
                        action=action,
                        resource=resource
                    )
                    if result and result.get("prepared"):
                        # For MVP, if preparation succeeded, consider authorized
                        return {
                            "authorized": True,
                            "roles": result.get("execution_contract", {}).get("roles", []),
                            "permissions": result.get("execution_contract", {}).get("permissions", [])
                        }
            except Exception as e:
                self.logger.warning(f"Authorization check failed: {e}")
        
        # Default: allow basic actions for authenticated users
        if user_id:
            return {
                "authorized": action in ["read", "write"],
                "roles": ["user"],
                "permissions": ["read", "write"]
            }
        
        return {"authorized": False}
