"""
Curator SDK - Capability, Agent, and Domain Registry Coordination

SDK for Curator coordination (used by Solution & Smart City).
Implements CuratorProtocol; delegates to CuratorFoundationService (in-memory) and/or CuratorService (promotion).

Sovereignty model: Runtime and agents call Curator for classification and approval;
ctx.governance.registry is the protocol boundary.
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from utilities import get_logger, get_clock


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
    Curator SDK - Implements CuratorProtocol.
    
    Delegates to curator_foundation (CuratorFoundationService) for register_capability,
    discover_agents, get_domain_registry; to curator_service (CuratorService) for promote_to_platform_dna.
    Sovereignty methods (classify_artifact, approve_*) are stubs (allow-all) until next layer.
    """
    
    def __init__(
        self,
        registry_abstraction: Optional[Any] = None,
        policy_resolver: Optional[Any] = None,
        curator_foundation: Optional[Any] = None,
        curator_service: Optional[Any] = None
    ):
        self.registry_abstraction = registry_abstraction
        self.policy_resolver = policy_resolver
        self._curator_foundation = curator_foundation
        self.curator_service = curator_service
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
    
    async def register_capability(
        self,
        capability_definition: Dict[str, Any],
        tenant_id: str
    ) -> CapabilityRegistration:
        """Register capability. REAL when curator_foundation wired (in-memory); else returns synthetic result."""
        execution_contract = {
            "action": "register_capability",
            "capability_definition": capability_definition,
            "tenant_id": tenant_id,
            "timestamp": self.clock.now_iso()
        }
        capability_id = capability_definition.get("capability_name") or f"capability_{self.clock.now_iso()}"
        
        if self._curator_foundation:
            try:
                from symphainy_platform.foundations.curator.models.capability_definition import CapabilityDefinition
                cap = CapabilityDefinition(
                    capability_name=capability_definition.get("capability_name", "unknown"),
                    service_name=capability_definition.get("service_name", "unknown"),
                    protocol_name=capability_definition.get("protocol_name", "UnknownProtocol"),
                    description=capability_definition.get("description", ""),
                    realm=capability_definition.get("realm", "default"),
                    contracts=capability_definition.get("contracts") or {"mcp_tool": {"tool_name": capability_definition.get("capability_name", "stub")}},
                    semantic_mapping=capability_definition.get("semantic_mapping"),
                    inputs=capability_definition.get("inputs"),
                    outputs=capability_definition.get("outputs"),
                    determinism=capability_definition.get("determinism"),
                    version=capability_definition.get("version", "1.0.0"),
                )
                ok = await self._curator_foundation.register_capability(cap)
                if ok:
                    capability_id = cap.capability_name
            except Exception as e:
                self.logger.debug(f"Curator foundation register_capability failed: {e}")
        
        return CapabilityRegistration(
            capability_id=capability_id,
            capability_definition=capability_definition,
            execution_contract=execution_contract
        )
    
    async def discover_agents(
        self,
        agent_type: Optional[str] = None,
        tenant_id: str = None
    ) -> AgentDiscovery:
        """Discover agents; delegates to CuratorFoundationService.list_agents when wired."""
        execution_contract = {
            "action": "discover_agents",
            "agent_type": agent_type,
            "tenant_id": tenant_id,
            "timestamp": self.clock.now_iso()
        }
        agents: List[Dict[str, Any]] = []
        if self._curator_foundation:
            try:
                agents = await self._curator_foundation.list_agents(realm=tenant_id, capability=agent_type)
            except Exception as e:
                self.logger.debug(f"Curator foundation list_agents failed: {e}")
        
        return AgentDiscovery(agents=agents, execution_contract=execution_contract)
    
    async def get_domain_registry(
        self,
        domain_name: Optional[str] = None,
        tenant_id: str = None
    ) -> Dict[str, Any]:
        """Get domain registry. Stub: no domain registry table yet; returns empty domains + contract."""
        execution_contract = {
            "action": "get_domain_registry",
            "domain_name": domain_name,
            "tenant_id": tenant_id,
            "timestamp": self.clock.now_iso()
        }
        return {"domains": [], "execution_contract": execution_contract}
    
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
        """Promote Purpose-Bound Outcome to Platform DNA. REAL when curator_service wired (Public Works builds it after initialize()); else no-op."""
        if not self.curator_service:
            self.logger.warning("Curator service not wired; promote_to_platform_dna is no-op.")
            return None
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
    
    # Sovereignty surface — STUBS until real policy is added (see CURATOR_REAL_VS_STUB_EXPLAINED.md)
    async def classify_artifact(self, artifact: Dict[str, Any]) -> Dict[str, Any]:
        """Classify artifact for sovereignty. STUB: always allow-all; replace with policy store when ready."""
        return {"sovereignty_domain": "default", "learning_permission": "allow"}
    
    async def approve_promotion(self, artifact: Dict[str, Any], target_domain: str) -> bool:
        """Approve promotion to target domain. STUB: always allow; replace with policy when ready."""
        return True
    
    async def approve_cross_domain(self, source: str, target: str, operation: str) -> bool:
        """Approve cross-domain operation. STUB: always allow; replace with policy when ready."""
        return True
    
    async def approve_message_routing(self, message: Dict[str, Any]) -> bool:
        """Approve message routing. STUB: always allow; replace with policy when ready."""
        return True