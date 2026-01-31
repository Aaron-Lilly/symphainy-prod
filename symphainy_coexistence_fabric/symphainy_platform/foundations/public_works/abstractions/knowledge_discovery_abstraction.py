"""
Knowledge Discovery Abstraction - Pure Infrastructure (Layer 1)

Implements knowledge discovery operations using Meilisearch and ArangoDB Graph adapters.
Returns raw data only - no business logic.

WHAT (Infrastructure Role): I provide knowledge discovery storage services
HOW (Infrastructure Implementation): I use Meilisearch and ArangoDB Graph adapters

NOTE: This is PURE INFRASTRUCTURE - no business logic.
Business logic (search coordination, result merging, analytics tracking) belongs in Librarian Service.
Domain logic (recommendations, clustering) belongs in Realm services.
"""

from typing import Dict, Any, Optional, List, Any as AdapterType
from utilities import get_logger
from ..protocols.knowledge_discovery_protocol import KnowledgeDiscoveryProtocol


class KnowledgeDiscoveryAbstraction(KnowledgeDiscoveryProtocol):
    """
    Knowledge discovery abstraction - pure infrastructure.
    
    Returns raw data only (Dict[str, Any] or List[Dict[str, Any]]), not business objects.
    Business logic (search coordination, result merging, analytics tracking) belongs in Librarian Service.
    Domain logic (recommendations, clustering) belongs in Realm services.
    """
    
    def __init__(
        self,
        meilisearch_adapter: AdapterType,
        arango_graph_adapter: Optional[AdapterType] = None,
        arango_adapter: Optional[AdapterType] = None
    ):
        """
        Initialize Knowledge Discovery abstraction.
        
        Args:
            meilisearch_adapter: Meilisearch adapter for search (Layer 0)
            arango_graph_adapter: Optional ArangoDB Graph adapter for graph operations (Layer 0)
            arango_adapter: Optional ArangoDB adapter for persistent storage (Layer 0)
        """
        self.meilisearch = meilisearch_adapter
        self.arango_graph = arango_graph_adapter
        self.arango = arango_adapter
        self.logger = get_logger(self.__class__.__name__)
        
        # Index and graph names (infrastructure concern)
        self.knowledge_index = "knowledge_assets"
        self.analytics_index = "knowledge_analytics"
        self.knowledge_graph = "knowledge_graph"
        self.semantic_graph = "semantic_graph"
        
        self.logger.info("Knowledge Discovery Abstraction initialized (pure infrastructure)")
    
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
        
        Returns raw data from Meilisearch adapter. No coordination, no merging.
        
        Args:
            index: Meilisearch index name
            query: Search query string
            filters: Optional search filters
            limit: Maximum number of results
            offset: Result offset for pagination
        
        Returns:
            Raw search results from Meilisearch adapter
        """
        try:
            result = await self.meilisearch.search(
                index,
                query,
                filters=filters,
                limit=limit,
                offset=offset
            )
            
            self.logger.debug(f"Meilisearch search completed: {index}, query: {query[:50]}")
            
            # Return raw data
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to search Meilisearch {index}: {e}", exc_info=True)
            raise
    
    async def search_meilisearch_with_facets(
        self,
        index: str,
        query: str,
        facets: List[str],
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Search Meilisearch with facets - pure infrastructure.
        
        Returns raw data from Meilisearch adapter. No analytics enhancement.
        
        Args:
            index: Meilisearch index name
            query: Search query string
            facets: Facets to analyze
            limit: Maximum number of results
        
        Returns:
            Raw faceted search results from Meilisearch adapter
        """
        try:
            result = await self.meilisearch.search_with_facets(
                index,
                query,
                facets,
                limit
            )
            
            self.logger.debug(f"Meilisearch faceted search completed: {index}, facets: {facets}")
            
            # Return raw data
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to search Meilisearch with facets {index}: {e}", exc_info=True)
            raise
    
    async def get_meilisearch_analytics(
        self,
        index: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get Meilisearch analytics - pure infrastructure.
        
        Returns raw analytics data from Meilisearch adapter.
        
        Args:
            index: Meilisearch index name
            start_date: Optional start date
            end_date: Optional end date
        
        Returns:
            Raw analytics data from Meilisearch adapter
        """
        try:
            result = await self.meilisearch.get_search_analytics(
                index,
                start_date,
                end_date
            )
            
            self.logger.debug(f"Meilisearch analytics retrieved: {index}")
            
            # Return raw data
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to get Meilisearch analytics {index}: {e}", exc_info=True)
            raise
    
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
        try:
            result = await self.meilisearch.track_search_event(
                index,
                query,
                results_count,
                user_id
            )
            
            self.logger.debug(f"Meilisearch event tracked: {index}, query: {query[:50]}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to track Meilisearch event {index}: {e}", exc_info=True)
            raise
    
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
        
        Returns raw data from ArangoDB Graph adapter. No merging.
        
        Args:
            graph: ArangoDB Graph name
            query: Search query
            similarity_threshold: Minimum similarity score
        
        Returns:
            Raw semantic similarity results from ArangoDB Graph adapter
        """
        try:
            if not self.arango_graph:
                raise ValueError("ArangoDB Graph adapter not available")
            
            result = await self.arango_graph.find_semantic_similarity(
                graph,
                query,
                similarity_threshold
            )
            
            self.logger.debug(f"ArangoDB Graph search completed: {graph}, query: {query[:50]}")
            
            # Return raw data
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to search ArangoDB Graph {graph}: {e}", exc_info=True)
            raise
    
    async def get_arango_graph_neighbors(
        self,
        graph: str,
        node_id: str,
        collection_name: str,
        max_depth: int = 2
    ) -> List[Dict[str, Any]]:
        """
        Get neighbors from ArangoDB Graph - pure infrastructure.
        
        Returns raw data from ArangoDB Graph adapter.
        
        Args:
            graph: ArangoDB Graph name
            node_id: Node ID
            collection_name: Node collection name
            max_depth: Maximum traversal depth
        
        Returns:
            Raw neighbor results from ArangoDB Graph adapter
        """
        try:
            if not self.arango_graph:
                raise ValueError("ArangoDB Graph adapter not available")
            
            result = await self.arango_graph.get_neighbors(
                graph,
                node_id,
                collection_name,
                max_depth
            )
            
            self.logger.debug(f"ArangoDB Graph neighbors retrieved: {graph}, node: {node_id}")
            
            # Return raw data
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to get ArangoDB Graph neighbors {graph}: {e}", exc_info=True)
            raise
    
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
        
        Returns raw data from ArangoDB Graph adapter.
        
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
        try:
            if not self.arango_graph:
                raise ValueError("ArangoDB Graph adapter not available")
            
            result = await self.arango_graph.find_path(
                graph,
                start_id,
                start_collection,
                end_id,
                end_collection,
                max_paths
            )
            
            self.logger.debug(
                f"ArangoDB Graph path found: {graph}, "
                f"{start_collection}/{start_id} → {end_collection}/{end_id}"
            )
            
            # Return raw data
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to find ArangoDB Graph path {graph}: {e}", exc_info=True)
            raise
    
    async def get_arango_graph_stats(
        self,
        graph: str
    ) -> Dict[str, Any]:
        """
        Get ArangoDB Graph statistics - pure infrastructure.
        
        Returns raw statistics from ArangoDB Graph adapter.
        
        Args:
            graph: ArangoDB Graph name
        
        Returns:
            Raw graph statistics from ArangoDB Graph adapter
        """
        try:
            if not self.arango_graph:
                raise ValueError("ArangoDB Graph adapter not available")
            
            result = await self.arango_graph.get_graph_stats(graph)
            
            self.logger.debug(f"ArangoDB Graph stats retrieved: {graph}")
            
            # Return raw data
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to get ArangoDB Graph stats {graph}: {e}", exc_info=True)
            raise
    
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
        
        Returns raw data from ArangoDB adapter. No merging.
        
        Args:
            query: Search query
            similarity_threshold: Minimum similarity score
            max_results: Maximum number of results
        
        Returns:
            Raw semantic similarity results from ArangoDB adapter
        """
        try:
            if not self.arango:
                raise ValueError("ArangoDB adapter not available")
            
            result = await self.arango.find_semantic_similarity(
                query,
                similarity_threshold,
                max_results
            )
            
            self.logger.debug(f"ArangoDB semantic search completed: query: {query[:50]}")
            
            # Return raw data
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to search ArangoDB semantic: {e}", exc_info=True)
            raise
    
    async def get_arango_related_documents(
        self,
        asset_id: str,
        relationship_types: Optional[List[str]] = None,
        max_depth: int = 2
    ) -> List[Dict[str, Any]]:
        """
        Get related documents from ArangoDB - pure infrastructure.
        
        Returns raw data from ArangoDB adapter.
        
        Args:
            asset_id: Asset ID
            relationship_types: Optional relationship type filters
            max_depth: Maximum relationship depth
        
        Returns:
            Raw related document results from ArangoDB adapter
        """
        try:
            if not self.arango:
                raise ValueError("ArangoDB adapter not available")
            
            result = await self.arango.get_related_documents(
                asset_id,
                relationship_types,
                max_depth
            )
            
            self.logger.debug(f"ArangoDB related documents retrieved: {asset_id}")
            
            # Return raw data
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to get ArangoDB related documents {asset_id}: {e}", exc_info=True)
            raise
    
    async def get_arango_database_statistics(
        self
    ) -> Dict[str, Any]:
        """
        Get ArangoDB database statistics - pure infrastructure.
        
        Returns raw statistics from ArangoDB adapter.
        
        Returns:
            Raw database statistics from ArangoDB adapter
        """
        try:
            if not self.arango:
                raise ValueError("ArangoDB adapter not available")
            
            result = await self.arango.get_database_statistics()
            
            self.logger.debug("ArangoDB database statistics retrieved")
            
            # Return raw data
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to get ArangoDB database statistics: {e}", exc_info=True)
            raise
    
    # ============================================================================
    # NARROW PROTOCOL SURFACE (FullTextSearchProtocol / GraphQueryProtocol)
    # Decomposed from mega KnowledgeDiscoveryProtocol; same impl, narrow type for callers.
    # ============================================================================
    
    async def search(
        self,
        index: str,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """FullTextSearchProtocol: search index (delegates to search_meilisearch)."""
        return await self.search_meilisearch(index, query, filters=filters, limit=limit, offset=offset)
    
    async def search_with_facets(
        self,
        index: str,
        query: str,
        facets: List[str],
        limit: int = 10,
    ) -> Dict[str, Any]:
        """FullTextSearchProtocol: search with facets (delegates to search_meilisearch_with_facets)."""
        return await self.search_meilisearch_with_facets(index, query, facets, limit=limit)
    
    async def get_analytics(
        self,
        index: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """FullTextSearchProtocol: get analytics (delegates to get_meilisearch_analytics)."""
        return await self.get_meilisearch_analytics(index, start_date=start_date, end_date=end_date)
    
    async def track_event(
        self,
        index: str,
        query: str,
        results_count: int,
        user_id: Optional[str] = None,
    ) -> bool:
        """FullTextSearchProtocol: track event (delegates to track_meilisearch_event)."""
        return await self.track_meilisearch_event(index, query, results_count, user_id=user_id)
    
    async def search_graph(
        self,
        graph: str,
        query: str,
        similarity_threshold: float = 0.7,
    ) -> List[Dict[str, Any]]:
        """GraphQueryProtocol: search graph (delegates to search_arango_graph)."""
        return await self.search_arango_graph(graph, query, similarity_threshold=similarity_threshold)
    
    async def get_neighbors(
        self,
        graph: str,
        node_id: str,
        collection_name: str,
        max_depth: int = 2,
    ) -> List[Dict[str, Any]]:
        """GraphQueryProtocol: get neighbors (delegates to get_arango_graph_neighbors)."""
        return await self.get_arango_graph_neighbors(graph, node_id, collection_name, max_depth=max_depth)
    
    async def find_path(
        self,
        graph: str,
        start_id: str,
        start_collection: str,
        end_id: str,
        end_collection: str,
        max_paths: int = 5,
    ) -> List[List[str]]:
        """GraphQueryProtocol: find path (delegates to find_arango_graph_path)."""
        return await self.find_arango_graph_path(
            graph, start_id, start_collection, end_id, end_collection, max_paths=max_paths
        )
    
    async def get_stats(self, graph: str) -> Dict[str, Any]:
        """GraphQueryProtocol: get stats (delegates to get_arango_graph_stats)."""
        return await self.get_arango_graph_stats(graph)
    
    # ============================================================================
    # HEALTH CHECK
    # ============================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check health of knowledge discovery services.
        
        Returns:
            Dict containing health status information
        """
        try:
            health_status = {
                "overall_health": "healthy",
                "timestamp": None
            }
            
            # Check Meilisearch
            try:
                meilisearch_health = await self.meilisearch._get_health()
                health_status["meilisearch"] = "healthy" if meilisearch_health else "unhealthy"
            except Exception as e:
                self.logger.warning(f"Meilisearch health check failed: {e}")
                health_status["meilisearch"] = "unhealthy"
            
            # Check ArangoDB Graph (if available)
            if self.arango_graph:
                try:
                    # Check if ArangoDB adapter is connected
                    arango_graph_health = self.arango_graph.arango_adapter.is_connected()
                    health_status["arango_graph"] = "healthy" if arango_graph_health else "unhealthy"
                except Exception as e:
                    self.logger.warning(f"ArangoDB Graph health check failed: {e}")
                    health_status["arango_graph"] = "unhealthy"
            else:
                health_status["arango_graph"] = "not_configured"
            
            # Check ArangoDB (if available)
            if self.arango:
                try:
                    arango_health = await self.arango._get_health()
                    health_status["arango"] = "healthy" if arango_health else "unhealthy"
                except Exception as e:
                    self.logger.warning(f"ArangoDB health check failed: {e}")
                    health_status["arango"] = "unhealthy"
            else:
                health_status["arango"] = "not_configured"
            
            # Determine overall health
            health_status["overall_health"] = "healthy" if all(
                v in ["healthy", "not_configured"] for k, v in health_status.items() 
                if k not in ["overall_health", "timestamp"]
            ) else "unhealthy"
            
            from utilities import get_clock
            health_status["timestamp"] = get_clock().now_iso()
            
            return health_status
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}", exc_info=True)
            raise
