# Content Realm Contracts Architecture Audit

## Status: 🔍 **AUDIT IN PROGRESS**

Comprehensive audit of 7 intent contracts and 1 journey contract for Content Realm to ensure alignment with updated architectural evolutions.

**Date:** January 27, 2026  
**Architectural Evolution:** Artifact-centric architecture, Intent Execution Log, State Surface/Artifact Registry

---

## Executive Summary

### Key Architectural Evolutions to Verify

1. **Artifact-Centric Architecture**
   - Shift from file-centric to artifact-centric thinking
   - Artifacts have: `artifact_id`, `artifact_type`, `lifecycle_state`, `materializations`
   - Artifact Registry (State Surface) is authoritative for artifact resolution
   - Artifact Index (Supabase) is for discovery/listing

2. **Intent Execution Log (`intent_executions` table)**
   - Durable, resumable intent context
   - `ingestion_profile` lives with intent context, NOT on artifacts
   - Pending intents enable resumable workflows

3. **State Surface & Artifact Registry**
   - State Surface is authoritative for artifact resolution (`resolve_artifact`)
   - Artifact Registry tracks artifact lifecycle states
   - Artifact Index (Supabase) is for discovery (`list_artifacts`)

4. **Lifecycle States**
   - `PENDING`, `READY`, `FAILED`, `ARCHIVED`, `DELETED`
   - Artifacts transition through lifecycle states

5. **Materialization Pattern**
   - Artifacts have `materializations` array
   - Each materialization has: `materialization_id`, `storage_type`, `uri`, `format`

---

## Contract-by-Contract Audit

### 1. Intent Contract: `ingest_file`

#### ✅ Aligned
- Uses intent-based API (`submitIntent`)
- Two-phase pattern (Working Material → Records of Fact)
- Idempotency key defined (`content_fingerprint`)

#### ⚠️ Needs Alignment
- **Artifact Terminology**: Still uses `file_id` instead of `artifact_id`
  - **Impact**: Should reference `artifact_id` and `artifact_type: "file"`
  - **Fix**: Update contract to use artifact terminology
- **Lifecycle State**: No mention of artifact lifecycle states (`PENDING`, `READY`)
  - **Impact**: Should specify lifecycle state transitions
  - **Fix**: Document lifecycle state: `PENDING` → `READY` after successful ingestion
- **Materializations**: No mention of materializations array
  - **Impact**: Should document materialization creation
  - **Fix**: Document that `ingest_file` creates artifact with materialization in GCS
- **Artifact Registry**: No mention of State Surface/Artifact Registry
  - **Impact**: Should document artifact registration in Artifact Registry
  - **Fix**: Document that artifact is registered in State Surface after ingestion

#### ❌ Misaligned
- **Ingestion Profile**: Contract mentions `ingestion_type` but not `ingestion_profile`
  - **Impact**: `ingestion_profile` should live in intent context (intent_executions), not on artifact
  - **Fix**: Remove `ingestion_type` from artifact, document that `ingestion_profile` is stored in pending intent context

**Alignment Score:** 6/10

---

### 2. Intent Contract: `parse_content`

#### ✅ Aligned
- Uses intent-based API (`submitIntent`)
- Idempotency key defined (`parsing_fingerprint`)
- Boundary constraints documented

#### ⚠️ Needs Alignment
- **Artifact Terminology**: Still uses `parsed_file_id` instead of artifact-centric thinking
  - **Impact**: Should reference parent artifact and derived artifact
  - **Fix**: Document that `parse_content` creates new artifact (`artifact_type: "parsed_content"`) with `parent_artifacts: [file_artifact_id]`
- **Lifecycle State**: No mention of artifact lifecycle states
  - **Impact**: Should specify lifecycle state transitions
  - **Fix**: Document lifecycle state: `PENDING` → `READY` after successful parsing
