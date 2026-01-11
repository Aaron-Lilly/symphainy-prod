"""
Kreuzberg Adapter - Layer 0

Raw technology client for Kreuzberg document intelligence platform.
Handles communication with Kreuzberg service (SDK, API, or local service).

WHAT (Infrastructure): I provide Kreuzberg document intelligence capabilities
HOW (Adapter): I call Kreuzberg SDK/API for document extraction
"""

import logging
from typing import Dict, Any, Optional
import httpx
import asyncio

logger = logging.getLogger(__name__)


class KreuzbergAdapter:
    """
    Adapter for Kreuzberg document intelligence platform.
    
    Kreuzberg extracts text, tables, and metadata from 56+ file formats.
    Supports both structured (tables) and unstructured (text) extraction in one pass.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "http://localhost:8080"
    ):
        """
        Initialize Kreuzberg adapter.
        
        Args:
            api_key: Kreuzberg API key (if using hosted service)
            base_url: Kreuzberg service URL (if using local service or API server)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.logger = logger
        
        self.logger.info(f"✅ Kreuzberg Adapter initialized (base_url: {base_url})")
    
    async def extract_document(
        self,
        file_data: bytes,
        filename: str,
        output_format: str = "json"  # "json" or "markdown"
    ) -> Dict[str, Any]:
        """
        Extract text, tables, and metadata from document using Kreuzberg.
        
        Args:
            file_data: File data as bytes
            filename: Original filename
            output_format: Output format ("json" or "markdown")
        
        Returns:
            Dictionary with extracted content:
            {
                "text": str,  # Full text content
                "tables": List[Dict],  # Extracted tables
                "metadata": Dict,  # Document metadata
                "structure": Dict  # Document structure
            }
        """
        try:
            # Try HTTP API first (if Kreuzberg is running as API server)
            if self.base_url.startswith("http"):
                return await self._extract_via_api(file_data, filename, output_format)
            
            # Try SDK (if Kreuzberg Python SDK is available)
            try:
                import kreuzberg
                return await self._extract_via_sdk(file_data, filename, output_format)
            except ImportError:
                self.logger.warning("Kreuzberg SDK not available, using API")
                return await self._extract_via_api(file_data, filename, output_format)
        
        except Exception as e:
            self.logger.error(f"❌ Kreuzberg extraction failed: {e}")
            raise
    
    async def _extract_via_api(
        self,
        file_data: bytes,
        filename: str,
        output_format: str
    ) -> Dict[str, Any]:
        """
        Extract document via Kreuzberg HTTP API.
        
        Args:
            file_data: File data as bytes
            filename: Original filename
            output_format: Output format ("json" or "markdown")
        
        Returns:
            Dictionary with extracted content
        """
        try:
            async with httpx.AsyncClient(timeout=300.0) as client:
                # Prepare multipart form data
                files = {
                    'file': (filename, file_data, 'application/octet-stream')
                }
                data = {
                    'output_format': output_format
                }
                
                headers = {}
                if self.api_key:
                    headers['Authorization'] = f'Bearer {self.api_key}'
                
                # Call Kreuzberg API
                response = await client.post(
                    f"{self.base_url}/extract",
                    files=files,
                    data=data,
                    headers=headers
                )
                response.raise_for_status()
                
                result = response.json()
                
                # Convert to standard format
                return {
                    "text": result.get("text", ""),
                    "tables": result.get("tables", []),
                    "metadata": result.get("metadata", {}),
                    "structure": result.get("structure", {})
                }
        
        except httpx.HTTPError as e:
            self.logger.error(f"❌ Kreuzberg API error: {e}")
            raise Exception(f"Kreuzberg API failed: {str(e)}")
        except Exception as e:
            self.logger.error(f"❌ Kreuzberg extraction error: {e}")
            raise
    
    async def _extract_via_sdk(
        self,
        file_data: bytes,
        filename: str,
        output_format: str
    ) -> Dict[str, Any]:
        """
        Extract document via Kreuzberg Python SDK.
        
        Args:
            file_data: File data as bytes
            filename: Original filename
            output_format: Output format ("json" or "markdown")
        
        Returns:
            Dictionary with extracted content
        """
        try:
            # Run SDK extraction in thread pool (SDK may be synchronous)
            result = await asyncio.to_thread(
                self._extract_sync,
                file_data,
                filename,
                output_format
            )
            return result
        
        except Exception as e:
            self.logger.error(f"❌ Kreuzberg SDK error: {e}")
            raise
    
    def _extract_sync(
        self,
        file_data: bytes,
        filename: str,
        output_format: str
    ) -> Dict[str, Any]:
        """
        Synchronous extraction using Kreuzberg SDK.
        
        This method runs in a thread pool to avoid blocking.
        """
        import kreuzberg
        
        # Create Kreuzberg client
        client = kreuzberg.Client(api_key=self.api_key)
        
        # Extract document
        result = client.extract(
            file_data=file_data,
            filename=filename,
            output_format=output_format
        )
        
        # Convert to standard format
        return {
            "text": result.get("text", ""),
            "tables": result.get("tables", []),
            "metadata": result.get("metadata", {}),
            "structure": result.get("structure", {})
        }
