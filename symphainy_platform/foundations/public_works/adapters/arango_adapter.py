"""
ArangoDB Adapter - Raw Technology Client (Layer 0)

Real ArangoDB client wrapper with no business logic.
This is the raw technology layer for ArangoDB operations.

WHAT (Infrastructure Role): I provide raw ArangoDB client operations
HOW (Infrastructure Implementation): I use real ArangoDB client with no business logic
"""

from typing import Dict, Any, Optional, List
from urllib.parse import urlparse

try:
    from arango import ArangoClient
    from arango.database import StandardDatabase
    from arango.exceptions import ArangoError
    ARANGO_AVAILABLE = True
except ImportError:
    ARANGO_AVAILABLE = False
    ArangoClient = None
    StandardDatabase = None
    ArangoError = Exception

from utilities import get_logger


class ArangoAdapter:
    """
    Raw ArangoDB client wrapper - no business logic.
    
    This adapter provides direct access to ArangoDB operations without
    any business logic or abstraction. It's the raw technology layer.
    """
    
    def __init__(
        self,
        url: str,
        username: str = "root",
        password: str = "",
        database: str = "symphainy_platform"
    ):
        """
        Initialize ArangoDB adapter with real connection.
        
        Args:
            url: ArangoDB connection URL (e.g., "http://localhost:8529")
            username: ArangoDB username
            password: ArangoDB password
            database: Database name
        """
        if not ARANGO_AVAILABLE:
            raise ImportError(
                "ArangoDB client not available. Install with: pip install python-arango"
            )
        
        self.url = url
        self.username = username
        self.password = password
        self.database = database
        self._client: Optional[ArangoClient] = None
        self._db: Optional[StandardDatabase] = None
        self.logger = get_logger(self.__class__.__name__)
    
    async def connect(self) -> bool:
        """Connect to ArangoDB."""
        try:
            # Parse URL
            parsed = urlparse(self.url)
            host = parsed.hostname or "localhost"
            port = parsed.port or 8529
            
            # Create ArangoDB client
            self._client = ArangoClient(hosts=f"http://{host}:{port}")
            
            # Connect to database
            self._db = self._client.db(
                name=self.database,
                username=self.username,
                password=self.password
            )
            
            # Test connection
            self._db.properties()
            
            self.logger.info(
                f"ArangoDB adapter connected: {host}:{port}/{self.database}"
            )
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to ArangoDB: {e}", exc_info=True)
            return False
    
    async def disconnect(self):
        """Disconnect from ArangoDB."""
        # ArangoDB client doesn't need explicit disconnect
        self._client = None
        self._db = None
    
    def is_connected(self) -> bool:
        """Check if connected to ArangoDB."""
        return self._db is not None
    
    # ============================================================================
    # RAW DATABASE OPERATIONS
    # ============================================================================
    
    async def create_database(self, database_name: str) -> bool:
        """Create database in ArangoDB."""
        if not self._client:
            return False
        try:
            sys_db = self._client.db("_system", username=self.username, password=self.password)
            sys_db.create_database(database_name)
            self.logger.info(f"Database created: {database_name}")
            return True
        except ArangoError as e:
            if "duplicate name" in str(e).lower():
                self.logger.debug(f"Database already exists: {database_name}")
                return True
            self.logger.error(f"Failed to create database {database_name}: {e}")
            return False
    
    async def database_exists(self, database_name: str) -> bool:
        """Check if database exists."""
        if not self._client:
            return False
        try:
            sys_db = self._client.db("_system", username=self.username, password=self.password)
            return sys_db.has_database(database_name)
        except Exception as e:
            self.logger.error(f"Failed to check database existence: {e}")
            return False
    
    # ============================================================================
    # RAW COLLECTION OPERATIONS
    # ============================================================================
    
    async def create_collection(
        self,
        collection_name: str,
        collection_type: str = "document"
    ) -> bool:
        """Create collection in ArangoDB."""
        if not self._db:
            return False
        try:
            if collection_type == "document":
                self._db.create_collection(collection_name)
            elif collection_type == "edge":
                self._db.create_collection(collection_name, edge=True)
            else:
                self.logger.error(f"Unknown collection type: {collection_type}")
                return False
            
            self.logger.debug(f"Collection created: {collection_name}")
            return True
        except ArangoError as e:
            if "duplicate name" in str(e).lower():
                self.logger.debug(f"Collection already exists: {collection_name}")
                return True
            self.logger.error(f"Failed to create collection {collection_name}: {e}")
            return False
    
    async def collection_exists(self, collection_name: str) -> bool:
        """Check if collection exists."""
        if not self._db:
            return False
        try:
            return self._db.has_collection(collection_name)
        except Exception as e:
            self.logger.error(f"Failed to check collection existence: {e}")
            return False
    
    async def delete_collection(self, collection_name: str) -> bool:
        """Delete collection from ArangoDB."""
        if not self._db:
            return False
        try:
            self._db.delete_collection(collection_name)
            self.logger.debug(f"Collection deleted: {collection_name}")
            return True
        except ArangoError as e:
            self.logger.error(f"Failed to delete collection {collection_name}: {e}")
            return False
    
    # ============================================================================
    # RAW DOCUMENT OPERATIONS
    # ============================================================================
    
    async def insert_document(
        self,
        collection_name: str,
        document: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Insert document into collection."""
        if not self._db:
            return None
        try:
            collection = self._db.collection(collection_name)
            result = collection.insert(document)
            return result
        except ArangoError as e:
            self.logger.error(f"Failed to insert document: {e}")
            return None
    
    async def get_document(
        self,
        collection_name: str,
        document_key: str
    ) -> Optional[Dict[str, Any]]:
        """Get document from collection."""
        if not self._db:
            return None
        try:
            collection = self._db.collection(collection_name)
            return collection.get(document_key)
        except ArangoError as e:
            self.logger.error(f"Failed to get document {document_key}: {e}")
            return None
    
    async def update_document(
        self,
        collection_name: str,
        document_key: str,
        updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update document in collection."""
        if not self._db:
            return None
        try:
            collection = self._db.collection(collection_name)
            return collection.update({"_key": document_key, **updates})
        except ArangoError as e:
            self.logger.error(f"Failed to update document {document_key}: {e}")
            return None
    
    async def delete_document(
        self,
        collection_name: str,
        document_key: str
    ) -> bool:
        """Delete document from collection."""
        if not self._db:
            return False
        try:
            collection = self._db.collection(collection_name)
            collection.delete(document_key)
            return True
        except ArangoError as e:
            self.logger.error(f"Failed to delete document {document_key}: {e}")
            return False
    
    # ============================================================================
    # RAW AQL OPERATIONS
    # ============================================================================
    
    async def execute_aql(
        self,
        query: str,
        bind_vars: Optional[Dict[str, Any]] = None,
        count: bool = False,
        batch_size: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Execute AQL query.
        
        Args:
            query: AQL query string
            bind_vars: Optional bind variables
            count: Return count instead of results
            batch_size: Batch size for cursor
            
        Returns:
            List of result documents
        """
        if not self._db:
            return []
        try:
            cursor = self._db.aql.execute(
                query,
                bind_vars=bind_vars or {},
                count=count,
                batch_size=batch_size
            )
            return list(cursor)
        except ArangoError as e:
            self.logger.error(f"Failed to execute AQL query: {e}")
            return []
    
    def get_database(self) -> Optional[StandardDatabase]:
        """Get ArangoDB database instance (for advanced operations)."""
        return self._db
