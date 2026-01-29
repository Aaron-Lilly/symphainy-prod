"""
Retrieve Artifact Metadata Intent Service

Retrieves metadata for a specific artifact.

Contract: docs/intent_contracts/journey_content_file_management/intent_retrieve_artifact_metadata.md

WHAT (Service Role): I retrieve artifact metadata
HOW (Service Implementation): I query registry for artifact metadata by ID
"""

from typing import Dict, Any, Optional

from utilities import get_logger
from symphainy_platform.bases.intent_service_base import BaseIntentService
from symphainy_platform.runtime.execution_context import ExecutionContext
from symphainy_platform.runtime.intent_model import Intent
from symphainy_platform.realms.utils.structured_artifacts import create_structured_artifact


class RetrieveArtifactMetadataService(BaseIntentService):
    """
    Retrieve Artifact Metadata Intent Service.
    
    Handles the `retrieve_artifact_metadata` intent:
    - Retrieves metadata for a specific artifact
    - Returns structured artifact with metadata
    
    This is a read-only query intent - no artifact registration required.
    """
    
    def __init__(
        self,
        public_works: Optional[Any] = None,
        state_surface: Optional[Any] = None
    ):
        """
        Initialize Retrieve Artifact Metadata Service.
        
        Args:
            public_works: Public Works Foundation Service
            state_surface: State Surface
        """
        super().__init__(
            service_id="retrieve_artifact_metadata_service",
            intent_type="retrieve_artifact_metadata",
            public_works=public_works,
            state_surface=state_surface
        )
    
    async def execute(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Execute retrieve_artifact_metadata intent.
        
        Args:
            intent: The retrieve_artifact_metadata intent
            context: Execution context
        
        Returns:
            Dict with artifacts containing metadata
        
        Raises:
            ValueError: If artifact_id/file_id not provided or artifact not found
        """
        # Support both artifact_id and file_id for compatibility
        artifact_id = intent.parameters.get("artifact_id") or intent.parameters.get("file_id")
        artifact_reference = intent.parameters.get("artifact_reference") or intent.parameters.get("file_reference")
        
        if not artifact_id and not artifact_reference:
            raise ValueError("Either artifact_id or artifact_reference is required")
        
        # Get artifact metadata
        artifact_metadata = await self._get_artifact_metadata(
            artifact_id=artifact_id,
            artifact_reference=artifact_reference,
            context=context
        )
        
        if not artifact_metadata:
            raise ValueError(f"Artifact not found: artifact_id={artifact_id}, artifact_reference={artifact_reference}")
        
        # Create structured artifact with semantic payload
        semantic_payload = {
            "artifact_id": artifact_id or artifact_metadata.get("file_id"),
            "artifact_reference": artifact_reference,
            "artifact_name": artifact_metadata.get("file_name") or artifact_metadata.get("ui_name"),
            "artifact_type": artifact_metadata.get("file_type"),
            "mime_type": artifact_metadata.get("mime_type") or artifact_metadata.get("content_type"),
            "file_size": artifact_metadata.get("file_size"),
            "content_fingerprint": artifact_metadata.get("file_hash"),
            "storage_location": artifact_metadata.get("storage_location") or artifact_metadata.get("file_path"),
            "lifecycle_state": artifact_metadata.get("lifecycle_state", "ready"),
            "created_at": artifact_metadata.get("created_at"),
            "updated_at": artifact_metadata.get("updated_at"),
            "metadata": artifact_metadata.get("metadata", {})
        }
        
        structured_artifact = create_structured_artifact(
            result_type="artifact_metadata",
            semantic_payload=semantic_payload,
            renderings={}
        )
        
        return {
            "artifacts": {
                "artifact_metadata": structured_artifact
            },
            "events": []
        }
    
    async def _get_artifact_metadata(
        self,
        artifact_id: Optional[str],
        artifact_reference: Optional[str],
        context: ExecutionContext
    ) -> Optional[Dict[str, Any]]:
        """
        Get artifact metadata from registry or state surface.
        
        Tries multiple lookup strategies:
        1. Direct file_id lookup via FileStorageAbstraction
        2. File reference lookup in State Surface
        3. Constructed file reference lookup
        """
        artifact_metadata = None
        
        # Strategy 1: Direct UUID lookup via FileStorageAbstraction
        if artifact_id and self.public_works:
            try:
                file_storage = self.public_works.get_file_storage_abstraction()
                if file_storage:
                    artifact_metadata = await file_storage.get_file_by_uuid(artifact_id)
                    if artifact_metadata:
                        return artifact_metadata
            except Exception as e:
                self.logger.debug(f"File storage lookup by UUID failed: {e}")
        
        # Strategy 2: File reference lookup in State Surface
        if artifact_reference and context.state_surface:
            try:
                artifact_metadata = await context.state_surface.get_file_metadata(artifact_reference)
                if artifact_metadata:
                    return artifact_metadata
            except Exception as e:
                self.logger.debug(f"State Surface lookup failed: {e}")
        
        # Strategy 3: Construct reference and try lookup
        if artifact_id and not artifact_reference and context.state_surface:
            artifact_reference = f"file:{context.tenant_id}:{context.session_id}:{artifact_id}"
            try:
                artifact_metadata = await context.state_surface.get_file_metadata(artifact_reference)
                if artifact_metadata:
                    return artifact_metadata
            except Exception as e:
                self.logger.debug(f"Constructed reference lookup failed: {e}")
        
        return artifact_metadata
