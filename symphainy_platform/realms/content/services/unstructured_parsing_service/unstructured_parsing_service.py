"""
Unstructured Parsing Service

Service for parsing unstructured data files (PDF, Word, Text, Image).
Uses State Surface for file retrieval (new architecture).

WHAT (Content Realm): I parse unstructured data files
HOW (Service): I coordinate parsing modules and abstractions
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from symphainy_platform.foundations.public_works.protocols.parsing_service_protocol import (
    ParsingRequest,
    ParsingResult,
    UnstructuredParsingProtocol
)

logger = logging.getLogger(__name__)


class UnstructuredParsingService(UnstructuredParsingProtocol):
    """
    Unstructured Parsing Service.
    
    Handles parsing of unstructured data files:
    - PDF
    - Word (DOCX, DOC)
    - Text (TXT)
    - Image (PNG, JPG, etc.) - OCR
    """
    
    def __init__(
        self,
        state_surface: Any,
        platform_gateway: Optional[Any] = None
    ):
        """
        Initialize Unstructured Parsing Service.
        
        Args:
            state_surface: State Surface instance for file retrieval
            platform_gateway: Platform Gateway for accessing abstractions
        """
        self.state_surface = state_surface
        self.platform_gateway = platform_gateway
        self.logger = logger
        
        # Lazy import modules to avoid circular dependencies
        self._pdf_parser = None
        self._word_parser = None
        self._text_parser = None
        self._image_parser = None
        
        self.logger.info("✅ Unstructured Parsing Service initialized")
    
    async def parse_unstructured_file(
        self,
        request: ParsingRequest
    ) -> ParsingResult:
        """
        Parse unstructured file.
        
        Routes to appropriate parser based on file type.
        
        Args:
            request: ParsingRequest with file_reference
        
        Returns:
            ParsingResult with text chunks for semantic processing
        """
        try:
            # Get file metadata to determine type
            file_metadata = await self.state_surface.get_file_metadata(request.file_reference)
            
            if not file_metadata:
                return ParsingResult(
                    success=False,
                    error=f"File not found: {request.file_reference}",
                    timestamp=datetime.utcnow().isoformat()
                )
            
            filename = file_metadata.get("filename", request.filename)
            file_type = self._get_file_type(filename)
            
            # Route to appropriate parser
            if file_type == "pdf":
                return await self._parse_pdf(request)
            elif file_type in ["docx", "doc"]:
                return await self._parse_word(request)
            elif file_type == "txt":
                return await self._parse_text(request)
            elif file_type in ["png", "jpg", "jpeg", "gif", "bmp", "tiff"]:
                return await self._parse_image(request)
            else:
                return ParsingResult(
                    success=False,
                    error=f"Unsupported unstructured file type: {file_type}",
                    timestamp=datetime.utcnow().isoformat()
                )
        
        except Exception as e:
            self.logger.error(f"❌ Unstructured parsing failed: {e}", exc_info=True)
            return ParsingResult(
                success=False,
                error=f"Unstructured parsing failed: {str(e)}",
                timestamp=datetime.utcnow().isoformat()
            )
    
    def _get_file_type(self, filename: str) -> str:
        """Get file type from filename."""
        if not filename:
            return "unknown"
        
        ext = filename.lower().split('.')[-1]
        return ext
    
    async def _parse_pdf(self, request: ParsingRequest) -> ParsingResult:
        """Parse PDF file."""
        from .modules.pdf_parser import PDFParser
        
        if not self._pdf_parser:
            self._pdf_parser = PDFParser(
                state_surface=self.state_surface,
                platform_gateway=self.platform_gateway
            )
        
        return await self._pdf_parser.parse(request)
    
    async def _parse_word(self, request: ParsingRequest) -> ParsingResult:
        """Parse Word file."""
        from .modules.word_parser import WordParser
        
        if not self._word_parser:
            self._word_parser = WordParser(
                state_surface=self.state_surface,
                platform_gateway=self.platform_gateway
            )
        
        return await self._word_parser.parse(request)
    
    async def _parse_text(self, request: ParsingRequest) -> ParsingResult:
        """Parse text file."""
        from .modules.text_parser import TextParser
        
        if not self._text_parser:
            self._text_parser = TextParser(
                state_surface=self.state_surface,
                platform_gateway=self.platform_gateway
            )
        
        return await self._text_parser.parse(request)
    
    async def _parse_image(self, request: ParsingRequest) -> ParsingResult:
        """Parse image file (OCR)."""
        from .modules.image_parser import ImageParser
        
        if not self._image_parser:
            self._image_parser = ImageParser(
                state_surface=self.state_surface,
                platform_gateway=self.platform_gateway
            )
        
        return await self._image_parser.parse(request)
