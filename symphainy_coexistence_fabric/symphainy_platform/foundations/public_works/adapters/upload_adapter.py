"""
Upload Adapter - Infrastructure Implementation (Layer 0)

Wraps existing file upload flow for ingestion architecture.
Preserves existing upload pathway while enabling unified ingestion.

WHAT (Infrastructure Role): I provide file upload ingestion
HOW (Infrastructure Implementation): I use FileStorageAbstraction to store files
"""

import uuid
from typing import Dict, Any, Optional
from utilities import get_logger, get_clock

from ..protocols.ingestion_protocol import (
    IngestionRequest,
    IngestionResult,
    IngestionType
)


class UploadAdapter:
    """
    Upload adapter - wraps existing file upload flow.
    
    This adapter preserves the existing upload pathway while enabling
    unified ingestion architecture.
    """
    
    def __init__(self, file_storage_abstraction: Any):
        """
        Initialize upload adapter.
        
        Args:
            file_storage_abstraction: FileStorageAbstraction instance
        """
        self.file_storage = file_storage_abstraction
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
    
    async def ingest(self, request: IngestionRequest) -> IngestionResult:
        """
        Ingest via file upload (existing flow).
        
        Args:
            request: Ingestion request with UPLOAD type
        
        Returns:
            IngestionResult with file_id, file_reference, storage_location, and metadata
        """
        if request.ingestion_type != IngestionType.UPLOAD:
            return IngestionResult(
                success=False,
                file_id="",
                file_reference="",
                storage_location="",
                ingestion_metadata={},
                error=f"Upload adapter only handles UPLOAD, got {request.ingestion_type}"
            )
        
        if not request.data:
            return IngestionResult(
                success=False,
                file_id="",
                file_reference="",
                storage_location="",
                ingestion_metadata={},
                error="Upload adapter requires file data"
            )
        
        # Generate file ID and reference
        file_id = str(uuid.uuid4())
        filename = request.source_metadata.get("filename", "uploaded_file")
        
        # Storage path in GCS (tenant/session/file_id format)
        storage_path = f"{request.tenant_id}/{request.session_id}/{file_id}/{filename}"
        file_reference = f"file:{request.tenant_id}:{request.session_id}:{file_id}"
        
        # Prepare metadata
        upload_metadata = {
            **request.source_metadata,
            "ingestion_type": "upload",
            "ingestion_timestamp": self.clock.now_iso(),
            "tenant_id": request.tenant_id,
            "session_id": request.session_id,
            "file_id": file_id
        }
        
        # Use existing file storage abstraction
        success = await self.file_storage.upload_file(
            file_path=storage_path,
            file_data=request.data,
            metadata=upload_metadata
        )
        
        if success:
            self.logger.info(f"File uploaded successfully: {storage_path} ({len(request.data)} bytes)")
            return IngestionResult(
                success=True,
                file_id=file_id,
                file_reference=file_reference,
                storage_location=storage_path,
                ingestion_metadata={
                    "ingestion_type": "upload",
                    "original_filename": filename,
                    "file_size": len(request.data),
                    "storage_path": storage_path
                }
            )
        else:
            return IngestionResult(
                success=False,
                file_id="",
                file_reference="",
                storage_location="",
                ingestion_metadata={},
                error="Upload failed - FileStorageAbstraction.upload_file() returned False"
            )
