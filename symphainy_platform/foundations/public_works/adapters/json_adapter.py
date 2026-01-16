"""
JSON Processing Adapter - Layer 0

Raw technology client for JSON file parsing.
Uses Python's built-in json module.

WHAT (Infrastructure): I provide JSON parsing capabilities
HOW (Adapter): I use Python's json module to parse JSON files
"""

import logging
import json
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class JsonProcessingAdapter:
    """
    Adapter for JSON file parsing.
    
    Uses Python's built-in json module for parsing.
    """
    
    def __init__(self):
        """Initialize JSON Processing Adapter."""
        self.logger = logger
        self.logger.info("✅ JSON Processing Adapter initialized")
    
    async def parse_file(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """
        Parse JSON file from bytes.
        
        Args:
            file_data: JSON file content as bytes
            filename: Original filename (for logging)
        
        Returns:
            Dict with parsed data:
            {
                "success": bool,
                "data": Any,  # Parsed JSON object/array
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
            
            # Parse JSON
            json_data = json.loads(text_content)
            
            # Build metadata
            metadata = {
                "type": "json",
                "is_array": isinstance(json_data, list),
                "is_object": isinstance(json_data, dict),
                "size": len(file_data),
                "filename": filename
            }
            
            return {
                "success": True,
                "data": json_data,
                "metadata": metadata
            }
        
        except json.JSONDecodeError as e:
            self.logger.error(f"❌ JSON parsing failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"JSON parsing failed: {str(e)}",
                "data": None,
                "metadata": {}
            }
        except Exception as e:
            self.logger.error(f"❌ JSON parsing failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"JSON parsing failed: {str(e)}",
                "data": None,
                "metadata": {}
            }
