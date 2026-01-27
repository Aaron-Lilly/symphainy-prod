"""
Archive File Intent Service

Archives a file artifact (soft delete).

Contract: docs/intent_contracts/journey_content_file_management/intent_archive_file.md

WHAT (Service Role): I archive file artifacts
HOW (Service Implementation): I mark files as archived in State Surface (soft delete)
"""

from typing import Dict, Any, Optional

from utilities import get_logger, generate_event_id, get_clock
from symphainy_platform.bases.intent_service_base import BaseIntentService
from symphainy_platform.runtime.execution_context import ExecutionContext
from symphainy_platform.runtime.intent_model import Intent


class ArchiveFileService(BaseIntentService):
    """
    Archive File Intent Service.
    
    Handles the `archive_file` intent:
    - Validates file_id or file_reference parameter
    - Gets file metadata from State Surface
    - Updates metadata to mark as archived (soft delete)
    - Stores updated metadata back to State Surface
    
    This is a soft delete - file remains in storage but marked as archived.
    """
    
    def __init__(
        self,
        public_works: Optional[Any] = None,
        state_surface: Optional[Any] = None
    ):
        """
        Initialize Archive File Service.
        
        Args:
            public_works: Public Works Foundation Service
            state_surface: State Surface
        """
        super().__init__(
            service_id="archive_file_service",
            intent_type="archive_file",
            public_works=public_works,
            state_surface=state_surface
        )
    
    async def execute(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Execute archive_file intent.
        
        Args:
            intent: The archive_file intent
            context: Execution context
        
        Returns:
            Dict with artifacts confirming archive and events
        
        Raises:
            ValueError: If file_id/file_reference not provided or file not found
        """
        file_id = intent.parameters.get("file_id")
        file_reference = intent.parameters.get("file_reference")
        reason = intent.parameters.get("reason", "User requested")
        
        if not file_id and not file_reference:
            raise ValueError("Either file_id or file_reference is required for archive_file intent")
        
        # Construct file reference if not provided
        if not file_reference:
            file_reference = f"file:{context.tenant_id}:{context.session_id}:{file_id}"
        
        # Get file metadata from State Surface
        if not context.state_surface:
            raise RuntimeError("State Surface not available")
        
        file_metadata = await context.state_surface.get_file_metadata(file_reference)
        if not file_metadata:
            raise ValueError(f"File not found in State Surface: {file_reference}")
        
        storage_location = file_metadata.get("storage_location")
        if not storage_location:
            raise ValueError(f"Storage location not found for file: {file_reference}")
        
        # Update metadata to mark as archived (soft delete)
        existing_metadata = file_metadata.get("metadata", {}) if isinstance(file_metadata.get("metadata"), dict) else {}
        archived_at = self.clock.now().isoformat() if self.clock else None
        
        updated_metadata = {
            **existing_metadata,
            "status": "archived",
            "archived_at": archived_at,
            "archive_reason": reason,
            "lifecycle_state": "archived"
        }
        
        # Update in State Surface
        await context.state_surface.store_file_reference(
            session_id=context.session_id,
            tenant_id=context.tenant_id,
            file_reference=file_reference,
            storage_location=storage_location,
            filename=file_metadata.get("filename", ""),
            metadata={
                **file_metadata,
                **updated_metadata
            }
        )
        
        self.logger.info(f"File archived: {file_id or file_reference} (reason: {reason})")
        
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
