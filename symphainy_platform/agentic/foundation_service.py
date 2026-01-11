"""
Agent Foundation Service - Phase 3

Orchestrates agent capabilities and provides unified access to agents.

WHAT: I provide agent capabilities to the platform
HOW: I orchestrate agent registration, discovery, and execution
"""

from typing import Dict, Any, Optional, List
from .agent_base import AgentBase
from symphainy_platform.foundations.curator.foundation_service import CuratorFoundationService
from symphainy_platform.runtime.runtime_service import RuntimeService
from symphainy_platform.runtime.state_surface import StateSurface
from utilities import get_logger, LogLevel, LogCategory


class AgentFoundationService:
    """
    Agent Foundation Service
    
    Orchestrates all agent capabilities and provides unified access.
    
    Responsibilities:
    - Register agents with Curator
    - Provide agent discovery
    - Coordinate agent execution
    - Manage agent lifecycle
    """
    
    def __init__(
        self,
        curator_foundation: CuratorFoundationService,
        runtime_service: RuntimeService,
        state_surface: StateSurface
    ):
        """
        Initialize Agent Foundation Service.
        
        Args:
            curator_foundation: Curator foundation for agent registration
            runtime_service: Runtime service for agent execution
            state_surface: State surface for agent fact gathering
        """
        self.curator = curator_foundation
        self.runtime_service = runtime_service
        self.state_surface = state_surface
        self.logger = get_logger("agent_foundation", LogLevel.INFO, LogCategory.PLATFORM)
        
        # Agent registry
        self.agents: Dict[str, AgentBase] = {}
        self.is_initialized = False
    
    async def initialize(self) -> bool:
        """Initialize Agent Foundation Service."""
        try:
            self.logger.info("Initializing Agent Foundation Service")
            self.is_initialized = True
            self.logger.info("Agent Foundation Service initialized")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize Agent Foundation: {e}", exc_info=e)
            return False
    
    async def register_agent(self, agent: AgentBase) -> bool:
        """
        Register an agent with the foundation and Curator.
        
        Args:
            agent: Agent instance to register
        
        Returns:
            True if registration successful, False otherwise
        """
        try:
            # Initialize agent if not already initialized
            if not agent.is_initialized:
                success = await agent.initialize()
                if not success:
                    self.logger.error(f"Failed to initialize agent: {agent.agent_name}")
                    return False
            
            # Store agent
            self.agents[agent.agent_name] = agent
            
            # Register with Curator
            # Use agent_name as agent_id (can be customized if needed)
            agent_id = agent.agent_name
            
            await self.curator.register_agent(
                agent_id=agent_id,
                agent_name=agent.agent_name,
                characteristics={
                    "capabilities": agent.capabilities,
                    "description": agent.description,
                    "agent_type": type(agent).__name__,
                    "realm": None  # Agents can be realm-specific or platform-wide
                },
                contracts={
                    "agent_api": {
                        "reason": "async method for reasoning",
                        "get_agent_info": "method for agent metadata"
                    }
                }
            )
            
            self.logger.info(f"Agent registered: {agent.agent_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register agent {agent.agent_name}: {e}", exc_info=e)
            return False
    
    def get_agent(self, agent_name: str) -> Optional[AgentBase]:
        """
        Get agent by name.
        
        Args:
            agent_name: Name of the agent
        
        Returns:
            Agent instance or None if not found
        """
        return self.agents.get(agent_name)
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """
        List all registered agents.
        
        Returns:
            List of agent metadata
        """
        return [
            agent.get_agent_info()
            for agent in self.agents.values()
        ]
    
    async def execute_agent_reasoning(
        self,
        agent_name: str,
        context: Dict[str, Any],
        execution_id: Optional[str] = None,
        session_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute agent reasoning.
        
        This method:
        1. Gets the agent
        2. Executes reasoning
        3. Returns reasoned artifacts
        
        Args:
            agent_name: Name of the agent to execute
            context: Input context for reasoning
            execution_id: Optional execution ID
            session_id: Optional session ID
            tenant_id: Tenant ID for isolation
            **kwargs: Additional parameters
        
        Returns:
            Dict containing reasoned artifacts
        """
        agent = self.get_agent(agent_name)
        if not agent:
            raise ValueError(f"Agent not found: {agent_name}")
        
        # Execute reasoning
        result = await agent.reason(
            context=context,
            execution_id=execution_id,
            session_id=session_id,
            tenant_id=tenant_id,
            **kwargs
        )
        
        return result
    
    async def shutdown(self) -> None:
        """Shutdown Agent Foundation Service."""
        self.logger.info("Shutting down Agent Foundation Service")
        
        # Shutdown all agents
        for agent_name, agent in self.agents.items():
            try:
                await agent.shutdown()
            except Exception as e:
                self.logger.error(f"Error shutting down agent {agent_name}: {e}")
        
        self.is_initialized = False
