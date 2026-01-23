# DuckDB Implementation Plan

**Date:** January 2026  
**Status:** 📋 **IMPLEMENTATION PLAN**  
**Purpose:** Add DuckDB to platform following 5-layer Public Works pattern

---

## Executive Summary

**Decision:** ✅ **YES - Implement DuckDB**

**Why:**
- Architecture Guide specifies it: "Deterministic compute: **DuckDB** - Embedded, replayable"
- Perfect fit for deterministic embeddings (schema fingerprints, pattern signatures)
- Embedded architecture (no separate service needed)
- Columnar storage (perfect for analytical workloads)

**Approach:** Follow 5-layer Public Works pattern exactly

---

## Architecture Alignment

### Current Architecture (From Guide):

| Abstraction                     | Technology (Adapter)       | Why                    |
| ------------------------------- | -------------------------- | ---------------------- |
| Lineage, meaning, relationships | **ArangoDB**               | Graph-native, semantic |
| Deterministic compute           | **DuckDB**                 | Embedded, replayable   |
| Vector semantics                | **ArangoDB (or external)** | Meaningful similarity  |

### Implementation Pattern:

```
Layer 0: DuckDBAdapter (raw technology)
    ↓
Layer 1: DeterministicComputeAbstraction (governed access)
    ↓
Layer 2: Public Works Foundation Service (registration)
    ↓
Layer 3: Content Realm Services (use abstraction)
    ↓
Layer 4: Agents/Orchestrators (use realm services)
```

---

## Implementation Phases

### Phase 1: DuckDB Adapter (Layer 0) - 4-6 hours

**File:** `symphainy_platform/foundations/public_works/adapters/duckdb_adapter.py`

**Responsibilities:**
- Raw DuckDB client wrapper
- Connection management
- SQL execution
- File-based database operations
- No business logic

**Key Methods:**
```python
class DuckDBAdapter:
    def __init__(self, database_path: str = None, read_only: bool = False):
        """
        Initialize DuckDB adapter.
        
        Args:
            database_path: Path to DuckDB database file (None = in-memory)
            read_only: If True, open database in read-only mode
        """
    
    async def connect(self) -> bool:
        """Connect to DuckDB database."""
    
    async def execute_query(
        self, 
        query: str, 
        parameters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Execute SQL query and return results as list of dicts."""
    
    async def execute_command(self, command: str) -> bool:
        """Execute SQL command (CREATE TABLE, INSERT, etc.) - no results."""
    
    async def create_table(
        self, 
        table_name: str, 
        schema: Dict[str, str]  # {"column_name": "TYPE"}
    ) -> bool:
        """Create table with schema."""
    
    async def insert_data(
        self, 
        table_name: str, 
        data: List[Dict[str, Any]]
    ) -> int:
        """Insert data into table. Returns number of rows inserted."""
    
    async def query_table(
        self,
        table_name: str,
        filter_conditions: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Query table with optional filters."""
    
    async def export_to_parquet(
        self, 
        table_name: str, 
        file_path: str
    ) -> bool:
        """Export table to Parquet file."""
    
    async def import_from_parquet(
        self, 
        table_name: str, 
        file_path: str
    ) -> bool:
        """Import table from Parquet file."""
    
    async def backup_database(self, backup_path: str) -> bool:
        """Backup database to file."""
    
    async def restore_database(self, backup_path: str) -> bool:
        """Restore database from backup."""
    
    async def close(self):
        """Close database connection."""
```

**Dependencies:**
- `duckdb` Python package
- File system access (or GCS/S3 for persistent storage)

---

### Phase 2: Deterministic Compute Abstraction (Layer 1) - 6-8 hours

**File:** `symphainy_platform/foundations/public_works/abstractions/deterministic_compute_abstraction.py`

**Responsibilities:**
- Governed access to DuckDB
- Policy enforcement (via context)
- Lifecycle management
- File storage coordination (GCS/S3 for backups)

