"""
Intent Submission API Endpoints
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
from typing import Dict, Any

from utilities import get_logger
from ..models.intent_request_model import IntentSubmitRequest, IntentSubmitResponse
from ..sdk.runtime_client import RuntimeClient
from symphainy_platform.runtime.intent_model import IntentFactory
from symphainy_platform.civic_systems.smart_city.sdk.traffic_cop_sdk import TrafficCopSDK


router = APIRouter(prefix="/api/intent", tags=["intents"])
logger = get_logger("ExperienceAPI.Intents")


def get_runtime_client() -> RuntimeClient:
    """Dependency to get Runtime client."""
    return RuntimeClient(runtime_url="http://runtime:8000")


def get_traffic_cop_sdk(request: Request) -> TrafficCopSDK:
    """Dependency to get Traffic Cop SDK."""
    if not hasattr(request.app.state, "traffic_cop_sdk"):
        raise RuntimeError("Traffic Cop SDK not initialized. Check Experience service startup.")
    return request.app.state.traffic_cop_sdk


@router.post("/submit", response_model=IntentSubmitResponse)
async def submit_intent(
    request: IntentSubmitRequest,
    runtime_client: RuntimeClient = Depends(get_runtime_client),
    traffic_cop_sdk: TrafficCopSDK = Depends(get_traffic_cop_sdk)
):
    """
    Submit intent via Runtime.
    
    Flow:
    1. Validate session (via Traffic Cop SDK)
    2. Create intent
    3. Submit intent to Runtime
    4. Return execution_id
    """
    try:
        # 1. Validate session (via Traffic Cop SDK - prepares validation contract)
        # For MVP, we'll extract tenant_id from parameters or use a default
        # In production, this would come from session state
        # Extract tenant_id from request body
        # CRITICAL: For multi-tenant support, tenant_id must come from request body
        # IntentSubmitRequest now has tenant_id as a required field
        tenant_id = request.tenant_id
        logger.info(f"🔵 EXPERIENCE API: Extracted tenant_id={tenant_id} from request")
        if not tenant_id:
            # This is a critical error - tenant_id is required for multi-tenant operation
            logger.error("❌ CRITICAL: tenant_id is missing from request - multi-tenant operation requires tenant_id")
            raise ValueError("tenant_id is required in request body for multi-tenant operation")
        
        # Try to validate session (for MVP, we'll be lenient if session doesn't exist)
        try:
            session_validation = await traffic_cop_sdk.validate_session(
                request.session_id,
                tenant_id=tenant_id
            )
            
            if session_validation and session_validation.is_valid:
                tenant_id = session_validation.tenant_id
            else:
                # For MVP, if session doesn't exist, we'll allow it (Runtime will handle)
                logger.warning(f"Session validation returned invalid for {request.session_id}, proceeding anyway for MVP")
        except Exception as e:
            # For MVP, if validation fails, we'll proceed with tenant_id from parameters
            logger.warning(f"Session validation failed (non-fatal for MVP): {e}")
        
        # 2. Get solution_id from request metadata, session, or use default
        solution_id = (
            request.metadata.get("solution_id") or
            request.parameters.get("solution_id") or
            "default"
        )
        
        # Try to get solution_id from session if available
        try:
            # Get session state from Runtime to extract solution_id
            session_state = await runtime_client.get_session_state(
                session_id=request.session_id,
                tenant_id=tenant_id
            )
            if session_state and session_state.get("solution_id"):
                solution_id = session_state["solution_id"]
        except Exception as e:
            # If session lookup fails, use solution_id from above
            logger.debug(f"Could not get solution_id from session: {e}")
        
        # 3. Create intent
        intent = IntentFactory.create_intent(
            intent_type=request.intent_type,
            tenant_id=tenant_id,
            session_id=request.session_id,
            solution_id=solution_id,
            parameters=request.parameters,
            metadata=request.metadata
        )
        
        # 3. Submit intent to Runtime (Runtime validates via primitives)
        result = await runtime_client.submit_intent(intent)
        
        return IntentSubmitResponse(
            execution_id=result.get("execution_id", ""),
            intent_id=intent.intent_id,
            status=result.get("status", "accepted"),
            created_at=result.get("created_at", "")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to submit intent: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
