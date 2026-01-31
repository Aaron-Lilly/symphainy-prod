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

from fastapi import FastAPI, HTTPException, Depends, Request, Query
from typing import Dict, Any, Optional, List
from pydantic import BaseModel

from utilities import get_logger
from .execution_lifecycle_manager import ExecutionLifecycleManager
from .intent_model import Intent, IntentFactory
from .intent_registry import IntentRegistry
from .state_surface import StateSurface
from .wal import WriteAheadLog
from .transactional_outbox import TransactionalOutbox
from symphainy_platform.civic_systems.smart_city.primitives.traffic_cop_primitives import (
    TrafficCopPrimitives,
    RateLimitStore
)


# Request/Response Models
class SessionCreateRequest(BaseModel):
    """Request to create a session (anonymous or authenticated)."""
    intent_type: str = "create_session"
    tenant_id: Optional[str] = None  # Optional for anonymous sessions
    user_id: Optional[str] = None    # Optional for anonymous sessions
    session_id: Optional[str] = None
    execution_contract: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None


class SessionCreateResponse(BaseModel):
    """Response from session creation."""
    session_id: str
    tenant_id: Optional[str] = None  # Optional for anonymous sessions
    user_id: Optional[str] = None     # Optional for anonymous sessions
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


class ArtifactResolveRequest(BaseModel):
    """Request to resolve an artifact."""
    artifact_id: str
    artifact_type: str
    tenant_id: str


class ArtifactResolveResponse(BaseModel):
    """Response from artifact resolution."""
    artifact_id: str
    artifact_type: str
    tenant_id: str
    lifecycle_state: str
    semantic_descriptor: Dict[str, Any]
    materializations: List[Dict[str, Any]]
    parent_artifacts: List[str]
    produced_by: Dict[str, str]
    created_at: str
    updated_at: str


class ArtifactListRequest(BaseModel):
    """Request to list artifacts (for UI dropdowns)."""
    tenant_id: str
    artifact_type: Optional[str] = None
    lifecycle_state: Optional[str] = None
    eligible_for: Optional[str] = None  # Next intent that needs this artifact
    limit: Optional[int] = 100
    offset: Optional[int] = 0


class ArtifactListItem(BaseModel):
    """Single artifact in list response."""
    artifact_id: str
    artifact_type: str
    lifecycle_state: str
    semantic_descriptor: Dict[str, Any]
    created_at: str
    updated_at: str


class ArtifactListResponse(BaseModel):
    """Response from artifact listing."""
    artifacts: List[ArtifactListItem]
    total: int
    limit: int
    offset: int


class PendingIntentListRequest(BaseModel):
    """Request to list pending intents."""
    tenant_id: str
    target_artifact_id: Optional[str] = None
    intent_type: Optional[str] = None


class PendingIntentItem(BaseModel):
    """Single pending intent in list response."""
    intent_id: str
    intent_type: str
    status: str
    target_artifact_id: Optional[str]
    context: Dict[str, Any]
    created_at: str
    updated_at: str


class PendingIntentListResponse(BaseModel):
    """Response from pending intent listing."""
    intents: List[PendingIntentItem]
    total: int


class PendingIntentCreateRequest(BaseModel):
    """Request to create pending intent."""
    intent_id: Optional[str] = None  # Auto-generated if not provided
    intent_type: str
    target_artifact_id: str
    context: Dict[str, Any]  # ingestion_profile, parse_options, etc.
    tenant_id: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None


