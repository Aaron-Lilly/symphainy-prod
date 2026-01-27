# Intent Contract: `get_parsed_file`

**Intent:** `get_parsed_file`  
**Realm:** `content`  
**Status:** ⏳ **IN PROGRESS**  
**Priority:** 🔴 **PRIORITY 1** - Used in Journey 1 (File Upload & Processing)

---

## 1. Intent Contract

### Required Inputs
- `artifact_id`: Parsed content artifact identifier - **Required** (artifact-centric)
- `file_reference`: File reference string - **Required** (legacy compatibility)

**Note:** This intent uses **State Surface `resolve_artifact()`** as the single source of truth for artifact resolution. It does NOT query Supabase or GCS directly. The State Surface returns the artifact record with materializations, and content is retrieved from the materialization URIs.

### Optional Inputs
- None

### Boundary Constraints
- **File Must Exist:** File must have been ingested via `ingest_file` first
- **File Must Be Accessible:** File must be accessible via `file_reference` within session/tenant scope

### Forbidden Behaviors
- ❌ Direct API calls to `/api/v1/*/parsed-file`
- ❌ Direct API calls to `/api/operations/*`
- ❌ Missing parameter validation
- ❌ Missing session validation
- ❌ Accessing file outside tenant/session scope

### Forbidden State Transitions
- ❌ `get_parsed_file` MUST NOT:
  - Modify source artifact content
  - Delete source artifact
  - Change artifact_id or file_reference
  - Create new artifacts or parsed data (read-only query intent)
  - Query Supabase or GCS directly (must use State Surface `resolve_artifact()`)
  - Use fallback logic (State Surface is single source of truth)

### Guaranteed Outputs
- `parsed_file_id`: Identifier for parsed file (typically same as `file_id`)
- `parsed_content`: Parsed file data
- `structure`: File structure (if structured data)
- `chunks`: File chunks (if unstructured data)
- `preview`: Preview of parsed content
- Realm state update: `state.realm.content.parsedFiles[fileId]` updated with parsed file data (if not already present)
- Execution tracked: `state.execution[executionId]` updated

**Note:** This is a **read-only query intent** - it retrieves existing data without side effects.

---

## 2. Runtime Enforcement

### ESLint Rule (if applicable)
- **Rule:** `no-direct-api-calls`
- **Pattern:** `fetch\('/api/v1.*parsed-file|fetch\('/api/operations.*parsed-file`
- **Message:** `Use submitIntent('get_parsed_file', ...) instead of direct API calls`
- **Status:** ⏳ Not implemented

### Runtime Check
- **Check:** Runtime validates intent parameters before execution
- **Action if violated:** Runtime rejects intent with error message
- **Status:** ✅ Implemented (Runtime validates parameters)

### Proof Tests
- **Test 1:** `test_get_parsed_file_direct_api_call_fails`
  - **Action:** Try to call `/api/v1/content/parsed-file` directly
  - **Expected:** Request fails or is rejected
  - **Status:** ⏳ Not implemented

- **Test 2:** `test_get_parsed_file_invalid_file_reference`
  - **Action:** Submit `get_parsed_file` with invalid `file_reference`
  - **Expected:** Intent rejected with clear error message
  - **Status:** ⏳ Not implemented

- **Test 3:** `test_get_parsed_file_cross_tenant_access`
  - **Action:** Submit `get_parsed_file` with file_reference from different tenant
  - **Expected:** Intent rejected with authorization error
  - **Status:** ⏳ Not implemented

---

## 3. Journey Evidence

### Journeys Using This Intent
- Journey 1: File Upload & Processing - Used to retrieve parsed file data for display

### Positive Evidence
- **Journey:** File Upload & Processing
- **Step:** User views parsed file → `get_parsed_file` intent → Parsed content artifact resolved
- **Verification:** 
  - Artifact resolved via State Surface `resolve_artifact(artifact_id)`
  - `artifact_id` returned (artifact_type: "parsed_content")
  - `parsed_content` retrieved from artifact's materializations (GCS URI)
  - `lifecycle_state` returned
  - `materializations` array returned
  - State updated: `state.realm.content.parsedFiles[artifactId]` contains parsed file data
- **Status:** ✅ Verified (Phase 4 implementation)

### Negative Evidence
- **Journey:** File Upload & Processing
- **Misuse Attempt:** Submit `get_parsed_file` without `file_id` or `file_reference`
- **Expected Behavior:** Intent rejects execution with clear error message
- **Verification:** Parameter validation throws error (ContentAPIManager line 477-482)
  - `if (!fileId) throw new Error("file_id is required for get_parsed_file")`
  - `if (!fileReference) throw new Error("file_reference is required for get_parsed_file")`
- **Status:** ✅ Verified

---

## 4. Idempotency & Re-entrancy

### Idempotency Key
- **Primary Key:** `query_fingerprint`
- **Derived From:** `hash(file_id + file_reference + session_id)`
- **Scope:** `per session, per file`

