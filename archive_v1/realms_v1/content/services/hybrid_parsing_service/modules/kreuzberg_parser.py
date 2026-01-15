"""
Kreuzberg Parser Module

Parses hybrid files using Kreuzberg (native hybrid support).
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from symphainy_platform.foundations.public_works.protocols.parsing_service_protocol import (
    ParsingRequest,
    ParsingResult
)
from symphainy_platform.foundations.public_works.protocols.file_parsing_protocol import (
    FileParsingRequest,
    FileParsingResult
)

logger = logging.getLogger(__name__)


class KreuzbergParser:
    """
    Kreuzberg Parser Module.
    
    Parses hybrid files using Kreuzberg Processing Abstraction.
    Kreuzberg natively extracts both structured (tables) and unstructured (text) in one pass.
    """
    
    def __init__(
        self,
        state_surface: Any,
        platform_gateway: Optional[Any] = None
    ):
        """
        Initialize Kreuzberg Parser.
        
        Args:
            state_surface: State Surface instance
            platform_gateway: Platform Gateway for accessing abstractions
        """
        self.state_surface = state_surface
        self.platform_gateway = platform_gateway
        self.logger = logger
    
    async def parse(self, request: ParsingRequest) -> ParsingResult:
        """
        Parse hybrid file using Kreuzberg.
        
        Args:
            request: ParsingRequest with file_reference
        
        Returns:
            ParsingResult with both structured (tables) and unstructured (text) data
        """
        try:
            # Get abstraction via Platform Gateway
            abstraction = await self._get_abstraction()
            
            if not abstraction:
                return ParsingResult(
                    success=False,
                    error="Kreuzberg Processing Abstraction not available",
                    timestamp=datetime.utcnow().isoformat()
                )
            
            # Create FileParsingRequest
            file_request = FileParsingRequest(
                file_reference=request.file_reference,
                filename=request.filename,
                options=request.options,
                state_surface=self.state_surface
            )
            
            # Parse file
            result: FileParsingResult = await abstraction.parse_file(file_request)
            
            # Convert to ParsingResult
            # Kreuzberg returns both structured (tables) and unstructured (text)
            structured_data = result.structured_data or {}
            text_content = result.text_content or ""
            
            return ParsingResult(
                success=result.success,
                data={
                    "structured": {
                        "tables": structured_data.get("tables", []),
                        "metadata": structured_data.get("metadata", {}),
                        "structure": structured_data.get("structure", {})
                    },
                    "unstructured": {
                        "text_chunks": text_content.split("\n\n") if text_content else []
                    },
                    "correlation": self._create_correlation_map(structured_data, text_content)
                },
                metadata=result.metadata,
                error=result.error,
                timestamp=result.timestamp
            )
        
        except Exception as e:
            self.logger.error(f"❌ Kreuzberg parsing failed: {e}", exc_info=True)
            return ParsingResult(
                success=False,
                error=f"Kreuzberg parsing failed: {str(e)}",
                timestamp=datetime.utcnow().isoformat()
            )
    
    def _create_correlation_map(
        self,
        structured_data: Dict[str, Any],
        text_content: str
    ) -> Dict[str, Any]:
        """
        Create correlation map between structured and unstructured content.
        
        Kreuzberg natively understands relationships, but we can enhance with metadata.
        """
        tables = structured_data.get("tables", [])
        structure = structured_data.get("structure", {})
        
        return {
            "table_count": len(tables),
            "text_length": len(text_content),
            "structure_metadata": structure,
            "note": "Kreuzberg natively maintains relationships between tables and text"
        }
    
    async def _get_abstraction(self) -> Optional[Any]:
        """Get Kreuzberg Processing Abstraction via Platform Gateway."""
        if not self.platform_gateway:
            self.logger.warning("Platform Gateway not available")
            return None
        
        try:
            abstraction = await self.platform_gateway.get_abstraction(
                "kreuzberg_processing_abstraction"
            )
            return abstraction
        except Exception as e:
            self.logger.error(f"Failed to get Kreuzberg abstraction: {e}")
            return None
