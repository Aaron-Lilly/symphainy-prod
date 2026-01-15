"""
Text Parser Module

Parses text files directly.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from symphainy_platform.foundations.public_works.protocols.parsing_service_protocol import (
    ParsingRequest,
    ParsingResult
)

logger = logging.getLogger(__name__)


class TextParser:
    """
    Text Parser Module.
    
    Parses text files directly (no abstraction needed).
    """
    
    def __init__(
        self,
        state_surface: Any,
        platform_gateway: Optional[Any] = None
    ):
        """
        Initialize Text Parser.
        
        Args:
            state_surface: State Surface instance
            platform_gateway: Platform Gateway (not used for text)
        """
        self.state_surface = state_surface
        self.logger = logger
    
    async def parse(self, request: ParsingRequest) -> ParsingResult:
        """
        Parse text file.
        
        Args:
            request: ParsingRequest with file_reference
        
        Returns:
            ParsingResult with text chunks
        """
        try:
            # Retrieve file from State Surface
            file_data = await self.state_surface.get_file(request.file_reference)
            
            if not file_data:
                return ParsingResult(
                    success=False,
                    error=f"File not found: {request.file_reference}",
                    timestamp=datetime.utcnow().isoformat()
                )
            
            # Try UTF-8 first, then fallback to latin-1
            try:
                text_content = file_data.decode('utf-8')
            except UnicodeDecodeError:
                text_content = file_data.decode('latin-1')
            
            # Split into chunks (by paragraphs)
            text_chunks = [chunk.strip() for chunk in text_content.split("\n\n") if chunk.strip()]
            
            # Return result
            return ParsingResult(
                success=True,
                data={"text_chunks": text_chunks},
                metadata={
                    "type": "text",
                    "size": len(file_data),
                    "chunk_count": len(text_chunks)
                },
                timestamp=datetime.utcnow().isoformat()
            )
        
        except Exception as e:
            self.logger.error(f"❌ Text parsing failed: {e}", exc_info=True)
            return ParsingResult(
                success=False,
                error=f"Text parsing failed: {str(e)}",
                timestamp=datetime.utcnow().isoformat()
            )
