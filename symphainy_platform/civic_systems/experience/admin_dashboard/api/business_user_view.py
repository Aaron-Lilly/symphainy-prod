"""
Business User View API - Solution Composition Endpoints
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[6]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Dict, Any, Optional

from utilities import get_logger
from ..admin_dashboard_service import AdminDashboardService


router = APIRouter(prefix="/api/admin/business", tags=["admin", "business"])
logger = get_logger("AdminDashboardAPI.BusinessUserView")


class SolutionCompositionRequest(BaseModel):
    """Request to compose a solution."""
    solution_config: Dict[str, Any]


class SolutionTemplateRequest(BaseModel):
    """Request to create solution from template."""
    template_id: str
    customizations: Optional[Dict[str, Any]] = None


class FeatureRequestSubmission(BaseModel):
    """Feature request submission."""
    title: str
    description: str
    business_need: str
    priority: Optional[str] = "medium"
    metadata: Optional[Dict[str, Any]] = None


def get_admin_dashboard_service(request: Request) -> AdminDashboardService:
    """Dependency to get Admin Dashboard Service."""
    if not hasattr(request.app.state, "admin_dashboard_service"):
        raise RuntimeError("Admin Dashboard Service not initialized")
    return request.app.state.admin_dashboard_service


@router.get("/composition-guide")
async def get_composition_guide(
    admin_service: AdminDashboardService = Depends(get_admin_dashboard_service),
    user_id: str = "admin"  # TODO: Get from auth context
):
    """Get solution composition guide."""
    # Check access
    has_access = await admin_service.check_access(user_id, "business")
    if not has_access:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        guide = await admin_service.business_user_view_service.get_composition_guide()
        return guide
    except Exception as e:
        logger.error(f"Failed to get composition guide: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/solution-templates")
async def get_solution_templates(
    admin_service: AdminDashboardService = Depends(get_admin_dashboard_service),
    user_id: str = "admin"  # TODO: Get from auth context
):
    """Get available solution templates (gated)."""
    # Check access to templates feature
    has_access = await admin_service.check_access(user_id, "business", "solution_templates")
    if not has_access:
        raise HTTPException(status_code=403, detail="Solution templates feature not available")
    
    try:
        templates = await admin_service.business_user_view_service.get_solution_templates()
        return templates
    except Exception as e:
        logger.error(f"Failed to get solution templates: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/solutions/from-template")
async def create_from_template(
    request: SolutionTemplateRequest,
    admin_service: AdminDashboardService = Depends(get_admin_dashboard_service),
    user_id: str = "admin"  # TODO: Get from auth context
):
    """Create solution from template (gated)."""
    # Check access to templates feature
    has_access = await admin_service.check_access(user_id, "business", "solution_templates")
    if not has_access:
        raise HTTPException(status_code=403, detail="Solution templates feature not available")
    
    try:
        result = await admin_service.business_user_view_service.create_from_template(
            request.template_id,
            request.customizations
        )
        return result
    except Exception as e:
        logger.error(f"Failed to create solution from template: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/solutions/compose")
async def compose_solution(
    request: SolutionCompositionRequest,
    admin_service: AdminDashboardService = Depends(get_admin_dashboard_service),
    user_id: str = "admin"  # TODO: Get from auth context
):
    """Compose a solution (advanced builder - gated)."""
    # Check access to advanced builder feature
    has_access = await admin_service.check_access(user_id, "business", "advanced_builder")
    if not has_access:
        raise HTTPException(status_code=403, detail="Advanced solution builder feature not available")
    
    try:
        result = await admin_service.business_user_view_service.compose_solution(
            request.solution_config
        )
        return result
    except Exception as e:
        logger.error(f"Failed to compose solution: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/solutions/register")
async def register_solution(
    request: SolutionCompositionRequest,
    admin_service: AdminDashboardService = Depends(get_admin_dashboard_service),
    user_id: str = "admin"  # TODO: Get from auth context
):
    """Register a composed solution."""
    # Check access
    has_access = await admin_service.check_access(user_id, "business")
    if not has_access:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        result = await admin_service.business_user_view_service.register_solution(
            request.solution_config
        )
        return result
    except Exception as e:
        logger.error(f"Failed to register solution: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/feature-requests/submit")
async def submit_feature_request(
    request: FeatureRequestSubmission,
    admin_service: AdminDashboardService = Depends(get_admin_dashboard_service),
    user_id: str = "admin"  # TODO: Get from auth context
):
    """Submit a feature request."""
    # Check access
    has_access = await admin_service.check_access(user_id, "business")
    if not has_access:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        result = await admin_service.business_user_view_service.submit_feature_request(
            request.dict()
        )
        return result
    except Exception as e:
        logger.error(f"Failed to submit feature request: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
