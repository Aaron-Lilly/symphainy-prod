"""
Vector Store Protocol - Abstraction Contract (Layer 2)

Narrow protocol for vector/embedding storage and search.
Decomposed from SemanticDataProtocol (mega). Swap unit: vector backend (e.g. Arango to Pinecone).

WHAT (Infrastructure Role): I define the contract for vector/embedding operations
HOW (Infrastructure Implementation): I specify the interface for embedding storage and vector search

NOTE: This is PURE INFRASTRUCTURE - no business logic.
"""

from typing import Protocol, Dict, Any, List, Optional


class VectorStoreProtocol(Protocol):
    """Protocol for vector/embedding storage and similarity search - pure infrastructure."""

    async def store_semantic_embeddings(
        self,
        embedding_documents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Store semantic embedding documents - pure infrastructure."""
        ...

    async def get_semantic_embeddings(
        self,
        filter_conditions: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Get semantic embeddings with filtering - pure infrastructure."""
        ...

    async def query_by_semantic_id(
        self,
        semantic_id: str,
        filter_conditions: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Query embeddings by semantic ID - pure infrastructure."""
        ...

    async def vector_search(
        self,
        query_embedding: List[float],
        filter_conditions: Optional[Dict[str, Any]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Vector similarity search - pure infrastructure."""
        ...