**Key Methods:**
```python
class DeterministicComputeAbstraction:
    def __init__(
        self,
        duckdb_adapter: DuckDBAdapter,
        file_storage_abstraction: Optional[FileStorageAbstraction] = None
    ):
        """
        Initialize Deterministic Compute abstraction.
        
        Args:
            duckdb_adapter: DuckDB adapter (Layer 0)
            file_storage_abstraction: Optional file storage for backups
        """
    
    async def store_deterministic_embedding(
        self,
        embedding_id: str,
        parsed_file_id: str,
        schema_fingerprint: Dict[str, Any],
        pattern_signature: Dict[str, Any],
        context: ExecutionContext
    ) -> bool:
        """
        Store deterministic embedding (schema fingerprint + pattern signature).
        
        ARCHITECTURAL PRINCIPLE: This is the correct way to store deterministic embeddings.
        - Goes through governance (context)
        - Stored in DuckDB (deterministic compute)
        - Lineage tracked in ArangoDB (via metadata)
        """
    
    async def query_deterministic_embeddings(
        self,
        filter_conditions: Optional[Dict[str, Any]] = None,
        context: ExecutionContext
    ) -> List[Dict[str, Any]]:
        """Query deterministic embeddings with governance."""
    
    async def find_matching_schema(
        self,
        schema_fingerprint: Dict[str, Any],
        context: ExecutionContext
    ) -> List[Dict[str, Any]]:
        """Find schemas matching fingerprint (exact match)."""
    
    async def store_computation_result(
        self,
        computation_id: str,
        result: Dict[str, Any],
        context: ExecutionContext
    ) -> bool:
        """Store replayable computation result."""
    
    async def replay_computation(
        self,
        computation_id: str,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Replay stored computation."""
```

**Schema Design:**
```sql
-- Deterministic embeddings table
CREATE TABLE deterministic_embeddings (
    embedding_id VARCHAR PRIMARY KEY,
    parsed_file_id VARCHAR NOT NULL,
    tenant_id VARCHAR NOT NULL,
    session_id VARCHAR,
    schema_fingerprint JSON NOT NULL,
    pattern_signature JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Computation results table
CREATE TABLE computation_results (
    computation_id VARCHAR PRIMARY KEY,
    computation_type VARCHAR NOT NULL,
    input_data JSON,
    result_data JSON NOT NULL,
    tenant_id VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_parsed_file_id ON deterministic_embeddings(parsed_file_id);
CREATE INDEX idx_tenant_id ON deterministic_embeddings(tenant_id);
CREATE INDEX idx_computation_type ON computation_results(computation_type);
```

---

### Phase 3: Update DeterministicEmbeddingService - 4-6 hours

**File:** `symphainy_platform/realms/content/enabling_services/deterministic_embedding_service.py`

**Current Implementation:**
- Stores in ArangoDB directly (via `arango_adapter.create_document()`)
- Should use DuckDB via `DeterministicComputeAbstraction`

**Changes:**
```python
# BEFORE (Current - Direct ArangoDB)
embedding_doc = {
    "_key": generate_event_id(),
    "parsed_file_id": parsed_file_id,
    "schema_fingerprint": schema_fingerprint,
    "pattern_signature": pattern_signature,
    ...
}
await self.arango_adapter.create_document("deterministic_embeddings", embedding_doc)

# AFTER (Correct - Through Abstraction)
deterministic_compute = self.public_works.get_deterministic_compute_abstraction()
if not deterministic_compute:
    raise ValueError("DeterministicComputeAbstraction not available")

await deterministic_compute.store_deterministic_embedding(
    embedding_id=embedding_id,
    parsed_file_id=parsed_file_id,
    schema_fingerprint=schema_fingerprint,
    pattern_signature=pattern_signature,
    context=context
)
```

**Also Update:**
- `get_deterministic_embedding()` - Use abstraction
- `find_matching_schemas()` - Use abstraction

