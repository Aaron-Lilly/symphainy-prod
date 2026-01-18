# Supabase File Schema Comparison & Enhanced Proposal

**Date:** January 2026  
**Status:** 📋 **SCHEMA COMPARISON & ENHANCED PROPOSAL**  
**Purpose:** Compare current schema with proposed schema and incorporate valuable fields

---

## 🔍 Current Schema Analysis

### Fields to Keep (Valuable for Platform)

#### Core Identity & Ownership
- ✅ `uuid` - Primary key (keep)
- ✅ `user_id` - User identifier (keep, but change from TEXT to UUID)
- ✅ `tenant_id` - Tenant identifier (keep, but change from TEXT to UUID)
- ✅ `ui_name` - User-friendly filename (keep)

#### File Storage & Paths
- ✅ `original_path` - Rename to `file_path` (GCS storage path)
- ✅ `parsed_path` - **KEEP** - Path to parsed results (very useful!)
- ✅ `file_size` - File size in bytes (keep)
- ✅ `file_hash` - SHA256 hash (keep)
- ✅ `file_checksum` - Additional checksum (keep - useful for verification)

#### File Metadata
- ✅ `file_type` - structured/unstructured/hybrid (keep)
- ✅ `mime_type` - MIME type (keep, consolidate with content_type)
- ✅ `content_type` - Has constraint but wrong values (fix constraint)

#### Status & Processing
- ✅ `status` - File status (keep, expand values: active, archived, purged, uploaded)
- ✅ `processing_status` - **KEEP** - Track parsing/processing state (pending, processing, completed, failed)
- ✅ `processing_errors` - **KEEP** - JSONB for error tracking (very useful!)

#### Audit Trail
- ✅ `created_by` - **KEEP** - Who created the file (audit trail)
- ✅ `updated_by` - **KEEP** - Who last updated (audit trail)
- ✅ `client_ip` - **KEEP** - IP address (security/audit)
- ✅ `user_agent` - **KEEP** - User agent (security/audit)
- ✅ `upload_source` - Similar to ingestion_type (keep, rename to `ingestion_type`)

#### Security & Compliance
- ✅ `access_level` - **KEEP** - Access control (open, restricted, private)
- ✅ `permissions` - **KEEP** - JSONB for fine-grained permissions
- ✅ `data_classification` - **KEEP** - Security classification (public, internal, confidential)
- ✅ `retention_policy` - **KEEP** - Compliance/retention policy
- ✅ `compliance_flags` - **KEEP** - JSONB for compliance tracking

#### Platform Context
- ✅ `pillar_origin` - **KEEP** - Which realm/pillar (content_pillar, insights_pillar, etc.)
- ✅ `service_context` - **KEEP** - JSONB for service-specific context
- ✅ `processing_pipeline` - **KEEP** - JSONB tracking processing steps

#### Data Lineage
- ✅ `arango_content_id` - **KEEP** - Link to ArangoDB content
- ✅ `lineage_depth` - **KEEP** - Depth in lineage tree
- ✅ `root_file_uuid` - **KEEP** - Root file in lineage
- ✅ `parent_file_uuid` - **KEEP** - Parent file in lineage
- ✅ `generation` - **KEEP** - Generation number
- ✅ `lineage_path` - **KEEP** - Path in lineage tree

#### Versioning & Insights
- ✅ `version` - **KEEP** - File version number
- ✅ `insights` - **KEEP** - JSONB for insights/metadata

#### Timestamps
- ✅ `created_at` - Creation timestamp (keep)
- ✅ `updated_at` - Update timestamp (keep, add trigger)
- ✅ `deleted` - Soft delete flag (keep)

### Fields to Remove/Consolidate

- ❌ `session_id` - Not in current schema (add if needed)
- ❌ `storage_location` - Redundant with `file_path` (remove)
- ❌ `ingestion_type` - Rename from `upload_source`
- ❌ `archived_at`, `archive_reason`, `purged_at` - Can use `status` + `insights` JSONB

