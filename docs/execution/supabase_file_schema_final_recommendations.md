# Supabase File Schema - Final Recommendations

**Date:** January 2026  
**Status:** 📋 **FINAL RECOMMENDATIONS**  
**Purpose:** Address schema questions and provide final recommendations

---

## 🎯 Questions & Answers

### 1. mime_type vs content_type - Do we need both?

**Answer: NO - We should standardize on `content_type`**

**Current Code Analysis:**
- `content_orchestrator.py` line 175: Gets `mime_type` from parameters
- `content_orchestrator.py` line 185: Sets `content_type: mime_type` in source_metadata
- `file_storage_abstraction.py` line 116: Stores `content_type` in Supabase metadata
- Code uses `content_type` consistently for storage

**Recommendation:**
- ✅ **Keep only `content_type`** (MIME type: `application/pdf`, `text/csv`, etc.)
- ❌ **Remove `mime_type`** from schema (it's redundant)
- ✅ **Update code** to use `content_type` consistently (already mostly done)

**Current Issue:**
- Code accepts `mime_type` as parameter but stores as `content_type`
- This is fine, but we should document that `mime_type` parameter maps to `content_type` field

**Action:**
- Remove `mime_type` column from schema
- Keep only `content_type` (which stores MIME type)

---

### 2. ingestion_type - web_interface vs upload?

**Answer: `web_interface` doesn't exist in current code. Default should be `upload`**

**Current Code Analysis:**
- `IngestionType` enum (ingestion_protocol.py): Only has `UPLOAD`, `EDI`, `API`
- No `web_interface` type exists
- `web_interface` was from old schema's `upload_source` field

**Recommendation:**
- ✅ **Default should be `upload`** (standard MVP pathway)
- ✅ **Remove `web_interface`** - it's not a valid ingestion type
- ✅ **Valid values:** `upload`, `edi`, `api`

**Action:**
- Change default from `web_interface` to `upload`
- Update schema to reflect actual IngestionType enum values

---

### 3. root_file_uuid vs parent_file_uuid - Separate concepts?

**Answer: YES - They are separate concepts in lineage tracking**

**Lineage Model:**
- **`parent_file_uuid`** = Immediate predecessor (direct parent in lineage tree)
  - Example: If File B was parsed from File A, then File A is parent_file_uuid of File B
  
- **`root_file_uuid`** = Original file (root of lineage tree)
  - Example: If File A → File B → File C, then File A is root_file_uuid for all three
  - Allows quick traversal to original source

**Use Cases:**
- `parent_file_uuid`: Navigate one level up (immediate parent)
- `root_file_uuid`: Navigate to original source (useful for "show me original file")
- `lineage_path`: Full path (e.g., "A→B→C") for detailed lineage visualization

**Recommendation:**
- ✅ **Keep both** - They serve different purposes in lineage tracking
- ✅ **This is standard lineage pattern** - Used in data lineage systems

---

### 4. session_id - Do we need it in Supabase?

**Answer: NO - It's a runtime concept, not persistent metadata**

**Current Usage:**
- `State Surface` uses `session_id` in file references: `file:tenant_id:session_id:file_id`
- `session_id` is for execution context, not file metadata
- Files can be accessed across sessions (they're tenant-scoped, not session-scoped)

**Recommendation:**
- ❌ **Remove `session_id` from Supabase schema**
- ✅ **Keep it in State Surface** (where it belongs - runtime execution context)
- ✅ **Files are tenant-scoped, not session-scoped** in persistent storage

**Rationale:**
- Session is a runtime/execution concept
- Files persist beyond sessions
- State Surface already tracks session context for file references
- Supabase should track persistent file metadata, not runtime context

**Action:**
- Remove `session_id` from schema
- Keep session tracking in State Surface only

---

## 🎯 Final Schema Recommendations

### Fields to Remove:
1. ❌ `mime_type` - Redundant with `content_type`
2. ❌ `session_id` - Runtime concept, not persistent metadata
3. ❌ Default `web_interface` - Not a valid ingestion type

### Fields to Keep:
1. ✅ `content_type` - MIME type (e.g., `application/pdf`)
2. ✅ `ingestion_type` - Default to `upload` (valid: `upload`, `edi`, `api`)
3. ✅ `root_file_uuid` - Original file in lineage
4. ✅ `parent_file_uuid` - Immediate parent in lineage

### Code Updates Needed:

1. **Standardize on `content_type`:**
   - Update `content_orchestrator.py` to use `content_type` parameter (or document that `mime_type` maps to `content_type`)
   - Remove `mime_type` from schema

2. **Fix ingestion_type default:**
   - Change default from `web_interface` to `upload`
   - Ensure code uses IngestionType enum values

3. **Remove session_id:**
   - Remove from schema
   - Keep in State Surface only

---

## 📋 Updated Schema (Final)

```sql
CREATE TABLE project_files (
    -- Primary Key
    uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Identity & Ownership
    user_id UUID NOT NULL,
    tenant_id UUID NOT NULL,
    -- session_id REMOVED - Runtime concept, not persistent metadata
    
    -- File Information
    ui_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    parsed_path TEXT,
    
    -- File Metadata
    file_type TEXT NOT NULL DEFAULT 'unstructured',
    content_type TEXT,  -- MIME type (e.g., application/pdf) - mime_type REMOVED
    file_size BIGINT,
    file_hash TEXT,
    file_checksum TEXT,
    
    -- Status & Processing
    status TEXT NOT NULL DEFAULT 'uploaded',
    processing_status TEXT DEFAULT 'pending',
    processing_errors JSONB,
    
    -- Ingestion
    ingestion_type TEXT DEFAULT 'upload',  -- Changed from web_interface to upload
    -- Valid values: upload, edi, api
    
    -- Audit Trail
    created_by TEXT,
    updated_by TEXT,
    client_ip INET,
    user_agent TEXT,
    
    -- Security & Compliance
    access_level TEXT DEFAULT 'open',
    permissions JSONB,
    data_classification TEXT DEFAULT 'public',
    retention_policy TEXT,
    compliance_flags JSONB,
    
    -- Platform Context
    pillar_origin TEXT DEFAULT 'content_pillar',
    service_context JSONB,
    processing_pipeline JSONB,
    
    -- Data Lineage (KEEP BOTH - separate concepts)
    arango_content_id UUID,
    lineage_depth INTEGER DEFAULT 0,
    root_file_uuid UUID,  -- Original file in lineage
    parent_file_uuid UUID,  -- Immediate parent in lineage
    generation INTEGER DEFAULT 0,
    lineage_path TEXT,
    
    -- Versioning & Insights
    version INTEGER DEFAULT 1,
    insights JSONB,
    
    -- Lifecycle Tracking
    archived_at TIMESTAMPTZ,
    archive_reason TEXT,
    purged_at TIMESTAMPTZ,
    
    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted BOOLEAN NOT NULL DEFAULT FALSE
);
```

---

## ✅ Validation Checklist

- [ ] **Schema Updated** - Removed `mime_type`, `session_id`, fixed `ingestion_type` default
- [ ] **Code Updated** - Standardize on `content_type` parameter name
- [ ] **Documentation Updated** - Document that `mime_type` parameter maps to `content_type` field
- [ ] **Tests Updated** - Verify all tests work with updated schema
- [ ] **Migration Created** - Final migration SQL ready

---

**Status:** 📋 **FINAL RECOMMENDATIONS READY FOR IMPLEMENTATION**
