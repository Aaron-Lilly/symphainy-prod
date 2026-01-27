"""
Admin Dashboard API - REST Endpoints for Admin Dashboard

Three view routers:
- Control Room API
- Developer View API
- Business User View API
"""

from .control_room import router as control_room_router
from .developer_view import router as developer_view_router
from .business_user_view import router as business_user_view_router

__all__ = [
    "control_room_router",
    "developer_view_router",
    "business_user_view_router",
]
