"""
Admin Dashboard Service - Access Control Coordinator

This service now only handles access control. All actual functionality
has been moved to Control Tower intent services, following the platform
architecture where everything flows through intents.

Pattern:
    Admin Dashboard API → intent_helper → Runtime → Control Tower Capability
    
The Admin Dashboard is now a thin persona-aware layer that:
1. Checks access permissions
2. Routes to appropriate Control Tower intents

WHAT (Admin Dashboard Role): I coordinate access to admin views
HOW (Admin Dashboard Implementation): I delegate to AccessControlService
"""

import sys
from pathlib import Path

# Add project root to path
current = Path(__file__).resolve()
project_root = current
for _ in range(10):
    if (project_root / "pyproject.toml").exists() or (project_root / "requirements.txt").exists():
        break
    project_root = project_root.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Optional

from utilities import get_logger
from .services.access_control_service import AccessControlService


class AdminDashboardService:
    """
    Admin Dashboard Service - Access control coordinator.
    
    Views (now thin intent routing layers):
    - Control Room View: Platform observability → Control Tower intents
    - Developer View: Documentation, playground → Control Tower intents
    - Business User View: Solution composition → Control Tower intents
    
    This service only handles access control. All functionality
    routes through Control Tower capability via intent submission.
    """
    
    def __init__(
        self,
        security_guard_sdk: Optional[object] = None
    ):
        """
        Initialize Admin Dashboard Service.
        
        Args:
            security_guard_sdk: Security Guard SDK for access control
        """
        self.logger = get_logger(self.__class__.__name__)
        
        # Only access control service needed now
        self.access_control_service = AccessControlService(
            security_guard_sdk=security_guard_sdk
        )
        
        self.logger.info("Admin Dashboard Service initialized (thin layer mode)")
    
    async def check_access(
        self,
        user_id: str,
        view: str,
        feature: Optional[str] = None
    ) -> bool:
        """
        Check if user has access to a view or feature.
        
        Args:
            user_id: User identifier
            view: View name ("developer", "business", "control_room")
            feature: Optional feature name (for gated features)
        
        Returns:
            True if user has access
        """
        return await self.access_control_service.check_access(
            user_id=user_id,
            view=view,
            feature=feature
        )
