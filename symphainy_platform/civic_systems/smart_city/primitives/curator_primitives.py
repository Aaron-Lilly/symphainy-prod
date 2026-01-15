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
