"""
Session Model - Session Request/Response Schemas
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class SessionCreateRequest:
    """Request to create a session."""
    credentials: Dict[str, Any]  # Authentication credentials (email, password)
    metadata: Optional[Dict[str, Any]] = None  # Optional session metadata


@dataclass
class SessionCreateResponse:
    """Response from session creation."""
    session_id: str
    tenant_id: str
    user_id: str
    created_at: str
