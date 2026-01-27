# Intent Contract: `create_deterministic_embeddings`

**Intent:** `create_deterministic_embeddings`  
**Realm:** `content`  
**Status:** ⏳ **IN PROGRESS**  
**Priority:** 🔴 **PRIORITY 1** - Required before `extract_embeddings` in Journey 1 (File Upload & Processing)

---

## 1. Intent Contract

### Required Inputs
- `artifact_id`: Parsed content artifact identifier - **Required** (artifact-centric)
- `parsed_file_id`: Parsed file identifier - **Required** (legacy compatibility)

**Note:** `parsed_file_id` is an alias for `artifact_id` for backward compatibility. The intent accepts either parameter, but `artifact_id` is preferred.

### Optional Inputs
- `embedding_options`: Options for deterministic embedding creation (Record<string, any>)

### Boundary Constraints
- **Artifact Must Exist:** Parsed content artifact must have been created via `parse_content` first
- **Artifact Must Be Accessible:** Artifact must be accessible via `artifact_id` and resolvable via State Surface
- **Artifact Lifecycle State:** Source artifact should be in `lifecycle_state: "PENDING"` or `"READY"`
- **Prerequisite:** This intent MUST be executed before `extract_embeddings` (semantic embeddings require deterministic embeddings)

### Forbidden Behaviors
- ❌ Direct API calls to `/api/v1/*/deterministic-embeddings`
- ❌ Direct API calls to `/api/operations/*`
- ❌ Missing parameter validation
- ❌ Missing session validation
- ❌ Missing state updates
- ❌ Creating deterministic embeddings from artifact that doesn't exist or isn't accessible
- ❌ Executing `extract_embeddings` before `create_deterministic_embeddings`

### Forbidden State Transitions
- ❌ `create_deterministic_embeddings` MUST NOT:
  - Modify source artifact content
  - Delete source artifact
  - Change artifact_id or parsed_file_id
  - Transition artifact `lifecycle_state` from `PENDING` to `READY` (deterministic embeddings are Working Material until promoted via `save_materialization`)
  - Modify parent artifact's lifecycle state

### Guaranteed Outputs
- `artifact_id`: Identifier for deterministic embeddings artifact (artifact-centric)
  - **Artifact Type:** `artifact_type: "deterministic_embeddings"`
  - **Parent Artifacts:** `parent_artifacts: [parsed_content_artifact_id]` (lineage)
- `deterministic_embedding_id`: Identifier for deterministic embeddings - **Legacy compatibility**
- `lifecycle_state`: Artifact lifecycle state - **MUST be `"PENDING"`** (Working Material until materialized)
- `schema_fingerprint`: Schema fingerprint for deterministic matching
- `pattern_signature`: Pattern signature for deterministic matching
- `materializations`: Array with single materialization entry:
  - Deterministic embeddings: `storage_type: "duckdb"`, `format: "parquet"`
- **Artifact Registry:** Deterministic embeddings artifact registered in State Surface (ArtifactRegistry) with:
  - `artifact_type: "deterministic_embeddings"`
  - `parent_artifacts: [parsed_content_artifact_id]`
  - `lifecycle_state: "PENDING"`
  - `produced_by: { intent: "create_deterministic_embeddings", execution_id: ... }`
- **Artifact Index:** Deterministic embeddings artifact metadata indexed in Supabase `artifact_index` table with lineage
- Realm state update: `state.realm.content.deterministicEmbeddings[artifactId]` updated with embeddings
- Execution tracked: `state.execution[executionId]` updated

**Legacy Compatibility:** `deterministic_embedding_id` is an alias for `artifact_id` for backward compatibility, but contracts should use `artifact_id` going forward.

---

## 2. Runtime Enforcement

### ESLint Rule (if applicable)
- **Rule:** `no-direct-api-calls`
- **Pattern:** `fetch\('/api/v1.*deterministic-embeddings|fetch\('/api/operations.*deterministic-embeddings`
- **Message:** `Use submitIntent('create_deterministic_embeddings', ...) instead of direct API calls`
- **Status:** ⏳ Not implemented

### Runtime Check
- **Check:** Runtime validates intent parameters before execution
- **Action if violated:** Runtime rejects intent with error message
- **Status:** ✅ Implemented (Runtime validates parameters)

