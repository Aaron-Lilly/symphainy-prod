"""
Knowledge Discovery Protocol - Abstraction Contract (Layer 2)

Defines the contract for knowledge discovery operations.
Enables swappability between Meilisearch, Redis Graph, ArangoDB, etc.

WHAT (Infrastructure Role): I define the contract for knowledge discovery operations
HOW (Infrastructure Implementation): I specify the interface for knowledge search and discovery

NOTE: This is PURE INFRASTRUCTURE - no business logic.
Business logic (search coordination, result merging, analytics tracking) belongs in Librarian Service.
"""

from typing import Protocol, Dict, Any, List, Optional


class KnowledgeDiscoveryProtocol(Protocol):
    """Protocol for knowledge discovery operations - pure infrastructure."""
    
    # ============================================================================
    # MEILISEARCH OPERATIONS (Pure Infrastructure)
    # ============================================================================
    
    async def search_meilisearch(
        self,
        index: str,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Search Meilisearch index - pure infrastructure.
        
        Args:
            index: Meilisearch index name
            query: Search query string
            filters: Optional search filters
            limit: Maximum number of results
            offset: Result offset for pagination
        
        Returns:
            Raw search results from Meilisearch adapter
        """
        ...
    
    async def search_meilisearch_with_facets(
        self,
        index: str,
        query: str,
        facets: List[str],
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Search Meilisearch with facets - pure infrastructure.
        
        Args:
            index: Meilisearch index name
            query: Search query string
            facets: Facets to analyze
            limit: Maximum number of results
        
        Returns:
            Raw faceted search results from Meilisearch adapter
        """
        ...
    
    async def get_meilisearch_analytics(
        self,
        index: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get Meilisearch analytics - pure infrastructure.
        
        Args:
            index: Meilisearch index name
            start_date: Optional start date
            end_date: Optional end date
        
        Returns:
            Raw analytics data from Meilisearch adapter
        """
        ...
    
    async def track_meilisearch_event(
        self,
        index: str,
        query: str,
        results_count: int,
        user_id: Optional[str] = None
    ) -> bool:
        """
        Track search event in Meilisearch - pure infrastructure.
        
        Args:
            index: Meilisearch index name
            query: Search query
            results_count: Number of results
            user_id: Optional user ID
        
        Returns:
            Success status
        """
        ...
    
    # ============================================================================
    # ARANGODB GRAPH OPERATIONS (Pure Infrastructure)
    # ============================================================================
    
    async def search_arango_graph(
        self,
        graph: str,
        query: str,
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Search ArangoDB Graph for semantic similarity - pure infrastructure.
        
        Args:
            graph: ArangoDB Graph name
            query: Search query
            similarity_threshold: Minimum similarity score
        
        Returns:
            Raw semantic similarity results from ArangoDB Graph adapter
        """
        ...
    
    async def get_arango_graph_neighbors(
        self,
        graph: str,
        node_id: str,
        collection_name: str,
        max_depth: int = 2
    ) -> List[Dict[str, Any]]:
        """
        Get neighbors from ArangoDB Graph - pure infrastructure.
        
        Args:
            graph: ArangoDB Graph name
            node_id: Node ID
            collection_name: Node collection name
            max_depth: Maximum traversal depth
        
        Returns:
            Raw neighbor results from ArangoDB Graph adapter
        """
        ...
    
    async def find_arango_graph_path(
        self,
        graph: str,
        start_id: str,
        start_collection: str,
        end_id: str,
        end_collection: str,
        max_paths: int = 5
    ) -> List[List[str]]:
        """
        Find path in ArangoDB Graph - pure infrastructure.
        
        Args:
            graph: ArangoDB Graph name
            start_id: Starting node ID
            start_collection: Starting node collection
            end_id: Ending node ID
            end_collection: Ending node collection
            max_paths: Maximum number of paths
        
        Returns:
            Raw path results from ArangoDB Graph adapter
        """
        ...
    
    async def get_arango_graph_stats(
        self,
        graph: str
    ) -> Dict[str, Any]:
        """
        Get ArangoDB Graph statistics - pure infrastructure.
        
        Args:
            graph: ArangoDB Graph name
        
        Returns:
            Raw graph statistics from ArangoDB Graph adapter
        """
        ...
    
    # ============================================================================
    # ARANGODB OPERATIONS (Pure Infrastructure)
    # ============================================================================
    
    async def search_arango_semantic(
        self,
        query: str,
        similarity_threshold: float = 0.7,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search ArangoDB for semantic similarity - pure infrastructure.
        
        Args:
            query: Search query
            similarity_threshold: Minimum similarity score
            max_results: Maximum number of results
        
        Returns:
            Raw semantic similarity results from ArangoDB adapter
        """
        ...
    
    async def get_arango_related_documents(
        self,
        asset_id: str,
        relationship_types: Optional[List[str]] = None,
        max_depth: int = 2
    ) -> List[Dict[str, Any]]:
        """
        Get related documents from ArangoDB - pure infrastructure.
        
        Args:
            asset_id: Asset ID
            relationship_types: Optional relationship type filters
            max_depth: Maximum relationship depth
        
        Returns:
            Raw related document results from ArangoDB adapter
        """
        ...
    
    async def get_arango_database_statistics(
        self
    ) -> Dict[str, Any]:
        """
        Get ArangoDB database statistics - pure infrastructure.
        
        Returns:
            Raw database statistics from ArangoDB adapter
        """
        ...
    
    # ============================================================================
    # HEALTH CHECK
    # ============================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check health of knowledge discovery services.
        
        Returns:
            Dict containing health status information
        """
        ...
