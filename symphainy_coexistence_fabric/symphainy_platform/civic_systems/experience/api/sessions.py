"""
Session API Endpoints
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

from fastapi import APIRouter, HTTPException, Depends, Request, Query
from typing import Dict, Any, Optional

from utilities import get_logger
from ..models.session_model import SessionCreateRequest, SessionCreateResponse
from ..sdk.runtime_client import RuntimeClient
from ..sdk.experience_sdk import ExperienceSDK
from symphainy_platform.civic_systems.smart_city.sdk.security_guard_sdk import SecurityGuardSDK
from symphainy_platform.civic_systems.smart_city.sdk.traffic_cop_sdk import TrafficCopSDK


router = APIRouter(prefix="/api/session", tags=["sessions"])
logger = get_logger("ExperienceAPI.Sessions")


def get_runtime_client() -> RuntimeClient:
    """Dependency to get Runtime client."""
    # In production, this would come from DI container
    return RuntimeClient(runtime_url="http://runtime:8000")


def get_experience_sdk(runtime_client: RuntimeClient = Depends(get_runtime_client)) -> ExperienceSDK:
    """Dependency to get Experience SDK (facade over RuntimeClient)."""
    return ExperienceSDK(runtime_client)


def get_security_guard_sdk(request: Request) -> SecurityGuardSDK:
    """Dependency to get Security Guard SDK."""
    if not hasattr(request.app.state, "security_guard_sdk"):
        raise RuntimeError("Security Guard SDK not initialized. Check Experience service startup.")
    return request.app.state.security_guard_sdk


def get_traffic_cop_sdk(request: Request) -> TrafficCopSDK:
    """Dependency to get Traffic Cop SDK."""
    if not hasattr(request.app.state, "traffic_cop_sdk"):
        raise RuntimeError("Traffic Cop SDK not initialized. Check Experience service startup.")
    return request.app.state.traffic_cop_sdk


@router.get("/{session_id}")
async def get_session(
    session_id: str,
    tenant_id: Optional[str] = Query(None, description="Tenant ID (optional for anonymous sessions)"),
    experience_sdk: ExperienceSDK = Depends(get_experience_sdk)
):
    """
    Get session details (anonymous or authenticated).
    Uses Experience SDK query_state.
    """
    try:
        state = await experience_sdk.query_state(session_id=session_id, tenant_id=tenant_id)
        session_data = state.get("session")
        if not session_data:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        return session_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get session {session_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/create", response_model=SessionCreateResponse)
async def create_session(
    request: SessionCreateRequest,
    runtime_client: RuntimeClient = Depends(get_runtime_client),
    security_guard_sdk: SecurityGuardSDK = Depends(get_security_guard_sdk),
    traffic_cop_sdk: TrafficCopSDK = Depends(get_traffic_cop_sdk)
):
    """
    Create session via Traffic Cop SDK → Runtime.
    
    Flow:
    1. Authenticate (via Security Guard SDK)
    2. Prepare session intent (via Traffic Cop SDK)
    3. Submit intent to Runtime
    4. Runtime validates via primitives and creates session
    5. Return session_id
    """
    try:
        # 1. Authenticate (via Security Guard SDK)
        auth_result = await security_guard_sdk.authenticate(request.credentials)
        
        if not auth_result:
            raise HTTPException(status_code=401, detail="Authentication failed")
        
        # 2. Prepare session intent (via Traffic Cop SDK)
        session_intent_data = await traffic_cop_sdk.create_session_intent(
            tenant_id=auth_result.tenant_id,
            user_id=auth_result.user_id,
            metadata=request.metadata
        )
        
        # Convert to dict for Runtime
        session_intent = {
            "intent_type": "create_session",
            "tenant_id": session_intent_data.tenant_id,
            "user_id": session_intent_data.user_id,
            "session_id": session_intent_data.session_id,
            "execution_contract": session_intent_data.execution_contract,
            "metadata": request.metadata or {}
        }
        
        # 3. Submit intent to Runtime (Runtime validates via primitives)
        result = await runtime_client.create_session(session_intent)
        
        # 4. Extract session_id from execution result
        session_id = result.get("session_id") or session_intent_data.session_id
        
        return SessionCreateResponse(
            session_id=session_id,
            tenant_id=auth_result.tenant_id,
            user_id=auth_result.user_id,
            created_at=result.get("created_at", "")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/create-anonymous", response_model=SessionCreateResponse)
async def create_anonymous_session(
    request: Optional[Dict[str, Any]] = None,
    runtime_client: RuntimeClient = Depends(get_runtime_client),
    traffic_cop_sdk: TrafficCopSDK = Depends(get_traffic_cop_sdk)
):
    """
    Create anonymous session (no authentication required).
    
    Flow:
    1. Prepare anonymous session intent (via Traffic Cop SDK)
    2. Submit intent to Runtime
    3. Runtime validates and creates anonymous session
    4. Return session_id
    
    This is the session-first pattern: sessions exist before authentication.
    """
    try:
        # Create anonymous session intent (no tenant_id, user_id)
        session_intent_data = await traffic_cop_sdk.create_anonymous_session_intent(
            metadata=request.get("metadata") if request else None
        )
        
        # Convert to dict for Runtime
        session_intent = {
            "intent_type": "create_session",
            "tenant_id": None,  # Anonymous - no tenant
            "user_id": None,    # Anonymous - no user
            "session_id": session_intent_data.session_id,
            "execution_contract": session_intent_data.execution_contract,
            "metadata": (request.get("metadata") if request else {}) or {}
        }
        
        # Submit to Runtime
        result = await runtime_client.create_session(session_intent)
        
        session_id = result.get("session_id") or session_intent_data.session_id
        
        return SessionCreateResponse(
            session_id=session_id,
            tenant_id=None,  # Empty for anonymous
            user_id=None,    # Empty for anonymous
            created_at=result.get("created_at", "")
        )
    except Exception as e:
        logger.error(f"Failed to create anonymous session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.patch("/{session_id}/upgrade", response_model=SessionCreateResponse)
async def upgrade_session(
    session_id: str,
    request: Dict[str, Any],  # { user_id, tenant_id, access_token, metadata }
    runtime_client: RuntimeClient = Depends(get_runtime_client),
    security_guard_sdk: SecurityGuardSDK = Depends(get_security_guard_sdk)
):
    """
    Upgrade anonymous session with authentication.
    
    Flow:
    1. Validate access_token (user is authenticated)
    2. Get existing session (must exist, may be anonymous)
    3. Upgrade session with user_id, tenant_id
    4. Return upgraded session
    
    This upgrades an existing anonymous session with identity after authentication.
    """
    try:
        # 1. Validate authentication
        access_token = request.get("access_token")
        if not access_token:
            raise HTTPException(status_code=401, detail="Access token required")
        
        auth_result = await security_guard_sdk.validate_token(access_token)
        if not auth_result:
            raise HTTPException(status_code=401, detail="Invalid access token")
        
        # 2. Get existing session (may be anonymous)
        session_data = await runtime_client.get_session(session_id, None)  # Try without tenant_id first
        
        if not session_data:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        # 3. Upgrade session (add user_id, tenant_id)
        upgraded = await runtime_client.upgrade_session(
            session_id=session_id,
            user_id=auth_result.user_id,
            tenant_id=auth_result.tenant_id,
            metadata=request.get("metadata")
        )
        
        return SessionCreateResponse(
            session_id=session_id,
            tenant_id=auth_result.tenant_id,
            user_id=auth_result.user_id,
            created_at=upgraded.get("created_at", "")
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upgrade session: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
