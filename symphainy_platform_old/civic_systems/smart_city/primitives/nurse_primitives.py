"""
Nurse Primitives - Policy Decisions for Telemetry and Retries

Primitives for Nurse policy decisions (used by Runtime only).
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional
from dataclasses import dataclass

from utilities import get_logger


@dataclass
class RetryPolicyCheck:
    """Retry policy check result."""
    can_retry: bool
    execution_id: str
    retry_count: int
    max_retries: int
    reason: Optional[str] = None


@dataclass
class TelemetryAccessValidation:
    """Telemetry access validation result."""
    is_allowed: bool
    telemetry_type: str
    reason: Optional[str] = None


class NursePrimitives:
    """
    Nurse Primitives - Policy Decisions
    
    Makes policy decisions for telemetry and retries.
    """
    
    def __init__(self, policy_store: Optional[Any] = None):
        self.policy_store = policy_store
        self.logger = get_logger(self.__class__.__name__)
    
    async def check_retry_policy(
        self,
        execution_id: str,
        retry_count: int,
        tenant_id: str,
        error_type: str
    ) -> RetryPolicyCheck:
        """Check retry policy (policy decision)."""
        # MVP: Basic retry policy
        max_retries = 3  # Default max retries
        
        can_retry = retry_count < max_retries
        
        return RetryPolicyCheck(
            can_retry=can_retry,
            execution_id=execution_id,
            retry_count=retry_count,
            max_retries=max_retries,
            reason=None if can_retry else f"Max retries ({max_retries}) exceeded"
        )
    
    async def validate_telemetry_access(
        self,
        telemetry_type: str,
        user_id: str,
        tenant_id: str
    ) -> TelemetryAccessValidation:
        """Validate telemetry access (policy decision)."""
        # MVP: Basic validation
        if not telemetry_type:
            return TelemetryAccessValidation(
                is_allowed=False,
                telemetry_type=telemetry_type,
                reason="Telemetry type is required"
            )
        
        return TelemetryAccessValidation(
            is_allowed=True,
            telemetry_type=telemetry_type
        )
