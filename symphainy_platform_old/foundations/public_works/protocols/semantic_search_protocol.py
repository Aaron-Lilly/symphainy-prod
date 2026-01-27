"""
Semantic Search Protocol - Abstraction Contract (Layer 2)

Defines the interface for semantic search operations.
Enables swappability between Meilisearch, Elasticsearch, etc.

WHAT (Infrastructure Role): I define the contract for semantic search operations
HOW (Infrastructure Implementation): I specify the interface for semantic search
"""

from typing import Protocol, Dict, Any, List, Optional


class SemanticSearchProtocol(Protocol):
    """Protocol for semantic search operations."""
    
    async def search(
        self,
        query: str,
        index: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Perform semantic search.
        
        Args:
            query: Search query
            index: Index name
            filters: Optional filters
            limit: Result limit
            offset: Result offset
        
        Returns:
            Dict containing search results
        """
        ...
    
    async def index_document(
        self,
        index: str,
        document: Dict[str, Any]
    ) -> bool:
        """
        Index a document.
        
        Args:
            index: Index name
            document: Document to index
        
        Returns:
            bool: True if successful
        """
        ...
    
    async def index_documents(
        self,
        index: str,
        documents: List[Dict[str, Any]]
    ) -> bool:
        """
        Index multiple documents.
        
        Args:
            index: Index name
            documents: Documents to index
        
        Returns:
            bool: True if successful
        """
        ...
    
    async def delete_document(
        self,
        index: str,
        document_id: str
    ) -> bool:
        """
        Delete a document from the index.
        
        Args:
            index: Index name
            document_id: Document ID to delete
        
        Returns:
            bool: True if successful
        """
        ...
    
    async def search_with_facets(
        self,
        query: str,
        index: str,
        facets: List[str],
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Perform faceted search.
        
        Args:
            query: Search query
            index: Index name
            facets: Facets to analyze
            limit: Result limit
        
        Returns:
            Dict containing results and facet distribution
        """
        ...
