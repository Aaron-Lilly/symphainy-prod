"""
Runtime API - FastAPI Service for Runtime

Exposes Runtime capabilities via REST API.

WHAT (Runtime Role): I expose Runtime capabilities via API
HOW (Runtime Implementation): I provide REST endpoints for intent submission, session management, execution status
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException, Depends
from typing import Dict, Any, Optional
from pydantic import BaseModel

from utilities import get_logger
from .execution_lifecycle_manager import ExecutionLifecycleManager
from .intent_model import Intent, IntentFactory
from .intent_registry import IntentRegistry
from .state_surface import StateSurface
from .wal import WriteAheadLog
from .transactional_outbox import TransactionalOutbox


# Request/Response Models
class SessionCreateRequest(BaseModel):
    """Request to create a session."""
    intent_type: str = "create_session"
    tenant_id: str
    user_id: str
    session_id: Optional[str] = None
    execution_contract: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class SessionCreateResponse(BaseModel):
    """Response from session creation."""
    session_id: str
    tenant_id: str
    user_id: str
    created_at: str


class IntentSubmitRequest(BaseModel):
    """Request to submit an intent."""
    intent_id: Optional[str] = None
    intent_type: str
    tenant_id: str
    session_id: str
    solution_id: str
    parameters: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}


class IntentSubmitResponse(BaseModel):
    """Response from intent submission."""
    execution_id: str
    intent_id: str
    status: str
    created_at: str


class ExecutionStatusResponse(BaseModel):
    """Response from execution status query."""
    execution_id: str
    status: str
    intent_id: str
    artifacts: Optional[Dict[str, Any]] = None
    events: Optional[list] = None
    error: Optional[str] = None


class RuntimeAPI:
    """
    Runtime API service.
    
    Exposes Runtime capabilities via REST API.
    """
    
    def __init__(
        self,
        execution_lifecycle_manager: ExecutionLifecycleManager,
        state_surface: StateSurface
    ):
        """
        Initialize Runtime API.
        
        Args:
            execution_lifecycle_manager: Execution lifecycle manager
            state_surface: State surface for execution state
        """
        self.execution_lifecycle_manager = execution_lifecycle_manager
        self.state_surface = state_surface
        self.logger = get_logger(self.__class__.__name__)
    
    async def create_session(
        self,
        request: SessionCreateRequest
    ) -> SessionCreateResponse:
        """
        Create session via Runtime.
        
        Args:
            request: Session creation request
        
        Returns:
            Session creation response
        """
        try:
            # Create session intent
            intent = IntentFactory.create_intent(
                intent_type=request.intent_type,
                tenant_id=request.tenant_id,
                session_id=request.session_id or f"session_{request.tenant_id}_{request.user_id}",
                solution_id="default",
                parameters={
                    "user_id": request.user_id,
                    "execution_contract": request.execution_contract or {}
                },
                metadata=request.metadata or {}
            )
            
            # Execute session creation intent
            result = await self.execution_lifecycle_manager.execute(intent)
            
            if not result.success:
                raise HTTPException(status_code=500, detail=result.error)
            
            # Extract session_id from artifacts
            session_id = result.artifacts.get("session_id") or intent.session_id
            
            return SessionCreateResponse(
                session_id=session_id,
                tenant_id=request.tenant_id,
                user_id=request.user_id,
                created_at=result.metadata.get("created_at", "")
            )
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Failed to create session: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
    async def submit_intent(
        self,
        request: IntentSubmitRequest
    ) -> IntentSubmitResponse:
        """
        Submit intent for execution.
        
        Args:
            request: Intent submission request
        
        Returns:
            Intent submission response
        """
        try:
            # Create intent
            intent = IntentFactory.create_intent(
                intent_type=request.intent_type,
                tenant_id=request.tenant_id,
                session_id=request.session_id,
                solution_id=request.solution_id,
                parameters=request.parameters,
                metadata=request.metadata,
                intent_id=request.intent_id
            )
            
            # Execute intent
            result = await self.execution_lifecycle_manager.execute(intent)
            
            if not result.success:
                raise HTTPException(status_code=500, detail=result.error)
            
            return IntentSubmitResponse(
                execution_id=result.execution_id,
                intent_id=intent.intent_id,
                status="accepted" if result.success else "failed",
                created_at=result.metadata.get("created_at", "")
            )
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Failed to submit intent: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
    async def get_execution_status(
        self,
        execution_id: str,
        tenant_id: str
    ) -> ExecutionStatusResponse:
        """
        Get execution status.
        
        Args:
            execution_id: Execution identifier
            tenant_id: Tenant identifier
        
        Returns:
            Execution status response
        """
        try:
            # Get execution state from state surface
            execution_state = await self.state_surface.get_execution_state(
                execution_id,
                tenant_id
            )
            
            if not execution_state:
                raise HTTPException(status_code=404, detail="Execution not found")
            
            return ExecutionStatusResponse(
                execution_id=execution_id,
                status=execution_state.get("status", "unknown"),
                intent_id=execution_state.get("intent_id", ""),
                artifacts=execution_state.get("artifacts"),
                events=execution_state.get("events"),
                error=execution_state.get("error")
            )
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Failed to get execution status: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


def create_runtime_app(
    execution_lifecycle_manager: ExecutionLifecycleManager,
    state_surface: StateSurface
) -> FastAPI:
    """
    Create FastAPI app for Runtime API.
    
    Args:
        execution_lifecycle_manager: Execution lifecycle manager
        state_surface: State surface
    
    Returns:
        FastAPI application
    """
    app = FastAPI(
        title="Symphainy Runtime API",
        description="Runtime API - Intent submission and execution management",
        version="2.0.0"
    )
    
    runtime_api = RuntimeAPI(execution_lifecycle_manager, state_surface)
    
    @app.post("/api/session/create", response_model=SessionCreateResponse)
    async def create_session(request: SessionCreateRequest):
        """Create a new session."""
        return await runtime_api.create_session(request)
    
    @app.post("/api/intent/submit", response_model=IntentSubmitResponse)
    async def submit_intent(request: IntentSubmitRequest):
        """Submit intent for execution."""
        return await runtime_api.submit_intent(request)
    
    @app.get("/api/execution/{execution_id}/status", response_model=ExecutionStatusResponse)
    async def get_execution_status(
        execution_id: str,
        tenant_id: str
    ):
        """Get execution status."""
        return await runtime_api.get_execution_status(execution_id, tenant_id)
    
    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return {"status": "healthy", "service": "runtime", "version": "2.0.0"}
    
    return app
