"""
Curator Protocol - Intelligence Governance and Registry Contract

Defines the contract for Curator (capability/agent/domain registry and sovereignty).
ctx.governance.registry implements this protocol.

WHAT (Boundary Role): I define how Curator registry and sovereignty surface behave
HOW (Implementation): CuratorSDK and CuratorService implement this protocol

Related: CURATOR_LAYER_CLEANUP_AND_TARGET_PATTERN.md, SOVEREIGNTY_ARCHITECTURE.md
"""

from typing import Protocol, Dict, Any, Optional, List, runtime_checkable


@runtime_checkable
class CuratorProtocol(Protocol):
    """
    Protocol for Curator (intelligence governance + registry surface).
    
    Registry surface: register_capability, discover_agents, get_domain_registry, promote_to_platform_dna.
    Sovereignty surface (next layer): classify_artifact, approve_promotion, approve_cross_domain, approve_message_routing.
    """

    async def register_capability(
        self,
        capability_definition: Dict[str, Any],
        tenant_id: str
    ) -> Any:
        """Register a capability. Returns CapabilityRegistration."""
        ...

    async def discover_agents(
        self,
        agent_type: Optional[str] = None,
        tenant_id: Optional[str] = None
    ) -> Any:
        """Discover agents. Returns AgentDiscovery."""
        ...

    async def get_domain_registry(
        self,
        domain_name: Optional[str] = None,
        tenant_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get domain registry. Returns dict with domains and execution_contract."""
        ...

    async def promote_to_platform_dna(
        self,
        artifact_id: str,
        tenant_id: str,
        registry_type: str,
        registry_name: str,
        registry_id: Optional[str] = None,
        promoted_by: str = "curator",
        description: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Optional[str]:
        """Promote Purpose-Bound Outcome to Platform DNA. Returns registry ID or None."""
        ...

    # Sovereignty surface (next layer; stub / allow-all for this layer)
    async def classify_artifact(self, artifact: Dict[str, Any]) -> Dict[str, Any]:
        """Classify artifact for sovereignty (sovereignty_domain, learning_permission). Stub: return allow-all."""
        ...

    async def approve_promotion(
        self,
        artifact: Dict[str, Any],
        target_domain: str
    ) -> bool:
        """Approve promotion to target domain. Stub: return True."""
        ...

    async def approve_cross_domain(
        self,
        source: str,
        target: str,
        operation: str
    ) -> bool:
        """Approve cross-domain operation. Stub: return True."""
        ...

    async def approve_message_routing(self, message: Dict[str, Any]) -> bool:
        """Approve message routing. Stub: return True."""
        ...
