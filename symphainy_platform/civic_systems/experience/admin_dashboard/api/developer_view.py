"""
Developer View API - Developer Tools Endpoints
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


router = APIRouter(prefix="/api/admin/developer", tags=["admin", "developer"])
logger = get_logger("AdminDashboardAPI.DeveloperView")


class SolutionValidationRequest(BaseModel):
    """Request to validate a solution."""
    solution_config: Dict[str, Any]


class FeatureRequestSubmission(BaseModel):
    """Feature request submission."""
    title: str
    description: str
    category: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


def get_admin_dashboard_service(request: Request) -> AdminDashboardService:
    """Dependency to get Admin Dashboard Service."""
    if not hasattr(request.app.state, "admin_dashboard_service"):
        raise RuntimeError("Admin Dashboard Service not initialized")
    return request.app.state.admin_dashboard_service


@router.get("/docs")
async def get_documentation(
    section: Optional[str] = None,
    admin_service: AdminDashboardService = Depends(get_admin_dashboard_service),
    user_id: str = "admin"  # TODO: Get from auth context
):
    """Get Platform SDK documentation."""
    # Check access
    has_access = await admin_service.check_access(user_id, "developer")
    if not has_access:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        docs = await admin_service.developer_view_service.get_documentation(section)
        return docs
    except Exception as e:
        logger.error(f"Failed to get documentation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/examples")
async def get_code_examples(
    category: Optional[str] = None,
    admin_service: AdminDashboardService = Depends(get_admin_dashboard_service),
    user_id: str = "admin"  # TODO: Get from auth context
):
    """Get code examples."""
    # Check access
    has_access = await admin_service.check_access(user_id, "developer")
    if not has_access:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        examples = await admin_service.developer_view_service.get_code_examples(category)
        return examples
    except Exception as e:
        logger.error(f"Failed to get code examples: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/patterns")
async def get_patterns(
    admin_service: AdminDashboardService = Depends(get_admin_dashboard_service),
    user_id: str = "admin"  # TODO: Get from auth context
):
    """Get patterns and best practices."""
    # Check access
    has_access = await admin_service.check_access(user_id, "developer")
    if not has_access:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        patterns = await admin_service.developer_view_service.get_patterns()
        return patterns
    except Exception as e:
        logger.error(f"Failed to get patterns: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/solution-builder/validate")
async def validate_solution(
    request: SolutionValidationRequest,
    admin_service: AdminDashboardService = Depends(get_admin_dashboard_service),
    user_id: str = "admin"  # TODO: Get from auth context
):
    """Validate a solution configuration (Playground - gated)."""
    # Check access to playground feature
    has_access = await admin_service.check_access(user_id, "developer", "playground")
    if not has_access:
        raise HTTPException(status_code=403, detail="Playground feature not available")
    
    try:
        result = await admin_service.developer_view_service.validate_solution(
            request.solution_config
        )
        return result
    except Exception as e:
        logger.error(f"Failed to validate solution: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/solution-builder/preview")
async def preview_solution(
    request: SolutionValidationRequest,
    admin_service: AdminDashboardService = Depends(get_admin_dashboard_service),
    user_id: str = "admin"  # TODO: Get from auth context
):
    """Preview a solution structure (Playground - gated)."""
    # Check access to playground feature
    has_access = await admin_service.check_access(user_id, "developer", "playground")
    if not has_access:
        raise HTTPException(status_code=403, detail="Playground feature not available")
    
    try:
        preview = await admin_service.developer_view_service.preview_solution(
            request.solution_config
        )
        return preview
    except Exception as e:
        logger.error(f"Failed to preview solution: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/features/submit")
async def submit_feature_request(
    request: FeatureRequestSubmission,
    admin_service: AdminDashboardService = Depends(get_admin_dashboard_service),
    user_id: str = "admin"  # TODO: Get from auth context
):
    """Submit a feature request (gated - 'Coming Soon' for MVP)."""
    # Check access to feature submission
    has_access = await admin_service.check_access(user_id, "developer", "feature_submission")
    if not has_access:
        return {
            "status": "coming_soon",
            "message": "Feature submission is coming soon! This will enable developers to submit feature proposals for platform team review."
        }
    
    try:
        result = await admin_service.developer_view_service.submit_feature_request(
            request.dict()
        )
        return result
    except Exception as e:
        logger.error(f"Failed to submit feature request: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
