"""
Redis Streams Event Log Backend - EventLogProtocol implementation

Wraps RedisAdapter to implement EventLogProtocol. Used by WAL, TransactionalOutbox, and PostOfficeSDK.
Lives inside Public Works; callers outside Public Works receive only EventLogProtocol.
"""

from typing import Dict, List, Optional, Tuple

from ..adapters.redis_adapter import RedisAdapter


class RedisStreamsEventLogBackend:
    """
    EventLogProtocol implementation using Redis Streams.

    Wraps RedisAdapter; all Redis Streams operations are delegated to the adapter.
    Created by foundation_service when Redis is available; exposed via get_wal_backend().
    """

    def __init__(self, redis_adapter: RedisAdapter):
        """
        Initialize backend with Redis adapter.

        Args:
            redis_adapter: Redis adapter (Layer 0); must not escape Public Works.
        """
        self._redis = redis_adapter

    async def xadd(
        self,
        stream_name: str,
        fields: Dict[str, str],
        maxlen: Optional[int] = None,
        approximate: bool = True
    ) -> Optional[str]:
        """Append entry to stream. Delegates to RedisAdapter."""
        return await self._redis.xadd(
            stream_name,
            fields,
            maxlen=maxlen,
            approximate=approximate
        )

    async def xrange(
        self,
        stream_name: str,
        start: str = "-",
        end: str = "+",
        count: Optional[int] = None
    ) -> List[Tuple[str, Dict[str, str]]]:
        """Read range from stream. Delegates to RedisAdapter."""
        result = await self._redis.xrange(
            stream_name,
            start=start,
            end=end,
            count=count
        )
        return [(msg_id, dict(fields)) for msg_id, fields in result]

    async def xgroup_create(
        self,
        stream_name: str,
        group_name: str,
        id: str = "0",
        mkstream: bool = False
    ) -> bool:
        """Create consumer group. Delegates to RedisAdapter."""
        return await self._redis.xgroup_create(
            stream_name,
            group_name,
            id=id,
            mkstream=mkstream
        )

    async def xreadgroup(
        self,
        group_name: str,
        consumer_name: str,
        streams: Dict[str, str],
        count: Optional[int] = None,
        block: Optional[int] = None
    ) -> Dict[str, List[Tuple[str, Dict[str, str]]]]:
        """Read from consumer group. Delegates to RedisAdapter."""
        result = await self._redis.xreadgroup(
            group_name,
            consumer_name,
            streams,
            count=count,
            block=block
        )
        return {
            stream: [(msg_id, dict(fields)) for msg_id, fields in messages]
            for stream, messages in result.items()
        }

    async def xack(
        self,
        stream_name: str,
        group_name: str,
        *message_ids: str
    ) -> int:
        """Acknowledge messages. Delegates to RedisAdapter."""
        return await self._redis.xack(
            stream_name,
            group_name,
            *message_ids
        )
