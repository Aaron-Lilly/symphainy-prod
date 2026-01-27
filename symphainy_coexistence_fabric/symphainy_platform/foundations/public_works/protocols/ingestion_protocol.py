"""
Ingestion Protocol - Abstraction Contract (Layer 2)

Defines the interface for ingestion operations.
Enables unified ingestion from multiple sources (Upload, EDI, API).

WHAT (Infrastructure Role): I define the contract for ingestion operations
HOW (Infrastructure Implementation): I specify the interface for ingestion
"""

from typing import Protocol, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class IngestionType(str, Enum):
    """Ingestion method types."""
    UPLOAD = "upload"      # Direct file upload (existing)
    EDI = "edi"            # EDI protocol (AS2, SFTP, etc.)
    API = "api"            # REST/GraphQL API


@dataclass
class IngestionRequest:
    """Unified ingestion request."""
    ingestion_type: IngestionType
    tenant_id: str
    session_id: str
    source_metadata: Dict[str, Any]  # Source-specific metadata
    data: Optional[bytes] = None      # For upload/EDI
    api_payload: Optional[Dict[str, Any]] = None  # For API
    options: Optional[Dict[str, Any]] = None


@dataclass
class IngestionResult:
    """Unified ingestion result."""
    success: bool
    file_id: str  # Unified file_id after ingestion
    file_reference: str  # State Surface reference
    storage_location: str  # Where file is stored (GCS path, ArangoDB doc ID, etc.)
    ingestion_metadata: Dict[str, Any]  # Ingestion-specific metadata
    error: Optional[str] = None


class IngestionAdapter(Protocol):
    """Protocol for ingestion adapters (Layer 0)."""
    
    async def ingest(
        self,
        request: IngestionRequest
    ) -> IngestionResult:
        """
        Ingest data from source.
        
        Args:
            request: Ingestion request with type, metadata, and data
        
        Returns:
            IngestionResult with file_id, file_reference, storage_location, and metadata
        """
        ...


class IngestionProtocol(Protocol):
    """Protocol for ingestion abstraction (Layer 1)."""
    
    async def ingest_data(
        self,
        request: IngestionRequest
    ) -> IngestionResult:
        """
        Ingest data using appropriate adapter.
        
        Routes to the correct adapter based on ingestion_type.
        
        Args:
            request: Ingestion request
        
        Returns:
            IngestionResult with file_id, file_reference, storage_location, and metadata
        """
        ...
