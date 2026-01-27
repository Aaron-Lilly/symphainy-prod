"""
Extract Embeddings Intent Service

Extracts semantic embeddings from parsed content using deterministic embeddings.

Contract: docs/intent_contracts/journey_content_deterministic_embedding/intent_extract_embeddings.md

WHAT (Service Role): I extract semantic embeddings from parsed content
HOW (Service Implementation): I coordinate EmbeddingService to create vector embeddings

NOTE: This uses the deterministic_embedding_id pattern. For chunk-based embeddings,
use hydrate_semantic_profile intent instead.
"""

from typing import Dict, Any, Optional

from utilities import get_logger, generate_event_id
from symphainy_platform.bases.intent_service_base import BaseIntentService
from symphainy_platform.runtime.execution_context import ExecutionContext
from symphainy_platform.runtime.intent_model import Intent
from symphainy_platform.runtime.artifact_registry import (
    SemanticDescriptor,
    ProducedBy,
    Materialization,
    LifecycleState
)


class ExtractEmbeddingsService(BaseIntentService):
    """
    Extract Embeddings Intent Service.
    
    Handles the `extract_embeddings` intent:
    - Validates parsed_file_id and deterministic_embedding_id parameters
    - Validates deterministic embedding exists
    - Creates semantic embeddings via EmbeddingService
    - Tracks embeddings for lineage
    - Registers artifact in State Surface
    
    Requires deterministic embeddings to be created first via create_deterministic_embeddings.
    """
    
    def __init__(
        self,
        public_works: Optional[Any] = None,
        state_surface: Optional[Any] = None,
        deterministic_embedding_service: Optional[Any] = None,
        embedding_service: Optional[Any] = None
    ):
        """
        Initialize Extract Embeddings Service.
        
        Args:
            public_works: Public Works Foundation Service
            state_surface: State Surface
            deterministic_embedding_service: DeterministicEmbeddingService instance
            embedding_service: EmbeddingService instance
        """
        super().__init__(
            service_id="extract_embeddings_service",
            intent_type="extract_embeddings",
            public_works=public_works,
            state_surface=state_surface
        )
        
        # Initialize services
        if deterministic_embedding_service:
            self.deterministic_embedding_service = deterministic_embedding_service
        else:
            from ..enabling_services.deterministic_embedding_service import DeterministicEmbeddingService
            self.deterministic_embedding_service = DeterministicEmbeddingService(public_works=public_works)
        
        if embedding_service:
            self.embedding_service = embedding_service
        else:
            from ..enabling_services.embedding_service import EmbeddingService
            self.embedding_service = EmbeddingService(public_works=public_works)
    
    async def execute(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Execute extract_embeddings intent.
        
        Args:
            intent: The extract_embeddings intent
            context: Execution context
        
        Returns:
            Dict with artifacts containing embedding info
        
        Raises:
            ValueError: If required parameters not provided or deterministic embedding not found
        """
        # Validate parameters
        parsed_file_id = intent.parameters.get("parsed_file_id")
        deterministic_embedding_id = intent.parameters.get("deterministic_embedding_id")
        
        if not parsed_file_id:
            raise ValueError("parsed_file_id is required for extract_embeddings intent")
        
        if not deterministic_embedding_id:
            raise ValueError(
                "deterministic_embedding_id is required for extract_embeddings intent. "
                "Please create deterministic embeddings first using create_deterministic_embeddings intent."
            )
        
        # Validate deterministic embedding exists
        deterministic_embedding = await self.deterministic_embedding_service.get_deterministic_embedding(
            deterministic_embedding_id=deterministic_embedding_id,
            context=context
        )
        
        if not deterministic_embedding:
            raise ValueError(f"Deterministic embedding not found: {deterministic_embedding_id}")
        
        # Get file_id from parsed results (for lineage tracking)
        file_id = await self._get_file_id_from_parsed_result(parsed_file_id, context.tenant_id)
        
        # Create semantic embeddings via EmbeddingService
        result = await self.embedding_service.create_semantic_embeddings(
            deterministic_embedding_id=deterministic_embedding_id,
            parsed_file_id=parsed_file_id,
            context=context
        )
        
        embedding_id = result.get("embedding_id")
        embeddings_count = result.get("embeddings_count", 0)
        
        # Track embeddings for lineage
        await self._track_embedding(
            embedding_id=embedding_id,
            parsed_file_id=parsed_file_id,
            file_id=file_id,
            embeddings_count=embeddings_count,
            tenant_id=context.tenant_id,
            context=context
        )
        
        # Register artifact in State Surface
        await self._register_embedding_artifact(
            embedding_id=embedding_id,
            parsed_file_id=parsed_file_id,
            deterministic_embedding_id=deterministic_embedding_id,
            embeddings_count=embeddings_count,
            context=context
        )
        
        # Create event
        event = {
            "type": "embeddings_created",
            "event_id": generate_event_id(),
            "parsed_file_id": parsed_file_id,
            "deterministic_embedding_id": deterministic_embedding_id,
            "embedding_id": embedding_id,
            "embeddings_count": embeddings_count
        }
        
        return {
            "artifacts": {
                "embeddings_created": True,
                "parsed_file_id": parsed_file_id,
                "deterministic_embedding_id": deterministic_embedding_id,
                "embedding_id": embedding_id,
                "embeddings_count": embeddings_count,
                "columns_processed": result.get("columns_processed", 0)
            },
            "events": [event]
        }
    
    async def _get_file_id_from_parsed_result(
        self,
        parsed_file_id: str,
        tenant_id: str
    ) -> Optional[str]:
        """Get file_id from parsed result for lineage tracking."""
        if not self.public_works:
            return None
        
        registry = getattr(self.public_works, 'registry_abstraction', None)
        if not registry:
            return None
        
        try:
            parsed_result = await registry.get_parsed_result(
                parsed_file_id=parsed_file_id,
                tenant_id=tenant_id
            )
            if parsed_result:
                return parsed_result.get("file_id")
        except Exception as e:
            self.logger.warning(f"Failed to get file_id from parsed result: {e}")
        
        return None
    
    async def _track_embedding(
        self,
        embedding_id: str,
        parsed_file_id: str,
        file_id: Optional[str],
        embeddings_count: int,
        tenant_id: str,
        context: ExecutionContext
    ) -> None:
        """Track embedding in registry for lineage."""
        if not self.public_works:
            return
        
        registry = getattr(self.public_works, 'registry_abstraction', None)
        if not registry:
            return
        
        try:
            await registry.track_embedding(
                embedding_id=embedding_id,
                parsed_file_id=parsed_file_id,
                file_id=file_id,
                arango_collection="structured_embeddings",
                arango_key=embedding_id,
                embedding_count=embeddings_count,
                model_name="sentence-transformers/all-mpnet-base-v2",
                tenant_id=tenant_id,
                session_id=context.session_id
            )
        except Exception as e:
            self.logger.warning(f"Failed to track embedding: {e}")
    
    async def _register_embedding_artifact(
        self,
        embedding_id: str,
        parsed_file_id: str,
        deterministic_embedding_id: str,
        embeddings_count: int,
        context: ExecutionContext
    ) -> None:
        """Register embedding artifact in State Surface."""
        if not context.state_surface:
            self.logger.warning("State Surface not available, skipping artifact registration")
            return
        
        try:
            # Create semantic descriptor
            semantic_descriptor = SemanticDescriptor(
                schema="embeddings_v1",
                record_count=embeddings_count,
                parser_type=None,
                embedding_model="sentence-transformers/all-mpnet-base-v2"
            )
            
            # Create produced_by (provenance)
            produced_by = ProducedBy(
                intent="extract_embeddings",
                execution_id=context.execution_id
            )
            
            # Register artifact (lifecycle_state = PENDING initially)
            artifact_registered = await context.state_surface.register_artifact(
                artifact_id=embedding_id,
                artifact_type="embeddings",
                tenant_id=context.tenant_id,
                produced_by=produced_by,
                semantic_descriptor=semantic_descriptor,
                parent_artifacts=[parsed_file_id, deterministic_embedding_id],
                lifecycle_state=LifecycleState.PENDING.value
            )
            
            if artifact_registered:
                # Add ArangoDB materialization
                materialization = Materialization(
                    materialization_id=f"mat_{embedding_id}",
                    storage_type="arango",
                    uri=f"structured_embeddings/{embedding_id}",
                    format="json",
                    compression=None
                )
                
                await context.state_surface.add_materialization(
                    artifact_id=embedding_id,
                    tenant_id=context.tenant_id,
                    materialization=materialization
                )
                
                # Update lifecycle state to READY
                await context.state_surface.update_artifact_lifecycle(
                    artifact_id=embedding_id,
                    tenant_id=context.tenant_id,
                    new_state=LifecycleState.READY.value,
                    reason="Semantic embeddings created and stored in ArangoDB"
                )
                
                self.logger.info(f"Registered embedding artifact: {embedding_id}")
            else:
                self.logger.error(f"Failed to register artifact: {embedding_id}")
                
        except Exception as e:
            self.logger.error(f"Error registering embedding artifact: {e}", exc_info=True)
