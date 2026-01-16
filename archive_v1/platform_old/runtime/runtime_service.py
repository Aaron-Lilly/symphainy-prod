"""
Runtime Service - FastAPI Service for Runtime Plane

Provides:
- /intent/submit - Submit intent for execution
- /session/create - Create new session
- /session/{id} - Get session
- /execution/{id}/status - Get execution status

No business logic. No realms imported.
"""

from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

from utilities import (
    get_logger, LogLevel, LogCategory,
    generate_execution_id,
    get_clock,
    PlatformError, DomainError
)

from .session import Session
from .state_surface import StateSurface
from .wal import WriteAheadLog, WALEventType
from .saga import SagaCoordinator, SagaState


# Request/Response Models
class CreateSessionRequest(BaseModel):
    """Request to create a session."""
    tenant_id: str = Field(..., description="Tenant identifier (mandatory)")
    user_id: str = Field(..., description="User identifier")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Optional initial context")


class CreateSessionResponse(BaseModel):
    """Response from session creation."""
    success: bool
    session: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class GetSessionResponse(BaseModel):
    """Response from getting a session."""
    success: bool
    session: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class SubmitIntentRequest(BaseModel):
    """Request to submit an intent."""
    intent_type: str = Field(..., description="Intent type (e.g., 'content.upload')")
    realm: str = Field(..., description="Target realm")
    session_id: str = Field(..., description="Session identifier (required)")
    tenant_id: str = Field(..., description="Tenant identifier (mandatory)")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Intent payload")


class SubmitIntentResponse(BaseModel):
    """Response from intent submission."""
    success: bool
    execution_id: Optional[str] = None
    error: Optional[str] = None


class GetExecutionStatusResponse(BaseModel):
    """Response from getting execution status."""
    success: bool
    execution_id: Optional[str] = None
    status: Optional[str] = None
    state: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# Runtime Service
class RuntimeService:
    """
    Runtime Service - FastAPI service for Runtime Plane.
    
    Provides endpoints for:
    - Session lifecycle
    - Intent submission
    - Execution status
    """
    
    def __init__(
        self,
        state_surface: StateSurface,
        wal: WriteAheadLog,
        saga_coordinator: SagaCoordinator
    ):
        """
        Initialize runtime service.
        
        Args:
            state_surface: State surface for state operations
            wal: Write-ahead log for event logging
            saga_coordinator: Saga coordinator for saga management
        """
        self.state_surface = state_surface
        self.wal = wal
        self.saga_coordinator = saga_coordinator
        self._sessions: Dict[str, Session] = {}  # In-memory session cache
        self.logger = get_logger("runtime_service", LogLevel.INFO, LogCategory.PLATFORM)
        self.clock = get_clock()
    
    async def create_session(
        self,
        request: CreateSessionRequest
    ) -> CreateSessionResponse:
        """
        Create a new session.
        
        Args:
            request: Session creation request
        
        Returns:
            Session creation response
        """
        try:
            # Create session
            session = Session.create(
                tenant_id=request.tenant_id,
                user_id=request.user_id,
                context=request.context
            )
            
            # Store in cache
            self._sessions[session.session_id] = session
            
            # Store in state surface
            await self.state_surface.set_session_state(
                session_id=session.session_id,
                tenant_id=session.tenant_id,
                state=session.to_dict()
            )
            
            # Log to WAL
            await self.wal.append(
                event_type=WALEventType.SESSION_CREATED,
                tenant_id=session.tenant_id,
                payload={
                    "session_id": session.session_id,
                    "user_id": session.user_id,
                    "context": session.context
                }
            )
            
            return CreateSessionResponse(
                success=True,
                session=session.to_dict()
            )
        except Exception as e:
            return CreateSessionResponse(
                success=False,
                error=str(e)
            )
    
    async def get_session(
        self,
        session_id: str,
        tenant_id: str
    ) -> GetSessionResponse:
        """
        Get session by ID.
        
        Args:
            session_id: Session identifier
            tenant_id: Tenant identifier (for isolation)
        
        Returns:
            Session response
        """
        try:
            # Check cache first
            if session_id in self._sessions:
                session = self._sessions[session_id]
                if session.tenant_id == tenant_id:
                    return GetSessionResponse(
                        success=True,
                        session=session.to_dict()
                    )
            
            # Load from state surface
            state = await self.state_surface.get_session_state(session_id, tenant_id)
            if state:
                return GetSessionResponse(
                    success=True,
                    session=state
                )
            
            return GetSessionResponse(
                success=False,
                error="Session not found"
            )
        except Exception as e:
            return GetSessionResponse(
                success=False,
                error=str(e)
            )
    
    async def submit_intent(
        self,
        request: SubmitIntentRequest
    ) -> SubmitIntentResponse:
        """
        Submit intent for execution.
        
        Args:
            request: Intent submission request
        
        Returns:
            Intent submission response
        """
        try:
            # Verify session exists
            session_response = await self.get_session(request.session_id, request.tenant_id)
            if not session_response.success or not session_response.session:
                return SubmitIntentResponse(
                    success=False,
                    error="Session not found"
                )
            
            # Create execution ID
            execution_id = generate_execution_id()
            
            # Log intent to WAL
            await self.wal.append(
                event_type=WALEventType.INTENT_RECEIVED,
                tenant_id=request.tenant_id,
                payload={
                    "execution_id": execution_id,
                    "session_id": request.session_id,
                    "intent_type": request.intent_type,
                    "realm": request.realm,
                    "payload": request.payload
                }
            )
            
            # Create saga for this intent
            saga = await self.saga_coordinator.create_saga(
                tenant_id=request.tenant_id,
                session_id=request.session_id,
                saga_name=f"{request.intent_type}_{request.realm}",
                context={
                    "intent_type": request.intent_type,
                    "realm": request.realm,
                    "payload": request.payload
                }
            )
            
            # Log saga creation
            await self.wal.append(
                event_type=WALEventType.SAGA_STARTED,
                tenant_id=request.tenant_id,
                payload={
                    "saga_id": saga.saga_id,
                    "execution_id": execution_id,
                    "session_id": request.session_id,
                    "saga_name": saga.saga_name
                }
            )
            
            # Store execution state
            await self.state_surface.set_execution_state(
                execution_id=execution_id,
                tenant_id=request.tenant_id,
                state={
                    "execution_id": execution_id,
                    "session_id": request.session_id,
                    "intent_type": request.intent_type,
                    "realm": request.realm,
                    "saga_id": saga.saga_id,
                    "status": "pending",
                    "created_at": self.clock.now_iso()
                }
            )
            
            return SubmitIntentResponse(
                success=True,
                execution_id=execution_id
            )
        except Exception as e:
            self.logger.error(
                "Failed to submit intent",
                session_id=request.session_id,
                tenant_id=request.tenant_id,
                metadata={"intent_type": request.intent_type, "realm": request.realm},
                exc_info=e
            )
            return SubmitIntentResponse(
                success=False,
                error=str(e)
            )
    
    async def get_execution_status(
        self,
        execution_id: str,
        tenant_id: str
    ) -> GetExecutionStatusResponse:
        """
        Get execution status.
        
        Args:
            execution_id: Execution identifier
            tenant_id: Tenant identifier (for isolation)
        
        Returns:
            Execution status response
        """
        try:
            state = await self.state_surface.get_execution_state(execution_id, tenant_id)
            if not state:
                return GetExecutionStatusResponse(
                    success=False,
                    error="Execution not found"
                )
            
            return GetExecutionStatusResponse(
                success=True,
                execution_id=execution_id,
                status=state.get("status", "unknown"),
                state=state
            )
        except Exception as e:
            return GetExecutionStatusResponse(
                success=False,
                error=str(e)
            )


