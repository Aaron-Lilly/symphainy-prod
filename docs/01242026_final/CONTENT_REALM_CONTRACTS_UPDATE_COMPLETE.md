# Content Realm Contracts Update Complete

## Status: ✅ **PHASE 1 & PHASE 2 COMPLETE**

All 7 intent contracts and 1 journey contract have been updated to align with the artifact-centric architecture and updated architectural evolutions.

**Date:** January 27, 2026

---

## Summary of Updates

### Phase 1 Updates (Before Testing) - ✅ COMPLETE

#### 1. Artifact-Centric Terminology
- ✅ Updated all contracts to use `artifact_id` instead of `file_id`, `parsed_file_id`, `embeddings_id`
- ✅ Documented `artifact_type` for each intent (file, parsed_content, embeddings)
- ✅ Documented `parent_artifacts` for lineage tracking
- ✅ Added legacy compatibility notes for backward compatibility

#### 2. State Surface / Artifact Registry
- ✅ Documented use of State Surface `resolve_artifact()` for authoritative resolution
- ✅ Documented Artifact Registry (State Surface) for artifact lifecycle management
- ✅ Documented Artifact Index (Supabase) for discovery/listing operations
- ✅ Clarified distinction between resolution (State Surface) and discovery (Artifact Index)

#### 3. Lifecycle States
- ✅ Documented artifact lifecycle states (`PENDING`, `READY`, `FAILED`, `ARCHIVED`, `DELETED`)
- ✅ Documented lifecycle state transitions for each intent
- ✅ Documented that `ingest_file` creates artifacts with `lifecycle_state: "PENDING"`
- ✅ Documented that `save_materialization` transitions `PENDING` → `READY`

#### 4. Materializations
- ✅ Documented `materializations` array pattern for all artifact-creating intents
- ✅ Documented materialization structure: `materialization_id`, `storage_type`, `uri`, `format`
- ✅ Documented storage types: GCS (files, parsed JSON), DuckDB (deterministic embeddings), ArangoDB (semantic embeddings)

#### 5. Ingestion Profile Location
- ✅ Documented that `ingestion_profile` lives in intent context (`intent_executions` table), NOT on artifacts
- ✅ Documented pending intent creation and resumable workflows
- ✅ Documented that `parse_content` retrieves `ingestion_profile` from pending intent context

### Phase 2 Updates (During Testing) - ✅ COMPLETE

#### 6. Intent-Based API Migration
- ✅ Updated `save_materialization` contract to reflect intent-based API usage
- ✅ Removed references to direct API calls
- ✅ Documented that all intents use `submitIntent()` via Runtime

#### 7. State Surface Resolution
- ✅ Updated `get_parsed_file` contract to use State Surface `resolve_artifact()` as single source of truth
- ✅ Removed fallback logic (State Surface → Supabase → GCS)
- ✅ Documented that content is retrieved from artifact's `materializations` array
- ✅ Updated `get_semantic_interpretation` contract similarly

#### 8. Artifact Index Discovery
- ✅ Updated `list_files` contract to use Artifact Index (Supabase `artifact_index` table)
- ✅ Documented discovery vs resolution distinction
- ✅ Documented filtering by `artifact_type`, `lifecycle_state`, `eligible_for`
- ✅ Documented that this is discovery (metadata only), not resolution (full content)

---

## Contract-by-Contract Summary

### 1. `ingest_file` Contract
**Updates:**
- ✅ Artifact terminology (`artifact_id`, `artifact_type: "file"`)
- ✅ Lifecycle state (`lifecycle_state: "PENDING"`)
- ✅ Materializations array (GCS storage)
- ✅ Artifact Registry registration
- ✅ Artifact Index indexing
- ✅ Ingestion profile location (NOT on artifact, in intent context)

### 2. `parse_content` Contract
**Updates:**
- ✅ Artifact terminology (`artifact_id`, `artifact_type: "parsed_content"`, `parent_artifacts`)
- ✅ Lifecycle state (`lifecycle_state: "PENDING"`)
- ✅ Materializations array (GCS JSON)
- ✅ Artifact Registry registration with lineage
- ✅ Artifact Index indexing with lineage metadata
- ✅ Pending intent context retrieval (`ingestion_profile` from `intent_executions`)

### 3. `extract_embeddings` Contract
**Updates:**
- ✅ Artifact terminology (`artifact_id`, `artifact_type: "embeddings"`, `parent_artifacts`)
- ✅ Lifecycle state (`lifecycle_state: "PENDING"`)
- ✅ Materializations array (DuckDB/ArangoDB)
- ✅ Artifact Registry registration with lineage
- ✅ Artifact Index indexing with lineage metadata