### Issues in Current Schema

1. **Type Mismatches:**
   - `user_id` is TEXT, should be UUID
   - `tenant_id` is TEXT, should be UUID

2. **Constraint Issue:**
   - `content_type` constraint checks for 'structured'/'unstructured'/'hybrid'
   - But `content_type` should be MIME type (e.g., 'application/pdf')
   - This constraint is on the wrong field (should be on `file_type`)

3. **Missing Fields:**
   - No `file_path` (has `original_path` instead)
   - No `session_id` (useful for session-scoped files)

---

## 🎯 Enhanced Schema Proposal

### Combined Best of Both Worlds

```sql
CREATE TABLE project_files (
    -- Primary Key
    uuid UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Identity & Ownership
    user_id UUID NOT NULL,  -- Changed from TEXT to UUID
    tenant_id UUID NOT NULL,  -- Changed from TEXT to UUID
    session_id UUID,  -- NEW: For session-scoped files
    
    -- File Information
    ui_name TEXT NOT NULL,  -- User-friendly filename
    file_path TEXT NOT NULL,  -- GCS storage path (renamed from original_path)
    parsed_path TEXT,  -- Path to parsed results (KEEP from current)
    
    -- File Metadata
    file_type TEXT NOT NULL DEFAULT 'unstructured',  -- structured, unstructured, hybrid
    mime_type TEXT,  -- MIME type (e.g., application/pdf)
    content_type TEXT,  -- Alias for mime_type (for compatibility)
    file_size BIGINT,  -- Size in bytes
    file_hash TEXT,  -- SHA256 hash
    file_checksum TEXT,  -- Additional checksum (KEEP from current)
    
    -- Status & Processing
    status TEXT NOT NULL DEFAULT 'uploaded',  -- uploaded, active, archived, purged
    processing_status TEXT DEFAULT 'pending',  -- pending, processing, completed, failed (KEEP from current)
    processing_errors JSONB,  -- Error tracking (KEEP from current)
    
    -- Ingestion
    ingestion_type TEXT DEFAULT 'web_interface',  -- web_interface, upload, edi, api (renamed from upload_source)
    
    -- Audit Trail
    created_by TEXT,  -- Who created (KEEP from current)
    updated_by TEXT,  -- Who updated (KEEP from current)
    client_ip INET,  -- IP address (KEEP from current)
    user_agent TEXT,  -- User agent (KEEP from current)
    
    -- Security & Compliance
    access_level TEXT DEFAULT 'open',  -- open, restricted, private (KEEP from current)
    permissions JSONB,  -- Fine-grained permissions (KEEP from current)
    data_classification TEXT DEFAULT 'public',  -- public, internal, confidential (KEEP from current)
    retention_policy TEXT,  -- Retention policy (KEEP from current)
    compliance_flags JSONB,  -- Compliance tracking (KEEP from current)
    
    -- Platform Context
    pillar_origin TEXT DEFAULT 'content_pillar',  -- Which realm/pillar (KEEP from current)
    service_context JSONB,  -- Service-specific context (KEEP from current)
    processing_pipeline JSONB,  -- Processing steps (KEEP from current)
    
    -- Data Lineage
    arango_content_id UUID,  -- Link to ArangoDB (KEEP from current)
    lineage_depth INTEGER DEFAULT 0,  -- Depth in lineage (KEEP from current)
    root_file_uuid UUID,  -- Root file (KEEP from current)
    parent_file_uuid UUID,  -- Parent file (KEEP from current)
    generation INTEGER DEFAULT 0,  -- Generation number (KEEP from current)
    lineage_path TEXT,  -- Lineage path (KEEP from current)
    
    -- Versioning & Insights
    version INTEGER DEFAULT 1,  -- File version (KEEP from current)
    insights JSONB,  -- Insights/metadata (KEEP from current)
    
    -- Lifecycle Tracking (in insights JSONB or separate fields)
    archived_at TIMESTAMPTZ,
    archive_reason TEXT,
    purged_at TIMESTAMPTZ,
    
    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted BOOLEAN NOT NULL DEFAULT FALSE
);

-- Constraints
ALTER TABLE project_files ADD CONSTRAINT project_files_file_type_check 
    CHECK (file_type IN ('structured', 'unstructured', 'hybrid'));

-- Indexes
CREATE INDEX idx_project_files_tenant_id ON project_files(tenant_id);
CREATE INDEX idx_project_files_user_id ON project_files(user_id);
CREATE INDEX idx_project_files_session_id ON project_files(session_id);
CREATE INDEX idx_project_files_status ON project_files(status);
CREATE INDEX idx_project_files_processing_status ON project_files(processing_status);
CREATE INDEX idx_project_files_deleted ON project_files(deleted);
CREATE INDEX idx_project_files_file_path ON project_files(file_path);
CREATE INDEX idx_project_files_created_at ON project_files(created_at DESC);
CREATE INDEX idx_project_files_pillar_origin ON project_files(pillar_origin);
CREATE INDEX idx_project_files_parent_file_uuid ON project_files(parent_file_uuid);
CREATE INDEX idx_project_files_root_file_uuid ON project_files(root_file_uuid);
CREATE INDEX idx_project_files_lineage_depth ON project_files(lineage_depth);

-- Composite indexes
CREATE INDEX idx_project_files_tenant_status ON project_files(tenant_id, status, deleted);
CREATE INDEX idx_project_files_lineage ON project_files(root_file_uuid, lineage_depth, generation);
```

