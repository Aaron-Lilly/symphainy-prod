"""
PDF Processing Adapter - Layer 0

Raw technology client for PDF file parsing.
Uses pdfplumber or PyPDF2 for parsing.

WHAT (Infrastructure): I provide PDF parsing capabilities
HOW (Adapter): I use pdfplumber/PyPDF2 to parse PDF files
"""

import logging
from typing import Dict, Any, Optional
import io

logger = logging.getLogger(__name__)


class PdfProcessingAdapter:
    """
    Adapter for PDF file parsing.
    
    Uses pdfplumber (preferred) or PyPDF2 for parsing PDF files.
    """
    
    def __init__(self):
        """Initialize PDF Processing Adapter."""
        self.logger = logger
        self.pdfplumber_available = False
        self.pypdf2_available = False
        
        # Try to import pdfplumber (preferred - better table extraction)
        try:
            import pdfplumber
            self.pdfplumber = pdfplumber
            self.pdfplumber_available = True
            self.logger.info("✅ Pdfplumber available for PDF parsing")
        except ImportError:
            self.logger.warning("⚠️ Pdfplumber not available, will try PyPDF2")
        
        # Try to import PyPDF2 (fallback)
        try:
            import PyPDF2
            self.PyPDF2 = PyPDF2
            self.pypdf2_available = True
            self.logger.info("✅ PyPDF2 available for PDF parsing")
        except ImportError:
            self.logger.warning("⚠️ PyPDF2 not available")
        
        if not self.pdfplumber_available and not self.pypdf2_available:
            self.logger.warning("⚠️ Neither pdfplumber nor PyPDF2 available - PDF parsing will be limited")
        
        self.logger.info("✅ PDF Processing Adapter initialized")
    
    async def parse_file(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """
        Parse PDF file from bytes.
        
        Args:
            file_data: PDF file content as bytes
            filename: Original filename (for logging)
        
        Returns:
            Dict with parsed data:
            {
                "success": bool,
                "text": str,  # Extracted text
                "tables": List[Dict],  # Extracted tables
                "metadata": Dict,
                "error": Optional[str]
            }
        """
        try:
            # Use pdfplumber if available (preferred - better table extraction)
            if self.pdfplumber_available:
                return await self._parse_with_pdfplumber(file_data, filename)
            
            # Fallback to PyPDF2
            if self.pypdf2_available:
                return await self._parse_with_pypdf2(file_data, filename)
            
            # No library available - return error
            return {
                "success": False,
                "error": "Neither pdfplumber nor PyPDF2 available for PDF parsing",
                "text": "",
                "tables": [],
                "metadata": {}
            }
        
        except Exception as e:
            self.logger.error(f"❌ PDF parsing failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"PDF parsing failed: {str(e)}",
                "text": "",
                "tables": [],
                "metadata": {}
            }
    
    async def _parse_with_pdfplumber(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """Parse PDF file using pdfplumber."""
        try:
            pdf_file = io.BytesIO(file_data)
            
            text_parts = []
            tables = []
            page_count = 0
            
            with self.pdfplumber.open(pdf_file) as pdf:
                page_count = len(pdf.pages)
                
                for page_num, page in enumerate(pdf.pages, 1):
                    # Extract text
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(f"--- Page {page_num} ---\n{page_text}")
                    
                    # Extract tables
                    page_tables = page.extract_tables()
                    for table_idx, table in enumerate(page_tables):
                        if table:
                            # Convert table to structured format
                            if len(table) > 0:
                                headers = table[0] if table else []
                                rows = table[1:] if len(table) > 1 else []
                                
                                tables.append({
                                    "page": page_num,
                                    "table_index": table_idx,
                                    "headers": headers,
                                    "rows": rows,
                                    "row_count": len(rows),
                                    "column_count": len(headers) if headers else 0
                                })
            
            full_text = "\n\n".join(text_parts)
            
            metadata = {
                "type": "pdf",
                "page_count": page_count,
                "table_count": len(tables),
                "filename": filename,
                "size": len(file_data)
            }
            
            return {
                "success": True,
                "text": full_text,
                "tables": tables,
                "metadata": metadata
            }
        
        except Exception as e:
            self.logger.error(f"❌ Pdfplumber PDF parsing failed: {e}", exc_info=True)
            raise
    
    async def _parse_with_pypdf2(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """Parse PDF file using PyPDF2 (text only, no table extraction)."""
        try:
            pdf_file = io.BytesIO(file_data)
            pdf_reader = self.PyPDF2.PdfReader(pdf_file)
            
            text_parts = []
            page_count = len(pdf_reader.pages)
            
            for page_num, page in enumerate(pdf_reader.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(f"--- Page {page_num} ---\n{page_text}")
            
            full_text = "\n\n".join(text_parts)
            
            metadata = {
                "type": "pdf",
                "page_count": page_count,
                "table_count": 0,  # PyPDF2 doesn't extract tables
                "filename": filename,
                "size": len(file_data),
                "parsing_method": "pypdf2"
            }
            
            return {
                "success": True,
                "text": full_text,
                "tables": [],  # PyPDF2 doesn't extract tables
                "metadata": metadata
            }
        
        except Exception as e:
            self.logger.error(f"❌ PyPDF2 PDF parsing failed: {e}", exc_info=True)
            raise