- **Materializations**: No mention of materializations array
  - **Impact**: Should document materialization creation
  - **Fix**: Document that parsed content is stored as materialization (GCS JSON)
- **Artifact Registry**: No mention of State Surface/Artifact Registry
  - **Impact**: Should document artifact registration
  - **Fix**: Document that parsed artifact is registered in State Surface
- **Ingestion Profile**: No mention of ingestion_profile in intent context
  - **Impact**: `parse_content` should use `ingestion_profile` from pending intent context
  - **Fix**: Document that `parse_content` retrieves `ingestion_profile` from intent_executions table (via pending intent)

#### ❌ Misaligned
- **Pending Intent Context**: Contract doesn't mention retrieving context from intent_executions
  - **Impact**: `ingestion_profile` should come from intent context, not parameters
  - **Fix**: Document that `parse_content` should check for pending intent and use its context

**Alignment Score:** 5/10

---

### 3. Intent Contract: `extract_embeddings`

#### ✅ Aligned
- Uses intent-based API (`submitIntent`)
- Idempotency key defined (`embedding_fingerprint`)
- Boundary constraints documented

#### ⚠️ Needs Alignment
- **Artifact Terminology**: Still uses `embeddings_id` instead of artifact-centric thinking
  - **Impact**: Should reference parent artifact and derived artifact
  - **Fix**: Document that `extract_embeddings` creates new artifact (`artifact_type: "embeddings"`) with `parent_artifacts: [parsed_artifact_id]`
- **Lifecycle State**: No mention of artifact lifecycle states
  - **Impact**: Should specify lifecycle state transitions
  - **Fix**: Document lifecycle state: `PENDING` → `READY` after successful extraction
- **Materializations**: No mention of materializations array
  - **Impact**: Should document materialization creation
  - **Fix**: Document that embeddings are stored as materialization (ArangoDB/DuckDB)
- **Artifact Registry**: No mention of State Surface/Artifact Registry
  - **Impact**: Should document artifact registration
  - **Fix**: Document that embeddings artifact is registered in State Surface

**Alignment Score:** 5/10

---

### 4. Intent Contract: `save_materialization`

#### ✅ Aligned
- Two-phase pattern (Working Material → Records of Fact)
- Idempotency key defined (`materialization_fingerprint`)

#### ⚠️ Needs Alignment
- **Artifact Terminology**: Still uses `materialization_id` instead of artifact-centric thinking
  - **Impact**: Should reference artifact lifecycle state transition
  - **Fix**: Document that `save_materialization` transitions artifact lifecycle state: `PENDING` → `READY`
- **Lifecycle State**: No explicit mention of lifecycle state transition
  - **Impact**: Should document lifecycle state change
  - **Fix**: Document lifecycle state transition: `PENDING` → `READY`
- **Materializations**: No mention of materializations array update
  - **Impact**: Should document materialization persistence
  - **Fix**: Document that materialization is persisted and added to artifact's `materializations` array
- **Artifact Registry**: No mention of State Surface/Artifact Registry update
  - **Impact**: Should document artifact state update in Artifact Registry
  - **Fix**: Document that artifact lifecycle state is updated in State Surface

#### ❌ Misaligned
- **Direct API Call**: Still uses direct API call (not intent-based)
  - **Impact**: Violates intent-based architecture
  - **Fix**: Migrate to `submitIntent('save_materialization', ...)`

**Alignment Score:** 4/10

---

### 5. Intent Contract: `get_parsed_file`

#### ✅ Aligned
- Uses intent-based API (`submitIntent`)
- Read-only query intent
- Boundary constraints documented

#### ⚠️ Needs Alignment
- **Artifact Resolution**: Contract mentions `file_reference` but not artifact resolution
  - **Impact**: Should use State Surface `resolve_artifact()` for authoritative resolution
  - **Fix**: Document that `get_parsed_file` should use `resolve_artifact(artifact_id)` from State Surface
