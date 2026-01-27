"""
State Management Protocol - Abstraction Contract

Defines the contract for state management operations across different backends.
This protocol enables swappability between Redis (hot state) and ArangoDB (durable state).

WHAT (Infrastructure Role): I define how state data should be managed and stored
HOW (Infrastructure Implementation): I provide the interface for state management logic
"""

from typing import Protocol, Dict, Any, Optional, List


class StateManagementProtocol(Protocol):
    """
    Protocol for state management operations.
    
    This protocol defines how state data should be stored, retrieved,
    updated, and managed across different persistence backends.
    
    Supports both hot state (Redis) and durable state (ArangoDB).
    """
    
    async def store_state(
        self,
        state_id: str,
        state_data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Store state data in the appropriate backend.
        
        Args:
            state_id: Unique identifier for the state
            state_data: The state data to store
            metadata: Optional metadata for the state (e.g., {"backend": "redis", "strategy": "hot"})
            ttl: Time-to-live in seconds (for hot state)
            
        Returns:
            bool: True if storage was successful
        """
        ...
    
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
        ...
    
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
        ...
    
    async def delete_state(self, state_id: str) -> bool:
        """
        Delete state data from storage.
        
        Args:
            state_id: Unique identifier for the state
            
        Returns:
            bool: True if deletion was successful
        """
        ...
    
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
        ...
