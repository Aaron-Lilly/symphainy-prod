# Supabase File Schema Analysis & Proposal

**Date:** January 2026  
**Status:** 📋 **SCHEMA REVIEW & PROPOSAL**  
**Purpose:** Analyze current schema misalignment and propose clean schema for current platform architecture

---

## 🎯 Executive Summary

The Supabase `project_files` table schema is missing the `file_path` column that the code expects. Since we're in breaking change world, we can design a clean schema aligned with our current architecture.

---

## 🔍 Current Code Expectations

### What FileStorageAbstraction Tries to Insert (line 109-123)

```python
file_metadata = {
    "uuid": file_id,                    # ✅ Primary key
    "user_id": metadata.get("user_id"), # ✅ User identifier
    "tenant_id": metadata.get("tenant_id"), # ✅ Tenant identifier
    "ui_name": metadata.get("ui_name", file_path.split('/')[-1]), # ✅ User-friendly name
    "file_path": file_path,             # ❌ MISSING - This is the error!
    "file_type": metadata.get("file_type", "unstructured"), # ✅ File type
    "content_type": content_type,       # ✅ MIME type
    "file_size": file_size,             # ✅ File size in bytes
    "file_hash": file_hash,             # ✅ SHA256 hash
    "status": metadata.get("status", "uploaded"), # ✅ Status
    "created_at": self.clock.now_iso(), # ✅ Timestamp
    "updated_at": self.clock.now_iso(), # ✅ Timestamp
    "deleted": False                    # ✅ Soft delete flag
}
```

### What SupabaseFileAdapter Expects

From `supabase_file_adapter.py`:
- `project_files` table exists ✅
- Fields: `uuid`, `user_id`, `tenant_id`, `deleted`, `created_at`, `updated_at` ✅
- Missing: `file_path` ❌

---

## 📊 Current Architecture Requirements

### File Lifecycle (Phases 1-4)

1. **Ingestion** - Files uploaded to GCS, metadata stored in Supabase
2. **Storage** - Files in GCS, references in State Surface
3. **Retrieval** - Files retrieved via `file_path` (GCS path)
4. **Lifecycle** - Archive, restore, purge operations
5. **Lineage** - Track file relationships and transformations

### Key Requirements

1. **Storage Location** - Need `file_path` (GCS path) to retrieve files
2. **User-Friendly Names** - Need `ui_name` for UI display
3. **File Identification** - Need `uuid` (file_id) for references
4. **Tenant Isolation** - Need `tenant_id` for multi-tenancy
5. **Status Tracking** - Need `status` for lifecycle (active, archived, purged)
6. **Metadata** - Need `file_type`, `content_type`, `file_size`, `file_hash`
7. **Timestamps** - Need `created_at`, `updated_at` for audit
8. **Soft Delete** - Need `deleted` flag for soft deletes

---

## 🎯 Proposed Clean Schema

### Table: `project_files`