- **Artifact Terminology**: Still uses `parsed_file_id` instead of `artifact_id`
  - **Impact**: Should reference artifact-centric thinking
  - **Fix**: Update to use `artifact_id` and `artifact_type: "parsed_content"`
- **Materializations**: No mention of retrieving from materializations array
  - **Impact**: Should retrieve content from artifact's materializations
  - **Fix**: Document that parsed content is retrieved from artifact's `materializations` array

#### ❌ Misaligned
- **Three Sources of Truth**: Contract mentions fallback logic (State Surface → Supabase → GCS)
  - **Impact**: Violates single source of truth principle
  - **Fix**: Use State Surface `resolve_artifact()` as single source of truth, retrieve materialization URI from artifact record

**Alignment Score:** 4/10

---

### 6. Intent Contract: `get_semantic_interpretation`

#### ✅ Aligned
- Uses intent-based API (`submitIntent`)
- Read-only query intent
- Boundary constraints documented

#### ⚠️ Needs Alignment
- **Artifact Resolution**: No mention of artifact resolution
  - **Impact**: Should use State Surface `resolve_artifact()` for authoritative resolution
  - **Fix**: Document that `get_semantic_interpretation` should use `resolve_artifact(artifact_id)` from State Surface
- **Artifact Terminology**: Still uses `file_id` instead of `artifact_id`
  - **Impact**: Should reference artifact-centric thinking
  - **Fix**: Update to use `artifact_id` and `artifact_type: "file"` or `"parsed_content"`
- **Materializations**: No mention of retrieving from materializations array
  - **Impact**: Should retrieve interpretation from artifact's materializations or derived artifacts
  - **Fix**: Document that interpretation is retrieved from artifact's materializations or related artifacts

**Alignment Score:** 5/10

---

### 7. Intent Contract: `list_files`

#### ✅ Aligned
- Uses intent-based API (`submitIntent`)
- Read-only query intent
- Boundary constraints documented

#### ⚠️ Needs Alignment
- **Artifact Discovery**: Contract mentions `list_files` but should use `list_artifacts`
  - **Impact**: Should use Artifact Index (Supabase) for discovery via `list_artifacts()`
  - **Fix**: Document that `list_files` should use `list_artifacts()` API with filters: `artifact_type: "file"`, `lifecycle_state: "READY"`
- **Artifact Terminology**: Still uses `files` array instead of `artifacts` array
  - **Impact**: Should return artifacts, not files
  - **Fix**: Update to return `artifacts` array with artifact metadata
- **Lifecycle State**: No mention of filtering by lifecycle state
  - **Impact**: Should filter by `lifecycle_state: "READY"` (materialized files)
  - **Fix**: Document that only artifacts with `lifecycle_state: "READY"` are returned
- **Eligibility**: No mention of eligibility-based filtering
  - **Impact**: Should support `eligible_for` filtering for UI dropdowns
  - **Fix**: Document that `list_files` supports `eligible_for` parameter for filtering

#### ❌ Misaligned
- **Discovery vs Resolution**: Contract doesn't distinguish between discovery (Supabase) and resolution (State Surface)
  - **Impact**: Should clarify that `list_files` is for discovery, not resolution
  - **Fix**: Document that `list_files` uses Artifact Index (Supabase) for discovery, not State Surface for resolution

**Alignment Score:** 4/10

---

### 8. Journey Contract: Journey 1 (File Upload & Processing)

#### ✅ Aligned
- Intent ordering is correct
- Two-phase pattern (Working Material → Records of Fact) is explicit
- Optionality (`get_semantic_interpretation`) is handled correctly
- Failure, retry, and boundary cases are first-class

#### ⚠️ Needs Alignment
- **Artifact Terminology**: Journey uses `file_id`, `parsed_file_id`, `embeddings_id` instead of artifact-centric thinking
  - **Impact**: Should reference artifacts and artifact lineage
  - **Fix**: Update journey to use `artifact_id` and document artifact lineage: `file_artifact` → `parsed_content_artifact` → `embeddings_artifact`
