"""
File Parsing Protocol - New Architecture

Defines the interface for file parsing operations using State Surface.
All file data is accessed via State Surface references, not passed as bytes.

WHAT (Infrastructure Role): I define how files should be parsed
HOW (Infrastructure Implementation): I provide the interface for file parsing logic
"""

from typing import Protocol, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class FileParsingRequest:
    """
    Request for file parsing using State Surface references.
    
    All file data is accessed via State Surface, not passed as bytes.
    """
    file_reference: str  # State Surface reference (e.g., "file:tenant:session:file_id")
    copybook_reference: Optional[str] = None  # State Surface reference for mainframe files
    filename: str = ""
    options: Optional[Dict[str, Any]] = None
    state_surface: Optional[Any] = None  # StateSurface instance for file retrieval


@dataclass
class FileParsingResult:
    """
    Result of file parsing operations.
    
    Standardized format for all parsing results.
    
    REQUIRED STANDARDS (for downstream chunking and semantic services):
    - parsing_type: MUST be set explicitly ("structured", "unstructured", "hybrid", "mainframe", "workflow", "sop", "data_model")
    - text_content: MUST be None (not empty string) if no text content exists
    - metadata.structure: MUST be populated for chunking service (pages, sections, paragraphs, rows, tasks, etc.)
    - structured_data: MUST be JSON-serializable, MUST NOT contain nested "metadata" or "structure"
    - structured_data.format: MUST be set ("structured", "unstructured", "hybrid", "mainframe", "workflow", "sop", "data_model")
    """
    success: bool
    text_content: Optional[str] = None  # Changed: None instead of empty string (None = no text, "" = empty text)
    structured_data: Optional[Dict[str, Any]] = None  # Tables, records, etc. - MUST be JSON-serializable
    metadata: Optional[Dict[str, Any]] = None  # MUST include "parsing_type" and "structure"
    validation_rules: Optional[Dict[str, Any]] = None  # 88-level fields, level-01 metadata (for insights pillar)
    error: Optional[str] = None
    timestamp: str = ""
    parsing_type: Optional[str] = None  # NEW: Explicit parsing type ("structured", "unstructured", "hybrid", "mainframe", "workflow", "sop", "data_model")

    def __post_init__(self):
        """Set timestamp if not provided."""
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()
        
        # Ensure metadata exists and includes parsing_type
        if self.metadata is None:
            self.metadata = {}
        
        # Set parsing_type in metadata if not already set
        if self.parsing_type and "parsing_type" not in self.metadata:
            self.metadata["parsing_type"] = self.parsing_type


class FileParsingProtocol(Protocol):
    """
    Protocol for file parsing operations.
    
    All implementations MUST:
    - Use State Surface for file retrieval (not accept bytes directly)
    - Return FileParsingResult with proper structure
    - Extract validation rules for insights pillar (where applicable)
    - Follow the new architecture patterns
    """
    
    async def parse_file(
        self,
        request: FileParsingRequest
    ) -> FileParsingResult:
        """
        Parse file using State Surface reference.
        
        Implementation should:
        1. Retrieve file from State Surface using file_reference
        2. Retrieve copybook from State Surface if copybook_reference provided
        3. Parse file using appropriate adapter
        4. Return FileParsingResult with structured data
        
        Args:
            request: FileParsingRequest with file_reference and options
        
        Returns:
            FileParsingResult with parsed data
        """
        ...
