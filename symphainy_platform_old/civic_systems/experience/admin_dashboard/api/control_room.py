"""
Control Room API - Platform Observability Endpoints
"""

import sys
from pathlib import Path

# Add project root to path
# Find project root by looking for common markers (pyproject.toml, requirements.txt, etc.)
current = Path(__file__).resolve()
project_root = current
for _ in range(10):  # Max 10 levels up
    if (project_root / "pyproject.toml").exists() or (project_root / "requirements.txt").exists():
        break
    project_root = project_root.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Dict, Any, Optional

from utilities import get_logger
from ..admin_dashboard_service import AdminDashboardService


router = APIRouter(prefix="/api/admin/control-room", tags=["admin", "control-room"])
logger = get_logger("AdminDashboardAPI.ControlRoom")


def get_admin_dashboard_service(request: Request) -> AdminDashboardService:
    """Dependency to get Admin Dashboard Service."""
    if not hasattr(request.app.state, "admin_dashboard_service"):
        raise RuntimeError("Admin Dashboard Service not initialized. Check Experience service startup.")
    return request.app.state.admin_dashboard_service


@router.get("/statistics")
async def get_platform_statistics(
    admin_service: AdminDashboardService = Depends(get_admin_dashboard_service),
    user_id: str = "admin"  # TODO: Get from auth context
):
    """Get overall platform statistics."""
    # Check access
    has_access = await admin_service.check_access(user_id, "control_room")
    if not has_access:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        stats = await admin_service.control_room_service.get_platform_statistics()
        return stats
    except Exception as e:
        logger.error(f"Failed to get platform statistics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/execution-metrics")
async def get_execution_metrics(
    time_range: str = "1h",
    admin_service: AdminDashboardService = Depends(get_admin_dashboard_service),
    user_id: str = "admin"  # TODO: Get from auth context
):
    """Get execution metrics."""
    # Check access
    has_access = await admin_service.check_access(user_id, "control_room")
    if not has_access:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        metrics = await admin_service.control_room_service.get_execution_metrics(time_range)
        return metrics
    except Exception as e:
        logger.error(f"Failed to get execution metrics: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/realm-health")
async def get_realm_health(
    admin_service: AdminDashboardService = Depends(get_admin_dashboard_service),
    user_id: str = "admin"  # TODO: Get from auth context
):
    """Get realm health status."""
    # Check access
    has_access = await admin_service.check_access(user_id, "control_room")
    if not has_access:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        health = await admin_service.control_room_service.get_realm_health()
        return health
    except Exception as e:
        logger.error(f"Failed to get realm health: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/solution-registry")
async def get_solution_registry_status(
    admin_service: AdminDashboardService = Depends(get_admin_dashboard_service),
    user_id: str = "admin"  # TODO: Get from auth context
):
    """Get solution registry status."""
    # Check access
    has_access = await admin_service.check_access(user_id, "control_room")
    if not has_access:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        status = await admin_service.control_room_service.get_solution_registry_status()
        return status
    except Exception as e:
        logger.error(f"Failed to get solution registry status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/system-health")
async def get_system_health(
    admin_service: AdminDashboardService = Depends(get_admin_dashboard_service),
    user_id: str = "admin"  # TODO: Get from auth context
):
    """Get system health status."""
    # Check access
    has_access = await admin_service.check_access(user_id, "control_room")
    if not has_access:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        health = await admin_service.control_room_service.get_system_health()
        return health
    except Exception as e:
        logger.error(f"Failed to get system health: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
