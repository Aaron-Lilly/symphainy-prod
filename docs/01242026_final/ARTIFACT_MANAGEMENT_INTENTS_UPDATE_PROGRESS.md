# Artifact Management Intents Update - Progress Report

## Status: ⏳ **IN PROGRESS**

**Date:** January 27, 2026

---

## Summary

Updating artifact management intents to use artifact-centric patterns and naming conventions.

---

## Completed Updates

### ✅ 1. Intent Routing (content_orchestrator.py)
- ✅ Added new artifact-centric intent handlers:
  - `register_artifact` (with `register_file` as legacy alias)
  - `retrieve_artifact_metadata` (with `retrieve_file_metadata` as legacy alias)
  - `retrieve_artifact` (with `retrieve_file` as legacy alias)
  - `archive_artifact` (with `archive_file` as legacy alias)
  - `delete_artifact` (with `purge_file` as legacy alias)

### ✅ 2. Service Factory Registration (service_factory.py)
- ✅ Updated `content_intents` list to include:
  - New artifact-centric intent names
  - Legacy aliases for backward compatibility

### ✅ 3. Register Artifact Implementation
- ✅ Updated `_handle_register_artifact()` method:
  - Uses `artifact_id` (with `file_id` as legacy support)
  - Registers in Artifact Registry via `state_surface.register_artifact()`
  - Sets `lifecycle_state: READY` (artifact already exists)
  - Adds materialization to artifact record
  - Returns artifact-centric response

---

## Remaining Updates

### ⏳ 4. Retrieve Artifact Metadata
**Method:** `_handle_retrieve_artifact_metadata()`
**Current:** Uses Supabase queries
**Should Be:** Uses Artifact Index (Supabase `artifact_index` table) for discovery
**Status:** ⏳ Not started

### ⏳ 5. Retrieve Artifact
**Method:** `_handle_retrieve_artifact()`
**Current:** Uses direct GCS queries and State Surface file references
**Should Be:** Uses State Surface `resolve_artifact()` as single source of truth
**Status:** ⏳ Not started

### ⏳ 6. Archive Artifact
**Method:** `_handle_archive_artifact()`
**Current:** Updates metadata in State Surface
**Should Be:** Transitions artifact `lifecycle_state` to `ARCHIVED` via `update_artifact_lifecycle()`
**Status:** ⏳ Not started

### ⏳ 7. Delete Artifact
**Method:** `_handle_delete_artifact()`
**Current:** `_handle_purge_file()` deletes from GCS
**Should Be:** Transitions artifact `lifecycle_state` to `DELETED` and deletes materializations
**Status:** ⏳ Not started

### ⏳ 8. Bulk Operations Vocabulary
**Methods:** 
- `_handle_bulk_ingest_files()`
- `_handle_bulk_parse_files()`
- `_handle_bulk_extract_embeddings()`
- `_handle_bulk_interpret_data()`

**Updates Needed:**
- Update docstrings to use artifact terminology
- Document artifact lifecycle states
- Document artifact lineage
**Status:** ⏳ Not started

---

## Implementation Notes

### Backward Compatibility
- All new artifact-centric intents have legacy aliases
- Legacy intents (`register_file`, `retrieve_file`, etc.) route to new handlers
- Both `artifact_id` and `file_id` parameters are supported (treat `file_id` as alias)

### Artifact Registry Usage
- **Registration:** Use `state_surface.register_artifact()` for new artifacts
- **Resolution:** Use `state_surface.resolve_artifact()` for retrieving artifacts
- **Lifecycle Updates:** Use `state_surface.update_artifact_lifecycle()` for state transitions
- **Materializations:** Use `state_surface.add_materialization()` for storage references

### Artifact Index Usage
- **Discovery:** Query Supabase `artifact_index` table for listing/filtering
- **Metadata:** Use Artifact Index for metadata-only queries (not full content)

### State Surface Resolution
- **Single Source of Truth:** State Surface `resolve_artifact()` is authoritative
- **No Direct Storage Queries:** Do not query GCS/Supabase directly for artifact content
- **Materializations:** Retrieve content from artifact's `materializations` array

---

## Next Steps

1. ⏳ Update `_handle_retrieve_artifact_metadata()` to use Artifact Index
2. ⏳ Update `_handle_retrieve_artifact()` to use `resolve_artifact()`
3. ⏳ Update `_handle_archive_artifact()` to transition lifecycle state
4. ⏳ Update `_handle_delete_artifact()` to transition lifecycle state and delete materializations
5. ⏳ Update bulk operations docstrings/comments to artifact-centric vocabulary

---

**Last Updated:** January 27, 2026  
**Owner:** Development Team