### 4. `save_materialization` Contract
**Updates:**
- ✅ Artifact terminology (`artifact_id`)
- ✅ Lifecycle state transition (`PENDING` → `READY`)
- ✅ Materializations array update
- ✅ Artifact Registry update (State Surface)
- ✅ Artifact Index update (Supabase)
- ✅ Intent-based API (migrated from direct API call)

### 5. `get_parsed_file` Contract
**Updates:**
- ✅ Artifact terminology (`artifact_id`)
- ✅ State Surface `resolve_artifact()` as single source of truth
- ✅ Materialization retrieval from artifact's `materializations` array
- ✅ Removed fallback logic (no Supabase/GCS direct queries)
- ✅ Lifecycle state in output

### 6. `get_semantic_interpretation` Contract
**Updates:**
- ✅ Artifact terminology (`artifact_id`)
- ✅ State Surface `resolve_artifact()` as single source of truth
- ✅ Related artifacts resolution via lineage
- ✅ Removed fallback logic
- ✅ Lifecycle state in output

### 7. `list_files` Contract
**Updates:**
- ✅ Artifact terminology (`artifacts` array instead of `files`)
- ✅ Artifact Index (Supabase `artifact_index` table) for discovery
- ✅ Filtering by `artifact_type`, `lifecycle_state`, `eligible_for`
- ✅ Discovery vs resolution distinction
- ✅ Returns metadata only (not full content)

### 8. Journey 1 Contract
**Updates:**
- ✅ Artifact-centric flow (artifact creation, lineage, lifecycle states)
- ✅ Pending intent creation with `ingestion_profile`
- ✅ Artifact Registry and Artifact Index operations
- ✅ Lifecycle state transitions throughout journey
- ✅ Materializations at each step
- ✅ State Surface resolution for retrieval operations

---

## Key Architectural Alignments

### ✅ Artifact-Centric Architecture
- All contracts now use artifact terminology
- Artifact lineage documented (`parent_artifacts`)
- Artifact types documented (`artifact_type`)
- Artifact lifecycle states documented

### ✅ State Surface / Artifact Registry
- State Surface is authoritative for artifact resolution
- Artifact Registry tracks artifact lifecycle states
- Artifact Index (Supabase) is for discovery/listing
- Clear distinction between resolution and discovery

### ✅ Intent Execution Log
- `ingestion_profile` lives in intent context (`intent_executions` table)
- Pending intents enable resumable workflows
- Intent context retrieved during execution

### ✅ Materializations Pattern
- All artifacts have `materializations` array
- Materializations specify storage location and format
- Content retrieved from materializations, not direct storage queries

### ✅ Lifecycle States
- Artifacts start in `PENDING` state (Working Material)
- `save_materialization` transitions to `READY` (Records of Fact)
- Lifecycle states tracked in Artifact Registry

---

## Remaining Work (Not in Phase 1/2)

### Phase 3 (After Core Testing)
- Document pending intents and resumable workflows in more detail
- Document eligibility-based filtering patterns
- Document artifact lineage visualization

### Implementation Verification
- Verify implementation matches updated contracts
- Update implementation code to match contract terminology
- Add State Surface `resolve_artifact()` calls where needed
- Add Artifact Index queries where needed

---

## Next Steps

1. ✅ **COMPLETE** - Phase 1 & Phase 2 contract updates
2. **NEXT** - Review updated contracts for consistency
3. **NEXT** - Verify implementation aligns with updated contracts
4. **NEXT** - Update implementation code to match contracts
5. **NEXT** - Run intent and journey contract tests

---

## Files Updated

1. `/docs/01242026_final/intent_contracts/content/ingest_file.md`
2. `/docs/01242026_final/intent_contracts/content/parse_content.md`
3. `/docs/01242026_final/intent_contracts/content/extract_embeddings.md`
4. `/docs/01242026_final/intent_contracts/content/save_materialization.md`
5. `/docs/01242026_final/intent_contracts/content/get_parsed_file.md`
6. `/docs/01242026_final/intent_contracts/content/get_semantic_interpretation.md`
7. `/docs/01242026_final/intent_contracts/content/list_files.md`
8. `/docs/01242026_final/journey_contracts/journey_1_file_upload_processing.md`

---

**Last Updated:** January 27, 2026  
**Owner:** Development Team
