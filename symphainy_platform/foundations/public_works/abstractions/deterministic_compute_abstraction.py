"""
Deterministic Compute Abstraction - Pure Infrastructure (Layer 1)

Implements deterministic compute operations using DuckDB adapter.
Returns raw data only - no business logic.

WHAT (Infrastructure Role): I provide deterministic compute storage services
HOW (Infrastructure Implementation): I use DuckDB adapter for deterministic embeddings and computations

NOTE: This is PURE INFRASTRUCTURE - no business logic.
Business logic (UUID generation, validation, metadata enhancement) belongs in Realm services.
Domain logic (schema fingerprinting, pattern signature generation) belongs in Realm services.
"""

from typing import Dict, Any, Optional, List
import json
from utilities import get_logger
from ..adapters.duckdb_adapter import DuckDBAdapter
from ..protocols.file_storage_protocol import FileStorageProtocol


class DeterministicComputeAbstraction:
    """
    Deterministic Compute Abstraction - Pure infrastructure.
    
    Provides governed access to DuckDB for deterministic embeddings and computations.
    
    ARCHITECTURAL PRINCIPLE: This is the correct way to store deterministic embeddings.
    - Goes through governance (context)
    - Stored in DuckDB (deterministic compute)
    - Lineage tracked in ArangoDB (via metadata, not content)
    """
    
    def __init__(
        self,
        duckdb_adapter: DuckDBAdapter,
        file_storage_abstraction: Optional[FileStorageProtocol] = None
    ):
        """
        Initialize Deterministic Compute abstraction.
        
        Args:
            duckdb_adapter: DuckDB adapter (Layer 0)
            file_storage_abstraction: Optional file storage for backups
        """
        self.duckdb = duckdb_adapter
        self.file_storage = file_storage_abstraction
        self.logger = get_logger(self.__class__.__name__)
        
        # Table names (infrastructure concern)
        self.deterministic_embeddings_table = "deterministic_embeddings"
        self.computation_results_table = "computation_results"
        
        self.logger.info("Deterministic Compute Abstraction initialized (pure infrastructure)")
    
    async def initialize_schema(self) -> bool:
        """
        Initialize DuckDB database schema (create tables if needed).
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create deterministic_embeddings table
            await self.duckdb.create_table(
                self.deterministic_embeddings_table,
                {
                    "embedding_id": "VARCHAR",
                    "parsed_file_id": "VARCHAR",
                    "tenant_id": "VARCHAR",
                    "session_id": "VARCHAR",
                    "schema_fingerprint": "JSON",
                    "pattern_signature": "JSON",
                    "created_at": "TIMESTAMP",
                    "updated_at": "TIMESTAMP"
                }
            )
            
            # Create computation_results table
            await self.duckdb.create_table(
                self.computation_results_table,
                {
                    "computation_id": "VARCHAR",
                    "computation_type": "VARCHAR",
                    "input_data": "JSON",
                    "result_data": "JSON",
                    "tenant_id": "VARCHAR",
                    "created_at": "TIMESTAMP"
                }
            )
            
            # Create indexes
            await self.duckdb.execute_command(
                f"CREATE INDEX IF NOT EXISTS idx_parsed_file_id ON {self.deterministic_embeddings_table}(parsed_file_id)"
            )
            await self.duckdb.execute_command(
                f"CREATE INDEX IF NOT EXISTS idx_tenant_id ON {self.deterministic_embeddings_table}(tenant_id)"
            )
            await self.duckdb.execute_command(
                f"CREATE INDEX IF NOT EXISTS idx_computation_type ON {self.computation_results_table}(computation_type)"
            )
            
            self.logger.info("DuckDB schema initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Schema initialization failed: {e}", exc_info=True)
            return False
    
    async def store_deterministic_embedding(
        self,
        embedding_id: str,
        parsed_file_id: str,
        schema_fingerprint: Dict[str, Any],
        pattern_signature: Dict[str, Any],
        tenant_id: str,
        session_id: Optional[str] = None
    ) -> bool:
        """
        Store deterministic embedding (schema fingerprint + pattern signature).
        
        ARCHITECTURAL PRINCIPLE: This is the correct way to store deterministic embeddings.
        - Goes through governance (context)
        - Stored in DuckDB (deterministic compute)
        - Lineage tracked in ArangoDB (via metadata, not content)
        
        Args:
            embedding_id: Embedding identifier
            parsed_file_id: Parsed file identifier
            schema_fingerprint: Schema fingerprint dictionary
            pattern_signature: Pattern signature dictionary
            tenant_id: Tenant identifier
            session_id: Optional session identifier
        
        Returns:
            True if successful, False otherwise
        """
        try:
            from datetime import datetime
            
            # Prepare data for insertion
            embedding_data = {
                "embedding_id": embedding_id,
                "parsed_file_id": parsed_file_id,
                "tenant_id": tenant_id,
                "session_id": session_id or "",
                "schema_fingerprint": json.dumps(schema_fingerprint),
                "pattern_signature": json.dumps(pattern_signature),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Insert into DuckDB
            rows_inserted = await self.duckdb.insert_data(
                self.deterministic_embeddings_table,
                [embedding_data]
            )
            
            if rows_inserted > 0:
                self.logger.info(f"Stored deterministic embedding: {embedding_id}")
                return True
            else:
                self.logger.warning(f"Failed to store deterministic embedding: {embedding_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to store deterministic embedding: {e}", exc_info=True)
            return False
    
    async def get_deterministic_embedding(
        self,
        embedding_id: str,
        tenant_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get deterministic embedding by ID.
        
        Args:
            embedding_id: Embedding identifier
            tenant_id: Optional tenant identifier (for filtering)
        
        Returns:
            Embedding document or None
        """
        try:
            filter_conditions = {"embedding_id": embedding_id}
            if tenant_id:
                filter_conditions["tenant_id"] = tenant_id
            
            results = await self.duckdb.query_table(
                self.deterministic_embeddings_table,
                filter_conditions=filter_conditions,
                limit=1
            )
            
            if results:
                embedding = results[0]
                # Parse JSON fields
                if isinstance(embedding.get("schema_fingerprint"), str):
                    embedding["schema_fingerprint"] = json.loads(embedding["schema_fingerprint"])
                if isinstance(embedding.get("pattern_signature"), str):
                    embedding["pattern_signature"] = json.loads(embedding["pattern_signature"])
                return embedding
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to get deterministic embedding: {e}", exc_info=True)
            return None
    
    async def query_deterministic_embeddings(
        self,
        filter_conditions: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Query deterministic embeddings with optional filters.
        
        Args:
            filter_conditions: Optional dictionary of filter conditions
            limit: Optional limit on number of results
        
        Returns:
            List of embedding documents
        """
        try:
            results = await self.duckdb.query_table(
                self.deterministic_embeddings_table,
                filter_conditions=filter_conditions,
                limit=limit
            )
            
            # Parse JSON fields
            for embedding in results:
                if isinstance(embedding.get("schema_fingerprint"), str):
                    embedding["schema_fingerprint"] = json.loads(embedding["schema_fingerprint"])
                if isinstance(embedding.get("pattern_signature"), str):
                    embedding["pattern_signature"] = json.loads(embedding["pattern_signature"])
            
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to query deterministic embeddings: {e}", exc_info=True)
            return []
    
    async def find_matching_schema(
        self,
        schema_fingerprint: Dict[str, Any],
        tenant_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find schemas matching fingerprint (exact match).
        
        Args:
            schema_fingerprint: Schema fingerprint to match
            tenant_id: Optional tenant identifier (for filtering)
        
        Returns:
            List of matching embedding documents
        """
        try:
            # Convert fingerprint to JSON string for comparison
            fingerprint_json = json.dumps(schema_fingerprint, sort_keys=True)
            
            # Query for matching fingerprints
            query = f"""
                SELECT * FROM {self.deterministic_embeddings_table}
                WHERE schema_fingerprint = ?
            """
            
            if tenant_id:
                query += " AND tenant_id = ?"
            
            # Query for matching fingerprints
            # Use JSON string comparison (DuckDB stores JSON as VARCHAR/JSON type)
            # Escape single quotes in JSON string for SQL safety
            escaped_fingerprint = fingerprint_json.replace("'", "''")
            
            if tenant_id:
                # Query with tenant filter - use parameterized query
                query = f"""
                    SELECT * FROM {self.deterministic_embeddings_table}
                    WHERE schema_fingerprint = ?
                    AND tenant_id = ?
                """
                # DuckDBAdapter.execute_query expects parameters as dict with values
                results = await self.duckdb.execute_query(query, {"schema_fingerprint": fingerprint_json, "tenant_id": tenant_id})
            else:
                # Query without tenant filter
                query = f"""
                    SELECT * FROM {self.deterministic_embeddings_table}
                    WHERE schema_fingerprint = ?
                """
                results = await self.duckdb.execute_query(query, {"schema_fingerprint": fingerprint_json})
            
            # Parse JSON fields
            for embedding in results:
                if isinstance(embedding.get("schema_fingerprint"), str):
                    embedding["schema_fingerprint"] = json.loads(embedding["schema_fingerprint"])
                if isinstance(embedding.get("pattern_signature"), str):
                    embedding["pattern_signature"] = json.loads(embedding["pattern_signature"])
            
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to find matching schema: {e}", exc_info=True)
            return []
    
    async def store_computation_result(
        self,
        computation_id: str,
        computation_type: str,
        input_data: Dict[str, Any],
        result_data: Dict[str, Any],
        tenant_id: str
    ) -> bool:
        """
        Store replayable computation result.
        
        Args:
            computation_id: Computation identifier
            computation_type: Type of computation
            input_data: Input data dictionary
            result_data: Result data dictionary
            tenant_id: Tenant identifier
        
        Returns:
            True if successful, False otherwise
        """
        try:
            from datetime import datetime
            
            computation_data = {
                "computation_id": computation_id,
                "computation_type": computation_type,
                "input_data": json.dumps(input_data),
                "result_data": json.dumps(result_data),
                "tenant_id": tenant_id,
                "created_at": datetime.utcnow().isoformat()
            }
            
            rows_inserted = await self.duckdb.insert_data(
                self.computation_results_table,
                [computation_data]
            )
            
            if rows_inserted > 0:
                self.logger.info(f"Stored computation result: {computation_id}")
                return True
            else:
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to store computation result: {e}", exc_info=True)
            return False
    
    async def replay_computation(
        self,
        computation_id: str,
        tenant_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Replay stored computation.
        
        Args:
            computation_id: Computation identifier
            tenant_id: Optional tenant identifier (for filtering)
        
        Returns:
            Computation result or None
        """
        try:
            filter_conditions = {"computation_id": computation_id}
            if tenant_id:
                filter_conditions["tenant_id"] = tenant_id
            
            results = await self.duckdb.query_table(
                self.computation_results_table,
                filter_conditions=filter_conditions,
                limit=1
            )
            
            if results:
                computation = results[0]
                # Parse JSON fields
                if isinstance(computation.get("input_data"), str):
                    computation["input_data"] = json.loads(computation["input_data"])
                if isinstance(computation.get("result_data"), str):
                    computation["result_data"] = json.loads(computation["result_data"])
                return computation
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to replay computation: {e}", exc_info=True)
            return None
