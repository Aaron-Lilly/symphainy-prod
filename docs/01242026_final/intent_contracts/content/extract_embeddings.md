# Intent Contract: `extract_embeddings`

**Intent:** `extract_embeddings`  
**Realm:** `content`  
**Status:** ⏳ **IN PROGRESS**  
**Priority:** 🔴 **PRIORITY 1** - Used in Journey 1 (File Upload & Processing)

---

## 1. Intent Contract

### Required Inputs
- `artifact_id`: Parsed content artifact identifier - **Required** (artifact-centric)
- `parsed_file_reference`: Reference to parsed file data - **Required** (legacy compatibility)

### Optional Inputs
- `embedding_options`: Options for embedding extraction (Record<string, any>)

### Boundary Constraints
- **Artifact Must Exist:** Parsed content artifact must have been created via `parse_content` first
- **Artifact Must Be Accessible:** Artifact must be accessible via `artifact_id` and resolvable via State Surface
- **Artifact Lifecycle State:** Source artifact should be in `lifecycle_state: "PENDING"` or `"READY"`

### Forbidden Behaviors
- ❌ Direct API calls to `/api/v1/*/embeddings`
- ❌ Direct API calls to `/api/operations/*`
- ❌ Missing parameter validation
- ❌ Missing session validation
- ❌ Missing state updates
- ❌ Extracting embeddings from file that doesn't exist or isn't accessible

### Forbidden State Transitions
- ❌ `extract_embeddings` MUST NOT:
  - Modify source artifact content
  - Delete source artifact
  - Change artifact_id or parsed_file_reference
  - Transition artifact `lifecycle_state` from `PENDING` to `READY` (embeddings are Working Material until promoted via `save_materialization`)
  - Modify parent artifact's lifecycle state

### Guaranteed Outputs
- `artifact_id`: Identifier for embeddings artifact (artifact-centric)
  - **Artifact Type:** `artifact_type: "embeddings"`
  - **Parent Artifacts:** `parent_artifacts: [parsed_content_artifact_id]` (lineage)
- `embedding_reference`: Reference to embedding vectors - **Legacy compatibility**
- `lifecycle_state`: Artifact lifecycle state - **MUST be `"PENDING"`** (Working Material until materialized)
- `embeddings`: Embedding vectors (or reference)
- `metadata`: Embedding metadata
- `materializations`: Array with materialization entries:
  - Deterministic embeddings: `storage_type: "duckdb"`, `format: "parquet"`
  - Semantic embeddings: `storage_type: "arango"`, `format: "vector"`
- **Artifact Registry:** Embeddings artifact registered in State Surface (ArtifactRegistry) with:
  - `artifact_type: "embeddings"`
  - `parent_artifacts: [parsed_content_artifact_id]`
  - `lifecycle_state: "PENDING"`
  - `produced_by: { intent: "extract_embeddings", execution_id: ... }`
- **Artifact Index:** Embeddings artifact metadata indexed in Supabase `artifact_index` table with lineage
- Realm state update: `state.realm.content.embeddings[artifactId]` updated with embeddings
- Execution tracked: `state.execution[executionId]` updated

**Legacy Compatibility:** `embeddings_id` is an alias for `artifact_id` for backward compatibility, but contracts should use `artifact_id` going forward.

---

## 2. Runtime Enforcement

### ESLint Rule (if applicable)
- **Rule:** `no-direct-api-calls`
- **Pattern:** `fetch\('/api/v1.*embeddings|fetch\('/api/operations.*embeddings`
- **Message:** `Use submitIntent('extract_embeddings', ...) instead of direct API calls`
- **Status:** ⏳ Not implemented

### Runtime Check
- **Check:** Runtime validates intent parameters before execution
- **Action if violated:** Runtime rejects intent with error message
- **Status:** ✅ Implemented (Runtime validates parameters)

### Proof Tests
- **Test 1:** `test_extract_embeddings_direct_api_call_fails`
  - **Action:** Try to call `/api/v1/content/extract-embeddings` directly
  - **Expected:** Request fails or is rejected
  - **Status:** ⏳ Not implemented

- **Test 2:** `test_extract_embeddings_invalid_parsed_file_reference`
  - **Action:** Submit `extract_embeddings` with invalid `parsed_file_reference`
  - **Expected:** Intent rejected with clear error message
  - **Status:** ⏳ Not implemented

---

## 3. Journey Evidence

### Journeys Using This Intent
- Journey 1: File Upload & Processing - Step 3 (Extract Embeddings)

