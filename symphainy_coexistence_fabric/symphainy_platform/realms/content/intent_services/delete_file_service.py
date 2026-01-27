"""
Delete File Intent Service

Permanently deletes a file artifact (hard delete).

Contract: docs/intent_contracts/journey_content_file_management/intent_delete_file.md

WHAT (Service Role): I permanently delete file artifacts
HOW (Service Implementation): I delete files from storage and remove from State Surface
"""

from typing import Dict, Any, Optional

from utilities import get_logger, generate_event_id, get_clock
from symphainy_platform.bases.intent_service_base import BaseIntentService
from symphainy_platform.runtime.execution_context import ExecutionContext
from symphainy_platform.runtime.intent_model import Intent


class DeleteFileService(BaseIntentService):
    """
    Delete File Intent Service.
    
    Handles the `delete_file` intent:
    - Validates file_id or file_reference parameter
    - Gets file metadata from State Surface
    - Deletes file from storage (GCS/Supabase)
    - Removes file reference from State Surface
    - Removes any associated artifacts/embeddings
    
    This is a HARD delete - file is permanently removed.
    For soft delete (archive), use ArchiveFileService.
    """
    
    def __init__(
        self,
        public_works: Optional[Any] = None,
        state_surface: Optional[Any] = None
    ):
        """
        Initialize Delete File Service.
        
        Args:
            public_works: Public Works Foundation Service
            state_surface: State Surface
        """
        super().__init__(
            service_id="delete_file_service",
            intent_type="delete_file",
            public_works=public_works,
            state_surface=state_surface
        )
    
    async def execute(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Execute delete_file intent.
        
        Args:
            intent: The delete_file intent
            context: Execution context
        
        Returns:
            Dict with artifacts confirming deletion and events
        
        Raises:
            ValueError: If file_id/file_reference not provided or file not found
        """
        file_id = intent.parameters.get("file_id")
        file_reference = intent.parameters.get("file_reference")
        delete_artifacts = intent.parameters.get("delete_artifacts", True)
        reason = intent.parameters.get("reason", "User requested deletion")
        
        if not file_id and not file_reference:
            raise ValueError("Either file_id or file_reference is required for delete_file intent")
        
        # Construct file reference if not provided
        if not file_reference:
            file_reference = f"file:{context.tenant_id}:{context.session_id}:{file_id}"
        
        # Get file metadata from State Surface
        if not context.state_surface:
            raise RuntimeError("State Surface not available")
        
        file_metadata = await context.state_surface.get_file_metadata(file_reference)
        if not file_metadata:
            self.logger.warning(f"File not found in State Surface (may already be deleted): {file_reference}")
            # Return success anyway - idempotent delete
            return {
                "artifacts": {
                    "file_id": file_id,
                    "file_reference": file_reference,
                    "status": "deleted",
                    "already_deleted": True
                },
                "events": [{
                    "type": "file_delete_attempted",
                    "event_id": generate_event_id(),
                    "file_reference": file_reference,
                    "result": "not_found"
                }]
            }
        
        storage_location = file_metadata.get("storage_location")
        deleted_at = self.clock.now().isoformat() if self.clock else None
        deleted_items = []
        
        # Step 1: Delete from storage (GCS/Supabase)
        if storage_location and self.public_works:
            try:
                file_storage = self.public_works.get_file_storage_abstraction()
                if file_storage:
                    await file_storage.delete_file(storage_location)
                    deleted_items.append(f"storage:{storage_location}")
                    self.logger.info(f"Deleted file from storage: {storage_location}")
            except Exception as e:
                self.logger.warning(f"Failed to delete from storage (may already be gone): {e}")
        
        # Step 2: Delete associated artifacts if requested
        if delete_artifacts:
            # Delete parsed content
            parsed_file_id = file_metadata.get("parsed_file_id")
            if parsed_file_id:
                try:
                    parsed_ref = f"parsed:{context.tenant_id}:{context.session_id}:{parsed_file_id}"
                    await context.state_surface.delete_file_reference(
                        session_id=context.session_id,
                        tenant_id=context.tenant_id,
                        file_reference=parsed_ref
                    )
                    deleted_items.append(f"parsed:{parsed_file_id}")
                except Exception as e:
                    self.logger.warning(f"Failed to delete parsed content: {e}")
            
            # Delete embeddings
            embedding_id = file_metadata.get("embedding_id")
            if embedding_id:
                try:
                    embedding_ref = f"embedding:{context.tenant_id}:{context.session_id}:{embedding_id}"
                    await context.state_surface.delete_file_reference(
                        session_id=context.session_id,
                        tenant_id=context.tenant_id,
                        file_reference=embedding_ref
                    )
                    deleted_items.append(f"embedding:{embedding_id}")
                except Exception as e:
                    self.logger.warning(f"Failed to delete embeddings: {e}")
        
        # Step 3: Delete file reference from State Surface
        try:
            await context.state_surface.delete_file_reference(
                session_id=context.session_id,
                tenant_id=context.tenant_id,
                file_reference=file_reference
            )
            deleted_items.append(f"reference:{file_reference}")
            self.logger.info(f"Deleted file reference from State Surface: {file_reference}")
        except Exception as e:
            self.logger.error(f"Failed to delete file reference: {e}")
            raise
        
        self.logger.info(f"File permanently deleted: {file_id or file_reference} (reason: {reason})")
        
        # Create event
        event = {
            "type": "file_deleted",
            "event_id": generate_event_id(),
            "file_id": file_id,
            "file_reference": file_reference,
            "reason": reason,
            "deleted_at": deleted_at,
            "deleted_items": deleted_items
        }
        
        return {
            "artifacts": {
                "file_id": file_id,
                "file_reference": file_reference,
                "status": "deleted",
                "deleted_at": deleted_at,
                "deleted_items": deleted_items,
                "artifacts_deleted": delete_artifacts
            },
            "events": [event]
        }
