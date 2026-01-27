# Supabase Tables Analysis and Evolution Plan

**Date:** January 26, 2026  
**Context:** Artifact-centric architecture migration  
**Status:** 📋 **ANALYSIS COMPLETE - READY FOR IMPLEMENTATION**

---

## Executive Summary

We have **multiple overlapping Supabase tables** that evolved organically. Some are actively used, others are legacy. This analysis identifies what's actually being used and proposes a clean evolution path aligned with our artifact-centric architecture.

**Key Finding:** We need a unified `artifact_index` table that serves as the discovery layer, while State Surface (ArangoDB) remains the authoritative resolution layer.

---

## 1. Current Supabase Tables Inventory

### 1.1 Tables from `table_list.md`

```
Agents, Analyses, Artifacts, capabilities, contracts, data_boundary_contracts, 
embedding_files, embeddings, file_links, guides, interpretations, 
materialization_policies, parsed_data_files, parsed_results, policy_rules, 
project_files, records_of_fact, services, tenants, user_tenants
```

### 1.2 Focus Tables (Content Pillar)

1. **`project_files`** - Main file metadata table (heavily used)
2. **`artifacts`** - Legacy artifact table (exists but misaligned)
3. **`parsed_results`** - Parsed file lineage (used for tracking)
4. **`embedding_files`** - Embedding lineage (used for tracking)

---

## 2. Current Usage Analysis

### 2.1 `project_files` Table ✅ **ACTIVELY USED**

**Used By:**
- `SupabaseFileAdapter` (primary interface)
- `FileStorageAbstraction` (via adapter)
- `ContentOrchestrator._get_file_metadata_from_supabase()`

**Usage Patterns:**
```python
# SupabaseFileAdapter.create_file()
self._client.table("project_files").insert(filtered_data).execute()

# SupabaseFileAdapter.get_file_by_uuid()
self._client.table("project_files").select("*").eq("uuid", file_uuid).execute()

# ContentOrchestrator._get_file_metadata_from_supabase()
# Queries project_files for file metadata
```

**Schema Purpose:**
- Stores file metadata (uuid, user_id, tenant_id, ui_name, file_path, etc.)
- Tracks file lineage (parent_file_uuid, root_file_uuid, lineage_depth)
- Stores materialization metadata (boundary_contract_id, materialization_backing_store)
- Has artifact_type field (nullable) - **indicates partial artifact awareness**

**Key Fields:**
- `uuid` (PK) - File identifier
- `file_path` - GCS storage path
- `parsed_path` - Parsed file GCS path
- `artifact_type` - **NEW** (nullable) - Partial artifact awareness
- `boundary_contract_id` - Materialization policy
- `materialization_backing_store` - Storage backend
- Lineage fields (parent_file_uuid, root_file_uuid, lineage_depth)

**Assessment:** ✅ **KEEP** (but mark as legacy for migration)

---

### 2.2 `artifacts` Table ⚠️ **EXISTS BUT MISALIGNED**

**Schema Analysis:**
- Has `artifact_id`, `artifact_type`, `lifecycle_state`
- **BUT** lifecycle states are wrong: `'draft'`, `'accepted'`, `'obsolete'`
- **Our new registry uses:** `'PENDING'`, `'READY'`, `'FAILED'`, `'ARCHIVED'`, `'DELETED'`
- Has `owner` field (`'client'`, `'platform'`, `'shared'`) - not in our schema
- Has `purpose` field (`'decision_support'`, `'delivery'`, etc.) - not in our schema
- Has `payload_storage_path` - single path (we use multiple materializations)
- Has `parent_artifact_id` (single) - we use `parent_artifacts` (array)

**Usage:**
- ❌ **NOT USED** in current codebase
- Appears to be from an older design iteration

