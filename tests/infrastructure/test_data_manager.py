"""
Test Data Management Utilities

Manages test data isolation and cleanup.

WHAT (Test Infrastructure Role): I manage test data isolation and cleanup
HOW (Test Infrastructure Implementation): I track test data and clean it up after tests
"""

from typing import Dict, Any, List, Optional
from symphainy_platform.foundations.public_works.adapters.arango_adapter import ArangoAdapter
from symphainy_platform.foundations.public_works.adapters.redis_adapter import RedisAdapter
from utilities import get_logger

logger = get_logger("TestDataManager")


class TestDataManager:
    """Manages test data isolation and cleanup."""
    
    def __init__(
        self,
        arango_adapter: Optional[ArangoAdapter] = None,
        redis_adapter: Optional[RedisAdapter] = None
    ):
        """
        Initialize test data manager.
        
        Args:
            arango_adapter: ArangoDB adapter for managing test collections
            redis_adapter: Redis adapter for managing test keys
        """
        self.arango_adapter = arango_adapter
        self.redis_adapter = redis_adapter
        self.test_collections: List[str] = []
        self.test_keys: List[str] = []
        self.test_documents: List[Dict[str, str]] = []  # List of (collection, key) tuples
    
    async def create_test_collection(self, collection_name: str) -> bool:
        """
        Create a test collection and track it for cleanup.
        
        Args:
            collection_name: Name of the collection to create
        
        Returns:
            True if collection created successfully
        """
        if not self.arango_adapter:
            logger.warning("ArangoDB adapter not available")
            return False
        
        success = await self.arango_adapter.create_collection(collection_name)
        if success:
            self.test_collections.append(collection_name)
            logger.debug(f"Created test collection: {collection_name}")
        return success
    
    def track_redis_key(self, key: str):
        """
        Track a Redis key for cleanup.
        
        Args:
            key: Redis key to track
        """
        if key not in self.test_keys:
            self.test_keys.append(key)
            logger.debug(f"Tracking Redis key: {key}")
    
    def track_document(self, collection_name: str, document_key: str):
        """
        Track a document for cleanup.
        
        Args:
            collection_name: Collection name
            document_key: Document key
        """
        doc_ref = {"collection": collection_name, "key": document_key}
        if doc_ref not in self.test_documents:
            self.test_documents.append(doc_ref)
            logger.debug(f"Tracking document: {collection_name}/{document_key}")
    
    async def cleanup(self):
        """
        Clean up all test data.
        
        This method deletes all tracked collections, documents, and Redis keys.
        """
        # Clean ArangoDB documents
        if self.arango_adapter:
            for doc_ref in self.test_documents:
                try:
                    await self.arango_adapter.delete_document(
                        doc_ref["collection"],
                        doc_ref["key"]
                    )
                    logger.debug(f"Deleted document: {doc_ref['collection']}/{doc_ref['key']}")
                except Exception as e:
                    logger.debug(f"Failed to delete document {doc_ref}: {e}")
            
            # Clean ArangoDB collections
            for collection in self.test_collections:
                try:
                    await self.arango_adapter.delete_collection(collection)
                    logger.debug(f"Deleted collection: {collection}")
                except Exception as e:
                    logger.debug(f"Failed to delete collection {collection}: {e}")
        
        # Clean Redis keys
        if self.redis_adapter:
            for key in self.test_keys:
                try:
                    await self.redis_adapter.delete(key)
                    logger.debug(f"Deleted Redis key: {key}")
                except Exception as e:
                    logger.debug(f"Failed to delete Redis key {key}: {e}")
        
        # Clear tracking lists
        self.test_collections.clear()
        self.test_keys.clear()
        self.test_documents.clear()
        logger.info("✅ Test data cleaned up")
    
    async def cleanup_collections(self, collection_names: Optional[List[str]] = None):
        """
        Clean up specific collections.
        
        Args:
            collection_names: List of collection names to clean. If None, cleans all tracked collections.
        """
        if not self.arango_adapter:
            return
        
        collections_to_clean = collection_names or self.test_collections
        
        for collection in collections_to_clean:
            try:
                await self.arango_adapter.delete_collection(collection)
                logger.debug(f"Deleted collection: {collection}")
                if collection in self.test_collections:
                    self.test_collections.remove(collection)
            except Exception as e:
                logger.debug(f"Failed to delete collection {collection}: {e}")
    
    async def cleanup_redis_keys(self, keys: Optional[List[str]] = None):
        """
        Clean up specific Redis keys.
        
        Args:
            keys: List of keys to clean. If None, cleans all tracked keys.
        """
        if not self.redis_adapter:
            return
        
        keys_to_clean = keys or self.test_keys
        
        for key in keys_to_clean:
            try:
                await self.redis_adapter.delete(key)
                logger.debug(f"Deleted Redis key: {key}")
                if key in self.test_keys:
                    self.test_keys.remove(key)
            except Exception as e:
                logger.debug(f"Failed to delete Redis key {key}: {e}")
