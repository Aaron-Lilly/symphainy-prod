"""
Runtime State Surface - Centralized Execution State

Runtime-owned, not realm-owned.
Redis-backed for hot state.
In-memory fallback for tests.
"""

import json
from typing import Dict, Any, Optional, List
import redis.asyncio as redis
from redis.asyncio import Redis

from utilities import get_clock


class StateSurface:
    """
    Centralized recording of execution state.
    
    Runtime-owned state surface that coordinates all state operations.
    Uses Redis for hot state, with in-memory fallback for tests.
    """
    
    def __init__(
        self,
        redis_client: Optional[Redis] = None,
        use_memory: bool = False
    ):
        """
        Initialize state surface.
        
        Args:
            redis_client: Optional Redis client (if None and not use_memory, will create)
            use_memory: If True, use in-memory storage (for tests)
        """
        self.use_memory = use_memory
        self.redis_client = redis_client
        self._memory_store: Dict[str, Any] = {}
    
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
        key = f"execution:{tenant_id}:{execution_id}"
        
        if self.use_memory:
            return self._memory_store.get(key)
        
        if not self.redis_client:
            return None
        
        try:
            data = await self.redis_client.get(key)
            if data:
                return json.loads(data)
        except Exception:
            pass
        
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
        key = f"execution:{tenant_id}:{execution_id}"
        state["updated_at"] = get_clock().now_iso()
        
        if self.use_memory:
            self._memory_store[key] = state
            return True
        
        if not self.redis_client:
            return False
        
        try:
            await self.redis_client.set(
                key,
                json.dumps(state),
                ex=3600  # 1 hour TTL
            )
            return True
        except Exception:
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
        key = f"session:{tenant_id}:{session_id}"
        
        if self.use_memory:
            return self._memory_store.get(key)
        
        if not self.redis_client:
            return None
        
        try:
            data = await self.redis_client.get(key)
            if data:
                return json.loads(data)
        except Exception:
            pass
        
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
        key = f"session:{tenant_id}:{session_id}"
        state["updated_at"] = get_clock().now_iso()
        
        if self.use_memory:
            self._memory_store[key] = state
            return True
        
        if not self.redis_client:
            return False
        
        try:
            await self.redis_client.set(
                key,
                json.dumps(state),
                ex=86400  # 24 hour TTL
            )
            return True
        except Exception:
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
        key = f"{key_prefix}:{tenant_id}:{resource_id}"
        
        if self.use_memory:
            if key in self._memory_store:
                del self._memory_store[key]
                return True
            return False
        
        if not self.redis_client:
            return False
        
        try:
            await self.redis_client.delete(key)
            return True
        except Exception:
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
        pattern = f"execution:{tenant_id}:*"
        
        if self.use_memory:
            return [
                key.split(":")[-1]
                for key in self._memory_store.keys()
                if key.startswith(f"execution:{tenant_id}:")
            ][:limit]
        
        if not self.redis_client:
            return []
        
        try:
            keys = []
            async for key in self.redis_client.scan_iter(match=pattern, count=limit):
                keys.append(key.decode().split(":")[-1])
            return keys[:limit]
        except Exception:
            return []
