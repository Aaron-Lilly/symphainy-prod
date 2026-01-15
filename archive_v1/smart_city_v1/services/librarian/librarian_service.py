"""
Librarian Service - Refactored Implementation

WHAT: I govern knowledge and manage semantic search
HOW: I use pure infrastructure abstractions + Platform SDK + domain logic

Domain Logic (belongs here):
- Embedding storage/retrieval operations
- Semantic graph operations
- Search coordination (hybrid search, result merging)
- Content metadata storage

Governance Logic (via Platform SDK + Primitive):
- Tenant filtering
- Access control validation
- Search access policies
- Knowledge access policies
"""

import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
from utilities import get_logger, get_clock

from symphainy_platform.foundations.public_works.protocols.semantic_data_protocol import SemanticDataProtocol
from symphainy_platform.foundations.public_works.protocols.knowledge_discovery_protocol import KnowledgeDiscoveryProtocol
from symphainy_platform.foundations.public_works.protocols.content_metadata_protocol import ContentMetadataProtocol
from civic_systems.platform_sdk.platform_sdk import PlatformSDK
from civic_systems.smart_city.primitives.librarian.librarian_primitive import LibrarianPrimitive
from symphainy_platform.foundations.public_works.protocols.auth_protocol import SecurityContext


class LibrarianService:
    """
    Librarian Service - Knowledge governance and semantic search.
    
    Domain Logic:
    - Coordinates search across multiple backends
    - Stores embeddings with proper document structure
    - Manages semantic graphs
    - Merges search results
    
    Governance (via Platform SDK + Primitive):
    - Uses Platform SDK for tenant filtering and access control
    - Uses Librarian Primitive for policy decisions
    """
    
    def __init__(
        self,
        semantic_data_abstraction: SemanticDataProtocol,
        knowledge_discovery_abstraction: KnowledgeDiscoveryProtocol,
        content_metadata_abstraction: Optional[ContentMetadataProtocol] = None,
        platform_sdk: Optional[PlatformSDK] = None,
        librarian_primitive: Optional[LibrarianPrimitive] = None
    ):
        """
        Initialize Librarian Service.
        
        Args:
            semantic_data_abstraction: Pure infrastructure for semantic data
            knowledge_discovery_abstraction: Pure infrastructure for knowledge discovery
            content_metadata_abstraction: Optional pure infrastructure for content metadata
            platform_sdk: Platform SDK for governance operations
            librarian_primitive: Librarian Primitive for policy decisions
        """
        self.semantic_data = semantic_data_abstraction
        self.knowledge_discovery = knowledge_discovery_abstraction
        self.content_metadata = content_metadata_abstraction
        self.platform_sdk = platform_sdk
        self.librarian_primitive = librarian_primitive or LibrarianPrimitive()
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
        
        self.logger.info("Librarian Service initialized")
    
    # ============================================================================
    # EMBEDDING OPERATIONS (Domain Logic)
    # ============================================================================
    
    async def store_embeddings(
        self,
        content_id: str,
        file_id: str,
        embeddings: List[Dict[str, Any]],
        security_context: SecurityContext
    ) -> Dict[str, Any]:
        """
        Store semantic embeddings (domain logic).
        
        This method contains the domain logic that was previously in SemanticDataAbstraction:
        - UUID generation for embedding keys
        - Field validation
        - Document structure building
        - Metadata enhancement
        
        Args:
            content_id: Content metadata ID
            file_id: File UUID
            embeddings: List of embedding dictionaries
            security_context: Security context for access control
        
        Returns:
            Dict with storage result
        """
        try:
            # Governance: Check access via Platform SDK + Primitive
            if self.platform_sdk:
                access_check = await self.platform_sdk.ensure_knowledge_access(
                    action="write_embeddings",
                    user_id=security_context.user_id,
                    tenant_id=security_context.tenant_id,
                    resource=content_id,
                    security_context=security_context
                )
                
                if access_check.get("ready_for_runtime") and self.librarian_primitive:
                    policy_decision = await self.librarian_primitive.evaluate_knowledge_access(
                        security_context=security_context,
                        action="write_embeddings",
                        tenant_id=security_context.tenant_id,
                        resource=content_id,
                        policy_rules=access_check.get("policy_rules", {})
                    )
                    
                    if not policy_decision.get("allowed"):
                        raise PermissionError(f"Access denied: {policy_decision.get('reason')}")
            
            # Domain Logic: Validate embeddings
            if not embeddings or len(embeddings) == 0:
                raise ValueError("embeddings list cannot be empty")
            
            for emb in embeddings:
                if "column_name" not in emb and "chunk_index" is None:
                    raise ValueError("Each embedding must have a column_name or chunk_index")
                if "metadata_embedding" not in emb and "meaning_embedding" not in emb and "chunk_embedding" not in emb:
                    raise ValueError("Each embedding must have at least one embedding vector")
            
            # Domain Logic: Build embedding documents (with UUID generation, metadata enhancement)
            embedding_documents = []
            tenant_id = security_context.tenant_id
            
            for emb in embeddings:
                # Generate UUID for embedding key (domain logic)
                embedding_key = f"emb_{file_id}_{emb.get('column_name', emb.get('chunk_index', 'unknown'))}_{uuid.uuid4().hex[:8]}"
                
                # Build embedding document (domain logic)
                embedding_doc = {
                    "_key": embedding_key,
                    "content_id": content_id,
                    "file_id": file_id,
                    "parsed_file_id": emb.get("parsed_file_id"),
                    "embedding_file_id": emb.get("embedding_file_id"),
                    "column_name": emb.get("column_name"),
                    "metadata_embedding": emb.get("metadata_embedding"),
                    "meaning_embedding": emb.get("meaning_embedding"),
                    "samples_embedding": emb.get("samples_embedding"),
                    "chunk_embedding": emb.get("chunk_embedding"),
                    "semantic_id": emb.get("semantic_id"),
                    "data_type": emb.get("data_type"),
                    "semantic_meaning": emb.get("semantic_meaning"),
                    "sample_values": emb.get("sample_values"),
                    "row_count": emb.get("row_count"),
                    "column_position": emb.get("column_position"),
                    "semantic_model_recommendation": emb.get("semantic_model_recommendation"),
                    "chunk_index": emb.get("chunk_index"),
                    "chunk_text": emb.get("chunk_text"),
                    "chunk_metadata": emb.get("chunk_metadata"),
                    "total_chunks": emb.get("total_chunks"),
                    "content_type": emb.get("content_type"),
                    "format_type": emb.get("format_type"),
                    "embedding_type": emb.get("embedding_type"),
                    "tenant_id": tenant_id,  # Tenant ID from security context
                    "created_at": self.clock.now_iso()  # Metadata enhancement (domain logic)
                }
                embedding_documents.append(embedding_doc)
            
            # Infrastructure: Store via pure abstraction
            result = await self.semantic_data.store_semantic_embeddings(embedding_documents)
            
            # Domain Logic: Update content metadata flags
            if self.content_metadata:
                await self.content_metadata.update_content_metadata(
                    content_id,
                    {
                        "has_embeddings": True,
                        "embedding_count": len(embeddings),
                        "updated_at": self.clock.now_iso()
                    }
                )
            
            self.logger.info(f"Stored {len(embeddings)} embeddings for content {content_id}")
            
            return {
                "success": True,
                "content_id": content_id,
                "file_id": file_id,
                "stored_count": result.get("stored_count", len(embeddings))
            }
            
        except Exception as e:
            self.logger.error(f"Failed to store embeddings: {e}", exc_info=True)
            raise
    
    async def get_embeddings(
        self,
        security_context: SecurityContext,
        content_id: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get semantic embeddings (domain logic).
        
        Args:
            content_id: Optional content metadata ID
            filters: Optional filters
            security_context: Security context for access control
        
        Returns:
            List of embedding dictionaries
        """
        try:
            # Governance: Check access via Platform SDK + Primitive
            if self.platform_sdk:
                access_check = await self.platform_sdk.ensure_knowledge_access(
                    action="read_embeddings",
                    user_id=security_context.user_id,
                    tenant_id=security_context.tenant_id,
                    resource=content_id,
                    security_context=security_context
                )
                
                if access_check.get("ready_for_runtime") and self.librarian_primitive:
                    policy_decision = await self.librarian_primitive.evaluate_knowledge_access(
                        security_context=security_context,
                        action="read_embeddings",
                        tenant_id=security_context.tenant_id,
                        resource=content_id,
                        policy_rules=access_check.get("policy_rules", {})
                    )
                    
                    if not policy_decision.get("allowed"):
                        raise PermissionError(f"Access denied: {policy_decision.get('reason')}")
            
            # Domain Logic: Apply tenant filter (via Platform SDK)
            filter_conditions = filters or {}
            if content_id:
                filter_conditions["content_id"] = content_id
            
            if self.platform_sdk:
                filter_conditions = await self.platform_sdk.apply_tenant_filter(
                    filter_conditions,
                    security_context.tenant_id
                )
            else:
                # Fallback: Add tenant_id directly if Platform SDK not available
                filter_conditions["tenant_id"] = security_context.tenant_id
            
            # Infrastructure: Get via pure abstraction
            result = await self.semantic_data.get_semantic_embeddings(
                filter_conditions=filter_conditions
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to get embeddings: {e}", exc_info=True)
            raise
    
    # ============================================================================
    # SEARCH OPERATIONS (Domain Logic - Coordination)
    # ============================================================================
    
    async def search_knowledge(
        self,
        query: str,
        security_context: SecurityContext,
        filters: Optional[Dict[str, Any]] = None,
        search_mode: str = "hybrid",
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Search knowledge base (domain logic - coordination).
        
        This method contains the domain logic that was previously in KnowledgeDiscoveryAbstraction:
        - Hybrid search coordination
        - Result merging
        - Search mode routing
        
        Args:
            query: Search query
            filters: Optional filters
            security_context: Security context for access control
            search_mode: Search mode (exact, fuzzy, semantic, hybrid)
            limit: Maximum number of results
        
        Returns:
            Dict containing search results
        """
        try:
            # Governance: Check access via Platform SDK + Primitive
            if self.platform_sdk:
                access_check = await self.platform_sdk.ensure_search_access(
                    action="search_knowledge",
                    user_id=security_context.user_id,
                    tenant_id=security_context.tenant_id,
                    query=query,
                    security_context=security_context
                )
                
                if access_check.get("ready_for_runtime") and self.librarian_primitive:
                    policy_decision = await self.librarian_primitive.evaluate_search_access(
                        security_context=security_context,
                        action="search_knowledge",
                        tenant_id=security_context.tenant_id,
                        query=query,
                        policy_rules=access_check.get("policy_rules", {})
                    )
                    
                    if not policy_decision.get("allowed"):
                        raise PermissionError(f"Access denied: {policy_decision.get('reason')}")
            
            # Domain Logic: Apply tenant filter
            filter_conditions = filters or {}
            if self.platform_sdk:
                filter_conditions = await self.platform_sdk.apply_tenant_filter(
                    filter_conditions,
                    security_context.tenant_id
                )
            else:
                filter_conditions["tenant_id"] = security_context.tenant_id
            
            # Domain Logic: Coordinate search across backends (hybrid search)
            search_results = None
            
            if search_mode == "hybrid" or search_mode == "exact":
                # Primary search using Meilisearch
                search_results = await self.knowledge_discovery.search_meilisearch(
                    index="knowledge_assets",
                    query=query,
                    filters=filter_conditions,
                    limit=limit,
                    offset=0
                )
            
            if search_mode == "hybrid" or search_mode == "semantic":
                # Semantic search using Redis Graph and ArangoDB
                redis_results = []
                arango_results = []
                
                try:
                    redis_results = await self.knowledge_discovery.search_redis_graph(
                        graph="semantic_graph",
                        query=query,
                        similarity_threshold=0.7
                    )
                except Exception as e:
                    self.logger.warning(f"Redis Graph search failed: {e}")
                
                try:
                    arango_results = await self.knowledge_discovery.search_arango_semantic(
                        query=query,
                        similarity_threshold=0.7,
                        max_results=limit
                    )
                except Exception as e:
                    self.logger.warning(f"ArangoDB semantic search failed: {e}")
                
                # Domain Logic: Merge semantic results
                semantic_results = self._merge_semantic_results(redis_results, arango_results)
                
                # Domain Logic: Merge with Meilisearch results if available
                if search_results:
                    search_results = self._merge_search_results(search_results, semantic_results)
                else:
                    search_results = {
                        "hits": semantic_results,
                        "totalHits": len(semantic_results),
                        "estimatedTotalHits": len(semantic_results)
                    }
            
            if not search_results:
                search_results = {
                    "hits": [],
                    "totalHits": 0,
                    "estimatedTotalHits": 0
                }
            
            self.logger.info(f"Search completed: {len(search_results.get('hits', []))} results")
            
            return {
                "query": query,
                "filters": filters,
                "results": search_results.get("hits", []),
                "total_results": search_results.get("totalHits", 0),
                "status": "success"
            }
            
        except Exception as e:
            self.logger.error(f"Search failed: {e}", exc_info=True)
            raise
    
    # ============================================================================
    # DOMAIN LOGIC HELPERS (Result Merging)
    # ============================================================================
    
    def _merge_semantic_results(
        self,
        redis_results: List[Dict[str, Any]],
        arango_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Merge semantic search results from Redis Graph and ArangoDB (domain logic).
        
        This is the domain logic that was previously in KnowledgeDiscoveryAbstraction.
        """
        combined_results = []
        seen_ids = set()
        
        # Add Redis results
        for result in redis_results:
            result_id = result.get('id') or result.get('_key') or result.get('asset_id')
            if result_id and result_id not in seen_ids:
                combined_results.append(result)
                seen_ids.add(result_id)
        
        # Add ArangoDB results
        for result in arango_results:
            result_id = result.get('id') or result.get('_key') or result.get('asset_id')
            if result_id and result_id not in seen_ids:
                combined_results.append(result)
                seen_ids.add(result_id)
        
        # Sort by similarity score
        combined_results.sort(key=lambda x: x.get('similarity', 0), reverse=True)
        
        return combined_results
    
    def _merge_search_results(
        self,
        meilisearch_results: Dict[str, Any],
        semantic_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Merge Meilisearch and semantic results (domain logic).
        
        This is the domain logic that was previously in KnowledgeDiscoveryAbstraction.
        """
        meilisearch_hits = meilisearch_results.get("hits", [])
        combined_hits = []
        seen_ids = set()
        
        # Add Meilisearch results
        for hit in meilisearch_hits:
            hit_id = hit.get('id') or hit.get('_key')
            if hit_id and hit_id not in seen_ids:
                combined_hits.append(hit)
                seen_ids.add(hit_id)
        
        # Add semantic results (avoid duplicates)
        for result in semantic_results:
            result_id = result.get('id') or result.get('_key') or result.get('asset_id')
            if result_id and result_id not in seen_ids:
                combined_hits.append(result)
                seen_ids.add(result_id)
        
        return {
            **meilisearch_results,
            "hits": combined_hits,
            "totalHits": len(combined_hits),
            "estimatedTotalHits": len(combined_hits)
        }