---

### Phase 4: Public Works Integration - 2-3 hours

**File:** `symphainy_platform/foundations/public_works/foundation_service.py`

**Changes:**
```python
# Add to __init__
self.duckdb_adapter: Optional[DuckDBAdapter] = None
self.deterministic_compute_abstraction: Optional[DeterministicComputeAbstraction] = None

# Add initialization method
def _initialize_duckdb(self):
    """Initialize DuckDB adapter and abstraction."""
    duckdb_config = self.config.get("duckdb", {})
    if duckdb_config:
        database_path = duckdb_config.get(
            "database_path", 
            "/data/duckdb/main.duckdb"  # Default path
        )
        
        self.duckdb_adapter = DuckDBAdapter(
            database_path=database_path,
            read_only=duckdb_config.get("read_only", False)
        )
        
        # Connect
        if self.duckdb_adapter.connect():
            self.logger.info(f"DuckDB adapter connected: {database_path}")
            
            # Create abstraction
            self.deterministic_compute_abstraction = DeterministicComputeAbstraction(
                duckdb_adapter=self.duckdb_adapter,
                file_storage_abstraction=self.file_storage_abstraction
            )
            
            # Initialize schema (create tables if needed)
            await self._initialize_duckdb_schema()
        else:
            self.logger.warning("DuckDB adapter connection failed")
    else:
        self.logger.info("DuckDB configuration not provided, DuckDB adapter not created")

async def _initialize_duckdb_schema(self):
    """Initialize DuckDB database schema."""
    if not self.duckdb_adapter:
        return
    
    # Create tables if they don't exist
    await self.duckdb_adapter.create_table(
        "deterministic_embeddings",
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
    
    await self.duckdb_adapter.create_table(
        "computation_results",
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
    await self.duckdb_adapter.execute_command(
        "CREATE INDEX IF NOT EXISTS idx_parsed_file_id ON deterministic_embeddings(parsed_file_id)"
    )
    # ... other indexes

# Add getter
def get_deterministic_compute_abstraction(self) -> Optional[DeterministicComputeAbstraction]:
    """Get deterministic compute abstraction."""
    return self.deterministic_compute_abstraction
```

---

### Phase 5: Containerization - 2-3 hours

**Dockerfile Updates:**
```dockerfile
FROM python:3.10-slim

# Install DuckDB
RUN pip install duckdb

# Create DuckDB data directory
RUN mkdir -p /app/data/duckdb

# Copy application
COPY . /app
WORKDIR /app

# DuckDB is embedded - no separate service needed
# Database files stored in mounted volume or GCS
```

**Docker Compose:**
```yaml
services:
  symphainy-platform:
    build: .
    volumes:
      - ./duckdb_data:/app/data/duckdb  # Local storage
      # OR use GCS/S3 for persistent storage
    environment:
      - DUCKDB_STORAGE_PATH=/app/data/duckdb
      - DUCKDB_BACKUP_TO_GCS=true  # Optional: backup to GCS
      - DUCKDB_BACKUP_INTERVAL=3600  # Backup every hour
```

**Kubernetes (if needed):**
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: duckdb-storage
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

---

### Phase 6: Migration & Testing - 4-6 hours

**Migration Strategy:**
1. **Dual Write Period:**
   - Write to both ArangoDB (existing) and DuckDB (new)
   - Read from DuckDB (new)
   - Fallback to ArangoDB if DuckDB fails

2. **Data Migration:**
   - Export existing deterministic embeddings from ArangoDB
   - Import into DuckDB
   - Verify data integrity

3. **Cutover:**
   - Switch reads to DuckDB only
   - Keep ArangoDB for lineage/metadata only
   - Remove dual write

**Testing:**
- Unit tests for DuckDBAdapter
- Integration tests for DeterministicComputeAbstraction
- E2E tests for DeterministicEmbeddingService
- Performance tests (DuckDB vs ArangoDB for deterministic queries)

