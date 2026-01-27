"""
HTML Processing Adapter - Layer 0

Raw technology client for HTML file parsing.
Uses BeautifulSoup for parsing.

WHAT (Infrastructure): I provide HTML parsing capabilities
HOW (Adapter): I use BeautifulSoup to parse HTML files
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class HtmlProcessingAdapter:
    """
    Adapter for HTML file parsing.
    
    Uses BeautifulSoup for parsing HTML files.
    """
    
    def __init__(self):
        """Initialize HTML Processing Adapter."""
        self.logger = logger
        self.bs4_available = False
        
        # Try to import BeautifulSoup
        try:
            from bs4 import BeautifulSoup
            self.BeautifulSoup = BeautifulSoup
            self.bs4_available = True
            self.logger.info("✅ BeautifulSoup available for HTML parsing")
        except ImportError:
            self.logger.warning("⚠️ BeautifulSoup not available - HTML parsing will not work")
        
        self.logger.info("✅ HTML Processing Adapter initialized")
    
    async def parse_file(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """
        Parse HTML file from bytes.
        
        Args:
            file_data: HTML file content as bytes
            filename: Original filename (for logging)
        
        Returns:
            Dict with parsed data:
            {
                "success": bool,
                "text": str,  # Extracted text
                "elements": List[Dict],  # Extracted elements
                "tables": List[Dict],  # Extracted tables
                "metadata": Dict,
                "error": Optional[str]
            }
        """
        try:
            if not self.bs4_available:
                return {
                    "success": False,
                    "error": "BeautifulSoup not available for HTML parsing",
                    "text": "",
                    "elements": [],
                    "tables": [],
                    "metadata": {}
                }
            
            # Try UTF-8 first, then fallback to latin-1
            try:
                html_content = file_data.decode('utf-8')
            except UnicodeDecodeError:
                html_content = file_data.decode('latin-1')
            
            # Parse HTML
            soup = self.BeautifulSoup(html_content, 'html.parser')
            
            # Extract text (remove script and style tags)
            for script in soup(["script", "style"]):
                script.decompose()
            
            text = soup.get_text(separator='\n', strip=True)
            
            # Extract tables
            tables = []
            for table_idx, table in enumerate(soup.find_all('table')):
                table_data = []
                headers = None
                
                # Find header row (th or first tr with th)
                header_row = table.find('tr')
                if header_row:
                    th_cells = header_row.find_all(['th', 'td'])
                    if th_cells:
                        headers = [cell.get_text(strip=True) for cell in th_cells]
                
                # Find data rows
                rows = table.find_all('tr')
                for row_idx, row in enumerate(rows):
                    if row_idx == 0 and headers:
                        continue  # Skip header row if we already extracted it
                    
                    cells = row.find_all(['td', 'th'])
                    if cells:
                        row_data = [cell.get_text(strip=True) for cell in cells]
                        
                        if headers:
                            row_dict = {headers[i]: row_data[i] if i < len(row_data) else "" for i in range(len(headers))}
                            table_data.append(row_dict)
                        else:
                            # No headers - use column indices
                            row_dict = {f"Column_{i+1}": row_data[i] if i < len(row_data) else "" for i in range(len(row_data))}
                            table_data.append(row_dict)
                
                if table_data:
                    table_headers = headers or [f"Column_{i+1}" for i in range(len(table_data[0].keys()) if table_data else 0)]
                    tables.append({
                        "table_index": table_idx,
                        "headers": table_headers,
                        "rows": table_data,
                        "row_count": len(table_data),
                        "column_count": len(table_headers)
                    })
            
            # Extract key elements (links, headings, etc.)
            elements = []
            
            # Extract links
            for link in soup.find_all('a', href=True):
                elements.append({
                    "type": "link",
                    "text": link.get_text(strip=True),
                    "href": link.get('href')
                })
            
            # Extract headings
            for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                elements.append({
                    "type": "heading",
                    "level": heading.name,
                    "text": heading.get_text(strip=True)
                })
            
            metadata = {
                "type": "html",
                "table_count": len(tables),
                "element_count": len(elements),
                "filename": filename,
                "size": len(file_data)
            }
            
            return {
                "success": True,
                "text": text,
                "elements": elements,
                "tables": tables,
                "metadata": metadata
            }
        
        except Exception as e:
            self.logger.error(f"❌ HTML parsing failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"HTML parsing failed: {str(e)}",
                "text": "",
                "elements": [],
                "tables": [],
                "metadata": {}
            }
