"""
Phase 0 Utilities

Platform primitives for:
- Structured logging (JSON)
- ID generation (session_id, saga_id, event_id)
- Clock abstraction (for determinism)
- Error taxonomy (platform vs domain vs agent)
"""

from .logging import StructuredLogger, get_logger, LogLevel, LogCategory
from .ids import IDGenerator, generate_session_id, generate_saga_id, generate_event_id, generate_trace_id, generate_execution_id, generate_step_id
from .clock import Clock, get_clock
from .errors import (
    PlatformError,
    DomainError,
    AgentError,
    ErrorTaxonomy,
    categorize_error
)

__all__ = [
    # Logging
    "StructuredLogger",
    "get_logger",
    "LogLevel",
    "LogCategory",
    # ID Generation
    "IDGenerator",
    "generate_session_id",
    "generate_saga_id",
    "generate_event_id",
    "generate_trace_id",
    "generate_execution_id",
    "generate_step_id",
    # Clock
    "Clock",
    "get_clock",
    # Errors
    "PlatformError",
    "DomainError",
    "AgentError",
    "ErrorTaxonomy",
    "categorize_error",
]
