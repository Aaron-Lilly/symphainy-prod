"""
JSON Processing Abstraction - Layer 1

Lightweight coordination layer for JSON processing operations.
Uses State Surface for file retrieval.

WHAT (Infrastructure): I coordinate JSON processing operations
HOW (Abstraction): I provide lightweight coordination for JSON adapter
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from ..protocols.file_parsing_protocol import FileParsingRequest, FileParsingResult

logger = logging.getLogger(__name__)


class JsonProcessingAbstraction:
    """
    JSON Processing Infrastructure Abstraction.
    
    Lightweight coordination layer for JSON processing operations.
    Uses State Surface for file retrieval (new architecture).
    """
    
    def __init__(
        self,
        json_adapter: Optional[Any] = None,  # Will be JsonProcessingAdapter
        state_surface: Optional[Any] = None
    ):
        """
        Initialize JSON Processing Abstraction.
        
        Args:
            json_adapter: JSON adapter (Layer 0)
            state_surface: State Surface instance for file retrieval
        """
        self.json_adapter = json_adapter
        self.state_surface = state_surface
        self.logger = logger
        
        self.logger.info("✅ JSON Processing Abstraction initialized")
    
    async def parse_file(self, request: FileParsingRequest) -> FileParsingResult:
        """
        Parse JSON file using State Surface reference.
        
        Args:
            request: FileParsingRequest with file_reference
        
        Returns:
            FileParsingResult with structured data (JSON object/array)
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
            
            if not self.json_adapter:
                return FileParsingResult(
                    success=False,
                    error="JSON adapter not available",
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
            
            # Parse using JSON adapter
            result = await self.json_adapter.parse_file(file_data, request.filename)
            
            if not result.get("success"):
                return FileParsingResult(
                    success=False,
                    error=result.get("error", "JSON parsing failed"),
                    timestamp=datetime.utcnow().isoformat()
                )
            
            # Convert to FileParsingResult
            return FileParsingResult(
                success=True,
                structured_data={
                    "json": result.get("data", {}),
                    "metadata": result.get("metadata", {})
                },
                metadata=result.get("metadata", {}),
                timestamp=datetime.utcnow().isoformat()
            )
        
        except Exception as e:
            self.logger.error(f"❌ JSON parsing failed: {e}", exc_info=True)
            return FileParsingResult(
                success=False,
                error=f"JSON parsing failed: {str(e)}",
                timestamp=datetime.utcnow().isoformat()
            )
