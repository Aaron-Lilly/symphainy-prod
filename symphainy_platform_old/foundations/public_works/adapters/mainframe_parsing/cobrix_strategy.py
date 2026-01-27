"""
Cobrix Mainframe Parsing Strategy

Industry-standard Cobrix implementation (gold standard, simplified).
Uses Cobrix service via HTTP API.

WHAT (Infrastructure): I parse mainframe files using Cobrix (industry standard)
HOW (Strategy): I use Cobrix service with minimal preprocessing
"""

import logging
import tempfile
import os
from typing import Dict, Any, Optional
from datetime import datetime
import httpx

from symphainy_platform.foundations.public_works.protocols.file_parsing_protocol import (
    FileParsingResult
)
from symphainy_platform.foundations.public_works.adapters.file_parsing.copybook_preprocessing import (
    CopybookPreprocessor
)
from .base import MainframeParsingStrategy

logger = logging.getLogger(__name__)


class CobrixMainframeStrategy:
    """
    Cobrix Mainframe Parsing Strategy.
    
    Industry-standard implementation using Cobrix service.
    Gold standard approach: Minimal preprocessing, trust Cobrix capabilities.
    """
    
    def __init__(
        self,
        state_surface: Any,
        cobrix_service_url: str = "http://localhost:8080"
    ):
        """
        Initialize Cobrix Mainframe Strategy.
        
        Args:
            state_surface: State Surface instance for file retrieval
            cobrix_service_url: Cobrix service URL
        """
        self.state_surface = state_surface
        self.cobrix_service_url = cobrix_service_url.rstrip('/')
        self.logger = logger
        self.preprocessor = CopybookPreprocessor()
        
        self.logger.info(f"✅ Cobrix Mainframe Strategy initialized (service: {cobrix_service_url})")
    
    async def parse_file(
        self,
        file_reference: str,
        copybook_reference: str,
        options: Dict[str, Any]
    ) -> FileParsingResult:
        """
        Parse mainframe file using Cobrix (gold standard approach).
        
        Steps:
        1. Extract 88-level metadata BEFORE cleaning (CRITICAL for insights pillar)
        2. Clean copybook (minimal - trust Cobrix capabilities)
        3. Normalize file (calculate offsets)
        4. Call Cobrix service
        5. Return result with validation_rules
        
        Args:
            file_reference: State Surface reference to binary file
            copybook_reference: State Surface reference to copybook file
            options: Parsing options (encoding, record_format, etc.)
        
        Returns:
            FileParsingResult with parsed records and validation_rules
        """
        try:
            # Retrieve files from State Surface
            file_data = await self.state_surface.get_file(file_reference)
            copybook_data = await self.state_surface.get_file(copybook_reference)
            
            if not file_data:
                return FileParsingResult(
                    success=False,
                    error=f"File not found: {file_reference}",
                    timestamp=datetime.utcnow().isoformat()
                )
            
            if not copybook_data:
                return FileParsingResult(
                    success=False,
                    error=f"Copybook not found: {copybook_reference}",
                    timestamp=datetime.utcnow().isoformat()
                )
            
            # Decode copybook
            copybook_content = copybook_data.decode('utf-8')
            
            # Step 1: Extract 88-level metadata BEFORE cleaning (CRITICAL)
            validation_rules = self.preprocessor.extract_88_level_metadata(copybook_content)
            
            # Step 2: Clean copybook (minimal preprocessing)
            cleaned_copybook = self.preprocessor.clean_copybook_for_cobrix(copybook_content)
            
            # Step 3: Normalize file (calculate offsets)
            encoding = options.get("encoding", "EBCDIC")
            record_size = options.get("record_size")
            normalized_file, file_start_offset, file_trailer_length = self.preprocessor.normalize_file_for_cobrix(
                file_data,
                record_size
            )
            
            # Step 4: Call Cobrix service
            result = await self._call_cobrix_service(
                normalized_file,
                cleaned_copybook,
                encoding,
                file_start_offset,
                file_trailer_length
            )
            
            if not result.get("success"):
                return FileParsingResult(
                    success=False,
                    error=result.get("error", "Cobrix parsing failed"),
                    validation_rules=validation_rules,
                    timestamp=datetime.utcnow().isoformat()
                )
            
            # Step 5: Return result with validation_rules
            return FileParsingResult(
                success=True,
                structured_data={
                    "records": result.get("records", []),
                    "tables": result.get("tables", [])
                },
                metadata=result.get("metadata", {}),
                validation_rules=validation_rules,  # For insights pillar
                timestamp=datetime.utcnow().isoformat()
            )
        
        except Exception as e:
            self.logger.error(f"❌ Cobrix mainframe parsing failed: {e}", exc_info=True)
            return FileParsingResult(
                success=False,
                error=f"Cobrix mainframe parsing failed: {str(e)}",
                timestamp=datetime.utcnow().isoformat()
            )
    
    async def _call_cobrix_service(
        self,
        file_data: bytes,
        copybook_content: str,
        encoding: str,
        file_start_offset: int,
        file_trailer_length: int
    ) -> Dict[str, Any]:
        """
        Call Cobrix service via HTTP API.
        
        Args:
            file_data: Normalized file data
            copybook_content: Cleaned copybook content
            encoding: File encoding (EBCDIC or ASCII)
            file_start_offset: Header offset
            file_trailer_length: Trailer length
        
        Returns:
            Dict with parsed records
        """
        try:
            # Create temporary files (Cobrix service requires file paths)
            with tempfile.NamedTemporaryFile(delete=False, suffix='.bin') as file_tmp:
                file_tmp.write(file_data)
                file_path = file_tmp.name
            
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.cpy') as copybook_tmp:
                copybook_tmp.write(copybook_content)
                copybook_path = copybook_tmp.name
            
            try:
                # Call Cobrix service
                async with httpx.AsyncClient(timeout=300.0) as client:
                    files = {
                        'file': (os.path.basename(file_path), open(file_path, 'rb'), 'application/octet-stream'),
                        'copybook': (os.path.basename(copybook_path), open(copybook_path, 'r'), 'text/plain')
                    }
                    data = {
                        'encoding': encoding,
                        'file_start_offset': str(file_start_offset),
                        'file_trailer_length': str(file_trailer_length),
                        'record_format': 'F'  # Fixed-length records
                    }
                    
                    response = await client.post(
                        f"{self.cobrix_service_url}/parse/cobol",
                        files=files,
                        data=data
                    )
                    response.raise_for_status()
                    
                    result = response.json()
                    
                    return {
                        "success": True,
                        "records": result.get("records", []),
                        "tables": result.get("tables", []),
                        "metadata": result.get("metadata", {})
                    }
            
            finally:
                # Clean up temporary files
                try:
                    os.unlink(file_path)
                    os.unlink(copybook_path)
                except Exception as e:
                    self.logger.warning(f"Failed to clean up temp files: {e}")
        
        except httpx.HTTPError as e:
            self.logger.error(f"❌ Cobrix service error: {e}")
            return {
                "success": False,
                "error": f"Cobrix service failed: {str(e)}"
            }
        except Exception as e:
            self.logger.error(f"❌ Cobrix parsing error: {e}")
            return {
                "success": False,
                "error": f"Cobrix parsing failed: {str(e)}"
            }
    
    def supports_feature(self, feature: str) -> bool:
        """
        Check if Cobrix strategy supports a COBOL feature.
        
        Args:
            feature: Feature name
        
        Returns:
            True if feature is supported
        """
        # Cobrix supports most COBOL features natively
        supported_features = {
            "OCCURS": True,
            "REDEFINES": True,
            "COMP-3": True,
            "BINARY": True,
            "88-level": False,  # Extracted separately (not in copybook)
            "VALUE": False,  # Extracted separately (not in copybook)
            "large_files": True,  # Spark-based, handles large files
            "parallel": True  # Spark-based, parallel processing
        }
        
        return supported_features.get(feature, False)
