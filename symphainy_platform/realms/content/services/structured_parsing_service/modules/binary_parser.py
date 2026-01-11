"""
Binary Parser Module

Parses binary/mainframe files using Mainframe Processing Abstraction.
Supports both custom and Cobrix strategies.
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


class BinaryParser:
    """
    Binary Parser Module.
    
    Parses binary/mainframe files using Mainframe Processing Abstraction.
    Supports both custom and Cobrix strategies (via unified adapter).
    """
    
    def __init__(
        self,
        state_surface: Any,
        platform_gateway: Optional[Any] = None
    ):
        """
        Initialize Binary Parser.
        
        Args:
            state_surface: State Surface instance
            platform_gateway: Platform Gateway for accessing abstractions
        """
        self.state_surface = state_surface
        self.platform_gateway = platform_gateway
        self.logger = logger
    
    async def parse(self, request: ParsingRequest) -> ParsingResult:
        """
        Parse binary/mainframe file.
        
        Requires copybook_reference in options for mainframe files.
        
        Args:
            request: ParsingRequest with file_reference and copybook_reference in options
        
        Returns:
            ParsingResult with structured data (records) and validation_rules (88-level fields)
        """
        try:
            # Validate copybook is provided
            options = request.options or {}
            copybook_reference = options.get("copybook_reference")
            
            if not copybook_reference:
                return ParsingResult(
                    success=False,
                    error="copybook_reference required in options for binary/mainframe files",
                    timestamp=datetime.utcnow().isoformat()
                )
            
            # Get abstraction via Platform Gateway
            abstraction = await self._get_abstraction()
            
            if not abstraction:
                return ParsingResult(
                    success=False,
                    error="Mainframe Processing Abstraction not available",
                    timestamp=datetime.utcnow().isoformat()
                )
            
            # Create FileParsingRequest
            file_request = FileParsingRequest(
                file_reference=request.file_reference,
                copybook_reference=copybook_reference,
                filename=request.filename,
                options=options,
                state_surface=self.state_surface
            )
            
            # Parse file
            result: FileParsingResult = await abstraction.parse_file(file_request)
            
            # Convert to ParsingResult
            return ParsingResult(
                success=result.success,
                data=result.structured_data,
                metadata=result.metadata,
                validation_rules=result.validation_rules,  # 88-level fields for insights pillar
                error=result.error,
                timestamp=result.timestamp
            )
        
        except Exception as e:
            self.logger.error(f"❌ Binary parsing failed: {e}", exc_info=True)
            return ParsingResult(
                success=False,
                error=f"Binary parsing failed: {str(e)}",
                timestamp=datetime.utcnow().isoformat()
            )
    
    async def _get_abstraction(self) -> Optional[Any]:
        """Get Mainframe Processing Abstraction via Platform Gateway."""
        if not self.platform_gateway:
            self.logger.warning("Platform Gateway not available")
            return None
        
        try:
            # Get abstraction by name (to be configured in Platform Gateway)
            abstraction = await self.platform_gateway.get_abstraction(
                "mainframe_processing_abstraction"
            )
            return abstraction
        except Exception as e:
            self.logger.error(f"Failed to get Mainframe abstraction: {e}")
            return None
