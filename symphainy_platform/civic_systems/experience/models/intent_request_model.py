"""
Intent Request Model - Intent Submission Schemas
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class IntentSubmitRequest:
    """Request to submit an intent."""
    session_id: str
    intent_type: str
    parameters: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class IntentSubmitResponse:
    """Response from intent submission."""
    execution_id: str
    intent_id: str
    status: str
    created_at: str