# FastAPI App Factory
def create_runtime_app(
    state_surface: StateSurface,
    wal: WriteAheadLog,
    saga_coordinator: SagaCoordinator
) -> FastAPI:
    """
    Create FastAPI app for Runtime Service.
    
    Args:
        state_surface: State surface
        wal: Write-ahead log
        saga_coordinator: Saga coordinator
    
    Returns:
        FastAPI application
    """
    app = FastAPI(
        title="Symphainy Runtime Plane",
        description="Runtime Plane - Execution Control Plane",
        version="0.1.0"
    )
    
    runtime_service = RuntimeService(state_surface, wal, saga_coordinator)
    
    @app.post("/session/create", response_model=CreateSessionResponse)
    async def create_session(request: CreateSessionRequest):
        """Create a new session."""
        return await runtime_service.create_session(request)
    
    @app.get("/session/{session_id}", response_model=GetSessionResponse)
    async def get_session(
        session_id: str,
        tenant_id: str = Query(..., description="Tenant identifier")
    ):
        """Get session by ID."""
        return await runtime_service.get_session(session_id, tenant_id)
    
    @app.post("/intent/submit", response_model=SubmitIntentResponse)
    async def submit_intent(request: SubmitIntentRequest):
        """Submit intent for execution."""
        return await runtime_service.submit_intent(request)
    
    @app.get("/execution/{execution_id}/status", response_model=GetExecutionStatusResponse)
    async def get_execution_status(
        execution_id: str,
        tenant_id: str = Query(..., description="Tenant identifier")
    ):
        """Get execution status."""
        return await runtime_service.get_execution_status(execution_id, tenant_id)
    
    @app.get("/health")
    async def health():
        """
        Health check endpoint for container orchestration.
        
        Returns component-level health status for Traefik/container health checks.
        """
        components = {
            "state_surface": "healthy" if state_surface else "unavailable",
            "wal": "healthy" if wal else "unavailable",
            "saga_coordinator": "healthy" if saga_coordinator else "unavailable"
        }
        
        # Overall health: healthy if all critical components are available
        overall_health = "healthy" if all(
            status == "healthy" for status in components.values()
        ) else "degraded"
        
        return {
            "status": overall_health,
            "service": "runtime_plane",
            "components": components,
            "timestamp": get_clock().now_iso()
        }
    
    @app.get("/health/ready")
    async def readiness():
        """
        Readiness probe - is service ready to accept traffic?
        
        Used by Traefik/container orchestration to determine if service is ready.
        Separate from liveness probe (/health).
        """
        # Check if all components are initialized
        if state_surface and wal and saga_coordinator:
            return {
                "status": "ready",
                "service": "runtime_plane",
                "timestamp": get_clock().now_iso()
            }
        
        from fastapi import Response
        return Response(
            content='{"status": "not_ready", "service": "runtime_plane"}',
            status_code=503,
            media_type="application/json"
        )
    
    return app
