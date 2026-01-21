"""
Intent Request Model - Intent Submission Schemas
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class IntentSubmitRequest:
    """Request to submit an intent."""
    session_id: str
    intent_type: str
    tenant_id: str  # Required for multi-tenant operation
    solution_id: str = "default"  # Optional, defaults to "default"
    parameters: Dict[str, Any] = field(default_factory=dict)
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class IntentSubmitResponse:
    """Response from intent submission."""
    execution_id: str
    intent_id: str
    status: str
    created_at: str