```sql
CREATE TABLE project_files (
    -- Primary Key
    uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Identity & Ownership
    user_id UUID NOT NULL,
    tenant_id UUID NOT NULL,
    session_id UUID,  -- Optional: for session-scoped files
    
    -- File Information
    ui_name TEXT NOT NULL,  -- User-friendly filename (e.g., "permit_application.pdf")
    file_path TEXT NOT NULL,  -- GCS storage path (e.g., "tenant_id/session_id/file_id/filename")
    storage_location TEXT NOT NULL,  -- Full GCS path (alias for file_path, for clarity)
    
    -- File Metadata
    file_type TEXT NOT NULL DEFAULT 'unstructured',  -- structured, unstructured, hybrid
    content_type TEXT NOT NULL DEFAULT 'application/octet-stream',  -- MIME type
    file_size BIGINT NOT NULL,  -- Size in bytes
    file_hash TEXT,  -- SHA256 hash for deduplication
    
    -- Lifecycle & Status
    status TEXT NOT NULL DEFAULT 'active',  -- active, archived, purged
    ingestion_type TEXT,  -- upload, edi, api
    archived_at TIMESTAMPTZ,
    archive_reason TEXT,
    purged_at TIMESTAMPTZ,
    
    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted BOOLEAN NOT NULL DEFAULT FALSE,  -- Soft delete flag
    
    -- Indexes
    CONSTRAINT project_files_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES tenants(id),
    CONSTRAINT project_files_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id)
);

-- Indexes for Performance
CREATE INDEX idx_project_files_tenant_id ON project_files(tenant_id);
CREATE INDEX idx_project_files_user_id ON project_files(user_id);
CREATE INDEX idx_project_files_session_id ON project_files(session_id);
CREATE INDEX idx_project_files_status ON project_files(status);
CREATE INDEX idx_project_files_deleted ON project_files(deleted);
CREATE INDEX idx_project_files_file_path ON project_files(file_path);
CREATE INDEX idx_project_files_created_at ON project_files(created_at DESC);

-- RLS Policies (Row Level Security)
ALTER TABLE project_files ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see files in their tenant
CREATE POLICY "Users can view files in their tenant"
    ON project_files FOR SELECT
    USING (tenant_id = auth.jwt() ->> 'tenant_id');

-- Policy: Users can insert files in their tenant
CREATE POLICY "Users can insert files in their tenant"
    ON project_files FOR INSERT
    WITH CHECK (tenant_id = auth.jwt() ->> 'tenant_id');

-- Policy: Users can update files in their tenant
CREATE POLICY "Users can update files in their tenant"
    ON project_files FOR UPDATE
    USING (tenant_id = auth.jwt() ->> 'tenant_id');

-- Policy: Users can delete files in their tenant (soft delete)
CREATE POLICY "Users can delete files in their tenant"
    ON project_files FOR DELETE
    USING (tenant_id = auth.jwt() ->> 'tenant_id');

-- Trigger: Auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_project_files_updated_at
    BEFORE UPDATE ON project_files
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

---

## 🔄 Schema Evolution Notes

### Changes from Old Schema

1. **Added `file_path`** ✅ - Critical for file retrieval
2. **Added `storage_location`** ✅ - Alias for clarity (can be same as file_path)
3. **Added `session_id`** ✅ - For session-scoped files
4. **Added `status`** ✅ - For lifecycle management (active, archived, purged)
5. **Added `ingestion_type`** ✅ - Track how file was ingested (upload, edi, api)
6. **Added `archived_at`, `archive_reason`** ✅ - For archive tracking
7. **Added `purged_at`** ✅ - For purge tracking
8. **Renamed fields** - Aligned with current code expectations

### Removed (If Existed)

- Any legacy fields not used by current code
- Any fields that don't align with current architecture

---

## 📋 Field Descriptions

### Identity & Ownership

- **`uuid`** - Primary key, file identifier (used as `file_id` in code)
- **`user_id`** - User who uploaded/owns the file
- **`tenant_id`** - Tenant for multi-tenancy isolation
- **`session_id`** - Optional session identifier for session-scoped files

### File Information

- **`ui_name`** - User-friendly filename (what user sees in UI)
- **`file_path`** - GCS storage path (e.g., `tenant_id/session_id/file_id/filename`)
- **`storage_location`** - Full storage location (can be same as file_path)

### File Metadata

- **`file_type`** - Type: `structured`, `unstructured`, `hybrid`
- **`content_type`** - MIME type (e.g., `application/pdf`, `text/csv`)
- **`file_size`** - Size in bytes
- **`file_hash`** - SHA256 hash for deduplication

### Lifecycle & Status

- **`status`** - Current status: `active`, `archived`, `purged`
- **`ingestion_type`** - How file was ingested: `upload`, `edi`, `api`
- **`archived_at`** - When file was archived (if archived)
- **`archive_reason`** - Reason for archiving
- **`purged_at`** - When file was purged (if purged)

### Timestamps

- **`created_at`** - When file was created
- **`updated_at`** - When file was last updated (auto-updated)
- **`deleted`** - Soft delete flag

---

## 🔗 Integration with Current Code

### FileStorageAbstraction (file_storage_abstraction.py)

**Current Code (line 109-123):**
```python
file_metadata = {
    "uuid": file_id,
    "user_id": metadata.get("user_id"),
    "tenant_id": metadata.get("tenant_id"),
    "ui_name": metadata.get("ui_name", file_path.split('/')[-1]),
    "file_path": file_path,  # ✅ Now supported!
    "file_type": metadata.get("file_type", "unstructured"),
    "content_type": content_type,
    "file_size": file_size,
    "file_hash": file_hash,
    "status": metadata.get("status", "uploaded"),
    "created_at": self.clock.now_iso(),
    "updated_at": self.clock.now_iso(),
    "deleted": False
}
```

**Status:** ✅ Code already expects this schema (just needs `file_path` added)

### Content Orchestrator (content_orchestrator.py)

**Archive File (line ~1400):**
```python
updated_metadata = {
    **file_metadata,
    "status": "archived",
    "archived_at": self.clock.now_iso(),
    "archive_reason": reason
}
```

**Status:** ✅ Code expects `status`, `archived_at`, `archive_reason`

### State Surface Integration

**File Reference Format:**
```
file:tenant_id:session_id:file_id
```

**Storage Location:**
```
tenant_id/session_id/file_id/ui_name
```

**Status:** ✅ Schema supports this pattern

---

## 🎯 Migration Strategy

### Option 1: Drop & Recreate (Breaking Change - Recommended)

Since we're in breaking change world:

```sql
-- Drop old table (if exists)
DROP TABLE IF EXISTS project_files CASCADE;

