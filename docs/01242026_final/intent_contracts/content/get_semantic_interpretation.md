# Intent Contract: `get_semantic_interpretation`

**Intent:** `get_semantic_interpretation`  
**Realm:** `content`  
**Status:** ⏳ **IN PROGRESS**  
**Priority:** 🔴 **PRIORITY 1** - Used in Journey 1 (File Upload & Processing)

---

## 1. Intent Contract

### Required Inputs
- `artifact_id`: File or parsed content artifact identifier - **Required** (artifact-centric)
- `file_reference`: File reference string - **Required** (legacy compatibility)

**Note:** This intent uses **State Surface `resolve_artifact()`** as the single source of truth for artifact resolution. It does NOT query Supabase or storage directly. The State Surface returns the artifact record with materializations and related artifacts.

### Optional Inputs
- None

### Boundary Constraints
- **Artifact Must Exist:** File or parsed content artifact must have been created via `ingest_file` or `parse_content` first
- **Artifact Must Be Accessible:** Artifact must be resolvable via State Surface `resolve_artifact(artifact_id)`
- **Artifact Lifecycle State:** Artifact should be in `lifecycle_state: "PENDING"` or `"READY"`
- **Single Source of Truth:** State Surface (ArtifactRegistry) is authoritative - no fallback to Supabase or storage

### Forbidden Behaviors
- ❌ Direct API calls to `/api/v1/*/semantic-interpretation`
- ❌ Direct API calls to `/api/operations/*`
- ❌ Missing parameter validation
- ❌ Missing session validation
- ❌ Accessing file outside tenant/session scope

### Forbidden State Transitions
- ❌ `get_semantic_interpretation` MUST NOT:
  - Modify source artifact content
  - Delete source artifact
  - Change artifact_id or file_reference
  - Create new artifacts or interpretations (read-only query intent)
  - Query Supabase or storage directly (must use State Surface `resolve_artifact()`)
  - Use fallback logic (State Surface is single source of truth)

### Guaranteed Outputs
- `interpretation`: Semantic interpretation data
- `entities`: Extracted entities
- `relationships`: Extracted relationships
- Realm state update: `state.realm.content.interpretations[fileId]` updated with interpretation (if not already present)
- Execution tracked: `state.execution[executionId]` updated

**Note:** This is a **read-only query intent** - it retrieves existing data without side effects.

---

## 2. Runtime Enforcement

### ESLint Rule (if applicable)
- **Rule:** `no-direct-api-calls`
- **Pattern:** `fetch\('/api/v1.*semantic-interpretation|fetch\('/api/operations.*semantic-interpretation`
- **Message:** `Use submitIntent('get_semantic_interpretation', ...) instead of direct API calls`
- **Status:** ⏳ Not implemented

### Runtime Check
- **Check:** Runtime validates intent parameters before execution
- **Action if violated:** Runtime rejects intent with error message
- **Status:** ✅ Implemented (Runtime validates parameters)

### Proof Tests
- **Test 1:** `test_get_semantic_interpretation_direct_api_call_fails`
  - **Action:** Try to call `/api/v1/content/semantic-interpretation` directly
  - **Expected:** Request fails or is rejected
  - **Status:** ⏳ Not implemented

- **Test 2:** `test_get_semantic_interpretation_invalid_file_reference`
  - **Action:** Submit `get_semantic_interpretation` with invalid `file_reference`
  - **Expected:** Intent rejected with clear error message
  - **Status:** ⏳ Not implemented

- **Test 3:** `test_get_semantic_interpretation_cross_tenant_access`
  - **Action:** Submit `get_semantic_interpretation` with file_reference from different tenant
  - **Expected:** Intent rejected with authorization error
  - **Status:** ⏳ Not implemented

---

## 3. Journey Evidence

### Journeys Using This Intent
- Journey 1: File Upload & Processing - Used to retrieve semantic interpretation for display

### Positive Evidence
- **Journey:** File Upload & Processing
- **Step:** User views semantic interpretation → `get_semantic_interpretation` intent → Interpretation data returned
- **Verification:** 
  - Artifact resolved via State Surface `resolve_artifact(artifact_id)`
  - Related artifacts resolved via artifact lineage (if needed)
  - Semantic interpretation retrieved successfully
  - `interpretation` returned
  - `entities` returned
  - `relationships` returned
  - `lifecycle_state` returned
  - State updated: `state.realm.content.interpretations[artifactId]` contains interpretation data
- **Status:** ✅ Verified (Phase 4 implementation)

### Negative Evidence
- **Journey:** File Upload & Processing
- **Misuse Attempt:** Submit `get_semantic_interpretation` without `file_id` or `file_reference`
- **Expected Behavior:** Intent rejects execution with clear error message
- **Verification:** Parameter validation throws error (ContentAPIManager line 523-528)
- **Status:** ✅ Verified

---

## 4. Idempotency & Re-entrancy

### Idempotency Key
- **Primary Key:** `interpretation_query_fingerprint`
- **Derived From:** `hash(file_id + file_reference + session_id)`
- **Scope:** `per session, per file`