### Positive Evidence
- **Journey:** File Upload & Processing
- **Step:** After parsing, extract embeddings → `extract_embeddings` intent → Embeddings artifact created
- **Verification:** 
  - Embeddings extracted successfully
  - `artifact_id` returned (artifact_type: "embeddings")
  - `embedding_reference` returned
  - Artifact registered in State Surface with `parent_artifacts: [parsed_content_artifact_id]`
  - Artifact indexed in Supabase `artifact_index` with lineage metadata
  - Materializations created (DuckDB for deterministic, ArangoDB for semantic)
  - `lifecycle_state: "PENDING"` (Working Material)
  - State updated: `state.realm.content.embeddings[artifactId]` contains embeddings
- **Status:** ✅ Verified (Phase 4 implementation)

### Negative Evidence
- **Journey:** File Upload & Processing
- **Misuse Attempt:** Submit `extract_embeddings` without `parsed_file_id` or `parsed_file_reference`
- **Expected Behavior:** Intent rejects execution with clear error message
- **Verification:** Parameter validation throws error (ContentAPIManager line 432-437)
  - `if (!parsedFileId) throw new Error("parsed_file_id is required for extract_embeddings")`
  - `if (!parsedFileReference) throw new Error("parsed_file_reference is required for extract_embeddings")`
- **Status:** ✅ Verified

---

## 4. Idempotency & Re-entrancy

### Idempotency Key
- **Primary Key:** `embedding_fingerprint`
- **Derived From:** `hash(parsed_file_id + parsed_file_reference + embedding_options)`
- **Scope:** `per session, per parsed file, per embedding configuration`

### Required Behavior
- Repeated execution with same `embedding_fingerprint` must:
  - [ ] Return same `embeddings_id` (deterministic for identical embedding_fingerprint)
  - [ ] Return same `embedding_reference`
  - [ ] Never duplicate embedding extraction work (same embeddings_id reused if embedding_fingerprint already exists)
  - [ ] Not corrupt state (no duplicate entries in state.realm.content.embeddings)

### Canonical Artifact Identity
- **embeddings_id is deterministic** for identical `embedding_fingerprint` within same session
- **embeddings_id is reused** if `embedding_fingerprint` already exists in session
- This enables:
  - Safe retries (same embeddings_id returned)
  - Safe resumes (same embeddings_id returned)
  - Safe concurrency (same embeddings_id returned for same embedding configuration)

### Proof Test
- **Test:** Execute `extract_embeddings` twice with same `embedding_fingerprint` (same parsed_file_id, same embedding_options)
- **Expected:** 
  - Same `embeddings_id` returned both times
  - No duplicate embedding extraction work
  - No duplicate state entries
  - Second execution returns existing embeddings_id (memoized)
- **Status:** ⏳ Not implemented

**Gate:** Intent cannot be COMPLETE without passing idempotency proof test.

---

## 5. Observability

### Correlation & Tracing
- [x] execution_id present in all logs
- [x] execution_id propagated across intent boundaries
- [x] Errors include intent + execution_id
- [x] Journey trace reconstructable from logs

### Structured Logging
- [x] Intent start logged with execution_id
- [x] Intent completion logged with execution_id
- [x] Intent failure logged with execution_id + error details
- [x] State transitions logged with execution_id

**Gate:** Intent cannot be COMPLETE without observability guarantees.

---

## 6. Violations Found

### Direct API Calls
- [x] ✅ **FIXED** - No direct API calls found (uses `submitIntent`)

### Missing Validation
- [x] ✅ **FIXED** - Session validation exists (ContentAPIManager line 420)
- [x] ✅ **FIXED** - Parameter validation for `parsed_file_id` and `parsed_file_reference` (ContentAPIManager line 424-430)
  - **Location:** ContentAPIManager.extractEmbeddings() - validation added
  - **Status:** ✅ **COMPLETE** - Validation implemented before submitIntent

### Missing State Updates
- [x] ✅ **FIXED** - State updates exist (via Runtime execution tracking)

### Other Violations
- [ ] ⚠️ **POTENTIAL ISSUE** - Embedding options may not be fully validated
  - **Location:** ContentAPIManager line 425-428
  - **Note:** Embedding options are passed through without validation

---

## 7. Fixes Applied

### API Migration
- [x] ✅ Migrated to `ContentAPIManager.extractEmbeddings()` using `submitIntent('extract_embeddings', ...)`
- [x] ✅ Removed direct API call (if any existed)

### Validation Added
- [x] ✅ Session validation: `validateSession(platformState, "extract embeddings")`
- [ ] ⏳ Parameter validation: `if (!parsedFileId || !parsedFileReference) throw new Error(...)` - **TODO**

### State Updates Added
- [x] ✅ Execution tracking: `platformState.trackExecution(executionId)`
- [x] ✅ Realm state update: `state.realm.content.embeddings[parsedFileId]` updated (via Runtime)