-- Create new table with clean schema
-- (Use schema from "Proposed Clean Schema" section above)
```

**Pros:**
- ✅ Clean slate
- ✅ No migration complexity
- ✅ Aligned with current architecture

**Cons:**
- ❌ Loses existing data (acceptable in breaking change world)

### Option 2: Alter Table (If Data Preservation Needed)

```sql
-- Add missing columns
ALTER TABLE project_files ADD COLUMN IF NOT EXISTS file_path TEXT;
ALTER TABLE project_files ADD COLUMN IF NOT EXISTS storage_location TEXT;
ALTER TABLE project_files ADD COLUMN IF NOT EXISTS session_id UUID;
ALTER TABLE project_files ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'active';
ALTER TABLE project_files ADD COLUMN IF NOT EXISTS ingestion_type TEXT;
ALTER TABLE project_files ADD COLUMN IF NOT EXISTS archived_at TIMESTAMPTZ;
ALTER TABLE project_files ADD COLUMN IF NOT EXISTS archive_reason TEXT;
ALTER TABLE project_files ADD COLUMN IF NOT EXISTS purged_at TIMESTAMPTZ;

-- Update existing records
UPDATE project_files SET status = 'active' WHERE status IS NULL;
UPDATE project_files SET file_path = storage_location WHERE file_path IS NULL AND storage_location IS NOT NULL;

-- Add NOT NULL constraints (after data migration)
ALTER TABLE project_files ALTER COLUMN file_path SET NOT NULL;
ALTER TABLE project_files ALTER COLUMN storage_location SET NOT NULL;
ALTER TABLE project_files ALTER COLUMN status SET NOT NULL;
```

**Pros:**
- ✅ Preserves existing data
- ✅ Gradual migration

**Cons:**
- ❌ More complex
- ❌ May have legacy data issues

---

## ✅ Validation Checklist

After schema update:

- [ ] **Schema Created** - `project_files` table with all required fields
- [ ] **Indexes Created** - Performance indexes for common queries
- [ ] **RLS Policies** - Row-level security for multi-tenancy
- [ ] **Triggers** - Auto-update `updated_at` timestamp
- [ ] **Code Alignment** - FileStorageAbstraction can insert all fields
- [ ] **File Upload Test** - Verify metadata creation works
- [ ] **File Retrieval Test** - Verify file_path is used correctly
- [ ] **Archive Test** - Verify status, archived_at, archive_reason work
- [ ] **List Files Test** - Verify queries work with new schema

---

## 🔗 Next Steps

1. **Review Schema** - Confirm schema aligns with requirements
2. **Create Migration** - Generate SQL migration script
3. **Test Migration** - Run on test Supabase instance
4. **Update Code** - Ensure code uses all new fields
5. **Run Tests** - Verify all tests pass with new schema
6. **Deploy** - Apply to production Supabase

---

## 📝 Notes

- **Breaking Change World** - No need to preserve legacy schemas
- **Clean Architecture** - Schema aligned with current platform architecture
- **Future-Proof** - Schema supports all Phase 1-4 features
- **Multi-Tenancy** - RLS policies ensure tenant isolation
- **Performance** - Indexes on common query fields

---

**Status:** 📋 **READY FOR REVIEW & IMPLEMENTATION**
