"""
Retrieve Artifact Metadata Service (Platform SDK)

Retrieves metadata for a specific artifact.

Uses ctx.platform for registry access.

Contract: docs/intent_contracts/journey_content_file_management/intent_retrieve_artifact_metadata.md
"""

from typing import Dict, Any, Optional

from utilities import get_logger

from symphainy_platform.civic_systems.platform_sdk import (
    PlatformIntentService,
    PlatformContext
)


class RetrieveArtifactMetadataService(PlatformIntentService):
    """
    Retrieve Artifact Metadata Service using Platform SDK.
    
    Handles the `retrieve_artifact_metadata` intent:
    - Retrieves metadata for a specific artifact
    - Returns structured artifact with metadata
    
    This is a read-only query intent.
    """
    
    def __init__(self, service_id: str = "retrieve_artifact_metadata_service"):
        """Initialize Retrieve Artifact Metadata Service."""
        super().__init__(service_id=service_id)
        self.logger = get_logger(self.__class__.__name__)
    
    async def execute(self, ctx: PlatformContext) -> Dict[str, Any]:
        """
        Execute retrieve_artifact_metadata intent.
        
        Args:
            ctx: Platform context with intent and platform services
        
        Returns:
            Dict with artifacts containing metadata
        """
        self.logger.info(f"Executing retrieve_artifact_metadata: {ctx.execution_id}")
        
        # Support both artifact_id and file_id for compatibility
        artifact_id = ctx.intent.parameters.get("artifact_id") or ctx.intent.parameters.get("file_id")
        artifact_reference = ctx.intent.parameters.get("artifact_reference") or ctx.intent.parameters.get("file_reference")
        
        if not artifact_id and not artifact_reference:
            raise ValueError("Either artifact_id or artifact_reference is required")
        
        # Get artifact metadata using multiple strategies
        artifact_metadata = await self._get_artifact_metadata(
            ctx=ctx,
            artifact_id=artifact_id,
            artifact_reference=artifact_reference
        )
        
        if not artifact_metadata:
            raise ValueError(f"Artifact not found: artifact_id={artifact_id}, artifact_reference={artifact_reference}")
        
        # Create semantic payload
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
        
        self.logger.info(f"✅ Retrieved artifact metadata: {artifact_id or artifact_reference}")
        
        return {
            "artifacts": {
                "artifact_metadata": {
                    "result_type": "artifact_metadata",
                    "semantic_payload": semantic_payload
                }
            },
            "events": []
        }
    
    async def _get_artifact_metadata(
        self,
        ctx: PlatformContext,
        artifact_id: Optional[str],
        artifact_reference: Optional[str]
    ) -> Optional[Dict[str, Any]]:
        """
        Get artifact metadata using multiple lookup strategies.
        
        Tries:
        1. ctx.platform.get_file_metadata() by reference
        2. Direct registry lookup by UUID
        3. Constructed reference lookup
        """
        # Strategy 1: Direct lookup via ctx.platform
        if artifact_id:
            try:
                metadata = await ctx.platform.get_file_metadata(artifact_id)
                if metadata:
                    return metadata
            except Exception as e:
                self.logger.debug(f"Platform lookup by ID failed: {e}")
        
        # Strategy 2: File reference lookup via state_surface
        if artifact_reference and ctx.state_surface:
            try:
                metadata = await ctx.state_surface.get_file_metadata(artifact_reference)
                if metadata:
                    return metadata
            except Exception as e:
                self.logger.debug(f"State surface lookup failed: {e}")
        
        # Strategy 3: Construct reference and try lookup
        if artifact_id and not artifact_reference and ctx.state_surface:
            constructed_ref = f"file:{ctx.tenant_id}:{ctx.session_id}:{artifact_id}"
            try:
                metadata = await ctx.state_surface.get_file_metadata(constructed_ref)
                if metadata:
                    return metadata
            except Exception as e:
                self.logger.debug(f"Constructed reference lookup failed: {e}")
        
        return None