**Assessment:** ⚠️ **DEPRECATE** (don't use, plan to drop after migration)

---

### 2.3 `parsed_results` Table ✅ **USED FOR LINEAGE**

**Used By:**
- `ContentOrchestrator._track_parsed_result()`
- Queried via `RegistryAbstraction.query_records()`

**Usage Pattern:**
```python
# ContentOrchestrator._track_parsed_result()
parsed_result_record = {
    "id": str(uuid.uuid4()),
    "tenant_id": tenant_id,
    "file_id": file_id,
    "parsed_result_id": parsed_file_id,
    "gcs_path": gcs_path,
    "parser_type": parser_type,
    "parser_config": parser_config,
    "record_count": record_count,
    "status": status,
    "created_at": datetime.utcnow().isoformat()
}
await registry.create_record("parsed_results", parsed_result_record)
```

**Purpose:**
- Tracks parsed file lineage (file_id → parsed_file_id)
- Stores GCS path for parsed content
- Stores parser metadata

**Assessment:** ✅ **KEEP** (but migrate to artifact_index)

---

### 2.4 `embedding_files` Table ✅ **USED FOR LINEAGE**

**Used By:**
- `ContentOrchestrator._track_embedding()`
- Queried via `RegistryAbstraction.query_records()`

**Usage Pattern:**
```python
# ContentOrchestrator._track_embedding()
embedding_record = {
    "id": str(uuid.uuid4()),
    "tenant_id": tenant_id,
    "parsed_result_id": parsed_file_id,
    "embedding_id": embedding_id,
    "arango_collection": arango_collection,
    "arango_key": arango_key,
    "embedding_count": embedding_count,
    "model_name": model_name,
    "created_at": datetime.utcnow().isoformat()
}
await registry.create_record("embedding_files", embedding_record)
```

**Purpose:**
- Tracks embedding lineage (parsed_file_id → embedding_id)
- Stores ArangoDB collection/key references

**Assessment:** ✅ **KEEP** (but migrate to artifact_index)

---

## 3. Architectural Alignment Analysis

### 3.1 Current State (File-Centric)

```
┌─────────────────┐
│  project_files  │ ← File metadata (heavily used)
└─────────────────┘
        │
        ├──→ parsed_results (lineage)
        └──→ embedding_files (lineage)
```

**Problems:**
- `project_files` is file-centric, not artifact-centric
- Lineage is split across multiple tables
- No unified artifact discovery
- `artifact_type` field exists but is nullable (partial awareness)

---

### 3.2 Target State (Artifact-Centric)

```
┌──────────────────┐
│  artifact_index  │ ← Discovery/exploration (NEW)
└──────────────────┘
        │
        └──→ State Surface (ArangoDB) ← Authoritative resolution
```

**Benefits:**
- Unified artifact discovery
- Single source of truth for artifact metadata
- Supports eligibility-based filtering
- Aligned with CTO-recommended schema

---

## 4. Evolution Plan

### Phase 1: Create `artifact_index` Table ✅ **READY**

**Purpose:** Discovery and exploration layer (Supabase)

**Schema Alignment:**
- Matches CTO-recommended `ArtifactRecord` schema
- Supports UI dropdown queries
- Supports eligibility filtering

**Key Fields:**
- `artifact_id` (PK) - Stable identifier
- `artifact_type` - Type of artifact
- `tenant_id` - Tenant identifier
- `lifecycle_state` - `'PENDING'`, `'READY'`, `'FAILED'`, `'ARCHIVED'`, `'DELETED'`
- `semantic_descriptor` (JSONB) - Schema, record_count, parser_type, embedding_model
- `parent_artifacts` (JSONB array) - Lineage
- `produced_by` (JSONB) - Intent, execution_id
- `created_at`, `updated_at` - Timestamps

**Indexes:**
- `tenant_id`, `artifact_type`, `lifecycle_state` (for filtering)
- `tenant_id`, `artifact_type`, `lifecycle_state` (composite for dropdowns)
- `parent_artifacts` (GIN for lineage queries)

---

### Phase 2: Dual-Write Pattern (Migration)

**Strategy:** Write to both old and new tables during migration

1. **Artifact Registration:**
   - Write to State Surface (authoritative) ✅ **DONE**
   - Write to `artifact_index` (discovery) ✅ **TODO**

2. **File Operations:**
   - Continue writing to `project_files` (backward compatibility)
   - Also write to `artifact_index` (new pattern)

3. **Lineage Tracking:**
   - Continue writing to `parsed_results`, `embedding_files` (backward compatibility)
   - Also write to `artifact_index` with proper lineage

**Duration:** 2-4 weeks (until all code paths migrated)

---

### Phase 3: Read Migration

**Strategy:** Gradually migrate reads from old tables to `artifact_index`

1. **UI Dropdowns:**
   - Migrate from `project_files` queries to `artifact_index` queries
   - Use `listArtifacts()` API endpoint

2. **Lineage Queries:**
   - Migrate from `parsed_results`/`embedding_files` to `artifact_index.parent_artifacts`
   - Use GIN index for efficient lineage queries

**Duration:** 2-4 weeks (parallel with Phase 2)

---

### Phase 4: Deprecation

**Strategy:** Remove old tables after migration complete

1. **Mark as deprecated:**
   - `project_files` → Keep for historical data, stop new writes
   - `parsed_results` → Migrate to `artifact_index`, then drop
   - `embedding_files` → Migrate to `artifact_index`, then drop
   - `artifacts` → Drop (never used)

2. **Data Migration:**
   - Migrate existing `project_files` records to `artifact_index` (if needed)
   - Migrate lineage from `parsed_results`/`embedding_files` to `artifact_index`

**Duration:** 1-2 weeks (after all reads migrated)

---

## 5. Recommended Schema: `artifact_index`

### 5.1 Table Definition

```sql
CREATE TABLE public.artifact_index (
    -- Identity
    artifact_id TEXT NOT NULL,
    artifact_type TEXT NOT NULL,
    tenant_id UUID NOT NULL,
    
    -- Lifecycle
    lifecycle_state TEXT NOT NULL DEFAULT 'PENDING',
    
    -- Semantics (what it means)
    semantic_descriptor JSONB NOT NULL DEFAULT '{}',
    
    -- Provenance
    produced_by JSONB NOT NULL,
    parent_artifacts JSONB NOT NULL DEFAULT '[]',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT artifact_index_pkey PRIMARY KEY (artifact_id),
    CONSTRAINT artifact_index_lifecycle_state_check CHECK (
        lifecycle_state IN ('PENDING', 'READY', 'FAILED', 'ARCHIVED', 'DELETED')
    ),
    CONSTRAINT artifact_index_artifact_type_check CHECK (
        artifact_type IN ('file', 'parsed_content', 'embeddings', 'summary', 'workflow', 'sop', 'solution')
    )
);

-- Indexes for discovery/exploration
CREATE INDEX idx_artifact_index_tenant_type_state 
    ON public.artifact_index (tenant_id, artifact_type, lifecycle_state)
    WHERE lifecycle_state IN ('READY', 'ARCHIVED');

CREATE INDEX idx_artifact_index_tenant_type 
    ON public.artifact_index (tenant_id, artifact_type);

CREATE INDEX idx_artifact_index_lifecycle_state 
    ON public.artifact_index (lifecycle_state);

CREATE INDEX idx_artifact_index_parent_artifacts 
    ON public.artifact_index USING GIN (parent_artifacts);

CREATE INDEX idx_artifact_index_created_at 
    ON public.artifact_index (created_at DESC);

CREATE INDEX idx_artifact_index_semantic_descriptor 
    ON public.artifact_index USING GIN (semantic_descriptor);

-- Update trigger
CREATE TRIGGER update_artifact_index_updated_at
    BEFORE UPDATE ON public.artifact_index
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

### 5.2 Schema Alignment

**Matches CTO-Recommended Schema:**
- ✅ Identity (artifact_id, artifact_type, tenant_id)
- ✅ Lifecycle (lifecycle_state)
- ✅ Semantics (semantic_descriptor JSONB)
- ✅ Provenance (produced_by, parent_artifacts)
- ✅ Timestamps (created_at, updated_at)

**Note:** Materializations are NOT stored here (they're in State Surface). This table is for discovery only.

---

## 6. Migration Strategy

### 6.1 Backward Compatibility

**Keep `project_files` for:**
- Historical file metadata
- Existing queries (during migration)
- File-specific operations (if needed)

**But:**
- Mark as legacy
- Stop new writes after migration
- Document deprecation timeline

### 6.2 Dual-Write Pattern

**When registering artifacts:**
```python
# 1. Register in State Surface (authoritative) ✅ DONE
await context.state_surface.register_artifact(...)

# 2. Write to artifact_index (discovery) ✅ TODO
await registry_abstraction.create_record("artifact_index", {
    "artifact_id": artifact_id,
    "artifact_type": artifact_type,
    "tenant_id": tenant_id,
    "lifecycle_state": lifecycle_state,
    "semantic_descriptor": semantic_descriptor.to_dict(),
    "produced_by": produced_by.to_dict(),
    "parent_artifacts": parent_artifacts
})
```

### 6.3 Read Migration

**Old Pattern:**
```python
# Query project_files
files = await supabase_adapter.list_files(tenant_id=tenant_id)
```

**New Pattern:**
```python
# Query artifact_index
artifacts = await registry_abstraction.query_records(
    table="artifact_index",
    filters={
        "tenant_id": tenant_id,
        "artifact_type": "file",
        "lifecycle_state": "READY"
    }
)
```

---

## 7. Implementation Steps

### Step 1: Create `artifact_index` Table ✅ **READY**

- [ ] Create migration script
- [ ] Add indexes
- [ ] Add update trigger
- [ ] Test schema

### Step 2: Update Artifact Registration

- [ ] Add dual-write to `ContentOrchestrator` artifact registration
- [ ] Write to `artifact_index` after State Surface registration
- [ ] Test dual-write pattern

### Step 3: Update Registry Abstraction

- [ ] Add `list_artifacts()` method to `RegistryAbstraction`
- [ ] Query `artifact_index` with filters
- [ ] Support pagination
- [ ] Support `eligible_for` filtering (computed)

### Step 4: Update Runtime API

- [ ] Implement `list_artifacts()` in `RuntimeAPI` (currently placeholder)
- [ ] Use `RegistryAbstraction.list_artifacts()`
- [ ] Test API endpoint

### Step 5: Frontend Migration

- [ ] Add `listArtifacts()` to `ContentAPIManager`
- [ ] Migrate dropdowns to use `listArtifacts()`
- [ ] Test UI dropdowns

### Step 6: Deprecation

- [ ] Mark `project_files` as legacy
- [ ] Stop new writes to `project_files`
- [ ] Migrate existing data (if needed)
- [ ] Drop old tables (after migration complete)

---

## 8. Recommendations

### ✅ **DO**

1. **Create `artifact_index` table** aligned with CTO-recommended schema
2. **Use dual-write pattern** during migration (State Surface + artifact_index)
3. **Keep `project_files`** for backward compatibility (mark as legacy)
4. **Migrate lineage tracking** to `artifact_index.parent_artifacts`
5. **Use `artifact_index`** for all UI dropdown queries

### ❌ **DON'T**

1. **Don't use old `artifacts` table** (misaligned schema)
2. **Don't store materializations in Supabase** (State Surface is authoritative)
3. **Don't query State Surface for listing** (use artifact_index for discovery)
4. **Don't break backward compatibility** (keep project_files during migration)

---

## 9. Success Criteria

### ✅ Phase 1 Complete When:
- `artifact_index` table created
- Artifact registration writes to both State Surface and artifact_index
- `list_artifacts()` API endpoint functional

### ✅ Migration Complete When:
- All UI dropdowns use `artifact_index`
- All lineage queries use `artifact_index.parent_artifacts`
- `project_files` marked as legacy (no new writes)

### ✅ Deprecation Complete When:
- All reads migrated to `artifact_index`
- Old tables dropped or archived
- Documentation updated

---

## 10. Next Steps

1. **Review this analysis** with team
2. **Create `artifact_index` migration script** (Phase 1)
3. **Implement dual-write pattern** in artifact registration
4. **Implement `list_artifacts()` in RegistryAbstraction**
5. **Test end-to-end** (registration → listing → resolution)

**Status:** ✅ **READY FOR PHASE 2B IMPLEMENTATION**
