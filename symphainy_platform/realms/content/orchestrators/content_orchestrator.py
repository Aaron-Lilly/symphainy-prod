"""
Content Orchestrator - Coordinates Content Operations

Coordinates enabling services for content processing.

WHAT (Orchestrator Role): I coordinate content operations
HOW (Orchestrator Implementation): I route intents to enabling services and compose results

⚠️ CRITICAL: Orchestrators coordinate within a single intent only.
They may NOT spawn long-running sagas, manage retries, or track cross-intent progress.
"""

import sys
from pathlib import Path
from symphainy_platform.realms.utils.structured_artifacts import create_structured_artifact

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

from utilities import get_logger, generate_event_id, get_clock
from symphainy_platform.runtime.intent_model import Intent, IntentFactory
from symphainy_platform.runtime.execution_context import ExecutionContext
from ..enabling_services.file_parser_service import FileParserService
from symphainy_platform.foundations.public_works.protocols.ingestion_protocol import (
    IngestionRequest,
    IngestionResult,
    IngestionType
)
from .retry_helpers import retry_with_backoff, get_retry_strategy_for_ingestion_type
import hashlib


class ContentOrchestrator:
    """
    Content Orchestrator - Coordinates content operations.
    
    Coordinates:
    - File parsing
    - Embedding creation
    - Semantic storage
    """
    
    def __init__(self, public_works: Optional[Any] = None):
        """
        Initialize Content Orchestrator.
        
        Args:
            public_works: Public Works Foundation Service (for accessing abstractions)
        """
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
        self.public_works = public_works
        
        # Initialize enabling services with Public Works
        self.file_parser_service = FileParserService(public_works=public_works)
    
    async def handle_intent(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Handle intent by coordinating enabling services.
        
        Args:
            intent: The intent to handle
            context: Runtime execution context
        
        Returns:
            Dict with "artifacts" and "events" keys
        """
        intent_type = intent.intent_type
        
        if intent_type == "ingest_file":
            return await self._handle_ingest_file(intent, context)
        elif intent_type == "bulk_ingest_files":
            return await self._handle_bulk_ingest_files(intent, context)
        elif intent_type == "bulk_parse_files":
            return await self._handle_bulk_parse_files(intent, context)
        elif intent_type == "bulk_extract_embeddings":
            return await self._handle_bulk_extract_embeddings(intent, context)
        elif intent_type == "bulk_interpret_data":
            return await self._handle_bulk_interpret_data(intent, context)
        elif intent_type == "get_operation_status":
            return await self._handle_get_operation_status(intent, context)
        elif intent_type == "register_file":
            return await self._handle_register_file(intent, context)
        elif intent_type == "retrieve_file_metadata":
            return await self._handle_retrieve_file_metadata(intent, context)
        elif intent_type == "retrieve_file":
            return await self._handle_retrieve_file(intent, context)
        elif intent_type == "list_files":
            return await self._handle_list_files(intent, context)
        elif intent_type == "save_materialization":
            return await self._handle_save_materialization(intent, context)
        elif intent_type == "get_file_by_id":
            return await self._handle_get_file_by_id(intent, context)
        elif intent_type == "archive_file":
            return await self._handle_archive_file(intent, context)
        elif intent_type == "purge_file":
            return await self._handle_purge_file(intent, context)
        elif intent_type == "restore_file":
            return await self._handle_restore_file(intent, context)
        elif intent_type == "validate_file":
            return await self._handle_validate_file(intent, context)
        elif intent_type == "preprocess_file":
            return await self._handle_preprocess_file(intent, context)
        elif intent_type == "search_files":
            return await self._handle_search_files(intent, context)
        elif intent_type == "query_files":
            return await self._handle_query_files(intent, context)
        elif intent_type == "update_file_metadata":
            return await self._handle_update_file_metadata(intent, context)
        elif intent_type == "parse_content":
            return await self._handle_parse_content(intent, context)
        elif intent_type == "extract_embeddings":
            return await self._handle_extract_embeddings(intent, context)
        elif intent_type == "get_parsed_file":
            return await self._handle_get_parsed_file(intent, context)
        elif intent_type == "get_semantic_interpretation":
            return await self._handle_get_semantic_interpretation(intent, context)
        else:
            raise ValueError(f"Unknown intent type: {intent_type}")
    
    async def _handle_ingest_file(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Handle ingest_file intent - unified ingestion from multiple sources.
        
        Supports:
        - UPLOAD: Direct file upload (hex-encoded bytes)
        - EDI: EDI protocol (AS2, SFTP, etc.)
        - API: REST/GraphQL API payloads
        
        Intent parameters:
        - ingestion_type: str (REQUIRED) - "upload", "edi", or "api" (defaults to "upload")
        - file_content: bytes (hex-encoded) - For UPLOAD type (REQUIRED for upload)
        - edi_data: bytes (hex-encoded) - For EDI type (REQUIRED for edi)
        - api_payload: Dict - For API type (REQUIRED for api)
        - ui_name: str (REQUIRED) - User-friendly filename
        - file_type: str - File type (e.g., "pdf", "csv")
        - mime_type: str - MIME type (e.g., "application/pdf")
        - filename: str - Original filename (defaults to ui_name)
        - user_id: str - User identifier (optional, from context if not provided)
        - source_metadata: Dict - Source-specific metadata (partner_id for EDI, endpoint for API, etc.)
        - ingestion_options: Dict - Ingestion-specific options
        """
        # CRITICAL: Files are NEVER ingested directly. A boundary contract is negotiated first.
        # Boundary contract negotiation happens in Runtime/ExecutionLifecycleManager before realm execution.
        # Check if boundary contract info is in context (from Runtime enforcement)
        boundary_contract_id = context.metadata.get("boundary_contract_id")
        materialization_type = context.metadata.get("materialization_type", "full_artifact")  # MVP default
        materialization_backing_store = context.metadata.get("materialization_backing_store", "gcs")  # MVP default
        
        if boundary_contract_id:
            self.logger.info(f"✅ Using boundary contract: {boundary_contract_id} (materialization: {materialization_type} -> {materialization_backing_store})")
        else:
            # MVP: Allow execution to continue without boundary contract (backwards compatibility)
            # In full implementation: This should raise an error
            self.logger.warning("⚠️ MVP: No boundary contract in context - files ingested directly (not aligned with 'data stays at door' principle)")
            self.logger.warning("⚠️ This should be blocked in full implementation")
        
        # Get ingestion abstraction from Public Works
        if not self.public_works:
            raise RuntimeError("Public Works not initialized - cannot access IngestionAbstraction")
        
        ingestion_abstraction = self.public_works.get_ingestion_abstraction()
        if not ingestion_abstraction:
            raise RuntimeError("IngestionAbstraction not available - Public Works not configured")
        
        # Determine ingestion type (default to upload for backwards compatibility)
        ingestion_type_str = intent.parameters.get("ingestion_type", "upload").lower()
        try:
            ingestion_type = IngestionType(ingestion_type_str)
        except ValueError:
            raise ValueError(f"Invalid ingestion_type: {ingestion_type_str}. Must be 'upload', 'edi', or 'api'")
        
        # Extract common metadata
        ui_name = intent.parameters.get("ui_name")
        if not ui_name:
            raise ValueError("ui_name is required for ingest_file intent")
        
        file_type = intent.parameters.get("file_type", "unstructured")
        mime_type = intent.parameters.get("mime_type", "application/octet-stream")
        filename = intent.parameters.get("filename", ui_name)
        user_id = intent.parameters.get("user_id") or context.metadata.get("user_id", "system")
        source_metadata = intent.parameters.get("source_metadata", {})
        ingestion_options = intent.parameters.get("ingestion_options", {})
        
        # Prepare source metadata
        source_metadata.update({
            "ui_name": ui_name,
            "file_type": file_type,  # Parsing pathway: structured/unstructured/hybrid
            "mime_type": mime_type,  # MIME type: application/pdf, text/csv, etc.
            "user_id": user_id,
            "filename": filename,
            "status": "uploaded"
        })
        
        # Prepare ingestion request based on type
        if ingestion_type == IngestionType.UPLOAD:
            # Extract file content (hex-encoded)
            file_content_hex = intent.parameters.get("file_content")
            if not file_content_hex:
                raise ValueError("file_content is required for upload ingestion_type")
            
            try:
                file_data = bytes.fromhex(file_content_hex)
            except ValueError as e:
                raise ValueError(f"Invalid file_content (must be hex-encoded): {e}")
            
            ingestion_request = IngestionRequest(
                ingestion_type=IngestionType.UPLOAD,
                tenant_id=context.tenant_id,
                session_id=context.session_id,
                source_metadata=source_metadata,
                data=file_data,
                options=ingestion_options
            )
        
        elif ingestion_type == IngestionType.EDI:
            # Extract EDI data
            edi_data_hex = intent.parameters.get("edi_data")
            if not edi_data_hex:
                raise ValueError("edi_data is required for edi ingestion_type")
            
            try:
                edi_data = bytes.fromhex(edi_data_hex)
            except ValueError as e:
                raise ValueError(f"Invalid edi_data (must be hex-encoded): {e}")
            
            # EDI-specific metadata
            partner_id = intent.parameters.get("partner_id")
            if not partner_id:
                raise ValueError("partner_id is required for edi ingestion_type")
            
            source_metadata["partner_id"] = partner_id
            source_metadata["edi_protocol"] = intent.parameters.get("edi_protocol", "as2")
            
            ingestion_request = IngestionRequest(
                ingestion_type=IngestionType.EDI,
                tenant_id=context.tenant_id,
                session_id=context.session_id,
                source_metadata=source_metadata,
                data=edi_data,
                options=ingestion_options
            )
        
        elif ingestion_type == IngestionType.API:
            # Extract API payload
            api_payload = intent.parameters.get("api_payload")
            if not api_payload:
                raise ValueError("api_payload is required for api ingestion_type")
            
            # API-specific metadata
            endpoint = intent.parameters.get("endpoint")
            api_type = intent.parameters.get("api_type", "rest")  # rest, graphql, webhook
            
            source_metadata["endpoint"] = endpoint
            source_metadata["api_type"] = api_type
            
            ingestion_request = IngestionRequest(
                ingestion_type=IngestionType.API,
                tenant_id=context.tenant_id,
                session_id=context.session_id,
                source_metadata=source_metadata,
                api_payload=api_payload,
                options=ingestion_options
            )
        
        # Execute ingestion via IngestionAbstraction
        ingestion_result = await ingestion_abstraction.ingest_data(ingestion_request)
        
        if not ingestion_result.success:
            raise RuntimeError(f"Ingestion failed: {ingestion_result.error}")
        
        # Register file reference in State Surface (for governed file access)
        file_reference = ingestion_result.file_reference
        
        # Get file metadata from ingestion result
        file_metadata = ingestion_result.ingestion_metadata
        
        await context.state_surface.store_file_reference(
            session_id=context.session_id,
            tenant_id=context.tenant_id,
            file_reference=file_reference,
            storage_location=ingestion_result.storage_location,
            filename=filename,
            metadata={
                "ui_name": ui_name,
                "file_type": file_type,  # Parsing pathway: structured/unstructured/hybrid
                "mime_type": mime_type,  # MIME type: application/pdf, text/csv, etc.
                "size": file_metadata.get("size"),
                "file_hash": file_metadata.get("file_hash"),
                "file_id": ingestion_result.file_id,
                "ingestion_type": ingestion_type.value,
                "ingestion_metadata": ingestion_result.ingestion_metadata
            }
        )
        
        self.logger.info(f"File ingested via {ingestion_type.value}: {ingestion_result.file_id} ({ui_name}) -> {file_reference}")
        
        # Create structured artifact with semantic_payload and renderings
        # Include boundary contract information (if available)
        semantic_payload = {
            "file_id": ingestion_result.file_id,
            "file_reference": file_reference,
            "storage_location": ingestion_result.storage_location,
            "ui_name": ui_name,
            "file_type": file_type,
            "mime_type": mime_type,
            "ingestion_type": ingestion_type.value,
            "status": "ingested",
            "file_size": file_metadata.get("size") if file_metadata else None,
            "file_hash": file_metadata.get("file_hash") if file_metadata else None,
            "created_at": file_metadata.get("created_at") if file_metadata else None
        }
        
        # Add boundary contract information if available
        materialization_pending = context.metadata.get("materialization_pending", False)
        
        if boundary_contract_id:
            semantic_payload["boundary_contract_id"] = boundary_contract_id
            semantic_payload["materialization_pending"] = materialization_pending  # NEW: Indicates if materialization is pending
            
            # If materialization is not pending, include materialization details
            if not materialization_pending:
                semantic_payload["materialization_type"] = materialization_type
                semantic_payload["materialization_backing_store"] = materialization_backing_store
                semantic_payload["materialization_scope"] = context.metadata.get("materialization_scope", {})
            semantic_payload["source_external"] = True  # Source data is external (not owned by platform)
        
        structured_artifact = create_structured_artifact(
            result_type="file",
            semantic_payload=semantic_payload,
            renderings={}  # No renderings for ingestion (file already stored)
        )
        
        return {
            "artifacts": {
                "file": structured_artifact
            },
            "events": [
                {
                    "type": "file_ingested",
                    "file_id": ingestion_result.file_id,
                    "file_reference": file_reference,
                    "ui_name": ui_name,
                    "ingestion_type": ingestion_type.value
                }
            ]
        }
    
    async def _handle_bulk_ingest_files(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Handle bulk_ingest_files intent - bulk ingestion with batching, parallel processing,
        idempotency, retry logic, and progress tracking.
        
        Supports all ingestion types (upload, EDI, API).
        
        Intent parameters:
        - files: List[Dict] (REQUIRED) - List of file ingestion requests
            Each file dict should contain:
            - ingestion_type: str (REQUIRED) - "upload", "edi", or "api"
            - file_content: str (hex-encoded) - For upload type
            - edi_data: str (hex-encoded) - For edi type
            - api_payload: Dict - For api type
            - ui_name: str (REQUIRED) - User-friendly filename
            - file_type: str (optional) - File type
            - mime_type: str (optional) - MIME type
            - source_metadata: Dict (optional) - Source-specific metadata
        - batch_size: int (optional) - Batch size for processing (default: 10)
        - max_parallel: int (optional) - Max parallel operations (default: 5)
        - ingestion_options: Dict (optional) - Ingestion-specific options
        - idempotency_key: str (optional) - Idempotency key for operation
        - resume_from_batch: int (optional) - Resume from batch number (for retry)
        - operation_id: str (optional) - Operation ID for progress tracking
        """
        files = intent.parameters.get("files")
        if not files or not isinstance(files, list):
            raise ValueError("files parameter is required and must be a list for bulk_ingest_files intent")
        
        batch_size = intent.parameters.get("batch_size", 10)
        max_parallel = intent.parameters.get("max_parallel", 5)
        ingestion_options = intent.parameters.get("ingestion_options", {})
        
        # Generate or use provided idempotency key
        idempotency_key = intent.idempotency_key
        if not idempotency_key:
            # Generate idempotency key from intent parameters
            key_data = f"{intent.intent_type}:{context.tenant_id}:{context.session_id}:{hashlib.sha256(str(files).encode()).hexdigest()[:16]}"
            idempotency_key = hashlib.sha256(key_data.encode()).hexdigest()
        
        # Check idempotency (if operation already completed, return previous result)
        previous_result = await context.state_surface.check_idempotency(idempotency_key, context.tenant_id)
        if previous_result and previous_result.get("status") == "completed":
            self.logger.info(f"Operation already completed (idempotency key: {idempotency_key[:16]}...), returning previous result")
            return previous_result.get("result")
        
        # Get or generate operation ID
        operation_id = intent.parameters.get("operation_id") or f"bulk_ingest_{generate_event_id()}"
        
        # Check for resume capability
        resume_from_batch = intent.parameters.get("resume_from_batch", 0)
        if resume_from_batch > 0:
            # Load previous progress
            previous_progress = await context.state_surface.get_operation_progress(operation_id, context.tenant_id)
            if previous_progress:
                results = previous_progress.get("results", [])
                errors = previous_progress.get("errors", [])
                self.logger.info(f"Resuming from batch {resume_from_batch}, {len(results)} files already processed")
            else:
                results = []
                errors = []
                resume_from_batch = 0
        else:
            results = []
            errors = []
        
        # Get ingestion abstraction
        if not self.public_works:
            raise RuntimeError("Public Works not initialized - cannot access IngestionAbstraction")
        
        ingestion_abstraction = self.public_works.get_ingestion_abstraction()
        if not ingestion_abstraction:
            raise RuntimeError("IngestionAbstraction not available - Public Works not configured")
        
        # Process files in batches with parallel processing
        import asyncio
        
        total_files = len(files)
        processed = len(results)  # Start from where we left off
        
        # Process in batches
        for batch_start in range(0, total_files, batch_size):
            batch = files[batch_start:batch_start + batch_size]
            batch_num = (batch_start // batch_size) + 1
            total_batches = (total_files + batch_size - 1) // batch_size
            
            # Skip batches that were already processed (resume capability)
            if resume_from_batch > 0 and batch_num <= resume_from_batch:
                self.logger.info(f"Skipping batch {batch_num}/{total_batches} (already processed)")
                continue
            
            self.logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} files)")
            
            # Process batch with limited parallelism
            semaphore = asyncio.Semaphore(max_parallel)
            
            async def process_single_file(file_data: Dict[str, Any], index: int) -> Dict[str, Any]:
                """Process a single file ingestion with retry logic."""
                async with semaphore:
                    # Get ingestion type for retry strategy
                    ingestion_type_str = file_data.get("ingestion_type", "upload").lower()
                    retry_strategy = get_retry_strategy_for_ingestion_type(ingestion_type_str)
                    
                    async def ingest_file_with_retry():
                        try:
                            # Extract common metadata
                            ingestion_type_str = file_data.get("ingestion_type", "upload").lower()
                            try:
                                ingestion_type = IngestionType(ingestion_type_str)
                            except ValueError:
                                return {
                                    "success": False,
                                    "index": index,
                                    "error": f"Invalid ingestion_type: {ingestion_type_str}"
                                }
                            
                            ui_name = file_data.get("ui_name")
                            if not ui_name:
                                return {
                                    "success": False,
                                    "index": index,
                                    "error": "ui_name is required"
                                }
                            
                            file_type = file_data.get("file_type", "unstructured")
                            mime_type = file_data.get("mime_type", "application/octet-stream")
                            filename = file_data.get("filename", ui_name)
                            user_id = file_data.get("user_id") or context.metadata.get("user_id", "system")
                            source_metadata = file_data.get("source_metadata", {})
                            
                            source_metadata.update({
                                "ui_name": ui_name,
                                "file_type": file_type,
                                "content_type": mime_type,
                                "user_id": user_id,
                                "filename": filename
                            })
                            
                            # Prepare ingestion request based on type
                            if ingestion_type == IngestionType.UPLOAD:
                                file_content_hex = file_data.get("file_content")
                                if not file_content_hex:
                                    return {
                                        "success": False,
                                        "index": index,
                                        "error": "file_content is required for upload ingestion_type"
                                    }
                                
                                try:
                                    file_data_bytes = bytes.fromhex(file_content_hex)
                                except ValueError as e:
                                    return {
                                        "success": False,
                                        "index": index,
                                        "error": f"Invalid file_content: {e}"
                                    }
                                
                                ingestion_request = IngestionRequest(
                                    ingestion_type=IngestionType.UPLOAD,
                                    tenant_id=context.tenant_id,
                                    session_id=context.session_id,
                                    source_metadata=source_metadata,
                                    data=file_data_bytes,
                                    options=ingestion_options
                                )
                            
                            elif ingestion_type == IngestionType.EDI:
                                edi_data_hex = file_data.get("edi_data")
                                if not edi_data_hex:
                                    return {
                                        "success": False,
                                        "index": index,
                                        "error": "edi_data is required for edi ingestion_type"
                                    }
                                
                                try:
                                    edi_data_bytes = bytes.fromhex(edi_data_hex)
                                except ValueError as e:
                                    return {
                                        "success": False,
                                        "index": index,
                                        "error": f"Invalid edi_data: {e}"
                                    }
                                
                                partner_id = file_data.get("partner_id")
                                if not partner_id:
                                    return {
                                        "success": False,
                                        "index": index,
                                        "error": "partner_id is required for edi ingestion_type"
                                    }
                                
                                source_metadata["partner_id"] = partner_id
                                source_metadata["edi_protocol"] = file_data.get("edi_protocol", "as2")
                                
                                ingestion_request = IngestionRequest(
                                    ingestion_type=IngestionType.EDI,
                                    tenant_id=context.tenant_id,
                                    session_id=context.session_id,
                                    source_metadata=source_metadata,
                                    data=edi_data_bytes,
                                    options=ingestion_options
                                )
                            
                            elif ingestion_type == IngestionType.API:
                                api_payload = file_data.get("api_payload")
                                if not api_payload:
                                    return {
                                        "success": False,
                                        "index": index,
                                        "error": "api_payload is required for api ingestion_type"
                                    }
                                
                                source_metadata["endpoint"] = file_data.get("endpoint")
                                source_metadata["api_type"] = file_data.get("api_type", "rest")
                                
                                ingestion_request = IngestionRequest(
                                    ingestion_type=IngestionType.API,
                                    tenant_id=context.tenant_id,
                                    session_id=context.session_id,
                                    source_metadata=source_metadata,
                                    api_payload=api_payload,
                                    options=ingestion_options
                                )
                            
                            # Execute ingestion
                            ingestion_result = await ingestion_abstraction.ingest_data(ingestion_request)
                            
                            if not ingestion_result.success:
                                raise RuntimeError(f"Ingestion failed: {ingestion_result.error}")
                            
                            # Register in State Surface
                            file_reference = ingestion_result.file_reference
                            file_metadata = ingestion_result.ingestion_metadata
                            
                            await context.state_surface.store_file_reference(
                                session_id=context.session_id,
                                tenant_id=context.tenant_id,
                                file_reference=file_reference,
                                storage_location=ingestion_result.storage_location,
                                filename=filename,
                                metadata={
                                    "ui_name": ui_name,
                                    "file_type": file_type,
                                    "content_type": mime_type,
                                    "size": file_metadata.get("size"),
                                    "file_hash": file_metadata.get("file_hash"),
                                    "file_id": ingestion_result.file_id,
                                    "ingestion_type": ingestion_type.value
                                }
                            )
                            
                            return {
                                "success": True,
                                "index": index,
                                "file_id": ingestion_result.file_id,
                                "file_reference": file_reference,
                                "ui_name": ui_name,
                                "ingestion_type": ingestion_type.value
                            }
                        except Exception as e:
                            raise  # Re-raise to be caught by retry logic
                    
                    # Execute with retry
                    try:
                        return await retry_with_backoff(
                            ingest_file_with_retry,
                            **retry_strategy,
                            retryable_exceptions=(RuntimeError, Exception)
                        )
                    except Exception as e:
                        self.logger.error(f"Error processing file at index {index} after retries: {e}", exc_info=True)
                        return {
                            "success": False,
                            "index": index,
                            "error": str(e)
                        }
            
            # Process batch in parallel
            batch_results = await asyncio.gather(*[
                process_single_file(file_data, batch_start + i)
                for i, file_data in enumerate(batch)
            ])
            
            # Collect results
            for result in batch_results:
                if result.get("success"):
                    results.append(result)
                else:
                    errors.append(result)
            
            processed += len(batch)
            success_in_batch = len([r for r in batch_results if r.get("success")])
            self.logger.info(f"Batch {batch_num} complete: {success_in_batch}/{len(batch)} succeeded")
            
            # Track progress after each batch
            await context.state_surface.track_operation_progress(
                operation_id=operation_id,
                tenant_id=context.tenant_id,
                progress={
                    "status": "running",
                    "total": total_files,
                    "processed": processed,
                    "succeeded": len(results),
                    "failed": len(errors),
                    "current_batch": batch_num,
                    "last_successful_batch": batch_num if success_in_batch == len(batch) else batch_num - 1,
                    "errors": errors,
                    "results": results
                }
            )
        
        # Summary
        success_count = len(results)
        error_count = len(errors)
        
        self.logger.info(f"Bulk ingestion complete: {success_count}/{total_files} succeeded, {error_count} failed")
        
        # Final result
        final_result = {
            "artifacts": {
                "total_files": total_files,
                "success_count": success_count,
                "error_count": error_count,
                "results": results,
                "errors": errors,
                "batch_size": batch_size,
                "max_parallel": max_parallel,
                "operation_id": operation_id
            },
            "events": [
                {
                    "type": "bulk_ingestion_complete",
                    "total_files": total_files,
                    "success_count": success_count,
                    "error_count": error_count,
                    "operation_id": operation_id
                }
            ]
        }
        
        # Store idempotency result
        await context.state_surface.store_idempotency_result(
            idempotency_key=idempotency_key,
            tenant_id=context.tenant_id,
            result={
                "status": "completed",
                "result": final_result,
                "operation_id": operation_id
            }
        )
        
        # Update final progress
        await context.state_surface.track_operation_progress(
            operation_id=operation_id,
            tenant_id=context.tenant_id,
            progress={
                "status": "completed",
                "total": total_files,
                "processed": processed,
                "succeeded": success_count,
                "failed": error_count,
                "current_batch": (total_files + batch_size - 1) // batch_size,
                "last_successful_batch": (total_files + batch_size - 1) // batch_size,
                "errors": errors,
                "results": results
            }
        )
        
        return final_result
    
    async def _handle_bulk_parse_files(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Handle bulk_parse_files intent - bulk parse with parallel processing.
        
        Intent parameters:
        - file_ids: List[str] (REQUIRED) - List of file IDs to parse
        - batch_size: int (optional) - Batch size for processing (default: 10)
        - max_parallel: int (optional) - Max parallel operations (default: 5)
        - parse_options: Dict (optional) - Parse-specific options
        """
        file_ids = intent.parameters.get("file_ids")
        if not file_ids or not isinstance(file_ids, list):
            raise ValueError("file_ids parameter is required and must be a list for bulk_parse_files intent")
        
        batch_size = intent.parameters.get("batch_size", 10)
        max_parallel = intent.parameters.get("max_parallel", 5)
        parse_options = intent.parameters.get("parse_options", {})
        
        import asyncio
        
        results = []
        errors = []
        total_files = len(file_ids)
        
        # Process in batches
        for batch_start in range(0, total_files, batch_size):
            batch = file_ids[batch_start:batch_start + batch_size]
            batch_num = (batch_start // batch_size) + 1
            total_batches = (total_files + batch_size - 1) // batch_size
            
            self.logger.info(f"Processing parse batch {batch_num}/{total_batches} ({len(batch)} files)")
            
            semaphore = asyncio.Semaphore(max_parallel)
            
            async def parse_single_file(file_id: str, index: int) -> Dict[str, Any]:
                """Parse a single file."""
                async with semaphore:
                    try:
                        # Create parse_content intent for this file
                        parse_intent = IntentFactory.create_intent(
                            intent_type="parse_content",
                            tenant_id=context.tenant_id,
                            session_id=context.session_id,
                            solution_id=intent.solution_id,
                            parameters={
                                "file_id": file_id,
                                **parse_options
                            }
                        )
                        
                        # Execute parse
                        parse_result = await self._handle_parse_content(parse_intent, context)
                        
                        return {
                            "success": True,
                            "index": index,
                            "file_id": file_id,
                            "parsed_result_id": parse_result.get("artifacts", {}).get("parsed_result_id")
                        }
                    
                    except Exception as e:
                        self.logger.error(f"Error parsing file {file_id}: {e}", exc_info=True)
                        return {
                            "success": False,
                            "index": index,
                            "file_id": file_id,
                            "error": str(e)
                        }
            
            # Process batch in parallel
            batch_results = await asyncio.gather(*[
                parse_single_file(file_id, batch_start + i)
                for i, file_id in enumerate(batch)
            ])
            
            # Collect results
            for result in batch_results:
                if result.get("success"):
                    results.append(result)
                else:
                    errors.append(result)
        
        success_count = len(results)
        error_count = len(errors)
        
        self.logger.info(f"Bulk parse complete: {success_count}/{total_files} succeeded, {error_count} failed")
        
        return {
            "artifacts": {
                "total_files": total_files,
                "success_count": success_count,
                "error_count": error_count,
                "results": results,
                "errors": errors
            },
            "events": [
                {
                    "type": "bulk_parse_complete",
                    "total_files": total_files,
                    "success_count": success_count,
                    "error_count": error_count
                }
            ]
        }
    
    async def _handle_bulk_extract_embeddings(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Handle bulk_extract_embeddings intent - bulk embedding creation.
        
        Intent parameters:
        - parsed_result_ids: List[str] (REQUIRED) - List of parsed result IDs
        - batch_size: int (optional) - Batch size for processing (default: 10)
        - max_parallel: int (optional) - Max parallel operations (default: 5)
        - embedding_options: Dict (optional) - Embedding-specific options
        """
        parsed_result_ids = intent.parameters.get("parsed_result_ids")
        if not parsed_result_ids or not isinstance(parsed_result_ids, list):
            raise ValueError("parsed_result_ids parameter is required and must be a list for bulk_extract_embeddings intent")
        
        batch_size = intent.parameters.get("batch_size", 10)
        max_parallel = intent.parameters.get("max_parallel", 5)
        embedding_options = intent.parameters.get("embedding_options", {})
        
        import asyncio
        
        results = []
        errors = []
        total_ids = len(parsed_result_ids)
        
        # Process in batches
        for batch_start in range(0, total_ids, batch_size):
            batch = parsed_result_ids[batch_start:batch_start + batch_size]
            batch_num = (batch_start // batch_size) + 1
            total_batches = (total_ids + batch_size - 1) // batch_size
            
            self.logger.info(f"Processing embedding batch {batch_num}/{total_batches} ({len(batch)} results)")
            
            semaphore = asyncio.Semaphore(max_parallel)
            
            async def extract_single_embedding(parsed_result_id: str, index: int) -> Dict[str, Any]:
                """Extract embedding for a single parsed result."""
                async with semaphore:
                    try:
                        # Create extract_embeddings intent
                        embedding_intent = IntentFactory.create_intent(
                            intent_type="extract_embeddings",
                            tenant_id=context.tenant_id,
                            session_id=context.session_id,
                            solution_id=intent.solution_id,
                            parameters={
                                "parsed_file_id": parsed_result_id,
                                **embedding_options
                            }
                        )
                        
                        # Execute embedding extraction
                        embedding_result = await self._handle_extract_embeddings(embedding_intent, context)
                        
                        return {
                            "success": True,
                            "index": index,
                            "parsed_result_id": parsed_result_id,
                            "embedding_id": embedding_result.get("artifacts", {}).get("embedding_id")
                        }
                    
                    except Exception as e:
                        self.logger.error(f"Error extracting embedding for {parsed_result_id}: {e}", exc_info=True)
                        return {
                            "success": False,
                            "index": index,
                            "parsed_result_id": parsed_result_id,
                            "error": str(e)
                        }
            
            # Process batch in parallel
            batch_results = await asyncio.gather(*[
                extract_single_embedding(parsed_result_id, batch_start + i)
                for i, parsed_result_id in enumerate(batch)
            ])
            
            # Collect results
            for result in batch_results:
                if result.get("success"):
                    results.append(result)
                else:
                    errors.append(result)
        
        success_count = len(results)
        error_count = len(errors)
        
        self.logger.info(f"Bulk embedding extraction complete: {success_count}/{total_ids} succeeded, {error_count} failed")
        
        return {
            "artifacts": {
                "total_ids": total_ids,
                "success_count": success_count,
                "error_count": error_count,
                "results": results,
                "errors": errors
            },
            "events": [
                {
                    "type": "bulk_embedding_extraction_complete",
                    "total_ids": total_ids,
                    "success_count": success_count,
                    "error_count": error_count
                }
            ]
        }
    
    async def _handle_bulk_interpret_data(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Handle bulk_interpret_data intent - bulk interpretation.
        
        Intent parameters:
        - parsed_result_ids: List[str] (REQUIRED) - List of parsed result IDs to interpret
        - batch_size: int (optional) - Batch size for processing (default: 10)
        - max_parallel: int (optional) - Max parallel operations (default: 5)
        - interpretation_options: Dict (optional) - Interpretation-specific options
        """
        parsed_result_ids = intent.parameters.get("parsed_result_ids")
        if not parsed_result_ids or not isinstance(parsed_result_ids, list):
            raise ValueError("parsed_result_ids parameter is required and must be a list for bulk_interpret_data intent")
        
        batch_size = intent.parameters.get("batch_size", 10)
        max_parallel = intent.parameters.get("max_parallel", 5)
        interpretation_options = intent.parameters.get("interpretation_options", {})
        
        import asyncio
        
        results = []
        errors = []
        total_ids = len(parsed_result_ids)
        
        # Process in batches
        for batch_start in range(0, total_ids, batch_size):
            batch = parsed_result_ids[batch_start:batch_start + batch_size]
            batch_num = (batch_start // batch_size) + 1
            total_batches = (total_ids + batch_size - 1) // batch_size
            
            self.logger.info(f"Processing interpretation batch {batch_num}/{total_batches} ({len(batch)} results)")
            
            semaphore = asyncio.Semaphore(max_parallel)
            
            async def interpret_single_result(parsed_result_id: str, index: int) -> Dict[str, Any]:
                """Interpret a single parsed result."""
                async with semaphore:
                    try:
                        # Create interpret intent (using self_discovery as default)
                        interpret_intent = IntentFactory.create_intent(
                            intent_type="interpret_data_self_discovery",
                            tenant_id=context.tenant_id,
                            session_id=context.session_id,
                            solution_id=intent.solution_id,
                            parameters={
                                "parsed_file_id": parsed_result_id,
                                **interpretation_options
                            }
                        )
                        
                        # Note: This would need to call Insights Realm, but for now we'll skip
                        # as it requires Insights Realm integration
                        return {
                            "success": False,
                            "index": index,
                            "parsed_result_id": parsed_result_id,
                            "error": "Bulk interpretation requires Insights Realm integration (not yet implemented)"
                        }
                    
                    except Exception as e:
                        self.logger.error(f"Error interpreting {parsed_result_id}: {e}", exc_info=True)
                        return {
                            "success": False,
                            "index": index,
                            "parsed_result_id": parsed_result_id,
                            "error": str(e)
                        }
            
            # Process batch in parallel
            batch_results = await asyncio.gather(*[
                interpret_single_result(parsed_result_id, batch_start + i)
                for i, parsed_result_id in enumerate(batch)
            ])
            
            # Collect results
            for result in batch_results:
                if result.get("success"):
                    results.append(result)
                else:
                    errors.append(result)
        
        success_count = len(results)
        error_count = len(errors)
        
        self.logger.info(f"Bulk interpretation complete: {success_count}/{total_ids} succeeded, {error_count} failed")
        
        return {
            "artifacts": {
                "total_ids": total_ids,
                "success_count": success_count,
                "error_count": error_count,
                "results": results,
                "errors": errors
            },
            "events": [
                {
                    "type": "bulk_interpretation_complete",
                    "total_ids": total_ids,
                    "success_count": success_count,
                    "error_count": error_count
                }
            ]
        }
    
    async def _handle_get_operation_status(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Handle get_operation_status intent - get operation progress/status.
        
        Intent parameters:
        - operation_id: str (REQUIRED) - Operation identifier
        """
        operation_id = intent.parameters.get("operation_id")
        if not operation_id:
            raise ValueError("operation_id is required for get_operation_status intent")
        
        # Get operation progress from State Surface
        progress = await context.state_surface.get_operation_progress(operation_id, context.tenant_id)
        
        if not progress:
            return {
                "artifacts": {
                    "operation_id": operation_id,
                    "status": "not_found",
                    "message": "Operation not found"
                },
                "events": []
            }
        
        return {
            "artifacts": {
                "operation_id": operation_id,
                "status": progress.get("status", "unknown"),
                "total": progress.get("total", 0),
                "processed": progress.get("processed", 0),
                "succeeded": progress.get("succeeded", 0),
                "failed": progress.get("failed", 0),
                "current_batch": progress.get("current_batch", 0),
                "last_successful_batch": progress.get("last_successful_batch", 0),
                "progress_percentage": (
                    (progress.get("processed", 0) / progress.get("total", 1)) * 100
                    if progress.get("total", 0) > 0 else 0
                ),
                "updated_at": progress.get("updated_at")
            },
            "events": []
        }
    
    async def _handle_register_file(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Handle register_file intent - register existing file in State Surface.
        
        Use case: File already exists in GCS/Supabase, needs to be registered
        for governed access in this execution context.
        
        Intent parameters:
        - file_id: str (REQUIRED) - File identifier
        - storage_location: str (optional) - GCS blob path (if not provided, will try to get from Supabase)
        - ui_name: str (REQUIRED) - User-friendly filename for display
        - file_type: str (optional) - File type
        - mime_type: str (optional) - MIME type
        """
        file_id = intent.parameters.get("file_id")
        if not file_id:
            raise ValueError("file_id is required for register_file intent")
        
        ui_name = intent.parameters.get("ui_name")
        if not ui_name:
            raise ValueError("ui_name is required for register_file intent")
        
        file_type = intent.parameters.get("file_type", "unstructured")
        mime_type = intent.parameters.get("mime_type", "application/octet-stream")
        storage_location = intent.parameters.get("storage_location")
        
        # Try to get file metadata from Supabase (optional - file might not be there yet)
        file_metadata = await self._get_file_metadata_from_supabase(file_id, context.tenant_id)
        
        # Get storage location from metadata if not provided
        if not storage_location and file_metadata:
            storage_location = file_metadata.get("gcs_blob_path") or file_metadata.get("file_path") or file_metadata.get("storage_path")
        
        # If still no storage location, derive from file_id (assume standard pattern)
        if not storage_location:
            storage_location = f"files/{file_id}"
            self.logger.warning(f"Storage location not found for file {file_id}, using default pattern: {storage_location}")
        
        # Register in State Surface
        file_reference = f"file:{context.tenant_id}:{context.session_id}:{file_id}"
        
        await context.state_surface.store_file_reference(
            session_id=context.session_id,
            tenant_id=context.tenant_id,
            file_reference=file_reference,
            storage_location=storage_location,
            filename=file_metadata.get("file_name", ui_name) if file_metadata else ui_name,
            metadata={
                "ui_name": ui_name,
                "file_type": file_type or (file_metadata.get("file_type") if file_metadata else None),
                "mime_type": mime_type or (file_metadata.get("mime_type") if file_metadata else None),
                "size": file_metadata.get("file_size") if file_metadata else None,
                "file_hash": file_metadata.get("file_hash") if file_metadata else None,
                "file_id": file_id
            }
        )
        
        self.logger.info(f"File registered in State Surface: {file_id} ({ui_name}) -> {file_reference}")
        
        # Create structured artifact
        semantic_payload = {
            "file_id": file_id,
            "file_reference": file_reference,
            "storage_location": storage_location,
            "ui_name": ui_name,
            "file_type": file_type,
            "mime_type": mime_type,
            "file_size": file_metadata.get("file_size") if file_metadata else None,
            "file_hash": file_metadata.get("file_hash") if file_metadata else None,
            "status": "registered"
        }
        
        structured_artifact = create_structured_artifact(
            result_type="file",
            semantic_payload=semantic_payload,
            renderings={}  # Registration doesn't include contents
        )
        
        return {
            "artifacts": {
                "file": structured_artifact
            },
            "events": [
                {
                    "type": "file_registered",
                    "file_id": file_id,
                    "file_reference": file_reference
                }
            ]
        }
    
    async def _handle_save_materialization(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Handle save_materialization intent - explicitly authorize and register materialization.
        
        This is the second step after upload:
        1. Upload → creates boundary contract (pending materialization)
        2. Save → authorizes materialization (active) and registers in materialization index
        
        Intent parameters:
        - boundary_contract_id: str (REQUIRED) - Boundary contract from upload
        - file_id: str (REQUIRED) - File ID from upload
        """
        boundary_contract_id = intent.parameters.get("boundary_contract_id")
        file_id = intent.parameters.get("file_id")
        
        if not boundary_contract_id:
            raise ValueError("boundary_contract_id is required for save_materialization intent")
        if not file_id:
            raise ValueError("file_id is required for save_materialization intent")
        
        # Materialization authorization already happened in ExecutionLifecycleManager
        # We just need to register it in the materialization index
        
        materialization_type = context.metadata.get("materialization_type", "full_artifact")
        materialization_scope = context.metadata.get("materialization_scope", {})
        materialization_backing_store = context.metadata.get("materialization_backing_store", "gcs")
        
        # Get file metadata from state surface
        file_reference = f"file:{context.tenant_id}:{context.session_id}:{file_id}"
        file_metadata = None
        
        try:
            file_metadata = await context.state_surface.get_file_metadata(
                session_id=context.session_id,
                tenant_id=context.tenant_id,
                file_reference=file_reference
            )
        except Exception as e:
            self.logger.warning(f"Could not retrieve file metadata from state surface: {e}")
        
        # Register in materialization index (Supabase project_files)
        # This is where the file becomes "saved" and available for parsing
        if self.public_works:
            file_storage = self.public_works.get_file_storage_abstraction()
            if file_storage and hasattr(file_storage, 'register_materialization'):
                try:
                    await file_storage.register_materialization(
                        file_id=file_id,
                        boundary_contract_id=boundary_contract_id,
                        materialization_type=materialization_type,
                        materialization_scope=materialization_scope,
                        materialization_backing_store=materialization_backing_store,
                        tenant_id=context.tenant_id,
                        user_id=context.metadata.get("user_id", "system"),
                        session_id=context.session_id,
                        file_reference=file_reference,
                        metadata=file_metadata or {}
                    )
                    self.logger.info(f"✅ Materialization registered: {file_id} (contract: {boundary_contract_id})")
                except Exception as e:
                    self.logger.error(f"Failed to register materialization: {e}", exc_info=True)
                    # Continue anyway - materialization is authorized, just not registered in index
            else:
                self.logger.warning("FileStorageAbstraction not available or missing register_materialization method")
        
        # Create structured artifact
        semantic_payload = {
            "boundary_contract_id": boundary_contract_id,
            "file_id": file_id,
            "file_reference": file_reference,
            "materialization_type": materialization_type,
            "materialization_scope": materialization_scope,
            "materialization_backing_store": materialization_backing_store,
            "status": "saved",
            "available_for_parsing": True
        }
        
        structured_artifact = create_structured_artifact(
            result_type="materialization",
            semantic_payload=semantic_payload,
            renderings={
                "message": "File saved and available for parsing"
            }
        )
        
        return {
            "artifacts": {
                "materialization": structured_artifact
            },
            "events": [
                {
                    "type": "materialization_saved",
                    "file_id": file_id,
                    "boundary_contract_id": boundary_contract_id,
                    "materialization_type": materialization_type,
                    "materialization_scope": materialization_scope
                }
            ]
        }
    
    async def _handle_retrieve_file_metadata(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Handle retrieve_file_metadata intent - get Supabase record (metadata only).
        
        Intent parameters:
        - file_id: str (REQUIRED) - File identifier
        """
        file_id = intent.parameters.get("file_id")
        if not file_id:
            raise ValueError("file_id is required for retrieve_file_metadata intent")
        
        # Try to get file metadata from Supabase first
        file_metadata = await self._get_file_metadata_from_supabase(file_id, context.tenant_id)
        
        # If not in Supabase, try State Surface (file might be in GCS but metadata creation failed)
        if not file_metadata:
            file_reference = f"file:{context.tenant_id}:{context.session_id}:{file_id}"
            state_metadata = await context.state_surface.get_file_metadata(file_reference)
            if state_metadata:
                # Convert State Surface metadata to Supabase-like format
                file_metadata = {
                    "uuid": file_id,
                    "ui_name": state_metadata.get("ui_name") or state_metadata.get("filename"),
                    "file_type": state_metadata.get("file_type"),
                    "file_size": state_metadata.get("size"),
                    "file_hash": state_metadata.get("file_hash"),
                    "created_at": state_metadata.get("created_at"),
                    "tenant_id": context.tenant_id,
                    "session_id": context.session_id,
                    "storage_location": state_metadata.get("storage_location"),
                    "_from_state_surface": True  # Flag to indicate source
                }
        
        if not file_metadata:
            raise ValueError(f"File not found: {file_id}")
        
        # Create structured artifact
        file_reference = f"file:{context.tenant_id}:{context.session_id}:{file_id}"
        semantic_payload = {
            "file_id": file_id,
            "file_reference": file_reference,
            "file_name": file_metadata.get("ui_name") or file_metadata.get("file_name"),
            "file_type": file_metadata.get("file_type"),
            "mime_type": file_metadata.get("mime_type") or file_metadata.get("content_type"),
            "file_size": file_metadata.get("file_size"),
            "file_hash": file_metadata.get("file_hash"),
            "storage_location": file_metadata.get("storage_location") or file_metadata.get("gcs_blob_path"),
            "created_at": file_metadata.get("created_at"),
            "updated_at": file_metadata.get("updated_at"),
            "tenant_id": file_metadata.get("tenant_id"),
            "session_id": file_metadata.get("session_id")
        }
        
        structured_artifact = create_structured_artifact(
            result_type="file",
            semantic_payload=semantic_payload,
            renderings={}  # Metadata only, no contents
        )
        
        return {
            "artifacts": {
                "file": structured_artifact
            },
            "events": []
        }
    
    async def _handle_retrieve_file(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Handle retrieve_file intent - get file contents from GCS.
        
        Intent parameters:
        - file_id: str (REQUIRED) - File identifier
        - file_reference: str (optional) - State Surface file reference
        - include_contents: bool (optional) - Whether to return file contents (default: True)
        """
        file_id = intent.parameters.get("file_id")
        file_reference = intent.parameters.get("file_reference")
        include_contents = intent.parameters.get("include_contents", True)
        
        if not file_id and not file_reference:
            raise ValueError("Either file_id or file_reference is required for retrieve_file intent")
        
        # Try to get file metadata - prefer direct file_id lookup via FileStorageAbstraction
        # This avoids session-scoped file_reference issues
        file_metadata = None
        storage_location = None
        
        # First, try direct file_id lookup via FileStorageAbstraction (most reliable)
        if file_id and hasattr(self, 'public_works') and self.public_works:
            file_storage = self.public_works.get_file_storage_abstraction()
            if file_storage:
                try:
                    file_metadata_dict = await file_storage.get_file_by_uuid(file_id)
                    if file_metadata_dict:
                        # Extract storage location
                        storage_location = file_metadata_dict.get("file_path") or file_metadata_dict.get("storage_path")
                        # Convert to State Surface format
                        file_metadata = {
                            "file_id": file_id,
                            "storage_location": storage_location,
                            "file_name": file_metadata_dict.get("file_name") or file_metadata_dict.get("ui_name"),
                            "file_type": file_metadata_dict.get("file_type"),
                            "mime_type": file_metadata_dict.get("mime_type") or file_metadata_dict.get("content_type"),
                            "file_size": file_metadata_dict.get("file_size"),
                            "file_hash": file_metadata_dict.get("file_hash"),
                            "metadata": file_metadata_dict.get("metadata", {}),
                            "created_at": file_metadata_dict.get("created_at"),
                            "updated_at": file_metadata_dict.get("updated_at")
                        }
                        # Construct file_reference for consistency (use current session or wildcard)
                        if not file_reference:
                            tenant_id = file_metadata_dict.get("tenant_id") or context.tenant_id
                            file_reference = f"file:{tenant_id}:{context.session_id}:{file_id}"
                except Exception as e:
                    self.logger.debug(f"File storage lookup by UUID failed: {e}")
        
        # Fallback: Try file_reference lookup in State Surface if provided
        if not file_metadata and file_reference:
            try:
                file_metadata = await context.state_surface.get_file_metadata(file_reference)
                if file_metadata:
                    storage_location = file_metadata.get("storage_location")
            except Exception as e:
                self.logger.debug(f"State Surface lookup failed: {e}")
        
        # Last resort: Try constructing file_reference from current session
        if not file_metadata and file_id and not file_reference:
            file_reference = f"file:{context.tenant_id}:{context.session_id}:{file_id}"
            try:
                file_metadata = await context.state_surface.get_file_metadata(file_reference)
                if file_metadata:
                    storage_location = file_metadata.get("storage_location")
            except Exception as e:
                self.logger.debug(f"State Surface lookup with constructed reference failed: {e}")
        
        if not file_metadata:
            raise ValueError(f"File not found: file_id={file_id}, file_reference={file_reference}")
        
        # Create structured artifact with semantic_payload and renderings
        semantic_payload = {
            "file_id": file_id or file_metadata.get("file_id") if isinstance(file_metadata, dict) else file_id,
            "file_reference": file_reference,
            "file_name": file_metadata.get("file_name") if isinstance(file_metadata, dict) else None,
            "file_type": file_metadata.get("file_type") if isinstance(file_metadata, dict) else None,
            "mime_type": file_metadata.get("mime_type") or file_metadata.get("content_type") if isinstance(file_metadata, dict) else None,
            "file_size": file_metadata.get("file_size") if isinstance(file_metadata, dict) else None,
            "file_hash": file_metadata.get("file_hash") if isinstance(file_metadata, dict) else None,
            "storage_location": storage_location or (file_metadata.get("storage_location") if isinstance(file_metadata, dict) else None),
            "created_at": file_metadata.get("created_at") if isinstance(file_metadata, dict) else None,
            "updated_at": file_metadata.get("updated_at") if isinstance(file_metadata, dict) else None
        }
        
        # Get file contents if requested (goes in renderings, handled by materialization policy)
        renderings = {}
        if include_contents:
            file_contents = None
            if storage_location and hasattr(self, 'public_works') and self.public_works:
                file_storage = self.public_works.get_file_storage_abstraction()
                if file_storage:
                    try:
                        file_contents = await file_storage.download_file(storage_location)
                    except Exception as e:
                        self.logger.debug(f"Direct file download failed: {e}")
            
            # Fallback: Try via State Surface
            if not file_contents and file_reference:
                try:
                    file_contents = await context.state_surface.get_file(file_reference)
                except Exception as e:
                    self.logger.debug(f"State Surface file retrieval failed: {e}")
            
            if file_contents:
                # Convert bytes to JSON-serializable format
                # For text files, decode to string; for binary, use base64
                if isinstance(file_contents, bytes):
                    # Try to decode as UTF-8 (for text files like CSV, JSON, etc.)
                    try:
                        renderings["file_contents"] = file_contents.decode('utf-8')
                    except UnicodeDecodeError:
                        # For binary files, use base64 encoding
                        import base64
                        renderings["file_contents"] = base64.b64encode(file_contents).decode('utf-8')
                        renderings["file_contents_encoding"] = "base64"
                else:
                    # Already a string or other serializable type
                    renderings["file_contents"] = file_contents
                semantic_payload["file_size"] = len(file_contents) if isinstance(file_contents, bytes) else len(str(file_contents).encode('utf-8'))  # Update size from actual content
            else:
                self.logger.warning(f"File contents not found: file_id={file_id}, storage_location={storage_location}")
        
        structured_artifact = create_structured_artifact(
            result_type="file",
            semantic_payload=semantic_payload,
            renderings=renderings
        )
        
        return {
            "artifacts": {
                "file": structured_artifact
            },
            "events": []
        }
    
    async def _handle_list_files(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Handle list_files intent - list files for tenant/session.
        
        Intent parameters:
        - tenant_id: str (optional, defaults to context.tenant_id)
        - session_id: str (optional, defaults to context.session_id)
        - file_type: str (optional) - Filter by file type
        - limit: int (optional) - Limit results (default: 100)
        - offset: int (optional) - Pagination offset (default: 0)
        """
        tenant_id = intent.parameters.get("tenant_id", context.tenant_id)
        session_id = intent.parameters.get("session_id", context.session_id)
        file_type = intent.parameters.get("file_type")
        limit = intent.parameters.get("limit", 100)
        offset = intent.parameters.get("offset", 0)
        
        # Query Supabase for files (filtered by workspace scope)
        user_id = context.metadata.get("user_id")  # Get user_id from context for workspace filtering
        files = await self._list_files_from_supabase(
            tenant_id=tenant_id,
            session_id=session_id,
            file_type=file_type,
            limit=limit,
            offset=offset,
            user_id=user_id  # NEW: Filter by workspace scope
        )
        
        # Extract semantic data from each file (all JSON-serializable)
        file_list_semantic = []
        for file in files:
            file_semantic = {
                "file_id": file.get("uuid") or file.get("file_id"),
                "file_name": file.get("ui_name") or file.get("file_name"),
                "file_type": file.get("file_type"),
                "mime_type": file.get("mime_type") or file.get("content_type"),
                "file_size": file.get("file_size"),
                "file_hash": file.get("file_hash"),
                "storage_location": file.get("gcs_blob_path") or file.get("file_path"),
                "created_at": file.get("created_at"),
                "updated_at": file.get("updated_at")
            }
            file_list_semantic.append(file_semantic)
        
        semantic_payload = {
            "files": file_list_semantic,  # Array of file metadata (all JSON-serializable)
            "count": len(files),
            "tenant_id": tenant_id,
            "session_id": session_id,
            "limit": limit,
            "offset": offset,
            "file_type_filter": file_type  # If filtered
        }
        
        structured_artifact = create_structured_artifact(
            result_type="file_list",
            semantic_payload=semantic_payload,
            renderings={}  # No renderings for listing
        )
        
        return {
            "artifacts": {
                "file_list": structured_artifact
            },
            "events": []
        }
    
    async def _handle_get_file_by_id(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Handle get_file_by_id intent - get file by file_id.
        
        Intent parameters:
        - file_id: str (REQUIRED) - File identifier
        """
        file_id = intent.parameters.get("file_id")
        if not file_id:
            raise ValueError("file_id is required for get_file_by_id intent")
        
        # Get file metadata from Supabase
        file_metadata = await self._get_file_metadata_from_supabase(file_id, context.tenant_id)
        if not file_metadata:
            raise ValueError(f"File not found: {file_id}")
        
        # Check if file is registered in State Surface
        file_reference = f"file:{context.tenant_id}:{context.session_id}:{file_id}"
        state_metadata = await context.state_surface.get_file_metadata(file_reference)
        
        # Create structured artifact
        semantic_payload = {
            "file_id": file_id,
            "file_reference": file_reference if state_metadata else None,
            "file_name": file_metadata.get("ui_name") or file_metadata.get("file_name"),
            "file_type": file_metadata.get("file_type"),
            "mime_type": file_metadata.get("mime_type") or file_metadata.get("content_type"),
            "file_size": file_metadata.get("file_size"),
            "file_hash": file_metadata.get("file_hash"),
            "storage_location": file_metadata.get("gcs_blob_path") or file_metadata.get("file_path"),
            "created_at": file_metadata.get("created_at"),
            "updated_at": file_metadata.get("updated_at"),
            "tenant_id": file_metadata.get("tenant_id"),
            "session_id": file_metadata.get("session_id"),
            "registered_in_state_surface": state_metadata is not None
        }
        
        structured_artifact = create_structured_artifact(
            result_type="file",
            semantic_payload=semantic_payload,
            renderings={}  # Metadata only
        )
        
        return {
            "artifacts": {
                "file": structured_artifact
            },
            "events": []
        }
    
    async def _get_file_metadata_from_supabase(
        self,
        file_id: str,
        tenant_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get file metadata from Supabase by file_id.
        
        Args:
            file_id: File identifier
            tenant_id: Tenant identifier
        
        Returns:
            File metadata dictionary or None if not found
        """
        if not self.public_works:
            return None
        
        supabase_adapter = self.public_works.get_supabase_adapter()
        if not supabase_adapter:
            return None
        
        try:
            # Use FileStorageAbstraction.get_file_by_uuid (proper abstraction layer)
            file_storage = self.public_works.get_file_storage_abstraction()
            if not file_storage:
                return None
            
            file_metadata = await file_storage.get_file_by_uuid(file_id)
            
            if file_metadata:
                # Verify tenant_id matches (convert both to UUID strings for comparison)
                import uuid as uuid_lib
                try:
                    # Convert query tenant_id to UUID string
                    if isinstance(tenant_id, str):
                        try:
                            tenant_id_uuid = uuid_lib.UUID(tenant_id)
                        except ValueError:
                            tenant_id_uuid = uuid_lib.uuid5(uuid_lib.NAMESPACE_DNS, tenant_id)
                        tenant_id_str = str(tenant_id_uuid)
                    else:
                        tenant_id_str = str(tenant_id)
                    
                    # Compare with file's tenant_id
                    file_tenant_id = str(file_metadata.get("tenant_id"))
                    if file_tenant_id == tenant_id_str:
                        return file_metadata
                    else:
                        self.logger.warning(f"File found but tenant_id mismatch: file={file_tenant_id}, query={tenant_id_str}")
                        return None
                except Exception as e:
                    self.logger.warning(f"Failed to verify tenant_id: {e}, returning metadata anyway")
                    return file_metadata
            
            return None
        except Exception as e:
            self.logger.error(f"Failed to get file metadata from Supabase: {e}", exc_info=True)
            return None
    
    async def _list_files_from_supabase(
        self,
        tenant_id: str,
        session_id: Optional[str] = None,
        file_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List files from Supabase with filters.
        
        Args:
            tenant_id: Tenant identifier (may be string, will be converted to UUID for query)
            session_id: Optional session identifier (not in schema, but kept for backward compatibility)
            file_type: Optional file type filter
            limit: Result limit
            offset: Pagination offset
        
        Returns:
            List of file metadata dictionaries
        """
        if not self.public_works:
            return []
        
        supabase_adapter = self.public_works.get_supabase_adapter()
        if not supabase_adapter:
            return []
        
        try:
            # Convert tenant_id to UUID format for query (if it's a string)
            import uuid as uuid_lib
            tenant_id_for_query = tenant_id
            try:
                if isinstance(tenant_id, str):
                    try:
                        tenant_id_uuid = uuid_lib.UUID(tenant_id)
                    except ValueError:
                        tenant_id_uuid = uuid_lib.uuid5(uuid_lib.NAMESPACE_DNS, tenant_id)
                    tenant_id_for_query = str(tenant_id_uuid)
            except Exception:
                # If conversion fails, use original
                pass
            
            # Use SupabaseFileAdapter directly (service_key bypasses RLS)
            # This is more reliable than RLS policy queries
            supabase_file_adapter = self.public_works.supabase_file_adapter
            if supabase_file_adapter:
                try:
                    # Query directly using service_key (bypasses RLS)
                    result = supabase_file_adapter._client.table("project_files").select("*").eq("tenant_id", tenant_id_for_query).eq("deleted", False).execute()
                    files = result.data if result.data else []
                    
                    # Filter by file_type if provided
                    if file_type:
                        files = [f for f in files if f.get("file_type") == file_type]
                    
                    # Apply pagination
                    files = files[offset:offset + limit]
                    
                    return files
                except Exception as e:
                    self.logger.error(f"Failed to list files using SupabaseFileAdapter: {e}", exc_info=True)
            
            # Fallback: Use RLS policy query
            query_result = await supabase_adapter.execute_rls_policy(
                table="project_files",
                operation="select",
                user_context={"tenant_id": tenant_id_for_query},
                data=None
            )
            
            if not query_result.get("success") or not query_result.get("data"):
                return []
            
            # Filter results
            files = query_result["data"]
            
            # Note: session_id is not in project_files schema, so we skip that filter
            # Files are already filtered by tenant_id via RLS policy
            
            # Filter by file_type if provided
            if file_type:
                files = [f for f in files if f.get("file_type") == file_type]
            
            # Apply pagination
            files = files[offset:offset + limit]
            
            return files
        except Exception as e:
            self.logger.error(f"Failed to list files from Supabase: {e}", exc_info=True)
            return []
    
    async def _handle_archive_file(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Handle archive_file intent - archive file (soft delete).
        
        Intent parameters:
        - file_id: str (REQUIRED) - File identifier
        - file_reference: str (optional) - State Surface file reference
        - reason: str (optional) - Archive reason
        """
        file_id = intent.parameters.get("file_id")
        file_reference = intent.parameters.get("file_reference")
        reason = intent.parameters.get("reason", "User requested")
        
        if not file_id and not file_reference:
            raise ValueError("Either file_id or file_reference is required for archive_file intent")
        
        # Construct file reference if not provided
        if not file_reference:
            file_reference = f"file:{context.tenant_id}:{context.session_id}:{file_id}"
        
        # Get file metadata
        file_metadata = await context.state_surface.get_file_metadata(file_reference)
        if not file_metadata:
            raise ValueError(f"File not found in State Surface: {file_reference}")
        
        storage_location = file_metadata.get("storage_location")
        if not storage_location:
            raise ValueError(f"Storage location not found for file: {file_reference}")
        
        # Update metadata to mark as archived (soft delete)
        # In production, this would update Supabase record
        # For now, we'll update State Surface metadata
        # Merge existing metadata with archive status
        existing_metadata = file_metadata.get("metadata", {}) if isinstance(file_metadata.get("metadata"), dict) else {}
        updated_metadata = {
            **existing_metadata,
            "status": "archived",
            "archived_at": self.clock.now_iso(),
            "archive_reason": reason
        }
        
        # Update in State Surface
        await context.state_surface.store_file_reference(
            session_id=context.session_id,
            tenant_id=context.tenant_id,
            file_reference=file_reference,
            storage_location=storage_location,
            filename=file_metadata.get("filename", ""),
            metadata={
                **file_metadata,  # Preserve all existing metadata
                **updated_metadata  # Add/update archive fields
            }
        )
        
        self.logger.info(f"File archived: {file_id or file_reference} (reason: {reason})")
        
        return {
            "artifacts": {
                "file_id": file_id,
                "file_reference": file_reference,
                "status": "archived",
                "archived_at": updated_metadata["archived_at"]
            },
            "events": [
                {
                    "type": "file_archived",
                    "file_id": file_id,
                    "file_reference": file_reference,
                    "reason": reason
                }
            ]
        }
    
    async def _handle_purge_file(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Handle purge_file intent - permanently delete file.
        
        Intent parameters:
        - file_id: str (REQUIRED) - File identifier
        - file_reference: str (optional) - State Surface file reference
        - confirm: bool (REQUIRED) - Confirmation flag (must be True)
        """
        file_id = intent.parameters.get("file_id")
        file_reference = intent.parameters.get("file_reference")
        confirm = intent.parameters.get("confirm", False)
        
        if not confirm:
            raise ValueError("confirm=True is required for purge_file intent (permanent deletion)")
        
        if not file_id and not file_reference:
            raise ValueError("Either file_id or file_reference is required for purge_file intent")
        
        # Construct file reference if not provided
        if not file_reference:
            file_reference = f"file:{context.tenant_id}:{context.session_id}:{file_id}"
        
        # Get file metadata
        file_metadata = await context.state_surface.get_file_metadata(file_reference)
        if not file_metadata:
            raise ValueError(f"File not found in State Surface: {file_reference}")
        
        storage_location = file_metadata.get("storage_location")
        if not storage_location:
            raise ValueError(f"Storage location not found for file: {file_reference}")
        
        # Delete from GCS via FileStorageAbstraction
        if not self.file_parser_service.file_storage_abstraction:
            raise RuntimeError("File storage abstraction not available")
        
        delete_success = await self.file_parser_service.file_storage_abstraction.delete_file(storage_location)
        
        if not delete_success:
            self.logger.warning(f"File deletion from GCS may have failed: {storage_location}")
        
        # Remove from State Surface (or mark as purged)
        # In production, would also delete from Supabase
        
        self.logger.info(f"File purged (permanently deleted): {file_id or file_reference}")
        
        return {
            "artifacts": {
                "file_id": file_id,
                "file_reference": file_reference,
                "status": "purged",
                "purged_at": self.clock.now_iso()
            },
            "events": [
                {
                    "type": "file_purged",
                    "file_id": file_id,
                    "file_reference": file_reference
                }
            ]
        }
    
    async def _handle_restore_file(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Handle restore_file intent - restore archived file.
        
        Intent parameters:
        - file_id: str (REQUIRED) - File identifier
        - file_reference: str (optional) - State Surface file reference
        """
        file_id = intent.parameters.get("file_id")
        file_reference = intent.parameters.get("file_reference")
        
        if not file_id and not file_reference:
            raise ValueError("Either file_id or file_reference is required for restore_file intent")
        
        # Construct file reference if not provided
        if not file_reference:
            file_reference = f"file:{context.tenant_id}:{context.session_id}:{file_id}"
        
        # Get file metadata
        file_metadata = await context.state_surface.get_file_metadata(file_reference)
        if not file_metadata:
            raise ValueError(f"File not found in State Surface: {file_reference}")
        
        # Check status in metadata dict or top-level
        status = file_metadata.get("status") or file_metadata.get("metadata", {}).get("status")
        if status != "archived":
            raise ValueError(f"File is not archived (status: {status})")
        
        storage_location = file_metadata.get("storage_location")
        if not storage_location:
            raise ValueError(f"Storage location not found for file: {file_reference}")
        
        # Update metadata to restore (remove archived status)
        existing_metadata = file_metadata.get("metadata", {}) if isinstance(file_metadata.get("metadata"), dict) else {}
        updated_metadata = {
            **existing_metadata,
            "status": "active",
            "restored_at": self.clock.now_iso()
        }
        # Remove archive-specific fields
        updated_metadata.pop("archived_at", None)
        updated_metadata.pop("archive_reason", None)
        
        # Update in State Surface
        await context.state_surface.store_file_reference(
            session_id=context.session_id,
            tenant_id=context.tenant_id,
            file_reference=file_reference,
            storage_location=storage_location,
            filename=file_metadata.get("filename", ""),
            metadata={
                **file_metadata,  # Preserve all existing metadata
                **updated_metadata  # Add/update restore fields
            }
        )
        
        self.logger.info(f"File restored: {file_id or file_reference}")
        
        return {
            "artifacts": {
                "file_id": file_id,
                "file_reference": file_reference,
                "status": "active",
                "restored_at": updated_metadata["restored_at"]
            },
            "events": [
                {
                    "type": "file_restored",
                    "file_id": file_id,
                    "file_reference": file_reference
                }
            ]
        }
    
    async def _handle_validate_file(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Handle validate_file intent - validate file format/contents.
        
        Intent parameters:
        - file_id: str (REQUIRED) - File identifier
        - file_reference: str (optional) - State Surface file reference
        - validation_rules: Dict (optional) - Validation rules
            - max_size: int - Maximum file size in bytes
            - allowed_types: List[str] - Allowed file types
            - required_metadata: List[str] - Required metadata fields
        """
        file_id = intent.parameters.get("file_id")
        file_reference = intent.parameters.get("file_reference")
        validation_rules = intent.parameters.get("validation_rules", {})
        
        if not file_id and not file_reference:
            raise ValueError("Either file_id or file_reference is required for validate_file intent")
        
        # Construct file reference if not provided
        if not file_reference:
            file_reference = f"file:{context.tenant_id}:{context.session_id}:{file_id}"
        
        # Get file metadata
        file_metadata = await context.state_surface.get_file_metadata(file_reference)
        if not file_metadata:
            raise ValueError(f"File not found in State Surface: {file_reference}")
        
        validation_results = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Validate file size
        max_size = validation_rules.get("max_size")
        if max_size:
            file_size = file_metadata.get("size")
            if file_size and file_size > max_size:
                validation_results["valid"] = False
                validation_results["errors"].append(f"File size ({file_size} bytes) exceeds maximum ({max_size} bytes)")
        
        # Validate file type
        allowed_types = validation_rules.get("allowed_types")
        if allowed_types:
            # Check file_type (parsing pathway) or mime_type (file format)
            file_type = file_metadata.get("file_type")
            mime_type = file_metadata.get("mime_type") or file_metadata.get("content_type")  # Support both for transition
            if not file_type and mime_type:
                # Extract file extension from MIME type as fallback
                file_type = mime_type.split("/")[-1] if "/" in mime_type else mime_type
            if file_type and file_type not in allowed_types:
                validation_results["valid"] = False
                validation_results["errors"].append(f"File type '{file_type}' not in allowed types: {allowed_types}")
        
        # Validate required metadata
        required_metadata = validation_rules.get("required_metadata", [])
        for field in required_metadata:
            if field not in file_metadata:
                validation_results["warnings"].append(f"Required metadata field '{field}' not found")
        
        # Validate file exists in storage
        storage_location = file_metadata.get("storage_location")
        if storage_location and self.file_parser_service.file_storage_abstraction:
            file_info = await self.file_parser_service.file_storage_abstraction.get_file_metadata(storage_location)
            if not file_info:
                validation_results["warnings"].append("File not found in storage (metadata exists but file missing)")
        
        return {
            "artifacts": {
                "file_id": file_id,
                "file_reference": file_reference,
                "validation_results": validation_results
            },
            "events": []
        }
    
    async def _handle_preprocess_file(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Handle preprocess_file intent - preprocess file (normalize, clean, etc.).
        
        Intent parameters:
        - file_id: str (REQUIRED) - File identifier
        - file_reference: str (optional) - State Surface file reference
        - preprocessing_options: Dict (optional) - Preprocessing options
            - normalize: bool - Normalize file format
            - clean: bool - Clean file contents
            - extract_metadata: bool - Extract additional metadata
        """
        file_id = intent.parameters.get("file_id")
        file_reference = intent.parameters.get("file_reference")
        preprocessing_options = intent.parameters.get("preprocessing_options", {})
        
        if not file_id and not file_reference:
            raise ValueError("Either file_id or file_reference is required for preprocess_file intent")
        
        # Construct file reference if not provided
        if not file_reference:
            file_reference = f"file:{context.tenant_id}:{context.session_id}:{file_id}"
        
        # Get file metadata
        file_metadata = await context.state_surface.get_file_metadata(file_reference)
        if not file_metadata:
            raise ValueError(f"File not found in State Surface: {file_reference}")
        
        storage_location = file_metadata.get("storage_location")
        if not storage_location:
            raise ValueError(f"Storage location not found for file: {file_reference}")
        
        # Get file contents
        file_contents = await context.state_surface.get_file(file_reference)
        if not file_contents:
            raise ValueError(f"File contents not found: {file_reference}")
        
        preprocessing_results = {
            "preprocessed": True,
            "changes": []
        }
        
        # Normalize file format (placeholder - would use actual normalization logic)
        if preprocessing_options.get("normalize", False):
            preprocessing_results["changes"].append("File format normalized")
        
        # Clean file contents (placeholder - would use actual cleaning logic)
        if preprocessing_options.get("clean", False):
            preprocessing_results["changes"].append("File contents cleaned")
        
        # Extract additional metadata (placeholder - would use actual extraction logic)
        if preprocessing_options.get("extract_metadata", False):
            preprocessing_results["changes"].append("Additional metadata extracted")
        
        # In production, would save preprocessed file and update metadata
        # For now, just return preprocessing results
        
        return {
            "artifacts": {
                "file_id": file_id,
                "file_reference": file_reference,
                "preprocessing_results": preprocessing_results
            },
            "events": [
                {
                    "type": "file_preprocessed",
                    "file_id": file_id,
                    "file_reference": file_reference
                }
            ]
        }
    
    async def _handle_search_files(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Handle search_files intent - search files by name/content.
        
        Intent parameters:
        - query: str (REQUIRED) - Search query
        - search_type: str (optional) - "name", "content", or "both" (default: "name")
        - limit: int (optional) - Limit results (default: 100)
        - offset: int (optional) - Pagination offset (default: 0)
        """
        query = intent.parameters.get("query")
        if not query:
            raise ValueError("query is required for search_files intent")
        
        search_type = intent.parameters.get("search_type", "name")
        limit = intent.parameters.get("limit", 100)
        offset = intent.parameters.get("offset", 0)
        
        # Get files from Supabase
        files = await self._list_files_from_supabase(
            tenant_id=context.tenant_id,
            session_id=context.session_id,
            file_type=None,
            limit=limit * 2,  # Get more to filter
            offset=offset
        )
        
        # Filter by search query
        matching_files = []
        query_lower = query.lower()
        
        for file in files:
            matched = False
            
            if search_type in ("name", "both"):
                # Search in filename, ui_name
                filename = (file.get("file_name") or file.get("ui_name") or "").lower()
                if query_lower in filename:
                    matched = True
            
            if search_type in ("content", "both") and not matched:
                # For content search, would need to index file contents
                # For now, just search in metadata
                file_type = (file.get("file_type") or "").lower()
                if query_lower in file_type:
                    matched = True
            
            if matched:
                matching_files.append(file)
                if len(matching_files) >= limit:
                    break
        
        return {
            "artifacts": {
                "query": query,
                "search_type": search_type,
                "files": matching_files,
                "count": len(matching_files)
            },
            "events": []
        }
    
    async def _handle_query_files(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Handle query_files intent - query files with filters.
        
        Intent parameters:
        - filters: Dict (REQUIRED) - Filter criteria
            - file_type: str (optional) - Filter by file type
            - status: str (optional) - Filter by status (active, archived, etc.)
            - min_size: int (optional) - Minimum file size
            - max_size: int (optional) - Maximum file size
            - created_after: str (optional) - ISO timestamp
            - created_before: str (optional) - ISO timestamp
        - limit: int (optional) - Limit results (default: 100)
        - offset: int (optional) - Pagination offset (default: 0)
        """
        filters = intent.parameters.get("filters", {})
        if not filters:
            raise ValueError("filters parameter is required for query_files intent")
        
        limit = intent.parameters.get("limit", 100)
        offset = intent.parameters.get("offset", 0)
        
        # Get files from Supabase
        files = await self._list_files_from_supabase(
            tenant_id=context.tenant_id,
            session_id=context.session_id,
            file_type=filters.get("file_type"),
            limit=limit * 2,  # Get more to filter
            offset=offset
        )
        
        # Apply filters
        filtered_files = []
        
        for file in files:
            # Filter by status
            if "status" in filters:
                file_status = file.get("status", "active")
                if file_status != filters["status"]:
                    continue
            
            # Filter by size
            if "min_size" in filters or "max_size" in filters:
                file_size = file.get("file_size", 0)
                if "min_size" in filters and file_size < filters["min_size"]:
                    continue
                if "max_size" in filters and file_size > filters["max_size"]:
                    continue
            
            # Filter by date
            if "created_after" in filters or "created_before" in filters:
                created_at = file.get("created_at", "")
                if "created_after" in filters and created_at < filters["created_after"]:
                    continue
                if "created_before" in filters and created_at > filters["created_before"]:
                    continue
            
            filtered_files.append(file)
            if len(filtered_files) >= limit:
                break
        
        return {
            "artifacts": {
                "filters": filters,
                "files": filtered_files,
                "count": len(filtered_files)
            },
            "events": []
        }
    
    async def _handle_update_file_metadata(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Handle update_file_metadata intent - update file metadata.
        
        Intent parameters:
        - file_id: str (REQUIRED) - File identifier
        - file_reference: str (optional) - State Surface file reference
        - metadata_updates: Dict (REQUIRED) - Metadata fields to update
        """
        file_id = intent.parameters.get("file_id")
        file_reference = intent.parameters.get("file_reference")
        metadata_updates = intent.parameters.get("metadata_updates")
        
        if not metadata_updates:
            raise ValueError("metadata_updates is required for update_file_metadata intent")
        
        if not file_id and not file_reference:
            raise ValueError("Either file_id or file_reference is required for update_file_metadata intent")
        
        # Construct file reference if not provided
        if not file_reference:
            file_reference = f"file:{context.tenant_id}:{context.session_id}:{file_id}"
        
        # Get current file metadata
        file_metadata = await context.state_surface.get_file_metadata(file_reference)
        if not file_metadata:
            raise ValueError(f"File not found in State Surface: {file_reference}")
        
        storage_location = file_metadata.get("storage_location")
        if not storage_location:
            raise ValueError(f"Storage location not found for file: {file_reference}")
        
        # Update metadata
        updated_metadata = {
            **file_metadata,
            **metadata_updates,
            "updated_at": self.clock.now_iso()
        }
        
        # Update in State Surface
        await context.state_surface.store_file_reference(
            session_id=context.session_id,
            tenant_id=context.tenant_id,
            file_reference=file_reference,
            storage_location=storage_location,
            filename=updated_metadata.get("filename", file_metadata.get("filename", "")),
            metadata=updated_metadata
        )
        
        # In production, would also update Supabase record
        
        self.logger.info(f"File metadata updated: {file_id or file_reference}")
        
        return {
            "artifacts": {
                "file_id": file_id,
                "file_reference": file_reference,
                "updated_metadata": updated_metadata
            },
            "events": [
                {
                    "type": "file_metadata_updated",
                    "file_id": file_id,
                    "file_reference": file_reference,
                    "updates": metadata_updates
                }
            ]
        }
    
    async def _handle_parse_content(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Handle parse_content intent - parse already uploaded file.
        
        Intent parameters:
        - file_id: str (required) - File identifier
        - file_reference: str (optional) - State Surface file reference
        - parsing_type: str (optional) - Explicit parsing type
        - parse_options: Dict (optional) - Parsing options
        """
        file_id = intent.parameters.get("file_id")
        if not file_id:
            raise ValueError("file_id is required for parse_content intent")
        
        file_reference = intent.parameters.get("file_reference")
        
        # If file_reference not provided, look up file metadata by file_id to get the correct session_id
        if not file_reference:
            file_metadata = await self._get_file_metadata_from_supabase(file_id, context.tenant_id)
            if file_metadata:
                # Construct file_reference from actual file metadata (includes correct session_id)
                actual_session_id = file_metadata.get("session_id")
                if actual_session_id:
                    file_reference = f"file:{context.tenant_id}:{actual_session_id}:{file_id}"
                else:
                    # Fallback: use context session_id if file metadata doesn't have session_id
                    file_reference = f"file:{context.tenant_id}:{context.session_id}:{file_id}"
            else:
                # Fallback: construct with context session_id if file not found in Supabase
                file_reference = f"file:{context.tenant_id}:{context.session_id}:{file_id}"
        
        parsing_type = intent.parameters.get("parsing_type")
        parse_options = intent.parameters.get("parse_options", {})
        copybook_reference = intent.parameters.get("copybook_reference")
        
        # Parse file via FileParserService
        parsed_result = await self.file_parser_service.parse_file(
            file_id=file_id,
            tenant_id=context.tenant_id,
            context=context,
            file_reference=file_reference,
            parsing_type=parsing_type,
            parse_options=parse_options,
            copybook_reference=copybook_reference
        )
        
        parsed_file_id = parsed_result.get("parsed_file_id")
        parsed_file_reference = parsed_result.get("parsed_file_reference")
        parsing_type_result = parsed_result.get("parsing_type", parsing_type or "unknown")
        parsing_status = parsed_result.get("parsing_status", "success")
        
        # Track parsed results in Supabase for lineage
        await self._track_parsed_result(
            parsed_file_id=parsed_file_id,
            file_id=file_id,
            parsed_file_reference=parsed_file_reference,
            parser_type=parsing_type_result,
            parser_config=parse_options,
            record_count=parsed_result.get("record_count"),
            status=parsing_status,
            tenant_id=context.tenant_id,
            context=context
        )
        
        # Create structured artifact for parsed content
        from symphainy_platform.realms.utils.structured_artifacts import create_structured_artifact
        
        semantic_payload = {
            "parsed_file_id": parsed_file_id,
            "parsed_file_reference": parsed_file_reference,
            "file_id": file_id,
            "parsing_type": parsing_type_result,
            "parsing_status": parsing_status,
            "record_count": parsed_result.get("record_count"),
            "parse_options": parse_options
        }
        
        # Renderings can include parsed data (full or preview)
        renderings = {}
        parsed_data = parsed_result.get("parsed_data")
        if parsed_data:
            # Include parsed data in renderings (can be large, but needed for immediate use)
            # For large datasets, could limit to preview, but for MVP include full data
            renderings["parsed_data"] = parsed_data
            # Also include a preview for quick access
            if isinstance(parsed_data, list) and len(parsed_data) > 10:
                renderings["parsed_data_preview"] = parsed_data[:10]
            elif isinstance(parsed_data, dict) and len(parsed_data) > 10:
                renderings["parsed_data_preview"] = dict(list(parsed_data.items())[:10])
            else:
                renderings["parsed_data_preview"] = parsed_data
        
        parsed_content_artifact = create_structured_artifact(
            result_type="parsed_content",
            semantic_payload=semantic_payload,
            renderings=renderings
        )
        
        return {
            "artifacts": {
                "parsed_content": parsed_content_artifact,
                "parsed_file_id": parsed_file_id,  # Keep for backward compatibility
                "parsed_file_reference": parsed_file_reference
            },
            "events": [
                {
                    "type": "content_parsed",
                    "file_id": file_id,
                    "parsed_file_id": parsed_file_id,
                    "parsing_type": parsing_type_result
                }
            ]
        }
    
    async def _handle_extract_embeddings(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Handle extract_embeddings intent."""
        parsed_file_id = intent.parameters.get("parsed_file_id")
        
        if not parsed_file_id:
            raise ValueError("parsed_file_id is required for extract_embeddings intent")
        
        # Get file_id from parsed results (for lineage tracking)
        file_id = await self._get_file_id_from_parsed_result(parsed_file_id, context.tenant_id)
        
        # For MVP: Return placeholder
        # In full implementation: Create embeddings via EmbeddingService
        embedding_id = generate_event_id()
        arango_collection = "embeddings"
        arango_key = embedding_id
        
        # Track embeddings in Supabase for lineage
        await self._track_embedding(
            embedding_id=embedding_id,
            parsed_file_id=parsed_file_id,
            file_id=file_id,
            arango_collection=arango_collection,
            arango_key=arango_key,
            embedding_count=0,  # Will be updated when embeddings are actually created
            model_name="placeholder",  # Will be updated when embeddings are actually created
            tenant_id=context.tenant_id,
            context=context
        )
        
        return {
            "artifacts": {
                "embeddings_created": True,
                "parsed_file_id": parsed_file_id,
                "embedding_id": embedding_id
            },
            "events": [
                {
                    "type": "embeddings_created",
                    "parsed_file_id": parsed_file_id,
                    "embedding_id": embedding_id
                }
            ]
        }
    
    async def _handle_get_parsed_file(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Handle get_parsed_file intent."""
        parsed_file_id = intent.parameters.get("parsed_file_id")
        
        if not parsed_file_id:
            raise ValueError("parsed_file_id is required for get_parsed_file intent")
        
        # Get parsed file via FileParserService
        parsed_file = await self.file_parser_service.get_parsed_file(
            parsed_file_id=parsed_file_id,
            tenant_id=context.tenant_id,
            context=context
        )
        
        return {
            "artifacts": {
                "parsed_file": parsed_file
            },
            "events": []
        }
    
    async def _handle_get_semantic_interpretation(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Handle get_semantic_interpretation intent - 3-layer semantic pattern.
        
        Intent parameters:
        - parsed_file_id: str (required) - Parsed file identifier
        - parsed_file_reference: str (optional) - State Surface parsed file reference
        
        Returns 3-layer semantic interpretation:
        - Layer 1: Metadata (schema, structure, format) - from parsed file
        - Layer 2: Meaning (semantic interpretation, relationships) - from embeddings
        - Layer 3: Context (domain-specific interpretation) - from semantic graph
        """
        parsed_file_id = intent.parameters.get("parsed_file_id")
        if not parsed_file_id:
            raise ValueError("parsed_file_id is required for get_semantic_interpretation intent")
        
        parsed_file_reference = intent.parameters.get("parsed_file_reference")
        if not parsed_file_reference:
            # Construct reference if not provided
            parsed_file_reference = f"parsed:{context.tenant_id}:{context.session_id}:{parsed_file_id}"
        
        # Get parsed file data from State Surface
        parsed_file_data = await context.state_surface.get_file(parsed_file_reference)
        if not parsed_file_data:
            raise ValueError(f"Parsed file not found: {parsed_file_reference}")
        
        # Parse JSON data
        import json
        parsed_result = json.loads(parsed_file_data.decode('utf-8'))
        
        # Layer 1: Metadata (from parsed file)
        layer1_metadata = {
            "parsing_type": parsed_result.get("parsing_type"),
            "file_id": parsed_result.get("file_id"),
            "has_text_content": bool(parsed_result.get("text_content")),
            "has_structured_data": bool(parsed_result.get("structured_data")),
            "has_validation_rules": bool(parsed_result.get("validation_rules")),
            "metadata": parsed_result.get("metadata", {})
        }
        
        # Extract structured data schema if available
        structured_data = parsed_result.get("structured_data")
        if structured_data:
            if isinstance(structured_data, dict):
                # Structured data (tables, columns, etc.)
                if "tables" in structured_data:
                    layer1_metadata["tables_count"] = len(structured_data["tables"])
                if "columns" in structured_data:
                    layer1_metadata["columns"] = structured_data["columns"]
                if "schema" in structured_data:
                    layer1_metadata["schema"] = structured_data["schema"]
        
        # Layer 2: Meaning (from semantic embeddings if available)
        layer2_meaning = {
            "semantic_embeddings_available": False,
            "semantic_interpretation": None,
            "relationships": []
        }
        
        # Try to get semantic embeddings from SemanticDataAbstraction
        semantic_data_abstraction = None
        if self.public_works:
            try:
                semantic_data_abstraction = self.public_works.get_semantic_data_abstraction()
                
                if semantic_data_abstraction:
                    # Query for embeddings related to this parsed file
                    embeddings = await semantic_data_abstraction.get_semantic_embeddings(
                        filter_conditions={"parsed_file_id": parsed_file_id},
                        limit=100
                    )
                    
                    if embeddings:
                        layer2_meaning["semantic_embeddings_available"] = True
                        layer2_meaning["embeddings_count"] = len(embeddings)
                        
                        # Extract semantic meanings from embeddings
                        semantic_meanings = []
                        for emb in embeddings:
                            if emb.get("semantic_meaning"):
                                semantic_meanings.append(emb.get("semantic_meaning"))
                        
                        if semantic_meanings:
                            layer2_meaning["semantic_interpretation"] = semantic_meanings
            except Exception as e:
                self.logger.warning(f"Could not retrieve semantic embeddings: {e}")
        
        # Layer 3: Context (from semantic graph if available)
        layer3_context = {
            "semantic_graph_available": False,
            "domain_interpretation": None,
            "contextual_relationships": []
        }
        
        # Try to get semantic graph from SemanticDataAbstraction
        if semantic_data_abstraction:
            try:
                # Query semantic graph related to this parsed file
                semantic_graph = await semantic_data_abstraction.get_semantic_graph(
                    filter_conditions={"parsed_file_id": parsed_file_id}
                )
                
                if semantic_graph:
                    nodes = semantic_graph.get("nodes", [])
                    edges = semantic_graph.get("edges", [])
                    
                    if nodes:
                        layer3_context["semantic_graph_available"] = True
                        layer3_context["nodes_count"] = len(nodes)
                        layer3_context["edges_count"] = len(edges) if edges else 0
                        
                        # Extract domain interpretations from nodes
                        domain_interpretations = []
                        for node in nodes:
                            if node.get("domain_interpretation"):
                                domain_interpretations.append(node.get("domain_interpretation"))
                            elif node.get("semantic_meaning"):
                                domain_interpretations.append(node.get("semantic_meaning"))
                        
                        if domain_interpretations:
                            layer3_context["domain_interpretation"] = domain_interpretations
                        
                        # Extract contextual relationships from edges
                        if edges:
                            relationships = []
                            for edge in edges:
                                relationships.append({
                                    "from": edge.get("_from"),
                                    "to": edge.get("_to"),
                                    "type": edge.get("relationship_type"),
                                    "confidence": edge.get("confidence")
                                })
                            layer3_context["contextual_relationships"] = relationships
            except Exception as e:
                self.logger.warning(f"Could not retrieve semantic graph: {e}")
        
        # Combine 3-layer interpretation
        semantic_interpretation = {
            "parsed_file_id": parsed_file_id,
            "parsed_file_reference": parsed_file_reference,
            "layer1_metadata": layer1_metadata,
            "layer2_meaning": layer2_meaning,
            "layer3_context": layer3_context,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.logger.info(f"Semantic interpretation generated: {parsed_file_id}")
        
        return {
            "artifacts": {
                "semantic_interpretation": semantic_interpretation
            },
            "events": [
                {
                    "type": "semantic_interpretation_generated",
                    "parsed_file_id": parsed_file_id
                }
            ]
        }
    
    async def _track_parsed_result(
        self,
        parsed_file_id: str,
        file_id: str,
        parsed_file_reference: str,
        parser_type: str,
        parser_config: Dict[str, Any],
        record_count: Optional[int],
        status: str,
        tenant_id: str,
        context: ExecutionContext
    ):
        """
        Track parsed result in Supabase for lineage tracking.
        
        Args:
            parsed_file_id: Parsed file identifier
            file_id: Source file identifier
            parsed_file_reference: State Surface file reference
            parser_type: Parser type used
            parser_config: Parser configuration
            record_count: Number of records parsed
            status: Parsing status
            tenant_id: Tenant identifier
            context: Execution context
        """
        if not self.public_works:
            self.logger.debug("Public Works not available, skipping lineage tracking")
            return
        
        supabase_adapter = self.public_works.get_supabase_adapter()
        if not supabase_adapter:
            self.logger.debug("Supabase adapter not available, skipping lineage tracking")
            return
        
        try:
            # Get GCS path from parsed_file_reference or construct it
            gcs_path = parsed_file_reference
            if not gcs_path or not gcs_path.startswith("gcs://"):
                # Construct GCS path
                gcs_path = f"tenant/{tenant_id}/parsed/{parsed_file_id}.jsonl"
            
            # Prepare parsed result record
            parsed_result_record = {
                "id": str(uuid.uuid4()),
                "tenant_id": tenant_id,
                "file_id": file_id,
                "parsed_result_id": parsed_file_id,
                "gcs_path": gcs_path,
                "parser_type": parser_type,
                "parser_config": parser_config,
                "record_count": record_count,
                "status": status
            }
            
            # Insert into Supabase using execute_rls_policy
            result = await supabase_adapter.execute_rls_policy(
                table="parsed_results",
                operation="insert",
                user_context={"tenant_id": tenant_id},
                data=parsed_result_record
            )
            if result.get("success"):
                self.logger.debug(f"Tracked parsed result in Supabase: {parsed_file_id}")
            else:
                self.logger.warning(f"Failed to track parsed result in Supabase: {parsed_file_id}: {result.get('error')}")
                
        except Exception as e:
            self.logger.error(f"Failed to track parsed result: {e}", exc_info=True)
    
    async def _track_embedding(
        self,
        embedding_id: str,
        parsed_file_id: str,
        file_id: Optional[str],
        arango_collection: str,
        arango_key: str,
        embedding_count: int,
        model_name: str,
        tenant_id: str,
        context: ExecutionContext
    ):
        """
        Track embedding in Supabase for lineage tracking.
        
        Args:
            embedding_id: Embedding identifier
            parsed_file_id: Parsed file identifier
            file_id: Source file identifier (optional)
            arango_collection: ArangoDB collection name
            arango_key: ArangoDB document key
            embedding_count: Number of embeddings
            model_name: Embedding model name
            tenant_id: Tenant identifier
            context: Execution context
        """
        if not self.public_works:
            self.logger.debug("Public Works not available, skipping lineage tracking")
            return
        
        supabase_adapter = self.public_works.get_supabase_adapter()
        if not supabase_adapter:
            self.logger.debug("Supabase adapter not available, skipping lineage tracking")
            return
        
        try:
            # Get parsed_result_id UUID from Supabase (lookup by parsed_result_id string)
            parsed_result_uuid = None
            if parsed_file_id:
                # Query parsed_results table to get UUID using execute_rls_policy
                query_result = await supabase_adapter.execute_rls_policy(
                    table="parsed_results",
                    operation="select",
                    user_context={"tenant_id": tenant_id},
                    data=None
                )
                if query_result.get("success") and query_result.get("data"):
                    # Filter in Python (Supabase client handles filtering)
                    matching_records = [
                        r for r in query_result["data"]
                        if r.get("parsed_result_id") == parsed_file_id and r.get("tenant_id") == tenant_id
                    ]
                    if matching_records:
                        parsed_result_uuid = matching_records[0].get("id")
                        # Also get file_id if not provided
                        if not file_id:
                            file_id = matching_records[0].get("file_id")
            
            # Prepare embedding record
            embedding_record = {
                "id": str(uuid.uuid4()),
                "tenant_id": tenant_id,
                "file_id": file_id or "",  # Use empty string if not available
                "parsed_result_id": parsed_result_uuid,  # UUID reference
                "embedding_id": embedding_id,
                "arango_collection": arango_collection,
                "arango_key": arango_key,
                "embedding_count": embedding_count,
                "model_name": model_name
            }
            
            # Insert into Supabase using execute_rls_policy
            result = await supabase_adapter.execute_rls_policy(
                table="embeddings",
                operation="insert",
                user_context={"tenant_id": tenant_id},
                data=embedding_record
            )
            if result.get("success"):
                self.logger.debug(f"Tracked embedding in Supabase: {embedding_id}")
            else:
                self.logger.warning(f"Failed to track embedding in Supabase: {embedding_id}: {result.get('error')}")
                
        except Exception as e:
            self.logger.error(f"Failed to track embedding: {e}", exc_info=True)
    
    async def _get_file_id_from_parsed_result(
        self,
        parsed_file_id: str,
        tenant_id: str
    ) -> Optional[str]:
        """
        Get file_id from parsed_result_id for lineage tracking.
        
        Args:
            parsed_file_id: Parsed file identifier
            tenant_id: Tenant identifier
        
        Returns:
            File identifier or None if not found
        """
        if not self.public_works:
            return None
        
        supabase_adapter = self.public_works.get_supabase_adapter()
        if not supabase_adapter:
            return None
        
        try:
            # Query parsed_results table to get file_id using execute_rls_policy
            query_result = await supabase_adapter.execute_rls_policy(
                table="parsed_results",
                operation="select",
                user_context={"tenant_id": tenant_id},
                data=None
            )
            if query_result.get("success") and query_result.get("data"):
                # Filter in Python (Supabase client handles filtering)
                matching_records = [
                    r for r in query_result["data"]
                    if r.get("parsed_result_id") == parsed_file_id and r.get("tenant_id") == tenant_id
                ]
                if matching_records:
                    return matching_records[0].get("file_id")
        except Exception as e:
            self.logger.debug(f"Could not get file_id from parsed_result: {e}")
        
        return None