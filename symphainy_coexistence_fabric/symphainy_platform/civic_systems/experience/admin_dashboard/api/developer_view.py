"""
Developer View API - Platform SDK Documentation & Developer Tools

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


router = APIRouter(prefix="/api/admin/developer", tags=["admin", "developer"])
logger = get_logger("AdminDashboardAPI.DeveloperView")


@router.get("/documentation")
async def get_documentation(
    request: Request,
    section: Optional[str] = Query(None, description="Documentation section"),
    session_id: Optional[str] = Query(None, description="Session ID"),
    tenant_id: Optional[str] = Query(None, description="Tenant ID")
) -> Dict[str, Any]:
    """
    Get Platform SDK documentation.
    
    Submits `get_documentation` intent to Control Tower.
    """
    user_ctx = await get_user_context(request)
    
    return await submit_control_tower_intent(
        request=request,
        intent_type="get_documentation",
        parameters={"section": section} if section else {},
        session_id=session_id or user_ctx["session_id"],
        tenant_id=tenant_id or user_ctx["tenant_id"]
    )


@router.get("/code-examples")
async def get_code_examples(
    request: Request,
    category: Optional[str] = Query(None, description="Example category"),
    session_id: Optional[str] = Query(None, description="Session ID"),
    tenant_id: Optional[str] = Query(None, description="Tenant ID")
) -> Dict[str, Any]:
    """
    Get code examples.
    
    Submits `get_code_examples` intent to Control Tower.
    """
    user_ctx = await get_user_context(request)
    
    return await submit_control_tower_intent(
        request=request,
        intent_type="get_code_examples",
        parameters={"category": category} if category else {},
        session_id=session_id or user_ctx["session_id"],
        tenant_id=tenant_id or user_ctx["tenant_id"]
    )


@router.get("/patterns")
async def get_patterns(
    request: Request,
    session_id: Optional[str] = Query(None, description="Session ID"),
    tenant_id: Optional[str] = Query(None, description="Tenant ID")
) -> Dict[str, Any]:
    """
    Get patterns and best practices.
    
    Submits `get_patterns` intent to Control Tower.
    """
    user_ctx = await get_user_context(request)
    
    return await submit_control_tower_intent(
        request=request,
        intent_type="get_patterns",
        parameters={},
        session_id=session_id or user_ctx["session_id"],
        tenant_id=tenant_id or user_ctx["tenant_id"]
    )


@router.post("/validate-solution")
async def validate_solution(
    request: Request,
    solution_config: Dict[str, Any],
    session_id: Optional[str] = Query(None, description="Session ID"),
    tenant_id: Optional[str] = Query(None, description="Tenant ID")
) -> Dict[str, Any]:
    """
    Validate a solution configuration (Solution Builder Playground).
    
    Submits `validate_solution` intent to Control Tower.
    """
    user_ctx = await get_user_context(request)
    
    return await submit_control_tower_intent(
        request=request,
        intent_type="validate_solution",
        parameters={"solution_config": solution_config},
        session_id=session_id or user_ctx["session_id"],
        tenant_id=tenant_id or user_ctx["tenant_id"]
    )


@router.post("/preview-solution")
async def preview_solution(
    request: Request,
    solution_config: Dict[str, Any],
    session_id: Optional[str] = Query(None, description="Session ID"),
    tenant_id: Optional[str] = Query(None, description="Tenant ID")
) -> Dict[str, Any]:
    """
    Preview a solution structure (Solution Builder Playground).
    
    Submits `validate_solution` intent with preview flag to Control Tower.
    """
    user_ctx = await get_user_context(request)
    
    return await submit_control_tower_intent(
        request=request,
        intent_type="validate_solution",
        parameters={"solution_config": solution_config, "preview": True},
        session_id=session_id or user_ctx["session_id"],
        tenant_id=tenant_id or user_ctx["tenant_id"]
    )


@router.post("/submit-feature-request")
async def submit_feature_request(
    request: Request,
    feature_request: Dict[str, Any],
    session_id: Optional[str] = Query(None, description="Session ID"),
    tenant_id: Optional[str] = Query(None, description="Tenant ID")
) -> Dict[str, Any]:
    """
    Submit a feature request (gated - "Coming Soon" for MVP).
    
    For MVP, returns a placeholder response. In future, this would
    submit a governance intent.
    """
    # For MVP: Return "Coming Soon" message
    # This is intentionally NOT an intent - it's a placeholder
    return {
        "status": "coming_soon",
        "message": "Feature submission is coming soon! This will enable developers to submit feature proposals for platform team review.",
        "feature_request": feature_request
    }
