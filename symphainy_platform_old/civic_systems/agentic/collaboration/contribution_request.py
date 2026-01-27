"""
Contribution Request - Non-Executing Agent Collaboration Request
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
from datetime import datetime

from utilities import generate_event_id, get_clock


@dataclass
class ContributionRequest:
    """
    Contribution request from one agent to another.
    
    This is NOT orchestration - it's reasoning collaboration.
    Returns non-executing artifacts only (proposals, blueprints).
    """
    request_id: str
    caller_agent_id: str
    target_agent_type: str
    purpose: str  # e.g., "workflow_design", "data_analysis"
    request_data: Dict[str, Any]
    constraints: Dict[str, Any]
    session_id: Optional[str] = None
    execution_id: Optional[str] = None
    created_at: datetime = None
    
    def __post_init__(self):
        """Initialize defaults."""
        if self.created_at is None:
            self.created_at = get_clock().now_utc()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "request_id": self.request_id,
            "caller_agent_id": self.caller_agent_id,
            "target_agent_type": self.target_agent_type,
            "purpose": self.purpose,
            "request_data": self.request_data,
            "constraints": self.constraints,
            "session_id": self.session_id,
            "execution_id": self.execution_id,
            "created_at": self.created_at.isoformat(),
        }
    
    @classmethod
    def create(
        cls,
        caller_agent_id: str,
        target_agent_type: str,
        purpose: str,
        request_data: Dict[str, Any],
        constraints: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
        execution_id: Optional[str] = None
    ) -> "ContributionRequest":
        """Create a new contribution request."""
        return cls(
            request_id=generate_event_id(),
            caller_agent_id=caller_agent_id,
            target_agent_type=target_agent_type,
            purpose=purpose,
            request_data=request_data,
            constraints=constraints or {},
            session_id=session_id,
            execution_id=execution_id
        )


@dataclass
class ContributionResponse:
    """
    Contribution response from target agent.
    
    Contains non-executing artifacts only (proposals, blueprints, ranked options).
    """
    request_id: str
    target_agent_id: str
    artifact_type: str  # e.g., "proposal", "blueprint", "ranked_options"
    artifact: Dict[str, Any]
    confidence: float
    notes: Optional[str] = None
    created_at: datetime = None
    
    def __post_init__(self):
        """Initialize defaults."""
        if self.created_at is None:
            self.created_at = get_clock().now_utc()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "request_id": self.request_id,
            "target_agent_id": self.target_agent_id,
            "artifact_type": self.artifact_type,
            "artifact": self.artifact,
            "confidence": self.confidence,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
        }
