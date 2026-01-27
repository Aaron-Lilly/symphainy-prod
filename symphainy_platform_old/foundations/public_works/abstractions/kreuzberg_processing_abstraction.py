"""
Kreuzberg Processing Abstraction - Layer 1

Lightweight coordination layer for Kreuzberg processing operations.
Uses State Surface for file retrieval.

WHAT (Infrastructure): I coordinate Kreuzberg document processing operations
HOW (Abstraction): I provide lightweight coordination for Kreuzberg adapter
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from ..adapters.kreuzberg_adapter import KreuzbergAdapter
from ..protocols.file_parsing_protocol import FileParsingRequest, FileParsingResult

logger = logging.getLogger(__name__)


class KreuzbergProcessingAbstraction:
    """
    Kreuzberg Processing Infrastructure Abstraction.
    
    Lightweight coordination layer for Kreuzberg processing operations.
    Uses State Surface for file retrieval (new architecture).
    """
    
    def __init__(
        self,
        kreuzberg_adapter: KreuzbergAdapter,
        state_surface: Optional[Any] = None
    ):
        """
        Initialize Kreuzberg Processing Abstraction.
        
        Args:
            kreuzberg_adapter: Kreuzberg adapter (Layer 0)
            state_surface: State Surface instance for file retrieval
        """
        self.kreuzberg_adapter = kreuzberg_adapter
        self.state_surface = state_surface
        self.logger = logger
        
        self.logger.info("✅ Kreuzberg Processing Abstraction initialized")
    
    async def parse_file(self, request: FileParsingRequest) -> FileParsingResult:
        """
        Parse file using Kreuzberg.
        
        Returns both structured (tables) and unstructured (text) content.
        Uses State Surface for file retrieval (new architecture).
        
        Args:
            request: FileParsingRequest with file_reference
        
        Returns:
            FileParsingResult with extracted content
        """
        try:
            # Get State Surface from request if not provided in __init__
            state_surface = request.state_surface or self.state_surface
            
            if not state_surface:
                return FileParsingResult(
                    success=False,
                    error="State Surface not available for file retrieval",
                    timestamp=datetime.utcnow().isoformat()
                )
            
            # Retrieve file from State Surface
            file_data = await state_surface.get_file(request.file_reference)
            
            if not file_data:
                return FileParsingResult(
                    success=False,
                    error=f"File not found: {request.file_reference}",
                    timestamp=datetime.utcnow().isoformat()
                )
            
            # Extract using Kreuzberg adapter
            result = await self.kreuzberg_adapter.extract_document(
                file_data=file_data,
                filename=request.filename,
                output_format="json"
            )
            
            # Extract data from adapter result
            text_content = result.get("text", "")
            tables = result.get("tables", [])
            adapter_metadata = result.get("metadata", {})
            
            # Move structure from structured_data to metadata.structure (standardization)
            structure = result.get("structure", {}) or result.get("structured_data", {}).get("structure", {})
            
            # Kreuzberg provides structure (pages, sections, paragraphs) - use it
            if not structure:
                # Fallback: Extract structure from text if not provided
                import re
                para_texts = re.split(r'\n\s*\n', text_content)
                structure = {
                    "paragraphs": [
                        {
                            "paragraph_index": idx,
                            "text": para.strip()
                        }
                        for idx, para in enumerate(para_texts) if para.strip()
                    ]
                }
            
            # Determine parsing type (hybrid - Kreuzberg extracts both text and tables)
            parsing_type = "hybrid"
            
            # Build metadata (include structure, parsing_type)
            metadata = {
                "parsing_type": parsing_type,
                "structure": structure,  # Move structure here (not in structured_data)
                "file_type": "pdf",  # Kreuzberg typically processes PDFs
                "table_count": len(tables),
                # Include other adapter metadata (but not structure)
                **{k: v for k, v in adapter_metadata.items() if k != "structure"}
            }
            
            # Build structured_data (standardized format, no nested metadata or structure)
            structured_data = {
                "format": "hybrid",
                "tables": tables
            }
            
            # Convert to FileParsingResult (standardized format)
            return FileParsingResult(
                success=True,
                text_content=text_content if text_content else None,
                structured_data=structured_data,
                metadata=metadata,
                parsing_type=parsing_type,  # Explicit parsing type
                timestamp=datetime.utcnow().isoformat()
            )
        
        except Exception as e:
            self.logger.error(f"❌ Kreuzberg parsing failed: {e}")
            return FileParsingResult(
                success=False,
                error=f"Kreuzberg parsing failed: {str(e)}",
                timestamp=datetime.utcnow().isoformat()
            )
