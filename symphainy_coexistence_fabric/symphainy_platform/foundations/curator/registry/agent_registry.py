"""
Agent Registry

Manages agent capability registration and discovery.

WHAT (Service Role): I manage agent capability registration and discovery
HOW (Service Implementation): I maintain an agent capability registry
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from utilities import get_logger, get_clock


class AgentRegistry:
    """
    Agent Registry - Central agent capability registration and discovery.
    
    Manages agent capabilities, specializations, and metadata.
    """
    
    def __init__(self):
        """Initialize Agent Registry."""
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
        
        # Agent registry
        # Key: agent_id, Value: Dict with agent_name, characteristics, contracts, etc.
        self.registered_agents: Dict[str, Dict[str, Any]] = {}
        
        # Agent capability index
        # Key: capability_name, Value: List[agent_id]
        self.capability_index: Dict[str, List[str]] = {}
        
        self.logger.info("Agent Registry initialized")
    
    async def register_agent(
        self,
        agent_id: str,
        agent_name: str,
        characteristics: Dict[str, Any],
        contracts: Dict[str, Any]
    ) -> bool:
        """
        Register an agent.
        
        Args:
            agent_id: Unique agent identifier
            agent_name: Human-readable agent name
            characteristics: Agent characteristics (capabilities, specialization, realm, etc.)
            contracts: Agent contracts (agent_api, mcp_tools, etc.)
        
        Returns:
            bool: True if registration successful
        """
        try:
            # Register agent
            self.registered_agents[agent_id] = {
                "agent_id": agent_id,
                "agent_name": agent_name,
                "characteristics": characteristics,
                "contracts": contracts,
                "registered_at": self.clock.now_iso(),
                "status": "active"
            }
            
            # Index capabilities
            capabilities = characteristics.get("capabilities", [])
            for capability in capabilities:
                if capability not in self.capability_index:
                    self.capability_index[capability] = []
                if agent_id not in self.capability_index[capability]:
                    self.capability_index[capability].append(agent_id)
            
            self.logger.info(f"Agent registered: {agent_name} ({agent_id})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register agent: {e}", exc_info=True)
            return False
    
    async def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get agent by ID.
        
        Args:
            agent_id: Agent identifier
        
        Returns:
            Optional[Dict[str, Any]]: Agent registration or None if not found
        """
        return self.registered_agents.get(agent_id)
    
    async def get_agent_by_name(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """
        Get agent by name.
        
        Args:
            agent_name: Agent name
        
        Returns:
            Optional[Dict[str, Any]]: Agent registration or None if not found
        """
        for agent in self.registered_agents.values():
            if agent.get("agent_name") == agent_name:
                return agent
        return None
    
    async def list_agents(
        self,
        realm: Optional[str] = None,
        capability: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List agents with optional filters.
        
        Args:
            realm: Optional realm filter
            capability: Optional capability filter
        
        Returns:
            List[Dict[str, Any]]: List of agent registrations
        """
        agents = list(self.registered_agents.values())
        
        if realm:
            agents = [
                a for a in agents
                if a.get("characteristics", {}).get("realm") == realm
            ]
        
        if capability:
            agent_ids = self.capability_index.get(capability, [])
            agents = [a for a in agents if a.get("agent_id") in agent_ids]
        
        return agents
    
    async def deregister_agent(self, agent_id: str) -> bool:
        """
        Deregister an agent.
        
        Args:
            agent_id: Agent identifier
        
        Returns:
            bool: True if deregistration successful
        """
        try:
            if agent_id not in self.registered_agents:
                self.logger.warning(f"Agent not found: {agent_id}")
                return False
            
            # Remove from capability index
            agent = self.registered_agents[agent_id]
            capabilities = agent.get("characteristics", {}).get("capabilities", [])
            for capability in capabilities:
                if capability in self.capability_index:
                    if agent_id in self.capability_index[capability]:
                        self.capability_index[capability].remove(agent_id)
                    if not self.capability_index[capability]:
                        del self.capability_index[capability]
            
            # Remove from registry
            del self.registered_agents[agent_id]
            
            self.logger.info(f"Agent deregistered: {agent_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to deregister agent: {e}", exc_info=True)
            return False
