# Artifact Index vs Project Files: Architecture Decision

**Date:** January 26, 2026  
**Context:** Choosing between in-place evolution vs. clean migration  
**Status:** 📋 **DECISION ANALYSIS**

---

## Executive Summary

After analyzing both options, I **strongly recommend Option 2: Create `artifact_index` and migrate**. Here's why:

---

## Option 1: Evolve `project_files` In-Place

### Where `project_files` is Hardcoded

**Infrastructure Layer (Acceptable):**
- `SupabaseFileAdapter` - 5 references (adapter layer, OK to hardcode)
- `FileStorageAbstraction` - 2 references (abstraction, acceptable)
- `ArtifactStorageAbstraction` - 1 reference (abstraction, acceptable)

**Business Logic Layer (Problem):**
- `ContentOrchestrator` - 1 reference (⚠️ **VIOLATION** - should use abstraction)

**Total:** 9 references, 1 architectural violation

### Pros
- ✅ No code changes to adapters
- ✅ Backward compatible
- ✅ Quick to implement

### Cons
- ❌ **Enables architectural violations** (ContentOrchestrator directly accessing adapter)
- ❌ **Misleading table name** - it's not just "files" anymore
- ❌ **Mixed concerns** - file metadata + artifact index in one table
- ❌ **Technical debt** - working around design flaw instead of fixing it
- ❌ **Confusing schema** - has both file-centric and artifact-centric fields
- ❌ **Future confusion** - "Is this a file table or artifact table?"

### Architecture Impact
```
project_files {
    -- File-specific fields (legacy)
    uuid, user_id, ui_name, file_path, status, processing_status, ...
    
    -- Artifact fields (new)
    artifact_type, artifact_lifecycle_state, semantic_descriptor, ...
}
```

**Problem:** This is a **schema smell** - one table doing two jobs.

---

## Option 2: Create `artifact_index` and Migrate

### Migration Scope

**Files to Update:**
1. `SupabaseFileAdapter` - Change table name (5 places)
2. `FileStorageAbstraction` - Change table name (2 places)
3. `ArtifactStorageAbstraction` - Change table name (1 place)
4. `ContentOrchestrator` - **Fix architectural violation** (1 place - should use abstraction)

**Total:** 9 references, but 1 is a bug fix anyway

### Pros
- ✅ **Clean architecture** - proper naming, single purpose
- ✅ **Fixes architectural violation** - forces ContentOrchestrator to use abstraction
- ✅ **Clear separation of concerns** - artifact index is for discovery
- ✅ **Future-proof** - aligns with artifact-centric vision
- ✅ **Self-documenting** - table name reflects purpose
- ✅ **No schema confusion** - artifact_index is clearly for artifacts

### Cons
- ⚠️ Requires updating 9 references (but 1 is a bug fix)
- ⚠️ More work upfront (but cleaner long-term)

### Architecture Impact
```
artifact_index {
    -- Artifact-centric fields only
    artifact_id, artifact_type, tenant_id,
    lifecycle_state, semantic_descriptor,
    produced_by, parent_artifacts, ...
}

project_files {
    -- File metadata only (if still needed)
    -- OR: Deprecate entirely if not needed
}
```

**Benefit:** Clear separation, proper naming, aligned with architecture.

---

## Key Insight: The ContentOrchestrator Violation

**Current Code:**
```python
# ContentOrchestrator._get_file_metadata_from_supabase()
query = supabase_file_adapter._client.table("project_files").select("*")
```

**Problem:** Business logic directly accessing adapter (violates layering).

**Should Be:**
```python
# Use abstraction instead
file_metadata = await self.public_works.file_storage_abstraction.get_file_by_uuid(file_id)
```

**Option 2 forces us to fix this violation** - that's a win, not a cost.

---

## Recommendation: Option 2 (artifact_index)

### Why Option 2 is Better

