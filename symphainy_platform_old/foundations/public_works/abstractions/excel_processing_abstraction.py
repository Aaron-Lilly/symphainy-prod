"""
Excel Processing Abstraction - Layer 1

Lightweight coordination layer for Excel processing operations.
Uses State Surface for file retrieval.

WHAT (Infrastructure): I coordinate Excel processing operations
HOW (Abstraction): I provide lightweight coordination for Excel adapter
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from ..protocols.file_parsing_protocol import FileParsingRequest, FileParsingResult

logger = logging.getLogger(__name__)


class ExcelProcessingAbstraction:
    """
    Excel Processing Infrastructure Abstraction.
    
    Lightweight coordination layer for Excel processing operations.
    Uses State Surface for file retrieval (new architecture).
    """
    
    def __init__(
        self,
        excel_adapter: Optional[Any] = None,  # Will be ExcelProcessingAdapter
        state_surface: Optional[Any] = None
    ):
        """
        Initialize Excel Processing Abstraction.
        
        Args:
            excel_adapter: Excel adapter (Layer 0)
            state_surface: State Surface instance for file retrieval
        """
        self.excel_adapter = excel_adapter
        self.state_surface = state_surface
        self.logger = logger
        
        self.logger.info("✅ Excel Processing Abstraction initialized")
    
    async def parse_file(self, request: FileParsingRequest) -> FileParsingResult:
        """
        Parse Excel file using State Surface reference.
        
        Args:
            request: FileParsingRequest with file_reference
        
        Returns:
            FileParsingResult with structured data (tables, sheets)
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
            
            if not self.excel_adapter:
                return FileParsingResult(
                    success=False,
                    error="Excel adapter not available",
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
            
            # Parse using Excel adapter
            result = await self.excel_adapter.parse_file(file_data, request.filename)
            
            if not result.get("success"):
                return FileParsingResult(
                    success=False,
                    error=result.get("error", "Excel parsing failed"),
                    timestamp=datetime.utcnow().isoformat()
                )
            
            # Convert to FileParsingResult
            return FileParsingResult(
                success=True,
                structured_data={
                    "sheets": result.get("sheets", []),
                    "tables": result.get("tables", []),
                    "metadata": result.get("metadata", {})
                },
                metadata=result.get("metadata", {}),
                timestamp=datetime.utcnow().isoformat()
            )
        
        except Exception as e:
            self.logger.error(f"❌ Excel parsing failed: {e}", exc_info=True)
            return FileParsingResult(
                success=False,
                error=f"Excel parsing failed: {str(e)}",
                timestamp=datetime.utcnow().isoformat()
            )
