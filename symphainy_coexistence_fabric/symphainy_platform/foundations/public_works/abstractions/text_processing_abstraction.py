"""
Text Processing Abstraction - Layer 1

Lightweight coordination layer for text processing operations.
Uses State Surface for file retrieval.

WHAT (Infrastructure): I coordinate text processing operations
HOW (Abstraction): I provide lightweight coordination for text adapter
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from ..protocols.file_parsing_protocol import FileParsingRequest, FileParsingResult

logger = logging.getLogger(__name__)


class TextProcessingAbstraction:
    """
    Text Processing Infrastructure Abstraction.
    
    Lightweight coordination layer for text processing operations.
    Uses State Surface for file retrieval (new architecture).
    """
    
    def __init__(
        self,
        text_adapter: Optional[Any] = None,  # Will be TextProcessingAdapter
        state_surface: Optional[Any] = None
    ):
        """
        Initialize Text Processing Abstraction.
        
        Args:
            text_adapter: Text adapter (Layer 0)
            state_surface: State Surface instance for file retrieval
        """
        self.text_adapter = text_adapter
        self.state_surface = state_surface
        self.logger = logger
        
        self.logger.info("✅ Text Processing Abstraction initialized")
    
    async def parse_file(self, request: FileParsingRequest) -> FileParsingResult:
        """
        Parse text file using State Surface reference.
        
        Args:
            request: FileParsingRequest with file_reference
        
        Returns:
            FileParsingResult with text content
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
            
            # Text parsing is simple - can be done directly if no adapter
            if not self.text_adapter:
                # Direct text parsing (no adapter needed)
                file_data = await state_surface.get_file(request.file_reference)
                
                if not file_data:
                    return FileParsingResult(
                        success=False,
                        error=f"File not found: {request.file_reference}",
                        timestamp=datetime.utcnow().isoformat()
                    )
                
                # Try UTF-8 first, then fallback to latin-1
                try:
                    text_content = file_data.decode('utf-8')
                except UnicodeDecodeError:
                    text_content = file_data.decode('latin-1')
                
                # Extract paragraphs from text (deterministic split)
                import re
                para_texts = re.split(r'\n\s*\n', text_content)
                paragraphs = [para.strip() for para in para_texts if para.strip()]
                
                # Build structure metadata for chunking service
                structure = {
                    "paragraphs": [
                        {
                            "paragraph_index": idx,
                            "text": para
                        }
                        for idx, para in enumerate(paragraphs)
                    ]
                }
                
                # Build metadata (include structure, parsing_type)
                metadata = {
                    "parsing_type": "unstructured",
                    "structure": structure,
                    "file_type": "txt",
                    "paragraph_count": len(paragraphs),
                    "size": len(file_data)
                }
                
                return FileParsingResult(
                    success=True,
                    text_content=text_content if text_content else None,
                    structured_data=None,  # Plain text has no structured data
                    metadata=metadata,
                    parsing_type="unstructured",  # Explicit parsing type
                    timestamp=datetime.utcnow().isoformat()
                )
            
            # Use adapter if provided
            file_data = await state_surface.get_file(request.file_reference)
            
            if not file_data:
                return FileParsingResult(
                    success=False,
                    error=f"File not found: {request.file_reference}",
                    timestamp=datetime.utcnow().isoformat()
                )
            
            result = await self.text_adapter.parse_file(file_data, request.filename)
            
            if not result.get("success"):
                return FileParsingResult(
                    success=False,
                    error=result.get("error", "Text parsing failed"),
                    timestamp=datetime.utcnow().isoformat()
                )
            
            # Extract data from adapter result
            text_content = result.get("text", "")
            adapter_metadata = result.get("metadata", {})
            
            # Extract paragraphs from text (deterministic split)
            import re
            para_texts = re.split(r'\n\s*\n', text_content)
            paragraphs = [para.strip() for para in para_texts if para.strip()]
            
            # Build structure metadata for chunking service
            structure = {
                "paragraphs": [
                    {
                        "paragraph_index": idx,
                        "text": para
                    }
                    for idx, para in enumerate(paragraphs)
                ]
            }
            
            # Build metadata (include structure, parsing_type)
            metadata = {
                "parsing_type": "unstructured",
                "structure": structure,
                "file_type": "txt",
                "paragraph_count": len(paragraphs),
                # Include other adapter metadata (but not structure)
                **{k: v for k, v in adapter_metadata.items() if k != "structure"}
            }
            
            # Convert to FileParsingResult (standardized format)
            return FileParsingResult(
                success=True,
                text_content=text_content if text_content else None,
                structured_data=None,  # Plain text has no structured data
                metadata=metadata,
                parsing_type="unstructured",  # Explicit parsing type
                timestamp=datetime.utcnow().isoformat()
            )
        
        except Exception as e:
            self.logger.error(f"❌ Text parsing failed: {e}", exc_info=True)
            return FileParsingResult(
                success=False,
                error=f"Text parsing failed: {str(e)}",
                timestamp=datetime.utcnow().isoformat()
            )
