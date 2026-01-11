"""
SOP Parser Module

Parses SOP documents (DOCX, PDF, TXT, MD) by extracting structure from text.
"""

import logging
import re
from typing import Dict, Any, Optional, List
from datetime import datetime

from symphainy_platform.foundations.public_works.protocols.parsing_service_protocol import (
    ParsingRequest,
    ParsingResult
)
from symphainy_platform.foundations.public_works.protocols.file_parsing_protocol import (
    FileParsingRequest,
    FileParsingResult
)

logger = logging.getLogger(__name__)


class SOPParser:
    """
    SOP Parser Module.
    
    Parses SOP documents by:
    1. Extracting text using unstructured parsing
    2. Extracting structure (sections, steps, roles, dependencies)
    """
    
    def __init__(
        self,
        state_surface: Any,
        platform_gateway: Optional[Any] = None
    ):
        """
        Initialize SOP Parser.
        
        Args:
            state_surface: State Surface instance
            platform_gateway: Platform Gateway for accessing unstructured parsing
        """
        self.state_surface = state_surface
        self.platform_gateway = platform_gateway
        self.logger = logger
    
    async def parse(self, request: ParsingRequest, file_type: str) -> ParsingResult:
        """
        Parse SOP file.
        
        Args:
            request: ParsingRequest with file_reference
            file_type: File type (docx, pdf, txt, md)
        
        Returns:
            ParsingResult with SOP structure (sections, steps, roles, dependencies)
        """
        try:
            # First, extract text using unstructured parsing
            text_content = await self._extract_text(request, file_type)
            
            if not text_content:
                return ParsingResult(
                    success=False,
                    error="Failed to extract text from SOP file",
                    timestamp=datetime.utcnow().isoformat()
                )
            
            # Extract SOP structure from text
            sop_structure = self._extract_sop_structure(text_content)
            
            return ParsingResult(
                success=True,
                data=sop_structure,
                metadata={
                    "type": "sop",
                    "file_type": file_type,
                    "text_length": len(text_content)
                },
                timestamp=datetime.utcnow().isoformat()
            )
        
        except Exception as e:
            self.logger.error(f"❌ SOP parsing failed: {e}", exc_info=True)
            return ParsingResult(
                success=False,
                error=f"SOP parsing failed: {str(e)}",
                timestamp=datetime.utcnow().isoformat()
            )
    
    async def _extract_text(self, request: ParsingRequest, file_type: str) -> str:
        """Extract text from SOP file using unstructured parsing."""
        try:
            # For text/markdown files, read directly
            if file_type in ["txt", "md"]:
                file_data = await self.state_surface.get_file(request.file_reference)
                if file_data:
                    return file_data.decode('utf-8')
                return ""
            
            # For DOCX/PDF, use unstructured parsing service
            if not self.platform_gateway:
                return ""
            
            # Get unstructured parsing service
            unstructured_service = await self.platform_gateway.get_service(
                "unstructured_parsing_service"
            )
            
            if not unstructured_service:
                return ""
            
            # Parse file
            result = await unstructured_service.parse_unstructured_file(request)
            
            if result.success and result.data:
                # Combine text chunks
                text_chunks = result.data.get("text_chunks", [])
                return "\n\n".join(text_chunks)
            
            return ""
        
        except Exception as e:
            self.logger.error(f"Failed to extract text: {e}")
            return ""
    
    def _extract_sop_structure(self, text_content: str) -> Dict[str, Any]:
        """
        Extract SOP structure from text.
        
        Extracts:
        - Title
        - Sections
        - Steps (numbered/bulleted)
        - Roles
        - Dependencies
        """
        lines = text_content.split("\n")
        
        # Extract title (first non-empty line, or line with #)
        title = ""
        for line in lines:
            line = line.strip()
            if line:
                if line.startswith("#"):
                    title = line.lstrip("#").strip()
                else:
                    title = line
                break
        
        # Extract sections (headers with # or all caps)
        sections = []
        current_section = None
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Check if this is a section header
            if line.startswith("#") or (line.isupper() and len(line) > 3):
                if current_section:
                    sections.append(current_section)
                current_section = {
                    "title": line.lstrip("#").strip(),
                    "content": [],
                    "steps": []
                }
            elif current_section:
                # Check if this is a step (numbered or bulleted)
                step_match = re.match(r'^(\d+\.|[-*])\s+(.+)', line)
                if step_match:
                    current_section["steps"].append({
                        "number": len(current_section["steps"]) + 1,
                        "text": step_match.group(2)
                    })
                else:
                    current_section["content"].append(line)
        
        if current_section:
            sections.append(current_section)
        
        # Extract roles (look for patterns like "Role:", "Responsible:", etc.)
        roles = []
        role_pattern = re.compile(r'(?:Role|Responsible|Owner|Assignee):\s*(.+)', re.IGNORECASE)
        for line in lines:
            match = role_pattern.search(line)
            if match:
                roles.append(match.group(1).strip())
        
        # Extract dependencies (look for patterns like "Depends on:", "Requires:", etc.)
        dependencies = []
        dep_pattern = re.compile(r'(?:Depends on|Requires|Prerequisite):\s*(.+)', re.IGNORECASE)
        for line in lines:
            match = dep_pattern.search(line)
            if match:
                dependencies.append(match.group(1).strip())
        
        return {
            "title": title,
            "sections": sections,
            "roles": list(set(roles)),  # Remove duplicates
            "dependencies": list(set(dependencies)),  # Remove duplicates
            "step_count": sum(len(section.get("steps", [])) for section in sections)
        }
