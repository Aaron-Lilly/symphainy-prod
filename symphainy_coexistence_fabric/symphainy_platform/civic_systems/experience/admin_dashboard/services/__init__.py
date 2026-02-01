"""
Admin Dashboard Services - Access Control

The view-specific services (ControlRoomService, DeveloperViewService, 
BusinessUserViewService) have been removed. Their functionality now
lives in Control Tower intent services, following the platform 
architecture where everything flows through intents.

Only AccessControlService remains for permission checking.
"""

from .access_control_service import AccessControlService

__all__ = [
    "AccessControlService",
]
