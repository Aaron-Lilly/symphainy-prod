"""
Write-Ahead Log (WAL) - Append-Only Event Log

Enables:
- Audit
- Replay
- Recovery
- Deterministic debugging

Uses Redis Streams for scalability (supports 350k+ policies).
"""

import json
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from datetime import datetime, date
from enum import Enum

from utilities import generate_event_id, get_clock, get_logger
from symphainy_platform.foundations.public_works.adapters.redis_adapter import RedisAdapter


class WALEventType(str, Enum):
    """WAL event types."""
    SESSION_CREATED = "session_created"
    INTENT_RECEIVED = "intent_received"
    SAGA_STARTED = "saga_started"
    STEP_COMPLETED = "step_completed"
    STEP_FAILED = "step_failed"
    EXECUTION_STARTED = "execution_started"
    EXECUTION_COMPLETED = "execution_completed"
    EXECUTION_FAILED = "execution_failed"


@dataclass
class WALEvent:
    """WAL event structure."""
    event_id: str
    event_type: WALEventType
    tenant_id: str
    timestamp: datetime
    payload: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "tenant_id": self.tenant_id,
            "timestamp": self.timestamp.isoformat(),
            "payload": self.payload,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WALEvent":
        """Create event from dictionary."""
        return cls(
            event_id=data["event_id"],
            event_type=WALEventType(data["event_type"]),
            tenant_id=data["tenant_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            payload=data["payload"],
        )
    
    def to_stream_fields(self) -> Dict[str, str]:
        """Convert event to Redis Stream fields format."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "tenant_id": self.tenant_id,
            "timestamp": self.timestamp.isoformat(),
            "payload": json.dumps(self.payload),
        }
    
    @classmethod
    def from_stream_fields(cls, fields: Dict[str, str], message_id: str) -> "WALEvent":
        """Create event from Redis Stream fields."""
        return cls(
            event_id=fields.get("event_id", message_id),
            event_type=WALEventType(fields["event_type"]),
            tenant_id=fields["tenant_id"],
            timestamp=datetime.fromisoformat(fields["timestamp"]),
            payload=json.loads(fields.get("payload", "{}")),
        )


class WriteAheadLog:
    """
    Append-only log for audit, replay, and recovery.
    
    Uses Redis Streams for scalability (supports 350k+ policies).
    Partitions by tenant + date for efficient querying and retention.
    """
    
    def __init__(
        self,
        redis_adapter: Optional[RedisAdapter] = None,
        use_memory: bool = False,
        max_events_per_partition: int = 100000
    ):
        """
        Initialize WAL.
        
        Args:
            redis_adapter: Optional Redis adapter (uses Streams)
            use_memory: If True, use in-memory storage (for tests)
            max_events_per_partition: Maximum events per partition (for retention)
        """
        self.use_memory = use_memory
        self.redis_adapter = redis_adapter
        self.max_events_per_partition = max_events_per_partition
        self._memory_log: List[WALEvent] = []
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
    
    def _get_stream_name(self, tenant_id: str, event_date: Optional[date] = None) -> str:
        """
        Get stream name for tenant and date.
        
        Partitions by tenant + date for scalability.
        
        Args:
            tenant_id: Tenant identifier
            event_date: Optional date (defaults to today)
        
        Returns:
            Stream name (e.g., "wal:tenant_1:2026-01-15")
        """
        if event_date is None:
            event_date = self.clock.now().date()
        return f"wal:{tenant_id}:{event_date.isoformat()}"
    
    async def append(
        self,
        event_type: WALEventType,
        tenant_id: str,
        payload: Dict[str, Any]
    ) -> WALEvent:
        """
        Append event to WAL.
        
        Args:
            event_type: Event type
            tenant_id: Tenant identifier (for isolation)
            payload: Event payload
        
        Returns:
            Created WAL event
        """
        event = WALEvent(
            event_id=generate_event_id(),
            event_type=event_type,
            tenant_id=tenant_id,
            timestamp=self.clock.now_utc(),
            payload=payload
        )
        
        if self.use_memory:
            self._memory_log.append(event)
            return event
        
        if not self.redis_adapter:
            # Fallback to memory if Redis not available
            self._memory_log.append(event)
            return event
        
        try:
            # Get stream name (partitioned by tenant + date)
            stream_name = self._get_stream_name(tenant_id)
            
            # Convert event to stream fields
            fields = event.to_stream_fields()
            
            # Add to stream with automatic retention
            message_id = await self.redis_adapter.xadd(
                stream_name,
                fields,
                maxlen=self.max_events_per_partition,
                approximate=True  # Faster trimming
            )
            
            if message_id:
                self.logger.debug(f"WAL event appended: {stream_name}/{message_id}")
            else:
                self.logger.warning(f"Failed to append WAL event to stream: {stream_name}")
                # Fallback to memory
                self._memory_log.append(event)
            
            return event
        except Exception as e:
            self.logger.error(f"Failed to append WAL event: {e}", exc_info=True)
            # Fallback to memory on error
            self._memory_log.append(event)
            return event
    
    async def get_events(
        self,
        tenant_id: str,
        event_type: Optional[WALEventType] = None,
        limit: int = 100,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[WALEvent]:
        """
        Get events for tenant.
        
        Args:
            tenant_id: Tenant identifier
            event_type: Optional event type filter
            limit: Maximum number of events to return
            start_date: Optional start date (defaults to today)
            end_date: Optional end date (defaults to today)
        
        Returns:
            List of WAL events (most recent first)
        """
        if self.use_memory:
            events = [
                e for e in self._memory_log
                if e.tenant_id == tenant_id
                and (event_type is None or e.event_type == event_type)
            ]
            return sorted(events, key=lambda e: e.timestamp, reverse=True)[:limit]
        
        if not self.redis_adapter:
            return []
        
        try:
            # Determine date range
            if start_date is None:
                start_date = self.clock.now().date()
            if end_date is None:
                end_date = start_date
            
            # Collect events from all partitions in date range
            all_events: List[WALEvent] = []
            current_date = start_date
            
            while current_date <= end_date:
                stream_name = self._get_stream_name(tenant_id, current_date)
                
                # Read from end (most recent first)
                stream_events = await self.redis_adapter.xrange(
                    stream_name,
                    start="-",
                    end="+",
                    count=limit * 2  # Get more to filter by type
                )
                
                # Convert to WALEvent objects
                for message_id, fields in stream_events:
                    try:
                        event = WALEvent.from_stream_fields(fields, message_id)
                        if event_type is None or event.event_type == event_type:
                            all_events.append(event)
                    except Exception as e:
                        self.logger.warning(f"Failed to parse WAL event: {e}")
                        continue
                
                # Move to next date
                from datetime import timedelta
                current_date += timedelta(days=1)
            
            # Sort by timestamp (most recent first) and limit
            all_events.sort(key=lambda e: e.timestamp, reverse=True)
            return all_events[:limit]
            
        except Exception as e:
            self.logger.error(f"Failed to get WAL events: {e}", exc_info=True)
            return []
    
    async def get_session_events(
        self,
        session_id: str,
        tenant_id: str
    ) -> List[WALEvent]:
        """
        Get all events for a session.
        
        Args:
            session_id: Session identifier
            tenant_id: Tenant identifier
        
        Returns:
            List of WAL events for session
        """
        # Get events from last 30 days (sessions shouldn't span longer)
        from datetime import timedelta
        end_date = self.clock.now().date()
        start_date = end_date - timedelta(days=30)
        
        all_events = await self.get_events(
            tenant_id,
            limit=100000,  # Large limit for session replay
            start_date=start_date,
            end_date=end_date
        )
        
        return [
            e for e in all_events
            if e.payload.get("session_id") == session_id
        ]
    
    async def replay_session(
        self,
        session_id: str,
        tenant_id: str
    ) -> List[WALEvent]:
        """
        Replay all events for a session (chronological order).
        
        Args:
            session_id: Session identifier
            tenant_id: Tenant identifier
        
        Returns:
            List of WAL events in chronological order
        """
        events = await self.get_session_events(session_id, tenant_id)
        return sorted(events, key=lambda e: e.timestamp)
    
    async def create_consumer_group(
        self,
        tenant_id: str,
        group_name: str,
        stream_date: Optional[date] = None
    ) -> bool:
        """
        Create consumer group for stream replay.
        
        Args:
            tenant_id: Tenant identifier
            group_name: Consumer group name
            stream_date: Optional date (defaults to today)
        
        Returns:
            True if group created successfully
        """
        if not self.redis_adapter:
            return False
        
        try:
            stream_name = self._get_stream_name(tenant_id, stream_date)
            return await self.redis_adapter.xgroup_create(
                stream_name,
                group_name,
                id="0",  # Start from beginning
                mkstream=True  # Create stream if it doesn't exist
            )
        except Exception as e:
            self.logger.error(f"Failed to create consumer group: {e}")
            return False
    
    async def read_from_group(
        self,
        tenant_id: str,
        group_name: str,
        consumer_name: str,
        stream_date: Optional[date] = None,
        count: Optional[int] = None,
        block: Optional[int] = None
    ) -> List[WALEvent]:
        """
        Read events from consumer group (for parallel replay).
        
        Args:
            tenant_id: Tenant identifier
            group_name: Consumer group name
            consumer_name: Consumer name
            stream_date: Optional date (defaults to today)
            count: Optional maximum number of messages
            block: Optional block time in milliseconds
        
        Returns:
            List of WAL events
        """
        if not self.redis_adapter:
            return []
        
        try:
            stream_name = self._get_stream_name(tenant_id, stream_date)
            streams = {stream_name: ">"}  # Read new messages
            
            result = await self.redis_adapter.xreadgroup(
                group_name,
                consumer_name,
                streams,
                count=count,
                block=block
            )
            
            # Convert to WALEvent objects
            events: List[WALEvent] = []
            for stream, messages in result.items():
                for message_id, fields in messages:
                    try:
                        event = WALEvent.from_stream_fields(fields, message_id)
                        events.append(event)
                    except Exception as e:
                        self.logger.warning(f"Failed to parse WAL event: {e}")
                        continue
            
            return events
        except Exception as e:
            self.logger.error(f"Failed to read from consumer group: {e}")
            return []
    
    async def acknowledge(
        self,
        tenant_id: str,
        group_name: str,
        stream_date: Optional[date],
        *message_ids: str
    ) -> int:
        """
        Acknowledge processed messages.
        
        Args:
            tenant_id: Tenant identifier
            group_name: Consumer group name
            stream_date: Stream date
            *message_ids: Message IDs to acknowledge
        
        Returns:
            Number of messages acknowledged
        """
        if not self.redis_adapter:
            return 0
        
        try:
            stream_name = self._get_stream_name(tenant_id, stream_date)
            return await self.redis_adapter.xack(stream_name, group_name, *message_ids)
        except Exception as e:
            self.logger.error(f"Failed to acknowledge messages: {e}")
            return 0
