"""
Agent Registry - Agent Registration and Discovery

Enhanced with persistence and health monitoring.
"""

from typing import Dict, Any, Optional, List
from utilities import get_logger, get_clock
import uuid

from .agent_base import AgentBase
from .health.agent_health_monitor import AgentHealthMonitor


class AgentRegistry:
    """
    Enhanced Agent Registry with persistence and health monitoring.
    
    Maintains a registry of all available agents with:
    - In-memory registration (fast access)
    - Supabase persistence (durable storage)
    - Health monitoring (availability, performance)
    """
    
    def __init__(self, supabase_adapter: Optional[Any] = None):
        """
        Initialize Agent Registry.
        
        Args:
            supabase_adapter: Optional Supabase adapter for persistence
        """
        self._agents: Dict[str, AgentBase] = {}  # agent_id -> Agent
        self._agents_by_type: Dict[str, List[AgentBase]] = {}  # agent_type -> [Agents]
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
        self.supabase_adapter = supabase_adapter
        self._health_monitor: Optional[AgentHealthMonitor] = None
    
    async def register(
        self,
        agent: AgentBase,
        persist: bool = True
    ) -> bool:
        """
        Register an agent (with optional persistence).
        
        Args:
            agent: Agent instance to register
            persist: Whether to persist to Supabase (default: True)
        
        Returns:
            True if registered successfully
        """
        try:
            # Register in memory
            self._agents[agent.agent_id] = agent
            
            # Index by type
            if agent.agent_type not in self._agents_by_type:
                self._agents_by_type[agent.agent_type] = []
            self._agents_by_type[agent.agent_type].append(agent)
            
            # Persist to Supabase if adapter available
            if persist and self.supabase_adapter:
                await self._persist_agent(agent)
            
            # Start health monitoring
            if self._health_monitor:
                await self._health_monitor.start_monitoring(agent.agent_id)
            
            self.logger.info(f"✅ Agent registered: {agent.agent_id} ({agent.agent_type})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register agent: {e}", exc_info=True)
            return False
    
    async def _persist_agent(self, agent: AgentBase) -> bool:
        """Persist agent to Supabase."""
        try:
            # Get agent definition ID if available
            agent_definition_id = None
            if hasattr(agent, 'agent_definition') and agent.agent_definition:
                agent_definition_id = agent.agent_definition.agent_id
            
            # Prepare agent record
            agent_record = {
                "id": str(uuid.uuid4()),
                "agent_id": agent.agent_id,
                "agent_name": getattr(agent, 'agent_definition', {}).get('constitution', {}).get('role', agent.agent_id) if hasattr(agent, 'agent_definition') else agent.agent_id,
                "agent_type": agent.agent_type,
                "agent_config_id": agent_definition_id,
                "capabilities": agent.capabilities,
                "required_roles": agent.permissions.get("required_roles", []) if hasattr(agent, 'permissions') else [],
                "tenant_id": getattr(agent, 'tenant_id', None),
                "status": "active",
                "health_status": {},
                "created_at": self.clock.now().isoformat() if self.clock else None
            }
            
            # Insert/update in Supabase
            result = await self.supabase_adapter.execute_rls_policy(
                table="agent_registry",
                operation="upsert",  # Insert or update
                user_context={"tenant_id": agent_record.get("tenant_id", "platform")},
                data=agent_record,
                filters={"agent_id": agent.agent_id}
            )
            
            if result.get("success"):
                self.logger.debug(f"✅ Persisted agent: {agent.agent_id}")
                return True
            else:
                self.logger.warning(f"Failed to persist agent: {result.get('error')}")
                return False
                
        except Exception as e:
            self.logger.error(f"Exception persisting agent: {e}", exc_info=True)
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
    
    def set_health_monitor(self, health_monitor: AgentHealthMonitor):
        """Set health monitor for this registry."""
        self._health_monitor = health_monitor
    
    async def get_agent_health(self, agent_id: str) -> Dict[str, Any]:
        """
        Get agent health status.
        
        Args:
            agent_id: Agent identifier
        
        Returns:
            Dict with health status
        """
        if self._health_monitor:
            return await self._health_monitor.get_health(agent_id)
        return {"status": "unknown"}