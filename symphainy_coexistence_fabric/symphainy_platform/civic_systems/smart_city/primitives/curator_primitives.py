"""
Curator Primitives - Policy Decisions for Registry Access

Primitives for Curator policy decisions (used by Runtime only).

⚠️ CRITICAL: Runtime consumes snapshotted registry state (read-only).
Runtime never calls Curator SDK methods.
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
class CapabilityRegistrationValidation:
    """Capability registration validation result."""
    is_valid: bool
    capability_id: str
    reason: Optional[str] = None


@dataclass
class RegistryAccessCheck:
    """Registry access check result."""
    is_allowed: bool
    registry_type: str
    reason: Optional[str] = None


@dataclass
class PromotionValidation:
    """Promotion validation result."""
    is_allowed: bool
    registry_type: str
    reason: Optional[str] = None
    policy_basis: Optional[str] = None


class CuratorPrimitives:
    """
    Curator Primitives - Policy Decisions
    
    Makes policy decisions for registry access.
    
    ⚠️ CRITICAL: Runtime consumes snapshotted registry state (read-only).
    """
    
    def __init__(self, policy_store: Optional[Any] = None):
        self.policy_store = policy_store
        self.logger = get_logger(self.__class__.__name__)
    
    async def validate_capability_registration(
        self,
        capability_definition: Dict[str, Any],
        tenant_id: str
    ) -> CapabilityRegistrationValidation:
        """Validate capability registration (policy decision)."""
        # MVP: Basic validation
        if not capability_definition:
            return CapabilityRegistrationValidation(
                is_valid=False,
                capability_id="",
                reason="Capability definition is required"
            )
        
        capability_id = capability_definition.get("capability_id", "")
        if not capability_id:
            return CapabilityRegistrationValidation(
                is_valid=False,
                capability_id=capability_id,
                reason="Capability ID is required"
            )
        
        return CapabilityRegistrationValidation(
            is_valid=True,
            capability_id=capability_id
        )
    
    async def check_registry_access(
        self,
        registry_type: str,
        user_id: str,
        tenant_id: str
    ) -> RegistryAccessCheck:
        """Check registry access (policy decision)."""
        # MVP: Basic validation
        if not registry_type:
            return RegistryAccessCheck(
                is_allowed=False,
                registry_type=registry_type,
                reason="Registry type is required"
            )
        
        return RegistryAccessCheck(
            is_allowed=True,
            registry_type=registry_type
        )
    
    async def validate_promotion(
        self,
        artifact_type: str,
        registry_type: str,
        tenant_id: Optional[str] = None,
        lifecycle_state: Optional[str] = None
    ) -> PromotionValidation:
        """
        Validate promotion of Purpose-Bound Outcome to Platform DNA (policy decision).
        
        This makes policy decisions about whether an artifact can be promoted:
        - Checks if artifact type is allowed for the registry type
        - Checks if lifecycle state allows promotion
        - Checks promotion policy (MVP: permissive, production: actual policy)
        
        Args:
            artifact_type: Type of artifact to promote (e.g., "blueprint", "workflow")
            registry_type: Type of registry ("solution", "intent", "realm")
            tenant_id: Optional tenant ID for tenant-scoped policies
            lifecycle_state: Optional lifecycle state of artifact
        
        Returns:
            PromotionValidation with policy decision
        """
        # Validate registry_type
        valid_registry_types = ["solution", "intent", "realm"]
        if registry_type not in valid_registry_types:
            return PromotionValidation(
                is_allowed=False,
                registry_type=registry_type,
                reason=f"Invalid registry_type: {registry_type}. Must be one of: {valid_registry_types}",
                policy_basis="invalid_registry_type"
            )
        
        # Check lifecycle state (policy: only accepted artifacts can be promoted)
        if lifecycle_state and lifecycle_state != "accepted":
            return PromotionValidation(
                is_allowed=False,
                registry_type=registry_type,
                reason=f"Artifact must be in 'accepted' state for promotion, current state: {lifecycle_state}",
                policy_basis="lifecycle_state_policy"
            )
        
        # Check artifact type matches registry type (policy: type compatibility)
        type_mapping = {
            "solution": ["solution", "blueprint"],
            "intent": ["intent", "workflow"],
            "realm": ["realm", "journey"]
        }
        
        allowed_types = type_mapping.get(registry_type, [])
        if artifact_type not in allowed_types:
            return PromotionValidation(
                is_allowed=False,
                registry_type=registry_type,
                reason=f"Artifact type '{artifact_type}' cannot be promoted to {registry_type} registry. Allowed types: {allowed_types}",
                policy_basis="artifact_type_policy"
            )
        
        # MVP: Permissive policy (capability by design, implementation by policy)
        # Production: Add actual policy store lookup, tenant-scoped policies, etc.
        return PromotionValidation(
            is_allowed=True,
            registry_type=registry_type,
            reason="Promotion allowed by policy (MVP: permissive)",
            policy_basis="mvp_permissive_policy"
        )