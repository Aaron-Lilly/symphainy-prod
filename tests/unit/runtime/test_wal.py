"""
Unit tests for Write-Ahead Log (WAL).
"""

import pytest
from symphainy_platform.runtime.wal import WriteAheadLog, WALEventType, WALEvent


@pytest.mark.unit
@pytest.mark.runtime
class TestWriteAheadLog:
    """Test Write-Ahead Log."""
    
    @pytest.mark.asyncio
    async def test_append_event_memory(self):
        """Test appending event to WAL (in-memory)."""
        wal = WriteAheadLog(use_memory=True)
        
        event = await wal.append(
            event_type=WALEventType.SESSION_CREATED,
            tenant_id="tenant_123",
            payload={"session_id": "session_123"}
        )
        
        assert event.event_type == WALEventType.SESSION_CREATED
        assert event.tenant_id == "tenant_123"
        assert event.payload["session_id"] == "session_123"
        assert event.event_id is not None
        assert event.timestamp is not None
    
    @pytest.mark.asyncio
    async def test_get_events_memory(self):
        """Test getting events from WAL (in-memory)."""
        wal = WriteAheadLog(use_memory=True)
        
        tenant_id = "tenant_123"
        
        # Append multiple events
        await wal.append(
            WALEventType.SESSION_CREATED,
            tenant_id,
            {"session_id": "session_1"}
        )
        await wal.append(
            WALEventType.INTENT_RECEIVED,
            tenant_id,
            {"intent_type": "content.upload"}
        )
        
        # Get all events
        events = await wal.get_events(tenant_id)
        assert len(events) == 2
        assert events[0].event_type == WALEventType.INTENT_RECEIVED  # Most recent first
        assert events[1].event_type == WALEventType.SESSION_CREATED
    
    @pytest.mark.asyncio
    async def test_get_events_filtered(self):
        """Test getting filtered events from WAL."""
        wal = WriteAheadLog(use_memory=True)
        
        tenant_id = "tenant_123"
        
        # Append different event types
        await wal.append(WALEventType.SESSION_CREATED, tenant_id, {})
        await wal.append(WALEventType.INTENT_RECEIVED, tenant_id, {})
        await wal.append(WALEventType.SESSION_CREATED, tenant_id, {})
        
        # Get only SESSION_CREATED events
        events = await wal.get_events(tenant_id, event_type=WALEventType.SESSION_CREATED)
        assert len(events) == 2
        assert all(e.event_type == WALEventType.SESSION_CREATED for e in events)
    
    @pytest.mark.asyncio
    async def test_get_session_events(self):
        """Test getting events for a session."""
        wal = WriteAheadLog(use_memory=True)
        
        tenant_id = "tenant_123"
        session_id = "session_123"
        
        # Append events for different sessions
        await wal.append(
            WALEventType.SESSION_CREATED,
            tenant_id,
            {"session_id": session_id}
        )
        await wal.append(
            WALEventType.INTENT_RECEIVED,
            tenant_id,
            {"session_id": session_id, "intent_type": "content.upload"}
        )
        await wal.append(
            WALEventType.SESSION_CREATED,
            tenant_id,
            {"session_id": "other_session"}
        )
        
        # Get events for session
        events = await wal.get_session_events(session_id, tenant_id)
        assert len(events) == 2
        assert all(e.payload["session_id"] == session_id for e in events)
    
    @pytest.mark.asyncio
    async def test_replay_session(self):
        """Test replaying session events in chronological order."""
        wal = WriteAheadLog(use_memory=True)
        
        tenant_id = "tenant_123"
        session_id = "session_123"
        
        # Append events
        event1 = await wal.append(
            WALEventType.SESSION_CREATED,
            tenant_id,
            {"session_id": session_id}
        )
        event2 = await wal.append(
            WALEventType.INTENT_RECEIVED,
            tenant_id,
            {"session_id": session_id}
        )
        
        # Replay (should be chronological)
        events = await wal.replay_session(session_id, tenant_id)
        assert len(events) == 2
        assert events[0].event_type == WALEventType.SESSION_CREATED
        assert events[1].event_type == WALEventType.INTENT_RECEIVED
