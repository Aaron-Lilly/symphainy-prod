"""
Vector Backend Protocol - Pluggable Vector Search Interface

Defines the contract for vector search backends (ArangoDB, Pinecone, Weaviate, etc.).
Enables swappability between different vector databases.

WHAT (Infrastructure Role): I define the contract for vector search operations
HOW (Infrastructure Implementation): I specify the interface for vector similarity search

NOTE: This is PURE INFRASTRUCTURE - no business logic.
Business logic (embedding generation, query construction) belongs in Realm services.
"""

from typing import Protocol, Dict, Any, List, Optional


class VectorBackendProtocol(Protocol):
    """
    Protocol for vector search backends - pure infrastructure.
    
    This protocol enables pluggable vector backends:
    - ArangoDB (default, implemented)
    - Pinecone (can be implemented)
    - Weaviate (can be implemented)
    - Other vector databases
    """
    
    async def vector_search(
        self,
        collection_name: str,
        query_vector: List[float],
        vector_field: str = "embedding",
        filter_conditions: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        similarity_threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform vector similarity search.
        
        Args:
            collection_name: Collection/index name to search in
            query_vector: Query vector (embedding) to search for
            vector_field: Field name containing the vector (default: "embedding")
            filter_conditions: Optional filter conditions (e.g., {"file_id": "..."})
            limit: Maximum number of results
            similarity_threshold: Optional minimum similarity score (0.0 to 1.0)
        
        Returns:
            List of documents with similarity scores, sorted by similarity (highest first)
            Each document should include a "similarity" field with the similarity score
        """
        ...
    
    async def create_collection(
        self,
        collection_name: str,
        vector_dimension: Optional[int] = None,
        collection_type: str = "document"
    ) -> bool:
        """
        Create collection/index for vector storage.
        
        Args:
            collection_name: Collection/index name
            vector_dimension: Optional vector dimension (for vector-specific backends)
            collection_type: Collection type ("document" or "edge")
        
        Returns:
            True if collection created successfully
        """
        ...
    
    async def collection_exists(self, collection_name: str) -> bool:
        """
        Check if collection/index exists.
        
        Args:
            collection_name: Collection/index name
        
        Returns:
            True if collection exists
        """
        ...
