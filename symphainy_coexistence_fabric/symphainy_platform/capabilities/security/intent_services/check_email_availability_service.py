"""
Check Email Availability Service (Platform SDK)

Checks if an email address is available for registration.

Uses ctx.platform for auth operations.

Contract: docs/intent_contracts/journey_security_registration/intent_check_email_availability.md
"""

from typing import Dict, Any
from datetime import datetime

from utilities import get_logger

from symphainy_platform.civic_systems.platform_sdk import (
    PlatformIntentService,
    PlatformContext
)


class CheckEmailAvailabilityService(PlatformIntentService):
    """
    Check Email Availability Service using Platform SDK.
    
    Handles the `check_email_availability` intent:
    - Checks if email is already registered
    - Returns availability status
    """
    
    def __init__(self, service_id: str = "check_email_availability_service"):
        """Initialize Check Email Availability Service."""
        super().__init__(service_id=service_id)
        self.logger = get_logger(self.__class__.__name__)
    
    async def execute(self, ctx: PlatformContext) -> Dict[str, Any]:
        """
        Execute check_email_availability intent.
        
        Args:
            ctx: Platform context with intent and platform services
        
        Returns:
            Dict with email availability result
        """
        self.logger.info(f"Executing check_email_availability: {ctx.execution_id}")
        
        email = ctx.intent.parameters.get("email")
        
        if not email:
            raise ValueError("email is required for availability check")
        
        # Check email availability
        availability_result = await self._check_email_availability(ctx, email)
        
        availability_response = {
            "email": email,
            "available": availability_result.get("available", False),
            "reason": availability_result.get("reason"),
            "checked_at": datetime.utcnow().isoformat()
        }
        
        if availability_result.get("available"):
            self.logger.info(f"✅ Email available: {email}")
        else:
            self.logger.info(f"❌ Email not available: {email}")
        
        return {
            "artifacts": availability_response,
            "events": [{
                "type": "email_availability_checked",
                "email": email,
                "available": availability_result.get("available", False)
            }]
        }
    
    async def _check_email_availability(self, ctx: PlatformContext, email: str) -> Dict[str, Any]:
        """Check email availability using Security Guard SDK."""
        if ctx.platform and ctx.platform._public_works:
            try:
                security_guard_sdk = getattr(ctx.platform._public_works, 'security_guard_sdk', None)
                if security_guard_sdk:
                    result = await security_guard_sdk.check_email_availability(email)
                    if result is not None:
                        return {
                            "available": result.get("available", False),
                            "reason": result.get("reason")
                        }
                
                # Fallback to auth_abstraction
                auth_abstraction = ctx.platform._public_works.get_auth_abstraction()
                if auth_abstraction:
                    result = await auth_abstraction.check_email_availability(email)
                    if result is not None:
                        return {
                            "available": result.get("available", False),
                            "reason": result.get("reason")
                        }
            except Exception as e:
                self.logger.warning(f"Email availability check failed: {e}")
        
        # Default to available if service is unavailable (let registration handle it)
        return {"available": True, "reason": "Could not verify - proceeding optimistically"}
