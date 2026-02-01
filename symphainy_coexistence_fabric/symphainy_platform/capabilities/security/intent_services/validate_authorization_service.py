"""
Validate Authorization Service (Platform SDK)

Checks if a user has permission for a specific action.

Uses ctx.platform for authorization checks.

Contract: docs/intent_contracts/journey_security_authorization/intent_validate_authorization.md
"""

from typing import Dict, Any
from datetime import datetime

from utilities import get_logger

from symphainy_platform.civic_systems.platform_sdk import (
    PlatformIntentService,
    PlatformContext
)


class ValidateAuthorizationService(PlatformIntentService):
    """
    Validate Authorization Service using Platform SDK.
    
    Handles the `validate_authorization` intent:
    - Checks user permissions
    - Returns authorization result
    """
    
    intent_type = "validate_authorization"
    
    def __init__(self, service_id: str = "validate_authorization_service"):
        """Initialize Validate Authorization Service."""
        super().__init__(service_id=service_id, intent_type="validate_authorization")
        self.logger = get_logger(self.__class__.__name__)
    
    async def execute(self, ctx: PlatformContext) -> Dict[str, Any]:
        """
        Execute validate_authorization intent.
        
        Args:
            ctx: Platform context with intent and platform services
        
        Returns:
            Dict with authorization result
        """
        self.logger.info(f"Executing validate_authorization: {ctx.execution_id}")
        
        user_id = ctx.intent.parameters.get("user_id")
        resource = ctx.intent.parameters.get("resource")
        action = ctx.intent.parameters.get("action")
        tenant_id = ctx.intent.parameters.get("tenant_id") or ctx.tenant_id
        
        if not resource or not action:
            raise ValueError("resource and action are required for authorization check")
        
        # Check authorization
        auth_result = await self._check_authorization(
            ctx=ctx,
            user_id=user_id,
            resource=resource,
            action=action,
            tenant_id=tenant_id
        )
        
        auth_response = {
            "authorized": auth_result.get("authorized", False),
            "user_id": user_id,
            "resource": resource,
            "action": action,
            "tenant_id": tenant_id,
            "reason": auth_result.get("reason"),
            "checked_at": datetime.utcnow().isoformat()
        }
        
        if auth_result.get("authorized"):
            self.logger.info(f"✅ Authorization granted: {user_id} -> {action} on {resource}")
        else:
            self.logger.info(f"❌ Authorization denied: {user_id} -> {action} on {resource}")
        
        return {
            "artifacts": auth_response,
            "events": [{
                "type": "authorization_checked",
                "authorized": auth_result.get("authorized", False),
                "user_id": user_id,
                "resource": resource,
                "action": action
            }]
        }
    
    async def _check_authorization(
        self,
        ctx: PlatformContext,
        user_id: str,
        resource: str,
        action: str,
        tenant_id: str
    ) -> Dict[str, Any]:
        """Check authorization using ctx.governance.auth (Security Guard SDK). No _public_works."""
        if not ctx.governance or not ctx.governance.auth:
            raise RuntimeError(
                "Security Guard SDK not available; cannot check authorization. "
                "Ensure Public Works provides get_auth_abstraction() and GovernanceService is built."
            )
        result = await ctx.governance.auth.check_permission(
            user_id=user_id,
            resource=resource,
            action=action,
            tenant_id=tenant_id
        )
        if not result:
            return {"authorized": False, "reason": "Authorization check returned no result"}
        return {
            "authorized": result.get("authorized", False),
            "reason": result.get("reason")
        }
