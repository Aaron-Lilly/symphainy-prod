"""
ArangoDB Graph Adapter - Raw Technology Client (Layer 0)

Real ArangoDB graph operations wrapper with no business logic.
This is the raw technology layer for ArangoDB graph operations.

Replaces Redis Graph adapter.

WHAT (Infrastructure Role): I provide raw ArangoDB graph operations
HOW (Infrastructure Implementation): I use real ArangoDB graph API with no business logic
"""

from typing import Dict, Any, Optional, List
from arango.exceptions import ArangoError

from utilities import get_logger
from .arango_adapter import ArangoAdapter


class ArangoGraphAdapter:
    """
    Raw ArangoDB graph operations wrapper - no business logic.
    
    This adapter provides direct access to ArangoDB graph operations without
    any business logic or abstraction. It's the raw technology layer.
    
    Replaces Redis Graph adapter.
    """
    
    def __init__(self, arango_adapter: ArangoAdapter):
        """
        Initialize ArangoDB Graph adapter.
        
        Args:
            arango_adapter: ArangoDB adapter instance
        """
        self.arango_adapter = arango_adapter
        self.logger = get_logger(self.__class__.__name__)
    
    def _get_db(self):
        """Get ArangoDB database instance."""
        return self.arango_adapter.get_database()
    
    # ============================================================================
    # RAW GRAPH OPERATIONS
    # ============================================================================
    
    async def create_graph(
        self,
        graph_name: str,
        edge_definitions: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """
        Create graph in ArangoDB.
        
        Args:
            graph_name: Graph name
            edge_definitions: Optional edge definitions
                [{"collection": "edges", "from": ["nodes"], "to": ["nodes"]}]
        
        Returns:
            True if graph created successfully
        """
        db = self._get_db()
        if not db:
            return False
        
        try:
            if db.has_graph(graph_name):
                self.logger.debug(f"Graph already exists: {graph_name}")
                return True
            
            db.create_graph(
                graph_name,
                edge_definitions=edge_definitions or []
            )
            self.logger.info(f"Graph created: {graph_name}")
            return True
        except ArangoError as e:
            self.logger.error(f"Failed to create graph {graph_name}: {e}")
            return False
    
    async def graph_exists(self, graph_name: str) -> bool:
        """Check if graph exists."""
        db = self._get_db()
        if not db:
            return False
        try:
            return db.has_graph(graph_name)
        except Exception as e:
            self.logger.error(f"Failed to check graph existence: {e}")
            return False
    
    async def delete_graph(self, graph_name: str) -> bool:
        """Delete graph from ArangoDB."""
        db = self._get_db()
        if not db:
            return False
        try:
            db.delete_graph(graph_name)
            self.logger.info(f"Graph deleted: {graph_name}")
            return True
        except ArangoError as e:
            self.logger.error(f"Failed to delete graph {graph_name}: {e}")
            return False
    
    # ============================================================================
    # RAW NODE OPERATIONS
    # ============================================================================
    
    async def create_node(
        self,
        graph_name: str,
        collection_name: str,
        node_id: str,
        properties: Dict[str, Any]
    ) -> bool:
        """
        Create graph node in ArangoDB.
        
        Args:
            graph_name: Graph name
            collection_name: Vertex collection name
            node_id: Node ID (will be used as _key)
            properties: Node properties
        
        Returns:
            True if node created successfully
        """
        db = self._get_db()
        if not db:
            return False
        
        try:
            # Ensure graph exists
            if not await self.graph_exists(graph_name):
                await self.create_graph(graph_name)
            
            # Ensure vertex collection exists
            if not await self.arango_adapter.collection_exists(collection_name):
                await self.arango_adapter.create_collection(collection_name, "document")
            
            # Insert node
            document = {"_key": node_id, **properties}
            result = await self.arango_adapter.insert_document(collection_name, document)
            
            if result:
                self.logger.debug(f"Node created: {graph_name}/{collection_name}/{node_id}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to create node {node_id}: {e}")
            return False
    
    async def get_node(
        self,
        graph_name: str,
        collection_name: str,
        node_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get node from graph."""
        return await self.arango_adapter.get_document(collection_name, node_id)
    
    async def update_node(
        self,
        graph_name: str,
        collection_name: str,
        node_id: str,
        properties: Dict[str, Any]
    ) -> bool:
        """Update node in graph."""
        result = await self.arango_adapter.update_document(
            collection_name,
            node_id,
            properties
        )
        return result is not None
    
    async def delete_node(
        self,
        graph_name: str,
        collection_name: str,
        node_id: str
    ) -> bool:
        """Delete node from graph."""
        return await self.arango_adapter.delete_document(collection_name, node_id)
    
    # ============================================================================
    # RAW RELATIONSHIP OPERATIONS
    # ============================================================================
    
    async def create_relationship(
        self,
        graph_name: str,
        edge_collection: str,
        from_node_id: str,
        from_collection: str,
        to_node_id: str,
        to_collection: str,
        relationship_type: str,
        properties: Dict[str, Any]
    ) -> bool:
        """
        Create graph relationship (edge) in ArangoDB.
        
        Args:
            graph_name: Graph name
            edge_collection: Edge collection name
            from_node_id: Source node ID
            from_collection: Source node collection
            to_node_id: Target node ID
            to_collection: Target node collection
            relationship_type: Relationship type (stored in properties)
            properties: Edge properties
        
        Returns:
            True if relationship created successfully
        """
        db = self._get_db()
        if not db:
            return False
        
        try:
            # Ensure graph exists
            if not await self.graph_exists(graph_name):
                # Create graph with edge definition
                edge_def = [{
                    "collection": edge_collection,
                    "from": [from_collection],
                    "to": [to_collection]
                }]
                await self.create_graph(graph_name, edge_definitions=edge_def)
            
            # Ensure edge collection exists
            if not await self.arango_adapter.collection_exists(edge_collection):
                await self.arango_adapter.create_collection(edge_collection, "edge")
            
            # Create edge
            edge_doc = {
                "_from": f"{from_collection}/{from_node_id}",
                "_to": f"{to_collection}/{to_node_id}",
                "type": relationship_type,
                **properties
            }
            
            # Generate edge key from from/to
            edge_key = f"{from_node_id}_{to_node_id}_{relationship_type}"
            edge_doc["_key"] = edge_key
            
            result = await self.arango_adapter.insert_document(edge_collection, edge_doc)
            
            if result:
                self.logger.debug(
                    f"Relationship created: {graph_name}/{edge_collection}/"
                    f"{from_node_id} -> {to_node_id}"
                )
                return True
            return False
        except Exception as e:
            self.logger.error(f"Failed to create relationship: {e}")
            return False
    
    # ============================================================================
    # RAW QUERY OPERATIONS
    # ============================================================================
    
    async def execute_query(
        self,
        graph_name: str,
        query: str,
        bind_vars: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute AQL graph query.
        
        Args:
            graph_name: Graph name
            query: AQL query string
            bind_vars: Optional bind variables
        
        Returns:
            List of result documents
        """
        return await self.arango_adapter.execute_aql(query, bind_vars=bind_vars)
    
    async def find_path(
        self,
        graph_name: str,
        start_node_id: str,
        start_collection: str,
        end_node_id: str,
        end_collection: str,
        max_paths: int = 5,
        max_depth: int = 10
    ) -> List[List[str]]:
        """
        Find path between nodes in graph.
        
        Args:
            graph_name: Graph name
            start_node_id: Start node ID
            start_collection: Start node collection
            end_node_id: End node ID
            end_collection: End node collection
            max_paths: Maximum number of paths to return
            max_depth: Maximum path depth
        
        Returns:
            List of paths (each path is a list of node IDs)
        """
        # Use ArangoDB graph API directly for path finding (more reliable than AQL)
        db = self._get_db()
        if not db:
            return []
        
        try:
            graph = db.graph(graph_name)
            start_vertex_id = f"{start_collection}/{start_node_id}"
            end_vertex_id = f"{end_collection}/{end_node_id}"
            
            # Use graph's shortest_path method
            paths = []
            try:
                # Get shortest path
                path_result = graph.shortest_path(
                    start_vertex_id,
                    end_vertex_id,
                    direction="any",
                    weight=None,
                    default_weight=1
                )
                if path_result and "vertices" in path_result:
                    path_vertices = [v.get("_key") for v in path_result["vertices"]]
                    if path_vertices:
                        paths.append(path_vertices)
            except Exception as e:
                self.logger.debug(f"Shortest path not found: {e}")
            
            # If no path found, try traversal query as fallback
            if not paths:
                # Use AQL with proper syntax - graph name must be quoted string literal
                graph_name_escaped = graph_name.replace("'", "\\'")
                start_vertex_escaped = start_vertex_id.replace("'", "\\'")
                end_vertex_escaped = end_vertex_id.replace("'", "\\'")
                
                query = f"FOR v, e, p IN 1..{max_depth} ANY '{start_vertex_escaped}' TO '{end_vertex_escaped}' GRAPH '{graph_name_escaped}' LIMIT {max_paths} RETURN p.vertices[*]._key"
                results = await self.arango_adapter.execute_aql(query, bind_vars={})
                paths = [path for path in results if path]
            
            return paths[:max_paths]
        except Exception as e:
            self.logger.error(f"Failed to find path: {e}")
            return []
    
    async def get_neighbors(
        self,
        graph_name: str,
        node_id: str,
        collection_name: str,
        max_depth: int = 2
    ) -> List[Dict[str, Any]]:
        """
        Get neighbors of a node in graph.
        
        Args:
            graph_name: Graph name
            node_id: Node ID
            collection_name: Node collection
            max_depth: Maximum traversal depth
        
        Returns:
            List of neighbor nodes
        """
        # AQL graph traversal - ArangoDB requires vertex IDs and graph name to be string literals
        start_vertex_id = f"{collection_name}/{node_id}"
        
        # Escape single quotes if needed
        start_vertex_id_escaped = start_vertex_id.replace("'", "\\'")
        graph_name_escaped = graph_name.replace("'", "\\'")
        
        # Use single line query to avoid formatting issues
        query = f"FOR v, e, p IN 1..@max_depth ANY '{start_vertex_id_escaped}' GRAPH '{graph_name_escaped}' RETURN DISTINCT v"
        
        bind_vars = {
            "max_depth": max_depth
        }
        
        return await self.execute_query(graph_name, query, bind_vars)
    
    async def find_semantic_similarity(
        self,
        graph_name: str,
        query: str,
        similarity_threshold: float = 0.7,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Find semantically similar nodes (using embeddings stored in nodes).
        
        This is a placeholder for semantic similarity search.
        In production, this would use ArangoDB's vector search capabilities
        or integrate with an embedding service.
        
        Args:
            graph_name: Graph name
            query: Search query
            similarity_threshold: Minimum similarity score
            limit: Maximum results
        
        Returns:
            List of similar nodes
        """
        # Note: This is a basic implementation
        # For production, integrate with embedding service or use ArangoDB vector search
        self.logger.warning(
            "Semantic similarity search is basic - consider integrating "
            "embedding service or ArangoDB vector search"
        )
        
        # Basic text search in node properties
        aql_query = """
        FOR node IN GRAPH @graph_name
            FILTER node.text != null
            FILTER CONTAINS(LOWER(node.text), LOWER(@query))
            LIMIT @limit
            RETURN node
        """
        
        bind_vars = {
            "graph_name": graph_name,
            "query": query,
            "limit": limit
        }
        
        return await self.execute_query(graph_name, aql_query, bind_vars)
    
    async def get_graph_stats(self, graph_name: str) -> Dict[str, Any]:
        """
        Get graph statistics.
        
        Args:
            graph_name: Graph name
        
        Returns:
            Graph statistics
        """
        db = self._get_db()
        if not db:
            return {}
        
        try:
            graph = db.graph(graph_name)
            return {
                "name": graph_name,
                "vertex_collections": graph.vertex_collections(),
                "edge_definitions": graph.edge_definitions()
            }
        except Exception as e:
            self.logger.error(f"Failed to get graph stats: {e}")
            return {}
