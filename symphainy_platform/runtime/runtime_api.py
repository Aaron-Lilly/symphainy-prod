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
        state_surface: StateSurface,
        artifact_storage: Optional[Any] = None  # ArtifactStorageAbstraction
    ):
        """
        Initialize Runtime API.
        
        Args:
            execution_lifecycle_manager: Execution lifecycle manager
            state_surface: State surface for execution state
            artifact_storage: Optional artifact storage abstraction
        """
        self.execution_lifecycle_manager = execution_lifecycle_manager
        self.state_surface = state_surface
        self.artifact_storage = artifact_storage
        self.logger = get_logger(self.__class__.__name__)
    
    async def create_session(
        self,
        request: SessionCreateRequest
    ) -> SessionCreateResponse:
        """
        Create session via Runtime (internal operation, not an intent).
        
        Session creation is a Runtime-internal operation that:
        1. Creates session state in State Surface
        2. Registers session with tenant context
        3. Returns session_id
        
        Args:
            request: Session creation request
        
        Returns:
            Session creation response
        """
        try:
            from datetime import datetime
            
            # Generate session_id if not provided
            session_id = request.session_id or f"session_{request.tenant_id}_{request.user_id}_{datetime.now().isoformat()}"
            
            # Create session state in State Surface
            session_state = {
                "session_id": session_id,
                "tenant_id": request.tenant_id,
                "user_id": request.user_id,
                "execution_contract": request.execution_contract or {},
                "metadata": request.metadata or {},
                "created_at": datetime.now().isoformat(),
                "status": "active"
            }
            
            # Store session in State Surface
            await self.state_surface.set_session_state(
                session_id=session_id,
                tenant_id=request.tenant_id,
                state=session_state
            )
            
            self.logger.info(f"Session created: {session_id} for tenant {request.tenant_id}")
            
            return SessionCreateResponse(
                session_id=session_id,
                tenant_id=request.tenant_id,
                user_id=request.user_id,
                created_at=session_state["created_at"]
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
        tenant_id: str,
        include_artifacts: bool = False,
        include_visuals: bool = False
    ) -> ExecutionStatusResponse:
        """
        Get execution status.
        
        Args:
            execution_id: Execution identifier
            tenant_id: Tenant identifier
            include_artifacts: If True, retrieve full artifact data (not just references)
            include_visuals: If True and include_artifacts=True, include full visual images
        
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
            
            artifacts = execution_state.get("artifacts", {})
            
            # If requested, retrieve full artifacts from storage
            if include_artifacts and self.artifact_storage and artifacts:
                retrieved_artifacts = {}
                for key, value in artifacts.items():
                    # Skip artifact_id and storage_path references
                    if key.endswith("_artifact_id"):
                        artifact_id = value
                        artifact_key = key.replace("_artifact_id", "")
                        
                        # Retrieve full artifact
                        artifact = await self.artifact_storage.get_artifact(
                            artifact_id=artifact_id,
                            tenant_id=tenant_id,
                            include_visuals=include_visuals
                        )
                        
                        if artifact:
                            retrieved_artifacts[artifact_key] = artifact
                            # Keep the artifact_id reference for convenience
                            retrieved_artifacts[f"{artifact_key}_artifact_id"] = artifact_id
                    elif not key.endswith("_storage_path"):
                        # Keep non-reference artifacts as-is
                        retrieved_artifacts[key] = value
                
                artifacts = retrieved_artifacts
            
            return ExecutionStatusResponse(
                execution_id=execution_id,
                status=execution_state.get("status", "unknown"),
                intent_id=execution_state.get("intent_id", ""),
                artifacts=artifacts,
                events=execution_state.get("events"),
                error=execution_state.get("error")
            )
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Failed to get execution status: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")



    
    async def get_artifact(
        self,
        artifact_id: str,
        tenant_id: str,
        include_visuals: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Get artifact by ID.
        
        Args:
            artifact_id: Artifact ID
            tenant_id: Tenant ID
            include_visuals: If True, include full visual images
        
        Returns:
            Optional[Dict]: Artifact data or None if not found
        """
        if not self.artifact_storage:
            self.logger.warning("Artifact storage not available")
            return None
        
        return await self.artifact_storage.get_artifact(
            artifact_id=artifact_id,
            tenant_id=tenant_id,
            include_visuals=include_visuals
        )

    
    async def get_visual(
        self,
        visual_path: str,
        tenant_id: str
    ) -> Optional[bytes]:
        """
        Get visual image by storage path.
        
        Args:
            visual_path: GCS storage path of the visual
            tenant_id: Tenant ID
        
        Returns:
            Optional[bytes]: Visual image bytes or None if not found
        """
        if not self.artifact_storage:
            self.logger.warning("Artifact storage not available")
            return None
        
        return await self.artifact_storage.get_visual(
            visual_path=visual_path,
            tenant_id=tenant_id
        )


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
    
    @app.get("/api/session/{session_id}")
    async def get_session(
        session_id: str,
        tenant_id: str
    ):
        """Get session details."""
        session_state = await runtime_api.state_surface.get_session_state(session_id, tenant_id)
        if not session_state:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        return session_state
    
    @app.get("/api/execution/{execution_id}/status", response_model=ExecutionStatusResponse)
    async def get_execution_status_endpoint(
        execution_id: str,
        tenant_id: str,
        include_artifacts: bool = False,
        include_visuals: bool = False
    ):
        """Get execution status."""
        return await runtime_api.get_execution_status(
            execution_id,
            tenant_id,
            include_artifacts=include_artifacts,
            include_visuals=include_visuals
        )
    
    

    @app.get("/api/artifacts/{artifact_id}")
    async def get_artifact_endpoint(
        artifact_id: str,
        tenant_id: str,
        include_visuals: bool = False
    ):
        """Get artifact by ID."""
        from fastapi import HTTPException
        artifact = await runtime_api.get_artifact(artifact_id, tenant_id, include_visuals)
        if not artifact:
            raise HTTPException(status_code=404, detail="Artifact not found")
        return artifact
    
    @app.get("/api/artifacts/visual/{visual_path:path}")
    async def get_visual_endpoint(
        visual_path: str,
        tenant_id: str
    ):
        """Get visual image by storage path."""
        from fastapi import HTTPException, Response
        visual_bytes = await runtime_api.get_visual(visual_path, tenant_id)
        if not visual_bytes:
            raise HTTPException(status_code=404, detail="Visual not found")
        return Response(content=visual_bytes, media_type="image/png")


        visual_bytes = await runtime_api.get_visual(visual_path, tenant_id)
        if not visual_bytes:
            raise HTTPException(status_code=404, detail="Visual not found")
        return Response(content=visual_bytes, media_type="image/png")

    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return {"status": "healthy", "service": "runtime", "version": "2.0.0"}
    
    return app
