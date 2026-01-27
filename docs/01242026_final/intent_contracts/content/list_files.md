# Intent Contract: `list_files`

**Intent:** `list_files`  
**Realm:** `content`  
**Status:** ⏳ **IN PROGRESS**  
**Priority:** 🔴 **PRIORITY 1** - Used in Journey 1 (File Upload & Processing)

---

## 1. Intent Contract

### Required Inputs
- `tenant_id`: Tenant identifier (from session) - **Required**
- `session_id`: Session identifier (from session) - **Required**

### Optional Inputs
- None

### Boundary Constraints
- **Tenant Scope:** Returns only artifacts for the current tenant
- **Workspace Scope:** Returns only materialized artifacts (`lifecycle_state: "READY"`), not working materials (`PENDING`)
- **Discovery vs Resolution:** This is a **discovery** operation (Artifact Index), not a **resolution** operation (State Surface)

### Forbidden Behaviors
- ❌ Direct API calls to `/api/v1/*/files`
- ❌ Direct API calls to `/api/operations/*`
- ❌ Missing parameter validation
- ❌ Missing session validation
- ❌ Accessing files outside tenant scope

### Forbidden State Transitions
- ❌ `list_files` MUST NOT:
  - Modify file content
  - Delete files
  - Create new files
  - Change file metadata (read-only query intent)

### Guaranteed Outputs
- `files`: Array of file metadata objects
  - Each file includes: `file_id`, `file_reference`, `boundary_contract_id`, `materialization_id`, `filename`, `mime_type`, etc.
- Realm state update: `state.realm.content.fileList` updated with file list
- Execution tracked: `state.execution[executionId]` updated

**Note:** This is a **read-only query intent** - it retrieves existing data without side effects. Returns only **materialized files** (Records of Fact), not working materials.

---

## 2. Runtime Enforcement

### ESLint Rule (if applicable)
- **Rule:** `no-direct-api-calls`
- **Pattern:** `fetch\('/api/v1.*files|fetch\('/api/operations.*files`
- **Message:** `Use submitIntent('list_files', ...) instead of direct API calls`
- **Status:** ⏳ Not implemented

### Runtime Check
- **Check:** Runtime validates intent parameters before execution
- **Action if violated:** Runtime rejects intent with error message
- **Status:** ✅ Implemented (Runtime validates parameters)

### Proof Tests
- **Test 1:** `test_list_files_direct_api_call_fails`
  - **Action:** Try to call `/api/v1/content/files` directly
  - **Expected:** Request fails or is rejected
  - **Status:** ⏳ Not implemented

- **Test 2:** `test_list_files_invalid_tenant_id`
  - **Action:** Submit `list_files` with invalid `tenant_id`
  - **Expected:** Intent rejected with clear error message
  - **Status:** ⏳ Not implemented

- **Test 3:** `test_list_files_cross_tenant_access`
  - **Action:** Submit `list_files` with tenant_id from different tenant
  - **Expected:** Intent rejected with authorization error (or returns empty list)
  - **Status:** ⏳ Not implemented

---

## 3. Journey Evidence

### Journeys Using This Intent
- Journey 1: File Upload & Processing - Used to display list of saved files

### Positive Evidence
- **Journey:** File Upload & Processing
- **Step:** User views file list → `list_files` intent → Artifact list returned
- **Verification:** 
  - Artifact list retrieved successfully via Artifact Index (Supabase `artifact_index` table)
  - `artifacts` array returned with artifact metadata
  - Only materialized artifacts returned (`lifecycle_state: "READY"`, not `PENDING`)
  - Filters applied correctly (`artifact_type: "file"`, `lifecycle_state: "READY"`)
  - Eligibility filtering works (if `eligible_for` specified)
  - State updated: `state.realm.content.fileList` contains artifact list
- **Status:** ✅ Verified (Phase 4 implementation)

### Negative Evidence
- **Journey:** File Upload & Processing
- **Misuse Attempt:** Submit `list_files` without `tenant_id` or `session_id`
- **Expected Behavior:** Intent rejects execution with clear error message
- **Verification:** Session validation throws error (ContentAPIManager line 288)
- **Status:** ✅ Verified

---

## 4. Idempotency & Re-entrancy

### Idempotency Key
- **Primary Key:** `list_query_fingerprint`
- **Derived From:** `hash(tenant_id + session_id)`
- **Scope:** `per session, per tenant`