---

## Implementation Details

### DuckDB Adapter Implementation

**Key Considerations:**
1. **Thread Safety:** DuckDB connections are not thread-safe. Use connection pooling or per-request connections.
2. **File Locking:** DuckDB uses file locking. Ensure only one process accesses database file.
3. **Backup Strategy:** Regular backups to GCS/S3 for durability.
4. **Schema Migration:** Version schema and support migrations.

**Connection Pattern:**
```python
# Option 1: Single connection (for single-threaded)
self.conn = duckdb.connect(database_path)

# Option 2: Connection per request (for async)
async def execute_query(self, query: str):
    conn = duckdb.connect(self.database_path)
    try:
        result = conn.execute(query).fetchall()
        return result
    finally:
        conn.close()
```

---

### Storage Strategy

**Option 1: Local File System (Development)**
- Database file in `/app/data/duckdb/main.duckdb`
- Mounted volume in Docker
- Simple, fast, but not durable across container restarts

**Option 2: GCS/S3 (Production)**
- Database file in GCS/S3 bucket
- Download on startup, upload on shutdown
- Or: Use DuckDB's S3 extension for direct S3 access
- More durable, but slower

**Option 3: Hybrid (Recommended)**
- Local file for active database
- Regular backups to GCS/S3
- Restore from backup on startup if local file missing

---

## Configuration

**Environment Variables:**
```bash
# DuckDB Configuration
DUCKDB_DATABASE_PATH=/app/data/duckdb/main.duckdb
DUCKDB_READ_ONLY=false
DUCKDB_BACKUP_ENABLED=true
DUCKDB_BACKUP_INTERVAL=3600  # seconds
DUCKDB_BACKUP_TO_GCS=true
DUCKDB_GCS_BUCKET=symphainy-duckdb-backups
```

**Config File:**
```python
{
    "duckdb": {
        "database_path": "/app/data/duckdb/main.duckdb",
        "read_only": false,
        "backup": {
            "enabled": true,
            "interval_seconds": 3600,
            "to_gcs": true,
            "gcs_bucket": "symphainy-duckdb-backups"
        }
    }
}
```

---

## Timeline Estimate

- **Phase 1:** DuckDB Adapter (4-6 hours)
- **Phase 2:** Deterministic Compute Abstraction (6-8 hours)
- **Phase 3:** Update DeterministicEmbeddingService (4-6 hours)
- **Phase 4:** Public Works Integration (2-3 hours)
- **Phase 5:** Containerization (2-3 hours)
- **Phase 6:** Migration & Testing (4-6 hours)

**Total:** 22-32 hours (2.75-4 days)

---

## Success Criteria

1. ✅ DuckDB adapter follows Layer 0 pattern (raw technology, no business logic)
2. ✅ DeterministicComputeAbstraction follows Layer 1 pattern (governed access)
3. ✅ DeterministicEmbeddingService uses abstraction (not direct adapter)
4. ✅ All deterministic embeddings stored in DuckDB
5. ✅ Schema fingerprints queryable via DuckDB
6. ✅ Pattern signatures queryable via DuckDB
7. ✅ Containerized and deployable
8. ✅ Backups to GCS/S3 working
9. ✅ Migration from ArangoDB complete
10. ✅ Tests passing

---

## Next Steps

1. **Implement Phase 1:** Create DuckDBAdapter
2. **Implement Phase 2:** Create DeterministicComputeAbstraction
3. **Update Phase 3:** Migrate DeterministicEmbeddingService
4. **Integrate Phase 4:** Add to Public Works
5. **Containerize Phase 5:** Docker setup
6. **Test Phase 6:** Migration and validation

---

## Notes

- **No Breaking Changes:** DuckDB addition is additive
- **Backward Compatible:** Can run alongside ArangoDB during migration
- **No External Dependencies:** DuckDB is embedded (no separate service)
- **File-Based:** Database is a file (can be backed up/restored easily)
