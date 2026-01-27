"""
API Adapter - Infrastructure Implementation (Layer 0)

Handles API-based ingestion (REST, GraphQL, Webhook).
Converts API payloads to files and stores via FileStorageAbstraction.

WHAT (Infrastructure Role): I provide API-based ingestion
HOW (Infrastructure Implementation): I convert API payloads to files and use FileStorageAbstraction
"""

import json
import uuid
from typing import Dict, Any, Optional
from utilities import get_logger, get_clock

from ..protocols.ingestion_protocol import (
    IngestionRequest,
    IngestionResult,
    IngestionType
)


class APIAdapter:
    """
    API adapter - handles API-based ingestion.
    
    Supports:
    - REST API (JSON payloads)
    - GraphQL API (queries/mutations)
    - Webhook callbacks
    """
    
    def __init__(self, file_storage_abstraction: Any):
        """
        Initialize API adapter.
        
        Args:
            file_storage_abstraction: FileStorageAbstraction instance
        """
        self.file_storage = file_storage_abstraction
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
    
    async def ingest(self, request: IngestionRequest) -> IngestionResult:
        """
        Ingest via API.
        
        Args:
            request: Ingestion request with API type
        
        Returns:
            IngestionResult with file_id, file_reference, storage_location, and metadata
        """
        if request.ingestion_type != IngestionType.API:
            return IngestionResult(
                success=False,
                file_id="",
                file_reference="",
                storage_location="",
                ingestion_metadata={},
                error=f"API adapter only handles API, got {request.ingestion_type}"
            )
        
        if not request.api_payload:
            return IngestionResult(
                success=False,
                file_id="",
                file_reference="",
                storage_location="",
                ingestion_metadata={},
                error="API adapter requires api_payload"
            )
        
        # Extract API-specific metadata
        api_type = request.source_metadata.get("api_type", "rest")  # rest, graphql, webhook
        endpoint = request.source_metadata.get("endpoint")
        
        # Convert API payload to file format
        file_data = await self._convert_api_payload_to_file(
            request.api_payload,
            api_type
        )
        
        # Generate file ID and reference
        file_id = str(uuid.uuid4())
        filename = request.source_metadata.get(
            "filename",
            f"api_{api_type}_{self.clock.now_iso().replace(':', '-')}.json"
        )
        
        # Storage path in GCS (tenant/session/file_id format)
        storage_path = f"{request.tenant_id}/{request.session_id}/{file_id}/{filename}"
        file_reference = f"file:{request.tenant_id}:{request.session_id}:{file_id}"
        
        # Prepare metadata
        api_metadata = {
            **request.source_metadata,
            "ingestion_type": "api",
            "api_type": api_type,
            "endpoint": endpoint,
            "ingestion_timestamp": self.clock.now_iso(),
            "tenant_id": request.tenant_id,
            "session_id": request.session_id,
            "file_id": file_id
        }
        
        # Store as file (same as upload)
        success = await self.file_storage.upload_file(
            file_path=storage_path,
            file_data=file_data,
            metadata=api_metadata
        )
        
        if success:
            self.logger.info(f"API payload ingested successfully: {storage_path} ({len(file_data)} bytes)")
            return IngestionResult(
                success=True,
                file_id=file_id,
                file_reference=file_reference,
                storage_location=storage_path,
                ingestion_metadata={
                    "ingestion_type": "api",
                    "api_type": api_type,
                    "endpoint": endpoint,
                    "original_filename": filename,
                    "file_size": len(file_data),
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
                error="API ingestion failed - FileStorageAbstraction.upload_file() returned False"
            )
    
    async def _convert_api_payload_to_file(
        self,
        payload: Dict[str, Any],
        api_type: str
    ) -> bytes:
        """
        Convert API payload to file bytes.
        
        Args:
            payload: API payload dictionary
            api_type: API type (rest, graphql, webhook)
        
        Returns:
            File data as bytes
        """
        if api_type == "rest" or api_type == "graphql":
            # Convert JSON payload to JSON file
            return json.dumps(payload, indent=2).encode('utf-8')
        else:
            # Webhook or other - convert to JSON
            return json.dumps(payload).encode('utf-8')
