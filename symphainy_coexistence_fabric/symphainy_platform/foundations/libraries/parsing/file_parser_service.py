"""
File Parser Service - Pure Data Processing for File Parsing

Enabling service for file parsing operations.

WHAT (Enabling Service Role): I execute file parsing
HOW (Enabling Service Implementation): I use Public Works abstractions for parsing

Key Principle: Pure data processing - no LLM, no business logic, no orchestration.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional
from datetime import datetime

from utilities import get_logger, generate_event_id
from symphainy_platform.runtime.execution_context import ExecutionContext
from symphainy_platform.foundations.public_works.protocols.file_parsing_protocol import (
    FileParsingRequest,
    FileParsingResult
)


class FileParserService:
    """
    File Parser Service - Pure data processing for file parsing.
    
    Uses Public Works abstractions to parse files.
    Returns raw data only - no business logic.
    """
    
    def __init__(self, public_works: Optional[Any] = None):
        """
        Initialize File Parser Service.
        
        Args:
            public_works: Public Works Foundation Service (for accessing abstractions)
        """
        self.logger = get_logger(self.__class__.__name__)
        self.public_works = public_works
        
        # Get abstractions from Public Works
        self.file_storage_abstraction = None
        if public_works:
            self.file_storage_abstraction = public_works.get_file_storage_abstraction()
        
        # Parsing abstractions (will be accessed as needed)
        self._parsing_abstractions = {}
    
    async def parse_file(
        self,
        file_id: str,
        tenant_id: str,
        context: ExecutionContext,
        file_reference: Optional[str] = None,
        parsing_type: Optional[str] = None,
        parse_options: Optional[Dict[str, Any]] = None,
        copybook_reference: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Parse file using Public Works abstractions via State Surface.
        
        Architecture:
        - Uses State Surface file references (governed file access)
        - Routes to appropriate parsing abstraction based on file type
        - Stores parsed results in GCS
        - Registers parsed file reference in State Surface
        
        Args:
            file_id: File identifier
            tenant_id: Tenant identifier
            context: Execution context
            file_reference: Optional file reference (if not provided, constructs from file_id)
            parsing_type: Optional explicit parsing type (structured, unstructured, hybrid, workflow, SOP)
            parse_options: Optional parsing options
        
        Returns:
            Dict with parsed file data including parsed_file_id
        """
        self.logger.info(f"Parsing file: {file_id} for tenant: {tenant_id}")
        
        # Get file metadata - try multiple approaches
        file_metadata = None
        
        # First, try with provided file_reference
        if file_reference:
            file_metadata = await context.state_surface.get_file_metadata(file_reference)
        
        # If that fails, try to get file by UUID directly (from FileStorageAbstraction)
        if not file_metadata and self.file_storage_abstraction:
            try:
                file_metadata = await self.file_storage_abstraction.get_file_by_uuid(file_id)
                if file_metadata:
                    # Construct file_reference from actual file metadata
                    actual_session_id = file_metadata.get("session_id") or context.session_id
                    file_reference = f"file:{tenant_id}:{actual_session_id}:{file_id}"
                    self.logger.info(f"Found file by UUID, using session_id: {actual_session_id}")
            except Exception as e:
                self.logger.debug(f"File lookup by UUID failed: {e}")
        
        # If still not found, try constructing file_reference with context session_id as fallback
        if not file_metadata:
            if not file_reference:
                file_reference = f"file:{tenant_id}:{context.session_id}:{file_id}"
            file_metadata = await context.state_surface.get_file_metadata(file_reference)
        
        if not file_metadata:
            raise ValueError(f"File metadata not found for file_id: {file_id} (tried file_reference: {file_reference})")
        
        filename = file_metadata.get("filename", "")
        file_type_from_metadata = file_metadata.get("file_type", "unstructured")
        ui_name = file_metadata.get("ui_name", filename)
        
        # Determine parsing type
        if not parsing_type:
            parsing_type = self._determine_parsing_type(
                file_type=file_type_from_metadata,
                filename=filename,
                parse_options=parse_options or {}
            )
        
        self.logger.info(f"Parsing type determined: {parsing_type} for file: {filename}")
        
        # P4: Use unified document parsing surface (single protocol entry point)
        document_parsing = self.public_works.get_document_parsing() if self.public_works else None
        if not document_parsing:
            raise ValueError("No document parsing surface available (get_document_parsing)")
        
        # Create parsing request; options carry parsing_type/file_type for router
        parse_opts = dict(parse_options or {})
        parse_opts["parsing_type"] = parsing_type
        parse_opts["file_type"] = file_type_from_metadata
        parsing_request = FileParsingRequest(
            file_reference=file_reference,
            filename=filename,
            options=parse_opts,
            state_surface=context.state_surface,
            copybook_reference=copybook_reference
        )
        
        # Parse file via unified surface (router delegates to correct parser)
        parsing_result: FileParsingResult = await document_parsing.parse_file(parsing_request)
        
        if not parsing_result.success:
            raise RuntimeError(f"File parsing failed: {parsing_result.error}")
        
        # Store parsed result in GCS
        parsed_file_id = f"parsed_{file_id}_{generate_event_id()}"
        parsed_file_path = f"parsed/{tenant_id}/{parsed_file_id}.json"
        
        # Convert parsed result to JSON (ensure parsing_type is included)
        import json
        # Ensure parsing_type is set in result (may come from FileParsingResult.parsing_type or metadata)
        result_parsing_type = parsing_result.parsing_type or parsing_result.metadata.get("parsing_type") or parsing_type
        
        parsed_data_json = json.dumps({
            "parsed_file_id": parsed_file_id,
            "file_id": file_id,
            "parsing_type": result_parsing_type,  # Use explicit parsing_type from result
            "text_content": parsing_result.text_content,
            "structured_data": parsing_result.structured_data,
            "metadata": parsing_result.metadata,  # Already includes parsing_type and structure
            "validation_rules": parsing_result.validation_rules,
            "timestamp": parsing_result.timestamp
        }).encode('utf-8')
        
        # Upload parsed result to GCS
        if not self.file_storage_abstraction:
            raise RuntimeError("File storage abstraction not available")
        
        upload_result = await self.file_storage_abstraction.upload_file(
            file_path=parsed_file_path,
            file_data=parsed_data_json,
            metadata={
                "content_type": "application/json",
                "parsed_file_id": parsed_file_id,
                "file_id": file_id,
                "parsing_type": parsing_type
            }
        )
        
        if not upload_result.get("success"):
            raise RuntimeError(f"Failed to store parsed result: {upload_result.get('error')}")
        
        # Register parsed file reference in State Surface
        parsed_file_reference = f"parsed:{tenant_id}:{context.session_id}:{parsed_file_id}"
        await context.state_surface.store_file_reference(
            session_id=context.session_id,
            tenant_id=tenant_id,
            file_reference=parsed_file_reference,
            storage_location=parsed_file_path,
            filename=f"{ui_name}_parsed.json",
            metadata={
                "ui_name": f"Parsed: {ui_name}",
                "file_type": "parsed",
                "parsing_type": parsing_type,
                "file_id": file_id,
                "original_file_reference": file_reference,
                "size": len(parsed_data_json)
            }
        )
        
        self.logger.info(f"File parsed successfully: {file_id} -> {parsed_file_id} ({parsing_type})")
        
        # Include parsed data in result (for immediate use, also stored in parsed file)
        parsed_data = None
        if parsing_result.structured_data is not None:
            parsed_data = parsing_result.structured_data
        elif parsing_result.text_content:
            parsed_data = parsing_result.text_content
        
        # Calculate record count if structured_data is a list
        record_count = None
        if isinstance(parsed_data, list):
            record_count = len(parsed_data)
        elif isinstance(parsed_data, dict):
            # For dict, count might be in a 'records' or 'data' key, or count keys
            record_count = len(parsed_data)
        
        # Ensure parsing_type is set (may come from FileParsingResult.parsing_type or metadata)
        result_parsing_type = parsing_result.parsing_type or parsing_result.metadata.get("parsing_type") or parsing_type
        
        return {
            "parsed_file_id": parsed_file_id,
            "parsed_file_reference": parsed_file_reference,
            "file_id": file_id,
            "parsing_status": "completed",
            "parsing_type": result_parsing_type,  # Use explicit parsing_type from result
            "format": result_parsing_type,
            "parsed_data": parsed_data,  # Include parsed data in result
            "record_count": record_count,
            "metadata": {
                "parsing_type": result_parsing_type,  # Ensure metadata includes parsing_type
                "structure": parsing_result.metadata.get("structure", {}),  # Include structure for chunking
                "text_content_length": len(parsing_result.text_content) if parsing_result.text_content else 0,
                "has_structured_data": parsing_result.structured_data is not None,
                "has_validation_rules": parsing_result.validation_rules is not None,
                **{k: v for k, v in (parsing_result.metadata or {}).items() if k not in ["parsing_type", "structure"]}  # Include other metadata
            }
        }
    
    def _determine_parsing_type(
        self,
        file_type: str,
        filename: str,
        parse_options: Dict[str, Any]
    ) -> str:
        """
        Determine parsing type from file type and options.
        
        Args:
            file_type: File type from metadata
            filename: Original filename
            parse_options: Parsing options
        
        Returns:
            Parsing type: "structured", "unstructured", "hybrid", "workflow", or "sop"
        """
        # Check explicit type in options first
        if parse_options.get("parsing_type"):
            return parse_options["parsing_type"]
        
        # Check explicit flags
        if parse_options.get("is_workflow"):
            return "workflow"
        if parse_options.get("is_sop"):
            return "sop"
        if parse_options.get("is_data_model") or parse_options.get("data_model"):
            return "data_model"
        
        # Get file extension from filename
        file_ext = filename.split('.')[-1].lower() if '.' in filename else ""
        
        # Rule-based determination
        structured_types = ["xlsx", "xls", "csv", "bin", "binary"]
        unstructured_types = ["pdf", "docx", "doc", "txt", "text", "html", "htm"]
        hybrid_types = ["excel_with_text"]
        workflow_types = ["bpmn", "drawio"]
        sop_types = ["md", "markdown"]
        data_model_types = []  # JSON/YAML handled by file_type check below
        
        # Check for data_model first (JSON/YAML schemas for Insights pillar)
        if file_type == "data_model" or parse_options.get("is_data_model"):
            return "data_model"
        elif file_ext in ["json", "yaml", "yml"] and parse_options.get("is_data_model"):
            return "data_model"
        elif file_ext in workflow_types:
            return "workflow"
        elif file_ext in sop_types:
            return "sop"
        elif file_ext in structured_types or file_type in structured_types:
            return "structured"
        elif file_ext in unstructured_types or file_type in unstructured_types:
            return "unstructured"
        elif file_ext in hybrid_types or file_type in hybrid_types:
            return "hybrid"
        elif file_ext == "json" and parse_options.get("is_workflow"):
            return "workflow"
        else:
            # Default to unstructured
            return "unstructured"
    
    def _get_parsing_abstraction(
        self,
        parsing_type: str,
        file_type: str,
        parse_options: Optional[Dict[str, Any]] = None
    ) -> Optional[Any]:
        """
        Get appropriate parsing abstraction for parsing type.
        
        Args:
            parsing_type: Parsing type (structured, unstructured, hybrid, workflow, sop)
            file_type: File type (for specific format selection)
        
        Returns:
            Parsing abstraction instance or None
        """
        if not self.public_works:
            raise RuntimeError(
                "Public Works not wired; cannot get parsing abstraction. Platform contract §8A."
            )
        
        # Cache abstractions
        cache_key = f"{parsing_type}:{file_type}"
        if cache_key in self._parsing_abstractions:
            return self._parsing_abstractions[cache_key]
        
        abstraction = None
        
        # Route to appropriate abstraction based on parsing type and file type
        parse_opts = parse_options or {}
        if parsing_type == "unstructured":
            # Check if Kreuzberg is requested for PDFs
            if file_type in ["pdf"]:
                # Check if Kreuzberg is requested in parse_options
                if parse_opts.get("use_kreuzberg"):
                    abstraction = self.public_works.get_kreuzberg_processing_abstraction()
                else:
                    abstraction = self.public_works.get_pdf_processing_abstraction()
            elif file_type in ["docx", "doc"]:
                abstraction = self.public_works.get_word_processing_abstraction()
            elif file_type in ["txt", "text"]:
                abstraction = self.public_works.get_text_processing_abstraction()
            elif file_type in ["html", "htm"]:
                abstraction = self.public_works.get_html_processing_abstraction()
            elif file_type in ["png", "jpg", "jpeg", "gif", "bmp", "tiff"]:
                abstraction = self.public_works.get_image_processing_abstraction()
            else:
                # Default to text processing
                abstraction = self.public_works.get_text_processing_abstraction()
        
        elif parsing_type == "structured":
            if file_type in ["xlsx", "xls"]:
                abstraction = self.public_works.get_excel_processing_abstraction()
            elif file_type in ["csv"]:
                abstraction = self.public_works.get_csv_processing_abstraction()
            elif file_type in ["json"]:
                abstraction = self.public_works.get_json_processing_abstraction()
            elif file_type in ["bin", "binary"]:
                # Binary files require mainframe processing abstraction (needs copybook)
                abstraction = self.public_works.get_mainframe_processing_abstraction()
            else:
                # Default to CSV for structured
                abstraction = self.public_works.get_csv_processing_abstraction()
        
        elif parsing_type == "hybrid":
            # Hybrid files (PDFs with both tables and text)
            if file_type in ["pdf"]:
                # Check if Kreuzberg is requested (best for hybrid PDFs)
                parse_opts = parse_options or {}
                if parse_opts.get("use_kreuzberg"):
                    abstraction = self.public_works.get_kreuzberg_processing_abstraction()
                else:
                    # Use PDF processing (can extract both text and tables)
                    abstraction = self.public_works.get_pdf_processing_abstraction()
            else:
                # Hybrid files can use Excel processing (handles both structured and text)
                abstraction = self.public_works.get_excel_processing_abstraction()
        
        elif parsing_type == "workflow":
            # Workflow files (BPMN, DrawIO) - may need special handling
            # For now, use JSON processing if JSON, otherwise text
            if file_type in ["json"]:
                abstraction = self.public_works.get_json_processing_abstraction()
            else:
                abstraction = self.public_works.get_text_processing_abstraction()
        
        elif parsing_type == "sop":
            # SOP files (Markdown, etc.) - use text processing (will be enhanced with SOP-specific structure)
            abstraction = self.public_works.get_text_processing_abstraction()
        
        elif parsing_type == "data_model":
            # Data model files (JSON Schema, YAML schemas) - use data model processing
            abstraction = self.public_works.get_data_model_processing_abstraction()
            if not abstraction:
                # Fallback to JSON/YAML processing if data model abstraction not available
                if file_type in ["json"]:
                    abstraction = self.public_works.get_json_processing_abstraction()
                elif file_type in ["yaml", "yml"]:
                    # YAML processing may not exist, fallback to text
                    abstraction = self.public_works.get_text_processing_abstraction()
        
        if abstraction:
            self._parsing_abstractions[cache_key] = abstraction
        
        return abstraction
    
    async def get_parsed_file(
        self,
        parsed_file_id: str,
        tenant_id: str,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Get parsed file data via Content Realm (governed access).
        
        ARCHITECTURAL PRINCIPLE: This is the correct way to retrieve parsed files.
        - Runtime records reality (doesn't retrieve files)
        - Smart City governs access (policy evaluation happens here)
        - Content Realm retrieves data (this method)
        - Agents never retrieve files directly
        
        Args:
            parsed_file_id: Parsed file identifier
            tenant_id: Tenant identifier
            context: Execution context
        
        Returns:
            Dict with parsed file data:
            {
                "parsed_file_id": str,
                "parsed_content": Any,  # Actual parsed content (dict, list, str, etc.)
                "metadata": Dict[str, Any]
            }
        """
        self.logger.info(f"Getting parsed file via Content Realm: {parsed_file_id} for tenant: {tenant_id}")
        
        if not self.public_works:
            raise ValueError("Public Works required for file retrieval")
        
        if not self.file_storage_abstraction:
            raise ValueError("FileStorageAbstraction not available")
        
        try:
            # CORRECT 2-STEP RETRIEVAL PATTERN:
            # Step 1: Get storage_location from State Surface (has reference) or Supabase (has lineage metadata)
            # Step 2: Download actual content from GCS using storage_location
            
            storage_location = None
            
            # Step 1a: Try State Surface first (has reference with storage_location)
            if context.state_surface:
                try:
                    parsed_file_reference = f"parsed:{tenant_id}:{context.session_id}:{parsed_file_id}"
                    state_metadata = await context.state_surface.get_file_metadata(parsed_file_reference)
                    if state_metadata:
                        storage_location = state_metadata.get("storage_location")
                        self.logger.debug(f"Found storage_location in State Surface: {storage_location}")
                except Exception as state_error:
                    self.logger.debug(f"State Surface lookup failed: {state_error}")
            
            # Step 1b: Fallback to Supabase lineage metadata (has gcs_path, not content)
            if not storage_location:
                try:
                    # Query Supabase for lineage metadata (metadata only, not content)
                    registry = getattr(self.public_works, 'registry_abstraction', None)
                    if registry:
                        # Query parsed_results table for gcs_path
                        lineage_query = await registry.query_records(
                            table="parsed_results",
                            filters={"parsed_result_id": parsed_file_id, "tenant_id": tenant_id},
                            columns=["gcs_path"]
                        )
                        if lineage_query and len(lineage_query) > 0:
                            gcs_path = lineage_query[0].get("gcs_path")
                            # Convert gcs_path to storage_location format if needed
                            if gcs_path:
                                # gcs_path might be "tenant/{tenant_id}/parsed/{parsed_file_id}.jsonl"
                                # storage_location should be "parsed/{tenant_id}/{parsed_file_id}.json"
                                # Try to extract or use as-is
                                storage_location = gcs_path.replace("tenant/", "").replace(".jsonl", ".json")
                                self.logger.debug(f"Found gcs_path in Supabase lineage: {storage_location}")
                except Exception as lineage_error:
                    self.logger.debug(f"Supabase lineage lookup failed: {lineage_error}")
            
            if not storage_location:
                raise ValueError(
                    f"Storage location not found for parsed_file_id: {parsed_file_id}. "
                    f"Checked State Surface and Supabase lineage."
                )
            
            # Step 2: Download actual content from GCS
            parsed_content_json_bytes = await self.file_storage_abstraction.download_file(storage_location)
            if not parsed_content_json_bytes:
                raise ValueError(f"Parsed file content not found at storage_location: {storage_location}")
            
            # Parse JSON content
            import json
            parsed_content_json = json.loads(parsed_content_json_bytes.decode('utf-8'))
            
            # Extract parsed content (structured_data or text_content)
            parsed_content = parsed_content_json.get("structured_data") or parsed_content_json.get("text_content")
            
            # Return parsed content with metadata
            return {
                "parsed_file_id": parsed_file_id,
                "parsed_content": parsed_content,
                "metadata": parsed_content_json.get("metadata", {})
            }
            
        except Exception as e:
            self.logger.error(
                f"Failed to retrieve parsed file {parsed_file_id} via Content Realm: {e}",
                exc_info=True
            )
            raise
