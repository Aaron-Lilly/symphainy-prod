"""
State Management Abstraction - Business Logic Implementation (Layer 1)

Implements state management operations across different backends.
Coordinates between Redis (hot state) and ArangoDB (durable state).

WHAT (Infrastructure Role): I manage state data storage and retrieval
HOW (Infrastructure Implementation): I coordinate between Redis and ArangoDB adapters
"""

import json
from typing import Dict, Any, Optional, List
from datetime import datetime

from utilities import get_logger, get_clock

from ..protocols.state_protocol import StateManagementProtocol
from ..adapters.redis_adapter import RedisAdapter


class StateManagementAbstraction(StateManagementProtocol):
    """
    State management abstraction with business logic.
    
    Coordinates between Redis (hot state) and ArangoDB (durable state).
    For Phase 2, we start with Redis only. ArangoDB will be added when needed.
    """
    
    def __init__(
        self,
        redis_adapter: Optional[RedisAdapter] = None,
        arango_adapter: Optional[Any] = None  # Will be added in Phase 2 when ArangoDB adapter is ready
    ):
        """
        Initialize state management abstraction.
        
        Args:
            redis_adapter: Redis adapter for hot state
            arango_adapter: ArangoDB adapter for durable state (optional for now)
        """
        self.redis_adapter = redis_adapter
        self.arango_adapter = arango_adapter
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
        
        # State storage configuration
        self.redis_prefix = "state:"
        
        self.logger.info("State Management Abstraction initialized")
    
    async def store_state(
        self,
        state_id: str,
        state_data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Store state data in the appropriate backend.
        
        Backend selection based on metadata:
        - Redis: Hot state with TTL (default)
        - ArangoDB: Durable state (when available)
        
        Args:
            state_id: Unique identifier for the state
            state_data: The state data to store
            metadata: Optional metadata (e.g., {"backend": "redis", "strategy": "hot"})
            ttl: Time-to-live in seconds (for hot state)
        
        Returns:
            bool: True if storage was successful
        """
        try:
            # Determine backend from metadata
            backend = (metadata or {}).get("backend", "redis")
            strategy = (metadata or {}).get("strategy", "hot")
            
            # Store in appropriate backend
            if backend == "arango_db" and self.arango_adapter:
                # ArangoDB storage (durable)
                try:
                    # Store in ArangoDB collection
                    collection_name = "state_data"
                    
                    # Ensure collection exists
                    if not await self.arango_adapter.collection_exists(collection_name):
                        await self.arango_adapter.create_collection(collection_name)
                    
                    # Prepare document
                    document = {
                        "_key": state_id,
                        "state_data": state_data,
                        "metadata": metadata or {},
                        "created_at": self.clock.now_iso(),
                        "strategy": strategy,
                        "ttl": ttl
                    }
                    
                    # Insert or update document
                    existing = await self.arango_adapter.get_document(collection_name, state_id)
                    if existing:
                        result = await self.arango_adapter.update_document(
                            collection_name,
                            state_id,
                            document
                        )
                    else:
                        result = await self.arango_adapter.insert_document(collection_name, document)
                    
                    if result:
                        self.logger.debug(f"State stored in ArangoDB: {state_id}")
                        return True
                    else:
                        self.logger.error(f"Failed to store state in ArangoDB: {state_id}")
                        return False
                except Exception as e:
                    self.logger.error(f"ArangoDB storage failed for {state_id}: {e}", exc_info=True)
                    # Fall back to Redis if ArangoDB fails
                    backend = "redis"
            
            if backend == "redis" and self.redis_adapter:
                # Redis storage (hot state)
                redis_key = f"{self.redis_prefix}{state_id}"
                redis_data = {
                    "state_data": state_data,
                    "metadata": metadata or {},
                    "created_at": self.clock.now_iso(),
                    "strategy": strategy
                }
                
                success = await self.redis_adapter.set_json(redis_key, redis_data, ttl)
                if success:
                    self.logger.debug(f"State stored in Redis: {state_id}")
                    return True
                else:
                    self.logger.error(f"Failed to store state in Redis: {state_id}")
                    return False
            else:
                self.logger.error(f"No adapter available for backend: {backend}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to store state {state_id}: {e}", exc_info=True)
            return False
    
    async def retrieve_state(self, state_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve state data from the appropriate backend.
        
        Tries backends in order of persistence:
        1. Redis (hot state)
        2. ArangoDB (durable state)
        
        Args:
            state_id: Unique identifier for the state
        
        Returns:
            Optional[Dict[str, Any]]: State data if found, None otherwise
        """
        try:
            # Try Redis first (hot state)
            if self.redis_adapter:
                redis_key = f"{self.redis_prefix}{state_id}"
                redis_result = await self.redis_adapter.get_json(redis_key)
                if redis_result:
                    return redis_result.get("state_data")
            
            # Try ArangoDB second (durable state)
            if self.arango_adapter:
                try:
                    collection_name = "state_data"
                    document = await self.arango_adapter.get_document(collection_name, state_id)
                    if document:
                        # Remove ArangoDB internal fields
                        document.pop("_key", None)
                        document.pop("_id", None)
                        document.pop("_rev", None)
                        return document.get("state_data")
                except Exception as e:
                    self.logger.debug(f"ArangoDB retrieval failed for {state_id}: {e}")
            
            self.logger.debug(f"State not found: {state_id}")
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve state {state_id}: {e}", exc_info=True)
            return None
    
    async def update_state(
        self,
        state_id: str,
        updates: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update existing state data.
        
        Args:
            state_id: Unique identifier for the state
            updates: The updates to apply
            metadata: Optional metadata updates
        
        Returns:
            bool: True if update was successful
        """
        try:
            # Retrieve existing state
            existing_state = await self.retrieve_state(state_id)
            if not existing_state:
                self.logger.warning(f"State not found for update: {state_id}")
                return False
            
            # Merge updates
            updated_state = {**existing_state, **updates}
            
            # Store updated state (preserve metadata)
            existing_metadata = (await self.redis_adapter.get_json(f"{self.redis_prefix}{state_id}") or {}).get("metadata", {})
            if metadata:
                existing_metadata.update(metadata)
            
            return await self.store_state(state_id, updated_state, existing_metadata)
            
        except Exception as e:
            self.logger.error(f"Failed to update state {state_id}: {e}", exc_info=True)
            return False
    
    async def delete_state(self, state_id: str) -> bool:
        """
        Delete state data from storage.
        
        Args:
            state_id: Unique identifier for the state
        
        Returns:
            bool: True if deletion was successful
        """
        try:
            # Try Redis first
            if self.redis_adapter:
                redis_key = f"{self.redis_prefix}{state_id}"
                success = await self.redis_adapter.delete(redis_key)
                if success:
                    self.logger.debug(f"State deleted from Redis: {state_id}")
                    return True
            
            # Try ArangoDB second
            if self.arango_adapter:
                try:
                    collection_name = "state_data"
                    success = await self.arango_adapter.delete_document(collection_name, state_id)
                    if success:
                        self.logger.debug(f"State deleted from ArangoDB: {state_id}")
                        return True
                except Exception as e:
                    self.logger.debug(f"ArangoDB deletion failed for {state_id}: {e}")
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to delete state {state_id}: {e}", exc_info=True)
            return False
    
    async def list_states(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        List states matching the given criteria.
        
        Args:
            filters: Optional filters to apply (e.g., {"tenant_id": "tenant_123"})
            limit: Maximum number of results
            offset: Number of results to skip
        
        Returns:
            List[Dict[str, Any]]: List of matching states
        """
        try:
            # Try ArangoDB first (if available) for more efficient querying
            if self.arango_adapter:
                try:
                    collection_name = "state_data"
                    limit = limit or 100
                    offset = offset or 0
                    
                    # Build AQL query with filters
                    query = f"""
                    FOR doc IN {collection_name}
                    """
                    
                    bind_vars = {}
                    
                    # Add filters if provided
                    if filters:
                        filter_conditions = []
                        for key, value in filters.items():
                            filter_key = f"filter_{key}"
                            filter_conditions.append(f"doc.state_data.{key} == @{filter_key}")
                            bind_vars[filter_key] = value
                        
                        if filter_conditions:
                            query += f"\n    FILTER {' AND '.join(filter_conditions)}"
                    
                    # Add limit and offset
                    query += f"\n    LIMIT @offset, @limit"
                    bind_vars["offset"] = offset
                    bind_vars["limit"] = limit
                    
                    query += "\n    RETURN doc.state_data"
                    
                    results = await self.arango_adapter.execute_aql(query, bind_vars=bind_vars)
                    return results
                except Exception as e:
                    self.logger.debug(f"ArangoDB list_states failed: {e}, falling back to Redis")
            
            # Fall back to Redis
            if not self.redis_adapter:
                return []
            
            # Scan Redis for matching keys
            pattern = f"{self.redis_prefix}*"
            limit = limit or 100
            
            states = []
            count = 0
            async for key in self.redis_adapter.scan_iter(match=pattern, count=limit):
                if offset and count < offset:
                    count += 1
                    continue
                
                state_data = await self.retrieve_state(key.replace(self.redis_prefix, ""))
                if state_data:
                    # Apply filters if provided
                    if filters:
                        # Simple filter matching (can be enhanced)
                        match = True
                        for key, value in filters.items():
                            if key not in state_data or state_data[key] != value:
                                match = False
                                break
                        if not match:
                            continue
                    
                    states.append(state_data)
                    if len(states) >= limit:
                        break
                
                count += 1
            
            return states
            
        except Exception as e:
            self.logger.error(f"Failed to list states: {e}", exc_info=True)
            return []
