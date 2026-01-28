"""
Base Handler - Common functionality for all content handlers
"""

from typing import Dict, Any, Optional, List
from abc import ABC

from utilities import get_logger, get_clock
from symphainy_platform.runtime.intent_model import Intent
from symphainy_platform.runtime.execution_context import ExecutionContext
from symphainy_platform.runtime.artifact_registry import (
    SemanticDescriptor,
    ProducedBy
)


class BaseContentHandler(ABC):
    """
    Base class for content intent handlers.
    
    Provides common functionality:
    - Logger
    - Clock
    - Public Works access
    - Enabling services
    - Artifact indexing helper
    """
    
    def __init__(self, public_works: Optional[Any] = None):
        """
        Initialize base handler.
        
        Args:
            public_works: Public Works Foundation Service
        """
        self.public_works = public_works
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
        
        # Initialize enabling services (lazy, can be overridden by subclasses)
        self._file_parser_service = None
        self._deterministic_embedding_service = None
        self._embedding_service = None
        self._deterministic_chunking_service = None
        self._semantic_signal_extractor = None
    
    @property
    def file_parser_service(self):
        """Lazy initialization of FileParserService."""
        if self._file_parser_service is None:
            from symphainy_platform.foundations.libraries.parsing.file_parser_service import FileParserService
            self._file_parser_service = FileParserService(public_works=self.public_works)
        return self._file_parser_service
    
    @property
    def deterministic_embedding_service(self):
        """Lazy initialization of DeterministicEmbeddingService."""
        if self._deterministic_embedding_service is None:
            from symphainy_platform.foundations.libraries.embeddings.deterministic_embedding_service import DeterministicEmbeddingService
            self._deterministic_embedding_service = DeterministicEmbeddingService(public_works=self.public_works)
        return self._deterministic_embedding_service
    
    @property
    def embedding_service(self):
        """Lazy initialization of EmbeddingService."""
        if self._embedding_service is None:
            from symphainy_platform.civic_systems.agentic.agents.embedding_agent import EmbeddingAgent as EmbeddingService
            self._embedding_service = EmbeddingService(public_works=self.public_works)
        return self._embedding_service
    
    async def _index_artifact(
        self,
        artifact_id: str,
        artifact_type: str,
        tenant_id: str,
        lifecycle_state: str,
        semantic_descriptor: SemanticDescriptor,
        produced_by: ProducedBy,
        parent_artifacts: List[str],
        context: ExecutionContext
    ) -> bool:
        """
        Index artifact in artifact_index (Supabase discovery layer).
        
        This is called after State Surface registration to also write to artifact_index
        for discovery/exploration queries (UI dropdowns).
        
        Includes structured lineage metadata (CTO-recommended).
        """
        if not self.public_works:
            self.logger.debug("Public Works not available, skipping artifact indexing")
            return False
        
        registry = getattr(self.public_works, 'registry_abstraction', None)
        if not registry:
            self.logger.debug("Registry abstraction not available, skipping artifact indexing")
            return False
        
        try:
            # Build structured lineage (CTO-recommended)
            lineage = {
                "derived_from": parent_artifacts,
                "derivation_intent": produced_by.intent,
                "derivation_run_id": produced_by.execution_id,
                "generation": len(parent_artifacts),  # Simple generation count
                "root_artifact_id": parent_artifacts[0] if parent_artifacts else artifact_id
            }
            
            # Prepare artifact index record
            artifact_record = {
                "artifact_id": artifact_id,
                "artifact_type": artifact_type,
                "tenant_id": tenant_id,
                "lifecycle_state": lifecycle_state,
                "semantic_descriptor": {
                    "schema": semantic_descriptor.schema,
                    "record_count": semantic_descriptor.record_count,
                    "parser_type": semantic_descriptor.parser_type,
                    "embedding_model": semantic_descriptor.embedding_model
                },
                "produced_by": {
                    "intent": produced_by.intent,
                    "execution_id": produced_by.execution_id
                },
                "parent_artifacts": parent_artifacts,  # Keep for backward compatibility
                "lineage": lineage  # NEW: Structured lineage metadata
            }
            
            # Insert into artifact_index via RegistryAbstraction
            result = await registry.insert_record(
                table="artifact_index",
                data=artifact_record,
                user_context={"tenant_id": tenant_id}
            )
            
            if result.get("success"):
                self.logger.debug(f"Artifact indexed: {artifact_id} ({artifact_type}) with lineage")
                return True
            else:
                self.logger.warning(f"Failed to index artifact {artifact_id}: {result.get('error')}")
                return False
                
        except Exception as e:
            # Don't fail if indexing fails (State Surface is authoritative)
            self.logger.warning(f"Failed to index artifact {artifact_id}: {e}")
            return False
