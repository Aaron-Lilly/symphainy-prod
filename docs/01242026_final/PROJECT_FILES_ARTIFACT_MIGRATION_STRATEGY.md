# Project Files → Artifact-Centric Migration Strategy

**Date:** January 26, 2026  
**Status:** 📋 **READY FOR IMPLEMENTATION**  
**Approach:** In-place schema evolution (keep table name, add artifact fields)

---

## Executive Summary

Since `project_files` is hardcoded throughout the codebase (`SupabaseFileAdapter`, `FileStorageAbstraction`, etc.), we'll **evolve it in-place** rather than creating a new table. This keeps backward compatibility while enabling artifact-centric operations.

**Key Decision:** `project_files` becomes both:
- File metadata table (existing functionality)
- Artifact index table (new functionality)

---

## Strategy: Dual-Purpose Table

### Current State
```
project_files {
    uuid, user_id, tenant_id, ui_name, file_path, ...
    artifact_type (nullable)  ← Partial artifact awareness
}
```

### Target State
```
project_files {
    -- Existing file fields (keep for backward compatibility)
    uuid, user_id, tenant_id, ui_name, file_path, ...
    
    -- New artifact-centric fields
    artifact_type (required for artifacts)
    artifact_lifecycle_state (PENDING, READY, FAILED, ARCHIVED, DELETED)
    semantic_descriptor (JSONB)
    produced_by (JSONB)
    parent_artifacts (JSONB array)
}
```

**Benefits:**
- ✅ No code changes to table references
- ✅ Backward compatible (existing queries work)
- ✅ Forward compatible (new artifact queries work)
- ✅ Single source of truth

---

## Migration Steps

### Step 1: Add Artifact-Centric Columns

**Migration Script:** `project_files_artifact_migration.sql`

**Adds:**
- `artifact_lifecycle_state` (TEXT, default 'PENDING')
- `semantic_descriptor` (JSONB, default '{}')
- `produced_by` (JSONB)
- `parent_artifacts` (JSONB array, default '[]')

**Indexes:**
- `idx_project_files_tenant_artifact_lifecycle` (for UI dropdowns)
- `idx_project_files_tenant_artifact_type`
- `idx_project_files_artifact_lifecycle_state`
- `idx_project_files_parent_artifacts` (GIN for lineage)
- `idx_project_files_semantic_descriptor` (GIN)
- `idx_project_files_produced_by` (GIN)

---

### Step 2: Migrate Existing Data

**Auto-migration:**
- Set `artifact_lifecycle_state` from existing `status`/`processing_status`
- Set `semantic_descriptor` from existing `file_type`/`mime_type`
- Set `artifact_type = 'file'` for existing records

**Result:** All existing records become artifact-aware

---

### Step 3: Update Code to Populate Artifact Fields

**File:** `symphainy_platform/realms/content/orchestrators/content_orchestrator.py`

**When creating file records:**
```python
# Existing file creation (keep)
file_data = {
    "uuid": file_id,
    "tenant_id": tenant_id,
    "ui_name": ui_name,
    "file_path": storage_location,
    # ... existing fields
}

# NEW: Add artifact-centric fields
file_data.update({
    "artifact_type": "file",  # Required
    "artifact_lifecycle_state": "PENDING",  # Will transition to READY
    "semantic_descriptor": {
        "schema": "file_v1",
        "file_type": file_type,
        "mime_type": mime_type
    },
    "produced_by": {
        "intent": "ingest_file",
        "execution_id": context.execution_id
    },
    "parent_artifacts": []
})

# Write to project_files (existing code path)
await supabase_adapter.create_file(file_data)
```

**When updating lifecycle:**
```python
# Update artifact_lifecycle_state
await supabase_adapter.update_file(file_id, {
    "artifact_lifecycle_state": "READY"
})
```

---

### Step 4: Update RegistryAbstraction to Query project_files

**File:** `symphainy_platform/foundations/public_works/abstractions/registry_abstraction.py`

