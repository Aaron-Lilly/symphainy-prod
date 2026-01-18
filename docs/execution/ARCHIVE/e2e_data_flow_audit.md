# E2E Data Flow Audit - Complete Gap Analysis

**Status:** Comprehensive Audit  
**Date:** January 2026  
**Context:** Preparing for EDI/API clients processing 350k+ policies  
**Goal:** Identify all gaps in upload→parse→embed→interpret flow

---

## Executive Summary

**Critical Finding:** We have significant gaps in the File Management System (FMS) that will cause failures at scale. Many capabilities exist "under the covers" but are not exposed as intents, creating architectural violations and making the system fragile.

**Key Issues:**
1. **Missing Intent Layer** - Many operations exist in services/abstractions but aren't exposed as intents
2. **Inconsistent Access Patterns** - Some operations go through State Surface, others directly to Supabase/GCS
3. **No Bulk Operations** - Critical for 350k policy processing
4. **Incomplete Error Handling** - Missing retry, idempotency, and failure recovery
5. **No File Lifecycle Management** - Missing archive, purge, versioning

---

## Complete E2E Flow Analysis

### Flow: Upload → Parse → Embed → Interpret → Analyze

```
1. UPLOAD
   User/EDI/API → ingest_file → FileStorageAbstraction → GCS + Supabase → State Surface
   
2. RETRIEVE (for parsing)
   parse_content → needs file_id → How do we get file?
   
3. PARSE
   parse_content → FileParserService → ParsingAbstraction → GCS (parsed results) → Supabase (lineage)
   
4. EMBED
   extract_embeddings → EmbeddingService → ArangoDB → Supabase (lineage)
   
5. INTERPRET
   interpret_data_* → Insights Services → GCS (results) → Supabase (lineage)
   
6. ANALYZE
   analyze_* → Insights Services → GCS (results) → Supabase (lineage)
```

---

## What EXISTS vs What's MISSING

### ✅ What EXISTS (Under the Covers)

#### File Storage Abstraction
- ✅ `upload_file()` - Uploads to GCS + creates Supabase metadata
- ✅ `download_file()` - Downloads from GCS
- ✅ `delete_file()` - Deletes from GCS + soft delete in Supabase
- ✅ `list_files()` - Lists files from GCS (by prefix)
- ✅ `get_file_metadata()` - Gets metadata from GCS
- ✅ `get_file_by_uuid()` - Gets file metadata from Supabase by UUID

#### State Surface
- ✅ `store_file_reference()` - Registers file in State Surface
- ✅ `get_file()` - Gets file data via State Surface reference
- ✅ `get_file_metadata()` - Gets file metadata from State Surface

#### Content Orchestrator
- ✅ `_handle_ingest_file()` - Uploads new file
- ✅ `_handle_parse_content()` - Parses file
- ✅ `_handle_extract_embeddings()` - Creates embeddings (placeholder)
- ✅ `_handle_get_parsed_file()` - Gets parsed results
- ✅ `_handle_get_semantic_interpretation()` - Gets semantic interpretation

#### File Parser Service
- ✅ `parse_file()` - Parses file using parsing abstractions
- ✅ Stores parsed results in GCS
- ✅ Registers parsed file reference in State Surface

---

### ❌ What's MISSING (Critical Gaps)

#### 1. File Management Intents (CRITICAL)

**Missing Intents:**
- ❌ `register_file` - Register existing file in State Surface
- ❌ `retrieve_file_metadata` - Get Supabase record (metadata only)
- ❌ `retrieve_file` - Get file contents from GCS
- ❌ `list_files` - List files for tenant/session (with filters)
- ❌ `get_file_by_id` - Get file by file_id (Supabase lookup)
- ❌ `search_files` - Search files by metadata (name, type, date, etc.)
- ❌ `update_file_metadata` - Update file metadata in Supabase
- ❌ `delete_file` - Delete file (intent-level, not just abstraction)

**Why Critical:**
- EDI/API clients need to query files before processing
- Need to verify file exists before parsing
- Need to list files for UI display
- Need to update metadata (status, tags, etc.)

#### 2. Bulk Operations (CRITICAL for 350k Policies)

**Missing:**
- ❌ `bulk_ingest_files` - Upload multiple files in batch
- ❌ `bulk_parse_files` - Parse multiple files in parallel
- ❌ `bulk_extract_embeddings` - Create embeddings for multiple parsed results
- ❌ `bulk_register_files` - Register multiple existing files

**Why Critical:**
- 350k policies = 350k file operations
- Sequential processing would take days/weeks
- Need parallel processing with batching
- Need progress tracking and failure recovery

