"""
Intent Helper - Thin layer for submitting Control Tower intents

This module provides helper functions for the Admin Dashboard API to submit
intents to the Control Tower capability, following the platform architecture
where everything flows through intents.

Pattern:
    Admin Dashboard API → intent_helper.submit_control_tower_intent() → Runtime → Control Tower
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

from typing import Dict, Any, Optional
from fastapi import Request, HTTPException

from utilities import get_logger
from ..sdk.runtime_client import RuntimeClient
from ..sdk.experience_sdk import ExperienceSDK

logger = get_logger("AdminDashboard.IntentHelper")


# Control Tower solution ID
CONTROL_TOWER_SOLUTION_ID = "control_tower"

# Default tenant for admin operations (in production, get from auth)
DEFAULT_ADMIN_TENANT = "platform_admin"


async def submit_control_tower_intent(
    request: Request,
    intent_type: str,
    parameters: Optional[Dict[str, Any]] = None,
    session_id: Optional[str] = None,
    tenant_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Submit an intent to the Control Tower capability.
    
    This is the thin layer that converts Admin Dashboard API calls
    into proper intent submissions to the platform.
    
    Args:
        request: FastAPI request (for getting app state)
        intent_type: Control Tower intent type (e.g., "get_platform_statistics")
        parameters: Intent parameters
        session_id: Optional session ID (uses admin session if not provided)
        tenant_id: Optional tenant ID (uses platform_admin if not provided)
    
    Returns:
        Dict with intent execution result (artifacts from Control Tower)
    
    Raises:
        HTTPException: On execution failure
    """
    try:
        # Get Runtime client
        runtime_client = RuntimeClient(runtime_url="http://runtime:8000")
        experience_sdk = ExperienceSDK(runtime_client)
        
        # Use defaults if not provided
        effective_tenant_id = tenant_id or DEFAULT_ADMIN_TENANT
        effective_session_id = session_id or f"admin_session_{effective_tenant_id}"
        
        # Submit intent via Experience SDK
        result = await experience_sdk.invoke_intent(
            intent_type=intent_type,
            parameters=parameters or {},
            tenant_id=effective_tenant_id,
            session_id=effective_session_id,
            solution_id=CONTROL_TOWER_SOLUTION_ID,
            metadata={"source": "admin_dashboard"}
        )
        
        logger.info(f"Control Tower intent '{intent_type}' executed: status={result.get('status')}")
        
        # Extract artifacts (the actual response data)
        artifacts = result.get("artifacts", {})
        
        # If execution failed, raise error
        status = result.get("status", "unknown")
        if status in ("failed", "error"):
            error_msg = result.get("error") or artifacts.get("error") or "Intent execution failed"
            raise HTTPException(status_code=500, detail=error_msg)
        
        return artifacts
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to submit Control Tower intent '{intent_type}': {e}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to execute {intent_type}: {str(e)}"
        )


async def get_user_context(request: Request) -> Dict[str, Any]:
    """
    Extract user context from request (auth headers, session).
    
    For MVP, returns default admin context. In production, this would
    extract user_id, tenant_id from JWT token.
    
    Args:
        request: FastAPI request
    
    Returns:
        Dict with user_id, tenant_id, session_id
    """
    # TODO: Extract from JWT token in production
    # For now, use defaults
    return {
        "user_id": "admin",
        "tenant_id": DEFAULT_ADMIN_TENANT,
        "session_id": f"admin_session_{DEFAULT_ADMIN_TENANT}"
    }
