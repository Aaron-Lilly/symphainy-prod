"""
Business User View API - Solution Composition & Business Tools

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


router = APIRouter(prefix="/api/admin/business", tags=["admin", "business"])
logger = get_logger("AdminDashboardAPI.BusinessUserView")


@router.get("/composition-guide")
async def get_composition_guide(
    request: Request,
    session_id: Optional[str] = Query(None, description="Session ID"),
    tenant_id: Optional[str] = Query(None, description="Tenant ID")
) -> Dict[str, Any]:
    """
    Get solution composition guide.
    
    Returns static guide content (no intent needed for MVP).
    In future, could be a `get_composition_guide` intent.
    """
    # Static content for MVP - doesn't need to go through intent system
    return {
        "steps": [
            {
                "step": 1,
                "title": "Define Goals",
                "description": "Define what you want to achieve with this solution"
            },
            {
                "step": 2,
                "title": "Select Domains",
                "description": "Choose which domains (Content, Insights, Operations, Outcomes) to include"
            },
            {
                "step": 3,
                "title": "Configure Intents",
                "description": "Select which intents your solution will support"
            },
            {
                "step": 4,
                "title": "Set Context",
                "description": "Define constraints and risk level"
            },
            {
                "step": 5,
                "title": "Review & Register",
                "description": "Review your solution and register it with the platform"
            }
        ],
        "available_domains": ["content", "insights", "operations", "outcomes"],
        "available_intents": {
            "content": ["ingest_file", "parse_content", "create_deterministic_embeddings"],
            "insights": ["analyze_structured_data", "interpret_data_self_discovery", "map_relationships"],
            "operations": ["create_workflow", "generate_sop", "optimize_process"],
            "outcomes": ["synthesize_outcome", "generate_roadmap", "create_poc"]
        }
    }


@router.get("/templates")
async def get_solution_templates(
    request: Request,
    session_id: Optional[str] = Query(None, description="Session ID"),
    tenant_id: Optional[str] = Query(None, description="Tenant ID")
) -> Dict[str, Any]:
    """
    Get available solution templates.
    
    Submits `get_solution_templates` intent to Control Tower.
    """
    user_ctx = await get_user_context(request)
    
    return await submit_control_tower_intent(
        request=request,
        intent_type="get_solution_templates",
        parameters={},
        session_id=session_id or user_ctx["session_id"],
        tenant_id=tenant_id or user_ctx["tenant_id"]
    )


@router.post("/create-from-template")
async def create_from_template(
    request: Request,
    template_id: str,
    customizations: Optional[Dict[str, Any]] = None,
    session_id: Optional[str] = Query(None, description="Session ID"),
    tenant_id: Optional[str] = Query(None, description="Tenant ID")
) -> Dict[str, Any]:
    """
    Create solution from template.
    
    Submits `compose_solution` intent to Control Tower.
    """
    user_ctx = await get_user_context(request)
    
    return await submit_control_tower_intent(
        request=request,
        intent_type="compose_solution",
        parameters={
            "template_id": template_id,
            "customizations": customizations or {}
        },
        session_id=session_id or user_ctx["session_id"],
        tenant_id=tenant_id or user_ctx["tenant_id"]
    )


@router.post("/compose")
async def compose_solution(
    request: Request,
    solution_config: Dict[str, Any],
    session_id: Optional[str] = Query(None, description="Session ID"),
    tenant_id: Optional[str] = Query(None, description="Tenant ID")
) -> Dict[str, Any]:
    """
    Compose a solution (advanced builder).
    
    Submits `compose_solution` intent to Control Tower.
    """
    user_ctx = await get_user_context(request)
    
    return await submit_control_tower_intent(
        request=request,
        intent_type="compose_solution",
        parameters={"solution_config": solution_config},
        session_id=session_id or user_ctx["session_id"],
        tenant_id=tenant_id or user_ctx["tenant_id"]
    )


@router.get("/solutions")
async def list_solutions(
    request: Request,
    active_only: bool = Query(False, description="Only list active solutions"),
    session_id: Optional[str] = Query(None, description="Session ID"),
    tenant_id: Optional[str] = Query(None, description="Tenant ID")
) -> Dict[str, Any]:
    """
    List registered solutions.
    
    Submits `list_solutions` intent to Control Tower.
    """
    user_ctx = await get_user_context(request)
    
    return await submit_control_tower_intent(
        request=request,
        intent_type="list_solutions",
        parameters={"active_only": active_only},
        session_id=session_id or user_ctx["session_id"],
        tenant_id=tenant_id or user_ctx["tenant_id"]
    )


@router.get("/solutions/{solution_id}")
async def get_solution_status(
    request: Request,
    solution_id: str,
    session_id: Optional[str] = Query(None, description="Session ID"),
    tenant_id: Optional[str] = Query(None, description="Tenant ID")
) -> Dict[str, Any]:
    """
    Get solution status.
    
    Submits `get_solution_status` intent to Control Tower.
    """
    user_ctx = await get_user_context(request)
    
    return await submit_control_tower_intent(
        request=request,
        intent_type="get_solution_status",
        parameters={"solution_id": solution_id},
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
    Submit a feature request.
    
    For MVP: Simple acknowledgment. In future, would trigger governance workflow.
    """
    # For MVP: Return acknowledgment
    feature_id = f"feature_{feature_request.get('title', 'unknown').lower().replace(' ', '_')}"
    
    return {
        "success": True,
        "feature_request_id": feature_id,
        "message": "Feature request submitted successfully",
        "feature_request": feature_request
    }
