"""
Ingestion Service - Content Realm

Handles all ingestion methods and routes to parsing.
Unified entry point for Upload, EDI, and API ingestion.
"""

from typing import Dict, Any, Optional
from utilities import get_logger

from symphainy_platform.foundations.public_works.protocols.ingestion_protocol import (
    IngestionRequest,
    IngestionResult,
    IngestionProtocol
)


class IngestionService:
    """
    Content Realm Ingestion Service.
    
    Handles all ingestion methods and routes to parsing.
    Provides unified entry point for Upload, EDI, and API ingestion.
    """
    
    def __init__(
        self,
        ingestion_abstraction: IngestionProtocol,
        content_orchestrator: Any,
        state_surface: Any
    ):
        """
        Initialize Ingestion Service.
        
        Args:
            ingestion_abstraction: Ingestion abstraction (from Public Works)
            content_orchestrator: Content Orchestrator for parsing
            state_surface: State Surface for file reference storage
        """
        self.ingestion = ingestion_abstraction
        self.orchestrator = content_orchestrator
        self.state_surface = state_surface
        self.logger = get_logger(self.__class__.__name__)
    
    async def ingest_and_parse(
        self,
        request: IngestionRequest,
        parse_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Ingest data and immediately parse it.
        
        This is the unified entry point for all ingestion methods.
        All ingestion methods converge here before parsing.
        
        Flow:
        1. Ingest (converges all methods to file storage)
        2. Store file reference in State Surface
        3. Parse (existing flow - unchanged)
        
        Args:
            request: Ingestion request with type, metadata, and data
            parse_options: Optional parsing options
        
        Returns:
            Dictionary with ingestion and parsing results
        """
        # Step 1: Ingest (converges all methods to file storage)
        ingestion_result = await self.ingestion.ingest_data(request)
        
        if not ingestion_result.success:
            return {
                "success": False,
                "error": ingestion_result.error,
                "ingestion_metadata": ingestion_result.ingestion_metadata
            }
        
        # Step 2: Store file reference in State Surface
        # File already stored by adapter, just register the reference
        await self.state_surface.store_file_reference(
            session_id=request.session_id,
            tenant_id=request.tenant_id,
            file_reference=ingestion_result.file_reference,
            storage_location=ingestion_result.storage_location,
            filename=ingestion_result.ingestion_metadata.get("original_filename", ingestion_result.file_id),
            metadata={
                **ingestion_result.ingestion_metadata,
                "file_id": ingestion_result.file_id,
                "file_reference": ingestion_result.file_reference
            }
        )
        
        # Step 3: Parse (existing flow - unchanged)
        parse_result = await self.orchestrator.parse_file(
            file_reference=ingestion_result.file_reference,
            filename=ingestion_result.ingestion_metadata.get("original_filename", ingestion_result.file_id),
            parsing_type=None,  # Auto-detect
            options=parse_options
        )
        
        return {
            "success": True,
            "file_id": ingestion_result.file_id,
            "file_reference": ingestion_result.file_reference,
            "storage_location": ingestion_result.storage_location,
            "ingestion_metadata": ingestion_result.ingestion_metadata,
            "parse_result": parse_result
        }
    
    async def ingest_only(
        self,
        request: IngestionRequest
    ) -> IngestionResult:
        """
        Ingest data without parsing.
        
        Use this when you want to ingest but parse later.
        
        Args:
            request: Ingestion request
        
        Returns:
            IngestionResult with file_id, file_reference, storage_location, and metadata
        """
        # Ingest (converges all methods to file storage)
        ingestion_result = await self.ingestion.ingest_data(request)
        
        if not ingestion_result.success:
            return ingestion_result
        
        # Store file reference in State Surface
        await self.state_surface.store_file_reference(
            session_id=request.session_id,
            tenant_id=request.tenant_id,
            file_reference=ingestion_result.file_reference,
            storage_location=ingestion_result.storage_location,
            filename=ingestion_result.ingestion_metadata.get("original_filename", ingestion_result.file_id),
            metadata={
                **ingestion_result.ingestion_metadata,
                "file_id": ingestion_result.file_id,
                "file_reference": ingestion_result.file_reference
            }
        )
        
        return ingestion_result
