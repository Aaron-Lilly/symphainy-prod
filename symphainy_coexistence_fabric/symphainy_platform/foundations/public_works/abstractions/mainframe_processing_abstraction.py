"""
Mainframe Processing Abstraction - Layer 1

Lightweight coordination layer for mainframe processing operations.
Uses State Surface for file retrieval.

WHAT (Infrastructure): I coordinate mainframe processing operations
HOW (Abstraction): I provide lightweight coordination for mainframe adapter
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from ..adapters.mainframe_parsing.unified_adapter import MainframeProcessingAdapter
from ..protocols.file_parsing_protocol import FileParsingRequest, FileParsingResult

logger = logging.getLogger(__name__)


class MainframeProcessingAbstraction:
    """
    Mainframe Processing Infrastructure Abstraction.
    
    Lightweight coordination layer for mainframe processing operations.
    Uses State Surface for file retrieval (new architecture).
    Implements FileParsingProtocol.
    """
    
    def __init__(
        self,
        mainframe_adapter: MainframeProcessingAdapter,
        state_surface: Optional[Any] = None
    ):
        """
        Initialize Mainframe Processing Abstraction.
        
        Args:
            mainframe_adapter: Mainframe processing adapter (Layer 0)
            state_surface: State Surface instance for file retrieval
        """
        self.mainframe_adapter = mainframe_adapter
        self.state_surface = state_surface
        self.logger = logger
        
        self.logger.info("✅ Mainframe Processing Abstraction initialized")
    
    async def parse_file(self, request: FileParsingRequest) -> FileParsingResult:
        """
        Parse mainframe file using State Surface references.
        
        Args:
            request: FileParsingRequest with file_reference and copybook_reference
        
        Returns:
            FileParsingResult with parsed records and validation_rules
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
            
            # Validate copybook_reference is provided
            if not request.copybook_reference:
                return FileParsingResult(
                    success=False,
                    error="copybook_reference required for mainframe parsing",
                    timestamp=datetime.utcnow().isoformat()
                )
            
            # Parse using unified adapter (returns FileParsingResult)
            result = await self.mainframe_adapter.parse_file(
                file_reference=request.file_reference,
                copybook_reference=request.copybook_reference,
                options=request.options or {}
            )
            
            # Ensure result is standardized (adapter may return FileParsingResult)
            if not isinstance(result, FileParsingResult):
                # If adapter returns dict, convert to FileParsingResult
                return FileParsingResult(
                    success=result.get("success", False),
                    text_content=result.get("text_content"),
                    structured_data=result.get("structured_data"),
                    metadata=result.get("metadata", {}),
                    validation_rules=result.get("validation_rules"),
                    error=result.get("error"),
                    timestamp=result.get("timestamp", datetime.utcnow().isoformat()),
                    parsing_type=result.get("parsing_type", "mainframe")
                )
            
            # Normalize FileParsingResult to ensure standardized format
            if result.success:
                # Extract data from result
                records = result.structured_data.get("records", []) if result.structured_data else []
                validation_rules = result.validation_rules or {}
                adapter_metadata = result.metadata or {}
                
                # Build structure metadata for chunking service (records as structure)
                structure = {
                    "records": [
                        {
                            "record_index": idx,
                            "record_type": record.get("record_type") if isinstance(record, dict) else None,
                            "data": record
                        }
                        for idx, record in enumerate(records)
                    ]
                }
                
                # Build metadata (include structure, parsing_type)
                metadata = {
                    "parsing_type": "mainframe",
                    "structure": structure,
                    "file_type": "binary",
                    "record_count": len(records),
                    "copybook_name": adapter_metadata.get("copybook_name"),
                    # Include other adapter metadata (but not structure)
                    **{k: v for k, v in adapter_metadata.items() if k not in ["structure", "parsing_type"]}
                }
                
                # Build structured_data (standardized format, no nested metadata)
                structured_data = {
                    "format": "mainframe",
                    "records": records,
                    "schema": result.structured_data.get("schema", {}) if result.structured_data else {}
                }
                
                # Return standardized FileParsingResult
                return FileParsingResult(
                    success=True,
                    text_content=result.text_content,  # May contain parsed records as text
                    structured_data=structured_data,
                    metadata=metadata,
                    validation_rules=validation_rules,  # 88-level fields, level-01
                    parsing_type="mainframe",  # Explicit parsing type
                    timestamp=result.timestamp
                )
            
            # Return error result as-is
            return result
        
        except Exception as e:
            self.logger.error(f"❌ Mainframe parsing failed: {e}", exc_info=True)
            return FileParsingResult(
                success=False,
                error=f"Mainframe parsing failed: {str(e)}",
                timestamp=datetime.utcnow().isoformat()
            )
