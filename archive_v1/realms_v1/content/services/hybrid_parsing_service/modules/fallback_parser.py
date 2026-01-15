"""
Fallback Parser Module

Parses hybrid files using structured + unstructured parsing (fallback approach).
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from symphainy_platform.foundations.public_works.protocols.parsing_service_protocol import (
    ParsingRequest,
    ParsingResult
)

logger = logging.getLogger(__name__)


class FallbackParser:
    """
    Fallback Parser Module.
    
    Parses hybrid files by calling both structured and unstructured parsing services,
    then creating a correlation map.
    """
    
    def __init__(
        self,
        state_surface: Any,
        platform_gateway: Optional[Any] = None
    ):
        """
        Initialize Fallback Parser.
        
        Args:
            state_surface: State Surface instance
            platform_gateway: Platform Gateway for accessing services
        """
        self.state_surface = state_surface
        self.platform_gateway = platform_gateway
        self.logger = logger
    
    async def parse(self, request: ParsingRequest) -> ParsingResult:
        """
        Parse hybrid file using structured + unstructured parsing.
        
        Args:
            request: ParsingRequest with file_reference
        
        Returns:
            ParsingResult with both structured and unstructured data + correlation map
        """
        try:
            # Get services via Platform Gateway
            structured_service = await self._get_structured_service()
            unstructured_service = await self._get_unstructured_service()
            
            if not structured_service or not unstructured_service:
                return ParsingResult(
                    success=False,
                    error="Structured or Unstructured Parsing Service not available",
                    timestamp=datetime.utcnow().isoformat()
                )
            
            # Parse with both services in parallel
            structured_result = await structured_service.parse_structured_file(request)
            unstructured_result = await unstructured_service.parse_unstructured_file(request)
            
            # Check if both succeeded
            if not structured_result.success and not unstructured_result.success:
                return ParsingResult(
                    success=False,
                    error=f"Both parsing failed: structured={structured_result.error}, unstructured={unstructured_result.error}",
                    timestamp=datetime.utcnow().isoformat()
                )
            
            # Create correlation map
            correlation_map = self._create_correlation_map(
                structured_result.data,
                unstructured_result.data
            )
            
            # Return combined result
            return ParsingResult(
                success=True,
                data={
                    "structured": structured_result.data,
                    "unstructured": unstructured_result.data,
                    "correlation": correlation_map
                },
                metadata={
                    "structured_metadata": structured_result.metadata,
                    "unstructured_metadata": unstructured_result.metadata
                },
                timestamp=datetime.utcnow().isoformat()
            )
        
        except Exception as e:
            self.logger.error(f"❌ Fallback parsing failed: {e}", exc_info=True)
            return ParsingResult(
                success=False,
                error=f"Fallback parsing failed: {str(e)}",
                timestamp=datetime.utcnow().isoformat()
            )
    
    def _create_correlation_map(
        self,
        structured_data: Optional[Dict[str, Any]],
        unstructured_data: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create correlation map between structured and unstructured content.
        
        This is a simple correlation - Kreuzberg provides better native correlation.
        """
        return {
            "note": "Fallback correlation - basic mapping between structured and unstructured content",
            "structured_keys": list(structured_data.keys()) if structured_data else [],
            "unstructured_keys": list(unstructured_data.keys()) if unstructured_data else [],
            "recommendation": "Use Kreuzberg for better native correlation"
        }
    
    async def _get_structured_service(self) -> Optional[Any]:
        """Get Structured Parsing Service via Platform Gateway."""
        if not self.platform_gateway:
            return None
        
        try:
            # Get service by name (to be configured in Platform Gateway)
            service = await self.platform_gateway.get_service(
                "structured_parsing_service"
            )
            return service
        except Exception as e:
            self.logger.error(f"Failed to get Structured Parsing Service: {e}")
            return None
    
    async def _get_unstructured_service(self) -> Optional[Any]:
        """Get Unstructured Parsing Service via Platform Gateway."""
        if not self.platform_gateway:
            return None
        
        try:
            service = await self.platform_gateway.get_service(
                "unstructured_parsing_service"
            )
            return service
        except Exception as e:
            self.logger.error(f"Failed to get Unstructured Parsing Service: {e}")
            return None
