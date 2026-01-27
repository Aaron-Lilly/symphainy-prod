"""
Semantic Data Protocol - Abstraction Contract (Layer 2)

Defines the contract for semantic data operations (embeddings, semantic graphs).
Enables swappability between ArangoDB, vector databases, etc.

WHAT (Infrastructure Role): I define the contract for semantic data operations
HOW (Infrastructure Implementation): I specify the interface for semantic data storage and retrieval

NOTE: This is PURE INFRASTRUCTURE - no business logic.
Business logic (UUID generation, validation, metadata enhancement) belongs in Librarian Service.
"""

from typing import Protocol, Dict, Any, List, Optional


class SemanticDataProtocol(Protocol):
    """Protocol for semantic data operations (embeddings, semantic graphs) - pure infrastructure."""
    
    # ============================================================================
    # EMBEDDING OPERATIONS (Pure Infrastructure)
    # ============================================================================
    
    async def store_semantic_embeddings(
        self,
        embedding_documents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Store semantic embedding documents - pure infrastructure.
        
        Args:
            embedding_documents: List of pre-built embedding documents (with _key, content_id, etc.)
        
        Returns:
            Dict with storage result (count, success status)
        """
        ...
    
    async def get_semantic_embeddings(
        self,
        filter_conditions: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get semantic embeddings with filtering - pure infrastructure.
        
        Args:
            filter_conditions: Optional filter conditions (content_id, file_id, column_name, etc.)
            limit: Optional limit on number of results
        
        Returns:
            List of raw embedding documents from ArangoDB
        """
        ...
    
    async def query_by_semantic_id(
        self,
        semantic_id: str,
        filter_conditions: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Query embeddings by semantic ID - pure infrastructure.
        
        Args:
            semantic_id: Semantic ID to query
            filter_conditions: Optional additional filter conditions
        
        Returns:
            List of matching embedding documents
        """
        ...
    
    async def vector_search(
        self,
        query_embedding: List[float],
        filter_conditions: Optional[Dict[str, Any]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Vector similarity search - pure infrastructure.
        
        Args:
            query_embedding: Query vector (embedding)
            filter_conditions: Optional filter conditions
            limit: Maximum number of results
        
        Returns:
            List of matching embedding documents (vector similarity calculation is infrastructure)
        """
        ...
    
    # ============================================================================
    # SEMANTIC GRAPH OPERATIONS (Pure Infrastructure)
    # ============================================================================
    
    async def store_semantic_graph(
        self,
        node_documents: List[Dict[str, Any]],
        edge_documents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Store semantic graph documents - pure infrastructure.
        
        Args:
            node_documents: List of pre-built node documents (with _key, content_id, etc.)
            edge_documents: List of pre-built edge documents (with _key, _from, _to, etc.)
        
        Returns:
            Dict with storage result (node_count, edge_count, success status)
        """
        ...
    
    async def get_semantic_graph(
        self,
        filter_conditions: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get semantic graph - pure infrastructure.
        
        Args:
            filter_conditions: Optional filter conditions (content_id, file_id, etc.)
        
        Returns:
            Dict with 'nodes' and 'edges' lists (raw documents from ArangoDB)
        """
        ...
    
    # ============================================================================
    # CORRELATION MAP OPERATIONS (Pure Infrastructure)
    # ============================================================================
    
    async def store_correlation_map(
        self,
        correlation_document: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Store correlation map document - pure infrastructure.
        
        Args:
            correlation_document: Pre-built correlation map document (with _key, content_id, etc.)
        
        Returns:
            Dict with storage result
        """
        ...
    
    async def get_correlation_map(
        self,
        filter_conditions: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get correlation map - pure infrastructure.
        
        Args:
            filter_conditions: Optional filter conditions (content_id, file_id, etc.)
        
        Returns:
            Correlation map document or None if not found
        """
        ...
    
    # ============================================================================
    # HEALTH CHECK
    # ============================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check health of the semantic data system.
        
        Returns:
            Dict containing health status information
        """
        ...
