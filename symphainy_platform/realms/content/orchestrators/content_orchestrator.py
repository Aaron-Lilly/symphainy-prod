"""
Content Orchestrator

Routes parsing requests to the appropriate parsing service based on file type and parsing pattern.

WHAT (Content Realm): I orchestrate file parsing operations
HOW (Orchestrator): I route to appropriate parsing services (structured, unstructured, hybrid, workflow/SOP)
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from symphainy_platform.foundations.public_works.protocols.parsing_service_protocol import (
    ParsingRequest,
    ParsingResult
)

logger = logging.getLogger(__name__)


class ContentOrchestrator:
    """
    Content Orchestrator.
    
    Routes parsing requests to appropriate parsing services:
    - Structured Parsing Service (Excel, CSV, JSON, Binary/Mainframe)
    - Unstructured Parsing Service (PDF, Word, Text, Image)
    - Hybrid Parsing Service (Kreuzberg + fallback)
    - Workflow/SOP Parsing Service (BPMN, Draw.io, JSON workflows, SOP documents)
    """
    
    def __init__(
        self,
        structured_service: Optional[Any] = None,
        unstructured_service: Optional[Any] = None,
        hybrid_service: Optional[Any] = None,
        workflow_sop_service: Optional[Any] = None,
        state_surface: Optional[Any] = None
    ):
        """
        Initialize Content Orchestrator.
        
        Args:
            structured_service: Structured Parsing Service instance
            unstructured_service: Unstructured Parsing Service instance
            hybrid_service: Hybrid Parsing Service instance
            workflow_sop_service: Workflow/SOP Parsing Service instance
            state_surface: State Surface instance
        """
        self.structured_service = structured_service
        self.unstructured_service = unstructured_service
        self.hybrid_service = hybrid_service
        self.workflow_sop_service = workflow_sop_service
        self.state_surface = state_surface
        self.logger = logger
        
        self.logger.info("✅ Content Orchestrator initialized")
    
    async def parse_file(
        self,
        file_reference: str,
        filename: str,
        parsing_type: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> ParsingResult:
        """
        Parse file by routing to appropriate parsing service.
        
        Args:
            file_reference: State Surface reference to file
            filename: Original filename
            parsing_type: Explicit parsing type (structured, unstructured, hybrid, workflow, sop)
                        If not provided, will be inferred from file type
            options: Parsing options (copybook_reference for mainframe, etc.)
        
        Returns:
            ParsingResult with parsed data
        """
        try:
            # Create parsing request
            request = ParsingRequest(
                file_reference=file_reference,
                filename=filename,
                options=options
            )
            
            # Determine parsing type if not provided
            if not parsing_type:
                parsing_type = self._determine_parsing_type(filename, options)
            
            # Route to appropriate service
            if parsing_type == "structured":
                return await self._parse_structured(request)
            elif parsing_type == "unstructured":
                return await self._parse_unstructured(request)
            elif parsing_type == "hybrid":
                return await self._parse_hybrid(request)
            elif parsing_type == "workflow":
                return await self._parse_workflow(request)
            elif parsing_type == "sop":
                return await self._parse_sop(request)
            else:
                return ParsingResult(
                    success=False,
                    error=f"Unknown parsing type: {parsing_type}",
                    timestamp=datetime.utcnow().isoformat()
                )
        
        except Exception as e:
            self.logger.error(f"❌ Content orchestration failed: {e}", exc_info=True)
            return ParsingResult(
                success=False,
                error=f"Content orchestration failed: {str(e)}",
                timestamp=datetime.utcnow().isoformat()
            )
    
    def _determine_parsing_type(
        self,
        filename: str,
        options: Optional[Dict[str, Any]]
    ) -> str:
        """
        Determine parsing type from filename and options.
        
        Args:
            filename: Original filename
            options: Parsing options
        
        Returns:
            Parsing type: "structured", "unstructured", "hybrid", "workflow", "sop"
        """
        # Check explicit type in options
        if options and options.get("parsing_type"):
            return options.get("parsing_type")
        
        # Get file extension
        file_type = self._get_file_type(filename)
        
        # Structured types
        structured_types = ["xlsx", "xls", "csv", "json", "bin", "binary"]
        if file_type in structured_types:
            return "structured"
        
        # Unstructured types
        unstructured_types = ["pdf", "docx", "doc", "txt", "text", "png", "jpg", "jpeg", "gif", "bmp", "tiff"]
        if file_type in unstructured_types:
            return "unstructured"
        
        # Hybrid types (can be parsed as both structured and unstructured)
        hybrid_types = ["excel_with_text"]  # Can be extended
        if file_type in hybrid_types or (options and options.get("hybrid")):
            return "hybrid"
        
        # Workflow types
        workflow_types = ["bpmn", "drawio"]
        if file_type in workflow_types:
            return "workflow"
        
        # SOP types
        sop_types = ["md", "sop"]
        if file_type in sop_types:
            return "sop"
        
        # Default: unstructured
        return "unstructured"
    
    def _get_file_type(self, filename: str) -> str:
        """Get file type from filename."""
        if not filename:
            return "unknown"
        
        ext = filename.lower().split('.')[-1]
        return ext
    
    async def _parse_structured(self, request: ParsingRequest) -> ParsingResult:
        """Route to Structured Parsing Service."""
        if not self.structured_service:
            return ParsingResult(
                success=False,
                error="Structured Parsing Service not available",
                timestamp=datetime.utcnow().isoformat()
            )
        
        return await self.structured_service.parse_structured_file(request)
    
    async def _parse_unstructured(self, request: ParsingRequest) -> ParsingResult:
        """Route to Unstructured Parsing Service."""
        if not self.unstructured_service:
            return ParsingResult(
                success=False,
                error="Unstructured Parsing Service not available",
                timestamp=datetime.utcnow().isoformat()
            )
        
        return await self.unstructured_service.parse_unstructured_file(request)
    
    async def _parse_hybrid(self, request: ParsingRequest) -> ParsingResult:
        """Route to Hybrid Parsing Service."""
        if not self.hybrid_service:
            return ParsingResult(
                success=False,
                error="Hybrid Parsing Service not available",
                timestamp=datetime.utcnow().isoformat()
            )
        
        return await self.hybrid_service.parse_hybrid_file(request)
    
    async def _parse_workflow(self, request: ParsingRequest) -> ParsingResult:
        """Route to Workflow/SOP Parsing Service for workflows."""
        if not self.workflow_sop_service:
            return ParsingResult(
                success=False,
                error="Workflow/SOP Parsing Service not available",
                timestamp=datetime.utcnow().isoformat()
            )
        
        return await self.workflow_sop_service.parse_workflow_file(request)
    
    async def _parse_sop(self, request: ParsingRequest) -> ParsingResult:
        """Route to Workflow/SOP Parsing Service for SOPs."""
        if not self.workflow_sop_service:
            return ParsingResult(
                success=False,
                error="Workflow/SOP Parsing Service not available",
                timestamp=datetime.utcnow().isoformat()
            )
        
        return await self.workflow_sop_service.parse_sop_file(request)
