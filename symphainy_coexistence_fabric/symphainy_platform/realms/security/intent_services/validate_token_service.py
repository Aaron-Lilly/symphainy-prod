"""
Validate Token Intent Service

Implements the validate_token intent for the Security Realm.

Contract: docs/intent_contracts/journey_security_authentication/intent_refresh_session.md

Purpose: Validate an authentication token and return user context.

WHAT (Intent Service Role): I validate authentication tokens
HOW (Intent Service Implementation): I use Security Guard SDK to validate tokens
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


class ValidateTokenService(BaseIntentService):
    """
    Intent service for token validation.
    
    Validates token and returns:
    - User context (id, email, roles, permissions)
    - Tenant context
    - Token validity status
    """
    
    def __init__(self, public_works, state_surface):
        """Initialize ValidateTokenService."""
        super().__init__(
            service_id="validate_token_service",
            intent_type="validate_token",
            public_works=public_works,
            state_surface=state_surface
        )
    
    async def execute(
        self,
        context: ExecutionContext,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute the validate_token intent."""
        await self.record_telemetry(
            telemetry_data={"action": "execute", "status": "started", "intent_type": self.intent_type},
            tenant_id=context.tenant_id
        )
        
        try:
            intent_params = context.intent.parameters or {} if context.intent else {}
            if params:
                intent_params = {**intent_params, **params}
            
            token = intent_params.get("token")
            
            if not token:
                raise ValueError("token is required for validation")
            
            # Validate token
            validation_result = await self._validate_token(token)
            
            if not validation_result.get("valid"):
                return {
                    "artifacts": {
                        "valid": False,
                        "reason": validation_result.get("reason", "Invalid token")
                    },
                    "events": [
                        {
                            "type": "token_validation_failed",
                            "reason": validation_result.get("reason")
                        }
                    ]
                }
            
            validation_response = {
                "valid": True,
                "user": {
                    "id": validation_result.get("user_id"),
                    "email": validation_result.get("email"),
                    "roles": validation_result.get("roles", []),
                    "permissions": validation_result.get("permissions", [])
                },
                "tenant_id": validation_result.get("tenant_id"),
                "validated_at": datetime.utcnow().isoformat()
            }
            
            self.logger.info(f"Token validated for user: {validation_result.get('user_id')}")
            
            await self.record_telemetry(
                telemetry_data={
                    "action": "execute", "status": "completed", "intent_type": self.intent_type,
                    "user_id": validation_result.get("user_id")
                },
                tenant_id=context.tenant_id
            )
            
            return {
                "artifacts": validation_response,
                "events": [
                    {
                        "type": "token_validated",
                        "user_id": validation_result.get("user_id")
                    }
                ]
            }
            
        except Exception as e:
            await self.record_telemetry(
                telemetry_data={"action": "execute", "status": "failed", "error": str(e)},
                tenant_id=context.tenant_id
            )
            raise
    
    async def _validate_token(self, token: str) -> Dict[str, Any]:
        """Validate token using Security Guard SDK."""
        if self.public_works:
            try:
                security_guard_sdk = getattr(self.public_works, 'security_guard_sdk', None)
                if security_guard_sdk:
                    result = await security_guard_sdk.validate_token(token)
                    if result:
                        return {
                            "valid": True,
                            "user_id": result.user_id,
                            "email": result.email,
                            "tenant_id": result.tenant_id,
                            "roles": result.roles,
                            "permissions": result.permissions
                        }
                
                # Fallback to auth_abstraction
                auth_abstraction = self.public_works.get_auth_abstraction()
                if auth_abstraction:
                    result = await auth_abstraction.validate_token(token)
                    if result and result.get("success"):
                        return {
                            "valid": True,
                            "user_id": result.get("user_id"),
                            "email": result.get("email"),
                            "tenant_id": result.get("tenant_id"),
                            "roles": result.get("roles", []),
                            "permissions": result.get("permissions", [])
                        }
            except Exception as e:
                self.logger.warning(f"Token validation failed: {e}")
        
        return {"valid": False, "reason": "Token validation failed"}
