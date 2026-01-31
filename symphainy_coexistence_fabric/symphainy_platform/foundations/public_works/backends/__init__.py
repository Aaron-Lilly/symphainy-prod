"""
Public Works backends - protocol implementations that wrap adapters.

All implementations live inside Public Works. No adapter escapes this package.
Callers (including foundation_service) use factory functions and protocol types only;
they do not import concrete backend classes.
"""

from .redis_streams_event_log import RedisStreamsEventLogBackend
from ..protocols.event_log_protocol import EventLogProtocol
from typing import Optional, Any

__all__ = ["RedisStreamsEventLogBackend", "create_event_log_backend"]


def create_event_log_backend(redis_adapter: Optional[Any]) -> Optional[EventLogProtocol]:
    """
    Factory: create EventLogProtocol implementation for WAL/event log.
    Returns None if redis_adapter is None. Foundation service uses this instead of
    importing RedisStreamsEventLogBackend directly (protocol-only pattern).
    """
    if redis_adapter is None:
        return None
    return RedisStreamsEventLogBackend(redis_adapter)
