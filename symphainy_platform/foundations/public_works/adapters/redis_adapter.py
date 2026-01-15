"""
Redis Adapter - Raw Technology Client (Layer 0)

Real Redis client wrapper with no business logic.
This is the raw technology layer for Redis operations.

WHAT (Infrastructure Role): I provide raw Redis client operations
HOW (Infrastructure Implementation): I use real Redis client with no business logic
"""

import json
import logging
from typing import Dict, Any, Optional, List
import redis.asyncio as redis
from redis.asyncio import Redis
from redis.exceptions import RedisError

from utilities import get_logger


class RedisAdapter:
    """
    Raw Redis client wrapper - no business logic.
    
    This adapter provides direct access to Redis operations without
    any business logic or abstraction. It's the raw technology layer.
    """
    
    def __init__(self, host: str, port: int, db: int = 0, password: Optional[str] = None):
        """
        Initialize Redis adapter with real connection.
        
        Args:
            host: Redis host
            port: Redis port
            db: Redis database number
            password: Optional Redis password
        """
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self._client: Optional[Redis] = None
        self.logger = get_logger(self.__class__.__name__)
    
    async def connect(self) -> bool:
        """Connect to Redis."""
        try:
            redis_url = f"redis://{self.host}:{self.port}/{self.db}"
            if self.password:
                redis_url = f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
            
            self._client = await redis.from_url(redis_url, decode_responses=True)
            await self._client.ping()
            self.logger.info(f"Redis adapter connected: {self.host}:{self.port}/{self.db}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to Redis: {e}", exc_info=True)
            return False
    
    async def disconnect(self):
        """Disconnect from Redis."""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    # ============================================================================
    # RAW STRING OPERATIONS
    # ============================================================================
    
    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        """Raw Redis SET operation - no business logic."""
        if not self._client:
            return False
        try:
            if ttl:
                return await self._client.setex(key, ttl, value)
            else:
                return await self._client.set(key, value)
        except RedisError as e:
            self.logger.error(f"Redis SET error: {e}")
            return False
    
    async def get(self, key: str) -> Optional[str]:
        """Raw Redis GET operation - no business logic."""
        if not self._client:
            return None
        try:
            return await self._client.get(key)
        except RedisError as e:
            self.logger.error(f"Redis GET error: {e}")
            return None
    
    async def delete(self, key: str) -> bool:
        """Raw Redis DELETE operation - no business logic."""
        if not self._client:
            return False
        try:
            return await self._client.delete(key) > 0
        except RedisError as e:
            self.logger.error(f"Redis DELETE error: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Raw Redis EXISTS operation - no business logic."""
        if not self._client:
            return False
        try:
            return await self._client.exists(key) > 0
        except RedisError as e:
            self.logger.error(f"Redis EXISTS error: {e}")
            return False
    
    async def expire(self, key: str, ttl: int) -> bool:
        """Raw Redis EXPIRE operation - no business logic."""
        if not self._client:
            return False
        try:
            return await self._client.expire(key, ttl)
        except RedisError as e:
            self.logger.error(f"Redis EXPIRE error: {e}")
            return False
    
    # ============================================================================
    # RAW JSON OPERATIONS (for state storage)
    # ============================================================================
    
    async def set_json(self, key: str, value: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Set JSON value in Redis."""
        return await self.set(key, json.dumps(value), ttl)
    
    async def get_json(self, key: str) -> Optional[Dict[str, Any]]:
        """Get JSON value from Redis."""
        data = await self.get(key)
        if data:
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                return None
        return None
    
    # ============================================================================
    # RAW LIST OPERATIONS (for WAL)
    # ============================================================================
    
    async def lpush(self, key: str, value: str) -> int:
        """Raw Redis LPUSH operation - no business logic."""
        if not self._client:
            return 0
        try:
            return await self._client.lpush(key, value)
        except RedisError as e:
            self.logger.error(f"Redis LPUSH error: {e}")
            return 0
    
    async def lrange(self, key: str, start: int, end: int) -> List[str]:
        """Raw Redis LRANGE operation - no business logic."""
        if not self._client:
            return []
        try:
            return await self._client.lrange(key, start, end)
        except RedisError as e:
            self.logger.error(f"Redis LRANGE error: {e}")
            return []
    
    async def ltrim(self, key: str, start: int, end: int) -> bool:
        """Raw Redis LTRIM operation - no business logic."""
        if not self._client:
            return False
        try:
            return await self._client.ltrim(key, start, end)
        except RedisError as e:
            self.logger.error(f"Redis LTRIM error: {e}")
            return False
    
    # ============================================================================
    # RAW SCAN OPERATIONS (for listing keys)
    # ============================================================================
    
    async def scan_iter(self, match: str, count: int = 100):
        """Raw Redis SCAN iterator - no business logic."""
        if not self._client:
            return
        try:
            async for key in self._client.scan_iter(match=match, count=count):
                yield key
        except RedisError as e:
            self.logger.error(f"Redis SCAN error: {e}")
    
    # ============================================================================
    # RAW STREAM OPERATIONS (for WAL)
    # ============================================================================
    
    async def xadd(
        self,
        stream_name: str,
        fields: Dict[str, str],
        maxlen: Optional[int] = None,
        approximate: bool = True
    ) -> Optional[str]:
        """
        Raw Redis XADD operation - no business logic.
        
        Args:
            stream_name: Stream name
            fields: Dictionary of field-value pairs
            maxlen: Optional maximum length (trims old entries)
            approximate: If True, use approximate trimming (faster)
        
        Returns:
            Message ID if successful, None otherwise
        """
        if not self._client:
            return None
        try:
            if maxlen:
                if approximate:
                    return await self._client.xadd(
                        stream_name,
                        fields,
                        maxlen=maxlen,
                        approximate=True
                    )
                else:
                    return await self._client.xadd(
                        stream_name,
                        fields,
                        maxlen=maxlen,
                        approximate=False
                    )
            else:
                return await self._client.xadd(stream_name, fields)
        except RedisError as e:
            self.logger.error(f"Redis XADD error: {e}")
            return None
    
    async def xread(
        self,
        streams: Dict[str, str],
        count: Optional[int] = None,
        block: Optional[int] = None
    ) -> Dict[str, List[tuple]]:
        """
        Raw Redis XREAD operation - no business logic.
        
        Args:
            streams: Dictionary mapping stream names to last message IDs
                e.g., {"stream1": "0", "stream2": "1234567890-0"}
            count: Optional maximum number of messages per stream
            block: Optional block time in milliseconds (None = non-blocking)
        
        Returns:
            Dictionary mapping stream names to lists of (message_id, fields_dict) tuples
        """
        if not self._client:
            return {}
        try:
            result = await self._client.xread(
                streams,
                count=count,
                block=block
            )
            # Convert result to dict format: {stream: [(id, {fields})]}
            return {stream: [(msg_id, dict(fields)) for msg_id, fields in messages]
                    for stream, messages in result}
        except RedisError as e:
            self.logger.error(f"Redis XREAD error: {e}")
            return {}
    
    async def xgroup_create(
        self,
        stream_name: str,
        group_name: str,
        id: str = "0",
        mkstream: bool = False
    ) -> bool:
        """
        Raw Redis XGROUP CREATE operation - no business logic.
        
        Args:
            stream_name: Stream name
            group_name: Consumer group name
            id: Starting message ID (default "0" = from beginning)
            mkstream: If True, create stream if it doesn't exist
        
        Returns:
            True if group created successfully
        """
        if not self._client:
            return False
        try:
            await self._client.xgroup_create(
                stream_name,
                group_name,
                id=id,
                mkstream=mkstream
            )
            return True
        except RedisError as e:
            # Group might already exist
            if "BUSYGROUP" in str(e):
                self.logger.debug(f"Consumer group already exists: {group_name}")
                return True
            self.logger.error(f"Redis XGROUP CREATE error: {e}")
            return False
    
    async def xreadgroup(
        self,
        group_name: str,
        consumer_name: str,
        streams: Dict[str, str],
        count: Optional[int] = None,
        block: Optional[int] = None,
        noack: bool = False
    ) -> Dict[str, List[tuple]]:
        """
        Raw Redis XREADGROUP operation - no business logic.
        
        Args:
            group_name: Consumer group name
            consumer_name: Consumer name
            streams: Dictionary mapping stream names to message IDs
                Use ">" to read new messages
            count: Optional maximum number of messages per stream
            block: Optional block time in milliseconds (None = non-blocking)
            noack: If True, don't add messages to pending list
        
        Returns:
            Dictionary mapping stream names to lists of (message_id, fields_dict) tuples
        """
        if not self._client:
            return {}
        try:
            result = await self._client.xreadgroup(
                group_name,
                consumer_name,
                streams,
                count=count,
                block=block,
                noack=noack
            )
            # Convert result to dict format: {stream: [(id, {fields})]}
            return {stream: [(msg_id, dict(fields)) for msg_id, fields in messages]
                    for stream, messages in result}
        except RedisError as e:
            self.logger.error(f"Redis XREADGROUP error: {e}")
            return {}
    
    async def xack(
        self,
        stream_name: str,
        group_name: str,
        *message_ids: str
    ) -> int:
        """
        Raw Redis XACK operation - no business logic.
        
        Args:
            stream_name: Stream name
            group_name: Consumer group name
            *message_ids: Message IDs to acknowledge
        
        Returns:
            Number of messages acknowledged
        """
        if not self._client:
            return 0
        try:
            return await self._client.xack(stream_name, group_name, *message_ids)
        except RedisError as e:
            self.logger.error(f"Redis XACK error: {e}")
            return 0
    
    async def xrange(
        self,
        stream_name: str,
        start: str = "-",
        end: str = "+",
        count: Optional[int] = None
    ) -> List[tuple]:
        """
        Raw Redis XRANGE operation - no business logic.
        
        Args:
            stream_name: Stream name
            start: Start message ID ("-" = beginning)
            end: End message ID ("+" = end)
            count: Optional maximum number of messages
        
        Returns:
            List of (message_id, fields_dict) tuples
        """
        if not self._client:
            return []
        try:
            result = await self._client.xrange(
                stream_name,
                min=start,
                max=end,
                count=count
            )
            return [(msg_id, dict(fields)) for msg_id, fields in result]
        except RedisError as e:
            self.logger.error(f"Redis XRANGE error: {e}")
            return []