### Enforcement Implemented
- [ ] ⏳ ESLint rule: `no-direct-api-calls` (not yet implemented)
- [x] ✅ Runtime check: Runtime validates intent parameters
- [ ] ⏳ Proof test 1: `test_extract_embeddings_direct_api_call_fails` (not yet implemented)
- [ ] ⏳ Proof test 2: `test_extract_embeddings_invalid_parsed_file_reference` (not yet implemented)

### Idempotency Implemented
- [ ] ⏳ Embedding fingerprint calculation: `hash(parsed_file_id + parsed_file_reference + embedding_options)` (not yet implemented)
- [ ] ⏳ Deterministic embeddings_id: Same embeddings_id for same embedding_fingerprint (not yet implemented)
- [ ] ⏳ Idempotency proof test: Execute twice with same embedding_fingerprint (not yet implemented)

### Observability Implemented
- [x] ✅ execution_id in all logs (via Runtime)
- [x] ✅ Trace continuity (via Runtime execution tracking)

---

## 8. Verification

### Contract Verification
- [x] Contract exists and is complete
- [x] Required inputs documented
- [x] Forbidden behaviors documented
- [x] Guaranteed outputs documented

### Enforcement Verification
- [ ] ESLint rule exists (if applicable) - ⏳ Not implemented
- [x] Runtime check exists - ✅ Implemented
- [ ] Proof tests exist - ⏳ Not implemented
- [ ] Intentional violation fails - ⏳ Not tested

### Journey Evidence Verification
- [x] At least one journey uses this intent (positive evidence) - ✅ Journey 1
- [x] Intent works in journey context - ✅ Verified
- [ ] At least one journey proves intent rejects misuse (negative evidence) - ⏳ Not verified
- [x] Journey evidence documented - ✅ This document

### Functional Verification
- [x] Intent works correctly - ✅ Verified in Phase 4
- [x] Observable artifacts created - ✅ artifact_id (embeddings), embedding_reference returned
- [x] Artifact registered in State Surface - ✅ ArtifactRegistry updated with parent_artifacts
- [x] Artifact indexed in Supabase - ✅ artifact_index table updated with lineage
- [x] Materializations created - ✅ DuckDB/ArangoDB storage, materializations array populated
- [x] Lifecycle state correct - ✅ lifecycle_state: "PENDING"
- [x] State updates correctly - ✅ state.realm.content.embeddings updated

### Idempotency Verification
- [ ] Idempotency key defined - ⏳ embedding_fingerprint (needs explicit definition)
- [ ] Deterministic embeddings_id - ⏳ Same embeddings_id for same embedding_fingerprint - **FIX REQUIRED**
- [ ] Idempotency proof test passes - ⏳ Not implemented
- [ ] No duplicate side effects on retry - ⏳ Not tested

### Observability Verification
- [x] execution_id in all logs - ✅ Via Runtime
- [x] Trace continuity verified - ✅ Via Runtime execution tracking
- [x] Errors include correlation IDs - ✅ Via Runtime error handling

---

## 9. Gate Status

**Intent is "done" only when:**
- [x] ✅ Contract exists
- [x] ✅ Enforcement implemented (Runtime check)
- [ ] ⏳ Proof tests pass (violation fails) - **BLOCKER**
- [x] ✅ Positive journey evidence exists
- [ ] ⏳ Negative journey evidence exists - **BLOCKER**
- [ ] ⏳ Idempotency proof test passes - **BLOCKER**
- [x] ✅ Observability guarantees met
- [x] ✅ Intent works correctly

**Current Status:** ⏳ **IN PROGRESS**

**Blockers:**
- **CRITICAL:** Idempotency key not implemented - Must use `embedding_fingerprint` (hash(parsed_file_id + parsed_file_reference + embedding_options))
- **CRITICAL:** Deterministic embeddings_id not implemented - Must return same embeddings_id for same embedding_fingerprint
- Parameter validation missing - Should validate parsed_file_id and parsed_file_reference before submitIntent
- Proof tests not implemented:
  - `test_extract_embeddings_direct_api_call_fails`
  - `test_extract_embeddings_invalid_parsed_file_reference`
  - `test_extract_embeddings_idempotency` (with embedding_fingerprint)
- Negative journey evidence not verified

**Next Steps:**
1. **Fix idempotency key:** Implement `embedding_fingerprint` calculation
2. **Fix deterministic embeddings_id:** Implement memoization - return same embeddings_id for same embedding_fingerprint
3. **Add parameter validation:** Validate parsed_file_id and parsed_file_reference before submitIntent
4. Implement all proof tests
5. Verify negative journey evidence
6. Verify ESLint rule (if applicable)

---

**Last Updated:** January 25, 2026  
**Owner:** Development Team
