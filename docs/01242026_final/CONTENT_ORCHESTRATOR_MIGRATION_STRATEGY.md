# Content Orchestrator Migration Strategy

## Status: ⏳ **IN PROGRESS**

**Date:** January 27, 2026

---

## Migration Approach

Given the size (4,300+ lines) and complexity, we'll:

1. **Create handler modules with proper implementations** (not stubs)
2. **Migrate implementations systematically** (extract from orchestrator)
3. **Update to artifact-centric patterns** (remove file-centric code)
4. **Refactor orchestrator to delegate** (thin routing layer)
5. **Remove all legacy aliases** (clean break)

---

## Handler Module Creation Order

### Phase 1: Critical Handlers (Journey 1) ✅
- [x] `artifact_management_handlers.py` ✅ COMPLETE
- [ ] `ingestion_handlers.py` - `ingest_file` (artifact-centric)
- [ ] `parsing_handlers.py` - `parse_content` (artifact-centric, pending intents)
- [ ] `embedding_handlers.py` - `create_deterministic_embeddings`, `extract_embeddings`
- [ ] `materialization_handlers.py` - `save_materialization` (lifecycle transition)

### Phase 2: Query Handlers
- [ ] `query_handlers.py` - `get_parsed_file`, `get_semantic_interpretation`, `list_files`

### Phase 3: Bulk Operations
- [ ] `bulk_handlers.py` - All bulk operations (artifact-centric vocabulary)

---

## Implementation Notes

### Key Patterns to Apply

1. **Artifact-Centric Terminology:**
   - `artifact_id` not `file_id`
   - `artifact_type` not implicit
   - `lifecycle_state` transitions
   - `parent_artifacts` for lineage

2. **State Surface Resolution:**
   - Use `resolve_artifact()` for resolution
   - Use Artifact Index for discovery
   - No direct storage queries

3. **Pending Intents:**
   - `ingestion_profile` in intent context
   - Retrieve from `intent_executions` table
   - Update intent status

4. **Materializations:**
   - Add materializations to artifact records
   - Store in `materializations` array
   - Retrieve from materializations

5. **Lifecycle States:**
   - `PENDING` → `READY` transitions
   - Use `update_artifact_lifecycle()`
   - Index in Artifact Index

---

## Migration Checklist

For each handler:
- [ ] Extract implementation from ContentOrchestrator
- [ ] Update to artifact-centric terminology
- [ ] Use State Surface for resolution
- [ ] Use Artifact Index for discovery
- [ ] Register artifacts properly
- [ ] Add materializations
- [ ] Update lifecycle states
- [ ] Handle pending intents (if applicable)
- [ ] Remove file-centric code
- [ ] Test implementation

---

## Next Steps

1. Create `ingestion_handlers.py` with artifact-centric `ingest_file`
2. Create `parsing_handlers.py` with artifact-centric `parse_content`
3. Create `embedding_handlers.py` with artifact-centric embedding intents
4. Create `materialization_handlers.py` with artifact-centric `save_materialization`
5. Create `query_handlers.py` with artifact-centric query intents
6. Refactor ContentOrchestrator to delegate to handlers
7. Remove all legacy aliases from service_factory.py
8. Remove legacy code from handlers

---

**Last Updated:** January 27, 2026  
**Owner:** Development Team
