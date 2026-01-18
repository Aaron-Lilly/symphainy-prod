# Supabase File Schema - Final Recommendations Summary

**Date:** January 2026  
**Status:** ✅ **FINAL RECOMMENDATIONS**  
**Purpose:** Summary of final schema decisions based on codebase analysis

---

## 🎯 Final Schema Decisions

### 1. mime_type vs content_type ✅ **USE `mime_type`**

**Decision:** Use `mime_type` for MIME type (industry standard)

**Rationale:**
- ✅ Industry standard name (`mime_type` is what the world expects)
- ✅ Clear separation: `file_type` for parsing pathway, `mime_type` for file format
- ✅ Code already accepts `mime_type` parameter, just needs to store it correctly
- ✅ Your intended purpose: Different purposes (parsing pathway vs file format)

**Schema:**
```sql
file_type TEXT NOT NULL DEFAULT 'unstructured',  -- structured/unstructured/hybrid (parsing pathway)
mime_type TEXT,  -- MIME type (e.g., application/pdf, text/csv) - for rendering, storage
```

**Code Analysis:**
- `file_type` is correctly used for parsing pathway (structured/unstructured/hybrid) ✅
- `FileParserService` uses `file_type` to determine parsing pathway ✅
- `mime_type` parameter is accepted but stored as `content_type` (needs fix)
- `content_type` in storage stores MIME type (should be `mime_type`)

---

### 2. ingestion_type ✅ **DEFAULT `upload`**

**Decision:** Default to `upload` (standard MVP pathway)

**Rationale:**
- ✅ `web_interface` doesn't exist in current code
- ✅ Valid values: `upload`, `edi`, `api` (matching `IngestionType` enum)
- ✅ `upload` is the standard MVP pathway

**Schema:**
```sql
ingestion_type TEXT DEFAULT 'upload',  -- upload, edi, api (standard MVP pathway)
```

---

### 3. root_file_uuid vs parent_file_uuid ✅ **KEEP BOTH**

**Decision:** Keep both (separate concepts in lineage tracking)

**Rationale:**
- ✅ `parent_file_uuid` = Immediate predecessor (direct parent)
- ✅ `root_file_uuid` = Original file (root of lineage tree)
- ✅ Standard lineage pattern - both needed for different navigation use cases

**Schema:**
```sql
root_file_uuid UUID,  -- Original file in lineage tree (root of lineage chain)
parent_file_uuid UUID,  -- Immediate parent file in lineage (direct predecessor)
```

---

### 4. session_id ✅ **REMOVED**

**Decision:** Remove from Supabase schema (runtime concept, not persistent metadata)

**Rationale:**
- ✅ Session is a runtime/execution concept
- ✅ Files persist beyond sessions
- ✅ State Surface already tracks session context for file references
- ✅ Supabase should track persistent file metadata, not runtime context

**Schema:**
```sql
-- session_id REMOVED - Runtime concept, tracked in State Surface, not persistent metadata
```

---

## 📋 Final Schema Fields

### Core Fields
- ✅ `uuid` - Primary key
- ✅ `user_id` (UUID) - User identifier
- ✅ `tenant_id` (UUID) - Tenant identifier
- ✅ `ui_name` - User-friendly filename
- ✅ `file_path` - GCS storage path

### File Metadata
- ✅ `file_type` - Parsing pathway (structured/unstructured/hybrid)
- ✅ `mime_type` - MIME type (application/pdf, text/csv, etc.)
- ✅ `file_size` - Size in bytes
- ✅ `file_hash` - SHA256 hash
- ✅ `file_checksum` - Additional checksum
- ✅ `parsed_path` - Path to parsed results

### Status & Processing
- ✅ `status` - File status (uploaded, active, archived, purged)
- ✅ `processing_status` - Processing state (pending, processing, completed, failed)
- ✅ `processing_errors` - JSONB for error tracking
- ✅ `ingestion_type` - How file was ingested (upload, edi, api) - **DEFAULT: upload**

### Lifecycle
- ✅ `archived_at` - When archived
- ✅ `archive_reason` - Reason for archiving
- ✅ `purged_at` - When purged

### Audit Trail
- ✅ `created_by` - Who created
- ✅ `updated_by` - Who updated
- ✅ `client_ip` - IP address
- ✅ `user_agent` - User agent

### Security & Compliance
- ✅ `access_level` - Access control
- ✅ `permissions` - JSONB permissions
- ✅ `data_classification` - Security classification
- ✅ `retention_policy` - Retention policy
- ✅ `compliance_flags` - JSONB compliance tracking

### Platform Context
- ✅ `pillar_origin` - Which realm/pillar
- ✅ `service_context` - JSONB service context
- ✅ `processing_pipeline` - JSONB processing steps

### Data Lineage
- ✅ `arango_content_id` - Link to ArangoDB
- ✅ `lineage_depth` - Depth in lineage
- ✅ `root_file_uuid` - Original file (root)
- ✅ `parent_file_uuid` - Immediate parent
- ✅ `generation` - Generation number
- ✅ `lineage_path` - Lineage path

### Versioning & Insights
- ✅ `version` - File version
- ✅ `insights` - JSONB insights/metadata

### Timestamps
- ✅ `created_at` - Creation timestamp
- ✅ `updated_at` - Update timestamp (auto-updated)
- ✅ `deleted` - Soft delete flag

---

## 🔧 Code Updates Needed

### 1. File Storage Abstraction

**Current (line 116):**
```python
"content_type": content_type,  # MIME type
```

**Should be:**
```python
"mime_type": mime_type,  # MIME type
```

### 2. Content Orchestrator

**Current (line 185):**
```python
"content_type": mime_type,  # Maps mime_type param to content_type field
```

**Should be:**
```python
"mime_type": mime_type,  # Store mime_type directly
```

### 3. Register File (line 1117)

**Current:**
```python
"content_type": mime_type or (file_metadata.get("file_type") if file_metadata else None),
```

**Should be:**
```python
"mime_type": mime_type or (file_metadata.get("mime_type") if file_metadata else None),
```

---

## ✅ Validation Checklist

- [ ] **Schema Created** - All fields from current + new fields
- [ ] **Types Fixed** - user_id and tenant_id are UUID
- [ ] **mime_type Added** - MIME type field in schema
- [ ] **content_type Removed** - Or kept as alias for backward compatibility
- [ ] **Constraint Fixed** - Constraint on `file_type`, not `mime_type`
- [ ] **ingestion_type Default** - Changed to `upload`
- [ ] **session_id Removed** - Not in schema
- [ ] **Code Updated** - FileStorageAbstraction uses `mime_type`
- [ ] **Code Updated** - ContentOrchestrator uses `mime_type`
- [ ] **Tests Updated** - All tests work with new schema

---

**Status:** ✅ **FINAL RECOMMENDATIONS COMPLETE**
