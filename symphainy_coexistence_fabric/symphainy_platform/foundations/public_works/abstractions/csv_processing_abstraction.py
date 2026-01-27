"""
CSV Processing Abstraction - Layer 1

Lightweight coordination layer for CSV processing operations.
Uses State Surface for file retrieval.

WHAT (Infrastructure): I coordinate CSV processing operations
HOW (Abstraction): I provide lightweight coordination for CSV adapter
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from ..protocols.file_parsing_protocol import FileParsingRequest, FileParsingResult

logger = logging.getLogger(__name__)


class CsvProcessingAbstraction:
    """
    CSV Processing Infrastructure Abstraction.
    
    Lightweight coordination layer for CSV processing operations.
    Uses State Surface for file retrieval (new architecture).
    """
    
    def __init__(
        self,
        csv_adapter: Optional[Any] = None,  # Will be CsvProcessingAdapter
        state_surface: Optional[Any] = None
    ):
        """
        Initialize CSV Processing Abstraction.
        
        Args:
            csv_adapter: CSV adapter (Layer 0)
            state_surface: State Surface instance for file retrieval
        """
        self.csv_adapter = csv_adapter
        self.state_surface = state_surface
        self.logger = logger
        
        self.logger.info("✅ CSV Processing Abstraction initialized")
    
    async def parse_file(self, request: FileParsingRequest) -> FileParsingResult:
        """
        Parse CSV file using State Surface reference.
        
        Args:
            request: FileParsingRequest with file_reference
        
        Returns:
            FileParsingResult with structured data (rows)
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
            
            # Retrieve file from State Surface
            file_data = await state_surface.get_file(request.file_reference)
            
            if not file_data:
                return FileParsingResult(
                    success=False,
                    error=f"File not found: {request.file_reference}",
                    timestamp=datetime.utcnow().isoformat()
                )
            
            # CSV adapter is REQUIRED - fail fast if missing
            if not self.csv_adapter:
                return FileParsingResult(
                    success=False,
                    error="CSV adapter is required for CSV parsing. Please ensure CsvProcessingAdapter is initialized in Public Works Foundation.",
                    timestamp=datetime.utcnow().isoformat()
                )
            
            # Parse using CSV adapter
            result = await self.csv_adapter.parse_file(file_data, request.filename)
            
            if not result.get("success"):
                return FileParsingResult(
                    success=False,
                    error=result.get("error", "CSV parsing failed"),
                    timestamp=datetime.utcnow().isoformat()
                )
            
            # Convert to FileParsingResult
            return FileParsingResult(
                success=True,
                structured_data={
                    "rows": result.get("rows", []),
                    "columns": result.get("columns", []),
                    "metadata": result.get("metadata", {})
                },
                metadata=result.get("metadata", {}),
                timestamp=datetime.utcnow().isoformat()
            )
        
        except Exception as e:
            self.logger.error(f"❌ CSV parsing failed: {e}", exc_info=True)
            return FileParsingResult(
                success=False,
                error=f"CSV parsing failed: {str(e)}",
                timestamp=datetime.utcnow().isoformat()
            )
