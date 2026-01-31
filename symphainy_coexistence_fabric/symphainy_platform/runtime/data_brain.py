"""
Data Brain - Runtime-Native Data Cognition

Runtime-native data cognition for data references, provenance, and virtualization.

WHAT (Runtime Role): I provide runtime-native data cognition
HOW (Runtime Implementation): I track data references and provenance, enable virtualization

Key Principle: Data Brain stores references, not data. It enables data mash without
ingestion, explainable interpretation, and replayable migration.

Critical Rule: Phase 2 Data Brain never returns raw data by default — only references.
"""

from typing import Dict, Any, List, Optional, TYPE_CHECKING
from dataclasses import dataclass, field
from datetime import datetime

from utilities import get_logger, get_clock, generate_event_id

if TYPE_CHECKING:
    from symphainy_platform.foundations.public_works.protocols.lineage_provenance_protocol import LineageProvenanceProtocol


@dataclass
class DataReference:
    """Data reference structure."""
    reference_id: str
    reference_type: str  # e.g., "file", "document", "policy", "record"
    storage_location: str  # Where the data is stored (e.g., GCS path, ArangoDB collection)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: get_clock().now_utc())
    execution_id: Optional[str] = None  # Execution that created this reference
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert reference to dictionary."""
        return {
            "reference_id": self.reference_id,
            "reference_type": self.reference_type,
            "storage_location": self.storage_location,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "execution_id": self.execution_id,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DataReference":
        """Create reference from dictionary."""
        return cls(
            reference_id=data["reference_id"],
            reference_type=data["reference_type"],
            storage_location=data["storage_location"],
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data.get("created_at", get_clock().now_utc().isoformat())),
            execution_id=data.get("execution_id"),
        )


@dataclass
class ProvenanceEntry:
    """Provenance entry structure."""
    entry_id: str
    reference_id: str
    execution_id: str
    operation: str  # e.g., "created", "updated", "derived_from"
    source_reference_ids: List[str] = field(default_factory=list)  # References this was derived from
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: get_clock().now_utc())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert provenance entry to dictionary."""
        return {
            "entry_id": self.entry_id,
            "reference_id": self.reference_id,
            "execution_id": self.execution_id,
            "operation": self.operation,
            "source_reference_ids": self.source_reference_ids,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProvenanceEntry":
        """Create provenance entry from dictionary."""
        return cls(
            entry_id=data["entry_id"],
            reference_id=data["reference_id"],
            execution_id=data["execution_id"],
            operation=data["operation"],
            source_reference_ids=data.get("source_reference_ids", []),
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data.get("created_at", get_clock().now_utc().isoformat())),
        )


