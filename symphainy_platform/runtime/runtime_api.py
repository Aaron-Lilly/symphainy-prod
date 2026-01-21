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

from fastapi import FastAPI, HTTPException, Depends, Request
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
        artifact_storage: Optional[Any] = None,  # ArtifactStorageAbstraction
        file_storage: Optional[Any] = None  # FileStorageAbstraction
    ):
        """
        Initialize Runtime API.
        
        Args:
            execution_lifecycle_manager: Execution lifecycle manager
            state_surface: State surface for execution state
            artifact_storage: Optional artifact storage abstraction
            file_storage: Optional file storage abstraction (for file artifacts)
        """
        self.execution_lifecycle_manager = execution_lifecycle_manager
        self.file_storage = file_storage
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
            # Log received tenant_id for debugging
            self.logger.info(f"🔵 RECEIVED REQUEST: tenant_id={request.tenant_id}, intent_type={request.intent_type}")
            
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
            
            # Validate artifacts structure on retrieval
            if artifacts:
                # Check for flat keys at top level (indicates semantic_payload was unwrapped)
                has_flat_keys = any(k in artifacts for k in ["file_id", "artifact_type", "file_path"])
                has_structured_key = "file" in artifacts
                
                if has_flat_keys and not has_structured_key:
                    self.logger.warning(f"Retrieved artifacts have flat keys instead of structured 'file' key! Keys: {list(artifacts.keys())[:15]}")
            
            # If requested, retrieve full artifacts from storage
            if include_artifacts and artifacts:
                retrieved_artifacts = {}
                for key, value in artifacts.items():
                    # Pattern 1: Structured artifacts (result_type, semantic_payload, renderings) - CHECK FIRST
                    # This is the new pattern from Content Realm refactoring
                    if isinstance(value, dict) and "result_type" in value:
                        self.logger.info(f"API_PATTERN1_MATCH: {key} -> structured artifact")
                        # Structured artifact - keep as-is (semantic_payload is JSON-serializable)
                        # renderings may need expansion if they contain artifact references
                        retrieved_artifacts[key] = value
                        continue
                    
                    # Pattern 2: Structured artifact references (*_artifact_id)
                    elif key.endswith("_artifact_id"):
                        artifact_id = value
                        artifact_key = key.replace("_artifact_id", "")
                        
                        # Use unified artifact retrieval (handles both structured and file artifacts)
                        artifact = await self.get_artifact(
                            artifact_id=artifact_id,
                            tenant_id=tenant_id,
                            include_visuals=include_visuals
                        )
                        
                        if artifact:
                            retrieved_artifacts[artifact_key] = artifact
                            retrieved_artifacts[f"{artifact_key}_artifact_id"] = artifact_id
                    
                    # Pattern 3: File artifact references (file_id) - LEGACY, should not happen after refactoring
                    elif key == "file_id" and isinstance(value, str):
                        artifact_id = value
                        artifact = await self.get_artifact(
                            artifact_id=artifact_id,
                            tenant_id=tenant_id,
                            include_visuals=include_visuals
                        )
                        if artifact:
                            retrieved_artifacts["file"] = artifact
                            retrieved_artifacts["file_id"] = artifact_id
                    
                    # Pattern 4: File reference (file_reference) - LEGACY
                    elif key == "file_reference" and isinstance(value, str):
                        if value.startswith("file:"):
                            parts = value.split(":")
                            if len(parts) >= 4:
                                file_id = parts[3]
                                artifact = await self.get_artifact(
                                    artifact_id=file_id,
                                    tenant_id=tenant_id,
                                    include_visuals=include_visuals
                                )
                                if artifact:
                                    retrieved_artifacts["file"] = artifact
                                    retrieved_artifacts["file_reference"] = value
                    
                    # Pattern 5: Visual path references (normalize and keep)
                    elif key.endswith("_visual_path") or key.endswith("_path"):
                        retrieved_artifacts[key] = value
                    
                    # Pattern 6: Skip storage_path references (internal use)
                    elif key.endswith("_storage_path"):
                        pass
                    
                    # Pattern 7: Keep all other artifacts as-is (legacy format - should not happen after refactoring)
                    else:
                        # Check if this is actually a flat dict that should be converted to structured
                        # This handles the case where execution state has old format but we want to return structured
                        if isinstance(value, dict) and not any(k in value for k in ["result_type", "semantic_payload"]):
                            # This looks like legacy flat format - log warning
                            self.logger.warning(f"API_PATTERN7_LEGACY: key '{key}' -> legacy flat format, keys: {list(value.keys())[:10]}")
                        else:
                            self.logger.info(f"API_PATTERN7_OTHER: key '{key}' -> type={type(value).__name__}, is_dict={isinstance(value, dict)}")
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
        include_visuals: bool = False,
        materialization_policy: Optional[Any] = None  # MaterializationPolicyAbstraction
    ) -> Optional[Dict[str, Any]]:
        """
        Get artifact by ID (unified retrieval with materialization policy awareness).
        
        Handles both:
        1. Structured artifacts (via ArtifactStorageAbstraction)
        2. File artifacts (via FileStorageAbstraction)
        3. Fallback to direct GCS lookup
        4. Materialization policy awareness (checks if artifact should be persisted)
        
        Args:
            artifact_id: Artifact ID (can be file_id or artifact_id)
            tenant_id: Tenant ID
            include_visuals: If True, include full visual images
            materialization_policy: Optional materialization policy abstraction
        
        Returns:
            Optional[Dict]: Artifact data or None if not found
        """
        # Try ArtifactStorageAbstraction first (structured artifacts)
        if self.artifact_storage:
            artifact = await self.artifact_storage.get_artifact(
                artifact_id=artifact_id,
                tenant_id=tenant_id,
                include_visuals=include_visuals
            )
            if artifact:
                # Add materialization policy metadata if available
                if materialization_policy:
                    artifact_type = artifact.get("artifact_type")
                    if artifact_type:
                        # Check if artifact type should be persisted (for future use)
                        # Currently MVP persists all, but this enables future policy checks
                        artifact["materialization_policy"] = "persist"  # MVP: all persisted
                return artifact
        
        # Try FileStorageAbstraction (file artifacts)
        # Files are always persisted (platform-native), so no policy check needed
        if self.file_storage:
            try:
                # Try to get file metadata by UUID
                file_metadata = await self.file_storage.get_file_by_uuid(artifact_id)
                if file_metadata:
                    # Format file as artifact
                    artifact = self._format_file_as_artifact(file_metadata, tenant_id, include_visuals)
                    # Files are always persisted (platform-native)
                    if materialization_policy:
                        artifact["materialization_policy"] = "persist"
                    return artifact
            except Exception as e:
                self.logger.debug(f"File storage lookup failed for {artifact_id}: {e}")
        
        # Fallback: Try to get file from State Surface (files might be in state but not in Supabase)
        if self.state_surface:
            try:
                # Try to construct file_reference and get from state
                # File references are in format: "file:tenant:session:file_id"
                # But we only have file_id, so try common patterns
                file_reference_patterns = [
                    f"file:{tenant_id}:*:{artifact_id}",  # Try with wildcard session
                    f"file:{tenant_id}:**:{artifact_id}",  # Try with any session pattern
                ]
                
                # Actually, we need to search state surface for files with this file_id
                # For now, try direct lookup if we can construct a reference
                # This is a limitation - we'd need file_id -> file_reference mapping
                # For MVP, files should be in Supabase, so this is a fallback
                pass  # State Surface lookup would require file_id -> file_reference mapping
            except Exception as e:
                self.logger.debug(f"State Surface lookup failed for {artifact_id}: {e}")
        
        # Fallback: Try direct GCS lookup (for artifacts stored directly)
        # This handles edge cases where metadata might be missing
        if self.artifact_storage and hasattr(self.artifact_storage, 'gcs'):
            # ArtifactStorageAbstraction has fallback logic, but we've already tried it
            pass
        
        # Materialization policy awareness: If artifact not found and policy says "discard",
        # it might have been ephemeral (future enhancement)
        if materialization_policy:
            self.logger.debug(f"Artifact {artifact_id} not found - may be ephemeral (discarded by policy)")
        
        self.logger.warning(f"Artifact not found: {artifact_id} (tenant: {tenant_id})")
        return None
    
    def _format_file_as_artifact(
        self,
        file_metadata: Dict[str, Any],
        tenant_id: str,
        include_visuals: bool = False
    ) -> Dict[str, Any]:
        """
        Format file metadata as artifact structure.
        
        Args:
            file_metadata: File metadata from FileStorageAbstraction
            tenant_id: Tenant ID
            include_visuals: Whether to include file contents
        
        Returns:
            Dict: Artifact-formatted file data
        """
        artifact = {
            "artifact_id": file_metadata.get("id") or file_metadata.get("file_id"),
            "artifact_type": "file",  # Standardize artifact type
            "tenant_id": tenant_id,
            "file_id": file_metadata.get("id") or file_metadata.get("file_id"),
            "file_path": file_metadata.get("file_path") or file_metadata.get("storage_path"),
            "file_reference": file_metadata.get("file_reference"),
            "file_name": file_metadata.get("file_name") or file_metadata.get("ui_name"),
            "file_type": file_metadata.get("file_type"),
            "mime_type": file_metadata.get("mime_type") or file_metadata.get("content_type"),
            "file_size": file_metadata.get("file_size"),
            "metadata": file_metadata.get("metadata", {}),
            "created_at": file_metadata.get("created_at"),
            "updated_at": file_metadata.get("updated_at")
        }
        
        # Include file contents if requested
        if include_visuals and file_metadata.get("content"):
            artifact["content"] = file_metadata.get("content")
        elif include_visuals and file_metadata.get("file_content"):
            artifact["content"] = file_metadata.get("file_content")
        
        return artifact

    
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
        """
        Get artifact by ID.
        
        Supports unified retrieval of:
        - Structured artifacts (workflow, sop, solution, etc.)
        - File artifacts (files ingested via Content Realm)
        - Composite artifacts with visuals
        
        Materialization policy awareness:
        - Files are always persisted (platform-native)
        - Structured artifacts follow materialization policy (MVP: all persisted)
        """
        from fastapi import HTTPException
        
        # Materialization policy is handled at storage time, not retrieval time
        # For MVP, all artifacts are persisted, so we don't need to check policy here
        # Future: When ephemeral artifacts are supported, we'll check policy here
        
        artifact = await runtime_api.get_artifact(
            artifact_id=artifact_id,
            tenant_id=tenant_id,
            include_visuals=include_visuals,
            materialization_policy=None  # Not needed for MVP (all persisted)
        )
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
