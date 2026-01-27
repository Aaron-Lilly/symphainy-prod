"""
Semantic Search Abstraction - Business Logic Implementation (Layer 1)

Implements semantic search operations using Meilisearch.
Coordinates search, indexing, and faceting operations.

WHAT (Infrastructure Role): I provide semantic search services
HOW (Infrastructure Implementation): I use Meilisearch adapter with business logic
"""

from typing import Dict, Any, List, Optional

from utilities import get_logger, get_clock
from ..protocols.semantic_search_protocol import SemanticSearchProtocol
from ..adapters.meilisearch_adapter import MeilisearchAdapter


class SemanticSearchAbstraction(SemanticSearchProtocol):
    """
    Semantic search abstraction with business logic.
    
    Implements semantic search operations using Meilisearch adapter.
    Provides search, indexing, and faceting capabilities.
    """
    
    def __init__(self, meilisearch_adapter: MeilisearchAdapter):
        """
        Initialize semantic search abstraction.
        
        Args:
            meilisearch_adapter: Meilisearch adapter (Layer 0)
        """
        self.meilisearch_adapter = meilisearch_adapter
        self.logger = get_logger(self.__class__.__name__)
        self.clock = get_clock()
        
        # Ensure adapter is connected
        if not meilisearch_adapter._client:
            meilisearch_adapter.connect()
        
        self.logger.info("Semantic Search Abstraction initialized")
    
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
        try:
            self.logger.info(f"Searching: {query} in index {index}")
            
            # Use Meilisearch adapter (synchronous, but we're in async context)
            # Meilisearch client is sync, so we run it in a thread pool
            import asyncio
            results = await asyncio.to_thread(
                self.meilisearch_adapter.search,
                index_name=index,
                query=query,
                filters=filters,
                limit=limit,
                offset=offset
            )
            
            self.logger.info(f"Search completed: {len(results.get('hits', []))} results")
            return results
        except Exception as e:
            self.logger.error(f"Search failed: {e}", exc_info=True)
            return {"hits": [], "estimatedTotalHits": 0}
    
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
        try:
            import asyncio
            
            # Ensure document has an ID
            if "id" not in document:
                self.logger.warning(f"Document missing 'id' field, generating one")
                from utilities import generate_session_id
                document["id"] = generate_session_id()
            
            success = await asyncio.to_thread(
                self.meilisearch_adapter.add_documents,
                index_name=index,
                documents=[document]
            )
            
            if success:
                self.logger.info(f"Document indexed: {document.get('id')} in {index}")
            
            return success
        except Exception as e:
            self.logger.error(f"Failed to index document: {e}", exc_info=True)
            return False
    
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
        try:
            import asyncio
            
            # Ensure all documents have IDs
            for doc in documents:
                if "id" not in doc:
                    from utilities import generate_session_id
                    doc["id"] = generate_session_id()
            
            success = await asyncio.to_thread(
                self.meilisearch_adapter.add_documents,
                index_name=index,
                documents=documents
            )
            
            if success:
                self.logger.info(f"Indexed {len(documents)} documents in {index}")
            
            return success
        except Exception as e:
            self.logger.error(f"Failed to index documents: {e}", exc_info=True)
            return False
    
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
        try:
            import asyncio
            
            success = await asyncio.to_thread(
                self.meilisearch_adapter.delete_documents,
                index_name=index,
                document_ids=[document_id]
            )
            
            if success:
                self.logger.info(f"Document deleted: {document_id} from {index}")
            
            return success
        except Exception as e:
            self.logger.error(f"Failed to delete document: {e}", exc_info=True)
            return False
    
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
        try:
            import asyncio
            
            self.logger.info(f"Faceted search: {query} in {index} with facets {facets}")
            
            results = await asyncio.to_thread(
                self.meilisearch_adapter.search_with_facets,
                index_name=index,
                query=query,
                facets=facets,
                limit=limit
            )
            
            self.logger.info(f"Faceted search completed: {len(results.get('hits', []))} results")
            return results
        except Exception as e:
            self.logger.error(f"Faceted search failed: {e}", exc_info=True)
            return {"hits": [], "estimatedTotalHits": 0, "facetDistribution": {}}
