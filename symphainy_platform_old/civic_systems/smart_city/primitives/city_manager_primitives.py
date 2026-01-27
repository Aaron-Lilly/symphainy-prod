"""
City Manager Primitives - Policy Decisions for Platform Lifecycle

Primitives for City Manager policy decisions (used by Runtime only).

WHAT (Smart City Role): I make policy decisions for platform lifecycle
HOW (Primitive Implementation): I evaluate policies and return decisions

⚠️ CRITICAL: Used by Runtime only, not by SDKs or Realms.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional
from dataclasses import dataclass

from utilities import get_logger


@dataclass
class RealmActivationValidation:
    """Realm activation validation result."""
    is_valid: bool
    realm_name: str
    reason: Optional[str] = None
    constraints: Dict[str, Any] = None


@dataclass
class LifecycleStateCheck:
    """Lifecycle state check result."""
    current_state: str
    can_transition: bool
    target_state: Optional[str] = None
    reason: Optional[str] = None


class CityManagerPrimitives:
    """
    City Manager Primitives - Policy Decisions
    
    Makes policy decisions for platform lifecycle and realm activation.
    Used by Runtime only.
    """
    
    def __init__(
        self,
        policy_store: Optional[Any] = None  # Policy store (from Public Works)
    ):
        """
        Initialize City Manager primitives.
        
        Args:
            policy_store: Optional policy store (for policy evaluation)
        """
        self.policy_store = policy_store
        self.logger = get_logger(self.__class__.__name__)
    
    async def validate_realm_activation(
        self,
        realm_name: str,
        solution_id: str,
        tenant_id: str,
        activation_params: Dict[str, Any]
    ) -> RealmActivationValidation:
        """
        Validate realm activation (policy decision).
        
        Args:
            realm_name: Realm name
            solution_id: Solution identifier
            tenant_id: Tenant identifier
            activation_params: Activation parameters
        
        Returns:
            Validation result
        """
        # For MVP: Basic validation
        # In full implementation: Evaluate policies from policy store
        
        if not realm_name:
            return RealmActivationValidation(
                is_valid=False,
                realm_name=realm_name,
                reason="Realm name is required"
            )
        
        if not solution_id:
            return RealmActivationValidation(
                is_valid=False,
                realm_name=realm_name,
                reason="Solution ID is required"
            )
        
        # MVP: Allow activation (full implementation would check policies)
        return RealmActivationValidation(
            is_valid=True,
            realm_name=realm_name,
            constraints={}
        )
    
    async def check_lifecycle_state(
        self,
        tenant_id: str,
        current_state: str,
        target_state: str
    ) -> LifecycleStateCheck:
        """
        Check if lifecycle state transition is allowed (policy decision).
        
        Args:
            tenant_id: Tenant identifier
            current_state: Current lifecycle state
            target_state: Target lifecycle state
        
        Returns:
            State check result
        """
        # For MVP: Basic state transition validation
        # In full implementation: Evaluate policies from policy store
        
        # Define valid state transitions
        valid_transitions = {
            "infra_wait": ["utilities_ready"],
            "utilities_ready": ["foundations_ready"],
            "foundations_ready": ["city_ready"],
            "city_ready": ["platform_idle"],
            "platform_idle": ["realm_active"],
            "realm_active": ["platform_idle", "realm_active"]
        }
        
        allowed_targets = valid_transitions.get(current_state, [])
        can_transition = target_state in allowed_targets
        
        return LifecycleStateCheck(
            current_state=current_state,
            can_transition=can_transition,
            target_state=target_state if can_transition else None,
            reason=None if can_transition else f"Invalid transition from {current_state} to {target_state}"
        )
