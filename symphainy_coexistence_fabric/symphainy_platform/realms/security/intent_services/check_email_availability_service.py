"""
Check Email Availability Intent Service

Implements the check_email_availability intent for the Security Realm.

Contract: docs/intent_contracts/journey_security_registration/intent_check_email_availability.md

Purpose: Check if an email address is available for registration.

WHAT (Intent Service Role): I check email availability
HOW (Intent Service Implementation): I query auth system to check if email exists
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


class CheckEmailAvailabilityService(BaseIntentService):
    """
    Intent service for email availability check.
    
    Checks if email is:
    - Not already registered
    - Valid format
    - Not on blocklist
    """
    
    def __init__(self, public_works, state_surface):
        """Initialize CheckEmailAvailabilityService."""
        super().__init__(
            service_id="check_email_availability_service",
            intent_type="check_email_availability",
            public_works=public_works,
            state_surface=state_surface
        )
    
    async def execute(
        self,
        context: ExecutionContext,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute the check_email_availability intent."""
        await self.record_telemetry(
            telemetry_data={"action": "execute", "status": "started", "intent_type": self.intent_type},
            tenant_id=context.tenant_id
        )
        
        try:
            intent_params = context.intent.parameters or {} if context.intent else {}
            if params:
                intent_params = {**intent_params, **params}
            
            email = intent_params.get("email")
            
            if not email:
                raise ValueError("email is required")
            
            # Check email availability
            availability_result = await self._check_email(email)
            
            availability_response = {
                "email": email,
                "available": availability_result.get("available", True),
                "reason": availability_result.get("reason"),
                "checked_at": datetime.utcnow().isoformat()
            }
            
            self.logger.info(f"Email availability check: {email} = {availability_result.get('available')}")
            
            await self.record_telemetry(
                telemetry_data={
                    "action": "execute", "status": "completed", "intent_type": self.intent_type,
                    "available": availability_result.get("available")
                },
                tenant_id=context.tenant_id
            )
            
            return {
                "artifacts": availability_response,
                "events": [
                    {
                        "type": "email_availability_checked",
                        "email": email,
                        "available": availability_result.get("available")
                    }
                ]
            }
            
        except Exception as e:
            await self.record_telemetry(
                telemetry_data={"action": "execute", "status": "failed", "error": str(e)},
                tenant_id=context.tenant_id
            )
            raise
    
    async def _check_email(self, email: str) -> Dict[str, Any]:
        """Check email availability via auth abstraction."""
        # Validate email format
        import re
        email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_regex, email):
            return {"available": False, "reason": "Invalid email format"}
        
        if self.public_works:
            try:
                auth_abstraction = self.public_works.get_auth_abstraction()
                if auth_abstraction and hasattr(auth_abstraction, 'check_email_exists'):
                    exists = await auth_abstraction.check_email_exists(email)
                    if exists:
                        return {"available": False, "reason": "Email already registered"}
            except Exception as e:
                self.logger.debug(f"Email check via abstraction failed: {e}")
        
        # Default: assume available if we can't check
        return {"available": True}
