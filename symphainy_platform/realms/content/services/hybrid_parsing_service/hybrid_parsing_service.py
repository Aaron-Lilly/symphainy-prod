"""
Hybrid Parsing Service

Service for parsing hybrid files (structured + unstructured content).
Uses Kreuzberg as primary parser, with fallback to structured + unstructured.

WHAT (Content Realm): I parse hybrid files (tables + text)
HOW (Service): I use Kreuzberg for native hybrid extraction, fallback to dual parsing
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from symphainy_platform.foundations.public_works.protocols.parsing_service_protocol import (
    ParsingRequest,
    ParsingResult,
    HybridParsingProtocol
)

logger = logging.getLogger(__name__)


class HybridParsingService(HybridParsingProtocol):
    """
    Hybrid Parsing Service.
    
    Handles parsing of hybrid files (structured + unstructured):
    - PDFs with embedded tables
    - Word documents with tables and text
    - Excel files with text annotations
    - Scanned documents (OCR + table extraction)
    
    Uses Kreuzberg as primary parser (native hybrid support).
    Falls back to structured + unstructured parsing if Kreuzberg unavailable.
    """
    
    def __init__(
        self,
        state_surface: Any,
        platform_gateway: Optional[Any] = None,
        use_kreuzberg: bool = True
    ):
        """
        Initialize Hybrid Parsing Service.
        
        Args:
            state_surface: State Surface instance for file retrieval
            platform_gateway: Platform Gateway for accessing abstractions
            use_kreuzberg: Whether to use Kreuzberg (default: True)
        """
        self.state_surface = state_surface
        self.platform_gateway = platform_gateway
        self.use_kreuzberg = use_kreuzberg
        self.logger = logger
        
        # Lazy import modules
        self._kreuzberg_parser = None
        self._fallback_parser = None
        
        self.logger.info(f"✅ Hybrid Parsing Service initialized (Kreuzberg: {use_kreuzberg})")
    
    async def parse_hybrid_file(
        self,
        request: ParsingRequest
    ) -> ParsingResult:
        """
        Parse hybrid file.
        
        Tries Kreuzberg first (if enabled), then falls back to structured + unstructured.
        
        Args:
            request: ParsingRequest with file_reference
        
        Returns:
            ParsingResult with both structured and unstructured data
        """
        try:
            # Try Kreuzberg first (if enabled)
            if self.use_kreuzberg:
                try:
                    return await self._parse_with_kreuzberg(request)
                except Exception as e:
                    self.logger.warning(f"Kreuzberg parsing failed, falling back: {e}")
                    # Fall through to fallback
            
            # Fallback: Use structured + unstructured parsing
            return await self._parse_with_fallback(request)
        
        except Exception as e:
            self.logger.error(f"❌ Hybrid parsing failed: {e}", exc_info=True)
            return ParsingResult(
                success=False,
                error=f"Hybrid parsing failed: {str(e)}",
                timestamp=datetime.utcnow().isoformat()
            )
    
    async def _parse_with_kreuzberg(self, request: ParsingRequest) -> ParsingResult:
        """Parse using Kreuzberg (native hybrid support)."""
        from .modules.kreuzberg_parser import KreuzbergParser
        
        if not self._kreuzberg_parser:
            self._kreuzberg_parser = KreuzbergParser(
                state_surface=self.state_surface,
                platform_gateway=self.platform_gateway
            )
        
        return await self._kreuzberg_parser.parse(request)
    
    async def _parse_with_fallback(self, request: ParsingRequest) -> ParsingResult:
        """Parse using structured + unstructured parsing (fallback)."""
        from .modules.fallback_parser import FallbackParser
        
        if not self._fallback_parser:
            self._fallback_parser = FallbackParser(
                state_surface=self.state_surface,
                platform_gateway=self.platform_gateway
            )
        
        return await self._fallback_parser.parse(request)
