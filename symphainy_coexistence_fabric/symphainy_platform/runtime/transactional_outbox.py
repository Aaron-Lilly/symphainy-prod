"""
Transactional Outbox - Atomic Event Publishing

Guarantees atomic event publishing within saga steps.

WHAT (Runtime Role): I guarantee events are published atomically with state changes
HOW (Runtime Implementation): I use Redis Streams for outbox storage

Key Principle: Events are added to outbox atomically with state changes.
They are published asynchronously, ensuring no events are lost even on failures.
"""

import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

from utilities import get_logger, get_clock, generate_event_id
from .wal import WriteAheadLog, WALEventType
from symphainy_platform.foundations.public_works.protocols.event_log_protocol import EventLogProtocol


@dataclass
class OutboxEvent:
    """Outbox event structure."""
    event_id: str
    execution_id: str
    event_type: str
    event_data: Dict[str, Any]
    created_at: datetime
    published: bool = False
    published_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "event_id": self.event_id,
            "execution_id": self.execution_id,
            "event_type": self.event_type,
            "event_data": self.event_data,
            "created_at": self.created_at.isoformat(),
            "published": self.published,
            "published_at": self.published_at.isoformat() if self.published_at else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OutboxEvent":
        """Create event from dictionary."""
        return cls(
            event_id=data["event_id"],
            execution_id=data["execution_id"],
            event_type=data["event_type"],
            event_data=data["event_data"],
            created_at=datetime.fromisoformat(data["created_at"]),
            published=data.get("published", False),
            published_at=datetime.fromisoformat(data["published_at"]) if data.get("published_at") else None,
        )


