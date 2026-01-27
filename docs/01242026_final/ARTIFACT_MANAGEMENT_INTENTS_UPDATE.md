# Artifact Management Intents - Artifact-Centric Update Plan

## Status: ⏳ **IN PROGRESS**

**Date:** January 27, 2026

---

## Summary

The following intents need to be updated to use artifact-centric patterns instead of file-centric patterns:

1. `register_file` → Should be `register_artifact` (or keep name but use artifact patterns)
2. `retrieve_file` → Should use `resolve_artifact()` from State Surface
3. `retrieve_file_metadata` → Should use Artifact Index for discovery
4. `archive_file` → Should transition artifact `lifecycle_state` to `ARCHIVED`
5. `purge_file` → Should transition artifact `lifecycle_state` to `DELETED` (or actually delete)

**Note:** These intents don't need contracts yet, but should be updated to use artifact-centric patterns to avoid anti-patterns.

---

## Current Implementation Analysis

### 1. `register_file`
**Current:** Registers existing file in State Surface (file-centric)
**Should Be:** Registers existing artifact in Artifact Registry
- Use `artifact_id` instead of `file_id`
- Register in Artifact Registry (State Surface)
- Index in Artifact Index (Supabase)
- Set `lifecycle_state: "READY"` (artifact already exists)

### 2. `retrieve_file`
**Current:** Gets file contents from GCS (file-centric)
**Should Be:** Resolves artifact via State Surface `resolve_artifact()`
- Use `artifact_id` instead of `file_id`
- Use State Surface `resolve_artifact(artifact_id)` as single source of truth
- Retrieve content from artifact's `materializations` array
- No direct GCS queries

### 3. `retrieve_file_metadata`
**Current:** Gets Supabase record (metadata only, file-centric)
**Should Be:** Discovers artifact metadata via Artifact Index
- Use `artifact_id` instead of `file_id`
- Query Artifact Index (Supabase `artifact_index` table)
- Return artifact metadata (not full content)
- This is discovery, not resolution

### 4. `archive_file`
**Current:** Soft delete (updates metadata, file-centric)
**Should Be:** Transitions artifact lifecycle state to `ARCHIVED`
- Use `artifact_id` instead of `file_id`
- Update Artifact Registry: `lifecycle_state: "PENDING"` or `"READY"` → `"ARCHIVED"`
- Update Artifact Index: `lifecycle_state: "ARCHIVED"`
- Preserve artifact and materializations (soft delete)

### 5. `purge_file`
**Current:** Permanently deletes file (file-centric)
**Should Be:** Transitions artifact lifecycle state to `DELETED` (or actually deletes)
- Use `artifact_id` instead of `file_id`
- Update Artifact Registry: `lifecycle_state: "DELETED"`
- Update Artifact Index: `lifecycle_state: "DELETED"`
- Delete materializations from storage (GCS, DuckDB, ArangoDB)
- Optionally: Actually delete artifact record (hard delete)

### 6. `delete_artifact` (Missing)
**Current:** Doesn't exist
**Should Be:** Created as explicit delete intent
- Transitions artifact `lifecycle_state` to `DELETED`
- Deletes materializations
- Optionally hard deletes artifact record

---

## Bulk Operations - Artifact-Centric Vocabulary Update

### Current Bulk Operations
- `bulk_ingest_files` → Should use artifact terminology in comments/docstrings
- `bulk_parse_files` → Should use artifact terminology in comments/docstrings
- `bulk_extract_embeddings` → Should use artifact terminology in comments/docstrings
- `bulk_interpret_data` → Should use artifact terminology in comments/docstrings

### Updates Needed
1. Update parameter names in docstrings: `file_ids` → `artifact_ids` (or keep for compatibility but document artifact-centric thinking)
2. Update return values: `file_id` → `artifact_id`
3. Update comments: "file" → "artifact" where appropriate
4. Document artifact lifecycle states in bulk operations
5. Document artifact lineage in bulk operations

---

## Implementation Priority

### Phase 1 (Critical - Do Now)
1. ✅ Create contract for `create_deterministic_embeddings`
2. ✅ Register `create_deterministic_embeddings` in `service_factory.py`
3. ⏳ Update `register_file` to use artifact-centric patterns
4. ⏳ Update `retrieve_file` to use `resolve_artifact()`
5. ⏳ Update `archive_file` to transition lifecycle state
6. ⏳ Update `purge_file` to transition lifecycle state

### Phase 2 (Important - Do Soon)
1. ⏳ Update `retrieve_file_metadata` to use Artifact Index
2. ⏳ Create `delete_artifact` intent (if needed)
3. ⏳ Update bulk operations vocabulary in docstrings/comments

### Phase 3 (Nice to Have - Do Later)
1. ⏳ Create contracts for artifact management intents
2. ⏳ Create contracts for bulk operations

---

## Code Updates Required

### `register_file` Updates
```python
# Change: file_id → artifact_id
# Change: file_reference → artifact_id
# Change: State Surface store_file_reference → Artifact Registry register_artifact
# Change: Set lifecycle_state: "READY" (artifact already exists)
```

### `retrieve_file` Updates
```python
# Change: file_id → artifact_id
# Change: Direct GCS query → State Surface resolve_artifact(artifact_id)
# Change: Get content from artifact.materializations array
```

### `retrieve_file_metadata` Updates
```python
# Change: file_id → artifact_id
# Change: Supabase query → Artifact Index query (artifact_index table)
# Change: Return artifact metadata (not file metadata)
```

### `archive_file` Updates
```python
# Change: file_id → artifact_id
# Change: Update metadata → Transition lifecycle_state to "ARCHIVED"
# Change: Update Artifact Registry and Artifact Index
```

### `purge_file` Updates
```python
# Change: file_id → artifact_id
# Change: Delete file → Transition lifecycle_state to "DELETED" + delete materializations
# Change: Update Artifact Registry and Artifact Index
```

---

## Notes

- **Backward Compatibility:** Keep parameter names like `file_id` for backward compatibility, but internally use `artifact_id` and document artifact-centric thinking
- **Legacy Support:** Support both `file_id` and `artifact_id` parameters (treat `file_id` as alias)
- **State Surface:** Use State Surface `resolve_artifact()` for resolution, Artifact Index for discovery
- **Lifecycle States:** Use proper lifecycle state transitions (`PENDING` → `READY` → `ARCHIVED` → `DELETED`)

---

**Last Updated:** January 27, 2026  
**Owner:** Development Team
