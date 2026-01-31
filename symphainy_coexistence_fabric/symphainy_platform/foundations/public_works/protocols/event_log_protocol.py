"""
Event Log Protocol - Abstraction Contract (Layer 2)

Defines the contract for append-only event log operations (Redis Streams–shaped surface).
Enables swappability between Redis Streams, in-memory, or other backends for WAL, Outbox, and event bus.

Swap unit: This protocol is swapped when we change the event log / stream backend (e.g. Redis Streams → Kafka, or in-memory for tests).

WHAT (Infrastructure Role): I define the contract for stream append, range read, consumer group, and ack.
HOW (Infrastructure Implementation): Implementations wrap adapters (e.g. RedisAdapter) inside Public Works only.
"""

from typing import Protocol, Dict, List, Optional, Tuple, Any


class EventLogProtocol(Protocol):
    """
    Protocol for event log (stream) operations.
    
    Mirrors the Redis Streams operations needed by WAL, TransactionalOutbox, and PostOfficeSDK.
    All implementations must live inside Public Works (e.g. RedisStreamsEventLogBackend).
    """

    async def xadd(
        self,
        stream_name: str,
        fields: Dict[str, str],
        maxlen: Optional[int] = None,
        approximate: bool = True
    ) -> Optional[str]:
        """
        Append an entry to the stream.

        Args:
            stream_name: Stream name
            fields: Field-value pairs (str keys and values)
            maxlen: Optional max stream length (trim old entries)
            approximate: If True, use approximate trimming when maxlen set

        Returns:
            Message ID if successful, None otherwise
        """
        ...

    async def xrange(
        self,
        stream_name: str,
        start: str = "-",
        end: str = "+",
        count: Optional[int] = None
    ) -> List[Tuple[str, Dict[str, str]]]:
        """
        Read a range of entries from the stream.

        Args:
            stream_name: Stream name
            start: Start message ID ("-" = beginning)
            end: End message ID ("+" = end)
            count: Optional maximum number of messages

        Returns:
            List of (message_id, fields_dict) tuples
        """
        ...

    async def xgroup_create(
        self,
        stream_name: str,
        group_name: str,
        id: str = "0",
        mkstream: bool = False
    ) -> bool:
        """
        Create a consumer group for the stream.

        Args:
            stream_name: Stream name
            group_name: Consumer group name
            id: Starting message ID ("0" = from beginning)
            mkstream: If True, create stream if it does not exist

        Returns:
            True if created (or already exists), False on failure
        """
        ...

    async def xreadgroup(
        self,
        group_name: str,
        consumer_name: str,
        streams: Dict[str, str],
        count: Optional[int] = None,
        block: Optional[int] = None
    ) -> Dict[str, List[Tuple[str, Dict[str, str]]]]:
        """
        Read from a consumer group.

        Args:
            group_name: Consumer group name
            consumer_name: Consumer name
            streams: Map stream name -> id (e.g. {stream_name: ">"} for new messages)
            count: Optional max messages per stream
            block: Optional block time in milliseconds

        Returns:
            Map stream name -> list of (message_id, fields_dict)
        """
        ...

    async def xack(
        self,
        stream_name: str,
        group_name: str,
        *message_ids: str
    ) -> int:
        """
        Acknowledge messages as processed.

        Args:
            stream_name: Stream name
            group_name: Consumer group name
            *message_ids: Message IDs to ack

        Returns:
            Number of messages acknowledged
        """
        ...
