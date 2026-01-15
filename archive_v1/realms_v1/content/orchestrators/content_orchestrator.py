"""
Content Orchestrator

Routes parsing requests to the appropriate parsing service based on file type and parsing pattern.
Handles Runtime intents and composes saga steps.

WHAT (Content Realm): I orchestrate file parsing operations
HOW (Orchestrator): I route to appropriate parsing services (structured, unstructured, hybrid, workflow/SOP)
                   I handle Runtime intents and compose saga steps
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from utilities import get_logger, get_clock

from symphainy_platform.foundations.public_works.protocols.parsing_service_protocol import (
    ParsingRequest,
    ParsingResult
)

logger = get_logger(__name__)


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
        state_surface: Optional[Any] = None,
        file_storage_abstraction: Optional[Any] = None
    ):
        """
        Initialize Content Orchestrator.
        
        Args:
            structured_service: Structured Parsing Service instance
            unstructured_service: Unstructured Parsing Service instance
            hybrid_service: Hybrid Parsing Service instance
            workflow_sop_service: Workflow/SOP Parsing Service instance
            state_surface: State Surface instance
            file_storage_abstraction: File Storage Abstraction (for file uploads)
        """
        self.structured_service = structured_service
        self.unstructured_service = unstructured_service
        self.hybrid_service = hybrid_service
        self.workflow_sop_service = workflow_sop_service
        self.state_surface = state_surface
        self.file_storage = file_storage_abstraction
        self.logger = logger
        self.clock = get_clock()
        
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
    
    async def handle_upload_intent(
        self,
        intent_payload: Dict[str, Any],
        execution_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle upload intent from Runtime.
        
        This method composes saga steps for file upload:
        1. Store file (via FileStorageAbstraction)
        2. Create file reference in State Surface
        3. Parse file (via Content Orchestrator)
        
        Args:
            intent_payload: Intent payload containing file_data, filename, etc.
            execution_context: Execution context with tenant_id, session_id, etc.
        
        Returns:
            Dict with file_id, file_reference, and parse_result
        """
        try:
            tenant_id = execution_context.get("tenant_id")
            session_id = execution_context.get("session_id")
            
            # Extract file data and metadata
            file_data_raw = intent_payload.get("file_data")
            filename = intent_payload.get("filename", "uploaded_file")
            
            if not file_data_raw:
                return {
                    "success": False,
                    "error": "file_data is required"
                }
            
            # Decode base64 if needed
            import base64
            if isinstance(file_data_raw, str):
                try:
                    file_data = base64.b64decode(file_data_raw)
                except Exception:
                    # If decoding fails, assume it's already bytes or raw string
                    file_data = file_data_raw.encode('utf-8') if isinstance(file_data_raw, str) else file_data_raw
            else:
                file_data = file_data_raw
            
            # Step 1: Store file via FileStorageAbstraction
            if not self.file_storage:
                return {
                    "success": False,
                    "error": "File Storage Abstraction not available"
                }
            
            # Upload file to GCS + Supabase
            upload_result = await self.file_storage.upload_file(
                file_path=filename,
                file_data=file_data,
                metadata={
                    "tenant_id": tenant_id,
                    "user_id": execution_context.get("user_id"),
                    "ui_name": filename,
                    "status": "uploaded"
                }
            )
            
            if not upload_result.get("success"):
                return {
                    "success": False,
                    "error": upload_result.get("error", "File upload failed")
                }
            
            # Get file_id from upload result
            file_id = upload_result.get("file_id")
            if not file_id:
                return {
                    "success": False,
                    "error": "File upload succeeded but file_id not returned"
                }
            
            # Step 2: Store in State Surface
            if not self.state_surface:
                return {
                    "success": False,
                    "error": "State Surface not available"
                }
            
            file_reference = await self.state_surface.store_file(
                session_id=session_id,
                tenant_id=tenant_id,
                file_data=file_data,
                filename=filename,
                metadata={
                    "file_id": file_id,
                    "uploaded_at": self.clock.now_iso()
                }
            )
            
            # Step 3: Parse file
            parse_result = await self.parse_file(
                file_reference=file_reference,
                filename=filename,
                parsing_type=None,
                options={}
            )
            
            return {
                "success": True,
                "file_id": file_id,
                "file_reference": file_reference,
                "parse_result": parse_result.to_dict() if hasattr(parse_result, 'to_dict') else {
                    "success": parse_result.success,
                    "data": parse_result.data if hasattr(parse_result, 'data') else None,
                    "error": parse_result.error if hasattr(parse_result, 'error') else None
                }
            }
        
        except Exception as e:
            self.logger.error(f"❌ Upload intent handling failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"Upload intent handling failed: {str(e)}"
            }