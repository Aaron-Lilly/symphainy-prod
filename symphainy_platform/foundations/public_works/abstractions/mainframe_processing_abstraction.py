"""
Mainframe Processing Abstraction - Layer 1

Lightweight coordination layer for mainframe processing operations.
Uses State Surface for file retrieval.

WHAT (Infrastructure): I coordinate mainframe processing operations
HOW (Abstraction): I provide lightweight coordination for mainframe adapter
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from ..adapters.mainframe_parsing.unified_adapter import MainframeProcessingAdapter
from ..protocols.file_parsing_protocol import FileParsingRequest, FileParsingResult

logger = logging.getLogger(__name__)


class MainframeProcessingAbstraction:
    """
    Mainframe Processing Infrastructure Abstraction.
    
    Lightweight coordination layer for mainframe processing operations.
    Uses State Surface for file retrieval (new architecture).
    Implements FileParsingProtocol.
    """
    
    def __init__(
        self,
        mainframe_adapter: MainframeProcessingAdapter,
        state_surface: Optional[Any] = None
    ):
        """
        Initialize Mainframe Processing Abstraction.
        
        Args:
            mainframe_adapter: Mainframe processing adapter (Layer 0)
            state_surface: State Surface instance for file retrieval
        """
        self.mainframe_adapter = mainframe_adapter
        self.state_surface = state_surface
        self.logger = logger
        
        self.logger.info("✅ Mainframe Processing Abstraction initialized")
    
    async def parse_file(self, request: FileParsingRequest) -> FileParsingResult:
        """
        Parse mainframe file using State Surface references.
        
        Args:
            request: FileParsingRequest with file_reference and copybook_reference
        
        Returns:
            FileParsingResult with parsed records and validation_rules
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
            
            # Validate copybook_reference is provided
            if not request.copybook_reference:
                return FileParsingResult(
                    success=False,
                    error="copybook_reference required for mainframe parsing",
                    timestamp=datetime.utcnow().isoformat()
                )
            
            # Parse using unified adapter
            result = await self.mainframe_adapter.parse_file(
                file_reference=request.file_reference,
                copybook_reference=request.copybook_reference,
                options=request.options or {}
            )
            
            return result
        
        except Exception as e:
            self.logger.error(f"❌ Mainframe parsing failed: {e}", exc_info=True)
            return FileParsingResult(
                success=False,
                error=f"Mainframe parsing failed: {str(e)}",
                timestamp=datetime.utcnow().isoformat()
            )