#### 3. File Lifecycle Management

**Missing:**
- ❌ `archive_file` - Move file to archive storage
- ❌ `purge_file` - Permanently delete file (GDPR compliance)
- ❌ `restore_file` - Restore from archive
- ❌ `version_file` - Create file version
- ❌ `get_file_versions` - List file versions

**Why Critical:**
- Long-term storage management
- Compliance requirements
- File versioning for audit trails

#### 4. Error Handling & Resilience

**Missing:**
- ❌ Idempotency keys - Prevent duplicate processing
- ❌ Retry logic - Automatic retry on transient failures
- ❌ Failure recovery - Resume from last successful step
- ❌ Dead letter queue - Handle permanently failed files
- ❌ Progress tracking - Track processing status for long-running operations

**Why Critical:**
- 350k files = high probability of failures
- Need to recover from partial failures
- Need to avoid duplicate processing
- Need visibility into processing status

#### 5. File Validation & Preprocessing

**Missing:**
- ❌ `validate_file` - Validate file before processing (size, type, format)
- ❌ `preprocess_file` - Clean/normalize file before parsing
- ❌ `detect_file_type` - Auto-detect file type from contents
- ❌ `extract_file_metadata` - Extract metadata from file (EXIF, etc.)

**Why Critical:**
- Prevent processing invalid files
- Auto-detect file types for better parsing
- Extract metadata for better organization

#### 6. Query & Search Capabilities

**Missing:**
- ❌ `query_files` - Query files by metadata (SQL-like)
- ❌ `search_files` - Full-text search on file names/metadata
- ❌ `filter_files` - Filter files by criteria (type, date, status)
- ❌ `get_file_lineage` - Get complete lineage for file

**Why Critical:**
- Need to find files quickly
- Need to query by business criteria
- Need to trace file lineage

---

## What's "BURIED" (Exists but Not Exposed)

### File Storage Abstraction Methods

**These exist but aren't exposed as intents:**
- ✅ `list_files(prefix)` - Lists files from GCS
- ✅ `get_file_metadata(file_path)` - Gets metadata from GCS
- ✅ `get_file_by_uuid(uuid)` - Gets file from Supabase

**Problem:** These are only accessible via direct abstraction calls, not through Runtime intents. This violates the architecture principle that all operations should go through Runtime.

### State Surface Methods

**These exist but aren't exposed as intents:**
- ✅ `get_file(file_reference)` - Gets file data
- ✅ `get_file_metadata(file_reference)` - Gets file metadata

**Problem:** These require a `file_reference` which must be created via `store_file_reference()`. But there's no intent to create file references for existing files.

### Supabase Direct Access

**Test Data Seeder directly accesses Supabase:**
- ✅ `seed_source_file()` - Directly inserts into `source_files` table
- ✅ `seed_parsed_result()` - Directly inserts into `parsed_results` table

**Problem:** This bypasses Runtime and State Surface, creating inconsistent access patterns.

---

## Architecture Violations

### Violation 1: Direct Supabase Access

**Location:** `tests/test_data/test_data_utils.py`

```python
# Direct Supabase insert - bypasses Runtime
response = client.table("source_files").insert({...}).execute()
```

**Problem:**
- Bypasses Runtime governance
- Not observable/replayable
- Creates inconsistent state

**Should be:**
- Use `ingest_file` intent (for new files)
- Use `register_file` intent (for existing files)
- All operations go through Runtime

### Violation 2: Missing Intent Layer

**Location:** File operations exist in abstractions but not as intents

**Problem:**
- Operations not governed by Runtime
- Not observable/replayable
- Can't be orchestrated in sagas

**Should be:**
- All file operations exposed as intents
- Runtime handles governance, observability, replayability

### Violation 3: Inconsistent File ID Resolution

**Location:** Multiple ways to get file metadata

**Current:**
- `ingest_file` → creates `file_id` → stores in Supabase
- `parse_content` → needs `file_id` → but how to get it?
- `seed_source_file` → creates `file_id` → stores in Supabase
- No intent to get `file_id` from Supabase

**Problem:**
- Tests create files via seeder, then need `file_id` for parsing
- No way to get `file_id` via intent
- Forces direct Supabase access

---

## Complete Intent Inventory

### Content Realm - Current Intents

```python
✅ ingest_file              # Upload NEW file
✅ parse_content            # Parse file
✅ extract_embeddings       # Create embeddings
✅ get_parsed_file          # Get parsed results
✅ get_semantic_interpretation  # Get semantic interpretation
```

### Content Realm - Missing Intents

