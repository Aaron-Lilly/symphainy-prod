"""
Delete File Service (Platform SDK)

Permanently deletes a file artifact (hard delete).

Uses ctx.state_surface and ctx.platform for deletion.

Contract: docs/intent_contracts/journey_content_file_management/intent_delete_file.md
"""

from typing import Dict, Any, List

from utilities import get_logger, generate_event_id, get_clock

from symphainy_platform.civic_systems.platform_sdk import (
    PlatformIntentService,
    PlatformContext
)


class DeleteFileService(PlatformIntentService):
    """
    Delete File Service using Platform SDK.
    
    Handles the `delete_file` intent:
    - Validates file_id or file_reference parameter
    - Gets file metadata from state_surface
    - Deletes file from storage
    - Removes file reference from state_surface
    - Removes any associated artifacts/embeddings
    
    This is a HARD delete - file is permanently removed.
    For soft delete (archive), use ArchiveFileService.
    """
    
    intent_type = "delete_file"
    
    def __init__(self, service_id: str = "delete_file_service"):
        """Initialize Delete File Service."""
        super().__init__(service_id=service_id)
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
    
    async def execute(self, ctx: PlatformContext) -> Dict[str, Any]:
        """
        Execute delete_file intent.
        
        Args:
            ctx: Platform context with intent and platform services
        
        Returns:
            Dict with artifacts confirming deletion and events
        """
        self.logger.info(f"Executing delete_file: {ctx.execution_id}")
        
        file_id = ctx.intent.parameters.get("file_id")
        file_reference = ctx.intent.parameters.get("file_reference")
        delete_artifacts = ctx.intent.parameters.get("delete_artifacts", True)
        reason = ctx.intent.parameters.get("reason", "User requested deletion")
        
        if not file_id and not file_reference:
            raise ValueError("Either file_id or file_reference is required")
        
        # Construct file reference if not provided
        if not file_reference:
            file_reference = f"file:{ctx.tenant_id}:{ctx.session_id}:{file_id}"
        
        # Get file metadata from state_surface
        if not ctx.state_surface:
            raise RuntimeError("State Surface not available")
        
        file_metadata = await ctx.state_surface.get_file_metadata(file_reference)
        if not file_metadata:
            self.logger.warning(f"File not found (may already be deleted): {file_reference}")
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
        deleted_items: List[str] = []
        
        # Step 1: Delete from storage via ctx.platform (protocol-compliant)
        if storage_location:
            try:
                if not ctx.platform:
                    raise RuntimeError("Platform contract §8A: ctx.platform required for file deletion")
                
                result = await ctx.platform.delete_file(storage_location)
                if result.get("success"):
                    deleted_items.append(f"storage:{storage_location}")
                    self.logger.info(f"Deleted file from storage: {storage_location}")
                else:
                    self.logger.warning(f"Failed to delete from storage: {result.get('error')}")
            except Exception as e:
                self.logger.warning(f"Failed to delete from storage (may already be gone): {e}")
        
        # Step 2: Delete associated artifacts if requested
        if delete_artifacts:
            # Delete parsed content
            parsed_file_id = file_metadata.get("parsed_file_id")
            if parsed_file_id:
                try:
                    parsed_ref = f"parsed:{ctx.tenant_id}:{ctx.session_id}:{parsed_file_id}"
                    await ctx.state_surface.delete_file_reference(
                        session_id=ctx.session_id,
                        tenant_id=ctx.tenant_id,
                        file_reference=parsed_ref
                    )
                    deleted_items.append(f"parsed:{parsed_file_id}")
                except Exception as e:
                    self.logger.warning(f"Failed to delete parsed content: {e}")
            
            # Delete embeddings
            embedding_id = file_metadata.get("embedding_id")
            if embedding_id:
                try:
                    embedding_ref = f"embedding:{ctx.tenant_id}:{ctx.session_id}:{embedding_id}"
                    await ctx.state_surface.delete_file_reference(
                        session_id=ctx.session_id,
                        tenant_id=ctx.tenant_id,
                        file_reference=embedding_ref
                    )
                    deleted_items.append(f"embedding:{embedding_id}")
                except Exception as e:
                    self.logger.warning(f"Failed to delete embeddings: {e}")
        
        # Step 3: Delete file reference from state_surface
        try:
            await ctx.state_surface.delete_file_reference(
                session_id=ctx.session_id,
                tenant_id=ctx.tenant_id,
                file_reference=file_reference
            )
            deleted_items.append(f"reference:{file_reference}")
            self.logger.info(f"Deleted file reference: {file_reference}")
        except Exception as e:
            self.logger.error(f"Failed to delete file reference: {e}")
            raise
        
        self.logger.info(f"✅ File permanently deleted: {file_id or file_reference} (reason: {reason})")
        
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
