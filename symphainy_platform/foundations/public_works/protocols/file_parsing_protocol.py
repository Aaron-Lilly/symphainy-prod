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
    """
    success: bool
    text_content: str = ""
    structured_data: Optional[Dict[str, Any]] = None  # Tables, records, etc.
    metadata: Optional[Dict[str, Any]] = None
    validation_rules: Optional[Dict[str, Any]] = None  # 88-level fields, level-01 metadata (for insights pillar)
    error: Optional[str] = None
    timestamp: str = ""

    def __post_init__(self):
        """Set timestamp if not provided."""
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()


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
