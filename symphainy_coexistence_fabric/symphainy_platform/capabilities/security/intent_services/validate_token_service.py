"""
Validate Token Service (Platform SDK)

Validates an authentication token and returns user context.

Uses ctx.platform for auth operations via Security Guard SDK.

Contract: docs/intent_contracts/journey_security_authentication/intent_refresh_session.md
"""

from typing import Dict, Any
from datetime import datetime

from utilities import get_logger

from symphainy_platform.civic_systems.platform_sdk import (
    PlatformIntentService,
    PlatformContext
)


class ValidateTokenService(PlatformIntentService):
    """
    Validate Token Service using Platform SDK.
    
    Handles the `validate_token` intent:
    - Validates authentication token
    - Returns user context if valid
    """
    
    intent_type = "validate_token"
    
    def __init__(self, service_id: str = "validate_token_service"):
        """Initialize Validate Token Service."""
        super().__init__(service_id=service_id, intent_type="validate_token")
        self.logger = get_logger(self.__class__.__name__)
    
    async def execute(self, ctx: PlatformContext) -> Dict[str, Any]:
        """
        Execute validate_token intent.
        
        Args:
            ctx: Platform context with intent and platform services
        
        Returns:
            Dict with token validation result
        """
        self.logger.info(f"Executing validate_token: {ctx.execution_id}")
        
        token = ctx.intent.parameters.get("token")
        
        if not token:
            raise ValueError("token is required for validation")
        
        # Validate token via Security Guard SDK
        validation_result = await self._validate_token(ctx, token)
        
        if not validation_result.get("valid"):
            return {
                "artifacts": {
                    "valid": False,
                    "reason": validation_result.get("reason", "Invalid token")
                },
                "events": [{
                    "type": "token_validation_failed",
                    "reason": validation_result.get("reason")
                }]
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
        
        self.logger.info(f"✅ Token validated for user: {validation_result.get('user_id')}")
        
        return {
            "artifacts": validation_response,
            "events": [{
                "type": "token_validated",
                "user_id": validation_result.get("user_id")
            }]
        }
    
    async def _validate_token(self, ctx: PlatformContext, token: str) -> Dict[str, Any]:
        """Validate token using Security Guard SDK via ctx.platform."""
        if ctx.platform and ctx.platform._public_works:
            try:
                security_guard_sdk = getattr(ctx.platform._public_works, 'security_guard_sdk', None)
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
                auth_abstraction = ctx.platform._public_works.get_auth_abstraction()
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
