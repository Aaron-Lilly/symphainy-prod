"""
JSON Parser Module

Parses JSON files.
"""

import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from symphainy_platform.foundations.public_works.protocols.parsing_service_protocol import (
    ParsingRequest,
    ParsingResult
)

logger = logging.getLogger(__name__)


class JSONParser:
    """
    JSON Parser Module.
    
    Parses JSON files directly (no abstraction needed for simple JSON).
    """
    
    def __init__(
        self,
        state_surface: Any,
        platform_gateway: Optional[Any] = None
    ):
        """
        Initialize JSON Parser.
        
        Args:
            state_surface: State Surface instance
            platform_gateway: Platform Gateway (not used for JSON)
        """
        self.state_surface = state_surface
        self.logger = logger
    
    async def parse(self, request: ParsingRequest) -> ParsingResult:
        """
        Parse JSON file.
        
        Args:
            request: ParsingRequest with file_reference
        
        Returns:
            ParsingResult with structured data (JSON object/array)
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
            
            # Parse JSON
            try:
                json_data = json.loads(file_data.decode('utf-8'))
            except UnicodeDecodeError:
                # Try other encodings
                json_data = json.loads(file_data.decode('latin-1'))
            
            # Return result
            return ParsingResult(
                success=True,
                data={"json": json_data},
                metadata={
                    "type": "json",
                    "size": len(file_data)
                },
                timestamp=datetime.utcnow().isoformat()
            )
        
        except json.JSONDecodeError as e:
            self.logger.error(f"❌ JSON parsing failed: {e}")
            return ParsingResult(
                success=False,
                error=f"Invalid JSON: {str(e)}",
                timestamp=datetime.utcnow().isoformat()
            )
        except Exception as e:
            self.logger.error(f"❌ JSON parsing failed: {e}", exc_info=True)
            return ParsingResult(
                success=False,
                error=f"JSON parsing failed: {str(e)}",
                timestamp=datetime.utcnow().isoformat()
            )
