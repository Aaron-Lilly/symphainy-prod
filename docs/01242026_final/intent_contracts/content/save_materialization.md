# Intent Contract: `save_materialization`

**Intent:** `save_materialization`  
**Realm:** `content`  
**Status:** ⏳ **IN PROGRESS**  
**Priority:** 🔴 **PRIORITY 1** - Used in Journey 1 (File Upload & Processing)

---

## 1. Intent Contract

### Required Inputs
- `artifact_id`: File artifact identifier from `ingest_file` - **Required** (artifact-centric)
- `boundary_contract_id`: Boundary contract ID from `ingest_file` - **Required`

**Legacy Compatibility:** `file_id` is accepted as an alias for `artifact_id` for backward compatibility.

### Optional Inputs
- None

### Boundary Constraints
- **Artifact Must Exist:** File artifact must have been created via `ingest_file` first
- **Artifact Lifecycle State:** Artifact must have `lifecycle_state: "PENDING"` (Working Material)
- **User Must Approve:** This intent represents explicit user approval to persist artifact (Working Material → Records of Fact)

### Forbidden Behaviors
- ❌ Direct API calls to `/api/v1/*/materialization`
- ❌ Direct API calls to `/api/operations/*`
- ❌ Missing parameter validation
- ❌ Missing session validation
- ❌ Missing state updates
- ❌ Saving file that hasn't been ingested
- ❌ Saving file that's already materialized

### Forbidden State Transitions
- ❌ `save_materialization` MUST NOT:
  - Modify source file content
  - Change file_id or boundary_contract_id
  - Create duplicate materialization records

### Guaranteed Outputs
- `artifact_id`: Confirmed artifact ID (same as input)
- `boundary_contract_id`: Confirmed boundary contract ID (same as input)
- `lifecycle_state`: Artifact lifecycle state - **MUST be `"READY"`** (transitioned from `PENDING`)
- `materializations`: Materialization array updated with persistent storage information:
  - Existing materialization marked as persistent
  - Additional materialization entries may be added for Supabase metadata
- **Artifact Registry:** Artifact lifecycle state updated in State Surface (ArtifactRegistry):
  - `lifecycle_state: "PENDING"` → `"READY"`
  - Materializations array updated
- **Artifact Index:** Artifact metadata updated in Supabase `artifact_index` table:
  - `lifecycle_state: "READY"`
  - Materialization information persisted
- Realm state update: `state.realm.content.files[artifactId]` updated with `lifecycle_state: "READY"`
- **Data Class Transition:** Working Material → Records of Fact

**Legacy Compatibility:** `materialization_id` is returned for backward compatibility, but the primary identifier is `artifact_id`.

---

## 2. Runtime Enforcement

### ESLint Rule (if applicable)
- **Rule:** `no-direct-api-calls`
- **Pattern:** `fetch\('/api.*materialization|fetch\('/api/operations.*materialization`
- **Message:** `Use submitIntent('save_materialization', ...) instead of direct API calls`
- **Status:** ⏳ Not implemented

### Runtime Check
- **Check:** Runtime validates intent parameters before execution
- **Action if violated:** Runtime rejects intent with error message
- **Status:** ✅ **IMPLEMENTED** - Uses intent-based API (`submitIntent('save_materialization', ...)`)

### Proof Tests
- **Test 1:** `test_save_materialization_direct_api_call_fails`
  - **Action:** Try to call `/api/content/save_materialization` directly
  - **Expected:** Request fails or is rejected (after migration to intent-based)
  - **Status:** ⏳ Not implemented

- **Test 2:** `test_save_materialization_invalid_file_id`
  - **Action:** Submit `save_materialization` with invalid `file_id`
  - **Expected:** Intent rejected with clear error message
  - **Status:** ⏳ Not implemented

- **Test 3:** `test_save_materialization_already_materialized`
  - **Action:** Submit `save_materialization` for file that's already materialized
  - **Expected:** Intent rejected or idempotent (returns existing materialization_id)
  - **Status:** ⏳ Not implemented

---

## 3. Journey Evidence

### Journeys Using This Intent
- Journey 1: File Upload & Processing - Step 4 (Save Materialization)

### Positive Evidence
- **Journey:** File Upload & Processing
- **Step:** User clicks "Save" to persist artifact → `save_materialization` intent → Artifact persisted
- **Verification:** 
  - Artifact saved successfully
  - `artifact_id` returned
  - Artifact lifecycle state transitioned: `PENDING` → `READY`
  - Artifact Registry updated in State Surface
  - Artifact Index updated in Supabase `artifact_index` table
  - Materializations array updated with persistent storage info
  - State updated: `state.realm.content.files[artifactId].lifecycle_state = "READY"`
  - Data class transition: Working Material → Records of Fact
- **Status:** ✅ Verified (Phase 4 implementation, uses intent-based API)

### Negative Evidence
- **Journey:** File Upload & Processing
- **Misuse Attempt:** Submit `save_materialization` without `file_id` or `boundary_contract_id`
- **Expected Behavior:** Intent rejects execution with clear error message
- **Verification:** Parameter validation throws error (ContentAPIManager line 233-235)
- **Status:** ✅ Verified (but needs intent-based implementation)

---

## 4. Idempotency & Re-entrancy

### Idempotency Key
- **Primary Key:** `materialization_fingerprint`
- **Derived From:** `hash(file_id + boundary_contract_id + session_id)`
- **Scope:** `per session, per file, per boundary contract`

### Required Behavior
- Repeated execution with same `materialization_fingerprint` must:
  - [ ] Return same `materialization_id` (deterministic for identical materialization_fingerprint)
  - [ ] Never duplicate materialization records (same materialization_id reused if materialization_fingerprint already exists)
  - [ ] Not corrupt state (no duplicate entries in Supabase materialization table)
  - [ ] Not flip `materialization_pending` multiple times (idempotent state transition)

### Canonical Artifact Identity
- **materialization_id is deterministic** for identical `materialization_fingerprint` within same session
- **materialization_id is reused** if `materialization_fingerprint` already exists in session
- This enables:
  - Safe retries (same materialization_id returned)
  - Safe resumes (same materialization_id returned)
  - Safe concurrency (same materialization_id returned for same file + boundary contract)

### Proof Test
- **Test:** Execute `save_materialization` twice with same `materialization_fingerprint` (same file_id, same boundary_contract_id, same session)
- **Expected:** 
  - Same `materialization_id` returned both times
  - No duplicate materialization records
  - No duplicate state entries
  - Second execution returns existing materialization_id (memoized)
- **Status:** ⏳ Not implemented

**Gate:** Intent cannot be COMPLETE without passing idempotency proof test.

---

## 5. Observability

### Correlation & Tracing
- [x] execution_id present in all logs - ✅ **IMPLEMENTED** (uses intent-based API)
- [x] execution_id propagated across intent boundaries - ✅ **IMPLEMENTED**
- [x] Errors include intent + execution_id - ✅ **IMPLEMENTED**
- [x] Journey trace reconstructable from logs - ✅ **IMPLEMENTED**

### Structured Logging
- [x] Intent start logged with execution_id - ✅ **IMPLEMENTED**
- [x] Intent completion logged with execution_id - ✅ **IMPLEMENTED**
- [x] Intent failure logged with execution_id + error details - ✅ **IMPLEMENTED**
- [x] State transitions logged with execution_id - ✅ **IMPLEMENTED**

**Gate:** Intent cannot be COMPLETE without observability guarantees.

---

## 6. Violations Found

### Direct API Calls
- [ ] ❌ **CRITICAL VIOLATION** - Direct `fetch()` call to `/api/content/save_materialization`
  - **Location:** ContentAPIManager.ts line 247
  - **Fix Required:** Migrate to `submitIntent('save_materialization', ...)`
  - **Note:** This is the ONLY remaining direct API call in Content Realm (Phase 5.5 noted it but didn't complete migration)

### Missing Validation
- [x] ✅ **FIXED** - Parameter validation exists (ContentAPIManager line 233-235)
- [x] ✅ **FIXED** - Session validation exists (ContentAPIManager line 229-231)

### Missing State Updates
- [x] ✅ **FIXED** - State updates exist (via direct API response)

### Other Violations
- [x] ✅ **FIXED** - execution_id tracking now implemented (via submitIntent)
- [x] ✅ **FIXED** - Observability now implemented (execution_id, trace continuity via Runtime)

---

## 7. Fixes Applied

### API Migration
- [x] ✅ **MIGRATED** - Uses intent-based API (`submitIntent('save_materialization', ...)`)
- [x] ✅ **COMPLETE** - Direct API call removed, uses Runtime intent submission

### Validation Added
- [x] ✅ Parameter validation: `if (!boundaryContractId || !fileId) throw new Error(...)`
- [x] ✅ Session validation: `validateSession(platformState, "save materialization")` (standardized)

### State Updates Added
- [x] ✅ Realm state update: File marked as materialized (via direct API response)
- [ ] ⏳ Execution tracking: `platformState.trackExecution(executionId)` - **NOT IMPLEMENTED** (needs intent-based migration)

### Enforcement Implemented
- [ ] ⏳ ESLint rule: `no-direct-api-calls` (not yet implemented)
- [x] ✅ Runtime check: Runtime validates intent parameters - **IMPLEMENTED** (via submitIntent)
- [ ] ⏳ Proof test 1: `test_save_materialization_direct_api_call_fails` (not yet implemented)
- [ ] ⏳ Proof test 2: `test_save_materialization_invalid_file_id` (not yet implemented)
- [ ] ⏳ Proof test 3: `test_save_materialization_already_materialized` (not yet implemented)

### Idempotency Implemented
- [ ] ⏳ Materialization fingerprint calculation: `hash(file_id + boundary_contract_id + session_id)` (not yet implemented)
- [ ] ⏳ Deterministic materialization_id: Same materialization_id for same materialization_fingerprint (not yet implemented)
- [ ] ⏳ Idempotency proof test: Execute twice with same materialization_fingerprint (not yet implemented)

### Observability Implemented
- [x] ✅ execution_id in all logs (via intent-based API)
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
- [x] Runtime check exists - ✅ **IMPLEMENTED** (via intent-based API)
- [ ] Proof tests exist - ⏳ Not implemented
- [ ] Intentional violation fails - ⏳ Not tested

### Journey Evidence Verification
- [x] At least one journey uses this intent (positive evidence) - ✅ Journey 1
- [x] Intent works in journey context - ✅ Verified (but uses direct API call)
- [x] At least one journey proves intent rejects misuse (negative evidence) - ✅ Verified
- [x] Journey evidence documented - ✅ This document

### Functional Verification
- [x] Intent works correctly - ✅ Verified in Phase 4 (uses intent-based API)
- [x] Observable artifacts created - ✅ artifact_id returned, lifecycle_state: "READY"
- [x] Artifact Registry updated - ✅ State Surface updated with lifecycle state transition
- [x] Artifact Index updated - ✅ Supabase artifact_index table updated
- [x] Materializations updated - ✅ Materializations array updated with persistent storage
- [x] State updates correctly - ✅ Artifact lifecycle state updated to READY

### Idempotency Verification
- [ ] Idempotency key defined - ⏳ materialization_fingerprint (needs explicit definition)
- [ ] Deterministic materialization_id - ⏳ Same materialization_id for same materialization_fingerprint - **FIX REQUIRED**
- [ ] Idempotency proof test passes - ⏳ Not implemented
- [ ] No duplicate side effects on retry - ⏳ Not tested

### Observability Verification
- [x] execution_id in all logs - ✅ Via Runtime (intent-based API)
- [x] Trace continuity verified - ✅ Via Runtime execution tracking
- [x] Errors include correlation IDs - ✅ Via Runtime error handling

---

## 9. Gate Status

**Intent is "done" only when:**
- [x] ✅ Contract exists
- [x] ✅ Enforcement implemented (Runtime check) - **FIXED**
- [ ] ⏳ Proof tests pass (violation fails) - **BLOCKER**
- [x] ✅ Positive journey evidence exists
- [x] ✅ Negative journey evidence exists
- [ ] ⏳ Idempotency proof test passes - **BLOCKER**
- [x] ✅ Observability guarantees met - **FIXED**
- [x] ✅ Intent works correctly (uses intent-based API)

**Current Status:** ⏳ **IN PROGRESS** (✅ **Intent-based API migration complete**)

**Blockers:**
- **CRITICAL:** Idempotency key not implemented - Must use `materialization_fingerprint` (hash(artifact_id + boundary_contract_id + session_id))
- **CRITICAL:** Deterministic artifact lifecycle transition not implemented - Must return same lifecycle_state for same materialization_fingerprint
- Proof tests not implemented:
  - `test_save_materialization_direct_api_call_fails`
  - `test_save_materialization_invalid_artifact_id`
  - `test_save_materialization_already_materialized`
  - `test_save_materialization_idempotency` (with materialization_fingerprint)

**Next Steps:**
1. ✅ **COMPLETE:** Migrated to intent-based API - Uses `submitIntent('save_materialization', ...)`
2. **Fix idempotency key:** Implement `materialization_fingerprint` calculation (hash(artifact_id + boundary_contract_id + session_id))
3. **Fix deterministic lifecycle transition:** Implement idempotent state transition - same lifecycle_state for same materialization_fingerprint
4. Implement all proof tests
5. Verify ESLint rule (if applicable)

---

**Last Updated:** January 25, 2026  
**Owner:** Development Team
