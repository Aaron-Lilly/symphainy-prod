"""
Control Room API - Platform Observability Endpoints

This is a thin routing layer that submits intents to the Control Tower capability.
All actual logic lives in Control Tower intent services.

Pattern: API Endpoint → submit_control_tower_intent() → Runtime → Control Tower Capability
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

from fastapi import APIRouter, HTTPException, Request, Query
from typing import Dict, Any, Optional

from utilities import get_logger
from ..intent_helper import submit_control_tower_intent, get_user_context


router = APIRouter(prefix="/api/admin/control-room", tags=["admin", "control-room"])
logger = get_logger("AdminDashboardAPI.ControlRoom")


@router.get("/statistics")
async def get_platform_statistics(
    request: Request,
    session_id: Optional[str] = Query(None, description="Session ID"),
    tenant_id: Optional[str] = Query(None, description="Tenant ID")
) -> Dict[str, Any]:
    """
    Get overall platform statistics.
    
    Submits `get_platform_statistics` intent to Control Tower.
    """
    user_ctx = await get_user_context(request)
    
    return await submit_control_tower_intent(
        request=request,
        intent_type="get_platform_statistics",
        parameters={},
        session_id=session_id or user_ctx["session_id"],
        tenant_id=tenant_id or user_ctx["tenant_id"]
    )


@router.get("/execution-metrics")
async def get_execution_metrics(
    request: Request,
    time_range: str = Query("1h", description="Time range (1h, 24h, 7d)"),
    session_id: Optional[str] = Query(None, description="Session ID"),
    tenant_id: Optional[str] = Query(None, description="Tenant ID")
) -> Dict[str, Any]:
    """
    Get execution metrics.
    
    Submits `get_execution_metrics` intent to Control Tower.
    """
    user_ctx = await get_user_context(request)
    
    return await submit_control_tower_intent(
        request=request,
        intent_type="get_execution_metrics",
        parameters={"time_range": time_range},
        session_id=session_id or user_ctx["session_id"],
        tenant_id=tenant_id or user_ctx["tenant_id"]
    )


@router.get("/realm-health")
async def get_realm_health(
    request: Request,
    session_id: Optional[str] = Query(None, description="Session ID"),
    tenant_id: Optional[str] = Query(None, description="Tenant ID")
) -> Dict[str, Any]:
    """
    Get realm health status.
    
    Submits `get_realm_health` intent to Control Tower.
    """
    user_ctx = await get_user_context(request)
    
    return await submit_control_tower_intent(
        request=request,
        intent_type="get_realm_health",
        parameters={},
        session_id=session_id or user_ctx["session_id"],
        tenant_id=tenant_id or user_ctx["tenant_id"]
    )


@router.get("/solution-registry")
async def get_solution_registry_status(
    request: Request,
    session_id: Optional[str] = Query(None, description="Session ID"),
    tenant_id: Optional[str] = Query(None, description="Tenant ID")
) -> Dict[str, Any]:
    """
    Get solution registry status.
    
    Submits `list_solutions` intent to Control Tower.
    """
    user_ctx = await get_user_context(request)
    
    return await submit_control_tower_intent(
        request=request,
        intent_type="list_solutions",
        parameters={},
        session_id=session_id or user_ctx["session_id"],
        tenant_id=tenant_id or user_ctx["tenant_id"]
    )


@router.get("/system-health")
async def get_system_health(
    request: Request,
    session_id: Optional[str] = Query(None, description="Session ID"),
    tenant_id: Optional[str] = Query(None, description="Tenant ID")
) -> Dict[str, Any]:
    """
    Get system health status.
    
    Submits `get_system_health` intent to Control Tower.
    """
    user_ctx = await get_user_context(request)
    
    return await submit_control_tower_intent(
        request=request,
        intent_type="get_system_health",
        parameters={},
        session_id=session_id or user_ctx["session_id"],
        tenant_id=tenant_id or user_ctx["tenant_id"]
    )