- **Lifecycle States**: No mention of artifact lifecycle state transitions
  - **Impact**: Should document lifecycle state progression through journey
  - **Fix**: Document lifecycle state transitions: `PENDING` → `READY` at each step
- **Artifact Registry**: No mention of State Surface/Artifact Registry
  - **Impact**: Should document artifact registration and resolution
  - **Fix**: Document that each step registers artifacts in State Surface
- **Pending Intents**: No mention of pending intents or ingestion_profile
  - **Impact**: Should document that `ingestion_profile` is stored in pending intent context
  - **Fix**: Document that user selects `ingestion_profile` before upload, stored in pending intent, used by `parse_content`

#### ❌ Misaligned
- **Ingestion Profile Flow**: Journey doesn't mention where `ingestion_profile` lives
  - **Impact**: `ingestion_profile` should live in intent context (intent_executions), not on artifacts
  - **Fix**: Document that `ingestion_profile` is stored in pending intent context when user selects parsing type, retrieved by `parse_content`

**Alignment Score:** 6/10

---

## Critical Alignment Issues Summary

### 🔴 Critical (Must Fix Before Testing)

1. **Artifact Terminology**
   - All contracts use file-centric terminology (`file_id`, `parsed_file_id`, etc.)
   - **Fix**: Update to artifact-centric terminology (`artifact_id`, `artifact_type`, `parent_artifacts`)

2. **State Surface / Artifact Registry**
   - Contracts don't mention State Surface for artifact resolution
   - **Fix**: Document use of `resolve_artifact()` for authoritative resolution

3. **Artifact Index / Discovery**
   - `list_files` doesn't mention Artifact Index for discovery
   - **Fix**: Document use of `list_artifacts()` with Artifact Index (Supabase)

4. **Lifecycle States**
   - Contracts don't mention artifact lifecycle states
   - **Fix**: Document lifecycle state transitions (`PENDING` → `READY`)

5. **Materializations**
   - Contracts don't mention materializations array
   - **Fix**: Document materialization creation and retrieval

6. **Ingestion Profile Location**
   - Contracts don't clarify that `ingestion_profile` lives in intent context (intent_executions)
   - **Fix**: Document that `ingestion_profile` is stored in pending intent context, not on artifacts

### ⚠️ Important (Should Fix Soon)

7. **Pending Intents**
   - Contracts don't mention pending intents or resumable workflows
   - **Fix**: Document pending intent creation and resumption

8. **Direct API Call**
   - `save_materialization` still uses direct API call
   - **Fix**: Migrate to intent-based API

9. **Three Sources of Truth**
   - `get_parsed_file` mentions fallback logic (State Surface → Supabase → GCS)
   - **Fix**: Use State Surface `resolve_artifact()` as single source of truth

---

## Recommended Fix Priority

### Phase 1: Terminology & Core Concepts (Before Testing)
1. Update all contracts to use artifact-centric terminology
2. Document State Surface/Artifact Registry usage
3. Document lifecycle state transitions
4. Document materializations array
5. Document ingestion_profile location (intent context)

### Phase 2: Implementation Alignment (During Testing)
6. Migrate `save_materialization` to intent-based API
7. Update `get_parsed_file` to use State Surface `resolve_artifact()`
8. Update `list_files` to use `list_artifacts()` with Artifact Index

### Phase 3: Advanced Features (After Core Testing)
9. Document pending intents and resumable workflows
10. Document eligibility-based filtering

---

## Next Steps

1. **Update Contracts**: Apply Phase 1 fixes to all contracts
2. **Review Implementation**: Verify implementation matches updated contracts
3. **Test Alignment**: Run tests to verify contracts align with implementation
4. **Documentation**: Update journey contract with artifact-centric flow

---

**Last Updated:** January 27, 2026  
**Owner:** Development Team