1. **Architectural Correctness**
   - Fixes the ContentOrchestrator violation
   - Proper separation of concerns
   - Aligned with artifact-centric vision

2. **Code Quality**
   - Self-documenting table name
   - No schema confusion
   - Clean, purpose-built schema

3. **Future Maintenance**
   - Easier to understand
   - Easier to extend
   - No technical debt

4. **Migration Effort**
   - Only 9 references (manageable)
   - 1 is a bug fix anyway
   - Can be done incrementally

### Migration Strategy

**Phase 1: Create artifact_index**
- Run migration script
- Create new table with clean schema

**Phase 2: Dual-Write (Temporary)**
- Write to both `project_files` (old) and `artifact_index` (new)
- Update adapters to write to both
- Test artifact registration

**Phase 3: Update Reads**
- Update `RegistryAbstraction.list_artifacts()` to query `artifact_index`
- Update `RuntimeAPI.list_artifacts()` to use RegistryAbstraction
- Fix ContentOrchestrator to use abstraction

**Phase 4: Deprecate project_files**
- Stop writing to `project_files` for artifacts
- Keep `project_files` for file-specific operations (if needed)
- Or deprecate entirely if not needed

---

## Comparison Table

| Criteria | Option 1: Evolve project_files | Option 2: Create artifact_index |
|----------|-------------------------------|----------------------------------|
| **Code Changes** | Minimal (add columns) | Moderate (9 references) |
| **Architecture** | ❌ Mixed concerns | ✅ Clean separation |
| **Naming** | ❌ Misleading | ✅ Self-documenting |
| **Technical Debt** | ❌ Creates debt | ✅ Reduces debt |
| **Future Maintenance** | ❌ Confusing | ✅ Clear |
| **Fixes Violations** | ❌ No | ✅ Yes (ContentOrchestrator) |
| **Migration Complexity** | ✅ Simple | ⚠️ Moderate |
| **Long-term Cost** | ❌ High (confusion) | ✅ Low (clarity) |

---

## Final Recommendation

**Choose Option 2: Create `artifact_index`**

**Reasoning:**
1. You're the only user - perfect time to fix architecture properly
2. Only 9 references to update (manageable)
3. Fixes architectural violation (ContentOrchestrator)
4. Clean, purpose-built schema
5. Aligned with artifact-centric vision
6. No technical debt

**The extra work upfront pays off in:**
- Cleaner architecture
- Better maintainability
- Proper separation of concerns
- Self-documenting code

---

## Implementation Plan (Option 2)

### Step 1: Create artifact_index Table ✅
- Run `artifact_index_migration.sql`
- Verify table and indexes

### Step 2: Update Adapters (Dual-Write)
- Update `SupabaseFileAdapter` to also write to `artifact_index`
- Keep writing to `project_files` temporarily
- Test dual-write

### Step 3: Update Abstractions
- Update `RegistryAbstraction.list_artifacts()` to query `artifact_index`
- Update `FileStorageAbstraction` if needed

### Step 4: Fix ContentOrchestrator
- Remove direct adapter access
- Use `FileStorageAbstraction` instead
- This fixes the architectural violation

### Step 5: Update Runtime API
- `RuntimeAPI.list_artifacts()` uses `RegistryAbstraction`
- Test end-to-end

### Step 6: Deprecate project_files (Optional)
- If `project_files` is only used for artifacts, deprecate it
- If it's used for file-specific operations, keep it but stop artifact writes

---

## Conclusion

**Option 2 is the right choice** because:
- ✅ Clean architecture
- ✅ Fixes violations
- ✅ Aligned with vision
- ✅ Manageable migration
- ✅ No technical debt

**The work is worth it** - you're building the foundation correctly.

---

## Next Steps

1. **Review this analysis**
2. **Approve Option 2**
3. **Run `artifact_index_migration.sql`**
4. **Begin migration (dual-write pattern)**
5. **Fix ContentOrchestrator violation**

**Status:** ✅ **READY FOR DECISION**
