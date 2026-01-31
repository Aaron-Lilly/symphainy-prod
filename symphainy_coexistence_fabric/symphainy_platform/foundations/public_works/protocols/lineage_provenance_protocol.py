"""
Lineage Provenance Protocol - Abstraction Contract (Layer 2)

Defines the contract for lineage/provenance storage (data references and provenance entries).
Used by DataBrain. Lineage data lives in Supabase; this protocol keeps the backend swappable.

WHAT (Infrastructure Role): I define the contract for reference and provenance storage.
HOW (Infrastructure Implementation): Primary implementation is Supabase-backed (same source of truth
as artifact lineage: Registry, get_file_lineage). Arango may be used later to analyze lineage
(graph queries, replay); analysis would read from Supabase or a synced view.
"""

from typing import Protocol, Optional, List, Dict, Any


class LineageProvenanceProtocol(Protocol):
    """
    Protocol for lineage/provenance store operations.

    Consumers (DataBrain) depend on this protocol.
    Public Works provides Supabase-backed implementation (lineage in one place).
    Arango-backed implementation is optional for execution-provenance or analysis use cases.
    """

    async def collection_exists(self, collection_name: str) -> bool:
        """Return True if the collection exists."""
        ...

    async def create_collection(self, collection_name: str) -> bool:
        """Create collection if it does not exist. Return True if successful."""
        ...

    async def insert_document(
        self, collection_name: str, document: Dict[str, Any]
    ) -> bool:
        """Insert document into collection. Return True if successful."""
        ...

    async def get_document(
        self, collection_name: str, document_key: str
    ) -> Optional[Dict[str, Any]]:
        """Get document by key. Return None if not found."""
        ...

    async def execute_aql(
        self,
        query: str,
        bind_vars: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Execute AQL query. Return list of result documents."""
        ...
