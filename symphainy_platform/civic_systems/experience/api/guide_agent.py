"""
Guide Agent API - FastAPI Routes for Guide Agent

API endpoints for Guide Agent interactions.
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
from symphainy_platform.runtime.execution_context import ExecutionContext
from symphainy_platform.runtime.state_surface import StateSurface
from symphainy_platform.foundations.public_works.foundation_service import PublicWorksFoundationService

logger = get_logger("GuideAgentAPI")

router = APIRouter(prefix="/api/v1/guide-agent", tags=["guide-agent"])


# Request/Response Models
class ChatMessageRequest(BaseModel):
    """Request model for chat message."""
    message: str
    session_id: str
    tenant_id: str


class ChatMessageResponse(BaseModel):
    """Response model for chat message."""
    success: bool
    response: Optional[str] = None
    intent_analysis: Optional[Dict[str, Any]] = None
    journey_guidance: Optional[Dict[str, Any]] = None
    routing_info: Optional[Dict[str, Any]] = None
    session_id: str
    error: Optional[str] = None


class AnalyzeIntentRequest(BaseModel):
    """Request model for intent analysis."""
    message: str
    user_context: Optional[Dict[str, Any]] = None
    tenant_id: str


class AnalyzeIntentResponse(BaseModel):
    """Response model for intent analysis."""
    success: bool
    intent_analysis: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class JourneyGuidanceRequest(BaseModel):
    """Request model for journey guidance."""
    user_state: Optional[Dict[str, Any]] = None
    tenant_id: str


class JourneyGuidanceResponse(BaseModel):
    """Response model for journey guidance."""
    success: bool
    guidance: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class RouteToPillarRequest(BaseModel):
    """Request model for pillar routing."""
    pillar: str
    user_intent: Dict[str, Any]
    session_id: str
    tenant_id: str


class RouteToPillarResponse(BaseModel):
    """Response model for pillar routing."""
    success: bool
    routing_info: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# Dependency to get Guide Agent Service
def get_guide_agent_service(request: Request) -> Any:
    """
    Get Guide Agent Service instance from app state.
    
    Args:
        request: FastAPI request object
    
    Returns:
        GuideAgentService instance
    """
    if not hasattr(request.app.state, "guide_agent_service"):
        raise HTTPException(
            status_code=503,
            detail="Guide Agent Service not initialized. Check Experience service startup."
        )
    return request.app.state.guide_agent_service


# Dependency to get Execution Context
async def get_execution_context(
    tenant_id: str,
    session_id: Optional[str] = None,
    request: Optional[Request] = None
) -> ExecutionContext:
    """
    Create Execution Context for request.
    
    Args:
        tenant_id: Tenant identifier
        session_id: Optional session identifier
        request: FastAPI request object (for accessing app state)
    
    Returns:
        ExecutionContext instance
    """
    from symphainy_platform.runtime.execution_context import ExecutionContext
    from utilities import generate_session_id, get_clock
    
    if not session_id:
        session_id = generate_session_id()
    
    # Get Public Works from app state if available
    public_works = None
    if request and hasattr(request.app.state, "public_works"):
        public_works = request.app.state.public_works
    
    # Create State Surface if Public Works available
    state_surface = None
    if public_works:
        state_abstraction = public_works.get_state_abstraction()
        if state_abstraction:
            from symphainy_platform.runtime.state_surface import StateSurface
            state_surface = StateSurface(
                state_abstraction=state_abstraction,
                use_memory=(state_abstraction is None)
            )
    
    context = ExecutionContext(
        session_id=session_id,
        tenant_id=tenant_id,
        intent_id=None,
        state_surface=state_surface,
        clock=get_clock()
    )
    
    return context


@router.post("/chat", response_model=ChatMessageResponse)
async def chat_with_guide_agent(
    request: ChatMessageRequest,
    http_request: Request,
    guide_service: Any = Depends(get_guide_agent_service)
):
    """
    Chat with Guide Agent.
    
    Main endpoint for Guide Agent chat interface.
    """
    try:
        # Create execution context
        context = await get_execution_context(
            tenant_id=request.tenant_id,
            session_id=request.session_id,
            request=http_request
        )
        
        # Process chat message
        result = await guide_service.process_chat_message(
            message=request.message,
            session_id=request.session_id,
            tenant_id=request.tenant_id,
            context=context
        )
        
        return ChatMessageResponse(
            success=result.get("success", False),
            response=result.get("response"),
            intent_analysis=result.get("intent_analysis"),
            journey_guidance=result.get("journey_guidance"),
            routing_info=result.get("routing_info"),
            session_id=request.session_id,
            error=result.get("error")
        )
    except Exception as e:
        logger.error(f"❌ Guide Agent chat failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-intent", response_model=AnalyzeIntentResponse)
async def analyze_user_intent(
    request: AnalyzeIntentRequest,
    http_request: Request,
    guide_service: Any = Depends(get_guide_agent_service)
):
    """
    Analyze user intent.
    
    Analyze what the user wants to accomplish.
    """
    try:
        # Create execution context
        context = await get_execution_context(
            tenant_id=request.tenant_id,
            request=http_request
        )
        
        # Analyze intent
        result = await guide_service.analyze_user_intent(
            message=request.message,
            user_context=request.user_context,
            context=context
        )
        
        return AnalyzeIntentResponse(
            success=result.get("success", False),
            intent_analysis=result.get("intent_analysis"),
            error=result.get("error")
        )
    except Exception as e:
        logger.error(f"❌ Intent analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/guidance", response_model=JourneyGuidanceResponse)
async def get_journey_guidance(
    request: JourneyGuidanceRequest,
    http_request: Request,
    guide_service: Any = Depends(get_guide_agent_service)
):
    """
    Get journey guidance.
    
    Get recommended next steps based on user's current state.
    """
    try:
        # Create execution context
        context = await get_execution_context(
            tenant_id=request.tenant_id,
            request=http_request
        )
        
        # Get journey guidance
        result = await guide_service.get_journey_guidance(
            user_state=request.user_state,
            context=context
        )
        
        return JourneyGuidanceResponse(
            success=result.get("success", False),
            guidance=result.get("guidance"),
            error=result.get("error")
        )
    except Exception as e:
        logger.error(f"❌ Journey guidance failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{session_id}")
async def get_conversation_history(
    session_id: str,
    tenant_id: str,
    http_request: Request,
    guide_service: Any = Depends(get_guide_agent_service)
):
    """
    Get conversation history.
    
    Retrieve conversation history for a session.
    """
    try:
        # Create execution context
        context = await get_execution_context(
            tenant_id=tenant_id,
            session_id=session_id,
            request=http_request
        )
        
        # Get conversation history
        result = await guide_service.get_conversation_history(
            session_id=session_id,
            tenant_id=tenant_id,
            context=context
        )
        
        return result
    except Exception as e:
        logger.error(f"❌ Get conversation history failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/route-to-pillar", response_model=RouteToPillarResponse)
async def route_to_pillar_liaison(
    request: RouteToPillarRequest,
    http_request: Request,
    guide_service: Any = Depends(get_guide_agent_service)
):
    """
    Route to pillar liaison agent.
    
    Route user to appropriate pillar liaison agent.
    """
    try:
        # Create execution context
        context = await get_execution_context(
            tenant_id=request.tenant_id,
            session_id=request.session_id,
            request=http_request
        )
        
        # Route to pillar liaison
        result = await guide_service.route_to_pillar_liaison(
            pillar=request.pillar,
            user_intent=request.user_intent,
            session_id=request.session_id,
            tenant_id=request.tenant_id,
            context=context
        )
        
        return RouteToPillarResponse(
            success=result.get("success", False),
            routing_info=result.get("routing_info"),
            error=result.get("error")
        )
    except Exception as e:
        logger.error(f"❌ Route to pillar failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
