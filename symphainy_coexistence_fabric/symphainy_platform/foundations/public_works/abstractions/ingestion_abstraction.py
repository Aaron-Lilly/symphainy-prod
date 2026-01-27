"""
Ingestion Abstraction - Business Logic Implementation (Layer 1)

Unified interface for all ingestion methods.
Routes to appropriate adapter based on ingestion type.

WHAT (Infrastructure Role): I provide unified ingestion services
HOW (Infrastructure Implementation): I route to appropriate ingestion adapters
"""

from typing import Dict, Any, Optional
from utilities import get_logger

from ..protocols.ingestion_protocol import (
    IngestionRequest,
    IngestionResult,
    IngestionType,
    IngestionAdapter,
    IngestionProtocol
)


class IngestionAbstraction(IngestionProtocol):
    """
    Ingestion abstraction - unified interface for all ingestion methods.
    
    Routes to appropriate adapter based on ingestion type.
    Coordinates between ingestion adapters and provides unified interface.
    """
    
    def __init__(
        self,
        upload_adapter: Optional[IngestionAdapter] = None,
        edi_adapter: Optional[IngestionAdapter] = None,
        api_adapter: Optional[IngestionAdapter] = None
    ):
        """
        Initialize ingestion abstraction.
        
        Args:
            upload_adapter: Upload adapter (Layer 0)
            edi_adapter: EDI adapter (Layer 0) - optional
            api_adapter: API adapter (Layer 0) - optional
        """
        self.upload_adapter = upload_adapter
        self.edi_adapter = edi_adapter
        self.api_adapter = api_adapter
        self.logger = get_logger(self.__class__.__name__)
    
    async def ingest_data(self, request: IngestionRequest) -> IngestionResult:
        """
        Ingest data using appropriate adapter.
        
        Routes to the correct adapter based on ingestion_type.
        
        Args:
            request: Ingestion request with type, metadata, and data
        
        Returns:
            IngestionResult with file_id, file_reference, storage_location, and metadata
        """
        # Route to appropriate adapter
        if request.ingestion_type == IngestionType.UPLOAD:
            if not self.upload_adapter:
                return IngestionResult(
                    success=False,
                    file_id="",
                    file_reference="",
                    storage_location="",
                    ingestion_metadata={},
                    error="Upload adapter not configured"
                )
            return await self.upload_adapter.ingest(request)
        
        elif request.ingestion_type == IngestionType.EDI:
            if not self.edi_adapter:
                return IngestionResult(
                    success=False,
                    file_id="",
                    file_reference="",
                    storage_location="",
                    ingestion_metadata={},
                    error="EDI adapter not configured"
                )
            return await self.edi_adapter.ingest(request)
        
        elif request.ingestion_type == IngestionType.API:
            if not self.api_adapter:
                return IngestionResult(
                    success=False,
                    file_id="",
                    file_reference="",
                    storage_location="",
                    ingestion_metadata={},
                    error="API adapter not configured"
                )
            return await self.api_adapter.ingest(request)
        
        else:
            return IngestionResult(
                success=False,
                file_id="",
                file_reference="",
                storage_location="",
                ingestion_metadata={},
                error=f"Unknown ingestion type: {request.ingestion_type}"
            )
