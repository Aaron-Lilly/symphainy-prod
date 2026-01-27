"""
CSV Processing Adapter - Layer 0

Raw technology client for CSV file parsing.
Uses Python's csv module for parsing.

WHAT (Infrastructure): I provide CSV parsing capabilities
HOW (Adapter): I use Python's csv module to parse CSV files
"""

import logging
import csv
import io
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class CsvProcessingAdapter:
    """
    Adapter for CSV file parsing.
    
    Uses Python's built-in csv module for parsing.
    """
    
    def __init__(self):
        """Initialize CSV Processing Adapter."""
        self.logger = logger
        self.logger.info("✅ CSV Processing Adapter initialized")
    
    async def parse_file(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """
        Parse CSV file from bytes.
        
        Args:
            file_data: CSV file content as bytes
            filename: Original filename (for logging)
        
        Returns:
            Dict with parsed data:
            {
                "success": bool,
                "rows": List[Dict],  # List of row dictionaries
                "columns": List[str],  # Column names
                "metadata": Dict,
                "error": Optional[str]
            }
        """
        try:
            # Try UTF-8 first, then fallback to latin-1
            try:
                text_content = file_data.decode('utf-8')
            except UnicodeDecodeError:
                text_content = file_data.decode('latin-1')
            
            # Parse CSV
            csv_reader = csv.DictReader(io.StringIO(text_content))
            rows = list(csv_reader)
            
            # Extract headers
            headers = list(rows[0].keys()) if rows else []
            
            # Build metadata
            metadata = {
                "type": "csv",
                "headers": headers,
                "row_count": len(rows),
                "column_count": len(headers),
                "size": len(file_data),
                "filename": filename
            }
            
            return {
                "success": True,
                "rows": rows,
                "columns": headers,
                "metadata": metadata
            }
        
        except Exception as e:
            self.logger.error(f"❌ CSV parsing failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"CSV parsing failed: {str(e)}",
                "rows": [],
                "columns": [],
                "metadata": {}
            }
