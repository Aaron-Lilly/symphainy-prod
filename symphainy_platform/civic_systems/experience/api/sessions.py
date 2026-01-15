"""
Session API Endpoints
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[6]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any

from utilities import get_logger
from ..models.session_model import SessionCreateRequest, SessionCreateResponse
from ..sdk.runtime_client import RuntimeClient
from symphainy_platform.civic_systems.smart_city.sdk.security_guard_sdk import SecurityGuardSDK
from symphainy_platform.civic_systems.smart_city.sdk.traffic_cop_sdk import TrafficCopSDK


router = APIRouter(prefix="/api/session", tags=["sessions"])
logger = get_logger("ExperienceAPI.Sessions")


def get_runtime_client() -> RuntimeClient:
    """Dependency to get Runtime client."""
    # In production, this would come from DI container
    return RuntimeClient(runtime_url="http://runtime:8000")


def get_security_guard_sdk() -> SecurityGuardSDK:
    """Dependency to get Security Guard SDK."""
    # In production, this would come from DI container with Public Works
    # For now, this is a placeholder - will be injected properly
    raise NotImplementedError("Security Guard SDK must be injected via DI")


def get_traffic_cop_sdk() -> TrafficCopSDK:
    """Dependency to get Traffic Cop SDK."""
    # In production, this would come from DI container with Public Works
    # For now, this is a placeholder - will be injected properly
    raise NotImplementedError("Traffic Cop SDK must be injected via DI")


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
