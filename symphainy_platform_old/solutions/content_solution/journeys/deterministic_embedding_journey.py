"""
Deterministic Embedding Journey Orchestrator

Composes the deterministic embedding creation journey:
1. create_deterministic_embeddings - Create deterministic embeddings from parsed content
2. save_embeddings - Save embeddings as artifact

WHAT (Journey Role): I orchestrate embedding creation
HOW (Journey Implementation): I compose create_deterministic_embeddings + save_embeddings intents

Key Principle: Deterministic embeddings enable reproducible semantic analysis.
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[5]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional
import hashlib

from utilities import get_logger, generate_event_id, get_clock
from symphainy_platform.runtime.execution_context import ExecutionContext
from symphainy_platform.runtime.artifact_registry import (
    ArtifactRecord,
    SemanticDescriptor,
    ProducedBy,
    Materialization,
    LifecycleState
)
from symphainy_platform.realms.utils.structured_artifacts import create_structured_artifact


class DeterministicEmbeddingJourney:
    """
    Deterministic Embedding Journey Orchestrator.
    
    Journey Flow:
    1. User selects parsed content artifact
    2. create_deterministic_embeddings creates embeddings
    3. save_embeddings saves embedding artifact
    
    Provides MCP Tools:
    - content_create_embeddings: Create embeddings for parsed content
    - content_extract_semantic_embeddings: Extract semantic embeddings
    """
    
    JOURNEY_ID = "deterministic_embedding"
    JOURNEY_NAME = "Deterministic Embedding Creation"
    
    def __init__(
        self,
        public_works: Optional[Any] = None,
        state_surface: Optional[Any] = None
    ):
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
        self.public_works = public_works
        self.state_surface = state_surface
        self.journey_id = self.JOURNEY_ID
        self.journey_name = self.JOURNEY_NAME
        self.telemetry_service = None
    
    async def compose_journey(
        self,
        context: ExecutionContext,
        journey_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Compose the deterministic embedding journey.
        
        Args:
            context: Execution context
            journey_params: Journey parameters including:
                - parsed_artifact_id: Parsed content artifact to embed
                - embedding_model: Optional embedding model to use
                - chunk_strategy: Optional chunking strategy
                - auto_save: If True, automatically save embeddings (default: True)
        """
        journey_params = journey_params or {}
        self.logger.info(f"Composing journey: {self.journey_name}")
        
        journey_execution_id = generate_event_id()
        
        try:
            # Validate parameters
            validation_result = self._validate_journey_params(journey_params)
            if not validation_result["valid"]:
                raise ValueError(f"Invalid journey parameters: {validation_result['error']}")
            
            parsed_artifact_id = journey_params.get("parsed_artifact_id")
            
            # Step 1: Execute create_deterministic_embeddings
            embedding_result = await self._execute_create_embeddings(context, journey_params)
            
            if not embedding_result.get("success", False):
                raise RuntimeError(f"create_deterministic_embeddings failed: {embedding_result.get('error')}")
            
            embedding_artifact_id = embedding_result.get("embedding_artifact_id")
            
            # Step 2: Execute save_embeddings (if auto_save)
            auto_save = journey_params.get("auto_save", True)
            save_result = None
            
            if auto_save:
                save_result = await self._execute_save_embeddings(
                    context,
                    embedding_artifact_id=embedding_artifact_id,
                    parent_artifact_id=parsed_artifact_id
                )
                
                if not save_result.get("success", False):
                    raise RuntimeError(f"save_embeddings failed: {save_result.get('error')}")
            
            return self._build_journey_result(
                embedding_result=embedding_result,
                save_result=save_result,
                journey_execution_id=journey_execution_id,
                auto_save=auto_save
            )
            
        except Exception as e:
            self.logger.error(f"Journey failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "journey_id": self.journey_id,
                "journey_execution_id": journey_execution_id,
                "artifacts": {},
                "events": [{"type": "journey_failed", "journey_id": self.journey_id, "error": str(e)}]
            }
    
    def _validate_journey_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        if not params.get("parsed_artifact_id"):
            return {"valid": False, "error": "parsed_artifact_id is required"}
        return {"valid": True}
    
    async def _execute_create_embeddings(self, context: ExecutionContext, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute create_deterministic_embeddings intent."""
        self.logger.info(f"Executing create_deterministic_embeddings for: {params.get('parsed_artifact_id')}")
        
        try:
            parsed_artifact_id = params.get("parsed_artifact_id")
            embedding_model = params.get("embedding_model", "default")
            chunk_strategy = params.get("chunk_strategy", "semantic")
            
            # Calculate embedding fingerprint for idempotency
            embedding_fingerprint = hashlib.sha256(
                f"{parsed_artifact_id}:{embedding_model}:{chunk_strategy}".encode('utf-8')
            ).hexdigest()
            
            # Generate embedding artifact ID
            embedding_artifact_id = generate_event_id()
            
            # Create embedding (simplified - in real impl would use EmbeddingService)
            embeddings = {
                "source_artifact_id": parsed_artifact_id,
                "embedding_model": embedding_model,
                "chunk_strategy": chunk_strategy,
                "created_at": self.clock.now_utc().isoformat(),
                "embedding_vectors": [],  # Would contain actual vectors
                "chunk_count": 0,
                "dimensions": 1536  # Standard embedding dimension
            }
            
            # Create embedding artifact
            artifact_record = ArtifactRecord(
                artifact_id=embedding_artifact_id,
                artifact_type="embeddings",
                semantic_descriptor=SemanticDescriptor(
                    domain="content",
                    entity_type="embeddings",
                    description=f"Embeddings from artifact {parsed_artifact_id}",
                    tags=["embeddings", embedding_model, chunk_strategy]
                ),
                produced_by=ProducedBy(
                    intent_type="create_deterministic_embeddings",
                    execution_id=context.execution_id,
                    service_id="deterministic_embedding_journey"
                ),
                lifecycle_state=LifecycleState.PENDING,
                materializations=[],
                tenant_id=context.tenant_id,
                parent_artifacts=[parsed_artifact_id]
            )
            
            # Register artifact
            state_surface = self.state_surface or context.state_surface
            if state_surface:
                await state_surface.register_artifact(artifact_record)
            
            return {
                "success": True,
                "embedding_artifact_id": embedding_artifact_id,
                "embedding_fingerprint": embedding_fingerprint,
                "parent_artifact_id": parsed_artifact_id,
                "embedding_model": embedding_model,
                "chunk_strategy": chunk_strategy,
                "embeddings": embeddings
            }
            
        except Exception as e:
            self.logger.error(f"create_deterministic_embeddings failed: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    async def _execute_save_embeddings(self, context: ExecutionContext, embedding_artifact_id: str, parent_artifact_id: str) -> Dict[str, Any]:
        """Execute save_embeddings intent."""
        self.logger.info(f"Executing save_embeddings for: {embedding_artifact_id}")
        
        try:
            state_surface = self.state_surface or context.state_surface
            if state_surface:
                await state_surface.update_artifact_lifecycle(
                    artifact_id=embedding_artifact_id,
                    new_state=LifecycleState.READY,
                    tenant_id=context.tenant_id
                )
            
            fingerprint = hashlib.sha256(
                f"{embedding_artifact_id}:{context.session_id}".encode('utf-8')
            ).hexdigest()
            
            return {
                "success": True,
                "embedding_artifact_id": embedding_artifact_id,
                "lifecycle_state": "READY",
                "embeddings_fingerprint": fingerprint
            }
            
        except Exception as e:
            self.logger.error(f"save_embeddings failed: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    def _build_journey_result(self, embedding_result: Dict, save_result: Optional[Dict], journey_execution_id: str, auto_save: bool) -> Dict[str, Any]:
        embedding_artifact_id = embedding_result.get("embedding_artifact_id")
        lifecycle_state = "READY" if auto_save and save_result else "PENDING"
        
        semantic_payload = {
            "embedding_artifact_id": embedding_artifact_id,
            "artifact_type": "embeddings",
            "lifecycle_state": lifecycle_state,
            "parent_artifact_id": embedding_result.get("parent_artifact_id"),
            "embedding_model": embedding_result.get("embedding_model"),
            "chunk_strategy": embedding_result.get("chunk_strategy"),
            "embedding_fingerprint": embedding_result.get("embedding_fingerprint"),
            "journey_execution_id": journey_execution_id
        }
        
        renderings = {"embedding_result": embedding_result, "save_result": save_result}
        
        artifact = create_structured_artifact(
            result_type="deterministic_embedding",
            semantic_payload=semantic_payload,
            renderings=renderings
        )
        
        events = [{"type": "embeddings_created", "embedding_artifact_id": embedding_artifact_id}]
        if auto_save and save_result:
            events.append({"type": "embeddings_saved", "embedding_artifact_id": embedding_artifact_id})
        
        return {
            "success": True,
            "journey_id": self.journey_id,
            "journey_execution_id": journey_execution_id,
            "embedding_artifact_id": embedding_artifact_id,
            "lifecycle_state": lifecycle_state,
            "artifacts": {"embeddings": artifact},
            "events": events
        }
    
    def get_soa_apis(self) -> Dict[str, Dict[str, Any]]:
        """Get SOA API definitions for MCP tool registration."""
        return {
            "create_embeddings": {
                "handler": self._handle_create_embeddings,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "parsed_artifact_id": {"type": "string", "description": "Parsed content artifact ID"},
                        "embedding_model": {"type": "string", "description": "Embedding model to use"},
                        "chunk_strategy": {"type": "string", "description": "Chunking strategy"},
                        "user_context": {"type": "object", "description": "User context"}
                    },
                    "required": ["parsed_artifact_id"]
                },
                "description": "Create deterministic embeddings from parsed content"
            },
            "extract_semantic_embeddings": {
                "handler": self._handle_extract_semantic,
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "parsed_artifact_id": {"type": "string", "description": "Parsed content artifact ID"},
                        "deterministic_embedding_id": {"type": "string", "description": "Deterministic embedding ID"},
                        "user_context": {"type": "object", "description": "User context"}
                    },
                    "required": ["parsed_artifact_id"]
                },
                "description": "Extract semantic embeddings for similarity search"
            }
        }
    
    async def _handle_create_embeddings(self, **kwargs) -> Dict[str, Any]:
        user_context = kwargs.get("user_context", {})
        context = ExecutionContext(
            execution_id=generate_event_id(),
            tenant_id=user_context.get("tenant_id", "default"),
            session_id=user_context.get("session_id", generate_event_id()),
            solution_id=user_context.get("solution_id", "content_solution")
        )
        context.state_surface = self.state_surface
        
        return await self.compose_journey(context, {
            "parsed_artifact_id": kwargs.get("parsed_artifact_id"),
            "embedding_model": kwargs.get("embedding_model"),
            "chunk_strategy": kwargs.get("chunk_strategy"),
            "auto_save": True
        })
    
    async def _handle_extract_semantic(self, **kwargs) -> Dict[str, Any]:
        # Similar to create_embeddings but focuses on semantic extraction
        return await self._handle_create_embeddings(**kwargs)
