"""
City Manager SDK - Platform Lifecycle and Realm Activation Coordination

SDK for City Manager coordination (used by Solution, Realms).

WHAT (Smart City Role): I coordinate platform lifecycle and realm activation
HOW (SDK Implementation): I prepare lifecycle contracts for Runtime validation

⚠️ CRITICAL: NO Runtime dependency.
SDKs prepare execution contracts. Runtime validates and executes them.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

from utilities import get_logger, get_clock


class PlatformLifecycleState(str, Enum):
    """Platform lifecycle states."""
    INFRA_WAIT = "infra_wait"
    UTILITIES_READY = "utilities_ready"
    FOUNDATIONS_READY = "foundations_ready"
    CITY_READY = "city_ready"
    PLATFORM_IDLE = "platform_idle"
    REALM_ACTIVE = "realm_active"


@dataclass
class RealmActivationRequest:
    """Realm activation request with execution contract."""
    realm_name: str
    solution_id: str
    tenant_id: str
    activation_params: Dict[str, Any]
    execution_contract: Dict[str, Any]  # Prepared for Runtime validation


@dataclass
class PlatformState:
    """Platform state information."""
    lifecycle_state: PlatformLifecycleState
    active_realms: List[str]
    solution_id: Optional[str]
    metadata: Dict[str, Any]


class CityManagerSDK:
    """
    City Manager SDK - Coordination Logic
    
    Coordinates platform lifecycle and realm activation.
    Prepares execution contracts for Runtime validation.
    
    ⚠️ NO Runtime dependency - SDKs prepare, Runtime executes.
    """
    
    def __init__(
        self,
        config_abstraction: Optional[Any] = None,  # Config abstraction (optional for MVP)
        policy_resolver: Optional[Any] = None  # Policy library (optional for MVP)
    ):
        """
        Initialize City Manager SDK.
        
        Args:
            config_abstraction: Optional config abstraction (from Public Works)
            policy_resolver: Optional policy resolver (for policy preparation)
        """
        self.config_abstraction = config_abstraction
        self.policy_resolver = policy_resolver
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
    
    async def bootstrap_platform(
        self,
        tenant_id: str,
        solution_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Bootstrap platform (prepare bootstrap contract).
        
        Args:
            tenant_id: Tenant identifier
            solution_id: Optional solution identifier
        
        Returns:
            Dict with bootstrap contract and metadata
        """
        # Prepare bootstrap execution contract
        execution_contract = {
            "action": "bootstrap_platform",
            "tenant_id": tenant_id,
            "solution_id": solution_id,
            "timestamp": self.clock.now_iso()
        }
        
        # Get policies (if available)
        if self.policy_resolver:
            policies = await self.policy_resolver.get_policies(tenant_id)
            execution_contract["policies"] = policies
        
        self.logger.info(f"Platform bootstrap contract prepared for tenant: {tenant_id}")
        
        return {
            "execution_contract": execution_contract,
            "metadata": {
                "tenant_id": tenant_id,
                "solution_id": solution_id,
                "prepared_at": self.clock.now_iso()
            }
        }
    
    async def activate_realm(
        self,
        realm_name: str,
        solution_id: str,
        tenant_id: str,
        activation_params: Optional[Dict[str, Any]] = None
    ) -> RealmActivationRequest:
        """
        Activate realm (prepare activation contract).
        
        Args:
            realm_name: Realm name (e.g., "content", "insights")
            solution_id: Solution identifier
            tenant_id: Tenant identifier
            activation_params: Optional activation parameters
        
        Returns:
            Realm activation request with execution contract
        """
        # Prepare activation execution contract
        execution_contract = {
            "action": "activate_realm",
            "realm_name": realm_name,
            "solution_id": solution_id,
            "tenant_id": tenant_id,
            "activation_params": activation_params or {},
            "timestamp": self.clock.now_iso()
        }
        
        # Get policies (if available)
        if self.policy_resolver:
            policies = await self.policy_resolver.get_policies(tenant_id)
            execution_contract["policies"] = policies
        
        self.logger.info(f"Realm activation contract prepared: {realm_name} for solution: {solution_id}")
        
        return RealmActivationRequest(
            realm_name=realm_name,
            solution_id=solution_id,
            tenant_id=tenant_id,
            activation_params=activation_params or {},
            execution_contract=execution_contract
        )
    
    async def get_platform_state(
        self,
        tenant_id: str,
        solution_id: Optional[str] = None
    ) -> PlatformState:
        """
        Get platform state (coordination only, not authoritative).
        
        Args:
            tenant_id: Tenant identifier
            solution_id: Optional solution identifier
        
        Returns:
            Platform state information
        """
        # For MVP: Return lightweight state
        # In full implementation: Query state from appropriate source
        
        return PlatformState(
            lifecycle_state=PlatformLifecycleState.PLATFORM_IDLE,
            active_realms=[],
            solution_id=solution_id,
            metadata={
                "tenant_id": tenant_id,
                "queried_at": self.clock.now_iso()
            }
        )
