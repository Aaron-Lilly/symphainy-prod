"""
Intent Submission API Endpoints
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
from ..models.intent_request_model import IntentSubmitRequest, IntentSubmitResponse
from ..sdk.runtime_client import RuntimeClient
from symphainy_platform.runtime.intent_model import IntentFactory
from symphainy_platform.civic_systems.smart_city.sdk.traffic_cop_sdk import TrafficCopSDK


router = APIRouter(prefix="/api/intent", tags=["intents"])
logger = get_logger("ExperienceAPI.Intents")


def get_runtime_client() -> RuntimeClient:
    """Dependency to get Runtime client."""
    return RuntimeClient(runtime_url="http://runtime:8000")


def get_traffic_cop_sdk() -> TrafficCopSDK:
    """Dependency to get Traffic Cop SDK."""
    raise NotImplementedError("Traffic Cop SDK must be injected via DI")


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
        # Extract tenant_id from session (would come from session state)
        # For MVP, we'll need to get tenant_id from session validation
        session_validation = await traffic_cop_sdk.validate_session(
            request.session_id,
            tenant_id="unknown"  # TODO: Get from session state
        )
        
        if not session_validation or not session_validation.is_valid:
            raise HTTPException(status_code=401, detail="Invalid session")
        
        tenant_id = session_validation.tenant_id
        
        # 2. Create intent
        intent = IntentFactory.create_intent(
            intent_type=request.intent_type,
            tenant_id=tenant_id,
            session_id=request.session_id,
            solution_id="default",  # TODO: Get from session or request
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