```python
❌ register_file            # Register existing file in State Surface
❌ retrieve_file_metadata  # Get Supabase record (metadata)
❌ retrieve_file            # Get file contents from GCS
❌ list_files               # List files for tenant/session
❌ get_file_by_id           # Get file by file_id
❌ search_files             # Search files by metadata
❌ update_file_metadata     # Update file metadata
❌ delete_file              # Delete file (intent-level)
❌ validate_file            # Validate file before processing
❌ bulk_ingest_files        # Bulk upload
❌ bulk_parse_files         # Bulk parse
❌ archive_file             # Archive file
❌ purge_file               # Permanently delete
```

---

## E2E Flow with Gaps Highlighted

### Scenario: EDI Client Uploads 350k Policies

```
1. UPLOAD (350k files)
   ❌ No bulk_ingest_files intent
   ❌ No idempotency keys
   ❌ No progress tracking
   ❌ No failure recovery
   
   Current: Must call ingest_file 350k times sequentially
   Needed: Bulk operation with batching, parallel processing, progress tracking

2. VERIFY UPLOAD (check which files uploaded successfully)
   ❌ No list_files intent (to query uploaded files)
   ❌ No get_file_by_id intent (to verify specific file)
   ❌ No query_files intent (to filter by status/date)
   
   Current: Must query Supabase directly (violates architecture)
   Needed: Intent to query files with filters

3. PARSE (350k files)
   ❌ No bulk_parse_files intent
   ❌ No retry logic for failed parses
   ❌ No progress tracking
   ❌ No failure recovery
   
   Current: Must call parse_content 350k times sequentially
   Needed: Bulk operation with batching, parallel processing, retry logic

4. EMBED (350k parsed results)
   ❌ No bulk_extract_embeddings intent
   ❌ No progress tracking
   ❌ No failure recovery
   
   Current: Must call extract_embeddings 350k times sequentially
   Needed: Bulk operation with batching, parallel processing

5. INTERPRET (350k embeddings)
   ❌ No bulk_interpret_data intent
   ❌ No progress tracking
   ❌ No failure recovery
   
   Current: Must call interpret_data 350k times sequentially
   Needed: Bulk operation with batching, parallel processing

6. MONITOR & RECOVER
   ❌ No get_processing_status intent
   ❌ No resume_processing intent
   ❌ No retry_failed_operations intent
   ❌ No dead_letter_queue intent
   
   Current: No way to monitor or recover from failures
   Needed: Status tracking, resume capability, retry mechanism
```

---

## Critical Gaps for 350k Policy Processing

### 1. Bulk Operations (CRITICAL)

**Missing:**
- `bulk_ingest_files` - Accept list of files, process in batches
- `bulk_parse_files` - Accept list of file_ids, parse in parallel
- `bulk_extract_embeddings` - Accept list of parsed_result_ids, embed in parallel
- `bulk_interpret_data` - Accept list of embedding_ids, interpret in parallel

