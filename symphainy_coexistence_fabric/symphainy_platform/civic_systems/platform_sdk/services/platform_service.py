"""
Platform Service (ctx.platform) - Capability-Oriented Operations

Provides capability-oriented operations that wrap Public Works protocols.
Primary purpose: enable infrastructure swappability while providing clean interfaces.

Operations:
    - parse(file_reference, file_type, options) → Parse documents
    - analyze(data, analysis_type) → Data analysis
    - visualize(data, viz_type, options) → Generate visualizations
    - embed(content, model) → Generate embeddings
    - ingest(source, source_type, options) → Ingest data
    - store(artifact_id, data, options) → Store artifacts

Usage:
    # Parse a PDF
    result = await ctx.platform.parse(file_ref, file_type="pdf")
    
    # Generate visualization
    viz = await ctx.platform.visualize(data, viz_type="chart")
    
    # Ingest from API
    result = await ctx.platform.ingest(api_endpoint, source_type="api")
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
        """Initialize abstractions from Public Works."""
        # Visual generation
        self._visual_generation = getattr(public_works, 'visual_generation_abstraction', None)
        if self._visual_generation:
            self._logger.debug("✅ VisualGenerationAbstraction initialized")
        
        # Ingestion
        self._ingestion = getattr(public_works, 'ingestion_abstraction', None)
        if self._ingestion:
            self._logger.debug("✅ IngestionAbstraction initialized")
        
        # Semantic data
        self._semantic_data = getattr(public_works, 'semantic_data_abstraction', None)
        if self._semantic_data:
            self._logger.debug("✅ SemanticDataAbstraction initialized")
        
        # Deterministic compute (embeddings)
        self._deterministic_compute = getattr(public_works, 'deterministic_compute_abstraction', None)
        if self._deterministic_compute:
            self._logger.debug("✅ DeterministicComputeAbstraction initialized")
        
        # File storage
        self._file_storage = getattr(public_works, 'file_storage_abstraction', None)
        if self._file_storage:
            self._logger.debug("✅ FileStorageAbstraction initialized")
        
        # Artifact storage
        self._artifact_storage = getattr(public_works, 'artifact_storage_abstraction', None)
        if self._artifact_storage:
            self._logger.debug("✅ ArtifactStorageAbstraction initialized")
        
        # Initialize parsers by type
        self._initialize_parsers(public_works)
    
    def _initialize_parsers(self, public_works: Any) -> None:
        """Initialize parsing abstractions by file type."""
        parser_mappings = {
            "csv": "csv_processing_abstraction",
            "excel": "excel_processing_abstraction",
            "pdf": "pdf_processing_abstraction",
            "word": "word_processing_abstraction",
            "docx": "word_processing_abstraction",
            "html": "html_processing_abstraction",
            "image": "image_processing_abstraction",
            "json": "json_processing_abstraction",
            "text": "text_processing_abstraction",
            "txt": "text_processing_abstraction",
            "kreuzberg": "kreuzberg_processing_abstraction",
            "mainframe": "mainframe_processing_abstraction",
            "data_model": "data_model_processing_abstraction",
            "workflow": "workflow_processing_abstraction",
            "bpmn": "workflow_processing_abstraction",
            "sop": "sop_processing_abstraction",
        }
        
        for file_type, attr_name in parser_mappings.items():
            parser = getattr(public_works, attr_name, None)
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
        Generate embeddings for content.
        
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
    
    # ========================================================================
    # INGESTION OPERATIONS
    # ========================================================================
    
    async def ingest(
        self,
        source: str,
        source_type: str,
        tenant_id: str,
        session_id: str,
        options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Ingest data from a source.
        
        Args:
            source: Source identifier (file path, API endpoint, etc.)
            source_type: Type of source ("file", "api", "edi", etc.)
            tenant_id: Tenant identifier
            session_id: Session identifier
            options: Ingestion options
        
        Returns:
            Dict with ingestion result
        """
        if not self._ingestion:
            raise RuntimeError("IngestionAbstraction not available.")
        
        try:
            request = IngestionRequest(
                source=source,
                source_type=source_type,
                tenant_id=tenant_id,
                session_id=session_id,
                options=options or {}
            )
            
            result = await self._ingestion.ingest(request)
            
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
            "store_artifact": self._artifact_storage is not None,
            "semantic": self._semantic_data is not None,
        }