### Required Behavior
- Repeated execution with same `query_fingerprint` must:
  - [ ] Return same result (same parsed_content, same structure, same chunks)
  - [ ] Not duplicate state entries (idempotent read operation)
  - [ ] Not corrupt state (read-only, no side effects)

### Canonical Artifact Identity
- **Result is deterministic** for identical `query_fingerprint` within same session
- **Result is cached** if `query_fingerprint` already exists in session
- This enables:
  - Safe retries (same result returned)
  - Safe resumes (same result returned)
  - Safe concurrency (same result returned for same query)

### Proof Test
- **Test:** Execute `get_parsed_file` twice with same `query_fingerprint` (same file_id, same file_reference, same session)
- **Expected:** 
  - Same `parsed_content` returned both times
  - Same `structure` returned both times
  - Same `chunks` returned both times
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
- [x] ✅ **FIXED** - Session validation exists (ContentAPIManager line 457 - now uses validateSession)
- [x] ✅ **FIXED** - Parameter validation for `file_id` and `file_reference` (ContentAPIManager line 461-467)
  - **Location:** ContentAPIManager.getParsedFile() - validation added
  - **Status:** ✅ **COMPLETE** - Validation implemented before submitIntent

### Missing State Updates
- [x] ✅ **FIXED** - State updates exist (via Runtime execution tracking)

### Other Violations
- [ ] ⚠️ **POTENTIAL ISSUE** - Polling mechanism (maxAttempts = 10, 500ms intervals) may timeout for large files
  - **Location:** ContentAPIManager line 475-495
  - **Note:** This is acceptable for MVP but may need WebSocket streaming for production

---

## 7. Fixes Applied

### API Migration
- [x] ✅ Migrated to `ContentAPIManager.getParsedFile()` using `submitIntent('get_parsed_file', ...)`
- [x] ✅ Removed direct API call (if any existed)

### Validation Added
- [x] ✅ Session validation: Manual check (ContentAPIManager line 456-458)
- [ ] ⏳ Parameter validation: `if (!fileId || !fileReference) throw new Error(...)` - **TODO**

### State Updates Added
- [x] ✅ Execution tracking: `platformState.trackExecution(executionId)`
- [x] ✅ Realm state update: `state.realm.content.parsedFiles[fileId]` updated (via Runtime)

### Enforcement Implemented
- [ ] ⏳ ESLint rule: `no-direct-api-calls` (not yet implemented)
- [x] ✅ Runtime check: Runtime validates intent parameters
- [ ] ⏳ Proof test 1: `test_get_parsed_file_direct_api_call_fails` (not yet implemented)
- [ ] ⏳ Proof test 2: `test_get_parsed_file_invalid_file_reference` (not yet implemented)
- [ ] ⏳ Proof test 3: `test_get_parsed_file_cross_tenant_access` (not yet implemented)

### Idempotency Implemented
- [ ] ⏳ Query fingerprint calculation: `hash(file_id + file_reference + session_id)` (not yet implemented)
- [ ] ⏳ Result caching: Cache result for same query_fingerprint (not yet implemented)
- [ ] ⏳ Idempotency proof test: Execute twice with same query_fingerprint (not yet implemented)

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
- [x] State Surface resolution - ✅ Uses `resolve_artifact()` from ArtifactRegistry
- [x] Materialization retrieval - ✅ Content retrieved from artifact's materializations array
- [x] Observable artifacts created - ✅ artifact_id, parsed_content returned
- [x] No fallback logic - ✅ Single source of truth (State Surface)
- [x] State updates correctly - ✅ state.realm.content.parsedFiles updated

### Idempotency Verification
- [ ] Idempotency key defined - ⏳ query_fingerprint (needs explicit definition)
- [ ] Deterministic result - ⏳ Same result for same query_fingerprint - **FIX REQUIRED**
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
- [ ] ⏳ Negative journey evidence exists - **BLOCKER**
- [ ] ⏳ Idempotency proof test passes - **BLOCKER**
- [x] ✅ Observability guarantees met
- [x] ✅ Intent works correctly

**Current Status:** ⏳ **IN PROGRESS**

**Blockers:**
- **CRITICAL:** Idempotency key not implemented - Must use `query_fingerprint` (hash(file_id + file_reference + session_id))
- **CRITICAL:** Result caching not implemented - Must return same result for same query_fingerprint
- Parameter validation missing - Should validate file_id and file_reference before submitIntent
- Proof tests not implemented:
  - `test_get_parsed_file_direct_api_call_fails`
  - `test_get_parsed_file_invalid_file_reference`
  - `test_get_parsed_file_cross_tenant_access`
  - `test_get_parsed_file_idempotency` (with query_fingerprint)
- Negative journey evidence not verified

**Next Steps:**
1. **Fix idempotency key:** Implement `query_fingerprint` calculation
2. **Fix result caching:** Implement memoization - return same result for same query_fingerprint
3. **Add parameter validation:** Validate file_id and file_reference before submitIntent
4. Implement all proof tests
5. Verify negative journey evidence
6. Verify ESLint rule (if applicable)

---

**Last Updated:** January 25, 2026  
**Owner:** Development Team
