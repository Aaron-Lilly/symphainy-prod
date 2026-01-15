"""
Agent Registry - Agent Registration and Discovery
"""

from typing import Dict, Any, Optional, List
from utilities import get_logger

from .agent_base import AgentBase


class AgentRegistry:
    """
    Registry for agent registration and discovery.
    
    Maintains a registry of all available agents.
    """
    
    def __init__(self):
        """Initialize agent registry."""
        self._agents: Dict[str, AgentBase] = {}  # agent_id -> Agent
        self._agents_by_type: Dict[str, List[AgentBase]] = {}  # agent_type -> [Agents]
        self.logger = get_logger(self.__class__.__name__)
    
    def register(self, agent: AgentBase) -> bool:
        """
        Register an agent.
        
        Args:
            agent: Agent instance to register
        
        Returns:
            True if registered successfully
        """
        try:
            self._agents[agent.agent_id] = agent
            
            # Index by type
            if agent.agent_type not in self._agents_by_type:
                self._agents_by_type[agent.agent_type] = []
            self._agents_by_type[agent.agent_type].append(agent)
            
            self.logger.info(f"Agent registered: {agent.agent_id} ({agent.agent_type})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register agent: {e}", exc_info=True)
            return False
    
    def unregister(self, agent_id: str) -> bool:
        """
        Unregister an agent.
        
        Args:
            agent_id: Agent identifier
        
        Returns:
            True if unregistered successfully
        """
        try:
            agent = self._agents.get(agent_id)
            if not agent:
                return False
            
            # Remove from type index
            if agent.agent_type in self._agents_by_type:
                self._agents_by_type[agent.agent_type] = [
                    a for a in self._agents_by_type[agent.agent_type]
                    if a.agent_id != agent_id
                ]
            
            del self._agents[agent_id]
            self.logger.info(f"Agent unregistered: {agent_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to unregister agent: {e}", exc_info=True)
            return False
    
    def get_agent(self, agent_id: str) -> Optional[AgentBase]:
        """
        Get agent by ID.
        
        Args:
            agent_id: Agent identifier
        
        Returns:
            Agent instance, or None if not found
        """
        return self._agents.get(agent_id)
    
    def get_agent_by_type(self, agent_type: str) -> Optional[AgentBase]:
        """
        Get first agent of a given type.
        
        Args:
            agent_type: Agent type
        
        Returns:
            Agent instance, or None if not found
        """
        agents = self._agents_by_type.get(agent_type, [])
        return agents[0] if agents else None
    
    def get_agents_by_type(self, agent_type: str) -> List[AgentBase]:
        """
        Get all agents of a given type.
        
        Args:
            agent_type: Agent type
        
        Returns:
            List of agent instances
        """
        return self._agents_by_type.get(agent_type, [])
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """
        List all registered agents.
        
        Returns:
            List of agent metadata dictionaries
        """
        return [
            {
                "agent_id": agent.agent_id,
                "agent_type": agent.agent_type,
                "capabilities": agent.capabilities
            }
            for agent in self._agents.values()
        ]
    
    def list_agent_types(self) -> List[str]:
        """
        List all registered agent types.
        
        Returns:
            List of agent type strings
        """
        return list(self._agents_by_type.keys())