### Required Behavior
- Repeated execution with same `interpretation_query_fingerprint` must:
  - [ ] Return same result (same interpretation, same entities, same relationships)
  - [ ] Not duplicate state entries (idempotent read operation)
  - [ ] Not corrupt state (read-only, no side effects)

### Canonical Artifact Identity
- **Result is deterministic** for identical `interpretation_query_fingerprint` within same session
- **Result is cached** if `interpretation_query_fingerprint` already exists in session
- This enables:
  - Safe retries (same result returned)
  - Safe resumes (same result returned)
  - Safe concurrency (same result returned for same query)

### Proof Test
- **Test:** Execute `get_semantic_interpretation` twice with same `interpretation_query_fingerprint` (same file_id, same file_reference, same session)
- **Expected:** 
  - Same `interpretation` returned both times
  - Same `entities` returned both times
  - Same `relationships` returned both times
  - No duplicate state entries
  - Second execution returns cached result (memoized)
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
- [x] ✅ **FIXED** - Session validation exists (ContentAPIManager line 520)
- [x] ✅ **FIXED** - Parameter validation exists (ContentAPIManager line 523-528)

### Missing State Updates
- [x] ✅ **FIXED** - State updates exist (via Runtime execution tracking)

### Other Violations
- [ ] ⚠️ **POTENTIAL ISSUE** - Polling mechanism (maxAttempts = 10, 500ms intervals) may timeout for large interpretations
  - **Location:** ContentAPIManager line 543-560
  - **Note:** This is acceptable for MVP but may need WebSocket streaming for production

---

## 7. Fixes Applied

### API Migration
- [x] ✅ Migrated to `ContentAPIManager.getSemanticInterpretation()` using `submitIntent('get_semantic_interpretation', ...)`
- [x] ✅ Removed direct API call (if any existed)

### Validation Added
- [x] ✅ Session validation: `validateSession(platformState, "get semantic interpretation")`
- [x] ✅ Parameter validation: `if (!fileId || !fileReference) throw new Error(...)`

### State Updates Added
- [x] ✅ Execution tracking: `platformState.trackExecution(executionId)`
- [x] ✅ Realm state update: `state.realm.content.interpretations[fileId]` updated (via Runtime)

### Enforcement Implemented
- [ ] ⏳ ESLint rule: `no-direct-api-calls` (not yet implemented)
- [x] ✅ Runtime check: Runtime validates intent parameters
- [ ] ⏳ Proof test 1: `test_get_semantic_interpretation_direct_api_call_fails` (not yet implemented)
- [ ] ⏳ Proof test 2: `test_get_semantic_interpretation_invalid_file_reference` (not yet implemented)
- [ ] ⏳ Proof test 3: `test_get_semantic_interpretation_cross_tenant_access` (not yet implemented)

### Idempotency Implemented
- [ ] ⏳ Interpretation query fingerprint calculation: `hash(file_id + file_reference + session_id)` (not yet implemented)
- [ ] ⏳ Result caching: Cache result for same interpretation_query_fingerprint (not yet implemented)
- [ ] ⏳ Idempotency proof test: Execute twice with same interpretation_query_fingerprint (not yet implemented)

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
- [x] State Surface resolution - ✅ Uses `resolve_artifact()` from ArtifactRegistry
- [x] Related artifacts resolution - ✅ Resolves related artifacts via lineage if needed
- [x] Observable artifacts created - ✅ artifact_id, interpretation, entities, relationships returned
- [x] No fallback logic - ✅ Single source of truth (State Surface)
- [x] State updates correctly - ✅ state.realm.content.interpretations updated

### Idempotency Verification
- [ ] Idempotency key defined - ⏳ interpretation_query_fingerprint (needs explicit definition)
- [ ] Deterministic result - ⏳ Same result for same interpretation_query_fingerprint - **FIX REQUIRED**
- [ ] Idempotency proof test passes - ⏳ Not implemented
- [ ] No duplicate side effects on retry - ⏳ Not tested (read-only, should be safe)

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
- **CRITICAL:** Idempotency key not implemented - Must use `interpretation_query_fingerprint` (hash(file_id + file_reference + session_id))
- **CRITICAL:** Result caching not implemented - Must return same result for same interpretation_query_fingerprint
- Proof tests not implemented:
  - `test_get_semantic_interpretation_direct_api_call_fails`
  - `test_get_semantic_interpretation_invalid_file_reference`
  - `test_get_semantic_interpretation_cross_tenant_access`
  - `test_get_semantic_interpretation_idempotency` (with interpretation_query_fingerprint)

**Next Steps:**
1. **Fix idempotency key:** Implement `interpretation_query_fingerprint` calculation
2. **Fix result caching:** Implement memoization - return same result for same interpretation_query_fingerprint
3. Implement all proof tests
4. Verify ESLint rule (if applicable)

---

**Last Updated:** January 25, 2026  
**Owner:** Development Team