**New Method:**
```python
async def list_artifacts(
    self,
    tenant_id: str,
    artifact_type: Optional[str] = None,
    lifecycle_state: Optional[str] = None,
    eligible_for: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
) -> Dict[str, Any]:
    """
    List artifacts from project_files (artifact-centric query).
    """
    try:
        # Query project_files with artifact-centric filters
        query = self._client.table("project_files").select("*")
        query = query.eq("tenant_id", tenant_id)
        
        # Filter by artifact_type (required for artifact queries)
        if artifact_type:
            query = query.eq("artifact_type", artifact_type)
        else:
            # Only return records with artifact_type (artifact-aware records)
            query = query.not_.is_("artifact_type", "null")
        
        # Filter by lifecycle state
        if lifecycle_state:
            query = query.eq("artifact_lifecycle_state", lifecycle_state)
        else:
            # Default to READY/ARCHIVED
            query = query.in_("artifact_lifecycle_state", ["READY", "ARCHIVED"])
        
        # Eligibility filtering (future enhancement)
        if eligible_for:
            eligible_types = self._get_eligible_artifact_types(eligible_for)
            if eligible_types:
                query = query.in_("artifact_type", eligible_types)
        
        # Get total count
        count_result = query.execute()
        total = len(count_result.data) if count_result.data else 0
        
        # Apply pagination
        query = query.order("created_at", desc=True).limit(limit).offset(offset)
        result = query.execute()
        
        return {
            "artifacts": result.data or [],
            "total": total,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        self.logger.error(f"Failed to list artifacts: {e}", exc_info=True)
        return {
            "artifacts": [],
            "total": 0,
            "limit": limit,
            "offset": offset
        }
```

**Key Point:** Query `project_files` but filter by artifact-centric fields

---

### Step 5: Update SupabaseFileAdapter (Optional Enhancement)

**File:** `symphainy_platform/foundations/public_works/adapters/supabase_file_adapter.py`

**Add helper method:**
```python
async def create_artifact_file(
    self,
    artifact_id: str,
    artifact_type: str,
    tenant_id: str,
    semantic_descriptor: Dict[str, Any],
    produced_by: Dict[str, str],
    parent_artifacts: List[str],
    file_data: Dict[str, Any]  # Existing file fields
) -> Dict[str, Any]:
    """
    Create file record with artifact-centric fields.
    """
    file_data.update({
        "uuid": artifact_id,  # Use artifact_id as uuid
        "artifact_type": artifact_type,
        "artifact_lifecycle_state": "PENDING",
        "semantic_descriptor": semantic_descriptor,
        "produced_by": produced_by,
        "parent_artifacts": parent_artifacts
    })
    return await self.create_file(file_data)
```

**But:** This is optional - existing `create_file()` works fine if we just add the artifact fields to `file_data`.

---

## Query Patterns

### Old Pattern (File-Centric)
```python
# Query by file status
files = await supabase_adapter.list_files(
    tenant_id=tenant_id,
    filters={"status": "uploaded"}
)
```

### New Pattern (Artifact-Centric)
```python
# Query by artifact type and lifecycle
artifacts = await registry_abstraction.list_artifacts(
    tenant_id=tenant_id,
    artifact_type="file",
    lifecycle_state="READY"
)
```

**Both work!** The table supports both query patterns.

---

## Benefits of This Approach

### ✅ Backward Compatibility
- Existing code continues to work
- No breaking changes to `SupabaseFileAdapter`
- File-specific queries still work

### ✅ Forward Compatibility
- New artifact-centric queries work
- Supports UI dropdown filtering
- Supports eligibility-based listing

### ✅ Single Source of Truth
- One table for both file metadata and artifact index
- No dual-write complexity
- No sync issues

### ✅ Gradual Migration
- Can migrate queries incrementally
- No big-bang rewrite
- Test as we go

---

## Migration Checklist

### Phase 1: Schema Migration ✅
- [ ] Run `project_files_artifact_migration.sql`
- [ ] Verify columns added
- [ ] Verify indexes created
- [ ] Verify existing data migrated

### Phase 2: Code Updates
- [ ] Update `ContentOrchestrator` to populate artifact fields
- [ ] Update lifecycle state transitions
- [ ] Test artifact registration

### Phase 3: Query Migration
- [ ] Implement `RegistryAbstraction.list_artifacts()`
- [ ] Update `RuntimeAPI.list_artifacts()` to use RegistryAbstraction
- [ ] Test artifact listing

### Phase 4: Frontend Integration
- [ ] Add `listArtifacts()` to `ContentAPIManager`
- [ ] Migrate UI dropdowns
- [ ] Test end-to-end

---

## Success Criteria

### ✅ Migration Complete When:
1. ✅ `project_files` has artifact-centric columns
2. ✅ All new artifact registrations populate artifact fields
3. ✅ `list_artifacts()` queries `project_files` with artifact filters
4. ✅ UI dropdowns use artifact-centric queries
5. ✅ Existing file queries still work

---

## Notes

- **Table name stays `project_files`** (hardcoded in codebase)
- **Schema evolves** to support artifact-centric operations
- **Both query patterns work** (file-centric and artifact-centric)
- **No breaking changes** to existing code
- **Gradual migration** possible

---

## Next Steps

1. **Review this strategy**
2. **Run migration script** (`project_files_artifact_migration.sql`)
3. **Update ContentOrchestrator** to populate artifact fields
4. **Implement RegistryAbstraction.list_artifacts()**
5. **Test end-to-end**

**Status:** ✅ **READY FOR IMPLEMENTATION**
