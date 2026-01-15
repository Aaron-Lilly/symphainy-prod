"""
Execution Context - Runtime Context for Domain Services

Provides runtime execution context to domain services.

WHAT (Runtime Role): I provide execution context to domain services
HOW (Runtime Implementation): I wrap intent, state, WAL, and metadata in a context

Key Principle: Domain services receive ExecutionContext, not raw parameters.
This ensures they have access to runtime capabilities (state, WAL, etc.)
without bypassing Runtime.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime

from utilities import generate_event_id, get_clock, get_logger
from .intent_model import Intent
from .wal import WriteAheadLog
from .state_surface import StateSurface


@dataclass
class ExecutionContext:
    """
    Runtime execution context for domain services.
    
    Domain services receive ExecutionContext, not raw parameters.
    This ensures they have access to runtime capabilities without
    bypassing Runtime.
    """
    execution_id: str
    intent: Intent
    tenant_id: str
    session_id: str
    solution_id: str
    state_surface: Optional[StateSurface] = None
    wal: Optional[WriteAheadLog] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: get_clock().now_utc())
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate execution context.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate required fields
        if not self.execution_id:
            return False, "execution_id is required"
        
        if not self.intent:
            return False, "intent is required"
        
        # Validate intent
        is_valid, error = self.intent.validate()
        if not is_valid:
            return False, f"Invalid intent: {error}"
        
        if not self.tenant_id:
            return False, "tenant_id is required"
        
        if not self.session_id:
            return False, "session_id is required"
        
        if not self.solution_id:
            return False, "solution_id is required"
        
        # Validate tenant_id matches intent
        if self.tenant_id != self.intent.tenant_id:
            return False, "tenant_id mismatch between context and intent"
        
        # Validate session_id matches intent
        if self.session_id != self.intent.session_id:
            return False, "session_id mismatch between context and intent"
        
        # Validate solution_id matches intent
        if self.solution_id != self.intent.solution_id:
            return False, "solution_id mismatch between context and intent"
        
        return True, None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert execution context to dictionary."""
        return {
            "execution_id": self.execution_id,
            "intent": self.intent.to_dict(),
            "tenant_id": self.tenant_id,
            "session_id": self.session_id,
            "solution_id": self.solution_id,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            # Note: state_surface and wal are not serialized (runtime-only)
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], state_surface: Optional[StateSurface] = None, wal: Optional[WriteAheadLog] = None) -> "ExecutionContext":
        """
        Create execution context from dictionary.
        
        Args:
            data: Dictionary data
            state_surface: Optional state surface (runtime-only)
            wal: Optional WAL (runtime-only)
        """
        from .intent_model import Intent
        
        return cls(
            execution_id=data["execution_id"],
            intent=Intent.from_dict(data["intent"]),
            tenant_id=data["tenant_id"],
            session_id=data["session_id"],
            solution_id=data["solution_id"],
            state_surface=state_surface,
            wal=wal,
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data.get("created_at", get_clock().now_utc().isoformat())),
        )


class ExecutionContextFactory:
    """
    Factory for creating execution contexts.
    
    Provides convenience methods for creating execution contexts.
    """
    
    @staticmethod
    def create_context(
        intent: Intent,
        state_surface: Optional[StateSurface] = None,
        wal: Optional[WriteAheadLog] = None,
        metadata: Optional[Dict[str, Any]] = None,
        execution_id: Optional[str] = None
    ) -> ExecutionContext:
        """
        Create an execution context.
        
        Args:
            intent: The intent being executed
            state_surface: Optional state surface
            wal: Optional WAL
            metadata: Optional execution metadata
            execution_id: Optional execution ID (generated if not provided)
        
        Returns:
            Created execution context
        """
        if execution_id is None:
            execution_id = generate_event_id()
        
        context = ExecutionContext(
            execution_id=execution_id,
            intent=intent,
            tenant_id=intent.tenant_id,
            session_id=intent.session_id,
            solution_id=intent.solution_id,
            state_surface=state_surface,
            wal=wal,
            metadata=metadata or {},
        )
        
        # Validate context
        is_valid, error = context.validate()
        if not is_valid:
            raise ValueError(f"Invalid execution context: {error}")
        
        return context
