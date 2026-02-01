"""
Platform Service (ctx.platform) - Capability-Oriented Operations

Provides capability-oriented operations that wrap Public Works protocols.
Primary purpose: enable infrastructure swappability while providing clean interfaces.

Operations:
    Parsing:
        - parse(file_reference, file_type, options) → Parse documents
        - parse_csv, parse_pdf, parse_excel, parse_word, parse_mainframe
    
    Ingestion:
        - ingest_file(file_data, ...) → Ingest uploaded files
        - ingest_edi(edi_data, partner_id, ...) → Ingest EDI data
        - ingest_api(api_payload, ...) → Ingest API payloads
    
    Processing:
        - visualize(data, viz_type, options) → Generate visualizations
        - embed(content, model) → Generate embeddings
    
    Storage:
        - store_artifact(artifact_id, data, ...) → Store artifacts
        - retrieve_artifact(artifact_id, tenant_id) → Retrieve artifacts
        - store_semantic / search_semantic → Semantic content operations
    
    Registry (file metadata, intents, lineage):
        - get_file_metadata(file_id, tenant_id) → File metadata
        - get_pending_intents(tenant_id, artifact_id, intent_type) → Pending intents
        - update_intent_status(intent_id, status, ...) → Update intent status
        - track_parsed_result(...) → Track parsing lineage

Usage:
    # Ingest a file
    result = await ctx.platform.ingest_file(file_bytes, tenant_id, session_id, metadata)
    
    # Parse a PDF
    result = await ctx.platform.parse(file_ref, file_type="pdf")
    
    # Generate visualization
    viz = await ctx.platform.visualize(data, viz_type="chart")
    
    # Get pending intents for a file
    pending = await ctx.platform.get_pending_intents(tenant_id, file_id, "parse_content")
"""

from dataclasses import dataclass, field
from typing import Any, Optional, Dict, List, Union

from utilities import get_logger

# Import protocols for type hints
from symphainy_platform.foundations.public_works.protocols.file_parsing_protocol import (
    FileParsingRequest,
    FileParsingResult,
    FileParsingProtocol
)
from symphainy_platform.foundations.public_works.protocols.visual_generation_protocol import (
    VisualGenerationProtocol
)
from symphainy_platform.foundations.public_works.protocols.ingestion_protocol import (
    IngestionProtocol,
    IngestionRequest,
    IngestionResult
)


