"""
Semantic Data Abstraction - Pure Infrastructure (Layer 1)

Implements semantic data operations using ArangoDB adapter.
Returns raw data only - no business logic.

WHAT (Infrastructure Role): I provide semantic data storage services
HOW (Infrastructure Implementation): I use ArangoDB adapter

NOTE: This is PURE INFRASTRUCTURE - no business logic.
Business logic (UUID generation, validation, metadata enhancement, tenant filtering) belongs in Librarian Service.
Domain logic (embedding generation, semantic graph generation) belongs in Realm services.
"""

from typing import Dict, Any, Optional, List, Any as AdapterType
from utilities import get_logger
from ..protocols.semantic_data_protocol import SemanticDataProtocol


class SemanticDataAbstraction(SemanticDataProtocol):
    """
    Semantic data abstraction - pure infrastructure.
    
    Returns raw data only (Dict[str, Any] or List[Dict[str, Any]]), not business objects.
    Business logic (UUID generation, validation, metadata enhancement) belongs in Librarian Service.
    Domain logic (embedding generation, semantic graph generation) belongs in Realm services.
    """
    
    def __init__(self, arango_adapter: AdapterType):
        """
        Initialize Semantic Data abstraction.
        
        Args:
            arango_adapter: ArangoDB adapter for semantic data storage (Layer 0)
        """
        self.arango = arango_adapter
        self.logger = get_logger(self.__class__.__name__)
        
        # Collection names for ArangoDB (infrastructure concern)
        self.structured_embeddings_collection = "structured_embeddings"
        self.semantic_graph_nodes_collection = "semantic_graph_nodes"
        self.semantic_graph_edges_collection = "semantic_graph_edges"
        self.correlation_maps_collection = "correlation_maps"
        
        self.logger.info("Semantic Data Abstraction initialized (pure infrastructure)")
    
    # ============================================================================
    # EMBEDDING OPERATIONS (Pure Infrastructure)
    # ============================================================================
    
    async def store_semantic_embeddings(
        self,
        embedding_documents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Store semantic embedding documents - pure infrastructure.
        
        Expects pre-built embedding documents (with _key, content_id, file_id, etc.).
        No validation, no UUID generation, no metadata enhancement.
        
        PHASE 3 ANTI-CORRUPTION: Require chunk_id in embedding documents.
        Embeddings must reference deterministic chunks, not parsed_file_id directly.
        
        Args:
            embedding_documents: List of pre-built embedding documents
        
        Returns:
            Dict with storage result (stored_count, success status)
        """
        try:
            if not embedding_documents:
                raise ValueError("embedding_documents list cannot be empty")
            
            stored_count = 0
            for doc in embedding_documents:
                # Ensure _key exists (should be provided by Librarian Service)
                if "_key" not in doc:
                    raise ValueError("Embedding document must have '_key' field")
                
                # ANTI-CORRUPTION: Require chunk_id (Phase 2 pattern)
                if "chunk_id" not in doc:
                    raise ValueError(
                        "❌ ANTI-PATTERN: Embedding document must have 'chunk_id' field.\n"
                        "Embeddings must reference deterministic chunks, not parsed_file_id directly.\n"
                        "Use EmbeddingService.create_chunk_embeddings() to create chunk-based embeddings."
                    )
                
                # Store in ArangoDB (pure infrastructure)
                await self.arango.create_document(
                    self.structured_embeddings_collection,
                    doc
                )
                stored_count += 1
            
            self.logger.info(f"Stored {stored_count} semantic embeddings")
            
            return {
                "success": True,
                "stored_count": stored_count
            }
            
        except Exception as e:
            self.logger.error(f"Failed to store semantic embeddings: {e}", exc_info=True)
            raise
    
    async def get_semantic_embeddings(
        self,
        filter_conditions: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get semantic embeddings - pure infrastructure.
        
        PHASE 3 ANTI-CORRUPTION: Fail fast if parsed_file_id used directly.
        Use chunk-based pattern instead:
        1. Create chunks via deterministic_chunking_service.create_chunks()
        2. Query embeddings by chunk_id, not parsed_file_id
        """
        # ANTI-CORRUPTION: Fail fast if parsed_file_id used directly
        if filter_conditions and "parsed_file_id" in filter_conditions:
            raise ValueError(
                "❌ ANTI-PATTERN: Direct embedding query by parsed_file_id is not allowed.\n"
                "Use chunk-based pattern:\n"
                "  1. Create chunks via deterministic_chunking_service.create_chunks()\n"
                "  2. Query embeddings by chunk_id, not parsed_file_id\n"
                "  3. Example: filter_conditions={'chunk_id': {'$in': chunk_ids}}\n"
                "\n"
                "This ensures:\n"
                "  - Deterministic chunks are created first\n"
                "  - Embeddings reference stable chunk_ids\n"
                "  - Semantic signals can be extracted from chunks\n"
                "\n"
                "Migration: Update your service to use chunk-based pattern."
            )
        """
        Get semantic embeddings with filtering - pure infrastructure.
        
        Returns raw data from ArangoDB. No tenant filtering (that's Platform SDK's job).
        
        Args:
            filter_conditions: Optional filter conditions (content_id, file_id, column_name, etc.)
            limit: Optional limit on number of results
        
        Returns:
            List of raw embedding documents from ArangoDB
        """
        try:
            filter_conditions = filter_conditions or {}
            
            result = await self.arango.find_documents(
                self.structured_embeddings_collection,
                filter_conditions=filter_conditions,
                limit=limit
            )
            
            self.logger.debug(f"Retrieved {len(result)} semantic embeddings")
            
            # Return raw data
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to get semantic embeddings: {e}", exc_info=True)
            raise
    
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
        try:
            filter_conditions = filter_conditions or {}
            filter_conditions["semantic_id"] = semantic_id
            
            result = await self.arango.find_documents(
                self.structured_embeddings_collection,
                filter_conditions=filter_conditions
            )
            
            self.logger.debug(f"Retrieved {len(result)} embeddings for semantic_id {semantic_id}")
            
            # Return raw data
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to query embeddings by semantic_id {semantic_id}: {e}", exc_info=True)
            raise
    
    async def vector_search(
        self,
        query_embedding: List[float],
        filter_conditions: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        similarity_threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Vector similarity search - pure infrastructure.
        
        Uses pluggable vector backend (ArangoDB by default) for similarity calculation.
        This method delegates to the vector backend adapter for vector search.
        The adapter can be swapped with other backends (Pinecone, Weaviate) that implement
        the VectorBackendProtocol interface.
        
        Args:
            query_embedding: Query vector (embedding)
            filter_conditions: Optional filter conditions (e.g., {"file_id": "..."})
            limit: Maximum number of results
            similarity_threshold: Optional minimum similarity score (0.0 to 1.0)
        
        Returns:
            List of matching embedding documents with similarity scores, sorted by similarity (highest first)
        """
        try:
            if not query_embedding or len(query_embedding) == 0:
                raise ValueError("query_embedding cannot be empty")
            
            filter_conditions = filter_conditions or {}
            
            # Use ArangoDB vector search via adapter
            # The adapter handles vector similarity calculation using ArangoDB functions
            results = await self.arango.vector_search(
                collection_name=self.structured_embeddings_collection,
                query_vector=query_embedding,
                vector_field="embedding",  # Field name in embedding documents
                filter_conditions=filter_conditions,
                limit=limit,
                similarity_threshold=similarity_threshold
            )
            
            self.logger.debug(f"Vector search returned {len(results)} results")
            
            # Return raw data with similarity scores
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to perform vector search: {e}", exc_info=True)
            raise
    
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
        
        Expects pre-built node and edge documents (with _key, _from, _to, etc.).
        No validation, no UUID generation, no metadata enhancement.
        
        Args:
            node_documents: List of pre-built node documents
            edge_documents: List of pre-built edge documents
        
        Returns:
            Dict with storage result (stored_nodes, stored_edges, success status)
        """
        try:
            stored_nodes = 0
            for doc in node_documents:
                # Ensure _key exists (should be provided by Librarian Service)
                if "_key" not in doc:
                    raise ValueError("Node document must have '_key' field")
                
                # Store in ArangoDB (pure infrastructure)
                await self.arango.create_document(
                    self.semantic_graph_nodes_collection,
                    doc
                )
                stored_nodes += 1
            
            stored_edges = 0
            for doc in edge_documents:
                # Ensure _key, _from, _to exist (should be provided by Librarian Service)
                if "_key" not in doc:
                    raise ValueError("Edge document must have '_key' field")
                if "_from" not in doc or "_to" not in doc:
                    raise ValueError("Edge document must have '_from' and '_to' fields")
                
                # Store in ArangoDB (pure infrastructure)
                await self.arango.create_document(
                    self.semantic_graph_edges_collection,
                    doc
                )
                stored_edges += 1
            
            self.logger.info(f"Stored semantic graph: {stored_nodes} nodes, {stored_edges} edges")
            
            return {
                "success": True,
                "stored_nodes": stored_nodes,
                "stored_edges": stored_edges
            }
            
        except Exception as e:
            self.logger.error(f"Failed to store semantic graph: {e}", exc_info=True)
            raise
    
    async def get_semantic_graph(
        self,
        filter_conditions: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get semantic graph - pure infrastructure.
        
        Returns raw data from ArangoDB. No tenant filtering (that's Platform SDK's job).
        
        Args:
            filter_conditions: Optional filter conditions (content_id, file_id, etc.)
        
        Returns:
            Dict with 'nodes' and 'edges' lists (raw documents from ArangoDB)
        """
        try:
            filter_conditions = filter_conditions or {}
            
            # Get nodes
            nodes = await self.arango.find_documents(
                self.semantic_graph_nodes_collection,
                filter_conditions=filter_conditions
            )
            
            # Get edges
            edges = await self.arango.find_documents(
                self.semantic_graph_edges_collection,
                filter_conditions=filter_conditions
            )
            
            self.logger.debug(f"Retrieved semantic graph: {len(nodes)} nodes, {len(edges)} edges")
            
            # Return raw data
            return {
                "nodes": nodes,
                "edges": edges
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get semantic graph: {e}", exc_info=True)
            raise
    
    # ============================================================================
    # CORRELATION MAP OPERATIONS (Pure Infrastructure)
    # ============================================================================
    
    async def store_correlation_map(
        self,
        correlation_document: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Store correlation map document - pure infrastructure.
        
        Expects pre-built correlation document (with _key, content_id, etc.).
        No validation, no UUID generation, no metadata enhancement.
        
        Args:
            correlation_document: Pre-built correlation map document
        
        Returns:
            Dict with storage result
        """
        try:
            # Ensure _key exists (should be provided by Librarian Service)
            if "_key" not in correlation_document:
                raise ValueError("Correlation document must have '_key' field")
            
            # Store in ArangoDB (pure infrastructure)
            result = await self.arango.create_document(
                self.correlation_maps_collection,
                correlation_document
            )
            
            self.logger.info(f"Stored correlation map: {correlation_document.get('_key')}")
            
            return {
                "success": True,
                "correlation_map_id": result.get("_key") if result else correlation_document.get("_key")
            }
            
        except Exception as e:
            self.logger.error(f"Failed to store correlation map: {e}", exc_info=True)
            raise
    
    async def get_correlation_map(
        self,
        filter_conditions: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get correlation map - pure infrastructure.
        
        Returns raw data from ArangoDB. No tenant filtering (that's Platform SDK's job).
        
        Args:
            filter_conditions: Optional filter conditions (content_id, file_id, etc.)
        
        Returns:
            Correlation map document or None if not found
        """
        try:
            filter_conditions = filter_conditions or {}
            
            result = await self.arango.find_documents(
                self.correlation_maps_collection,
                filter_conditions=filter_conditions,
                limit=1
            )
            
            if result and len(result) > 0:
                correlation_map = result[0]
                self.logger.debug(f"Retrieved correlation map: {correlation_map.get('_key')}")
                return correlation_map
            else:
                self.logger.debug("No correlation map found")
                return None
            
        except Exception as e:
            self.logger.error(f"Failed to get correlation map: {e}", exc_info=True)
            raise
    
    # ============================================================================
    # HEALTH CHECK
    # ============================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check health of the semantic data system.
        
        Returns:
            Dict containing health status information
        """
        try:
            result = await self.arango.health_check()
            
            # Add collection information (infrastructure concern)
            result["collections"] = [
                self.structured_embeddings_collection,
                self.semantic_graph_nodes_collection,
                self.semantic_graph_edges_collection,
                self.correlation_maps_collection
            ]
            
            return result
            
        except Exception as e:
            self.logger.error(f"Health check failed: {e}", exc_info=True)
            raise
