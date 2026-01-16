"""
Admin Dashboard Service - Core Service for Admin Dashboard

Coordinates all admin dashboard operations across three views.

WHAT (Admin Dashboard Role): I coordinate admin dashboard operations
HOW (Admin Dashboard Implementation): I delegate to specialized services for each view
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional

from utilities import get_logger
from .services.control_room_service import ControlRoomService
from .services.developer_view_service import DeveloperViewService
from .services.business_user_view_service import BusinessUserViewService
from .services.access_control_service import AccessControlService


class AdminDashboardService:
    """
    Admin Dashboard Service - Core service for admin dashboard.
    
    Coordinates:
    - Control Room View (platform observability)
    - Developer View (documentation, playground, features)
    - Business User View (solution composition, templates)
    - Access Control (gated features)
    """
    
    def __init__(
        self,
        runtime_client: Optional[Any] = None,
        realm_registry: Optional[Any] = None,
        solution_registry: Optional[Any] = None,
        security_guard_sdk: Optional[Any] = None,
        public_works: Optional[Any] = None
    ):
        """
        Initialize Admin Dashboard Service.
        
        Args:
            runtime_client: Runtime client for execution metrics
            realm_registry: Realm registry for realm health
            solution_registry: Solution registry for solution status
            security_guard_sdk: Security Guard SDK for access control
            public_works: Public Works Foundation Service
        """
        self.logger = get_logger(self.__class__.__name__)
        
        # Initialize specialized services
        self.control_room_service = ControlRoomService(
            runtime_client=runtime_client,
            realm_registry=realm_registry,
            solution_registry=solution_registry,
            public_works=public_works
        )
        
        self.developer_view_service = DeveloperViewService(
            solution_registry=solution_registry,
            public_works=public_works
        )
        
        self.business_user_view_service = BusinessUserViewService(
            solution_registry=solution_registry,
            public_works=public_works
        )
        
        self.access_control_service = AccessControlService(
            security_guard_sdk=security_guard_sdk
        )
        
        self.logger.info("Admin Dashboard Service initialized")
    
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
