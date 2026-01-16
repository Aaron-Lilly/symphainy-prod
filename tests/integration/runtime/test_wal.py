"""
Write-Ahead Log (WAL) Integration Tests

Tests WAL with real Redis Streams.

WHAT (Test Role): I verify WAL append-only event logging works
HOW (Test Implementation): I use docker-compose Redis and test WAL operations
"""

import pytest
from typing import Dict, Any
from symphainy_platform.foundations.public_works.adapters.redis_adapter import RedisAdapter
from symphainy_platform.runtime.wal import WriteAheadLog, WALEventType, WALEvent
from tests.infrastructure.test_fixtures import test_redis, clean_test_db
from datetime import datetime


@pytest.mark.integration
@pytest.mark.infrastructure
@pytest.mark.runtime
class TestWriteAheadLog:
    """Test WriteAheadLog with real Redis Streams."""
    
    @pytest.fixture
    def wal(
        self,
        test_redis: RedisAdapter
    ) -> WriteAheadLog:
        """Create WriteAheadLog with real Redis adapter."""
        return WriteAheadLog(redis_adapter=test_redis)
    
    @pytest.mark.asyncio
    async def test_append_event(
        self,
        wal: WriteAheadLog
    ):
        """Test appending event to WAL."""
        tenant_id = "tenant_wal_1"
        event_type = WALEventType.SESSION_CREATED
        payload = {
            "session_id": "session_123",
            "user_id": "user_456"
        }
        
        event = await wal.append(event_type, tenant_id, payload)
        assert event is not None, "Event should be appended to WAL"
        assert event.event_type == event_type, "Event type should match"
    
    @pytest.mark.asyncio
    async def test_read_events(
        self,
        wal: WriteAheadLog
    ):
        """Test reading events from WAL."""
        tenant_id = "tenant_wal_read"
        
        # Append multiple events
        await wal.append(WALEventType.SESSION_CREATED, tenant_id, {"session_id": "session_1"})
        await wal.append(WALEventType.INTENT_RECEIVED, tenant_id, {"intent_id": "intent_1"})
        await wal.append(WALEventType.EXECUTION_STARTED, tenant_id, {"execution_id": "exec_1"})
        
        # Read events
        events = await wal.get_events(tenant_id, limit=10)
        assert len(events) >= 3, "Should read at least 3 events"
        
        # Verify event types
        event_types = [e.event_type for e in events]
        assert WALEventType.SESSION_CREATED in event_types, "Should include SESSION_CREATED"
        assert WALEventType.INTENT_RECEIVED in event_types, "Should include INTENT_RECEIVED"
        assert WALEventType.EXECUTION_STARTED in event_types, "Should include EXECUTION_STARTED"
    
    @pytest.mark.asyncio
    async def test_event_ordering(
        self,
        wal: WriteAheadLog
    ):
        """Test that events maintain chronological order."""
        tenant_id = "tenant_wal_order"
        
        # Append events in sequence
        for i in range(5):
            await wal.append(
                WALEventType.STEP_COMPLETED,
                tenant_id,
                {"step": i, "sequence": i}
            )
        
        # Read events
        events = await wal.get_events(tenant_id, limit=10)
        assert len(events) >= 5, "Should read at least 5 events"
        
        # Verify order (events are returned in reverse chronological order - most recent first)
        timestamps = [e.timestamp for e in events]
        assert timestamps == sorted(timestamps, reverse=True), "Events should be in reverse chronological order (most recent first)"
        
        # Verify sequence numbers (need to reverse since events are most recent first)
        step_events = [e for e in events if e.event_type == WALEventType.STEP_COMPLETED]
        # Reverse to get chronological order for sequence verification
        step_events_chronological = sorted(step_events, key=lambda e: e.timestamp)
        for i, event in enumerate(step_events_chronological[:5]):
            assert event.payload.get("sequence") == i, f"Event {i} should have correct sequence"
    
    @pytest.mark.asyncio
    async def test_read_events_by_type(
        self,
        wal: WriteAheadLog
    ):
        """Test reading events filtered by type."""
        tenant_id = "tenant_wal_filter"
        
        # Append different event types
        await wal.append(WALEventType.SESSION_CREATED, tenant_id, {"session_id": "session_filter"})
        await wal.append(WALEventType.INTENT_RECEIVED, tenant_id, {"intent_id": "intent_filter"})
        await wal.append(WALEventType.SESSION_CREATED, tenant_id, {"session_id": "session_filter_2"})
        
        # Read only SESSION_CREATED events
        events = await wal.get_events(tenant_id, event_type=WALEventType.SESSION_CREATED, limit=10)
        assert len(events) >= 2, "Should read at least 2 SESSION_CREATED events"
        assert all(e.event_type == WALEventType.SESSION_CREATED for e in events), "All events should be SESSION_CREATED"
    
    @pytest.mark.asyncio
    async def test_read_events_by_date_range(
        self,
        wal: WriteAheadLog
    ):
        """Test reading events within date range."""
        tenant_id = "tenant_wal_date"
        
        # Append events
        await wal.append(WALEventType.SESSION_CREATED, tenant_id, {"session_id": "session_date"})
        
        # Read events for today
        from datetime import date
        today = date.today()
        events = await wal.get_events(
            tenant_id,
            start_date=today,
            end_date=today,
            limit=10
        )
        
        assert len(events) >= 1, "Should read at least 1 event for today"
        assert all(e.timestamp.date() == today for e in events), "All events should be from today"
    
    @pytest.mark.asyncio
    async def test_tenant_isolation(
        self,
        wal: WriteAheadLog
    ):
        """Test that WAL events are isolated by tenant."""
        tenant1 = "tenant_wal_isolate_1"
        tenant2 = "tenant_wal_isolate_2"
        
        # Append events to different tenants
        await wal.append(WALEventType.SESSION_CREATED, tenant1, {"session_id": "session_tenant1"})
        await wal.append(WALEventType.SESSION_CREATED, tenant2, {"session_id": "session_tenant2"})
        
        # Read events for each tenant
        events1 = await wal.get_events(tenant1, limit=10)
        events2 = await wal.get_events(tenant2, limit=10)
        
        assert len(events1) >= 1, "Tenant1 should have at least 1 event"
        assert len(events2) >= 1, "Tenant2 should have at least 1 event"
        
        # Verify isolation
        session_ids_1 = [e.payload.get("session_id") for e in events1 if e.payload.get("session_id")]
        session_ids_2 = [e.payload.get("session_id") for e in events2 if e.payload.get("session_id")]
        
        assert "session_tenant1" in session_ids_1, "Tenant1 should have its own events"
        assert "session_tenant2" in session_ids_2, "Tenant2 should have its own events"
        assert "session_tenant1" not in session_ids_2, "Tenant2 should not have tenant1 events"
        assert "session_tenant2" not in session_ids_1, "Tenant1 should not have tenant2 events"
    
    @pytest.mark.asyncio
    async def test_event_payload_preservation(
        self,
        wal: WriteAheadLog
    ):
        """Test that event payloads are preserved correctly."""
        tenant_id = "tenant_wal_payload"
        payload = {
            "string": "value",
            "number": 42,
            "boolean": True,
            "nested": {
                "key": "nested_value",
                "array": [1, 2, 3]
            }
        }
        
        # Append event with complex payload
        await wal.append(WALEventType.EXECUTION_COMPLETED, tenant_id, payload)
        
        # Read event
        events = await wal.get_events(tenant_id, limit=1)
        assert len(events) == 1, "Should read 1 event"
        
        # Verify payload preservation
        retrieved_payload = events[0].payload
        assert retrieved_payload["string"] == "value", "String should be preserved"
        assert retrieved_payload["number"] == 42, "Number should be preserved"
        assert retrieved_payload["boolean"] is True, "Boolean should be preserved"
        assert retrieved_payload["nested"]["key"] == "nested_value", "Nested data should be preserved"
        assert retrieved_payload["nested"]["array"] == [1, 2, 3], "Array should be preserved"
    
    @pytest.mark.asyncio
    async def test_all_event_types(
        self,
        wal: WriteAheadLog
    ):
        """Test appending all WAL event types."""
        tenant_id = "tenant_wal_all_types"
        
        # Append all event types
        event_types = [
            WALEventType.SESSION_CREATED,
            WALEventType.INTENT_RECEIVED,
            WALEventType.SAGA_STARTED,
            WALEventType.STEP_COMPLETED,
            WALEventType.STEP_FAILED,
            WALEventType.EXECUTION_STARTED,
            WALEventType.EXECUTION_COMPLETED,
            WALEventType.EXECUTION_FAILED
        ]
        
        for event_type in event_types:
            success = await wal.append(event_type, tenant_id, {"test": event_type.value})
            assert success, f"Event type {event_type.value} should be appended"
        
        # Read all events
        events = await wal.get_events(tenant_id, limit=20)
        assert len(events) >= len(event_types), f"Should read at least {len(event_types)} events"
        
        # Verify all event types are present
        read_event_types = {e.event_type for e in events}
        for event_type in event_types:
            assert event_type in read_event_types, f"Event type {event_type.value} should be present"
    
    @pytest.mark.asyncio
    async def test_empty_wal(
        self,
        wal: WriteAheadLog
    ):
        """Test operations on empty WAL."""
        tenant_id = "tenant_wal_empty"
        
        # Read from empty WAL
        events = await wal.get_events(tenant_id, limit=10)
        assert len(events) == 0, "Empty WAL should return no events"