class DataBrain:
    """
    Runtime-native data cognition.
    
    Provides:
    - Data reference registration
    - Provenance tracking
    - Virtual query interface (scaffolding)
    
    Critical Rule: Returns references, not raw data.
    """
    
    def __init__(
        self,
        lineage_backend: Optional["LineageProvenanceProtocol"] = None,
        use_memory: bool = False
    ):
        """
        Initialize Data Brain.

        Uses LineageProvenanceProtocol (e.g. from public_works.get_lineage_backend());
        adapters must not escape Public Works. Artifact lineage lives in Supabase;
        this backend is for runtime execution provenance (Arango-backed).
        
        Args:
            lineage_backend: Optional lineage backend (from Public Works get_lineage_backend())
            use_memory: If True, use in-memory storage (for tests)
        """
        self.lineage_backend = lineage_backend
        self.use_memory = use_memory
        self._memory_references: Dict[str, DataReference] = {}
        self._memory_provenance: Dict[str, List[ProvenanceEntry]] = {}
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
        
        # Collection names
        self.references_collection = "data_references"
        self.provenance_collection = "data_provenance"
    
    async def initialize(self) -> bool:
        """
        Initialize Data Brain (create collections if needed).
        
        Returns:
            True if initialization successful
        """
        if self.use_memory:
            return True
        
        if not self.lineage_backend:
            raise RuntimeError(
                "Lineage backend not wired; cannot initialize Data Brain (use_memory=False). Platform contract §8A."
            )
        
        try:
            # Ensure collections exist
            if not await self.lineage_backend.collection_exists(self.references_collection):
                await self.lineage_backend.create_collection(self.references_collection)
                self.logger.info(f"Created collection: {self.references_collection}")
            
            if not await self.lineage_backend.collection_exists(self.provenance_collection):
                await self.lineage_backend.create_collection(self.provenance_collection)
                self.logger.info(f"Created collection: {self.provenance_collection}")
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize Data Brain: {e}", exc_info=True)
            return False
    
    async def register_reference(
        self,
        reference_id: str,
        reference_type: str,
        storage_location: str,
        metadata: Optional[Dict[str, Any]] = None,
        execution_id: Optional[str] = None
    ) -> bool:
        """
        Register a data reference.
        
        Args:
            reference_id: Unique reference identifier
            reference_type: Type of reference (e.g., "file", "document", "policy")
            storage_location: Where the data is stored
            metadata: Optional reference metadata
            execution_id: Optional execution that created this reference
        
        Returns:
            True if registration successful
        """
        try:
            reference = DataReference(
                reference_id=reference_id,
                reference_type=reference_type,
                storage_location=storage_location,
                metadata=metadata or {},
                execution_id=execution_id,
            )
            
            if self.use_memory:
                self._memory_references[reference_id] = reference
                return True
            
            if not self.lineage_backend:
                raise RuntimeError(
                    "Lineage backend not wired; cannot register reference (use_memory=False). Platform contract §8A."
                )
            
            # Store via lineage backend (Arango-backed inside Public Works)
            document = reference.to_dict()
            document["_key"] = reference_id
            
            result = await self.lineage_backend.insert_document(
                self.references_collection,
                document
            )
            
            if result:
                self.logger.debug(f"Registered data reference: {reference_id}")
                return True
            else:
                self.logger.error(f"Failed to register data reference: {reference_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to register reference: {e}", exc_info=True)
            return False
    
    async def get_reference(self, reference_id: str) -> Optional[DataReference]:
        """
        Get a data reference.
        
        Critical Rule: Returns reference, not raw data.
        
        Args:
            reference_id: Reference identifier
        
        Returns:
            Data reference or None if not found
        """
        try:
            if self.use_memory:
                return self._memory_references.get(reference_id)
            
            if not self.lineage_backend:
                raise RuntimeError(
                    "Lineage backend not wired; cannot get reference (use_memory=False). Platform contract §8A."
                )
            
            # Get via lineage backend
            document = await self.lineage_backend.get_document(
                self.references_collection,
                reference_id
            )
            
            if document:
                # Remove ArangoDB internal fields
                document.pop("_key", None)
                document.pop("_id", None)
                document.pop("_rev", None)
                return DataReference.from_dict(document)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get reference: {e}", exc_info=True)
            return None
    
    async def list_references(
        self,
        reference_type: Optional[str] = None,
        execution_id: Optional[str] = None,
        limit: int = 100
    ) -> List[DataReference]:
        """
        List data references by criteria.
        
        Args:
            reference_type: Optional reference type filter
            execution_id: Optional execution ID filter
            limit: Maximum number of references to return
        
        Returns:
            List of data references
        """
        try:
            if self.use_memory:
                references = list(self._memory_references.values())
                
                # Apply filters
                if reference_type:
                    references = [r for r in references if r.reference_type == reference_type]
                if execution_id:
                    references = [r for r in references if r.execution_id == execution_id]
                
                return references[:limit]
            
            if not self.lineage_backend:
                raise RuntimeError(
                    "Lineage backend not wired; cannot list references (use_memory=False). Platform contract §8A."
                )
            
            # Query via lineage backend
            query = f"""
            FOR ref IN {self.references_collection}
                FILTER @reference_type == null OR ref.reference_type == @reference_type
                FILTER @execution_id == null OR ref.execution_id == @execution_id
                LIMIT @limit
                RETURN ref
            """
            
            bind_vars = {
                "reference_type": reference_type,
                "execution_id": execution_id,
                "limit": limit
            }
            
            results = await self.lineage_backend.execute_aql(query, bind_vars=bind_vars)
            
            references = []
            for doc in results:
                # Remove ArangoDB internal fields
                doc.pop("_key", None)
                doc.pop("_id", None)
                doc.pop("_rev", None)
                references.append(DataReference.from_dict(doc))
            
            return references
            
        except Exception as e:
            self.logger.error(f"Failed to list references: {e}", exc_info=True)
            return []
    
    async def track_provenance(
        self,
        reference_id: str,
        execution_id: str,
        operation: str,
        source_reference_ids: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Track provenance for a data reference.
        
        Args:
            reference_id: Reference identifier
            execution_id: Execution identifier
            operation: Operation type (e.g., "created", "updated", "derived_from")
            source_reference_ids: Optional list of source reference IDs
            metadata: Optional provenance metadata
        
        Returns:
            True if tracking successful
        """
        try:
            entry_id = generate_event_id()
            
            provenance_entry = ProvenanceEntry(
                entry_id=entry_id,
                reference_id=reference_id,
                execution_id=execution_id,
                operation=operation,
                source_reference_ids=source_reference_ids or [],
                metadata=metadata or {},
            )
            
            if self.use_memory:
                if reference_id not in self._memory_provenance:
                    self._memory_provenance[reference_id] = []
                self._memory_provenance[reference_id].append(provenance_entry)
                return True
            
            if not self.lineage_backend:
                raise RuntimeError(
                    "Lineage backend not wired; cannot track provenance (use_memory=False). Platform contract §8A."
                )
            
            # Store via lineage backend
            document = provenance_entry.to_dict()
            document["_key"] = entry_id
            
            result = await self.lineage_backend.insert_document(
                self.provenance_collection,
                document
            )
            
            if result:
                self.logger.debug(f"Tracked provenance: {reference_id}/{operation}")
                return True
            else:
                self.logger.error(f"Failed to track provenance: {reference_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to track provenance: {e}", exc_info=True)
            return False
    
    async def get_provenance(
        self,
        reference_id: str,
        limit: int = 100
    ) -> List[ProvenanceEntry]:
        """
        Get provenance chain for a data reference.
        
        Args:
            reference_id: Reference identifier
            limit: Maximum number of provenance entries to return
        
        Returns:
            List of provenance entries (chronological order)
        """
        try:
            if self.use_memory:
                entries = self._memory_provenance.get(reference_id, [])
                # Sort by created_at
                entries.sort(key=lambda e: e.created_at)
                return entries[:limit]
            
            if not self.lineage_backend:
                raise RuntimeError(
                    "Lineage backend not wired; cannot get provenance (use_memory=False). Platform contract §8A."
                )
            
            # Query via lineage backend
            query = f"""
            FOR prov IN {self.provenance_collection}
                FILTER prov.reference_id == @reference_id
                SORT prov.created_at ASC
                LIMIT @limit
                RETURN prov
            """
            
            bind_vars = {
                "reference_id": reference_id,
                "limit": limit
            }
            
            results = await self.lineage_backend.execute_aql(query, bind_vars=bind_vars)
            
            entries = []
            for doc in results:
                # Remove ArangoDB internal fields
                doc.pop("_key", None)
                doc.pop("_id", None)
                doc.pop("_rev", None)
                entries.append(ProvenanceEntry.from_dict(doc))
            
            return entries
            
        except Exception as e:
            self.logger.error(f"Failed to get provenance: {e}", exc_info=True)
            return []
    
    async def get_lineage(
        self,
        reference_id: str,
        max_depth: int = 10
    ) -> Dict[str, Any]:
        """
        Get full lineage for a data reference (references it was derived from).
        
        Args:
            reference_id: Reference identifier
            max_depth: Maximum lineage depth
        
        Returns:
            Lineage graph (references and relationships)
        """
        try:
            # Get provenance chain
            provenance = await self.get_provenance(reference_id, limit=1000)
            
            # Build lineage graph
            lineage = {
                "reference_id": reference_id,
                "provenance_chain": [entry.to_dict() for entry in provenance],
                "source_references": [],
                "depth": 0
            }
            
            # Collect source references
            source_ids = set()
            for entry in provenance:
                source_ids.update(entry.source_reference_ids)
            
            # Get source references (up to max_depth)
            if source_ids and max_depth > 0:
                for source_id in list(source_ids)[:max_depth]:
                    source_ref = await self.get_reference(source_id)
                    if source_ref:
                        lineage["source_references"].append(source_ref.to_dict())
            
            return lineage
            
        except Exception as e:
            self.logger.error(f"Failed to get lineage: {e}", exc_info=True)
            return {
                "reference_id": reference_id,
                "provenance_chain": [],
                "source_references": [],
                "depth": 0
            }