### Proof Tests
- **Test 1:** `test_create_deterministic_embeddings_direct_api_call_fails`
  - **Action:** Try to call `/api/v1/content/create-deterministic-embeddings` directly
  - **Expected:** Request fails or is rejected
  - **Status:** ⏳ Not implemented

- **Test 2:** `test_create_deterministic_embeddings_invalid_artifact_id`
  - **Action:** Submit `create_deterministic_embeddings` with invalid `artifact_id`
  - **Expected:** Intent rejected with clear error message
  - **Status:** ⏳ Not implemented

- **Test 3:** `test_create_deterministic_embeddings_prerequisite`
  - **Action:** Try to execute `extract_embeddings` before `create_deterministic_embeddings`
  - **Expected:** `extract_embeddings` rejects with error indicating deterministic embeddings required
  - **Status:** ⏳ Not implemented

---

## 3. Journey Evidence

### Journeys Using This Intent
- Journey 1: File Upload & Processing - Step 3a (Create Deterministic Embeddings) - **REQUIRED before Step 3 (Extract Embeddings)**

### Positive Evidence
- **Journey:** File Upload & Processing
- **Step:** After parsing, create deterministic embeddings → `create_deterministic_embeddings` intent → Deterministic embeddings artifact created
- **Verification:** 
  - Deterministic embeddings created successfully
  - `artifact_id` returned (artifact_type: "deterministic_embeddings")
  - `deterministic_embedding_id` returned
  - `schema_fingerprint` and `pattern_signature` returned
  - Artifact registered in State Surface with `parent_artifacts: [parsed_content_artifact_id]`
  - Artifact indexed in Supabase `artifact_index` with lineage metadata
  - Materialization created in DuckDB (parquet format)
  - `lifecycle_state: "PENDING"` (Working Material)
  - State updated: `state.realm.content.deterministicEmbeddings[artifactId]` contains embeddings
- **Status:** ✅ Verified (Phase 4 implementation)

### Negative Evidence
- **Journey:** File Upload & Processing
- **Misuse Attempt:** Submit `create_deterministic_embeddings` without `artifact_id` or `parsed_file_id`
- **Expected Behavior:** Intent rejects execution with clear error message
- **Verification:** Parameter validation throws error: "parsed_file_id is required for create_deterministic_embeddings intent"
- **Status:** ✅ Verified

---

## 4. Idempotency & Re-entrancy

### Idempotency Key
- **Primary Key:** `deterministic_embedding_fingerprint`
- **Derived From:** `hash(artifact_id + embedding_options)`
- **Scope:** `per session, per parsed content artifact, per embedding configuration`

### Required Behavior
- Repeated execution with same `deterministic_embedding_fingerprint` must:
  - [ ] Return same `artifact_id` (deterministic for identical fingerprint)
  - [ ] Return same `deterministic_embedding_id`
  - [ ] Never duplicate deterministic embedding creation work (same artifact_id reused if fingerprint already exists)
  - [ ] Not corrupt state (no duplicate entries in state.realm.content.deterministicEmbeddings)

### Canonical Artifact Identity
- **artifact_id is deterministic** for identical `deterministic_embedding_fingerprint` within same session
- **artifact_id is reused** if `deterministic_embedding_fingerprint` already exists in session
- This enables:
  - Safe retries (same artifact_id returned)
  - Safe resumes (same artifact_id returned)
  - Safe concurrency (same artifact_id returned for same embedding configuration)

### Proof Test
- **Test:** Execute `create_deterministic_embeddings` twice with same `deterministic_embedding_fingerprint` (same artifact_id, same embedding_options)
- **Expected:** 
  - Same `artifact_id` returned both times
  - No duplicate deterministic embedding creation work
  - No duplicate state entries
  - Second execution returns existing artifact_id (memoized)
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
- [x] ✅ **FIXED** - Parameter validation exists (ContentOrchestrator line 3180-3181)
- [x] ✅ **FIXED** - Session validation exists (via Runtime)

### Missing State Updates
- [x] ✅ **FIXED** - State updates exist (via Runtime execution tracking)

