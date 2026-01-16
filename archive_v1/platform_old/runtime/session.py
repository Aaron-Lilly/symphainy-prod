"""
Session Lifecycle - First-Class Sessions

Sessions are first-class, not incidental.
Every intent requires a session.
Tenant is mandatory from day one.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List, Optional

from utilities import generate_session_id, get_clock


@dataclass
class Session:
    """
    First-class session object.
    
    Sessions are required for all intents and provide:
    - Tenant isolation (mandatory from day one)
    - User context
    - Active saga tracking
    - Execution context
    """
    session_id: str
    tenant_id: str
    user_id: str
    created_at: datetime
    context: Dict[str, Any] = field(default_factory=dict)
    active_sagas: List[str] = field(default_factory=list)
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Set updated_at if not provided."""
        if self.updated_at is None:
            self.updated_at = self.created_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary."""
        return {
            "session_id": self.session_id,
            "tenant_id": self.tenant_id,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "context": self.context,
            "active_sagas": self.active_sagas,
        }
    
    @classmethod
    def create(
        cls,
        tenant_id: str,
        user_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> "Session":
        """
        Create a new session.
        
        Args:
            tenant_id: Tenant identifier (mandatory)
            user_id: User identifier
            context: Optional initial context
        
        Returns:
            New Session instance
        """
        clock = get_clock()
        now = clock.now()
        return cls(
            session_id=generate_session_id(),
            tenant_id=tenant_id,
            user_id=user_id,
            created_at=now,
            context=context or {},
            active_sagas=[],
            updated_at=now
        )
    
    def add_saga(self, saga_id: str) -> None:
        """Add active saga to session."""
        if saga_id not in self.active_sagas:
            self.active_sagas.append(saga_id)
            self.updated_at = get_clock().now()
    
    def remove_saga(self, saga_id: str) -> None:
        """Remove saga from active list."""
        if saga_id in self.active_sagas:
            self.active_sagas.remove(saga_id)
            self.updated_at = get_clock().now()
    
    def update_context(self, updates: Dict[str, Any]) -> None:
        """Update session context."""
        self.context.update(updates)
        self.updated_at = get_clock().now()
