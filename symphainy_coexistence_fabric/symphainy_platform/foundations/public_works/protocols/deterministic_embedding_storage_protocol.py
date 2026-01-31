"""
Deterministic Embedding Storage Protocol - Abstraction Contract (Layer 2)

Defines the interface for deterministic embedding storage (DuckDB-backed).
Used for schema fingerprints, pattern signatures, and repeatable embeddings.

WHAT (Infrastructure Role): I define the contract for deterministic embedding storage
HOW (Infrastructure Implementation): I specify the interface for store/get embeddings
"""

from typing import Protocol, Optional, Dict, Any, List


class DeterministicEmbeddingStorageProtocol(Protocol):
    """Protocol for deterministic embedding storage (e.g. DuckDB-backed)."""

    async def get_deterministic_embedding(
        self,
        embedding_id: str,
        tenant_id: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Get deterministic embedding by ID.

        Args:
            embedding_id: Embedding identifier
            tenant_id: Optional tenant identifier (for filtering)

        Returns:
            Embedding document (schema_fingerprint, pattern_signature, etc.) or None
        """
        ...

    async def store_deterministic_embedding(
        self,
        embedding_id: str,
        parsed_file_id: str,
        schema_fingerprint: Dict[str, Any],
        pattern_signature: Dict[str, Any],
        tenant_id: str,
        session_id: Optional[str] = None,
    ) -> bool:
        """
        Store deterministic embedding (schema fingerprint + pattern signature).

        Args:
            embedding_id: Embedding identifier
            parsed_file_id: Parsed file identifier
            schema_fingerprint: Schema fingerprint dictionary
            pattern_signature: Pattern signature dictionary
            tenant_id: Tenant identifier
            session_id: Optional session identifier

        Returns:
            True if successful, False otherwise
        """
        ...

    async def query_deterministic_embeddings(
        self,
        filter_conditions: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Query deterministic embeddings with optional filters.

        Args:
            filter_conditions: Optional dictionary of filter conditions
            limit: Optional limit on number of results

        Returns:
            List of embedding documents
        """
        ...
