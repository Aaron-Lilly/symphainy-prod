"""
Artifact Management Handlers - Register, Retrieve, Archive, Delete Artifacts
"""

from typing import Dict, Any, Optional
import uuid

from utilities import get_logger
from symphainy_platform.runtime.intent_model import Intent
from symphainy_platform.runtime.execution_context import ExecutionContext
from symphainy_platform.runtime.artifact_registry import (
    ProducedBy,
    SemanticDescriptor,
    Materialization,
    LifecycleState
)
from symphainy_platform.realms.utils.structured_artifacts import create_structured_artifact
from .base_handler import BaseContentHandler


class ArtifactManagementHandlers(BaseContentHandler):
    """
    Handlers for artifact management intents:
    - register_artifact
    - retrieve_artifact
    - retrieve_artifact_metadata
    - archive_artifact
    - delete_artifact
    """
    
    async def handle_register_artifact(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Handle register_artifact intent - register existing artifact in Artifact Registry.
        
        Use case: Artifact already exists in storage (GCS/Supabase), needs to be registered
        in Artifact Registry for governed access and lifecycle management.
        
        Intent parameters:
        - artifact_id: str (REQUIRED) - Artifact identifier
        - artifact_type: str (optional) - Artifact type (default: "file")
        - storage_location: str (optional) - GCS blob path (if not provided, will try to get from Supabase)
        - ui_name: str (REQUIRED) - User-friendly filename for display
        - file_type: str (optional) - File type
        - mime_type: str (optional) - MIME type
        """
        artifact_id = intent.parameters.get("artifact_id")
        if not artifact_id:
            raise ValueError("artifact_id is required for register_artifact intent")
        
        ui_name = intent.parameters.get("ui_name")
        if not ui_name:
            raise ValueError("ui_name is required for register_artifact intent")
        
        artifact_type = intent.parameters.get("artifact_type", "file")
        file_type = intent.parameters.get("file_type", "unstructured")
        mime_type = intent.parameters.get("mime_type", "application/octet-stream")
        storage_location = intent.parameters.get("storage_location")
        
        # Try to get artifact metadata from Artifact Index (optional - artifact might not be indexed yet)
        file_metadata = None
        if self.public_works and self.public_works.registry_abstraction:
            try:
                artifact_metadata = await self.public_works.registry_abstraction.get_artifact_metadata(
                    artifact_id=artifact_id,
                    tenant_id=context.tenant_id,
                    artifact_type=artifact_type
                )
                if artifact_metadata:
                    # Convert to legacy format for compatibility
                    file_metadata = {
                        "file_size": artifact_metadata.get("file_size"),
                        "file_hash": artifact_metadata.get("file_hash"),
                        "gcs_blob_path": None,  # Will be in materializations
                        "file_path": None,
                        "storage_path": None
                    }
            except Exception as e:
                self.logger.debug(f"Artifact Index lookup failed: {e}")
        
        # Get storage location from metadata if not provided
        if not storage_location and file_metadata:
            storage_location = file_metadata.get("gcs_blob_path") or file_metadata.get("file_path") or file_metadata.get("storage_path")
        
        # If still no storage location, derive from artifact_id (assume standard pattern)
        if not storage_location:
            storage_location = f"files/{artifact_id}"
            self.logger.warning(f"Storage location not found for artifact {artifact_id}, using default pattern: {storage_location}")
        
        # Register artifact in Artifact Registry (State Surface)
        produced_by = ProducedBy(
            intent="register_artifact",
            execution_id=context.execution_id
        )
        
        semantic_descriptor = SemanticDescriptor(
            schema="artifact_registry_v1",
            parser_type=file_type,
            embedding_model=None
        )
        
        # Register artifact with lifecycle_state: READY (artifact already exists)
        success = await context.state_surface.register_artifact(
            artifact_id=artifact_id,
            artifact_type=artifact_type,
            tenant_id=context.tenant_id,
            produced_by=produced_by,
            semantic_descriptor=semantic_descriptor,
            lifecycle_state=LifecycleState.READY.value
        )
        
        if not success:
            raise RuntimeError(f"Failed to register artifact in Artifact Registry: {artifact_id}")
        
        # Add materialization (GCS storage)
        materialization = Materialization(
            materialization_id=str(uuid.uuid4()),
            storage_type="gcs",
            uri=storage_location,
            format=mime_type or "application/octet-stream"
        )
        
        await context.state_surface.add_materialization(
            artifact_id=artifact_id,
            tenant_id=context.tenant_id,
            materialization=materialization
        )
        
        self.logger.info(f"Artifact registered in Artifact Registry: {artifact_id} ({artifact_type}) -> {storage_location}")
        
        # Create structured artifact for response
        semantic_payload = {
            "artifact_id": artifact_id,
            "artifact_type": artifact_type,
            "storage_location": storage_location,
            "ui_name": ui_name,
            "file_type": file_type,
            "mime_type": mime_type,
            "file_size": file_metadata.get("file_size") if file_metadata else None,
            "file_hash": file_metadata.get("file_hash") if file_metadata else None,
            "lifecycle_state": LifecycleState.READY.value,
            "status": "registered"
        }
        
        structured_artifact = create_structured_artifact(
            result_type="artifact",
            semantic_payload=semantic_payload,
            renderings={}  # Registration doesn't include contents
        )
        
        return {
            "artifacts": {
                "artifact": structured_artifact
            },
            "events": [
                {
                    "type": "artifact_registered",
                    "artifact_id": artifact_id,
                    "artifact_type": artifact_type
                }
            ]
        }
    
    async def handle_retrieve_artifact_metadata(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Handle retrieve_artifact_metadata intent - get artifact metadata from Artifact Index (discovery).
        
        This is a discovery operation (Artifact Index), not resolution (State Surface).
        Returns artifact metadata only, not full content.
        
        Intent parameters:
        - artifact_id: str (REQUIRED) - Artifact identifier
        - artifact_type: str (optional) - Artifact type filter (default: "file")
        """
        artifact_id = intent.parameters.get("artifact_id")
        if not artifact_id:
            raise ValueError("artifact_id is required for retrieve_artifact_metadata intent")
        
        artifact_type = intent.parameters.get("artifact_type", "file")
        
        # Query Artifact Index (Supabase artifact_index table) for discovery
        if not self.public_works:
            raise RuntimeError("Public Works not initialized - cannot access RegistryAbstraction")
        
        registry_abstraction = self.public_works.registry_abstraction
        if not registry_abstraction:
            raise RuntimeError("RegistryAbstraction not available")
        
        # Query artifact_index table
        artifact_metadata = await registry_abstraction.get_artifact_metadata(
            artifact_id=artifact_id,
            tenant_id=context.tenant_id,
            artifact_type=artifact_type
        )
        
        if not artifact_metadata:
            raise ValueError(f"Artifact not found in Artifact Index: {artifact_id}")
        
        # Create structured artifact for response
        semantic_payload = {
            "artifact_id": artifact_metadata.get("artifact_id"),
            "artifact_type": artifact_metadata.get("artifact_type"),
            "lifecycle_state": artifact_metadata.get("lifecycle_state"),
            "created_at": artifact_metadata.get("created_at"),
            "updated_at": artifact_metadata.get("updated_at"),
            "semantic_descriptor": artifact_metadata.get("semantic_descriptor"),
            "parent_artifacts": artifact_metadata.get("parent_artifacts", [])
        }
        
        structured_artifact = create_structured_artifact(
            result_type="artifact_metadata",
            semantic_payload=semantic_payload,
            renderings={}  # Metadata only, no contents
        )
        
        return {
            "artifacts": {
                "artifact_metadata": structured_artifact
            },
            "events": []
        }
    
    async def handle_retrieve_artifact(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Handle retrieve_artifact intent - resolve artifact via State Surface and retrieve content.
        
        Uses State Surface resolve_artifact() as single source of truth.
        Retrieves content from artifact's materializations array.
        
        Intent parameters:
        - artifact_id: str (REQUIRED) - Artifact identifier
        - artifact_type: str (optional) - Artifact type (default: "file")
        - include_contents: bool (optional) - Whether to return artifact contents (default: True)
        """
        artifact_id = intent.parameters.get("artifact_id")
        if not artifact_id:
            raise ValueError("artifact_id is required for retrieve_artifact intent")
        
        artifact_type = intent.parameters.get("artifact_type", "file")
        include_contents = intent.parameters.get("include_contents", True)
        
        # Resolve artifact via State Surface (single source of truth)
        artifact = await context.state_surface.resolve_artifact(
            artifact_id=artifact_id,
            artifact_type=artifact_type,
            tenant_id=context.tenant_id
        )
        
        if not artifact:
            raise ValueError(f"Artifact not found or not accessible: {artifact_id}")
        
        # Retrieve content from materializations if requested
        renderings = {}
        if include_contents and artifact.materializations:
            # Get file storage abstraction
            if not self.public_works:
                raise RuntimeError("Public Works not initialized - cannot access FileStorageAbstraction")
            
            file_storage = self.public_works.get_file_storage_abstraction()
            if not file_storage:
                raise RuntimeError("FileStorageAbstraction not available")
            
            # Retrieve content from first materialization (GCS)
            for materialization in artifact.materializations:
                if materialization.storage_type == "gcs":
                    try:
                        file_contents = await file_storage.download_file(materialization.uri)
                        
                        # Convert bytes to JSON-serializable format
                        if isinstance(file_contents, bytes):
                            try:
                                renderings["file_contents"] = file_contents.decode('utf-8')
                            except UnicodeDecodeError:
                                import base64
                                renderings["file_contents"] = base64.b64encode(file_contents).decode('utf-8')
                                renderings["file_contents_encoding"] = "base64"
                        else:
                            renderings["file_contents"] = file_contents
                        
                        break  # Use first GCS materialization
                    except Exception as e:
                        self.logger.warning(f"Failed to retrieve content from materialization {materialization.uri}: {e}")
        
        # Create structured artifact for response
        semantic_payload = {
            "artifact_id": artifact.artifact_id,
            "artifact_type": artifact.artifact_type,
            "lifecycle_state": artifact.lifecycle_state,
            "parent_artifacts": artifact.parent_artifacts,
            "semantic_descriptor": {
                "schema": artifact.semantic_descriptor.schema,
                "parser_type": artifact.semantic_descriptor.parser_type,
                "embedding_model": artifact.semantic_descriptor.embedding_model
            },
            "materializations": [
                {
                    "materialization_id": m.materialization_id,
                    "storage_type": m.storage_type,
                    "uri": m.uri,
                    "format": m.format
                }
                for m in artifact.materializations
            ],
            "created_at": artifact.created_at,
            "updated_at": artifact.updated_at
        }
        
        structured_artifact = create_structured_artifact(
            result_type="artifact",
            semantic_payload=semantic_payload,
            renderings=renderings
        )
        
        return {
            "artifacts": {
                "artifact": structured_artifact
            },
            "events": []
        }
    
    async def handle_archive_artifact(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Handle archive_artifact intent - transition artifact lifecycle state to ARCHIVED.
        
        Intent parameters:
        - artifact_id: str (REQUIRED) - Artifact identifier
        - artifact_type: str (optional) - Artifact type (default: "file")
        - reason: str (optional) - Archive reason
        """
        artifact_id = intent.parameters.get("artifact_id")
        if not artifact_id:
            raise ValueError("artifact_id is required for archive_artifact intent")
        
        artifact_type = intent.parameters.get("artifact_type", "file")
        reason = intent.parameters.get("reason", "User requested")
        
        # Update artifact lifecycle state to ARCHIVED
        success = await context.state_surface.update_artifact_lifecycle(
            artifact_id=artifact_id,
            tenant_id=context.tenant_id,
            new_state=LifecycleState.ARCHIVED.value,
            reason=reason
        )
        
        if not success:
            raise RuntimeError(f"Failed to archive artifact: {artifact_id}")
        
        self.logger.info(f"Artifact archived: {artifact_id} (reason: {reason})")
        
        return {
            "artifacts": {
                "artifact_id": artifact_id,
                "artifact_type": artifact_type,
                "lifecycle_state": LifecycleState.ARCHIVED.value,
                "archived_at": self.clock.now_iso(),
                "archive_reason": reason
            },
            "events": [
                {
                    "type": "artifact_archived",
                    "artifact_id": artifact_id,
                    "artifact_type": artifact_type,
                    "reason": reason
                }
            ]
        }
    
    async def handle_delete_artifact(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Handle delete_artifact intent - transition artifact lifecycle state to DELETED and delete materializations.
        
        Intent parameters:
        - artifact_id: str (REQUIRED) - Artifact identifier
        - artifact_type: str (optional) - Artifact type (default: "file")
        - confirm: bool (REQUIRED) - Confirmation flag (must be True)
        - hard_delete: bool (optional) - If True, actually delete artifact record (default: False)
        """
        artifact_id = intent.parameters.get("artifact_id")
        if not artifact_id:
            raise ValueError("artifact_id is required for delete_artifact intent")
        
        confirm = intent.parameters.get("confirm", False)
        if not confirm:
            raise ValueError("confirm=True is required for delete_artifact intent (permanent deletion)")
        
        artifact_type = intent.parameters.get("artifact_type", "file")
        hard_delete = intent.parameters.get("hard_delete", False)
        
        # Resolve artifact to get materializations
        artifact = await context.state_surface.resolve_artifact(
            artifact_id=artifact_id,
            artifact_type=artifact_type,
            tenant_id=context.tenant_id
        )
        
        if not artifact:
            raise ValueError(f"Artifact not found or not accessible: {artifact_id}")
        
        # Delete materializations from storage
        if not self.public_works:
            raise RuntimeError("Public Works not initialized - cannot access FileStorageAbstraction")
        
        file_storage = self.public_works.get_file_storage_abstraction()
        if not file_storage:
            raise RuntimeError("FileStorageAbstraction not available")
        
        deleted_materializations = []
        for materialization in artifact.materializations:
            try:
                if materialization.storage_type == "gcs":
                    delete_success = await file_storage.delete_file(materialization.uri)
                    if delete_success:
                        deleted_materializations.append(materialization.materialization_id)
                # TODO: Handle other storage types (DuckDB, ArangoDB)
            except Exception as e:
                self.logger.warning(f"Failed to delete materialization {materialization.uri}: {e}")
        
        # Update artifact lifecycle state to DELETED
        success = await context.state_surface.update_artifact_lifecycle(
            artifact_id=artifact_id,
            tenant_id=context.tenant_id,
            new_state=LifecycleState.DELETED.value,
            reason="User requested deletion"
        )
        
        if not success:
            raise RuntimeError(f"Failed to delete artifact: {artifact_id}")
        
        # TODO: If hard_delete=True, actually delete artifact record from Artifact Registry
        
        self.logger.info(f"Artifact deleted: {artifact_id} (materializations: {len(deleted_materializations)})")
        
        return {
            "artifacts": {
                "artifact_id": artifact_id,
                "artifact_type": artifact_type,
                "lifecycle_state": LifecycleState.DELETED.value,
                "deleted_at": self.clock.now_iso(),
                "deleted_materializations": deleted_materializations
            },
            "events": [
                {
                    "type": "artifact_deleted",
                    "artifact_id": artifact_id,
                    "artifact_type": artifact_type
                }
            ]
        }
    
