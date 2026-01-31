"""
Curator SDK - Capability, Agent, and Domain Registry Coordination

SDK for Curator coordination (used by Solution & Smart City).

⚠️ CRITICAL CONSTRAINT:
- Curator SDK → Used by Solution & Smart City (registration, discovery)
- Curator Data → Visible to Runtime (read-only, snapshotted registry state)
- Runtime → Never calls Curator SDK methods, only consumes snapshotted registry state
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from utilities import get_logger, get_clock
from symphainy_platform.civic_systems.smart_city.services.curator_service import CuratorService


@dataclass
class CapabilityRegistration:
    """Capability registration with execution contract."""
    capability_id: str
    capability_definition: Dict[str, Any]
    execution_contract: Dict[str, Any]


@dataclass
class AgentDiscovery:
    """Agent discovery result."""
    agents: List[Dict[str, Any]]
    execution_contract: Dict[str, Any]


class CuratorSDK:
    """
    Curator SDK - Coordination Logic
    
    Coordinates capability, agent, and domain registry.
    
    ⚠️ CRITICAL: Runtime never calls Curator SDK methods.
    Runtime only consumes snapshotted registry state (read-only).
    """
    
    def __init__(
        self,
        registry_abstraction: Optional[Any] = None,
        policy_resolver: Optional[Any] = None
    ):
        self.registry_abstraction = registry_abstraction
        self.policy_resolver = policy_resolver
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
    
    async def register_capability(
        self,
        capability_definition: Dict[str, Any],
        tenant_id: str
    ) -> CapabilityRegistration:
        """Register capability (prepare registration contract)."""
        execution_contract = {
            "action": "register_capability",
            "capability_definition": capability_definition,
            "tenant_id": tenant_id,
            "timestamp": self.clock.now_iso()
        }
        
        return CapabilityRegistration(
            capability_id=f"capability_{self.clock.now_iso()}",
            capability_definition=capability_definition,
            execution_contract=execution_contract
        )
    
    async def discover_agents(
        self,
        agent_type: Optional[str] = None,
        tenant_id: str = None
    ) -> AgentDiscovery:
        """Discover agents (prepare discovery contract)."""
        execution_contract = {
            "action": "discover_agents",
            "agent_type": agent_type,
            "tenant_id": tenant_id,
            "timestamp": self.clock.now_iso()
        }
        
        return AgentDiscovery(
            agents=[],
            execution_contract=execution_contract
        )
    
    async def get_domain_registry(
        self,
        domain_name: Optional[str] = None,
        tenant_id: str = None
    ) -> Dict[str, Any]:
        """Get domain registry (prepare registry contract)."""
        execution_contract = {
            "action": "get_domain_registry",
            "domain_name": domain_name,
            "tenant_id": tenant_id,
            "timestamp": self.clock.now_iso()
        }
        
        return {
            "domains": [],
            "execution_contract": execution_contract
        }
    
    async def promote_to_platform_dna(
        self,
        artifact_id: str,
        tenant_id: str,
        registry_type: str,  # "solution", "intent", "realm"
        registry_name: str,
        registry_id: Optional[str] = None,
        promoted_by: str = "curator",
        description: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Optional[str]:
        """
        Promote Purpose-Bound Outcome to Platform DNA.
        
        This is an explicit workflow that creates a generalized, curated capability
        from a Purpose-Bound Outcome.
        
        Args:
            artifact_id: Artifact ID of Purpose-Bound Outcome to promote
            tenant_id: Tenant ID (for retrieving artifact)
            registry_type: Type of registry ("solution", "intent", "realm")
            registry_name: Human-readable name for the registry entry
            registry_id: Optional registry ID (if None, will be generated)
            promoted_by: Who/what initiated the promotion
            description: Optional description
            tags: Optional tags for discovery
        
        Returns:
            Registry ID (UUID string) or None if promotion failed
        """
        if not self.curator_service:
            raise RuntimeError(
                "Curator service not wired; cannot promote to Platform DNA. Platform contract §8A."
            )
        
        return await self.curator_service.promote_to_platform_dna(
            artifact_id=artifact_id,
            tenant_id=tenant_id,
            registry_type=registry_type,
            registry_name=registry_name,
            registry_id=registry_id,
            promoted_by=promoted_by,
            description=description,
            tags=tags
        )