### Other Violations
- [ ] ⚠️ **POTENTIAL ISSUE** - Embedding options may not be fully validated
  - **Location:** ContentOrchestrator line 3191-3195
  - **Note:** Embedding options are passed through without validation

---

## 7. Fixes Applied

### API Migration
- [x] ✅ Migrated to `ContentAPIManager.createDeterministicEmbeddings()` using `submitIntent('create_deterministic_embeddings', ...)`
- [x] ✅ Removed direct API call (if any existed)

### Validation Added
- [x] ✅ Parameter validation: `if (!parsedFileId) throw new Error("parsed_file_id is required for create_deterministic_embeddings")`
- [x] ✅ Session validation: `validateSession(platformState, "create deterministic embeddings")`

### State Updates Added
- [x] ✅ Execution tracking: `platformState.trackExecution(executionId)`
- [x] ✅ Realm state update: `state.realm.content.deterministicEmbeddings[artifactId]` updated (via Runtime)

### Enforcement Implemented
- [ ] ⏳ ESLint rule: `no-direct-api-calls` (not yet implemented)
- [x] ✅ Runtime check: Runtime validates intent parameters
- [ ] ⏳ Proof test 1: `test_create_deterministic_embeddings_direct_api_call_fails` (not yet implemented)
- [ ] ⏳ Proof test 2: `test_create_deterministic_embeddings_invalid_artifact_id` (not yet implemented)
- [ ] ⏳ Proof test 3: `test_create_deterministic_embeddings_prerequisite` (not yet implemented)

### Idempotency Implemented
- [ ] ⏳ Deterministic embedding fingerprint calculation: `hash(artifact_id + embedding_options)` (not yet implemented)
- [ ] ⏳ Deterministic artifact_id: Same artifact_id for same deterministic_embedding_fingerprint (not yet implemented)
- [ ] ⏳ Idempotency proof test: Execute twice with same deterministic_embedding_fingerprint (not yet implemented)

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
- [x] At least one journey proves intent rejects misuse (negative evidence) - ✅ Verified
- [x] Journey evidence documented - ✅ This document

### Functional Verification
- [x] Intent works correctly - ✅ Verified in Phase 4
- [x] Observable artifacts created - ✅ artifact_id (deterministic_embeddings), deterministic_embedding_id returned
- [x] Artifact registered in State Surface - ✅ ArtifactRegistry updated with parent_artifacts
- [x] Artifact indexed in Supabase - ✅ artifact_index table updated with lineage
- [x] Materialization created - ✅ DuckDB storage, materializations array populated
- [x] Lifecycle state correct - ✅ lifecycle_state: "PENDING"
- [x] State updates correctly - ✅ state.realm.content.deterministicEmbeddings updated

### Idempotency Verification
- [ ] Idempotency key defined - ⏳ deterministic_embedding_fingerprint (needs explicit definition)
- [ ] Deterministic artifact_id - ⏳ Same artifact_id for same deterministic_embedding_fingerprint - **FIX REQUIRED**
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
- [x] ✅ Negative journey evidence exists
- [ ] ⏳ Idempotency proof test passes - **BLOCKER**
- [x] ✅ Observability guarantees met
- [x] ✅ Intent works correctly

**Current Status:** ⏳ **IN PROGRESS**

**Blockers:**
- **CRITICAL:** Idempotency key not implemented - Must use `deterministic_embedding_fingerprint` (hash(artifact_id + embedding_options))
- **CRITICAL:** Deterministic artifact_id not implemented - Must return same artifact_id for same deterministic_embedding_fingerprint
- Proof tests not implemented:
  - `test_create_deterministic_embeddings_direct_api_call_fails`
  - `test_create_deterministic_embeddings_invalid_artifact_id`
  - `test_create_deterministic_embeddings_prerequisite`
  - `test_create_deterministic_embeddings_idempotency` (with deterministic_embedding_fingerprint)

**Next Steps:**
1. **Fix idempotency key:** Implement `deterministic_embedding_fingerprint` calculation
2. **Fix deterministic artifact_id:** Implement memoization - return same artifact_id for same deterministic_embedding_fingerprint
3. Implement all proof tests
4. Verify ESLint rule (if applicable)
5. Update Journey 1 contract to include this as Step 3a

---

**Last Updated:** January 27, 2026  
**Owner:** Development Team
