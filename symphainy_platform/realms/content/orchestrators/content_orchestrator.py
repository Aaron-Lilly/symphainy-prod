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

# Add project root to path
project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional
from datetime import datetime
import uuid

from utilities import get_logger, generate_event_id
from symphainy_platform.runtime.intent_model import Intent
from symphainy_platform.runtime.execution_context import ExecutionContext
from ..enabling_services.file_parser_service import FileParserService


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
        Handle ingest_file intent - upload file to GCS and Supabase.
        
        Intent parameters:
        - file_content: bytes (hex-encoded for JSON transport)
        - ui_name: str (user-friendly filename)
        - file_type: str (e.g., "pdf", "csv")
        - mime_type: str (e.g., "application/pdf")
        - filename: str (original filename)
        - user_id: str (optional, from context if not provided)
        """
        # Extract file content (hex-encoded)
        file_content_hex = intent.parameters.get("file_content")
        if not file_content_hex:
            raise ValueError("file_content is required for ingest_file intent")
        
        # Decode hex to bytes
        try:
            file_content = bytes.fromhex(file_content_hex)
        except ValueError as e:
            raise ValueError(f"Invalid file_content (must be hex-encoded): {e}")
        
        # Extract metadata
        ui_name = intent.parameters.get("ui_name")
        if not ui_name:
            raise ValueError("ui_name is required for ingest_file intent")
        
        file_type = intent.parameters.get("file_type", "unstructured")
        mime_type = intent.parameters.get("mime_type", "application/octet-stream")
        filename = intent.parameters.get("filename", ui_name)
        user_id = intent.parameters.get("user_id") or context.metadata.get("user_id", "system")
        
        # Generate file path (will use file_id from upload result)
        # For now, use a temporary path - upload_file will generate file_id
        temp_file_path = f"files/{generate_event_id()}"
        
        # Prepare metadata for upload
        upload_metadata = {
            "user_id": user_id,
            "tenant_id": context.tenant_id,
            "ui_name": ui_name,
            "file_type": file_type,
            "content_type": mime_type,
            "filename": filename,
            "status": "uploaded"
        }
        
        # Upload file via FileStorageAbstraction
        if not self.file_parser_service.file_storage_abstraction:
            raise RuntimeError("File storage abstraction not available - Public Works not initialized")
        
        upload_result = await self.file_parser_service.file_storage_abstraction.upload_file(
            file_path=temp_file_path,
            file_data=file_content,
            metadata=upload_metadata
        )
        
        if not upload_result.get("success"):
            error = upload_result.get("error", "Unknown error")
            raise RuntimeError(f"File upload failed: {error}")
        
        file_id = upload_result.get("file_id")
        actual_file_path = upload_result.get("file_path")
        
        if not file_id:
            raise RuntimeError("File upload succeeded but file_id not returned")
        
        # Register file reference in State Surface (for governed file access)
        file_reference = f"file:{context.tenant_id}:{context.session_id}:{file_id}"
        
        # Calculate file hash for metadata
        import hashlib
        file_hash = hashlib.sha256(file_content).hexdigest()
        
        # Store file reference in State Surface
        await context.state_surface.store_file_reference(
            session_id=context.session_id,
            tenant_id=context.tenant_id,
            file_reference=file_reference,
            storage_location=actual_file_path,
            filename=filename,
            metadata={
                "ui_name": ui_name,
                "file_type": file_type,
                "content_type": mime_type,
                "size": len(file_content),
                "file_hash": file_hash,
                "file_id": file_id
            }
        )
        
        self.logger.info(f"File uploaded and registered: {file_id} ({ui_name}) -> {file_reference}")
        
        return {
            "artifacts": {
                "file_id": file_id,
                "file_reference": file_reference,
                "file_path": actual_file_path,
                "ui_name": ui_name,
                "file_type": file_type,
                "status": "uploaded"
            },
            "events": [
                {
                    "type": "file_uploaded",
                    "file_id": file_id,
                    "file_reference": file_reference,
                    "ui_name": ui_name,
                    "file_type": file_type
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
        
        return {
            "artifacts": {
                "parsed_file_id": parsed_file_id,
                "parsed_file_reference": parsed_file_reference,
                "file_id": file_id,
                "parsing_type": parsing_type_result,
                "parsing_status": parsing_status
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