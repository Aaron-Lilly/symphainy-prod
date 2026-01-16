"""
Access Control Service - Gated Access Management

Manages gated access to admin dashboard features.

WHAT (Access Control Role): I manage gated access to features
HOW (Access Control Implementation): I use feature flags and Smart City SDK
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[6]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional, List

from utilities import get_logger


# Feature flags configuration
FEATURE_FLAGS: Dict[str, List[str]] = {
    # View-level access
    "developer": ["admin", "demo_user", "developer"],
    "business": ["admin", "demo_user", "business_user"],
    "control_room": ["admin", "demo_user"],
    
    # Feature-level access (gated features)
    "developer.playground": ["admin", "demo_user"],
    "developer.feature_submission": ["admin"],  # Coming soon for others
    "business.advanced_builder": ["admin", "demo_user"],
    "business.solution_templates": ["admin", "demo_user"],
    "control_room.real_time": ["admin", "demo_user"],
    "control_room.advanced_metrics": ["admin", "demo_user"],
    "control_room.alerting": ["admin"],  # Admin only
}


class AccessControlService:
    """
    Access Control Service - Manages gated access.
    
    Provides:
    - View-level access control
    - Feature-level access control (gated features)
    - Feature flag management
    """
    
    def __init__(self, security_guard_sdk: Optional[Any] = None):
        """
        Initialize Access Control Service.
        
        Args:
            security_guard_sdk: Optional Security Guard SDK for advanced access control
        """
        self.logger = get_logger(self.__class__.__name__)
        self.security_guard_sdk = security_guard_sdk
        self.feature_flags = FEATURE_FLAGS.copy()
    
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
            feature: Optional feature name (e.g., "playground", "real_time")
        
        Returns:
            True if user has access
        """
        # For MVP: Simple role-based check
        # In production: Use Security Guard SDK for full RBAC
        
        # Get user role (for MVP, assume from user_id or metadata)
        # In production, this would come from Security Guard SDK
        user_role = self._get_user_role(user_id)
        
        # Check view-level access
        if view not in self.feature_flags:
            self.logger.warning(f"Unknown view: {view}")
            return False
        
        view_roles = self.feature_flags[view]
        if user_role not in view_roles:
            return False
        
        # Check feature-level access (if feature specified)
        if feature:
            feature_key = f"{view}.{feature}"
            if feature_key in self.feature_flags:
                feature_roles = self.feature_flags[feature_key]
                return user_role in feature_roles
            # If feature not in flags, allow if view access is granted
            return True
        
        return True
    
    def _get_user_role(self, user_id: str) -> str:
        """
        Get user role (MVP implementation).
        
        In production, this would use Security Guard SDK.
        
        Args:
            user_id: User identifier
        
        Returns:
            User role
        """
        # MVP: Simple role detection
        # In production: Query Security Guard SDK
        
        # For demo: Check if user_id contains role indicator
        if "admin" in user_id.lower():
            return "admin"
        elif "demo" in user_id.lower():
            return "demo_user"
        elif "developer" in user_id.lower():
            return "developer"
        elif "business" in user_id.lower():
            return "business_user"
        
        # Default: admin for MVP (can be configured)
        return "admin"
    
    def get_available_features(self, user_id: str, view: str) -> List[str]:
        """
        Get list of available features for a user in a view.
        
        Args:
            user_id: User identifier
            view: View name
        
        Returns:
            List of available feature names
        """
        user_role = self._get_user_role(user_id)
        available_features = []
        
        # Check all features for this view
        for feature_key, roles in self.feature_flags.items():
            if feature_key.startswith(f"{view}."):
                feature_name = feature_key.split(".", 1)[1]
                if user_role in roles:
                    available_features.append(feature_name)
        
        return available_features