@dataclass
class PlatformService:
    """
    Capability-oriented platform operations.
    
    Available via ctx.platform in PlatformContext.
    
    This service wraps Public Works protocols to provide clean, capability-oriented
    interfaces. The primary axis is infrastructure swappability - implementations
    can be swapped without changing the interface.
    """
    
    # Public Works abstractions (protocol-typed)
    _file_parsing: Optional[Any] = None
    _visual_generation: Optional[Any] = None
    _ingestion: Optional[Any] = None
    _semantic_data: Optional[Any] = None
    _deterministic_compute: Optional[Any] = None
    _file_storage: Optional[Any] = None
    _artifact_storage: Optional[Any] = None
    _state_surface: Optional[Any] = None
    
    # Parsing abstractions by type
    _parsers: Dict[str, Any] = field(default_factory=dict)
    
    def __init__(
        self,
        public_works: Optional[Any] = None,
        state_surface: Optional[Any] = None
    ):
        """
        Initialize PlatformService from Public Works.
        
        Args:
            public_works: Public Works foundation service
            state_surface: Runtime state surface
        """
        self._logger = get_logger("PlatformService")
        self._public_works = public_works
        self._state_surface = state_surface
        self._parsers = {}
        
        if public_works:
            self._initialize_abstractions(public_works)
    
    def _initialize_abstractions(self, public_works: Any) -> None:
        """Initialize abstractions from Public Works via getters only (no getattr on raw attributes)."""
        if not public_works:
            return
        # Visual generation
        if hasattr(public_works, "get_visual_generation_abstraction"):
            self._visual_generation = public_works.get_visual_generation_abstraction()
        if self._visual_generation:
            self._logger.debug("✅ VisualGenerationAbstraction initialized")
        # Ingestion
        if hasattr(public_works, "get_ingestion_abstraction"):
            self._ingestion = public_works.get_ingestion_abstraction()
        if self._ingestion:
            self._logger.debug("✅ IngestionAbstraction initialized")
        # Semantic data
        if hasattr(public_works, "get_semantic_data_abstraction"):
            self._semantic_data = public_works.get_semantic_data_abstraction()
        if self._semantic_data:
            self._logger.debug("✅ SemanticDataAbstraction initialized")
        # Deterministic compute (embeddings)
        if hasattr(public_works, "get_deterministic_compute_abstraction"):
            self._deterministic_compute = public_works.get_deterministic_compute_abstraction()
        if self._deterministic_compute:
            self._logger.debug("✅ DeterministicComputeAbstraction initialized")
        # File storage
        if hasattr(public_works, "get_file_storage_abstraction"):
            self._file_storage = public_works.get_file_storage_abstraction()
        if self._file_storage:
            self._logger.debug("✅ FileStorageAbstraction initialized")
        # Artifact storage
        if hasattr(public_works, "get_artifact_storage_abstraction"):
            self._artifact_storage = public_works.get_artifact_storage_abstraction()
        if self._artifact_storage:
            self._logger.debug("✅ ArtifactStorageAbstraction initialized")
        # Initialize parsers by type (getters only)
        self._initialize_parsers(public_works)

    def get_wal_query_interface(self) -> Optional[Any]:
        """
        Get WAL query interface (WALQueryProtocol) for execution metrics.
        Delegates to Public Works; intent services use this for get_execution_metrics.
        """
        if not self._public_works or not hasattr(self._public_works, "get_wal_query_interface"):
            return None
        return self._public_works.get_wal_query_interface()

    def get_solution_registry(self) -> Optional[Any]:
        """
        Get solution registry (SolutionRegistryProtocol) for Control Tower (list_solutions, compose_solution).
        Delegates to Public Works.
        """
        if not self._public_works or not hasattr(self._public_works, "get_solution_registry"):
            return None
        return self._public_works.get_solution_registry()

    def get_file_storage_abstraction(self) -> Optional[Any]:
        """
        Get file storage abstraction (FileStorageProtocol) for intent services that need direct storage access.
        Prefer platform methods (e.g. ingest_file, parse) when possible; use this when deletion or raw storage is needed.
        """
        return self._file_storage
    
    def _initialize_parsers(self, public_works: Any) -> None:
        """Initialize parsing abstractions by file type via Public Works getters only."""
        if not public_works:
            return
        # file_type -> getter method name on public_works
        parser_getters = {
            "csv": "get_csv_processing_abstraction",
            "excel": "get_excel_processing_abstraction",
            "pdf": "get_pdf_processing_abstraction",
            "word": "get_word_processing_abstraction",
            "docx": "get_word_processing_abstraction",
            "html": "get_html_processing_abstraction",
            "image": "get_image_processing_abstraction",
            "json": "get_json_processing_abstraction",
            "text": "get_text_processing_abstraction",
            "txt": "get_text_processing_abstraction",
            "kreuzberg": "get_kreuzberg_processing_abstraction",
            "mainframe": "get_mainframe_processing_abstraction",
            "data_model": "get_data_model_processing_abstraction",
            "workflow": "get_workflow_processing_abstraction",
            "bpmn": "get_workflow_processing_abstraction",
            "sop": "get_sop_processing_abstraction",
        }
        for file_type, getter_name in parser_getters.items():
            getter = getattr(public_works, getter_name, None)
            if callable(getter):
                parser = getter()
                if parser:
                    self._parsers[file_type] = parser
                    self._logger.debug(f"✅ Parser for '{file_type}' initialized")
    
    # ========================================================================
    # PARSING OPERATIONS
    # ========================================================================
    
    async def parse(
        self,
        file_reference: str,
        file_type: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Parse a document.
        
        Primary parsing interface. Routes to appropriate parser based on file_type.
        
        Args:
            file_reference: State Surface file reference (e.g., "file:tenant:session:id")
            file_type: Type of file ("pdf", "csv", "excel", "word", etc.)
            options: Parser-specific options
        
        Returns:
            Dict with parsed content and metadata
        """
        file_type = file_type.lower()
        
        # Get parser for file type
        parser = self._parsers.get(file_type)
        if not parser:
            raise ValueError(f"No parser available for file type: {file_type}")
        
        try:
            # Get file data from state surface if needed
            file_data = None
            if self._state_surface:
                file_data = await self._state_surface.get_file(file_reference)
            
            # Create parsing request
            request = FileParsingRequest(
                file_reference=file_reference,
                file_data=file_data,
                options=options or {}
            )
            
            # Execute parsing
            if hasattr(parser, 'parse'):
                result = await parser.parse(request)
            elif hasattr(parser, 'process'):
                result = await parser.process(file_reference, file_data, options or {})
            else:
                raise AttributeError(f"Parser for {file_type} has no parse/process method")
            
            return {
                "file_reference": file_reference,
                "file_type": file_type,
                "parsed_content": result.content if hasattr(result, 'content') else result,
                "metadata": result.metadata if hasattr(result, 'metadata') else {},
                "status": "success"
            }
            
        except Exception as e:
            self._logger.error(f"Parsing failed for {file_type}: {e}")
            return {
                "file_reference": file_reference,
                "file_type": file_type,
                "error": str(e),
                "status": "failed"
            }
    
    async def parse_csv(
        self,
        file_reference: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Parse CSV file."""
        return await self.parse(file_reference, "csv", options)
    
    async def parse_pdf(
        self,
        file_reference: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Parse PDF file."""
        return await self.parse(file_reference, "pdf", options)
    
    async def parse_excel(
        self,
        file_reference: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Parse Excel file."""
        return await self.parse(file_reference, "excel", options)
    
    async def parse_word(
        self,
        file_reference: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Parse Word document."""
        return await self.parse(file_reference, "word", options)
    
    async def parse_mainframe(
        self,
        file_reference: str,
        copybook_reference: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Parse mainframe file with optional copybook.
        
        Args:
            file_reference: File reference
            copybook_reference: Optional copybook reference for layout
            options: Parser options
        
        Returns:
            Parsed content
        """
        opts = options or {}
        if copybook_reference:
            opts["copybook_reference"] = copybook_reference
        return await self.parse(file_reference, "mainframe", opts)
    
    async def get_parsed_file(
        self,
        parsed_file_id: str,
        tenant_id: str,
        session_id: Optional[str] = None,
        execution_context: Optional[Any] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get parsed file content by ID.
        
        Retrieves previously parsed content for further processing
        (e.g., for creating deterministic embeddings).
        
        Args:
            parsed_file_id: Parsed file identifier
            tenant_id: Tenant identifier
            session_id: Optional session identifier
            execution_context: Optional ExecutionContext from caller (preferred).
                              If not provided, a minimal context is created (legacy support).
        
        Returns:
            Parsed content dict or None if not found
        
        Note:
            DISPOSABLE WRAPPER PATTERN: This method delegates to FileParserService.
            Callers should pass execution_context when available to maintain proper audit trail.
        """
        try:
            # Use FileParserService from libraries
            from symphainy_platform.foundations.libraries.parsing.file_parser_service import (
                FileParserService
            )
            
            service = FileParserService(public_works=self._public_works)
            
            # Use provided context or create minimal one for legacy callers
            context = execution_context
            if context is None:
                # Legacy support: create minimal context
                # WARNING: This path loses execution audit trail. Callers should pass context.
                self._logger.warning(
                    "get_parsed_file called without execution_context - "
                    "audit trail may be incomplete. Callers should pass execution_context."
                )
                from symphainy_platform.runtime.execution_context import ExecutionContext
                from symphainy_platform.runtime.intent_model import Intent
                from utilities import generate_event_id
                
                minimal_intent = Intent(
                    intent_type="get_parsed_file",
                    tenant_id=tenant_id,
                    session_id=session_id or "platform_sdk",
                    solution_id="platform_sdk",
                    parameters={"parsed_file_id": parsed_file_id}
                )
                
                context = ExecutionContext(
                    execution_id=generate_event_id(),
                    intent=minimal_intent,
                    tenant_id=tenant_id,
                    session_id=session_id or "platform_sdk",
                    solution_id="platform_sdk"
                )
            
            # Pure delegation
            return await service.get_parsed_file(
                parsed_file_id=parsed_file_id,
                tenant_id=tenant_id,
                context=context
            )
        except Exception as e:
            self._logger.error(f"Failed to get parsed file: {e}")
            return None
    
    # ========================================================================
    # VISUALIZATION OPERATIONS
    # ========================================================================
    
    async def visualize(
        self,
        data: Union[Dict, List],
        viz_type: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a visualization.
        
        Args:
            data: Data to visualize
            viz_type: Visualization type ("chart", "graph", "diagram", etc.)
            options: Visualization options (title, colors, dimensions, etc.)
        
        Returns:
            Dict with visualization result
        """
        if not self._visual_generation:
            raise RuntimeError("VisualGenerationAbstraction not available.")
        
        try:
            result = await self._visual_generation.generate(
                data=data,
                visualization_type=viz_type,
                options=options or {}
            )
            
            return {
                "viz_type": viz_type,
                "result": result,
                "status": "success"
            }
        except Exception as e:
            self._logger.error(f"Visualization failed: {e}")
            return {
                "viz_type": viz_type,
                "error": str(e),
                "status": "failed"
            }
    
    # ========================================================================
    # EMBEDDING OPERATIONS
    # ========================================================================
    
    async def embed(
        self,
        content: str,
        model: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate semantic embeddings for content.
        
        Args:
            content: Text content to embed
            model: Embedding model to use
            options: Embedding options
        
        Returns:
            Dict with embedding vector and metadata
        """
        if not self._deterministic_compute:
            raise RuntimeError("DeterministicComputeAbstraction not available.")
        
        try:
            result = await self._deterministic_compute.compute_embeddings(
                content=content,
                model=model,
                options=options or {}
            )
            
            return {
                "embedding": result.get("embedding", []),
                "model": model,
                "dimensions": len(result.get("embedding", [])),
                "status": "success"
            }
        except Exception as e:
            self._logger.error(f"Embedding generation failed: {e}")
            return {
                "error": str(e),
                "status": "failed"
            }
    
    async def create_deterministic_embeddings(
        self,
        parsed_file_id: str,
        parsed_content: Dict[str, Any],
        tenant_id: str,
        session_id: str,
        execution_context: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Create deterministic embeddings (schema fingerprints + pattern signatures).
        
        Deterministic embeddings capture structural patterns (schema) rather than
        semantic meaning. They are idempotent - same input always produces same output.
        
        Args:
            parsed_file_id: Parsed file identifier
            parsed_content: Parsed file content
            tenant_id: Tenant identifier
            session_id: Session identifier
            execution_context: Optional ExecutionContext from caller (preferred).
                              If not provided, a minimal context is created (legacy support).
        
        Returns:
            Dict with:
                - deterministic_embedding_id: Embedding identifier
                - schema_fingerprint: Hash of column structure
                - pattern_signature: Statistical signature of data patterns
                - schema: Extracted schema
                - status: "success" or "failed"
        
        Note:
            DISPOSABLE WRAPPER PATTERN: This method delegates to DeterministicEmbeddingService.
            Callers should pass execution_context when available to maintain proper audit trail.
        """
        try:
            # Use DeterministicEmbeddingService from libraries
            from symphainy_platform.foundations.libraries.embeddings.deterministic_embedding_service import (
                DeterministicEmbeddingService
            )
            
            # Create service with our public_works
            service = DeterministicEmbeddingService(public_works=self._public_works)
            
            # Use provided context or create minimal one for legacy callers
            context = execution_context
            if context is None:
                # Legacy support: create minimal context
                # WARNING: This path loses execution audit trail. Callers should pass context.
                self._logger.warning(
                    "create_deterministic_embeddings called without execution_context - "
                    "audit trail may be incomplete. Callers should pass execution_context."
                )
                from symphainy_platform.runtime.execution_context import ExecutionContext
                from symphainy_platform.runtime.intent_model import Intent
                from utilities import generate_event_id
                
                minimal_intent = Intent(
                    intent_type="create_deterministic_embeddings",
                    tenant_id=tenant_id,
                    session_id=session_id,
                    solution_id="platform_sdk",
                    parameters={"parsed_file_id": parsed_file_id}
                )
                
                context = ExecutionContext(
                    execution_id=generate_event_id(),
                    intent=minimal_intent,
                    tenant_id=tenant_id,
                    session_id=session_id,
                    solution_id="platform_sdk"
                )
            
            # Create deterministic embeddings (pure delegation)
            result = await service.create_deterministic_embeddings(
                parsed_file_id=parsed_file_id,
                parsed_content=parsed_content,
                context=context
            )
            
            # Light shaping: consistent return format
            return {
                "deterministic_embedding_id": result.get("deterministic_embedding_id"),
                "schema_fingerprint": result.get("schema_fingerprint"),
                "pattern_signature": result.get("pattern_signature"),
                "schema": result.get("schema"),
                "status": "success"
            }
        except Exception as e:
            self._logger.error(f"Deterministic embedding creation failed: {e}")
            return {
                "error": str(e),
                "status": "failed"
            }
    
    async def get_deterministic_embedding(
        self,
        embedding_id: str,
        tenant_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get deterministic embedding by ID.
        
        Args:
            embedding_id: Deterministic embedding identifier
            tenant_id: Tenant identifier
        
        Returns:
            Embedding data or None if not found
        """
        if not self._deterministic_compute:
            raise RuntimeError(
                "DeterministicComputeAbstraction not wired; cannot get deterministic embedding. Platform contract §8A."
            )
        
        try:
            embedding = await self._deterministic_compute.get_deterministic_embedding(
                embedding_id=embedding_id,
                tenant_id=tenant_id
            )
            return embedding
        except Exception as e:
            self._logger.error(f"Failed to get deterministic embedding: {e}")
            return None
    
    # ========================================================================
    # INGESTION OPERATIONS
    # ========================================================================
    
    async def ingest_file(
        self,
        file_data: bytes,
        tenant_id: str,
        session_id: str,
        source_metadata: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Ingest a file (upload type).
        
        Primary file ingestion method for direct uploads.
        
        Args:
            file_data: File content as bytes
            tenant_id: Tenant identifier
            session_id: Session identifier
            source_metadata: File metadata (ui_name, file_type, mime_type, etc.)
            options: Ingestion options
        
        Returns:
            Dict with:
                - success: bool
                - file_id: Artifact ID
                - file_reference: State Surface reference
                - storage_location: Where file is stored
                - ingestion_metadata: Additional metadata
                - status: "success" or "failed"
                - error: Error message if failed
        """
        from symphainy_platform.foundations.public_works.protocols.ingestion_protocol import (
            IngestionRequest as FullIngestionRequest,
            IngestionType
        )
        
        if not self._ingestion:
            raise RuntimeError("IngestionAbstraction not available.")
        
        try:
            request = FullIngestionRequest(
                ingestion_type=IngestionType.UPLOAD,
                tenant_id=tenant_id,
                session_id=session_id,
                source_metadata=source_metadata,
                data=file_data,
                options=options or {}
            )
            
            result = await self._ingestion.ingest_data(request)
            
            if not result.success:
                return {
                    "success": False,
                    "error": result.error,
                    "status": "failed"
                }
            
            return {
                "success": True,
                "file_id": result.file_id,
                "file_reference": result.file_reference,
                "storage_location": result.storage_location,
                "ingestion_metadata": result.ingestion_metadata,
                "status": "success"
            }
        except Exception as e:
            self._logger.error(f"File ingestion failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "status": "failed"
            }
    
    async def ingest_edi(
        self,
        edi_data: bytes,
        tenant_id: str,
        session_id: str,
        partner_id: str,
        source_metadata: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Ingest EDI data.
        
        Handles EDI protocol ingestion (AS2, SFTP, etc.).
        
        Args:
            edi_data: EDI content as bytes
            tenant_id: Tenant identifier
            session_id: Session identifier
            partner_id: Trading partner identifier
            source_metadata: EDI metadata
            options: Ingestion options
        
        Returns:
            Dict with ingestion result
        """
        from symphainy_platform.foundations.public_works.protocols.ingestion_protocol import (
            IngestionRequest as FullIngestionRequest,
            IngestionType
        )
        
        if not self._ingestion:
            raise RuntimeError("IngestionAbstraction not available.")
        
        try:
            # Add partner_id to metadata
            metadata = {**source_metadata, "partner_id": partner_id}
            
            request = FullIngestionRequest(
                ingestion_type=IngestionType.EDI,
                tenant_id=tenant_id,
                session_id=session_id,
                source_metadata=metadata,
                data=edi_data,
                options=options or {}
            )
            
            result = await self._ingestion.ingest_data(request)
            
            if not result.success:
                return {
                    "success": False,
                    "error": result.error,
                    "status": "failed"
                }
            
            return {
                "success": True,
                "file_id": result.file_id,
                "file_reference": result.file_reference,
                "storage_location": result.storage_location,
                "ingestion_metadata": result.ingestion_metadata,
                "status": "success"
            }
        except Exception as e:
            self._logger.error(f"EDI ingestion failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "status": "failed"
            }
    
    async def ingest_api(
        self,
        api_payload: Dict[str, Any],
        tenant_id: str,
        session_id: str,
        source_metadata: Dict[str, Any],
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Ingest API payload.
        
        Handles REST/GraphQL API payload ingestion.
        
        Args:
            api_payload: API payload data
            tenant_id: Tenant identifier
            session_id: Session identifier
            source_metadata: API metadata (endpoint, api_type, etc.)
            options: Ingestion options
        
        Returns:
            Dict with ingestion result
        """
        from symphainy_platform.foundations.public_works.protocols.ingestion_protocol import (
            IngestionRequest as FullIngestionRequest,
            IngestionType
        )
        
        if not self._ingestion:
            raise RuntimeError("IngestionAbstraction not available.")
        
        try:
            request = FullIngestionRequest(
                ingestion_type=IngestionType.API,
                tenant_id=tenant_id,
                session_id=session_id,
                source_metadata=source_metadata,
                api_payload=api_payload,
                options=options or {}
            )
            
            result = await self._ingestion.ingest_data(request)
            
            if not result.success:
                return {
                    "success": False,
                    "error": result.error,
                    "status": "failed"
                }
            
            return {
                "success": True,
                "file_id": result.file_id,
                "file_reference": result.file_reference,
                "storage_location": result.storage_location,
                "ingestion_metadata": result.ingestion_metadata,
                "status": "success"
            }
        except Exception as e:
            self._logger.error(f"API ingestion failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "status": "failed"
            }
    
    async def ingest(
        self,
        source: str,
        source_type: str,
        tenant_id: str,
        session_id: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generic ingest operation (legacy compatibility).
        
        For new code, prefer the specific methods:
        - ingest_file() for uploads
        - ingest_edi() for EDI
        - ingest_api() for API payloads
        
        Args:
            source: Source identifier
            source_type: Type of source
            tenant_id: Tenant identifier
            session_id: Session identifier
            options: Ingestion options
        
        Returns:
            Dict with ingestion result
        """
        if not self._ingestion:
            raise RuntimeError("IngestionAbstraction not available.")
        
        try:
            # Use simplified request for generic ingest
            result = await self._ingestion.ingest(
                source=source,
                source_type=source_type,
                tenant_id=tenant_id,
                session_id=session_id,
                options=options or {}
            )
            
            return {
                "source": source,
                "source_type": source_type,
                "file_reference": result.file_reference if hasattr(result, 'file_reference') else None,
                "metadata": result.metadata if hasattr(result, 'metadata') else {},
                "status": "success"
            }
        except Exception as e:
            self._logger.error(f"Ingestion failed: {e}")
            return {
                "source": source,
                "source_type": source_type,
                "error": str(e),
                "status": "failed"
            }
    
    # ========================================================================
    # STORAGE OPERATIONS
    # ========================================================================
    
    async def store_artifact(
        self,
        artifact_id: str,
        data: bytes,
        content_type: str,
        tenant_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Store an artifact.
        
        Args:
            artifact_id: Artifact identifier
            data: Artifact data
            content_type: MIME type
            tenant_id: Tenant identifier
            metadata: Optional metadata
        
        Returns:
            Dict with storage result
        """
        if not self._artifact_storage:
            raise RuntimeError("ArtifactStorageAbstraction not available.")
        
        try:
            result = await self._artifact_storage.store(
                artifact_id=artifact_id,
                data=data,
                content_type=content_type,
                tenant_id=tenant_id,
                metadata=metadata or {}
            )
            
            return {
                "artifact_id": artifact_id,
                "storage_location": result.get("storage_location"),
                "status": "success"
            }
        except Exception as e:
            self._logger.error(f"Artifact storage failed: {e}")
            return {
                "artifact_id": artifact_id,
                "error": str(e),
                "status": "failed"
            }
    
    async def retrieve_artifact(
        self,
        artifact_id: str,
        tenant_id: str
    ) -> Optional[bytes]:
        """
        Retrieve an artifact.
        
        Args:
            artifact_id: Artifact identifier
            tenant_id: Tenant identifier
        
        Returns:
            Artifact data or None
        """
        if not self._artifact_storage:
            raise RuntimeError("ArtifactStorageAbstraction not available.")
        
        try:
            return await self._artifact_storage.retrieve(
                artifact_id=artifact_id,
                tenant_id=tenant_id
            )
        except Exception as e:
            self._logger.error(f"Artifact retrieval failed: {e}")
            return None
    
    # ========================================================================
    # SEMANTIC DATA OPERATIONS
    # ========================================================================
    
    async def store_semantic(
        self,
        content_id: str,
        content: str,
        embedding: List[float],
        tenant_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Store semantic content with embedding.
        
        Args:
            content_id: Content identifier
            content: Text content
            embedding: Embedding vector
            tenant_id: Tenant identifier
            metadata: Optional metadata
        
        Returns:
            Dict with storage result
        """
        if not self._semantic_data:
            raise RuntimeError("SemanticDataAbstraction not available.")
        
        try:
            result = await self._semantic_data.store(
                content_id=content_id,
                content=content,
                embedding=embedding,
                tenant_id=tenant_id,
                metadata=metadata or {}
            )
            
            return {
                "content_id": content_id,
                "status": "success"
            }
        except Exception as e:
            self._logger.error(f"Semantic storage failed: {e}")
            return {
                "content_id": content_id,
                "error": str(e),
                "status": "failed"
            }
    
    async def search_semantic(
        self,
        query_embedding: List[float],
        tenant_id: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search semantic content by embedding similarity.
        
        Args:
            query_embedding: Query embedding vector
            tenant_id: Tenant identifier
            limit: Maximum results
            filters: Optional filters
        
        Returns:
            List of matching content
        """
        if not self._semantic_data:
            raise RuntimeError("SemanticDataAbstraction not available.")
        
        try:
            return await self._semantic_data.search(
                query_embedding=query_embedding,
                tenant_id=tenant_id,
                limit=limit,
                filters=filters or {}
            )
        except Exception as e:
            self._logger.error(f"Semantic search failed: {e}")
            return []
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def get_available_parsers(self) -> List[str]:
        """Get list of available parser types."""
        return list(self._parsers.keys())
    
    def get_available_capabilities(self) -> Dict[str, bool]:
        """
        Get availability status of platform capabilities.
        
        Returns:
            Dict mapping capability name to availability boolean
        """
        return {
            "parse": len(self._parsers) > 0,
            "parse_csv": "csv" in self._parsers,
            "parse_pdf": "pdf" in self._parsers,
            "parse_excel": "excel" in self._parsers,
            "parse_word": "word" in self._parsers,
            "parse_mainframe": "mainframe" in self._parsers,
            "visualize": self._visual_generation is not None,
            "embed": self._deterministic_compute is not None,
            "ingest": self._ingestion is not None,
            "ingest_file": self._ingestion is not None,
            "ingest_edi": self._ingestion is not None,
            "ingest_api": self._ingestion is not None,
            "store_artifact": self._artifact_storage is not None,
            "semantic": self._semantic_data is not None,
            "registry": self.registry is not None,
        }
    
    # ========================================================================
    # REGISTRY OPERATIONS (File metadata, pending intents, lineage tracking)
    # ========================================================================
    # These operations provide capability builders with access to file metadata,
    # pending intent management, and lineage tracking. They are legitimate
    # Platform SDK operations - capability builders access them via ctx.platform
    # rather than needing to navigate Civic Systems directly.
    #
    # The Platform SDK composes from underlying infrastructure (registry_abstraction)
    # but presents a unified interface for capability development.
    
    @property
    def registry(self) -> Optional[Any]:
        """
        Access to underlying registry abstraction.
        
        Used internally by Platform SDK registry operations.
        Capability builders should use the helper methods below rather than
        accessing this directly.
        """
        if self._public_works and hasattr(self._public_works, "get_registry_abstraction"):
            return self._public_works.get_registry_abstraction()
        return None
    
    async def get_file_metadata(
        self,
        file_id: str,
        tenant_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get file metadata.
        
        Retrieves metadata for a file including session_id, file_type, etc.
        Used to resolve file references and understand file context.
        
        Args:
            file_id: File identifier
            tenant_id: Tenant identifier
        
        Returns:
            File metadata dict or None if not found
        """
        registry = self.registry
        if not registry:
            return None
        
        try:
            return await registry.get_file_metadata(
                file_id=file_id,
                tenant_id=tenant_id
            )
        except Exception as e:
            self._logger.warning(f"Failed to get file metadata: {e}")
            return None
    
    async def list_files(
        self,
        tenant_id: Optional[str] = None,
        user_id: Optional[str] = None,
        file_type: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        List files from file storage (not registry).
        
        Per Curator layer target: file listing uses file_storage, not registry.
        """
        if not self._file_storage or not hasattr(self._file_storage, "list_files"):
            return []
        try:
            return await self._file_storage.list_files(
                tenant_id=tenant_id,
                user_id=user_id,
                file_type=file_type,
                limit=limit,
                offset=offset,
            ) or []
        except Exception as e:
            self._logger.warning(f"Failed to list files: {e}")
            return []
    
    async def get_pending_intents(
        self,
        tenant_id: str,
        target_artifact_id: str,
        intent_type: str
    ) -> List[Dict[str, Any]]:
        """
        Get pending intents for an artifact.
        
        Retrieves pending intents that target a specific artifact.
        Used to get context from earlier pipeline stages (e.g., ingestion
        profile from ingest intent when parsing).
        
        Args:
            tenant_id: Tenant identifier
            target_artifact_id: Artifact ID the intents target
            intent_type: Type of intent to filter by
        
        Returns:
            List of pending intent dicts
        """
        registry = self.registry
        if not registry:
            return []
        
        try:
            return await registry.get_pending_intents(
                tenant_id=tenant_id,
                target_artifact_id=target_artifact_id,
                intent_type=intent_type
            )
        except Exception as e:
            self._logger.warning(f"Failed to get pending intents: {e}")
            return []
    
    async def update_intent_status(
        self,
        intent_id: str,
        status: str,
        tenant_id: str,
        execution_id: str
    ) -> bool:
        """
        Update pending intent status.
        
        Updates the status of a pending intent (e.g., to "in_progress" or "completed").
        Used to track progress through multi-stage pipelines.
        
        Args:
            intent_id: Intent identifier
            status: New status ("pending", "in_progress", "completed", "failed")
            tenant_id: Tenant identifier
            execution_id: Current execution ID
        
        Returns:
            True if update succeeded
        """
        registry = self.registry
        if not registry:
            return False
        
        try:
            await registry.update_intent_status(
                intent_id=intent_id,
                status=status,
                tenant_id=tenant_id,
                execution_id=execution_id
            )
            return True
        except Exception as e:
            self._logger.warning(f"Failed to update intent status: {e}")
            return False
    
    async def track_parsed_result(
        self,
        parsed_file_id: str,
        file_id: str,
        parsed_file_reference: str,
        parser_type: str,
        parser_config: Dict[str, Any],
        record_count: Optional[int],
        status: str,
        tenant_id: str,
        session_id: str
    ) -> bool:
        """
        Track parsed result for lineage.
        
        Records the parsing of a file for lineage tracking. Creates a
        relationship between source file and parsed output.
        
        Args:
            parsed_file_id: ID of the parsed output
            file_id: ID of the source file
            parsed_file_reference: Reference to parsed content
            parser_type: Type of parser used
            parser_config: Parser configuration
            record_count: Number of records parsed (if applicable)
            status: Parsing status
            tenant_id: Tenant identifier
            session_id: Session identifier
        
        Returns:
            True if tracking succeeded
        """
        registry = self.registry
        if not registry:
            return False
        
        try:
            await registry.track_parsed_result(
                parsed_file_id=parsed_file_id,
                file_id=file_id,
                parsed_file_reference=parsed_file_reference,
                parser_type=parser_type,
                parser_config=parser_config,
                record_count=record_count,
                status=status,
                tenant_id=tenant_id,
                session_id=session_id
            )
            return True
        except Exception as e:
            self._logger.warning(f"Failed to track parsed result: {e}")
            return False
    
    # ========================================================================
    # FILE OPERATIONS
    # ========================================================================
    
    async def delete_file(
        self,
        storage_location: str,
        tenant_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Delete a file from storage.
        
        Args:
            storage_location: Storage location/path of the file
            tenant_id: Optional tenant identifier
        
        Returns:
            Dict with:
                - success: bool
                - status: "success" or "failed"
                - error: Error message if failed
        """
        if not self._file_storage:
            raise RuntimeError(
                "FileStorageAbstraction not wired; cannot delete file. Platform contract §8A."
            )
        
        try:
            await self._file_storage.delete_file(storage_location)
            return {
                "success": True,
                "status": "success"
            }
        except Exception as e:
            self._logger.error(f"File deletion failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "status": "failed"
            }
    
    # ========================================================================
    # MATERIALIZATION OPERATIONS
    # ========================================================================
    
    async def register_materialization(
        self,
        file_id: str,
        boundary_contract_id: str,
        tenant_id: str,
        session_id: str,
        user_id: str,
        file_reference: str,
        materialization_type: str = "full_artifact",
        materialization_scope: Optional[Dict[str, Any]] = None,
        materialization_backing_store: str = "gcs",
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Register materialization in the materialization index.
        
        Transitions a file from Working Material (pending) to Records of Fact (saved).
        
        Args:
            file_id: File artifact identifier
            boundary_contract_id: Boundary contract identifier
            tenant_id: Tenant identifier
            session_id: Session identifier
            user_id: User identifier
            file_reference: File reference string
            materialization_type: Type of materialization
            materialization_scope: Materialization scope
            materialization_backing_store: Backing store (e.g., "gcs")
            metadata: File metadata
        
        Returns:
            True if registration succeeded
        """
        if not self._file_storage:
            raise RuntimeError(
                "FileStorageAbstraction not wired; cannot register materialization. Platform contract §8A."
            )
        
        try:
            if hasattr(self._file_storage, 'register_materialization'):
                await self._file_storage.register_materialization(
                    file_id=file_id,
                    boundary_contract_id=boundary_contract_id,
                    materialization_type=materialization_type,
                    materialization_scope=materialization_scope or {},
                    materialization_backing_store=materialization_backing_store,
                    tenant_id=tenant_id,
                    user_id=user_id,
                    session_id=session_id,
                    file_reference=file_reference,
                    metadata=metadata or {}
                )
                self._logger.info(f"✅ Materialization registered: {file_id}")
                return True
            else:
                self._logger.warning("FileStorageAbstraction missing register_materialization method")
                return False
        except Exception as e:
            self._logger.error(f"Failed to register materialization: {e}")
            return False
    
    async def create_pending_intent(
        self,
        intent_type: str,
        target_artifact_id: str,
        tenant_id: str,
        session_id: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Create a pending intent for later execution.
        
        Used to queue intents for asynchronous execution, e.g., creating a
        pending parse_content intent after save_materialization.
        
        Args:
            intent_type: Type of intent (e.g., "parse_content")
            target_artifact_id: Artifact ID the intent targets
            tenant_id: Tenant identifier
            session_id: Session identifier
            context: Intent context (e.g., ingestion_profile, file_type)
        
        Returns:
            Pending intent ID if created, None otherwise
        """
        registry = self.registry
        if not registry:
            self._logger.warning("Registry not available for pending intent creation")
            return None
        
        try:
            if hasattr(registry, 'register_pending_intent'):
                pending_intent_id = await registry.register_pending_intent(
                    intent_type=intent_type,
                    target_artifact_id=target_artifact_id,
                    tenant_id=tenant_id,
                    session_id=session_id,
                    context=context or {}
                )
                self._logger.info(f"Created pending intent: {pending_intent_id}")
                return pending_intent_id
            else:
                self._logger.warning("Registry missing register_pending_intent method")
                return None
        except Exception as e:
            self._logger.warning(f"Failed to create pending intent: {e}")
            return None
