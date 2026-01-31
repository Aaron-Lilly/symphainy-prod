"""
Public Works backends - protocol implementations that wrap adapters.

All implementations live inside Public Works. No adapter escapes this package.
"""

from .redis_streams_event_log import RedisStreamsEventLogBackend

__all__ = ["RedisStreamsEventLogBackend"]
