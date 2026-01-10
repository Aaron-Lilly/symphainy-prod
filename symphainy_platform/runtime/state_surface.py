"""
Runtime State Surface - Centralized Execution State

Runtime-owned, not realm-owned.
Uses Public Works StateManagementAbstraction for swappable backends.
In-memory fallback for tests.
"""

from typing import Dict, Any, Optional, List
from utilities import get_logger, get_clock

from symphainy_platform.foundations.public_works.protocols.state_protocol import StateManagementProtocol


class StateSurface:
    """
    Centralized recording of execution state.
    
    Runtime-owned state surface that coordinates all state operations.
    Uses Public Works StateManagementAbstraction for swappable backends.
    In-memory fallback for tests.
    """
    
    def __init__(
        self,
        state_abstraction: Optional[StateManagementProtocol] = None,
        use_memory: bool = False
    ):
        """
        Initialize state surface.
        
        Args:
            state_abstraction: Optional state management abstraction (from Public Works)
            use_memory: If True, use in-memory storage (for tests)
        """
        self.use_memory = use_memory
        self.state_abstraction = state_abstraction
        self._memory_store: Dict[str, Any] = {}
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
    
    async def get_execution_state(
        self,
        execution_id: str,
        tenant_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get execution state.
        
        Args:
            execution_id: Execution identifier
            tenant_id: Tenant identifier (for isolation)
        
        Returns:
            Execution state dictionary or None if not found
        """
        state_id = f"execution:{tenant_id}:{execution_id}"
        
        if self.use_memory:
            return self._memory_store.get(state_id)
        
        if not self.state_abstraction:
            self.logger.warning("State abstraction not available, using in-memory fallback")
            return self._memory_store.get(state_id)
        
        try:
            state_data = await self.state_abstraction.retrieve_state(state_id)
            if state_data:
                return state_data.get("state_data")
        except Exception as e:
            self.logger.error(f"Failed to get execution state: {e}", exc_info=True)
        
        return None
    
    async def set_execution_state(
        self,
        execution_id: str,
        tenant_id: str,
        state: Dict[str, Any]
    ) -> bool:
        """
        Set execution state.
        
        Args:
            execution_id: Execution identifier
            tenant_id: Tenant identifier (for isolation)
            state: State dictionary
        
        Returns:
            True if successful
        """
        state_id = f"execution:{tenant_id}:{execution_id}"
        state["updated_at"] = self.clock.now_iso()
        
        if self.use_memory:
            self._memory_store[state_id] = state
            return True
        
        if not self.state_abstraction:
            self.logger.warning("State abstraction not available, using in-memory fallback")
            self._memory_store[state_id] = state
            return True
        
        try:
            success = await self.state_abstraction.store_state(
                state_id=state_id,
                state_data=state,
                metadata={"backend": "redis", "strategy": "hot", "type": "execution"},
                ttl=3600  # 1 hour TTL
            )
            return success
        except Exception as e:
            self.logger.error(f"Failed to set execution state: {e}", exc_info=True)
            # Fallback to memory
            self._memory_store[state_id] = state
            return False
    
    async def get_session_state(
        self,
        session_id: str,
        tenant_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get session state.
        
        Args:
            session_id: Session identifier
            tenant_id: Tenant identifier (for isolation)
        
        Returns:
            Session state dictionary or None if not found
        """
        state_id = f"session:{tenant_id}:{session_id}"
        
        if self.use_memory:
            return self._memory_store.get(state_id)
        
        if not self.state_abstraction:
            self.logger.warning("State abstraction not available, using in-memory fallback")
            return self._memory_store.get(state_id)
        
        try:
            state_data = await self.state_abstraction.retrieve_state(state_id)
            if state_data:
                return state_data.get("state_data")
        except Exception as e:
            self.logger.error(f"Failed to get session state: {e}", exc_info=True)
        
        return None
    
    async def set_session_state(
        self,
        session_id: str,
        tenant_id: str,
        state: Dict[str, Any]
    ) -> bool:
        """
        Set session state.
        
        Args:
            session_id: Session identifier
            tenant_id: Tenant identifier (for isolation)
            state: State dictionary
        
        Returns:
            True if successful
        """
        state_id = f"session:{tenant_id}:{session_id}"
        state["updated_at"] = self.clock.now_iso()
        
        if self.use_memory:
            self._memory_store[state_id] = state
            return True
        
        if not self.state_abstraction:
            self.logger.warning("State abstraction not available, using in-memory fallback")
            self._memory_store[state_id] = state
            return True
        
        try:
            success = await self.state_abstraction.store_state(
                state_id=state_id,
                state_data=state,
                metadata={"backend": "redis", "strategy": "hot", "type": "session"},
                ttl=86400  # 24 hour TTL
            )
            return success
        except Exception as e:
            self.logger.error(f"Failed to set session state: {e}", exc_info=True)
            # Fallback to memory
            self._memory_store[state_id] = state
            return False
    
    async def delete_state(
        self,
        key_prefix: str,
        tenant_id: str,
        resource_id: str
    ) -> bool:
        """
        Delete state.
        
        Args:
            key_prefix: Key prefix (e.g., "execution", "session")
            tenant_id: Tenant identifier
            resource_id: Resource identifier
        
        Returns:
            True if successful
        """
        state_id = f"{key_prefix}:{tenant_id}:{resource_id}"
        
        if self.use_memory:
            if state_id in self._memory_store:
                del self._memory_store[state_id]
                return True
            return False
        
        if not self.state_abstraction:
            self.logger.warning("State abstraction not available, using in-memory fallback")
            if state_id in self._memory_store:
                del self._memory_store[state_id]
                return True
            return False
        
        try:
            success = await self.state_abstraction.delete_state(state_id)
            return success
        except Exception as e:
            self.logger.error(f"Failed to delete state: {e}", exc_info=True)
            return False
    
    async def list_executions(
        self,
        tenant_id: str,
        limit: int = 100
    ) -> List[str]:
        """
        List execution IDs for tenant.
        
        Args:
            tenant_id: Tenant identifier
            limit: Maximum number of executions to return
        
        Returns:
            List of execution IDs
        """
        if self.use_memory:
            return [
                key.split(":")[-1]
                for key in self._memory_store.keys()
                if key.startswith(f"execution:{tenant_id}:")
            ][:limit]
        
        if not self.state_abstraction:
            return []
        
        try:
            states = await self.state_abstraction.list_states(
                filters={"tenant_id": tenant_id, "type": "execution"},
                limit=limit
            )
            # Extract execution IDs from state IDs
            execution_ids = []
            for state in states:
                state_id = state.get("state_id", "")
                if state_id.startswith(f"execution:{tenant_id}:"):
                    execution_ids.append(state_id.split(":")[-1])
            return execution_ids[:limit]
        except Exception as e:
            self.logger.error(f"Failed to list executions: {e}", exc_info=True)
            return []
