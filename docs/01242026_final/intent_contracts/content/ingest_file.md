# Intent Contract: `ingest_file`

**Intent:** `ingest_file`  
**Realm:** `content`  
**Status:** ⏳ **IN PROGRESS**  
**Priority:** 🔴 **PRIORITY 1** - Used in Journey 1 (File Upload & Processing)

---

## 1. Intent Contract

### Required Inputs
- `file`: File object (from user upload) - **Required**
- `file_content`: Hex-encoded file content - **Required** (derived from file)
- `ui_name`: User-friendly filename - **Required**

### Optional Inputs
- `boundary_contract_id`: Optional boundary contract ID (auto-created if not provided)
- `file_type`: File type category (default: 'unstructured')
- `mime_type`: MIME type (from file.type)
- `filename`: Original filename (from file.name)

**Note:** `ingestion_profile` (parsing type selection) is **NOT** stored on the artifact. It lives in the **intent context** (`intent_executions` table) as a pending intent. This enables resumable workflows where the user can upload a file, select an ingestion profile later, and resume parsing in a different session.

### Forbidden Behaviors
- ❌ Direct API calls to `/api/v1/*/upload-file`
- ❌ Direct API calls to `/api/operations/*`
- ❌ Missing parameter validation
- ❌ Missing session validation
- ❌ Missing file size validation (must enforce 100MB limit)
- ❌ Missing state updates
- ❌ Persisting file without user approval (must use two-phase: upload → save)

### Forbidden State Transitions
- ❌ `ingest_file` MUST NOT:
  - Write to persistent storage (Supabase materialization table)
  - Transition artifact `lifecycle_state` from `PENDING` to `READY`
  - Create persistent materialization record
  - Mark artifact as "saved" or "persisted"
- **Enforcement:** Runtime must reject any attempt to materialize during `ingest_file` execution
- **Lifecycle State:** Artifact MUST remain in `lifecycle_state: "PENDING"` until `save_materialization` is called
- **Proof Test:** `test_ingest_file_cannot_materialize` - Verify `lifecycle_state` remains `PENDING` and no persistent record created

### Guaranteed Outputs
- `file_id`: Unique identifier for the uploaded file
  - **Deterministic:** Same `file_id` returned for identical `content_fingerprint` within same session
  - **Memoized:** If `content_fingerprint` already exists in session, existing `file_id` is reused
- `boundary_contract_id`: Boundary contract ID (auto-created)
- `file_reference`: File reference string (`file:tenantId:sessionId:fileId`)
- `materialization_pending`: Boolean indicating file is not yet persisted (MUST be `true` - see Forbidden State Transitions)
- `content_fingerprint`: Content fingerprint (hash of file_content + session_id) for idempotency
- Realm state update: `state.realm.content.files[fileId]` updated with file metadata
- Execution tracked: `state.execution[executionId]` updated

---

## 2. Runtime Enforcement

### ESLint Rule (if applicable)
- **Rule:** `no-direct-api-calls`
- **Pattern:** `fetch\('/api/v1.*upload|fetch\('/api/operations.*upload`
- **Message:** `Use submitIntent('ingest_file', ...) instead of direct API calls`
- **Status:** ⏳ Not implemented

### Runtime Check
- **Check:** Runtime validates intent parameters before execution
- **Action if violated:** Runtime rejects intent with error message
- **Status:** ✅ Implemented (Runtime validates parameters)

### Payload Size Enforcement
- **Max file_content size:** 100 MB (104,857,600 bytes) - See `FILE_SIZE_POLICY.md`
- **Action if exceeded:**
  - Reject intent immediately
  - Return error: "File size exceeds 100MB limit. Maximum allowed size is 100MB."
  - Require pre-signed upload / chunked flow for larger files (future enhancement)
- **Status:** ⏳ Not implemented (needs enforcement in ContentAPIManager before submitIntent)
- **Proof Test:** `test_ingest_file_large_payload_rejected` - Verify intent rejected for files > 100MB