### Required Behavior
- Repeated execution with same `list_query_fingerprint` must:
  - [ ] Return same result (same files array, same order)
  - [ ] Not duplicate state entries (idempotent read operation)
  - [ ] Not corrupt state (read-only, no side effects)

### Canonical Artifact Identity
- **Result is deterministic** for identical `list_query_fingerprint` within same session
- **Result is cached** if `list_query_fingerprint` already exists in session
- This enables:
  - Safe retries (same result returned)
  - Safe resumes (same result returned)
  - Safe concurrency (same result returned for same query)

### Proof Test
- **Test:** Execute `list_files` twice with same `list_query_fingerprint` (same tenant_id, same session_id)
- **Expected:** 
  - Same `files` array returned both times
  - Same file order
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
- [x] ✅ **FIXED** - Session validation exists (ContentAPIManager line 288)
- [x] ✅ **FIXED** - Tenant and session IDs extracted from platformState (line 294-295)

### Missing State Updates
- [x] ✅ **FIXED** - State updates exist (via Runtime execution tracking)

### Other Violations
- [ ] ⚠️ **POTENTIAL ISSUE** - Polling mechanism (maxAttempts = 10, 500ms intervals) may timeout for large file lists
  - **Location:** ContentAPIManager line 303-325
  - **Note:** This is acceptable for MVP but may need WebSocket streaming for production

---

## 7. Fixes Applied

### API Migration
- [x] ✅ Migrated to `ContentAPIManager.listFiles()` using `submitIntent('list_files', ...)`
- [x] ✅ Removed direct API call (if any existed)

### Validation Added
- [x] ✅ Session validation: `validateSession(platformState, "list files")`
- [x] ✅ Tenant and session IDs extracted from platformState

### State Updates Added
- [x] ✅ Execution tracking: `platformState.trackExecution(executionId)`
- [x] ✅ Realm state update: `state.realm.content.fileList` updated (via Runtime)

### Enforcement Implemented
- [ ] ⏳ ESLint rule: `no-direct-api-calls` (not yet implemented)
- [x] ✅ Runtime check: Runtime validates intent parameters
- [ ] ⏳ Proof test 1: `test_list_files_direct_api_call_fails` (not yet implemented)
- [ ] ⏳ Proof test 2: `test_list_files_invalid_tenant_id` (not yet implemented)
- [ ] ⏳ Proof test 3: `test_list_files_cross_tenant_access` (not yet implemented)

### Idempotency Implemented
- [ ] ⏳ List query fingerprint calculation: `hash(tenant_id + session_id)` (not yet implemented)
- [ ] ⏳ Result caching: Cache result for same list_query_fingerprint (not yet implemented)
- [ ] ⏳ Idempotency proof test: Execute twice with same list_query_fingerprint (not yet implemented)

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
- [x] Artifact Index query - ✅ Uses Supabase `artifact_index` table for discovery
- [x] Lifecycle state filtering - ✅ Only returns `lifecycle_state: "READY"` artifacts
- [x] Eligibility filtering - ✅ Supports `eligible_for` parameter for UI dropdowns
- [x] Observable artifacts created - ✅ artifacts array returned with metadata
- [x] No State Surface resolution - ✅ This is discovery, not resolution
- [x] State updates correctly - ✅ state.realm.content.fileList updated

### Idempotency Verification
- [ ] Idempotency key defined - ⏳ list_query_fingerprint (needs explicit definition)
- [ ] Deterministic result - ⏳ Same result for same list_query_fingerprint - **FIX REQUIRED**
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
- **CRITICAL:** Idempotency key not implemented - Must use `list_query_fingerprint` (hash(tenant_id + session_id))
- **CRITICAL:** Result caching not implemented - Must return same result for same list_query_fingerprint
- Proof tests not implemented:
  - `test_list_files_direct_api_call_fails`
  - `test_list_files_invalid_tenant_id`
  - `test_list_files_cross_tenant_access`
  - `test_list_files_idempotency` (with list_query_fingerprint)

**Next Steps:**
1. **Fix idempotency key:** Implement `list_query_fingerprint` calculation
2. **Fix result caching:** Implement memoization - return same result for same list_query_fingerprint
3. Implement all proof tests
4. Verify ESLint rule (if applicable)

---

**Last Updated:** January 25, 2026  
**Owner:** Development Team
