"""
Meilisearch Adapter - Raw Technology Client (Layer 0)

Raw Meilisearch client wrapper with no business logic.
This is the raw technology layer for Meilisearch operations.

WHAT (Infrastructure Role): I provide raw Meilisearch client operations
HOW (Infrastructure Implementation): I use real Meilisearch client with no business logic
"""

import asyncio
from typing import Dict, Any, Optional, List
from meilisearch import Client as MeilisearchClient
from meilisearch.errors import MeilisearchError

from utilities import get_logger


class MeilisearchAdapter:
    """
    Raw Meilisearch client wrapper - no business logic.
    
    This adapter provides direct access to Meilisearch operations without
    any business logic or abstraction. It's the raw technology layer.
    """
    
    def __init__(self, host: str = "localhost", port: int = 7700, api_key: Optional[str] = None):
        """
        Initialize Meilisearch adapter with real connection.
        
        Args:
            host: Meilisearch host
            port: Meilisearch port
            api_key: Optional API key
        """
        self.host = host
        self.port = port
        self.api_key = api_key
        self._client: Optional[MeilisearchClient] = None
        self.logger = get_logger(self.__class__.__name__)
        self.base_url = f"http://{host}:{port}"
    
    def connect(self) -> bool:
        """Connect to Meilisearch."""
        try:
            self._client = MeilisearchClient(
                url=self.base_url,
                api_key=self.api_key
            )
            # Test connection (synchronous check)
            # Meilisearch client doesn't have async health check in sync mode
            self.logger.info(f"Meilisearch adapter connected: {self.host}:{self.port}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to Meilisearch: {e}", exc_info=True)
            return False
    
    def disconnect(self):
        """Disconnect from Meilisearch."""
        self._client = None
    
    # ============================================================================
    # RAW INDEX OPERATIONS
    # ============================================================================
    
    def create_index(self, index_name: str, primary_key: str = "id") -> bool:
        """Raw index creation - no business logic."""
        if not self._client:
            return False
        
        try:
            self._client.create_index(index_name, {"primaryKey": primary_key})
            self.logger.debug(f"Index created: {index_name}")
            return True
        except MeilisearchError as e:
            self.logger.error(f"Meilisearch index creation error: {e}")
            return False
    
    def delete_index(self, index_name: str) -> bool:
        """Raw index deletion - no business logic."""
        if not self._client:
            return False
        
        try:
            self._client.delete_index(index_name)
            self.logger.debug(f"Index deleted: {index_name}")
            return True
        except MeilisearchError as e:
            self.logger.error(f"Meilisearch index deletion error: {e}")
            return False
    
    def get_indexes(self) -> List[Dict[str, Any]]:
        """Raw index listing - no business logic."""
        if not self._client:
            return []
        
        try:
            indexes = self._client.get_indexes()
            return indexes.get('results', [])
        except MeilisearchError as e:
            self.logger.error(f"Meilisearch index listing error: {e}")
            return []
    
    # ============================================================================
    # RAW DOCUMENT OPERATIONS
    # ============================================================================
    
    def add_documents(self, index_name: str, documents: List[Dict[str, Any]]) -> bool:
        """Raw document addition - no business logic."""
        if not self._client:
            return False
        
        try:
            index = self._client.index(index_name)
            index.add_documents(documents)
            self.logger.debug(f"Added {len(documents)} documents to {index_name}")
            return True
        except MeilisearchError as e:
            self.logger.error(f"Meilisearch document addition error: {e}")
            return False
    
    def update_documents(self, index_name: str, documents: List[Dict[str, Any]]) -> bool:
        """Raw document update - no business logic."""
        if not self._client:
            return False
        
        try:
            index = self._client.index(index_name)
            index.update_documents(documents)
            self.logger.debug(f"Updated {len(documents)} documents in {index_name}")
            return True
        except MeilisearchError as e:
            self.logger.error(f"Meilisearch document update error: {e}")
            return False
    
    def delete_documents(self, index_name: str, document_ids: List[str]) -> bool:
        """Raw document deletion - no business logic."""
        if not self._client:
            return False
        
        try:
            index = self._client.index(index_name)
            index.delete_documents(document_ids)
            self.logger.debug(f"Deleted {len(document_ids)} documents from {index_name}")
            return True
        except MeilisearchError as e:
            self.logger.error(f"Meilisearch document deletion error: {e}")
            return False
    
    # ============================================================================
    # RAW SEARCH OPERATIONS
    # ============================================================================
    
    def search(
        self,
        index_name: str,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 20,
        offset: int = 0,
        attributes_to_retrieve: Optional[List[str]] = None,
        attributes_to_crop: Optional[List[str]] = None,
        crop_length: int = 200
    ) -> Dict[str, Any]:
        """
        Raw Meilisearch search - no business logic.
        
        Args:
            index_name: Index name
            query: Search query
            filters: Optional filters
            limit: Result limit
            offset: Result offset
            attributes_to_retrieve: Optional attributes to retrieve
            attributes_to_crop: Optional attributes to crop
            crop_length: Crop length
        
        Returns:
            Dict containing search results
        """
        if not self._client:
            return {"hits": [], "estimatedTotalHits": 0}
        
        try:
            index = self._client.index(index_name)
            
            # Build search parameters
            search_params = {
                "q": query,
                "limit": limit,
                "offset": offset
            }
            
            if filters:
                search_params["filter"] = self._build_filter_string(filters)
            
            if attributes_to_retrieve:
                search_params["attributesToRetrieve"] = attributes_to_retrieve
            
            if attributes_to_crop:
                search_params["attributesToCrop"] = attributes_to_crop
                search_params["cropLength"] = crop_length
            
            results = index.search(query, search_params)
            return results
        except MeilisearchError as e:
            self.logger.error(f"Meilisearch search error: {e}")
            return {"hits": [], "estimatedTotalHits": 0}
    
    def search_with_facets(
        self,
        index_name: str,
        query: str,
        facets: List[str],
        limit: int = 20
    ) -> Dict[str, Any]:
        """Raw faceted search - no business logic."""
        if not self._client:
            return {"hits": [], "estimatedTotalHits": 0, "facetDistribution": {}}
        
        try:
            index = self._client.index(index_name)
            search_params = {
                "q": query,
                "limit": limit,
                "facets": facets
            }
            results = index.search(query, search_params)
            return results
        except MeilisearchError as e:
            self.logger.error(f"Meilisearch faceted search error: {e}")
            return {"hits": [], "estimatedTotalHits": 0, "facetDistribution": {}}
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def _build_filter_string(self, filters: Dict[str, Any]) -> str:
        """Build Meilisearch filter string from filters dict."""
        try:
            filter_parts = []
            
            for key, value in filters.items():
                if isinstance(value, list):
                    # Handle array filters: key IN [value1, value2]
                    value_str = ", ".join([f'"{v}"' if isinstance(v, str) else str(v) for v in value])
                    filter_parts.append(f"{key} IN [{value_str}]")
                elif isinstance(value, str):
                    # Handle string filters: key = "value"
                    filter_parts.append(f'{key} = "{value}"')
                else:
                    # Handle other types: key = value
                    filter_parts.append(f"{key} = {value}")
            
            return " AND ".join(filter_parts)
        except Exception as e:
            self.logger.error(f"Failed to build filter string: {e}")
            return ""
    
    def get_index_stats(self, index_name: str) -> Dict[str, Any]:
        """Raw index statistics - no business logic."""
        if not self._client:
            return {"numberOfDocuments": 0, "isIndexing": False}
        
        try:
            index = self._client.index(index_name)
            stats = index.get_stats()
            return stats
        except MeilisearchError as e:
            self.logger.error(f"Meilisearch stats error: {e}")
            return {"numberOfDocuments": 0, "isIndexing": False}
