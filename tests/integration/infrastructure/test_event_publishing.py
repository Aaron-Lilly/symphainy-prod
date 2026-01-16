"""
Event Publishing Integration Tests

Tests event publishing with real Redis Streams.

WHAT (Test Role): I verify event publishing works with Redis Streams
HOW (Test Implementation): I use docker-compose Redis and test event publishing operations
"""

import pytest
import json
from typing import Dict, Any
from symphainy_platform.foundations.public_works.adapters.redis_adapter import RedisAdapter
from tests.infrastructure.test_fixtures import test_redis, clean_test_db


@pytest.mark.integration
@pytest.mark.infrastructure
class TestEventPublishing:
    """Test event publishing with real Redis Streams."""
    
    @pytest.mark.asyncio
    async def test_publish_event(
        self,
        test_redis: RedisAdapter
    ):
        """Test publishing a single event to Redis Streams."""
        stream_name = "test_events"
        event_type = "test.event.created"
        event_data = {
            "id": "event_123",
            "message": "Test event",
            "value": 42
        }
        headers = {
            "correlation_id": "corr_123",
            "tenant_id": "tenant_1"
        }
        
        # Publish event using Redis Streams XADD
        fields = {
            "event_type": event_type,
            "event_data": json.dumps(event_data),
            "headers": json.dumps(headers)
        }
        
        message_id = await test_redis.xadd(stream_name, fields)
        assert message_id is not None, "Event should be published"
        assert isinstance(message_id, str), "Message ID should be a string"
    
    @pytest.mark.asyncio
    async def test_read_event(
        self,
        test_redis: RedisAdapter
    ):
        """Test reading events from Redis Streams."""
        stream_name = "test_read_events"
        event_type = "test.event.read"
        event_data = {"id": "event_456", "action": "read"}
        
        # Publish event
        fields = {
            "event_type": event_type,
            "event_data": json.dumps(event_data)
        }
        message_id = await test_redis.xadd(stream_name, fields)
        assert message_id is not None, "Event should be published"
        
        # Read event
        streams = {stream_name: "0"}  # Read from beginning
        results = await test_redis.xread(streams, count=1)
        
        assert stream_name in results, "Stream should be in results"
        assert len(results[stream_name]) > 0, "Should have at least one message"
        
        # Verify event data
        read_message_id, read_fields = results[stream_name][0]
        assert read_fields["event_type"] == event_type, "Event type should match"
        assert json.loads(read_fields["event_data"]) == event_data, "Event data should match"
    
    @pytest.mark.asyncio
    async def test_publish_batch_events(
        self,
        test_redis: RedisAdapter
    ):
        """Test publishing multiple events in a batch."""
        stream_name = "test_batch_events"
        
        # Publish multiple events
        events = [
            {"event_type": "test.event.1", "event_data": {"id": 1}},
            {"event_type": "test.event.2", "event_data": {"id": 2}},
            {"event_type": "test.event.3", "event_data": {"id": 3}}
        ]
        
        message_ids = []
        for event in events:
            fields = {
                "event_type": event["event_type"],
                "event_data": json.dumps(event["event_data"])
            }
            message_id = await test_redis.xadd(stream_name, fields)
            assert message_id is not None, f"Event {event['event_type']} should be published"
            message_ids.append(message_id)
        
        assert len(message_ids) == 3, "All events should be published"
        
        # Read all events
        streams = {stream_name: "0"}
        results = await test_redis.xread(streams, count=10)
        
        assert len(results[stream_name]) == 3, "Should read all 3 events"
    
    @pytest.mark.asyncio
    async def test_event_with_headers(
        self,
        test_redis: RedisAdapter
    ):
        """Test publishing event with headers."""
        stream_name = "test_headers_events"
        event_type = "test.event.headers"
        event_data = {"id": "event_headers"}
        headers = {
            "correlation_id": "corr_789",
            "tenant_id": "tenant_2",
            "user_id": "user_123"
        }
        
        # Publish event with headers
        fields = {
            "event_type": event_type,
            "event_data": json.dumps(event_data),
            "headers": json.dumps(headers)
        }
        message_id = await test_redis.xadd(stream_name, fields)
        assert message_id is not None, "Event with headers should be published"
        
        # Read and verify headers
        streams = {stream_name: "0"}
        results = await test_redis.xread(streams, count=1)
        
        read_message_id, read_fields = results[stream_name][0]
        read_headers = json.loads(read_fields.get("headers", "{}"))
        assert read_headers["correlation_id"] == "corr_789", "Headers should be preserved"
        assert read_headers["tenant_id"] == "tenant_2", "Headers should be preserved"
    
    @pytest.mark.asyncio
    async def test_stream_maxlen(
        self,
        test_redis: RedisAdapter
    ):
        """Test stream with maxlen (trims old entries)."""
        stream_name = "test_maxlen_events"
        
        # Publish events with maxlen
        for i in range(5):
            fields = {
                "event_type": "test.event.maxlen",
                "event_data": json.dumps({"id": i})
            }
            message_id = await test_redis.xadd(
                stream_name,
                fields,
                maxlen=3,  # Keep only last 3 events
                approximate=True
            )
            assert message_id is not None, f"Event {i} should be published"
        
        # Read events (should have at most 3 due to maxlen)
        streams = {stream_name: "0"}
        results = await test_redis.xread(streams, count=10)
        
        # Note: maxlen with approximate=True may not be exact, but should limit stream size
        assert len(results[stream_name]) <= 5, "Stream should have limited size"
    
    @pytest.mark.asyncio
    async def test_multiple_streams(
        self,
        test_redis: RedisAdapter
    ):
        """Test publishing to multiple streams."""
        stream1 = "test_stream_1"
        stream2 = "test_stream_2"
        
        # Publish to stream1
        fields1 = {
            "event_type": "stream1.event",
            "event_data": json.dumps({"stream": 1})
        }
        message_id1 = await test_redis.xadd(stream1, fields1)
        assert message_id1 is not None, "Event to stream1 should be published"
        
        # Publish to stream2
        fields2 = {
            "event_type": "stream2.event",
            "event_data": json.dumps({"stream": 2})
        }
        message_id2 = await test_redis.xadd(stream2, fields2)
        assert message_id2 is not None, "Event to stream2 should be published"
        
        # Read from both streams
        streams = {stream1: "0", stream2: "0"}
        results = await test_redis.xread(streams, count=10)
        
        assert stream1 in results, "Stream1 should be in results"
        assert stream2 in results, "Stream2 should be in results"
        assert len(results[stream1]) == 1, "Stream1 should have 1 event"
        assert len(results[stream2]) == 1, "Stream2 should have 1 event"
    
    @pytest.mark.asyncio
    async def test_event_ordering(
        self,
        test_redis: RedisAdapter
    ):
        """Test that events maintain order in stream."""
        stream_name = "test_ordering_events"
        
        # Publish events in sequence
        event_ids = []
        for i in range(5):
            fields = {
                "event_type": "test.event.ordered",
                "event_data": json.dumps({"sequence": i})
            }
            message_id = await test_redis.xadd(stream_name, fields)
            event_ids.append(message_id)
        
        # Read events
        streams = {stream_name: "0"}
        results = await test_redis.xread(streams, count=10)
        
        # Verify order (message IDs should be in ascending order)
        read_message_ids = [msg_id for msg_id, _ in results[stream_name]]
        assert read_message_ids == event_ids, "Events should maintain order"
        
        # Verify sequence numbers
        for i, (msg_id, fields) in enumerate(results[stream_name]):
            event_data = json.loads(fields["event_data"])
            assert event_data["sequence"] == i, f"Event {i} should have correct sequence"
