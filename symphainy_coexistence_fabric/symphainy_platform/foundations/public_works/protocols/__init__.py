"""
Abstraction Contracts (Protocols)

Protocols define the contracts for infrastructure abstractions.
All abstractions must implement these protocols for swappability.
"""

from .file_parsing_protocol import (
    FileParsingRequest,
    FileParsingResult,
    FileParsingProtocol
)

from .parsing_service_protocol import (
    ParsingRequest,
    ParsingResult,
    StructuredParsingProtocol,
    UnstructuredParsingProtocol,
    HybridParsingProtocol,
    WorkflowSOPParsingProtocol
)

from .event_log_protocol import EventLogProtocol

__all__ = [
    "FileParsingRequest",
    "FileParsingResult",
    "FileParsingProtocol",
    "ParsingRequest",
    "ParsingResult",
    "StructuredParsingProtocol",
    "UnstructuredParsingProtocol",
    "HybridParsingProtocol",
    "WorkflowSOPParsingProtocol",
    "EventLogProtocol",
]
