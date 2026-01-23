"""
DuckDB Adapter - Raw Technology Client (Layer 0)

Real DuckDB client wrapper with no business logic.
This is the raw technology layer for DuckDB operations.

WHAT (Infrastructure Role): I provide raw DuckDB database operations
HOW (Infrastructure Implementation): I use real DuckDB client with no business logic
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
import json
import logging

try:
    import duckdb
    DUCKDB_AVAILABLE = True
except ImportError:
    DUCKDB_AVAILABLE = False
    duckdb = None

logger = logging.getLogger(__name__)


class DuckDBAdapter:
    """
    Raw DuckDB client wrapper - no business logic.
    
    This adapter provides direct access to DuckDB operations without
    any business logic or abstraction. It's the raw technology layer.
    
    DuckDB is an embedded, in-process OLAP database.
    - File-based (database is a file)
    - Columnar storage (perfect for analytical workloads)
    - SQL interface
    - No separate server process needed
    """
    
    def __init__(
        self,
        database_path: Optional[str] = None,
        read_only: bool = False
    ):
        """
        Initialize DuckDB adapter.
        
        Args:
            database_path: Path to DuckDB database file (None = in-memory database)
            read_only: If True, open database in read-only mode
        """
        if not DUCKDB_AVAILABLE:
            raise ImportError(
                "DuckDB not available. Install with: pip install duckdb"
            )
        
        self.database_path = database_path
        self.read_only = read_only
        self._connection = None
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Ensure database directory exists if path provided
        if database_path:
            db_dir = Path(database_path).parent
            if db_dir and not db_dir.exists():
                db_dir.mkdir(parents=True, exist_ok=True)
                self.logger.info(f"Created DuckDB directory: {db_dir}")
    
    async def connect(self) -> bool:
        """
        Connect to DuckDB database.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            if self.database_path:
                # File-based database
                self._connection = duckdb.connect(
                    self.database_path,
                    read_only=self.read_only
                )
                self.logger.info(f"DuckDB adapter connected: {self.database_path}")
            else:
                # In-memory database
                self._connection = duckdb.connect()
                self.logger.info("DuckDB adapter connected (in-memory)")
            
            # Test connection
            self._connection.execute("SELECT 1").fetchone()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to DuckDB: {e}", exc_info=True)
            return False
    
    async def disconnect(self):
        """Disconnect from DuckDB database."""
        if self._connection:
            self._connection.close()
            self._connection = None
            self.logger.info("DuckDB adapter disconnected")
    
    async def execute_query(
        self,
        query: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute SQL query and return results as list of dicts.
        
        Args:
            query: SQL query string
            parameters: Optional query parameters (for parameterized queries)
        
        Returns:
            List of dictionaries (one per row)
        """
        if not self._connection:
            raise RuntimeError("DuckDB connection not established. Call connect() first.")
        
        try:
            if parameters:
                # Parameterized query - DuckDB uses positional parameters
                # Convert dict to list of values in order they appear in query
                param_values = []
                # Simple approach: extract ? placeholders and use dict values in order
                # For now, assume parameters dict values are in correct order
                param_values = list(parameters.values())
                result = self._connection.execute(query, param_values).fetchall()
            else:
                # Direct query
                result = self._connection.execute(query).fetchall()
            
            # Get column names
            if result:
                columns = [desc[0] for desc in self._connection.description]
                # Convert to list of dicts
                return [dict(zip(columns, row)) for row in result]
            else:
                return []
                
        except Exception as e:
            self.logger.error(f"Query execution failed: {e}", exc_info=True)
            raise
    
    async def execute_command(self, command: str) -> bool:
        """
        Execute SQL command (CREATE TABLE, INSERT, etc.) - no results.
        
        Args:
            command: SQL command string
        
        Returns:
            True if successful, False otherwise
        """
        if not self._connection:
            raise RuntimeError("DuckDB connection not established. Call connect() first.")
        
        try:
            self._connection.execute(command)
            return True
        except Exception as e:
            self.logger.error(f"Command execution failed: {e}", exc_info=True)
            return False
    
    async def create_table(
        self,
        table_name: str,
        schema: Dict[str, str]  # {"column_name": "TYPE"}
    ) -> bool:
        """
        Create table with schema.
        
        Args:
            table_name: Table name
            schema: Dictionary mapping column names to types (e.g., {"id": "VARCHAR", "created_at": "TIMESTAMP"})
        
        Returns:
            True if successful, False otherwise
        """
        if not schema:
            raise ValueError("Schema cannot be empty")
        
        # Build CREATE TABLE statement
        columns = [f"{name} {type_}" for name, type_ in schema.items()]
        create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})"
        
        return await self.execute_command(create_sql)
    
    async def insert_data(
        self,
        table_name: str,
        data: List[Dict[str, Any]]
    ) -> int:
        """
        Insert data into table.
        
        Args:
            table_name: Table name
            data: List of dictionaries (one per row)
        
        Returns:
            Number of rows inserted
        """
        if not data:
            return 0
        
        if not self._connection:
            raise RuntimeError("DuckDB connection not established. Call connect() first.")
        
        try:
            # Get column names from first row
            columns = list(data[0].keys())
            
            # Build INSERT statement
            placeholders = ", ".join(["?" for _ in columns])
            insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
            
            # Insert rows
            rows_inserted = 0
            for row in data:
                values = [row.get(col) for col in columns]
                self._connection.execute(insert_sql, values)
                rows_inserted += 1
            
            return rows_inserted
            
        except Exception as e:
            self.logger.error(f"Insert failed: {e}", exc_info=True)
            raise
    
    async def query_table(
        self,
        table_name: str,
        filter_conditions: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Query table with optional filters.
        
        Args:
            table_name: Table name
            filter_conditions: Optional dictionary of filter conditions (e.g., {"tenant_id": "abc", "status": "active"})
            limit: Optional limit on number of results
        
        Returns:
            List of dictionaries (one per row)
        """
        query = f"SELECT * FROM {table_name}"
        
        # Add WHERE clause if filters provided
        if filter_conditions:
            conditions = [f"{k} = ?" for k in filter_conditions.keys()]
            query += f" WHERE {' AND '.join(conditions)}"
        
        # Add LIMIT if provided
        if limit:
            query += f" LIMIT {limit}"
        
        # Execute with parameters
        parameters = list(filter_conditions.values()) if filter_conditions else None
        
        return await self.execute_query(query, {k: v for k, v in (filter_conditions.items() if filter_conditions else [])})
    
    async def export_to_parquet(
        self,
        table_name: str,
        file_path: str
    ) -> bool:
        """
        Export table to Parquet file.
        
        Args:
            table_name: Table name
            file_path: Path to output Parquet file
        
        Returns:
            True if successful, False otherwise
        """
        if not self._connection:
            raise RuntimeError("DuckDB connection not established. Call connect() first.")
        
        try:
            export_sql = f"COPY (SELECT * FROM {table_name}) TO '{file_path}' (FORMAT PARQUET)"
            self._connection.execute(export_sql)
            return True
        except Exception as e:
            self.logger.error(f"Export to Parquet failed: {e}", exc_info=True)
            return False
    
    async def import_from_parquet(
        self,
        table_name: str,
        file_path: str
    ) -> bool:
        """
        Import table from Parquet file.
        
        Args:
            table_name: Table name
            file_path: Path to input Parquet file
        
        Returns:
            True if successful, False otherwise
        """
        if not self._connection:
            raise RuntimeError("DuckDB connection not established. Call connect() first.")
        
        try:
            import_sql = f"CREATE TABLE {table_name} AS SELECT * FROM read_parquet('{file_path}')"
            self._connection.execute(import_sql)
            return True
        except Exception as e:
            self.logger.error(f"Import from Parquet failed: {e}", exc_info=True)
            return False
    
    async def backup_database(self, backup_path: str) -> bool:
        """
        Backup database to file.
        
        Args:
            backup_path: Path to backup file
        
        Returns:
            True if successful, False otherwise
        """
        if not self._connection:
            raise RuntimeError("DuckDB connection not established. Call connect() first.")
        
        if not self.database_path:
            raise ValueError("Cannot backup in-memory database")
        
        try:
            # Copy database file
            import shutil
            shutil.copy2(self.database_path, backup_path)
            self.logger.info(f"Database backed up to: {backup_path}")
            return True
        except Exception as e:
            self.logger.error(f"Backup failed: {e}", exc_info=True)
            return False
    
    async def restore_database(self, backup_path: str) -> bool:
        """
        Restore database from backup.
        
        Args:
            backup_path: Path to backup file
        
        Returns:
            True if successful, False otherwise
        """
        if not self.database_path:
            raise ValueError("Cannot restore in-memory database")
        
        try:
            # Close current connection
            if self._connection:
                await self.disconnect()
            
            # Copy backup file to database path
            import shutil
            shutil.copy2(backup_path, self.database_path)
            
            # Reconnect
            await self.connect()
            
            self.logger.info(f"Database restored from: {backup_path}")
            return True
        except Exception as e:
            self.logger.error(f"Restore failed: {e}", exc_info=True)
            return False
    
    async def close(self):
        """Close database connection (alias for disconnect)."""
        await self.disconnect()
