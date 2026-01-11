"""
PDF Processing Abstraction - Layer 1

Lightweight coordination layer for PDF processing operations.
Uses State Surface for file retrieval.

WHAT (Infrastructure): I coordinate PDF processing operations
HOW (Abstraction): I provide lightweight coordination for PDF adapter
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from ..protocols.file_parsing_protocol import FileParsingRequest, FileParsingResult

logger = logging.getLogger(__name__)


class PdfProcessingAbstraction:
    """
    PDF Processing Infrastructure Abstraction.
    
    Lightweight coordination layer for PDF processing operations.
    Uses State Surface for file retrieval (new architecture).
    """
    
    def __init__(
        self,
        pdf_adapter: Optional[Any] = None,  # Will be PdfplumberAdapter or PyPDF2Adapter
        state_surface: Optional[Any] = None
    ):
        """
        Initialize PDF Processing Abstraction.
        
        Args:
            pdf_adapter: PDF adapter (Layer 0) - can be pdfplumber or pypdf2
            state_surface: State Surface instance for file retrieval
        """
        self.pdf_adapter = pdf_adapter
        self.state_surface = state_surface
        self.logger = logger
        
        self.logger.info("✅ PDF Processing Abstraction initialized")
    
    async def parse_file(self, request: FileParsingRequest) -> FileParsingResult:
        """
        Parse PDF file using State Surface reference.
        
        Args:
            request: FileParsingRequest with file_reference
        
        Returns:
            FileParsingResult with text content and structured data (tables)
        """
        try:
            # Get State Surface from request if not provided in __init__
            state_surface = request.state_surface or self.state_surface
            
            if not state_surface:
                return FileParsingResult(
                    success=False,
                    error="State Surface not available for file retrieval",
                    timestamp=datetime.utcnow().isoformat()
                )
            
            if not self.pdf_adapter:
                return FileParsingResult(
                    success=False,
                    error="PDF adapter not available",
                    timestamp=datetime.utcnow().isoformat()
                )
            
            # Retrieve file from State Surface
            file_data = await state_surface.get_file(request.file_reference)
            
            if not file_data:
                return FileParsingResult(
                    success=False,
                    error=f"File not found: {request.file_reference}",
                    timestamp=datetime.utcnow().isoformat()
                )
            
            # Parse using PDF adapter
            # Adapter should have parse_file(file_data: bytes, filename: str) method
            result = await self.pdf_adapter.parse_file(file_data, request.filename)
            
            if not result.get("success"):
                return FileParsingResult(
                    success=False,
                    error=result.get("error", "PDF parsing failed"),
                    timestamp=datetime.utcnow().isoformat()
                )
            
            # Convert to FileParsingResult
            return FileParsingResult(
                success=True,
                text_content=result.get("text", ""),
                structured_data={
                    "tables": result.get("tables", []),
                    "metadata": result.get("metadata", {})
                },
                metadata=result.get("metadata", {}),
                timestamp=datetime.utcnow().isoformat()
            )
        
        except Exception as e:
            self.logger.error(f"❌ PDF parsing failed: {e}", exc_info=True)
            return FileParsingResult(
                success=False,
                error=f"PDF parsing failed: {str(e)}",
                timestamp=datetime.utcnow().isoformat()
            )
