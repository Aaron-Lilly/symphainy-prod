"""
Arango Lineage Backend - LineageProvenanceProtocol implementation

Implements LineageProvenanceProtocol using ArangoAdapter for execution provenance.
Used by DataBrain. Artifact/file lineage lives in Supabase; this backend is for
runtime execution provenance (references, execution_id, operation). Arango can
also be used to analyze lineage (graph queries). Lives inside Public Works.
"""

from typing import Dict, Any, Optional, List

from utilities import get_logger
from ..adapters.arango_adapter import ArangoAdapter


class ArangoLineageBackend:
    """
    LineageProvenanceProtocol implementation using ArangoDB.

    Wraps ArangoAdapter for data_references and data_provenance collections.
    Created by foundation_service when Arango is available; exposed via get_lineage_backend().
    """

    def __init__(self, arango_adapter: ArangoAdapter):
        self._arango = arango_adapter
        self.logger = get_logger(self.__class__.__name__)

    async def collection_exists(self, collection_name: str) -> bool:
        """Return True if the collection exists."""
        if not self._arango:
            raise RuntimeError(
                "Arango adapter not wired; cannot check collection. Platform contract §8A."
            )
        return await self._arango.collection_exists(collection_name)

    async def create_collection(self, collection_name: str) -> bool:
        """Create collection if it does not exist. Return True if successful."""
        if not self._arango:
            raise RuntimeError(
                "Arango adapter not wired; cannot create collection. Platform contract §8A."
            )
        return await self._arango.create_collection(collection_name)

    async def insert_document(
        self, collection_name: str, document: Dict[str, Any]
    ) -> bool:
        """Insert document into collection. Return True if successful."""
        if not self._arango:
            raise RuntimeError(
                "Arango adapter not wired; cannot insert document. Platform contract §8A."
            )
        result = await self._arango.insert_document(collection_name, document)
        return bool(result)

    async def get_document(
        self, collection_name: str, document_key: str
    ) -> Optional[Dict[str, Any]]:
        """Get document by key. Return None if not found."""
        if not self._arango:
            raise RuntimeError(
                "Arango adapter not wired; cannot get document. Platform contract §8A."
            )
        return await self._arango.get_document(collection_name, document_key)

    async def execute_aql(
        self,
        query: str,
        bind_vars: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Execute AQL query. Return list of result documents."""
        if not self._arango:
            raise RuntimeError(
                "Arango adapter not wired; cannot execute AQL. Platform contract §8A."
            )
        return await self._arango.execute_aql(query, bind_vars=bind_vars or {})
