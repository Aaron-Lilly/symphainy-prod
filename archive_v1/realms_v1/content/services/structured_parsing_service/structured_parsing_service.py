"""
Structured Parsing Service

Service for parsing structured data files (Excel, CSV, JSON, Binary/Mainframe).
Uses State Surface for file retrieval (new architecture).

WHAT (Content Realm): I parse structured data files
HOW (Service): I coordinate parsing modules and abstractions
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from symphainy_platform.foundations.public_works.protocols.parsing_service_protocol import (
    ParsingRequest,
    ParsingResult,
    StructuredParsingProtocol
)

logger = logging.getLogger(__name__)


class StructuredParsingService(StructuredParsingProtocol):
    """
    Structured Parsing Service.
    
    Handles parsing of structured data files:
    - Excel (XLSX, XLS)
    - CSV
    - JSON
    - Binary/Mainframe (with copybook)
    """
    
    def __init__(
        self,
        state_surface: Any,
        platform_gateway: Optional[Any] = None
    ):
        """
        Initialize Structured Parsing Service.
        
        Args:
            state_surface: State Surface instance for file retrieval
            platform_gateway: Platform Gateway for accessing abstractions
        """
        self.state_surface = state_surface
        self.platform_gateway = platform_gateway
        self.logger = logger
        
        # Lazy import modules to avoid circular dependencies
        self._excel_parser = None
        self._csv_parser = None
        self._json_parser = None
        self._binary_parser = None
        
        self.logger.info("✅ Structured Parsing Service initialized")
    
    async def parse_structured_file(
        self,
        request: ParsingRequest
    ) -> ParsingResult:
        """
        Parse structured file.
        
        Routes to appropriate parser based on file type.
        
        Args:
            request: ParsingRequest with file_reference
        
        Returns:
            ParsingResult with structured data
        """
        try:
            # Get file metadata to determine type
            file_metadata = await self.state_surface.get_file_metadata(request.file_reference)
            
            if not file_metadata:
                return ParsingResult(
                    success=False,
                    error=f"File not found: {request.file_reference}",
                    timestamp=datetime.utcnow().isoformat()
                )
            
            filename = file_metadata.get("filename", request.filename)
            file_type = self._get_file_type(filename)
            
            # Route to appropriate parser
            if file_type in ["xlsx", "xls"]:
                return await self._parse_excel(request)
            elif file_type == "csv":
                return await self._parse_csv(request)
            elif file_type == "json":
                return await self._parse_json(request)
            elif file_type in ["bin", "binary"]:
                return await self._parse_binary(request)
            else:
                return ParsingResult(
                    success=False,
                    error=f"Unsupported structured file type: {file_type}",
                    timestamp=datetime.utcnow().isoformat()
                )
        
        except Exception as e:
            self.logger.error(f"❌ Structured parsing failed: {e}", exc_info=True)
            return ParsingResult(
                success=False,
                error=f"Structured parsing failed: {str(e)}",
                timestamp=datetime.utcnow().isoformat()
            )
    
    def _get_file_type(self, filename: str) -> str:
        """Get file type from filename."""
        if not filename:
            return "unknown"
        
        ext = filename.lower().split('.')[-1]
        return ext
    
    async def _parse_excel(self, request: ParsingRequest) -> ParsingResult:
        """Parse Excel file."""
        from .modules.excel_parser import ExcelParser
        
        if not self._excel_parser:
            self._excel_parser = ExcelParser(
                state_surface=self.state_surface,
                platform_gateway=self.platform_gateway
            )
        
        return await self._excel_parser.parse(request)
    
    async def _parse_csv(self, request: ParsingRequest) -> ParsingResult:
        """Parse CSV file."""
        from .modules.csv_parser import CSVParser
        
        if not self._csv_parser:
            self._csv_parser = CSVParser(
                state_surface=self.state_surface,
                platform_gateway=self.platform_gateway
            )
        
        return await self._csv_parser.parse(request)
    
    async def _parse_json(self, request: ParsingRequest) -> ParsingResult:
        """Parse JSON file."""
        from .modules.json_parser import JSONParser
        
        if not self._json_parser:
            self._json_parser = JSONParser(
                state_surface=self.state_surface,
                platform_gateway=self.platform_gateway
            )
        
        return await self._json_parser.parse(request)
    
    async def _parse_binary(self, request: ParsingRequest) -> ParsingResult:
        """Parse binary/mainframe file."""
        from .modules.binary_parser import BinaryParser
        
        if not self._binary_parser:
            self._binary_parser = BinaryParser(
                state_surface=self.state_surface,
                platform_gateway=self.platform_gateway
            )
        
        return await self._binary_parser.parse(request)