### Proof Tests
- **Test 1:** `test_ingest_file_direct_api_call_fails`
  - **Action:** Try to call `/api/v1/content/upload-file` directly
  - **Expected:** Request fails or is rejected
  - **Status:** ⏳ Not implemented

- **Test 2:** `test_ingest_file_large_payload_rejected`
  - **Action:** Submit `ingest_file` with file_content > 100MB
  - **Expected:** Intent rejected with clear error message
  - **Status:** ⏳ Not implemented

- **Test 3:** `test_ingest_file_cannot_materialize`
  - **Action:** Execute `ingest_file` and verify no persistent storage record created
  - **Expected:** 
    - `materialization_pending` remains `true`
    - No record in Supabase materialization table
    - File stored only in temporary/working material storage
  - **Status:** ⏳ Not implemented

---

## 3. Journey Evidence

### Journeys Using This Intent
- Journey 1: File Upload & Processing - Step 1 (File Upload)

### Positive Evidence
- **Journey:** File Upload & Processing
- **Step:** User uploads file → `ingest_file` intent → File artifact created (Working Material)
- **Verification:** 
  - File uploaded successfully
  - `artifact_id` returned (artifact_type: "file")
  - `boundary_contract_id` returned
  - `lifecycle_state: "PENDING"` (artifact not yet persisted)
  - Artifact registered in State Surface (ArtifactRegistry)
  - Artifact indexed in Supabase `artifact_index` table
  - Materialization created in GCS (stored in `materializations` array)
  - State updated: `state.realm.content.files[artifactId]` contains file metadata
- **Status:** ✅ Verified (Phase 4 implementation)

### Negative Evidence
- **Journey:** File Upload & Processing
- **Misuse Attempt:** Submit `ingest_file` without `file` parameter
- **Expected Behavior:** Intent rejects execution with clear error message
- **Verification:** Parameter validation throws error: "file is required for ingest_file"
- **Status:** ✅ Verified (ContentAPIManager line 114-116)

---

## 4. Idempotency & Re-entrancy

### Idempotency Key
- **Key:** `execution_id` (per intent execution)
- **Scope:** `per intent`

### Required Behavior
- Repeated execution with same execution_id must:
  - [ ] Return same result (same file_id, same boundary_contract_id)
  - [ ] Not duplicate side effects (no duplicate file storage)
  - [ ] Not corrupt state (no duplicate entries in state.realm.content.files)

### Proof Test
- **Test:** Execute `ingest_file` twice with same execution_id
- **Expected:** No duplicate files, no duplicate state entries
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
- [x] ✅ **FIXED** - Parameter validation exists (ContentAPIManager line 114-116)
- [x] ✅ **FIXED** - Session validation exists (ContentAPIManager line 111)
- [ ] ⚠️ **MISSING** - File size validation (100MB limit) not enforced in ContentAPIManager.uploadFile()
  - **Location:** Should be added before `submitIntent` call
  - **Policy:** See `FILE_SIZE_POLICY.md`
  - **Fix Required:** Add file size check: `if (file.size > 100 * 1024 * 1024) throw new Error("File size exceeds 100MB limit")`

### Missing State Updates
- [x] ✅ **FIXED** - State updates exist (ContentAPIManager line 181-195)

### Other Violations
- [ ] ⚠️ **POTENTIAL ISSUE** - File content sent as hex-encoded string in intent parameters (large files may cause issues)
  - **Location:** ContentAPIManager line 122-124
  - **Note:** This follows CIO guidance for two-phase upload pattern, but may need optimization for large files

---

## 7. Fixes Applied

### API Migration
- [x] ✅ Migrated to `ContentAPIManager.uploadFile()` using `submitIntent('ingest_file', ...)`
- [x] ✅ Removed direct API call (if any existed)