**Requirements:**
- Batch size configuration (e.g., 100 files per batch)
- Parallel processing (e.g., 10 batches in parallel)
- Progress tracking (e.g., "Processing batch 50/3500")
- Failure isolation (one file failure doesn't stop batch)
- Partial success handling (track which files succeeded/failed)

### 2. Idempotency (CRITICAL)

**Missing:**
- Idempotency keys for all operations
- Duplicate detection
- Skip already-processed files

**Requirements:**
- Each file operation has idempotency key
- Runtime checks if operation already completed
- Returns existing result if already processed
- Prevents duplicate processing

### 3. Progress Tracking (CRITICAL)

**Missing:**
- Status tracking for long-running operations
- Progress percentage
- ETA calculation
- Failure counts

**Requirements:**
- Store processing status in State Surface or Supabase
- Update status as batches complete
- Query status via intent
- Resume from last successful batch

### 4. Error Handling & Recovery (CRITICAL)

**Missing:**
- Retry logic with exponential backoff
- Failure categorization (transient vs permanent)
- Dead letter queue for permanent failures
- Resume capability

**Requirements:**
- Automatic retry for transient failures (network, timeout)
- Dead letter queue for permanent failures (invalid file format)
- Resume from last successful operation
- Failure notifications/alerts

### 5. File Query & Search (CRITICAL)

**Missing:**
- Query files by metadata
- Search files by name/type
- Filter files by status/date
- Get file lineage

**Requirements:**
- SQL-like query interface
- Full-text search
- Efficient indexing (for 350k+ files)
- Pagination support

---

## Recommended Implementation Plan

### Phase 1: Core File Management & Unified Ingestion (Week 1)

**Priority: CRITICAL**

**File Management Intents:**
1. `register_file` - Register existing file in State Surface
2. `retrieve_file_metadata` - Get Supabase record
3. `retrieve_file` - Get file contents
4. `list_files` - List files with filters
5. `get_file_by_id` - Get file by file_id

**Unified Ingestion (NEW - Extensibility Built In):**
6. **Refactor `ingest_file` to use `IngestionAbstraction`**
   - Support `ingestion_type` parameter (upload, edi, api)
   - Route to appropriate adapter via abstraction
   - Unified error handling and metadata tracking
7. **Wire up IngestionAbstraction in Public Works**
   - Ensure `get_ingestion_abstraction()` is available
   - Initialize adapters (Upload, EDI, API)
8. **Update tests to use unified ingestion**

**Why:** 
- File management intents are foundational
- **Unified ingestion enables extensibility from day 1**
- **EDI/API clients can use same intent as uploads**
- **Sets pattern for future ingestion types (webhook, scheduled, streaming)**

**See:** [Ingestion Extensibility Plan](./ingestion_extensibility_plan.md) for details

### Phase 2: Bulk Operations (Week 2)

**Priority: CRITICAL**

1. `bulk_ingest_files` - Bulk ingestion with batching
   - **Supports all ingestion types** (upload, EDI, API)
   - Batch size configuration
   - Parallel processing
   - Progress tracking
2. `bulk_parse_files` - Bulk parse with parallel processing
3. `bulk_extract_embeddings` - Bulk embedding creation
4. `bulk_interpret_data` - Bulk interpretation

**Why:** 
- Essential for 350k policy processing
- **Bulk operations work with all ingestion types**
- **Enables high-throughput processing from any source**

### Phase 3: Error Handling & Resilience (Week 3)

**Priority: HIGH**

1. Idempotency keys for all operations
   - **Include ingestion_type in idempotency key**
   - Prevents duplicate ingestion across types
2. Retry logic with exponential backoff
   - **Ingestion-specific retry strategies** (EDI may need different retry than API)
3. Progress tracking and status queries
4. Resume capability
   - **Resume bulk ingestion from last successful batch**

**Why:** 
- Critical for reliability at scale
- **Different ingestion types may need different retry strategies**
- **Need to track progress across all ingestion types**

### Phase 4: File Lifecycle & Advanced Features (Week 4)

**Priority: MEDIUM**

1. `archive_file`, `purge_file`, `restore_file`
2. `validate_file`, `preprocess_file`
3. `search_files`, `query_files`
4. `update_file_metadata`
5. **Future ingestion types** (webhook, scheduled, streaming) - if needed

**Why:** 
- Important for production operations
- **Advanced features can be added incrementally**
- **Future ingestion types can be added without changing core**

---

## Architecture Compliance Checklist

### ✅ What We're Doing Right

- ✅ Using Public Works abstractions (FileStorageAbstraction, etc.)
- ✅ State Surface for governed file access
- ✅ Runtime Participation Contract for realms
- ✅ Lineage tracking in Supabase

### ❌ What We're Violating

- ❌ Direct Supabase access in tests (bypasses Runtime)
- ❌ Operations exist in abstractions but not as intents
- ❌ Inconsistent file ID resolution
- ❌ No bulk operations (forces sequential processing)
- ❌ No idempotency (risk of duplicate processing)
- ❌ No progress tracking (no visibility into long-running operations)

---

## Success Criteria

### For 350k Policy Processing

✅ **Bulk Operations:**
- Can upload 350k files in < 1 hour (with batching)
- Can parse 350k files in < 2 hours (with parallel processing)
- Can embed 350k parsed results in < 3 hours
- Can interpret 350k embeddings in < 4 hours

✅ **Error Handling:**
- Automatic retry for transient failures
- Dead letter queue for permanent failures
- Resume from last successful operation
- < 0.1% failure rate

✅ **Visibility:**
- Real-time progress tracking
- Status queries for any file
- Failure notifications
- Complete audit trail

✅ **Architecture Compliance:**
- All operations via Runtime intents
- No direct Supabase/GCS access
- All operations observable/replayable
- Consistent access patterns

---

## Next Steps

1. **Immediate:** Implement core file management intents (Phase 1)
2. **Short-term:** Implement bulk operations (Phase 2)
3. **Medium-term:** Add error handling & resilience (Phase 3)
4. **Long-term:** Add lifecycle management & advanced features (Phase 4)

---

## References

- [Platform Rules](../PLATFORM_RULES.md)
- [Ingest File Analysis](./ingest_file_analysis.md)
- [Architectural Fixes Analysis](./architectural_fixes_analysis.md)
- [Lineage Tracking Architecture](../architecture/insights_lineage_tracking.md)
