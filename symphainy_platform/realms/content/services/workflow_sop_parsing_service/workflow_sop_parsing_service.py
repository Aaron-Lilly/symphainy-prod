"""
Workflow/SOP Parsing Service

Service for parsing workflow files (BPMN, Draw.io, JSON) and SOP documents.
Uses State Surface for file retrieval (new architecture).

WHAT (Content Realm): I parse workflow and SOP files
HOW (Service): I coordinate parsing modules for workflows and SOPs
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from symphainy_platform.foundations.public_works.protocols.parsing_service_protocol import (
    ParsingRequest,
    ParsingResult,
    WorkflowSOPParsingProtocol
)

logger = logging.getLogger(__name__)


class WorkflowSOPParsingService(WorkflowSOPParsingProtocol):
    """
    Workflow/SOP Parsing Service.
    
    Handles parsing of:
    - Workflow files: BPMN, Draw.io, JSON workflows
    - SOP documents: DOCX, PDF, TXT, MD
    """
    
    def __init__(
        self,
        state_surface: Any,
        platform_gateway: Optional[Any] = None
    ):
        """
        Initialize Workflow/SOP Parsing Service.
        
        Args:
            state_surface: State Surface instance for file retrieval
            platform_gateway: Platform Gateway for accessing abstractions
        """
        self.state_surface = state_surface
        self.platform_gateway = platform_gateway
        self.logger = logger
        
        # Lazy import modules
        self._workflow_parser = None
        self._sop_parser = None
        
        self.logger.info("✅ Workflow/SOP Parsing Service initialized")
    
    async def parse_workflow_file(
        self,
        request: ParsingRequest
    ) -> ParsingResult:
        """
        Parse workflow file (BPMN, Draw.io, JSON).
        
        Args:
            request: ParsingRequest with file_reference
        
        Returns:
            ParsingResult with workflow structure (nodes, edges)
        """
        try:
            # Get file metadata to determine type
            file_metadata = await self.state_surface.get_file_metadata(request.file_reference)
            
            if not file_metadata:
                return ParsingResult(
                    success=False,
                    error=f"File not found: {request.file_reference}",
                    timestamp=datetime.utcnow().isoformat()
                )
            
            filename = file_metadata.get("filename", request.filename)
            file_type = self._get_file_type(filename)
            
            # Route to workflow parser
            if not self._workflow_parser:
                from .modules.workflow_parser import WorkflowParser
                self._workflow_parser = WorkflowParser(
                    state_surface=self.state_surface,
                    platform_gateway=self.platform_gateway
                )
            
            return await self._workflow_parser.parse(request, file_type)
        
        except Exception as e:
            self.logger.error(f"❌ Workflow parsing failed: {e}", exc_info=True)
            return ParsingResult(
                success=False,
                error=f"Workflow parsing failed: {str(e)}",
                timestamp=datetime.utcnow().isoformat()
            )
    
    async def parse_sop_file(
        self,
        request: ParsingRequest
    ) -> ParsingResult:
        """
        Parse SOP file (DOCX, PDF, TXT, MD).
        
        Args:
            request: ParsingRequest with file_reference
        
        Returns:
            ParsingResult with SOP structure (sections, steps, roles)
        """
        try:
            # Get file metadata to determine type
            file_metadata = await self.state_surface.get_file_metadata(request.file_reference)
            
            if not file_metadata:
                return ParsingResult(
                    success=False,
                    error=f"File not found: {request.file_reference}",
                    timestamp=datetime.utcnow().isoformat()
                )
            
            filename = file_metadata.get("filename", request.filename)
            file_type = self._get_file_type(filename)
            
            # Route to SOP parser
            if not self._sop_parser:
                from .modules.sop_parser import SOPParser
                self._sop_parser = SOPParser(
                    state_surface=self.state_surface,
                    platform_gateway=self.platform_gateway
                )
            
            return await self._sop_parser.parse(request, file_type)
        
        except Exception as e:
            self.logger.error(f"❌ SOP parsing failed: {e}", exc_info=True)
            return ParsingResult(
                success=False,
                error=f"SOP parsing failed: {str(e)}",
                timestamp=datetime.utcnow().isoformat()
            )
    
    def _get_file_type(self, filename: str) -> str:
        """Get file type from filename."""
        if not filename:
            return "unknown"
        
        ext = filename.lower().split('.')[-1]
        return ext
