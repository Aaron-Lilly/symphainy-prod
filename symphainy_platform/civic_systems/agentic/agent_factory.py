"""
Agent Factory - Creates Agent Instances
"""

from typing import Dict, Any, Optional, Type
from utilities import get_logger, generate_event_id

from .agent_base import AgentBase
from .agent_registry import AgentRegistry
from .collaboration.collaboration_router import CollaborationRouter


class AgentFactory:
    """
    Factory for creating agent instances.
    
    Provides convenience methods for creating agents with proper initialization.
    """
    
    def __init__(
        self,
        agent_registry: Optional[AgentRegistry] = None,
        collaboration_router: Optional[CollaborationRouter] = None
    ):
        """
        Initialize agent factory.
        
        Args:
            agent_registry: Optional agent registry (for auto-registration)
            collaboration_router: Optional collaboration router
        """
        self.agent_registry = agent_registry or AgentRegistry()
        self.collaboration_router = collaboration_router
        self.logger = get_logger(self.__class__.__name__)
    
    def create_agent(
        self,
        agent_class: Type[AgentBase],
        agent_type: str,
        capabilities: list[str],
        agent_id: Optional[str] = None,
        **kwargs
    ) -> AgentBase:
        """
        Create an agent instance.
        
        Args:
            agent_class: Agent class to instantiate
            agent_type: Agent type
            capabilities: List of agent capabilities
            agent_id: Optional agent ID (generated if not provided)
            **kwargs: Additional arguments for agent constructor
        
        Returns:
            Created agent instance
        """
        if agent_id is None:
            agent_id = f"{agent_type}:{generate_event_id()}"
        
        # Create agent with collaboration router
        agent = agent_class(
            agent_id=agent_id,
            agent_type=agent_type,
            capabilities=capabilities,
            collaboration_router=self.collaboration_router,
            **kwargs
        )
        
        # Auto-register if registry is available
        if self.agent_registry:
            self.agent_registry.register(agent)
        
        self.logger.info(f"Agent created: {agent_id} ({agent_type})")
        return agent
    
    def get_registry(self) -> AgentRegistry:
        """Get agent registry."""
        return self.agent_registry
