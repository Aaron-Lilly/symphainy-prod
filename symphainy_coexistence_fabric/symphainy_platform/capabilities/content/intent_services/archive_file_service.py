"""
Archive File Service (Platform SDK)

Archives a file artifact (soft delete).

Uses ctx.state_surface for state transitions.

Contract: docs/intent_contracts/journey_content_file_management/intent_archive_file.md
"""

from typing import Dict, Any

from utilities import get_logger, generate_event_id, get_clock

from symphainy_platform.civic_systems.platform_sdk import (
    PlatformIntentService,
    PlatformContext
)


class ArchiveFileService(PlatformIntentService):
    """
    Archive File Service using Platform SDK.
    
    Handles the `archive_file` intent:
    - Validates file_id or file_reference parameter
    - Gets file metadata from state_surface
    - Updates metadata to mark as archived (soft delete)
    - Stores updated metadata back
    
    This is a soft delete - file remains in storage but marked as archived.
    """
    
    intent_type = "archive_file"
    
    def __init__(self, service_id: str = "archive_file_service"):
        """Initialize Archive File Service."""
        super().__init__(service_id=service_id)
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
    
    async def execute(self, ctx: PlatformContext) -> Dict[str, Any]:
        """
        Execute archive_file intent.
        
        Args:
            ctx: Platform context with intent and platform services
        
        Returns:
            Dict with artifacts confirming archive and events
        """
        self.logger.info(f"Executing archive_file: {ctx.execution_id}")
        
        file_id = ctx.intent.parameters.get("file_id")
        file_reference = ctx.intent.parameters.get("file_reference")
        reason = ctx.intent.parameters.get("reason", "User requested")
        
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
            raise ValueError(f"File not found: {file_reference}")
        
        storage_location = file_metadata.get("storage_location")
        if not storage_location:
            raise ValueError(f"Storage location not found for file: {file_reference}")
        
        # Update metadata to mark as archived
        existing_metadata = file_metadata.get("metadata", {}) if isinstance(file_metadata.get("metadata"), dict) else {}
        archived_at = self.clock.now().isoformat() if self.clock else None
        
        updated_metadata = {
            **existing_metadata,
            "status": "archived",
            "archived_at": archived_at,
            "archive_reason": reason,
            "lifecycle_state": "archived"
        }
        
        # Update in state_surface
        await ctx.state_surface.store_file_reference(
            session_id=ctx.session_id,
            tenant_id=ctx.tenant_id,
            file_reference=file_reference,
            storage_location=storage_location,
            filename=file_metadata.get("filename", ""),
            metadata={
                **file_metadata,
                **updated_metadata
            }
        )
        
        self.logger.info(f"✅ File archived: {file_id or file_reference} (reason: {reason})")
        
        # Create event
        event = {
            "type": "file_archived",
            "event_id": generate_event_id(),
            "file_id": file_id,
            "file_reference": file_reference,
            "reason": reason,
            "archived_at": archived_at
        }
        
        return {
            "artifacts": {
                "file_id": file_id,
                "file_reference": file_reference,
                "status": "archived",
                "archived_at": archived_at,
                "lifecycle_state": "archived"
            },
            "events": [event]
        }