class TransactionalOutbox:
    """
    Transactional outbox for atomic event publishing.
    
    Ensures events are published atomically with state changes.
    Uses Redis Streams for outbox storage.
    """
    
    def __init__(
        self,
        event_log: Optional[EventLogProtocol] = None,
        wal: Optional[WriteAheadLog] = None
    ):
        """
        Initialize transactional outbox.

        Args:
            event_log: Event log backend (protocol from Public Works; no adapter)
            wal: Optional WAL for audit logging
        """
        self.event_log = event_log
        self.wal = wal
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
        self.outbox_stream_prefix = "outbox:"
    
    def _get_stream_name(self, execution_id: str) -> str:
        """Get stream name for execution outbox."""
        return f"{self.outbox_stream_prefix}{execution_id}"
    
    async def add_event(
        self,
        execution_id: str,
        event_type: str,
        event_data: Dict[str, Any],
        tenant_id: Optional[str] = None
    ) -> bool:
        """
        Add event to outbox (atomic with state change).
        
        This should be called within the same transaction as the state change.
        In our case, we use Redis Streams which provides atomicity.
        
        Args:
            execution_id: Execution identifier
            event_type: Event type
            event_data: Event data
            tenant_id: Optional tenant identifier (for WAL logging)
        
        Returns:
            True if event added successfully

        Raises:
            RuntimeError: If event_log was not wired (platform contract violation).
        """
        if not self.event_log:
            raise RuntimeError(
                "TransactionalOutbox was not wired with an event log backend; "
                "platform contract violation. Composition root must pass get_wal_backend() when building Outbox."
            )
        try:
            event_id = generate_event_id()
            stream_name = self._get_stream_name(execution_id)
            
            # Create outbox event
            outbox_event = OutboxEvent(
                event_id=event_id,
                execution_id=execution_id,
                event_type=event_type,
                event_data=event_data,
                created_at=self.clock.now_utc(),
                published=False
            )
            
            # Add to Redis Stream (atomic operation)
            fields = {
                "event_id": outbox_event.event_id,
                "event_type": outbox_event.event_type,
                "event_data": json.dumps(outbox_event.event_data),
                "created_at": outbox_event.created_at.isoformat(),
                "published": "false",
            }
            
            message_id = await self.event_log.xadd(
                stream_name,
                fields,
                maxlen=10000,  # Keep last 10k events per execution
                approximate=True
            )
            
            if message_id:
                self.logger.debug(f"Event added to outbox: {execution_id}/{event_id}")
                
                # Log to WAL if available
                if self.wal and tenant_id:
                    await self.wal.append(
                        WALEventType.STEP_COMPLETED,
                        tenant_id,
                        {
                            "execution_id": execution_id,
                            "outbox_event_id": event_id,
                            "event_type": event_type,
                        }
                    )
                
                return True
            else:
                self.logger.error(f"Failed to add event to outbox: {execution_id}/{event_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to add event to outbox: {e}", exc_info=True)
            return False
    
    async def get_pending_events(self, execution_id: str) -> List[OutboxEvent]:
        """
        Get pending events for execution.
        
        Args:
            execution_id: Execution identifier
        
        Returns:
            List of pending outbox events
        """
        if not self.event_log:
            raise RuntimeError(
                "TransactionalOutbox was not wired with an event log backend; "
                "platform contract §8A. Composition root must pass get_wal_backend() when building Outbox."
            )
        try:
            stream_name = self._get_stream_name(execution_id)
            
            # Read all events from stream
            events_data = await self.event_log.xrange(
                stream_name,
                start="-",
                end="+",
                count=10000
            )
            
            events = []
            for message_id, fields in events_data:
                try:
                    # Check if published
                    published = fields.get("published", "false").lower() == "true"
                    if published:
                        continue  # Skip published events
                    
                    # Parse event
                    event = OutboxEvent(
                        event_id=fields.get("event_id", message_id),
                        execution_id=execution_id,
                        event_type=fields.get("event_type", "unknown"),
                        event_data=json.loads(fields.get("event_data", "{}")),
                        created_at=datetime.fromisoformat(fields.get("created_at", self.clock.now_utc().isoformat())),
                        published=False
                    )
                    events.append(event)
                except Exception as e:
                    self.logger.warning(f"Failed to parse outbox event: {e}")
                    continue
            
            return events
            
        except Exception as e:
            self.logger.error(f"Failed to get pending events: {e}", exc_info=True)
            return []
    
    async def mark_published(self, execution_id: str, event_id: str) -> bool:
        """
        Mark event as published.
        
        Args:
            execution_id: Execution identifier
            event_id: Event identifier
        
        Returns:
            True if marked successfully
        """
        if not self.event_log:
            raise RuntimeError(
                "TransactionalOutbox was not wired with an event log backend; "
                "platform contract violation. Composition root must pass get_wal_backend() when building Outbox."
            )
        try:
            stream_name = self._get_stream_name(execution_id)
            
            # Read events to find the one to update
            events_data = await self.event_log.xrange(
                stream_name,
                start="-",
                end="+",
                count=10000
            )
            
            for message_id, fields in events_data:
                if fields.get("event_id") == event_id:
                    # Update fields to mark as published
                    updated_fields = fields.copy()
                    updated_fields["published"] = "true"
                    updated_fields["published_at"] = self.clock.now_utc().isoformat()
                    
                    # Add updated event (Redis Streams are append-only, so we add a new entry)
                    # In production, you might want to use a different pattern (e.g., separate published stream)
                    await self.event_log.xadd(
                        stream_name,
                        updated_fields,
                        maxlen=10000
                    )
                    
                    self.logger.debug(f"Event marked as published: {execution_id}/{event_id}")
                    return True
            
            self.logger.warning(f"Event not found in outbox: {execution_id}/{event_id}")
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to mark event as published: {e}", exc_info=True)
            return False
    
    async def publish_events(self, execution_id: str) -> int:
        """
        Publish pending events from outbox.
        
        This is a placeholder - actual publishing will be implemented
        when we have event publishers (e.g., to Kafka, RabbitMQ, etc.).
        
        For now, we just mark events as published.
        
        Args:
            execution_id: Execution identifier
        
        Returns:
            Number of events published
        """
        try:
            pending_events = await self.get_pending_events(execution_id)
            
            if not pending_events:
                self.logger.debug(f"No pending events to publish: {execution_id}")
                return 0
            
            published_count = 0
            
            for event in pending_events:
                # TODO: Actual event publishing (e.g., to Kafka, RabbitMQ, etc.)
                # For now, we just mark as published
                # In Phase 3, we'll implement actual event publishing
                
                self.logger.info(
                    f"Publishing event: {execution_id}/{event.event_id} "
                    f"(type: {event.event_type})"
                )
                
                # Mark as published
                if await self.mark_published(execution_id, event.event_id):
                    published_count += 1
            
            self.logger.info(f"Published {published_count} events for execution: {execution_id}")
            return published_count
            
        except Exception as e:
            self.logger.error(f"Failed to publish events: {e}", exc_info=True)
            return 0
