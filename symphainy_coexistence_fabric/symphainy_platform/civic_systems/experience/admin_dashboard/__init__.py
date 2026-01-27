"""
Admin Dashboard - Administrator/Owner Front Door

Experience Plane component providing three revolutionary views:
1. Developer View - Platform SDK documentation, feature submission, playground
2. Business User View - Solution composition, templates, feature requests
3. Control Room View - Real-time platform observability and governance

WHAT (Experience Plane Role): I provide admin dashboard capabilities
HOW (Experience Plane Implementation): I expose admin dashboard APIs with gated access
"""

from .admin_dashboard_service import AdminDashboardService

__all__ = ["AdminDashboardService"]