---

## 📊 Field Mapping

### Current → Enhanced

| Current Field | Enhanced Field | Notes |
|--------------|---------------|-------|
| `uuid` | `uuid` | ✅ Keep as-is |
| `user_id` (TEXT) | `user_id` (UUID) | ✅ Fix type |
| `tenant_id` (TEXT) | `tenant_id` (UUID) | ✅ Fix type |
| `ui_name` | `ui_name` | ✅ Keep as-is |
| `original_path` | `file_path` | ✅ Rename for clarity |
| `parsed_path` | `parsed_path` | ✅ Keep as-is |
| `file_type` | `file_type` | ✅ Keep as-is |
| `mime_type` | `mime_type` | ✅ Keep as-is |
| `content_type` | `content_type` | ✅ Keep, fix constraint |
| `file_size` | `file_size` | ✅ Keep as-is |
| `file_hash` | `file_hash` | ✅ Keep as-is |
| `file_checksum` | `file_checksum` | ✅ Keep as-is |
| `status` | `status` | ✅ Keep, expand values |
| `processing_status` | `processing_status` | ✅ Keep as-is |
| `processing_errors` | `processing_errors` | ✅ Keep as-is |
| `upload_source` | `ingestion_type` | ✅ Rename for clarity |
| `created_by` | `created_by` | ✅ Keep as-is |
| `updated_by` | `updated_by` | ✅ Keep as-is |
| `client_ip` | `client_ip` | ✅ Keep as-is |
| `user_agent` | `user_agent` | ✅ Keep as-is |
| `access_level` | `access_level` | ✅ Keep as-is |
| `permissions` | `permissions` | ✅ Keep as-is |
| `data_classification` | `data_classification` | ✅ Keep as-is |
| `retention_policy` | `retention_policy` | ✅ Keep as-is |
| `compliance_flags` | `compliance_flags` | ✅ Keep as-is |
| `pillar_origin` | `pillar_origin` | ✅ Keep as-is |
| `service_context` | `service_context` | ✅ Keep as-is |
| `processing_pipeline` | `processing_pipeline` | ✅ Keep as-is |
| `arango_content_id` | `arango_content_id` | ✅ Keep as-is |
| `lineage_depth` | `lineage_depth` | ✅ Keep as-is |
| `root_file_uuid` | `root_file_uuid` | ✅ Keep as-is |
| `parent_file_uuid` | `parent_file_uuid` | ✅ Keep as-is |
| `generation` | `generation` | ✅ Keep as-is |
| `lineage_path` | `lineage_path` | ✅ Keep as-is |
| `version` | `version` | ✅ Keep as-is |
| `insights` | `insights` | ✅ Keep as-is |
| - | `session_id` | ✅ NEW - For session-scoped files |
| - | `archived_at` | ✅ NEW - For lifecycle tracking |
| - | `archive_reason` | ✅ NEW - For lifecycle tracking |
| - | `purged_at` | ✅ NEW - For lifecycle tracking |

