"""
Authenticate User Service (Platform SDK)

Authenticates user credentials and returns authentication result.

Uses ctx.platform for auth operations via Security Guard SDK.

Contract: docs/intent_contracts/journey_security_authentication/intent_authenticate_user.md
"""

from typing import Dict, Any
from datetime import datetime

from utilities import get_logger

from symphainy_platform.civic_systems.platform_sdk import (
    PlatformIntentService,
    PlatformContext
)


class AuthenticateUserService(PlatformIntentService):
    """
    Authenticate User Service using Platform SDK.
    
    Handles the `authenticate_user` intent:
    - Validates email and password
    - Authenticates via Security Guard SDK
    - Returns access/refresh tokens and user info
    """
    
    intent_type = "authenticate_user"
    
    def __init__(self, service_id: str = "authenticate_user_service"):
        """Initialize Authenticate User Service."""
        super().__init__(service_id=service_id, intent_type="authenticate_user")
        self.logger = get_logger(self.__class__.__name__)
    
    async def execute(self, ctx: PlatformContext) -> Dict[str, Any]:
        """
        Execute authenticate_user intent.
        
        Args:
            ctx: Platform context with intent and platform services
        
        Returns:
            Dict with authentication result artifacts and events
        """
        self.logger.info(f"Executing authenticate_user: {ctx.execution_id}")
        
        email = ctx.intent.parameters.get("email")
        password = ctx.intent.parameters.get("password")
        
        if not email or not password:
            raise ValueError("email and password are required for authentication")
        
        # Authenticate via Security Guard SDK
        auth_result = await self._authenticate(ctx, email, password)
        
        if not auth_result.get("success"):
            self.logger.warning(f"Authentication failed for {email}")
            return {
                "artifacts": {
                    "authenticated": False,
                    "error": auth_result.get("error", "Authentication failed")
                },
                "events": [{
                    "type": "authentication_failed",
                    "email": email,
                    "reason": auth_result.get("error", "Invalid credentials")
                }]
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
        
        self.logger.info(f"✅ User authenticated: {email}")
        
        return {
            "artifacts": auth_response,
            "events": [{
                "type": "user_authenticated",
                "user_id": auth_result.get("user_id"),
                "tenant_id": auth_result.get("tenant_id")
            }]
        }
    
    async def _authenticate(self, ctx: PlatformContext, email: str, password: str) -> Dict[str, Any]:
        """Authenticate using Security Guard SDK via ctx.governance.auth (no _public_works)."""
        if not ctx.governance or not ctx.governance.auth:
            raise RuntimeError(
                "Security Guard SDK not available; cannot authenticate. "
                "Ensure Public Works provides get_auth_abstraction() and GovernanceService is built."
            )
        result = await ctx.governance.auth.authenticate({
            "email": email,
            "password": password
        })
        if not result:
            return {"success": False, "error": "Authentication failed"}
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