class PendingIntentCreateResponse(BaseModel):
    """Response from pending intent creation."""
    intent_id: str
    status: str


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
        file_storage: Optional[Any] = None,  # FileStorageAbstraction
        registry_abstraction: Optional[Any] = None  # RegistryAbstraction (for Supabase queries)
    ):
        """
        Initialize Runtime API.
        
        Args:
            execution_lifecycle_manager: Execution lifecycle manager
            state_surface: State surface for execution state
            artifact_storage: Optional artifact storage abstraction
            file_storage: Optional file storage abstraction (for file artifacts)
            registry_abstraction: Optional registry abstraction (for Supabase artifact index queries)
        """
        self.execution_lifecycle_manager = execution_lifecycle_manager
        self.file_storage = file_storage
        self.state_surface = state_surface
        self.artifact_storage = artifact_storage
        self.registry_abstraction = registry_abstraction
        self.logger = get_logger(self.__class__.__name__)
    
    async def create_session(
        self,
        request: SessionCreateRequest
    ) -> SessionCreateResponse:
        """
        Create session via Runtime with intent validation.
        
        Session creation follows the intent pattern:
        1. Validate execution contract via Traffic Cop Primitives
        2. Create session state in State Surface
        3. Register session with tenant context
        4. Return session_id
        
        Args:
            request: Session creation request (with execution_contract from Traffic Cop SDK)
            
        Returns:
            Session creation response
        """
        try:
            from datetime import datetime
            
            # Generate session_id if not provided
            if request.session_id:
                session_id = request.session_id
            elif request.tenant_id and request.user_id:
                # Authenticated session
                session_id = f"session_{request.tenant_id}_{request.user_id}_{datetime.now().isoformat()}"
            else:
                # Anonymous session
                import uuid
                session_id = f"session_anonymous_{uuid.uuid4().hex}_{datetime.now().isoformat()}"
            
            # Validate execution contract via Traffic Cop Primitives (intent validation pattern)
            execution_contract = request.execution_contract or {}
            
            # Initialize Traffic Cop Primitives (MVP: simple validation)
            rate_limit_store = RateLimitStore()  # MVP: in-memory, always allows
            traffic_cop_primitives = TrafficCopPrimitives(rate_limit_store=rate_limit_store)
            
            # Validate session creation intent
            is_valid = await traffic_cop_primitives.validate_session_creation(
                execution_contract=execution_contract,
                rate_limit_store=rate_limit_store
            )
            
            if not is_valid:
                self.logger.warning(f"Session creation validation failed for tenant {request.tenant_id}, user {request.user_id}")
                raise HTTPException(
                    status_code=403,
                    detail="Session creation validation failed. Rate limit exceeded or invalid execution contract."
                )
            
            # Validation passed - create session state in State Surface
            is_anonymous = request.tenant_id is None or request.user_id is None
            
            session_state = {
                "session_id": session_id,
                "tenant_id": request.tenant_id,  # May be None for anonymous
                "user_id": request.user_id,      # May be None for anonymous
                "is_anonymous": is_anonymous,
                "execution_contract": execution_contract,
                "metadata": request.metadata or {},
                "created_at": datetime.now().isoformat(),
                "status": "active"
            }
            
            # Store session in State Surface
            # For anonymous sessions, use a special tenant_id or handle differently
            # For now, use session_id as tenant_id fallback for anonymous sessions
            storage_tenant_id = request.tenant_id or f"anonymous_{session_id}"
            
            await self.state_surface.set_session_state(
                session_id=session_id,
                tenant_id=storage_tenant_id,
                state=session_state
            )
            
            if is_anonymous:
                self.logger.info(f"Anonymous session created: {session_id}")
            else:
                self.logger.info(f"Session created (validated via Traffic Cop Primitives): {session_id} for tenant {request.tenant_id}")
            
            return SessionCreateResponse(
                session_id=session_id,
                tenant_id=request.tenant_id,  # May be None
                user_id=request.user_id,      # May be None
                created_at=session_state["created_at"]
            )
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Failed to create session: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
    async def upgrade_session(
        self,
        session_id: str,
        user_id: str,
        tenant_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Upgrade anonymous session with user_id and tenant_id.
        
        Args:
            session_id: Existing session identifier (anonymous)
            user_id: User identifier to attach
            tenant_id: Tenant identifier to attach
            metadata: Optional metadata to add
        
        Returns:
            Updated session state
        """
        try:
            from datetime import datetime
            
            # Get existing session (may be anonymous, so try without tenant_id first)
            session_state = await self.state_surface.get_session_state(session_id, None)
            
            # If not found, try with anonymous tenant_id pattern
            if not session_state:
                anonymous_tenant_id = f"anonymous_{session_id}"
                session_state = await self.state_surface.get_session_state(session_id, anonymous_tenant_id)
            
            if not session_state:
                raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
            
            # Update session state with user_id and tenant_id
            session_state["user_id"] = user_id
            session_state["tenant_id"] = tenant_id
            session_state["is_anonymous"] = False
            session_state["upgraded_at"] = datetime.now().isoformat()
            if metadata:
                if "metadata" not in session_state:
                    session_state["metadata"] = {}
                session_state["metadata"].update(metadata)
            
            # Store updated session (now with tenant_id)
            await self.state_surface.set_session_state(
                session_id=session_id,
                tenant_id=tenant_id,  # Now has tenant_id
                state=session_state
            )
            
            self.logger.info(f"Session upgraded: {session_id} for tenant {tenant_id}, user {user_id}")
            
            return session_state
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Failed to upgrade session: {e}", exc_info=True)
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
                    
                    # Pattern 3: File artifact references (file_id) - no longer supported
                    # Use structured artifacts with result_type instead
                    elif key == "file_id" and isinstance(value, str):
                        self.logger.error(f"Legacy file_id pattern detected - use structured artifacts instead")
                        # Still store the reference for debugging
                        retrieved_artifacts[key] = value
                    
                    # Pattern 4: File reference (file_reference) - no longer supported
                    # Use structured artifacts with result_type instead
                    elif key == "file_reference" and isinstance(value, str):
                        self.logger.error(f"Legacy file_reference pattern detected - use structured artifacts instead")
                        # Still store the reference for debugging
                        retrieved_artifacts[key] = value
                    
                    # Pattern 5: Visual path references (normalize and keep)
                    elif key.endswith("_visual_path") or key.endswith("_path"):
                        retrieved_artifacts[key] = value
                    
                    # Pattern 6: Skip storage_path references (internal use)
                    elif key.endswith("_storage_path"):
                        pass
                    
                    # Pattern 7: Other artifacts - must be structured or scalar
                    else:
                        if isinstance(value, dict) and not any(k in value for k in ["result_type", "semantic_payload"]):
                            # Non-structured dict format is no longer supported
                            self.logger.error(f"Non-structured artifact '{key}' detected - must use structured format with result_type")
                            # Store for debugging but this should be fixed
                            retrieved_artifacts[key] = value
                        else:
                            # Scalar or properly structured - keep as-is
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
            raise RuntimeError(
                "Artifact storage not wired; cannot get visual. Platform contract §8A."
            )
        
        return await self.artifact_storage.get_visual(
            visual_path=visual_path,
            tenant_id=tenant_id
        )
    
    async def resolve_artifact(
        self,
        request: ArtifactResolveRequest
    ) -> ArtifactResolveResponse:
        """
        Resolve artifact by ID via State Surface (authoritative resolution).
        
        This is the single source of truth for artifact resolution.
        Validates:
        - Artifact exists
        - Artifact type matches
        - Tenant access
        - Lifecycle state is accessible (READY or ARCHIVED)
        
        Args:
            request: Artifact resolution request
        
        Returns:
            Artifact resolution response with full artifact record
        
        Raises:
            HTTPException: If artifact not found or not accessible
        """
        try:
            from symphainy_platform.runtime.artifact_registry import ArtifactRecord
            
            # Resolve artifact via State Surface (authoritative)
            artifact = await self.state_surface.resolve_artifact(
                artifact_id=request.artifact_id,
                artifact_type=request.artifact_type,
                tenant_id=request.tenant_id
            )
            
            if not artifact:
                raise HTTPException(
                    status_code=404,
                    detail=f"Artifact not found or not accessible: {request.artifact_id} (type: {request.artifact_type})"
                )
            
            # Convert ArtifactRecord to response
            return ArtifactResolveResponse(
                artifact_id=artifact.artifact_id,
                artifact_type=artifact.artifact_type,
                tenant_id=artifact.tenant_id,
                lifecycle_state=artifact.lifecycle_state,
                semantic_descriptor={
                    "schema": artifact.semantic_descriptor.schema,
                    "record_count": artifact.semantic_descriptor.record_count,
                    "parser_type": artifact.semantic_descriptor.parser_type,
                    "embedding_model": artifact.semantic_descriptor.embedding_model
                },
                materializations=[
                    {
                        "materialization_id": m.materialization_id,
                        "storage_type": m.storage_type,
                        "uri": m.uri,
                        "format": m.format,
                        "compression": m.compression,
                        "created_at": m.created_at
                    }
                    for m in artifact.materializations
                ],
                parent_artifacts=artifact.parent_artifacts,
                produced_by={
                    "intent": artifact.produced_by.intent,
                    "execution_id": artifact.produced_by.execution_id
                },
                created_at=artifact.created_at,
                updated_at=artifact.updated_at
            )
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Failed to resolve artifact {request.artifact_id}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
    async def list_artifacts(
        self,
        request: ArtifactListRequest
    ) -> ArtifactListResponse:
        """
        List artifacts for UI dropdowns (discovery/indexing via Supabase).
        
        This queries Supabase artifact_index for exploration and filtering.
        For actual artifact content, use resolve_artifact().
        
        Filters:
        - artifact_type: Filter by artifact type
        - lifecycle_state: Filter by lifecycle state (default: READY)
        - eligible_for: Filter artifacts eligible for next intent
        
        Args:
            request: Artifact listing request
        
        Returns:
            Artifact list response with metadata (not content)
        
        Raises:
            HTTPException: If query fails
        """
        try:
            if not self.registry_abstraction:
                self.logger.warning("Registry abstraction not available")
                return ArtifactListResponse(
                    artifacts=[],
                    total=0,
                    limit=request.limit or 100,
                    offset=request.offset or 0
                )
            
            # Query artifact_index via RegistryAbstraction
            result = await self.registry_abstraction.list_artifacts(
                tenant_id=request.tenant_id,
                artifact_type=request.artifact_type,
                lifecycle_state=request.lifecycle_state or "READY",
                eligible_for=request.eligible_for,
                limit=request.limit or 100,
                offset=request.offset or 0
            )
            
            # Convert to response format
            artifacts = [
                ArtifactListItem(
                    artifact_id=item["artifact_id"],
                    artifact_type=item["artifact_type"],
                    lifecycle_state=item["lifecycle_state"],
                    semantic_descriptor=item["semantic_descriptor"],
                    created_at=item["created_at"],
                    updated_at=item["updated_at"]
                )
                for item in result.get("artifacts", [])
            ]
            
            return ArtifactListResponse(
                artifacts=artifacts,
                total=result.get("total", 0),
                limit=result.get("limit", request.limit or 100),
                offset=result.get("offset", request.offset or 0)
            )
            
        except Exception as e:
            self.logger.error(f"Failed to list artifacts: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
    async def list_pending_intents(
        self,
        request: PendingIntentListRequest
    ) -> PendingIntentListResponse:
        """
        List pending intents for UI.
        
        Used to show "files with pending parse intents" and similar UI features.
        Returns pending intents with context (ingestion_profile lives here).
        """
        try:
            if not self.registry_abstraction:
                raise HTTPException(
                    status_code=500,
                    detail="Registry abstraction not available"
                )
            
            # Query pending intents from intent_executions table
            pending_intents = await self.registry_abstraction.get_pending_intents(
                tenant_id=request.tenant_id,
                target_artifact_id=request.target_artifact_id,
                intent_type=request.intent_type
            )
            
            # Convert to response format
            intent_items = [
                PendingIntentItem(
                    intent_id=item.get("intent_id", ""),
                    intent_type=item.get("intent_type", ""),
                    status=item.get("status", "pending"),
                    target_artifact_id=item.get("target_artifact_id"),
                    context=item.get("context", {}),
                    created_at=item.get("created_at", ""),
                    updated_at=item.get("updated_at", "")
                )
                for item in pending_intents
            ]
            
            return PendingIntentListResponse(
                intents=intent_items,
                total=len(intent_items)
            )
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Failed to list pending intents: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
    async def create_pending_intent(
        self,
        request: PendingIntentCreateRequest
    ) -> PendingIntentCreateResponse:
        """
        Create pending intent (where ingestion_profile lives).
        
        This enables resumable workflows - user can upload file, select ingestion_profile,
        and resume parsing later (even in a different session).
        
        The ingestion_profile is stored in the intent context, not on the artifact.
        """
        try:
            if not self.registry_abstraction:
                raise HTTPException(
                    status_code=500,
                    detail="Registry abstraction not available"
                )
            
            # Generate intent_id if not provided
            import uuid
            intent_id = request.intent_id or str(uuid.uuid4())
            
            # Create pending intent in intent_executions table
            result = await self.registry_abstraction.create_pending_intent(
                intent_id=intent_id,
                intent_type=request.intent_type,
                target_artifact_id=request.target_artifact_id,
                context=request.context,
                tenant_id=request.tenant_id,
                user_id=request.user_id,
                session_id=request.session_id
            )
            
            if not result.get("success"):
                error_msg = result.get("error", "Unknown error")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to create pending intent: {error_msg}"
                )
            
            return PendingIntentCreateResponse(
                intent_id=intent_id,
                status="pending"
            )
            
        except HTTPException:
            raise
        except Exception as e:
            self.logger.error(f"Failed to create pending intent: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


def create_runtime_app(
    execution_lifecycle_manager: ExecutionLifecycleManager,
    state_surface: StateSurface,
    artifact_storage: Optional[Any] = None,
    file_storage: Optional[Any] = None,
    registry_abstraction: Optional[Any] = None
) -> FastAPI:
    """
    Create FastAPI app for Runtime API.
    
    Args:
        execution_lifecycle_manager: Execution lifecycle manager
        state_surface: State surface
        artifact_storage: Optional artifact storage abstraction
        file_storage: Optional file storage abstraction
        registry_abstraction: Optional registry abstraction (for Supabase artifact index queries)
    
    Returns:
        FastAPI application
    """
    app = FastAPI(
        title="Symphainy Runtime API",
        description="Runtime API - Intent submission and execution management",
        version="2.0.0"
    )
    
    runtime_api = RuntimeAPI(
        execution_lifecycle_manager,
        state_surface,
        artifact_storage=artifact_storage,
        file_storage=file_storage,
        registry_abstraction=registry_abstraction
    )
    
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
        tenant_id: Optional[str] = Query(None, description="Tenant ID (optional for anonymous sessions)")
    ):
        """Get session details (anonymous or authenticated)."""
        # For anonymous sessions, tenant_id may be None
        # get_session_state will handle this by using session_id as fallback
        session_state = await runtime_api.state_surface.get_session_state(session_id, tenant_id)
        if not session_state:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        return session_state
    
    @app.patch("/api/session/{session_id}/upgrade")
    async def upgrade_session_endpoint(
        session_id: str,
        request: Dict[str, Any]  # { user_id, tenant_id, metadata }
    ):
        """Upgrade anonymous session with user_id and tenant_id."""
        return await runtime_api.upgrade_session(
            session_id=session_id,
            user_id=request.get("user_id"),
            tenant_id=request.get("tenant_id"),
            metadata=request.get("metadata")
        )
    
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

    @app.post("/api/artifact/resolve", response_model=ArtifactResolveResponse)
    async def resolve_artifact_endpoint(request: ArtifactResolveRequest):
        """
        Resolve artifact by ID (authoritative resolution via State Surface).
        
        This is the single source of truth for artifact resolution.
        Returns full artifact record with materializations and lineage.
        """
        return await runtime_api.resolve_artifact(request)
    
    @app.post("/api/artifact/list", response_model=ArtifactListResponse)
    async def list_artifacts_endpoint(request: ArtifactListRequest):
        """
        List artifacts for UI dropdowns (discovery/indexing via Supabase).
        
        Returns artifact metadata (not content) filtered by:
        - artifact_type
        - lifecycle_state (default: READY)
        - eligible_for (next intent that needs this artifact)
        
        For actual artifact content, use /api/artifact/resolve.
        """
        return await runtime_api.list_artifacts(request)
    
    @app.post("/api/intent/pending/list", response_model=PendingIntentListResponse)
    async def list_pending_intents_endpoint(request: PendingIntentListRequest):
        """
        List pending intents for UI.
        
        Used to show "files with pending parse intents" and similar UI features.
        Returns pending intents with context (ingestion_profile lives here).
        """
        return await runtime_api.list_pending_intents(request)
    
    @app.post("/api/intent/pending/create", response_model=PendingIntentCreateResponse)
    async def create_pending_intent_endpoint(request: PendingIntentCreateRequest):
        """
        Create pending intent (where ingestion_profile lives).
        
        This enables resumable workflows - user can upload file, select ingestion_profile,
        and resume parsing later (even in a different session).
        
        The ingestion_profile is stored in the intent context, not on the artifact.
        """
        return await runtime_api.create_pending_intent(request)
    
    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return {"status": "healthy", "service": "runtime", "version": "2.0.0"}
    
    return app
