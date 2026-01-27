"""
Image Processing Abstraction - Layer 1

Lightweight coordination layer for image processing operations (OCR).
Uses State Surface for file retrieval.

WHAT (Infrastructure): I coordinate image processing operations
HOW (Abstraction): I provide lightweight coordination for OCR adapter
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from ..protocols.file_parsing_protocol import FileParsingRequest, FileParsingResult

logger = logging.getLogger(__name__)


class ImageProcessingAbstraction:
    """
    Image Processing Infrastructure Abstraction.
    
    Lightweight coordination layer for image processing operations (OCR).
    Uses State Surface for file retrieval (new architecture).
    """
    
    def __init__(
        self,
        ocr_adapter: Optional[Any] = None,  # Will be PyTesseractOCRAdapter or similar
        state_surface: Optional[Any] = None
    ):
        """
        Initialize Image Processing Abstraction.
        
        Args:
            ocr_adapter: OCR adapter (Layer 0)
            state_surface: State Surface instance for file retrieval
        """
        self.ocr_adapter = ocr_adapter
        self.state_surface = state_surface
        self.logger = logger
        
        self.logger.info("✅ Image Processing Abstraction initialized")
    
    async def parse_file(self, request: FileParsingRequest) -> FileParsingResult:
        """
        Parse image file (OCR) using State Surface reference.
        
        Args:
            request: FileParsingRequest with file_reference
        
        Returns:
            FileParsingResult with extracted text
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
            
            if not self.ocr_adapter:
                return FileParsingResult(
                    success=False,
                    error="OCR adapter not available",
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
            
            # Parse using OCR adapter
            result = await self.ocr_adapter.extract_text_from_bytes(file_data)
            
            if not result.get("success"):
                return FileParsingResult(
                    success=False,
                    error=result.get("error", "OCR parsing failed"),
                    timestamp=datetime.utcnow().isoformat()
                )
            
            # Convert to FileParsingResult
            return FileParsingResult(
                success=True,
                text_content=result.get("text", ""),
                metadata=result.get("metadata", {}),
                timestamp=datetime.utcnow().isoformat()
            )
        
        except Exception as e:
            self.logger.error(f"❌ Image parsing (OCR) failed: {e}", exc_info=True)
            return FileParsingResult(
                success=False,
                error=f"Image parsing failed: {str(e)}",
                timestamp=datetime.utcnow().isoformat()
            )
