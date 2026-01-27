"""
ID Generation Utilities

Phase 0 Utility: Provides consistent ID generation for session_id, saga_id, event_id.

WHAT (Utility): I provide ID generation for platform identifiers
HOW (Implementation): I use UUID v4 with optional prefixes
"""

import uuid
from typing import Optional


class IDGenerator:
    """
    ID generator for platform identifiers.
    
    Provides consistent ID generation with optional prefixes.
    """
    
    @staticmethod
    def generate(prefix: Optional[str] = None) -> str:
        """
        Generate a unique ID.
        
        Args:
            prefix: Optional prefix (e.g., "session", "saga", "event")
        
        Returns:
            Unique ID string (e.g., "session_550e8400-e29b-41d4-a716-446655440000")
        """
        id_value = str(uuid.uuid4())
        if prefix:
            return f"{prefix}_{id_value}"
        return id_value
    
    @staticmethod
    def generate_session_id() -> str:
        """Generate session ID."""
        return IDGenerator.generate("session")
    
    @staticmethod
    def generate_saga_id() -> str:
        """Generate saga ID."""
        return IDGenerator.generate("saga")
    
    @staticmethod
    def generate_event_id() -> str:
        """Generate event ID."""
        return IDGenerator.generate("event")
    
    @staticmethod
    def generate_trace_id() -> str:
        """Generate trace ID."""
        return IDGenerator.generate("trace")
    
    @staticmethod
    def generate_execution_id() -> str:
        """Generate execution ID."""
        return IDGenerator.generate("execution")


# Convenience functions
def generate_session_id() -> str:
    """Generate session ID."""
    return IDGenerator.generate_session_id()


def generate_saga_id() -> str:
    """Generate saga ID."""
    return IDGenerator.generate_saga_id()


def generate_event_id() -> str:
    """Generate event ID."""
    return IDGenerator.generate_event_id()


def generate_trace_id() -> str:
    """Generate trace ID."""
    return IDGenerator.generate_trace_id()


def generate_execution_id() -> str:
    """Generate execution ID."""
    return IDGenerator.generate_execution_id()


def generate_step_id() -> str:
    """Generate step ID for saga steps."""
    return IDGenerator.generate("step")
