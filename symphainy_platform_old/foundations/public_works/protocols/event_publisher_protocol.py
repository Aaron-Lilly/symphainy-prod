"""
Event Publisher Protocol - Interface Definition (Layer 2)

Defines the interface for event publishing across different backends.

WHAT (Infrastructure Role): I define the contract for event publishing
HOW (Infrastructure Implementation): I specify the interface that adapters must implement
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List


class EventPublisherProtocol(ABC):
    """
    Protocol for event publishing.
    
    Defines the interface that event publisher adapters must implement.
    """
    
    @abstractmethod
    async def publish(
        self,
        topic: str,
        event_type: str,
        event_data: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Publish an event to a topic.
        
        Args:
            topic: Topic/channel name
            event_type: Event type identifier
            event_data: Event data payload
            headers: Optional event headers (e.g., correlation_id, tenant_id)
        
        Returns:
            True if event published successfully
        """
        pass
    
    @abstractmethod
    async def publish_batch(
        self,
        topic: str,
        events: List[Dict[str, Any]]
    ) -> int:
        """
        Publish multiple events to a topic in a batch.
        
        Args:
            topic: Topic/channel name
            events: List of events, each with 'event_type', 'event_data', and optional 'headers'
        
        Returns:
            Number of events published successfully
        """
        pass
    
    @abstractmethod
    async def connect(self) -> bool:
        """
        Connect to event publishing backend.
        
        Returns:
            True if connection successful
        """
        pass
    
    @abstractmethod
    async def disconnect(self):
        """Disconnect from event publishing backend."""
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """
        Check if connected to event publishing backend.
        
        Returns:
            True if connected
        """
        pass
