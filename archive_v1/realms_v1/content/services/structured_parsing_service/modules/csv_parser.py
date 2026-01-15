"""
CSV Parser Module

Parses CSV files using appropriate abstraction.
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


class CSVParser:
    """
    CSV Parser Module.
    
    Parses CSV files using CSV Processing Abstraction.
    """
    
    def __init__(
        self,
        state_surface: Any,
        platform_gateway: Optional[Any] = None
    ):
        """
        Initialize CSV Parser.
        
        Args:
            state_surface: State Surface instance
            platform_gateway: Platform Gateway for accessing abstractions
        """
        self.state_surface = state_surface
        self.platform_gateway = platform_gateway
        self.logger = logger
    
    async def parse(self, request: ParsingRequest) -> ParsingResult:
        """
        Parse CSV file.
        
        Args:
            request: ParsingRequest with file_reference
        
        Returns:
            ParsingResult with structured data (rows)
        """
        try:
            # Get abstraction via Platform Gateway
            abstraction = await self._get_abstraction()
            
            if not abstraction:
                return ParsingResult(
                    success=False,
                    error="CSV Processing Abstraction not available",
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
            return ParsingResult(
                success=result.success,
                data=result.structured_data,
                metadata=result.metadata,
                error=result.error,
                timestamp=result.timestamp
            )
        
        except Exception as e:
            self.logger.error(f"❌ CSV parsing failed: {e}", exc_info=True)
            return ParsingResult(
                success=False,
                error=f"CSV parsing failed: {str(e)}",
                timestamp=datetime.utcnow().isoformat()
            )
    
    async def _get_abstraction(self) -> Optional[Any]:
        """Get CSV Processing Abstraction via Platform Gateway."""
        if not self.platform_gateway:
            self.logger.warning("Platform Gateway not available")
            return None
        
        try:
            abstraction = await self.platform_gateway.get_abstraction(
                "csv_processing_abstraction"
            )
            return abstraction
        except Exception as e:
            self.logger.error(f"Failed to get CSV abstraction: {e}")
            return None
