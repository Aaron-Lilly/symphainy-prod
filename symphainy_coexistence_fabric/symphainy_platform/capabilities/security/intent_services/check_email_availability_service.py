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
    
    intent_type = "check_email_availability"
    
    def __init__(self, service_id: str = "check_email_availability_service"):
        """Initialize Check Email Availability Service."""
        super().__init__(service_id=service_id, intent_type="check_email_availability")
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
        """Check email availability using ctx.governance.auth (protocol-compliant)."""
        # Use ctx.governance.auth - the proper protocol boundary
        if not ctx.governance or not ctx.governance.auth:
            raise RuntimeError("Platform contract §8A: ctx.governance.auth required for email check")
        
        try:
            result = await ctx.governance.auth.check_email_availability(email)
            
            if result is not None:
                if isinstance(result, dict):
                    return {
                        "available": result.get("available", False),
                        "reason": result.get("reason")
                    }
                # Handle object result
                return {
                    "available": getattr(result, "available", False),
                    "reason": getattr(result, "reason", None)
                }
            
            return {"available": False, "reason": "Email check returned no result"}
            
        except Exception as e:
            self.logger.error(f"Email availability check failed: {e}", exc_info=True)
            raise RuntimeError(f"Platform contract §8A: Email check failed - {e}")
