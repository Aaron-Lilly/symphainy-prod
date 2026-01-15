"""
Write-Ahead Log (WAL) - Append-Only Event Log

Enables:
- Audit
- Replay
- Recovery
- Deterministic debugging
"""

import json
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
from uuid import uuid4
import redis.asyncio as redis
from redis.asyncio import Redis

from utilities import get_logger, generate_event_id, get_clock


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


class WriteAheadLog:
    """
    Append-only log for audit, replay, and recovery.
    
    Stores events in Redis (or memory for tests) with tenant isolation.
    """
    
    def __init__(
        self,
        redis_client: Optional[Redis] = None,
        use_memory: bool = False
    ):
        """
        Initialize WAL.
        
        Args:
            redis_client: Optional Redis client
            use_memory: If True, use in-memory storage (for tests)
        """
        self.use_memory = use_memory
        self.redis_client = redis_client
        self._memory_log: List[WALEvent] = []
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
    
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
        
        if not self.redis_client:
            # Fallback to memory if Redis not available
            self._memory_log.append(event)
            return event
        
        try:
            # Store in Redis list (append-only)
            key = f"wal:{tenant_id}"
            await self.redis_client.lpush(
                key,
                json.dumps(event.to_dict())
            )
            # Keep last 10000 events per tenant
            await self.redis_client.ltrim(key, 0, 9999)
        except Exception:
            # Fallback to memory on error
            self._memory_log.append(event)
        
        return event
    
    async def get_events(
        self,
        tenant_id: str,
        event_type: Optional[WALEventType] = None,
        limit: int = 100
    ) -> List[WALEvent]:
        """
        Get events for tenant.
        
        Args:
            tenant_id: Tenant identifier
            event_type: Optional event type filter
            limit: Maximum number of events to return
        
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
        
        if not self.redis_client:
            return []
        
        try:
            key = f"wal:{tenant_id}"
            data_list = await self.redis_client.lrange(key, 0, limit - 1)
            
            events = []
            for data in data_list:
                try:
                    event_dict = json.loads(data)
                    event = WALEvent.from_dict(event_dict)
                    if event_type is None or event.event_type == event_type:
                        events.append(event)
                except Exception:
                    continue
            
            return events
        except Exception:
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
        all_events = await self.get_events(tenant_id, limit=10000)
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
