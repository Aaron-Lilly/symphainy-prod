"""
Artifact Registry - Authoritative Artifact Resolution

Provides artifact registry within State Surface for authoritative artifact resolution.

WHAT (Runtime Role): I provide artifact authority and resolution
HOW (Runtime Implementation): I maintain artifact registry with lifecycle state

Key Principle: Runtime (via State Surface) is the sole authority for resolving artifacts.
Storage systems are never queried directly by application code.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum

from utilities import get_logger, get_clock
from symphainy_platform.foundations.public_works.protocols.state_protocol import StateManagementProtocol


class LifecycleState(str, Enum):
    """Artifact lifecycle states."""
    PENDING = "PENDING"  # Registered but not yet materialized
    READY = "READY"  # Valid and accessible
    FAILED = "FAILED"  # Intent executed but artifact invalid
    ARCHIVED = "ARCHIVED"  # Retained but not active
    DELETED = "DELETED"  # Marked for deletion


@dataclass
class Materialization:
    """Single materialization of an artifact."""
    materialization_id: str
    storage_type: str  # "gcs" | "arango" | "duckdb" | "vector_store"
    uri: str
    format: str  # "json" | "parquet" | "csv" | "faiss"
    compression: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class SemanticDescriptor:
    """What the artifact means (independent of storage)."""
    schema: str  # logical schema / version
    record_count: Optional[int] = None
    parser_type: Optional[str] = None
    embedding_model: Optional[str] = None
    # Add other semantic fields as needed
    # NO storage info here


@dataclass
class ProducedBy:
    """Provenance: which intent execution produced this artifact."""
    intent: str  # "ingest_file", "parse_content", "extract_embeddings"
    execution_id: str


@dataclass
class ArtifactRecord:
    """Authoritative artifact registry entry."""
    # Identity (required fields first)
    artifact_id: str
    artifact_type: str  # "file" | "parsed_content" | "embeddings" | "summary" | etc.
    tenant_id: str
    
    # Provenance (required fields)
    produced_by: ProducedBy
    
    # Lifecycle (required field)
    lifecycle_state: str  # "PENDING" | "READY" | "FAILED" | "ARCHIVED" | "DELETED"
    
    # Semantics (required field)
    semantic_descriptor: SemanticDescriptor
    
    # Optional fields (with defaults) come last
    parent_artifacts: List[str] = field(default_factory=list)  # lineage
    materializations: List[Materialization] = field(default_factory=list)  # how it's stored
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "artifact_id": self.artifact_id,
            "artifact_type": self.artifact_type,
            "tenant_id": self.tenant_id,
            "produced_by": {
                "intent": self.produced_by.intent,
                "execution_id": self.produced_by.execution_id
            },
            "parent_artifacts": self.parent_artifacts,
            "lifecycle_state": self.lifecycle_state,
            "semantic_descriptor": {
                "schema": self.semantic_descriptor.schema,
                "record_count": self.semantic_descriptor.record_count,
                "parser_type": self.semantic_descriptor.parser_type,
                "embedding_model": self.semantic_descriptor.embedding_model
            },
            "materializations": [
                {
                    "materialization_id": m.materialization_id,
                    "storage_type": m.storage_type,
                    "uri": m.uri,
                    "format": m.format,
                    "compression": m.compression,
                    "created_at": m.created_at
                }
                for m in self.materializations
            ],
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ArtifactRecord":
        """Create from dictionary."""
        return cls(
            artifact_id=data["artifact_id"],
            artifact_type=data["artifact_type"],
            tenant_id=data["tenant_id"],
            produced_by=ProducedBy(
                intent=data["produced_by"]["intent"],
                execution_id=data["produced_by"]["execution_id"]
            ),
            parent_artifacts=data.get("parent_artifacts", []),
            lifecycle_state=data["lifecycle_state"],
            semantic_descriptor=SemanticDescriptor(
                schema=data["semantic_descriptor"]["schema"],
                record_count=data["semantic_descriptor"].get("record_count"),
                parser_type=data["semantic_descriptor"].get("parser_type"),
                embedding_model=data["semantic_descriptor"].get("embedding_model")
            ),
            materializations=[
                Materialization(
                    materialization_id=m["materialization_id"],
                    storage_type=m["storage_type"],
                    uri=m["uri"],
                    format=m["format"],
                    compression=m.get("compression"),
                    created_at=m.get("created_at", datetime.utcnow().isoformat())
                )
                for m in data.get("materializations", [])
            ],
            created_at=data.get("created_at", datetime.utcnow().isoformat()),
            updated_at=data.get("updated_at", datetime.utcnow().isoformat())
        )


class ArtifactRegistry:
    """
    Artifact registry within State Surface.
    
    Provides authoritative artifact resolution and lifecycle management.
    
    Key Principle: Runtime (via State Surface) is the sole authority for resolving artifacts.
    """
    
    def __init__(
        self,
        state_abstraction: Optional[StateManagementProtocol] = None,
        use_memory: bool = False
    ):
        """
        Initialize artifact registry.
        
        Args:
            state_abstraction: State management abstraction (from Public Works)
            use_memory: If True, use in-memory storage (for tests)
        """
        self.state_abstraction = state_abstraction
        self.use_memory = use_memory
        self._memory_store: Dict[str, ArtifactRecord] = {}
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
    
    def _get_state_key(self, artifact_id: str, tenant_id: str) -> str:
        """Get state key for artifact."""
        return f"artifact:{tenant_id}:{artifact_id}"
    
    async def register_artifact(
        self,
        artifact_id: str,
        artifact_type: str,
        tenant_id: str,
        produced_by: ProducedBy,
        semantic_descriptor: SemanticDescriptor,
        parent_artifacts: Optional[List[str]] = None,
        lifecycle_state: str = LifecycleState.PENDING.value
    ) -> bool:
        """
        Register a new artifact.
        
        Args:
            artifact_id: Stable, global artifact identifier
            artifact_type: Type of artifact
            tenant_id: Tenant identifier
            produced_by: Intent execution that produced this artifact
            semantic_descriptor: What the artifact means
            parent_artifacts: Lineage (optional)
            lifecycle_state: Initial lifecycle state (default: PENDING)
        
        Returns:
            True if registration successful
        """
        try:
            # Validate lifecycle state
            if lifecycle_state not in [s.value for s in LifecycleState]:
                raise ValueError(f"Invalid lifecycle_state: {lifecycle_state}")
            
            # Create artifact record
            artifact = ArtifactRecord(
                artifact_id=artifact_id,
                artifact_type=artifact_type,
                tenant_id=tenant_id,
                produced_by=produced_by,
                parent_artifacts=parent_artifacts or [],
                lifecycle_state=lifecycle_state,
                semantic_descriptor=semantic_descriptor,
                materializations=[]  # Materializations added separately
            )
            
            state_key = self._get_state_key(artifact_id, tenant_id)
            
            if self.use_memory:
                self._memory_store[state_key] = artifact
                self.logger.info(f"Artifact registered (memory): {artifact_id} ({artifact_type})")
                return True
            
            if not self.state_abstraction:
                raise RuntimeError(
                    "State abstraction not wired; cannot register artifact (use_memory=False). Platform contract §8A."
                )
            
            # Store in State Surface (durable)
            success = await self.state_abstraction.store_state(
                state_id=state_key,
                state_data=artifact.to_dict(),
                metadata={
                    "type": "artifact_registry",
                    "artifact_id": artifact_id,
                    "artifact_type": artifact_type,
                    "tenant_id": tenant_id,
                    "backend": "arango_db",  # Artifacts must be durable
                    "strategy": "durable"
                },
                ttl=None  # No TTL for artifacts
            )
            
            if success:
                self.logger.info(f"Artifact registered: {artifact_id} ({artifact_type}) - {lifecycle_state}")
            else:
                self.logger.error(f"Failed to register artifact: {artifact_id}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to register artifact {artifact_id}: {e}", exc_info=True)
            return False
    
    async def resolve_artifact(
        self,
        artifact_id: str,
        artifact_type: str,
        tenant_id: str
    ) -> Optional[ArtifactRecord]:
        """
        Resolve artifact by ID with validation.
        
        Validates:
        - Artifact exists
        - Artifact type matches
        - Tenant access
        - Lifecycle state is accessible (READY or ARCHIVED)
        
        Args:
            artifact_id: Artifact identifier
            artifact_type: Expected artifact type
            tenant_id: Tenant identifier (for access control)
        
        Returns:
            ArtifactRecord if found and accessible, None otherwise
        
        Raises:
            ValueError: If artifact not found or not accessible
        """
        try:
            state_key = self._get_state_key(artifact_id, tenant_id)
            
            # Retrieve from storage
            if self.use_memory:
                artifact_data = self._memory_store.get(state_key)
            elif not self.state_abstraction:
                raise RuntimeError(
                    "State abstraction not wired; cannot resolve artifact (use_memory=False). Platform contract §8A."
                )
            else:
                artifact_data = await self.state_abstraction.retrieve_state(state_key)
            
            if not artifact_data:
                self.logger.warning(f"Artifact not found: {artifact_id}")
                return None
            
            # Convert to ArtifactRecord
            if isinstance(artifact_data, dict):
                artifact = ArtifactRecord.from_dict(artifact_data)
            else:
                artifact = artifact_data
            
            # Validate artifact type
            if artifact.artifact_type != artifact_type:
                self.logger.warning(
                    f"Artifact type mismatch: expected {artifact_type}, got {artifact.artifact_type}"
                )
                return None
            
            # Validate tenant access
            if artifact.tenant_id != tenant_id:
                self.logger.warning(
                    f"Tenant access denied: artifact belongs to {artifact.tenant_id}, requested by {tenant_id}"
                )
                return None
            
            # Validate lifecycle state (must be accessible)
            if artifact.lifecycle_state not in [LifecycleState.READY.value, LifecycleState.ARCHIVED.value]:
                self.logger.warning(
                    f"Artifact not accessible: lifecycle_state={artifact.lifecycle_state}, "
                    f"must be READY or ARCHIVED"
                )
                return None
            
            self.logger.debug(f"Artifact resolved: {artifact_id} ({artifact_type})")
            return artifact
            
        except RuntimeError as e:
            if "Platform contract §8A" in str(e):
                raise
            self.logger.error(f"Failed to resolve artifact {artifact_id}: {e}", exc_info=True)
            return None
        except Exception as e:
            self.logger.error(f"Failed to resolve artifact {artifact_id}: {e}", exc_info=True)
            return None
    
    async def add_materialization(
        self,
        artifact_id: str,
        tenant_id: str,
        materialization: Materialization
    ) -> bool:
        """
        Add a materialization to an existing artifact.
        
        Allows one artifact to have multiple storage forms.
        
        Args:
            artifact_id: Artifact identifier
            tenant_id: Tenant identifier
            materialization: Materialization to add
        
        Returns:
            True if successful
        """
        try:
            state_key = self._get_state_key(artifact_id, tenant_id)
            
            # Retrieve existing artifact
            if self.use_memory:
                artifact = self._memory_store.get(state_key)
            elif not self.state_abstraction:
                raise RuntimeError(
                    "State abstraction not wired; cannot add materialization (use_memory=False). Platform contract §8A."
                )
            else:
                artifact_data = await self.state_abstraction.retrieve_state(state_key)
                if artifact_data:
                    artifact = ArtifactRecord.from_dict(artifact_data) if isinstance(artifact_data, dict) else artifact_data
                else:
                    artifact = None
            
            if not artifact:
                self.logger.error(f"Artifact not found for materialization: {artifact_id}")
                return False
            
            # Add materialization
            artifact.materializations.append(materialization)
            artifact.updated_at = self.clock.now_iso()
            
            # Store updated artifact
            if self.use_memory:
                self._memory_store[state_key] = artifact
                return True
            
            if not self.state_abstraction:
                raise RuntimeError(
                    "State abstraction not wired; cannot add materialization (use_memory=False). Platform contract §8A."
                )
            
            success = await self.state_abstraction.store_state(
                state_id=state_key,
                state_data=artifact.to_dict(),
                metadata={
                    "type": "artifact_registry",
                    "artifact_id": artifact_id,
                    "artifact_type": artifact.artifact_type,
                    "tenant_id": tenant_id,
                    "backend": "arango_db",
                    "strategy": "durable"
                },
                ttl=None
            )
            
            if success:
                self.logger.info(
                    f"Materialization added to artifact {artifact_id}: "
                    f"{materialization.storage_type}://{materialization.uri}"
                )
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to add materialization to artifact {artifact_id}: {e}", exc_info=True)
            return False
    
    async def update_artifact_lifecycle(
        self,
        artifact_id: str,
        tenant_id: str,
        new_state: str,
        reason: Optional[str] = None
    ) -> bool:
        """
        Update artifact lifecycle state.
        
        Valid state transitions:
        - PENDING → READY (materialization complete)
        - PENDING → FAILED (materialization failed)
        - READY → ARCHIVED (retention policy)
        - ARCHIVED → DELETED (deletion policy)
        - Any → FAILED (validation failure)
        
        Args:
            artifact_id: Artifact identifier
            tenant_id: Tenant identifier
            new_state: New lifecycle state
            reason: Optional reason for state change
        
        Returns:
            True if successful
        """
        try:
            # Validate lifecycle state
            if new_state not in [s.value for s in LifecycleState]:
                raise ValueError(f"Invalid lifecycle_state: {new_state}")
            
            state_key = self._get_state_key(artifact_id, tenant_id)
            
            # Retrieve existing artifact
            if self.use_memory:
                artifact = self._memory_store.get(state_key)
            elif not self.state_abstraction:
                artifact = self._memory_store.get(state_key)
            else:
                artifact_data = await self.state_abstraction.retrieve_state(state_key)
                if artifact_data:
                    artifact = ArtifactRecord.from_dict(artifact_data) if isinstance(artifact_data, dict) else artifact_data
                else:
                    artifact = None
            
            if not artifact:
                self.logger.error(f"Artifact not found for lifecycle update: {artifact_id}")
                return False
            
            # Validate tenant access
            if artifact.tenant_id != tenant_id:
                self.logger.warning(f"Tenant access denied for lifecycle update: {artifact_id}")
                return False
            
            # Update lifecycle state
            old_state = artifact.lifecycle_state
            artifact.lifecycle_state = new_state
            artifact.updated_at = self.clock.now_iso()
            
            # Store updated artifact
            if self.use_memory:
                self._memory_store[state_key] = artifact
                self.logger.info(
                    f"Artifact lifecycle updated: {artifact_id} {old_state} → {new_state}"
                    + (f" ({reason})" if reason else "")
                )
                return True
            
            if not self.state_abstraction:
                raise RuntimeError(
                    "State abstraction not wired; cannot update lifecycle (use_memory=False). Platform contract §8A."
                )
            
            success = await self.state_abstraction.store_state(
                state_id=state_key,
                state_data=artifact.to_dict(),
                metadata={
                    "type": "artifact_registry",
                    "artifact_id": artifact_id,
                    "artifact_type": artifact.artifact_type,
                    "tenant_id": tenant_id,
                    "backend": "arango_db",
                    "strategy": "durable"
                },
                ttl=None
            )
            
            if success:
                self.logger.info(
                    f"Artifact lifecycle updated: {artifact_id} {old_state} → {new_state}"
                    + (f" ({reason})" if reason else "")
                )
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to update artifact lifecycle {artifact_id}: {e}", exc_info=True)
            return False
