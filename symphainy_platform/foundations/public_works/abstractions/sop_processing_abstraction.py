"""
SOP Processing Abstraction - Layer 1

Lightweight coordination layer for SOP processing operations (Markdown).
Extracts SOP structure (sections, steps) for Journey realm.

WHAT (Infrastructure): I coordinate SOP processing operations
HOW (Abstraction): I provide lightweight coordination for SOP parsing
"""

import logging
import re
from typing import Dict, Any, Optional, List
from datetime import datetime

from ..protocols.file_parsing_protocol import FileParsingRequest, FileParsingResult

logger = logging.getLogger(__name__)


class SopProcessingAbstraction:
    """
    SOP Processing Infrastructure Abstraction.
    
    Lightweight coordination layer for SOP processing operations.
    Processes Markdown files and extracts SOP structure (sections, steps).
    """
    
    def __init__(
        self,
        sop_adapter: Optional[Any] = None,  # For future SOP-specific adapter
        state_surface: Optional[Any] = None
    ):
        """
        Initialize SOP Processing Abstraction.
        
        Args:
            sop_adapter: SOP adapter (Layer 0) - optional, uses built-in parsing for now
            state_surface: State Surface instance for file retrieval
        """
        self.sop_adapter = sop_adapter
        self.state_surface = state_surface
        self.logger = logger
        
        self.logger.info("✅ SOP Processing Abstraction initialized")
    
    async def parse_file(self, request: FileParsingRequest) -> FileParsingResult:
        """
        Parse SOP file (Markdown) using State Surface reference.
        
        Args:
            request: FileParsingRequest with file_reference
        
        Returns:
            FileParsingResult with SOP structure (sections, steps)
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
            
            # Decode file data if bytes
            if isinstance(file_data, bytes):
                markdown_text = file_data.decode('utf-8')
            else:
                markdown_text = str(file_data)
            
            # Extract SOP structure from Markdown
            sections, steps = self._extract_sop_structure(markdown_text)
            
            # Build structure metadata for chunking service
            structure = {
                "sections": [
                    {
                        "section_index": idx,
                        "section_title": section.get("title", ""),
                        "section_level": section.get("level", 1),  # H1, H2, etc.
                        "text": section.get("text", ""),
                        "paragraphs": section.get("paragraphs", [])
                    }
                    for idx, section in enumerate(sections)
                ],
                "steps": [
                    {
                        "step_index": idx,
                        "step_number": step.get("number"),
                        "step_text": step.get("text", ""),
                        "checkpoints": step.get("checkpoints", [])
                    }
                    for idx, step in enumerate(steps)
                ]
            }
            
            # Build metadata (include structure, parsing_type)
            metadata = {
                "parsing_type": "sop",
                "structure": structure,
                "file_type": "markdown",
                "section_count": len(sections),
                "step_count": len(steps)
            }
            
            # Build structured_data (standardized format, no nested metadata)
            structured_data = {
                "format": "sop",
                "sections": sections,
                "steps": steps
            }
            
            # Convert to FileParsingResult (standardized format)
            return FileParsingResult(
                success=True,
                text_content=markdown_text if markdown_text else None,
                structured_data=structured_data,
                metadata=metadata,
                parsing_type="sop",  # Explicit parsing type
                timestamp=datetime.utcnow().isoformat()
            )
        
        except Exception as e:
            self.logger.error(f"❌ SOP parsing failed: {e}", exc_info=True)
            return FileParsingResult(
                success=False,
                error=f"SOP parsing failed: {str(e)}",
                timestamp=datetime.utcnow().isoformat()
            )
    
    def _extract_sop_structure(self, markdown_text: str) -> tuple:
        """
        Extract SOP structure (sections, steps) from Markdown.
        
        Args:
            markdown_text: Markdown content
        
        Returns:
            Tuple of (sections, steps) lists
        """
        sections = []
        steps = []
        
        lines = markdown_text.split('\n')
        current_section = None
        current_paragraphs = []
        step_number = 1
        
        for line in lines:
            line_stripped = line.strip()
            
            # Detect headers (sections)
            if line_stripped.startswith('#'):
                # Save previous section if exists
                if current_section:
                    current_section["paragraphs"] = current_paragraphs
                    sections.append(current_section)
                    current_paragraphs = []
                
                # Extract header level and title
                level = len(line) - len(line.lstrip('#'))
                title = line_stripped.lstrip('#').strip()
                
                current_section = {
                    "title": title,
                    "level": level,
                    "text": line_stripped,
                    "paragraphs": []
                }
            
            # Detect numbered steps (1., 2., etc. or -)
            elif re.match(r'^\d+[\.\)]\s+', line_stripped) or re.match(r'^-\s+', line_stripped):
                step_text = re.sub(r'^\d+[\.\)]\s+', '', line_stripped).lstrip('- ').strip()
                steps.append({
                    "number": step_number,
                    "text": step_text,
                    "checkpoints": []  # Could be enhanced to detect checkpoints
                })
                step_number += 1
            
            # Regular paragraph text
            elif line_stripped:
                if current_section:
                    current_paragraphs.append(line_stripped)
                else:
                    # Text before first section
                    if not sections:
                        sections.append({
                            "title": "",
                            "level": 0,
                            "text": line_stripped,
                            "paragraphs": []
                        })
        
        # Save last section
        if current_section:
            current_section["paragraphs"] = current_paragraphs
            sections.append(current_section)
        
        return sections, steps
