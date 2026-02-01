"""
Create User Account Service (Platform SDK)

Registers a new user account.

Uses ctx.platform for auth operations via Security Guard SDK.

Contract: docs/intent_contracts/journey_security_registration/intent_create_user_account.md
"""

from typing import Dict, Any
from datetime import datetime

from utilities import get_logger

from symphainy_platform.civic_systems.platform_sdk import (
    PlatformIntentService,
    PlatformContext
)


class CreateUserAccountService(PlatformIntentService):
    """
    Create User Account Service using Platform SDK.
    
    Handles the `create_user_account` intent:
    - Validates registration data
    - Creates user via Security Guard SDK
    - Returns access/refresh tokens and user info
    """
    
    intent_type = "create_user_account"
    
    def __init__(self, service_id: str = "create_user_account_service"):
        """Initialize Create User Account Service."""
        super().__init__(service_id=service_id, intent_type="create_user_account")
        self.logger = get_logger(self.__class__.__name__)
    
    async def execute(self, ctx: PlatformContext) -> Dict[str, Any]:
        """
        Execute create_user_account intent.
        
        Args:
            ctx: Platform context with intent and platform services
        
        Returns:
            Dict with registration result artifacts and events
        """
        self.logger.info(f"Executing create_user_account: {ctx.execution_id}")
        
        name = ctx.intent.parameters.get("name")
        email = ctx.intent.parameters.get("email")
        password = ctx.intent.parameters.get("password")
        
        if not email or not password:
            raise ValueError("email and password are required for registration")
        
        # Register user via Security Guard SDK
        register_result = await self._register_user(ctx, name, email, password)
        
        if not register_result.get("success"):
            self.logger.warning(f"Registration failed for {email}")
            return {
                "artifacts": {
                    "registered": False,
                    "error": register_result.get("error", "Registration failed")
                },
                "events": [{
                    "type": "registration_failed",
                    "email": email,
                    "reason": register_result.get("error", "Registration failed")
                }]
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
        
        self.logger.info(f"✅ User registered: {email}")
        
        return {
            "artifacts": register_response,
            "events": [{
                "type": "user_registered",
                "user_id": register_result.get("user_id"),
                "tenant_id": register_result.get("tenant_id")
            }]
        }
    
    async def _register_user(self, ctx: PlatformContext, name: str, email: str, password: str) -> Dict[str, Any]:
        """Register user using ctx.governance.auth (Security Guard SDK). No _public_works."""
        if not ctx.governance or not ctx.governance.auth:
            raise RuntimeError(
                "Security Guard SDK not available; cannot register user. "
                "Ensure Public Works provides get_auth_abstraction() and GovernanceService is built."
            )
        result = await ctx.governance.auth.register_user({
            "email": email,
            "password": password,
            "user_metadata": {"name": name, "full_name": name}
        })
        if not result:
            return {"success": False, "error": "Registration failed"}
        if hasattr(result, "user_id"):
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
        if isinstance(result, dict) and result.get("success"):
            return result
        return {"success": False, "error": result.get("error", "Registration failed") if isinstance(result, dict) else "Registration failed"}