---

## 🎯 Key Improvements

### 1. Type Fixes
- ✅ `user_id`: TEXT → UUID
- ✅ `tenant_id`: TEXT → UUID

### 2. Field Renames
- ✅ `original_path` → `file_path` (clearer name)
- ✅ `upload_source` → `ingestion_type` (aligns with code)

### 3. Constraint Fix
- ✅ Move constraint from `content_type` to `file_type`
- ✅ `content_type` should be MIME type, not structured/unstructured/hybrid

### 4. New Fields
- ✅ `session_id` - For session-scoped files
- ✅ `archived_at`, `archive_reason`, `purged_at` - For lifecycle tracking

### 5. Preserved Valuable Fields
- ✅ All lineage fields (critical for data lineage)
- ✅ All security/compliance fields (critical for enterprise)
- ✅ All processing fields (critical for workflow tracking)
- ✅ All audit fields (critical for compliance)

---

## 📝 Migration Notes

### Breaking Changes
1. **Type Changes:**
   - `user_id`: TEXT → UUID (requires data migration)
   - `tenant_id`: TEXT → UUID (requires data migration)

2. **Field Renames:**
   - `original_path` → `file_path`
   - `upload_source` → `ingestion_type`

3. **Constraint Changes:**
   - Remove constraint from `content_type`
   - Add constraint to `file_type`

### Migration Strategy

**Option 1: Clean Slate (Recommended for Breaking Change World)**
```sql
DROP TABLE IF EXISTS project_files CASCADE;
-- Create new table with enhanced schema
```

**Option 2: Preserve Data (If Needed)**
```sql
-- Add new fields
ALTER TABLE project_files ADD COLUMN IF NOT EXISTS session_id UUID;
ALTER TABLE project_files ADD COLUMN IF NOT EXISTS archived_at TIMESTAMPTZ;
ALTER TABLE project_files ADD COLUMN IF NOT EXISTS archive_reason TEXT;
ALTER TABLE project_files ADD COLUMN IF NOT EXISTS purged_at TIMESTAMPTZ;

-- Rename fields
ALTER TABLE project_files RENAME COLUMN original_path TO file_path;
ALTER TABLE project_files RENAME COLUMN upload_source TO ingestion_type;

-- Fix types (requires data migration)
-- ... (complex migration for user_id and tenant_id)

-- Fix constraints
ALTER TABLE project_files DROP CONSTRAINT IF EXISTS project_files_content_type_check;
ALTER TABLE project_files ADD CONSTRAINT project_files_file_type_check 
    CHECK (file_type IN ('structured', 'unstructured', 'hybrid'));
```

---

## ✅ Validation Checklist

After migration:

- [ ] **Schema Created** - All fields from current + new fields
- [ ] **Types Fixed** - user_id and tenant_id are UUID
- [ ] **Constraints Fixed** - Constraint on file_type, not content_type
- [ ] **Indexes Created** - All performance indexes
- [ ] **RLS Policies** - Row-level security for multi-tenancy
- [ ] **Triggers** - Auto-update updated_at
- [ ] **Code Alignment** - FileStorageAbstraction works with new schema
- [ ] **Lineage Works** - Lineage fields preserved and functional
- [ ] **Security Works** - Security/compliance fields functional
- [ ] **Processing Works** - Processing fields functional

---

**Status:** 📋 **ENHANCED SCHEMA READY FOR REVIEW**
