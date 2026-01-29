"""
List Artifacts Intent Service

Lists artifacts (files) for a tenant/session.

Contract: docs/intent_contracts/journey_content_file_management/intent_list_artifacts.md

WHAT (Service Role): I list artifacts for a tenant/session
HOW (Service Implementation): I query registry for artifacts with optional filtering
"""

from typing import Dict, Any, Optional

from utilities import get_logger, generate_event_id
from symphainy_platform.bases.intent_service_base import BaseIntentService
from symphainy_platform.runtime.execution_context import ExecutionContext
from symphainy_platform.runtime.intent_model import Intent
from symphainy_platform.realms.utils.structured_artifacts import create_structured_artifact


class ListArtifactsService(BaseIntentService):
    """
    List Artifacts Intent Service.
    
    Handles the `list_artifacts` intent (also supports `list_files` for compatibility):
    - Lists artifacts for tenant/session with optional filtering
    - Supports pagination (limit, offset)
    - Returns structured artifact with file list
    
    Note: This uses artifact-centric vocabulary per contract guidance.
    Backend implementation queries files from Supabase registry.
    """
    
    def __init__(
        self,
        public_works: Optional[Any] = None,
        state_surface: Optional[Any] = None
    ):
        """
        Initialize List Artifacts Service.
        
        Args:
            public_works: Public Works Foundation Service
            state_surface: State Surface
        """
        super().__init__(
            service_id="list_artifacts_service",
            intent_type="list_artifacts",
            public_works=public_works,
            state_surface=state_surface
        )
    
    async def execute(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Execute list_artifacts intent.
        
        Args:
            intent: The list_artifacts intent
            context: Execution context
        
        Returns:
            Dict with artifacts containing file list
        """
        # Extract parameters with defaults
        tenant_id = intent.parameters.get("tenant_id", context.tenant_id)
        session_id = intent.parameters.get("session_id", context.session_id)
        file_type = intent.parameters.get("file_type")
        artifact_type = intent.parameters.get("artifact_type")  # Artifact-centric
        limit = intent.parameters.get("limit", 100)
        offset = intent.parameters.get("offset", 0)
        
        # Get user_id from context for workspace-scoped filtering
        user_id = context.metadata.get("user_id")
        if not user_id:
            user_id = intent.metadata.get("user_id", "system")
            self.logger.warning(f"No user_id in context.metadata, using fallback: {user_id}")
        
        # List files from registry
        files = await self._list_files_from_registry(
            tenant_id=tenant_id,
            session_id=session_id,
            file_type=file_type or artifact_type,
            limit=limit,
            offset=offset,
            user_id=user_id
        )
        
        # Transform to semantic payload
        file_list_semantic = []
        for file in files:
            file_semantic = {
                "artifact_id": file.get("uuid") or file.get("file_id"),
                "artifact_name": file.get("ui_name") or file.get("file_name"),
                "artifact_type": file.get("file_type"),
                "mime_type": file.get("mime_type") or file.get("content_type"),
                "file_size": file.get("file_size"),
                "content_fingerprint": file.get("file_hash"),
                "storage_location": file.get("gcs_blob_path") or file.get("file_path"),
                "created_at": file.get("created_at"),
                "updated_at": file.get("updated_at")
            }
            file_list_semantic.append(file_semantic)
        
        semantic_payload = {
            "artifacts": file_list_semantic,
            "count": len(files),
            "tenant_id": tenant_id,
            "session_id": session_id,
            "limit": limit,
            "offset": offset,
            "artifact_type_filter": file_type or artifact_type
        }
        
        structured_artifact = create_structured_artifact(
            result_type="artifact_list",
            semantic_payload=semantic_payload,
            renderings={}
        )
        
        return {
            "artifacts": {
                "artifact_list": structured_artifact
            },
            "events": []
        }
    
    async def _list_files_from_registry(
        self,
        tenant_id: str,
        session_id: str,
        file_type: Optional[str],
        limit: int,
        offset: int,
        user_id: str
    ) -> list:
        """
        List files from registry (Supabase).
        
        Args:
            tenant_id: Tenant identifier
            session_id: Session identifier
            file_type: Optional file type filter
            limit: Maximum results
            offset: Pagination offset
            user_id: User identifier for workspace scoping
        
        Returns:
            List of file metadata dicts
        """
        if not self.public_works:
            self.logger.warning("Public Works not available, returning empty list")
            return []
        
        registry = getattr(self.public_works, 'registry_abstraction', None)
        if not registry:
            self.logger.warning("Registry abstraction not available, returning empty list")
            return []
        
        try:
            files = await registry.list_files(
                tenant_id=tenant_id,
                session_id=session_id,
                file_type=file_type,
                limit=limit,
                offset=offset,
                user_id=user_id
            )
            return files or []
        except Exception as e:
            self.logger.error(f"Failed to list files from registry: {e}")
            return []
