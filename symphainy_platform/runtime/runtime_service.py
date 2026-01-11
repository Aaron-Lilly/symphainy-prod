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
from datetime import datetime

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
        saga_coordinator: SagaCoordinator,
        curator: Optional[Any] = None  # Optional Curator Foundation for capability lookup
    ):
        """
        Initialize runtime service.
        
        Args:
            state_surface: State surface for state operations
            wal: Write-ahead log for event logging
            saga_coordinator: Saga coordinator for saga management
            curator: Optional Curator Foundation for intent → capability lookup
        """
        self.state_surface = state_surface
        self.wal = wal
        self.saga_coordinator = saga_coordinator
        self.curator = curator
        self._sessions: Dict[str, Session] = {}  # In-memory session cache
        self._observers: Dict[str, Any] = {}  # Smart City observers
    
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
            
            # Lookup capability via Curator (if available)
            capability = None
            if self.curator:
                try:
                    capabilities = await self.curator.lookup_capability_by_intent(request.intent_type)
                    if capabilities:
                        capability = capabilities[0]  # Use first matching capability
                except Exception as e:
                    # Curator lookup failed, continue without capability
                    pass
            
            # Create execution ID
            execution_id = generate_execution_id(request.session_id)
            
            # Log intent to WAL
            wal_payload = {
                "execution_id": execution_id,
                "session_id": request.session_id,
                "intent_type": request.intent_type,
                "realm": request.realm,
                "payload": request.payload
            }
            if capability:
                wal_payload["capability_name"] = capability.capability_name
                wal_payload["service_name"] = capability.service_name
            
            await self.wal.append(
                event_type=WALEventType.INTENT_RECEIVED,
                tenant_id=request.tenant_id,
                payload=wal_payload
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
                    "created_at": get_clock().now_iso()
                }
            )
            
            # Notify observers (Smart City services)
            await self._notify_observers(execution_id, {
                "event_type": "intent_submitted",
                "execution_id": execution_id,
                "session_id": request.session_id,
                "intent_type": request.intent_type,
                "realm": request.realm,
                "tenant_id": request.tenant_id,
                "timestamp": get_clock().now_iso()
            })
            
            return SubmitIntentResponse(
                success=True,
                execution_id=execution_id
            )
        except Exception as e:
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
    
    async def register_observer(self, observer_id: str, observer: Any) -> None:
        """
        Register Smart City service as observer.
        
        Args:
            observer_id: Unique identifier for the observer
            observer: Observer instance (must implement observe_execution method)
        """
        self._observers[observer_id] = observer
        from utilities import get_logger
        logger = get_logger("runtime_service")
        logger.info(f"Registered observer: {observer_id}")
    
    async def _notify_observers(self, execution_id: str, event: dict) -> None:
        """
        Notify all observers of execution event.
        
        Args:
            execution_id: Execution identifier
            event: Event dict with event_type, payload, etc.
        """
        for observer_id, observer in self._observers.items():
            try:
                if hasattr(observer, 'observe_execution'):
                    await observer.observe_execution(execution_id, event)
            except Exception as e:
                from utilities import get_logger
                logger = get_logger("runtime_service")
                logger.error(f"Observer {observer_id} error: {e}", exc_info=e)


# FastAPI App Factory
def create_runtime_app(
    state_surface: StateSurface,
    wal: WriteAheadLog,
    saga_coordinator: SagaCoordinator,
    curator: Optional[Any] = None  # Optional Curator Foundation
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
    
    runtime_service = RuntimeService(state_surface, wal, saga_coordinator, curator=curator)
    
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
        """Health check endpoint."""
        return {"status": "healthy", "service": "runtime_plane"}
    
    return app