### Validation Added
- [x] ✅ Parameter validation: `if (!file) throw new Error("file is required for ingest_file")`
- [x] ✅ Session validation: `validateSession(platformState, "upload file")`
- [ ] ⏳ File size validation: `if (file.size > 100 * 1024 * 1024) throw new Error("File size exceeds 100MB limit")` - **TODO**

### State Updates Added
- [x] ✅ Realm state update: `state.realm.content.files[fileId]` updated with file metadata
- [x] ✅ Execution tracking: `platformState.trackExecution(executionId)`

### Enforcement Implemented
- [ ] ⏳ ESLint rule: `no-direct-api-calls` (not yet implemented)
- [x] ✅ Runtime check: Runtime validates intent parameters
- [ ] ⏳ Proof test: `test_ingest_file_direct_api_call_fails` (not yet implemented)

### Idempotency Implemented
- [ ] ⏳ Content fingerprint calculation: `hash(file_content) + session_id` (not yet implemented)
- [ ] ⏳ Deterministic file_id: Same file_id for same content_fingerprint (not yet implemented)
- [ ] ⏳ Idempotency proof test: Execute twice with same content_fingerprint (not yet implemented)

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
- [ ] Proof test exists - ⏳ Not implemented
- [ ] Intentional violation fails - ⏳ Not tested

### Journey Evidence Verification
- [x] At least one journey uses this intent (positive evidence) - ✅ Journey 1
- [x] Intent works in journey context - ✅ Verified
- [x] At least one journey proves intent rejects misuse (negative evidence) - ✅ Verified
- [x] Journey evidence documented - ✅ This document

### Functional Verification
- [x] Intent works correctly - ✅ Verified in Phase 4
- [x] Observable artifacts created - ✅ artifact_id, boundary_contract_id returned
- [x] Artifact registered in State Surface - ✅ ArtifactRegistry updated
- [x] Artifact indexed in Supabase - ✅ artifact_index table updated
- [x] Materialization created - ✅ GCS storage, materializations array populated
- [x] Lifecycle state correct - ✅ lifecycle_state: "PENDING"
- [x] State updates correctly - ✅ state.realm.content.files updated

### Idempotency Verification
- [ ] Idempotency key defined - ⏳ content_fingerprint (hash(file_content) + session_id) - **FIX REQUIRED**
- [ ] Deterministic file_id - ⏳ Same file_id for same content_fingerprint - **FIX REQUIRED**
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
- [ ] ⏳ Proof test passes (violation fails) - **BLOCKER**
- [x] ✅ Positive journey evidence exists
- [x] ✅ Negative journey evidence exists
- [ ] ⏳ Idempotency proof test passes - **BLOCKER**
- [x] ✅ Observability guarantees met
- [x] ✅ Intent works correctly

**Current Status:** ⏳ **IN PROGRESS**

**Blockers:**
- **CRITICAL:** Idempotency key wrong - Must use `content_fingerprint` (hash(file_content) + session_id), not `execution_id`
- **CRITICAL:** Deterministic file_id not implemented - Must return same file_id for same content_fingerprint
- **CRITICAL:** Payload size enforcement not implemented - Must enforce 100MB limit before submitIntent
- **CRITICAL:** Two-phase persistence enforcement not implemented - Runtime must prevent materialization during ingest_file
- Proof tests not implemented:
  - `test_ingest_file_direct_api_call_fails`
  - `test_ingest_file_large_payload_rejected`
  - `test_ingest_file_cannot_materialize`
  - `test_ingest_file_idempotency` (with content_fingerprint)

**Next Steps:**
1. **Fix idempotency key:** Implement `content_fingerprint` calculation (hash(file_content) + session_id)
2. **Fix deterministic file_id:** Implement memoization - return same file_id for same content_fingerprint
3. **Fix payload size enforcement:** Add 100MB check in ContentAPIManager.uploadFile() before submitIntent
4. **Fix two-phase enforcement:** Add runtime check to prevent materialization during ingest_file
5. Implement all proof tests
6. Verify ESLint rule (if applicable)

---

**Last Updated:** January 25, 2026  
**Owner:** Development Team
