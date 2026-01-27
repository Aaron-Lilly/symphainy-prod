# Intent Contract: `parse_content`

**Intent:** `parse_content`  
**Realm:** `content`  
**Status:** ⏳ **IN PROGRESS**  
**Priority:** 🔴 **PRIORITY 1** - Used in Journey 1 (File Upload & Processing)

---

## 1. Intent Contract

### Required Inputs
- `artifact_id`: File artifact identifier - **Required** (artifact-centric)
- `file_reference`: File reference string - **Required** (legacy compatibility)

### Optional Inputs
- `copybook_reference`: Copybook reference (for mainframe files)
- `parse_options`: Parser-specific options (Record<string, any>)

**Note:** `ingestion_profile` (parsing type: structured, unstructured, hybrid, workflow/SOP, data model) is **NOT** passed as a parameter. It is retrieved from the **pending intent context** in the `intent_executions` table. This enables resumable workflows where the user can upload a file, select an ingestion profile later, and resume parsing in a different session.

**Pending Intent Context:** If a pending intent exists for this artifact with `intent_type: "parse_content"`, the `ingestion_profile` is retrieved from the intent's `context` field in `intent_executions` table.

### Boundary Constraints
- **Artifact Must Exist:** File artifact must have been created via `ingest_file` first
- **Artifact Must Be Accessible:** Artifact must be accessible via `artifact_id` and resolvable via State Surface
- **Artifact Lifecycle State:** Source artifact should be in `lifecycle_state: "PENDING"` or `"READY"`

### Forbidden Behaviors
- ❌ Direct API calls to `/api/v1/*/parse`
- ❌ Direct API calls to `/api/operations/*`
- ❌ Missing parameter validation
- ❌ Missing session validation
- ❌ Missing state updates
- ❌ Parsing file that doesn't exist or isn't accessible

### Forbidden State Transitions
- ❌ `parse_content` MUST NOT:
  - Modify source artifact content
  - Delete source artifact
  - Change artifact_id or file_reference
  - Transition artifact `lifecycle_state` from `PENDING` to `READY` (parsed data is Working Material until promoted via `save_materialization`)
  - Modify parent artifact's lifecycle state

### Guaranteed Outputs
- `parsed_file_id`: Identifier for parsed file (typically same as `file_id`)
- `parsed_file_reference`: Reference to parsed file data
- `structure`: Extracted structure (if structured data)
- `chunks`: Extracted chunks (if unstructured data)
- Realm state update: `state.realm.content.parsedFiles[fileId]` updated with parsed file data
- Execution tracked: `state.execution[executionId]` updated

---

## 2. Runtime Enforcement

### ESLint Rule (if applicable)
- **Rule:** `no-direct-api-calls`
- **Pattern:** `fetch\('/api/v1.*parse|fetch\('/api/operations.*parse`
- **Message:** `Use submitIntent('parse_content', ...) instead of direct API calls`
- **Status:** ⏳ Not implemented

### Runtime Check
- **Check:** Runtime validates intent parameters before execution
- **Action if violated:** Runtime rejects intent with error message
- **Status:** ✅ Implemented (Runtime validates parameters)

### Proof Tests
- **Test 1:** `test_parse_content_direct_api_call_fails`
  - **Action:** Try to call `/api/v1/content/parse` directly
  - **Expected:** Request fails or is rejected
  - **Status:** ⏳ Not implemented

- **Test 2:** `test_parse_content_invalid_file_reference`
  - **Action:** Submit `parse_content` with invalid `file_reference`
  - **Expected:** Intent rejected with clear error message
  - **Status:** ⏳ Not implemented

---

## 3. Journey Evidence

### Journeys Using This Intent
- Journey 1: File Upload & Processing - Step 2 (File Parsing)

### Positive Evidence
- **Journey:** File Upload & Processing
- **Step:** User clicks "Parse" on uploaded file → `parse_content` intent → Parsed content artifact created
- **Verification:** 
  - File parsed successfully
  - `artifact_id` returned (artifact_type: "parsed_content")
  - `parsed_file_reference` returned
  - Structure/chunks extracted
  - `ingestion_profile` retrieved from pending intent context (intent_executions table)
  - Artifact registered in State Surface with `parent_artifacts: [file_artifact_id]`
  - Artifact indexed in Supabase `artifact_index` with lineage metadata
  - Materialization created in GCS (parsed JSON)
  - `lifecycle_state: "PENDING"` (Working Material)
  - State updated: `state.realm.content.parsedFiles[artifactId]` contains parsed file data
- **Status:** ✅ Verified (Phase 4 implementation)

### Negative Evidence
- **Journey:** File Upload & Processing
- **Misuse Attempt:** Submit `parse_content` without `file_id` or `file_reference`
- **Expected Behavior:** Intent rejects execution with clear error message
- **Verification:** Parameter validation throws error (ContentAPIManager line 371-376)
  - `if (!fileId) throw new Error("file_id is required for parse_content")`
  - `if (!fileReference) throw new Error("file_reference is required for parse_content")`
- **Status:** ✅ Verified

---

## 4. Idempotency & Re-entrancy

### Idempotency Key
- **Primary Key:** `parsing_fingerprint`
- **Derived From:** `hash(file_id + file_reference + parse_options)`
- **Scope:** `per session, per file, per parse configuration`

### Required Behavior
- Repeated execution with same `parsing_fingerprint` must:
  - [ ] Return same `parsed_file_id` (deterministic for identical parsing_fingerprint)
  - [ ] Return same `parsed_file_reference`
  - [ ] Never duplicate parsing work (same parsed_file_id reused if parsing_fingerprint already exists)
  - [ ] Not corrupt state (no duplicate entries in state.realm.content.parsedFiles)

### Canonical Artifact Identity
- **parsed_file_id is deterministic** for identical `parsing_fingerprint` within same session
- **parsed_file_id is reused** if `parsing_fingerprint` already exists in session
- This enables:
  - Safe retries (same parsed_file_id returned)
  - Safe resumes (same parsed_file_id returned)
  - Safe concurrency (same parsed_file_id returned for same parsing configuration)

### Proof Test
- **Test:** Execute `parse_content` twice with same `parsing_fingerprint` (same file_id, same parse_options)
- **Expected:** 
  - Same `parsed_file_id` returned both times
  - No duplicate parsing work
  - No duplicate state entries
  - Second execution returns existing parsed_file_id (memoized)
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
- [x] ✅ **FIXED** - Session validation exists (ContentAPIManager line 367)
- [x] ✅ **FIXED** - Parameter validation for `file_id` and `file_reference` (ContentAPIManager line 371-377)
  - **Location:** ContentAPIManager.parseFile() - validation added
  - **Status:** ✅ **COMPLETE** - Validation implemented before submitIntent

### Missing State Updates
- [x] ✅ **FIXED** - State updates exist (via Runtime execution tracking)

### Other Violations
- [ ] ⚠️ **POTENTIAL ISSUE** - Parse options may not be fully validated
  - **Location:** ContentAPIManager line 372-376
  - **Note:** Parse options are passed through without validation

---

## 7. Fixes Applied

### API Migration
- [x] ✅ Migrated to `ContentAPIManager.parseFile()` using `submitIntent('parse_content', ...)`
- [x] ✅ Removed direct API call (if any existed)

### Validation Added
- [x] ✅ Session validation: `validateSession(platformState, "parse file")`
- [ ] ⏳ Parameter validation: `if (!fileId || !fileReference) throw new Error(...)` - **TODO**

### State Updates Added
- [x] ✅ Execution tracking: `platformState.trackExecution(executionId)`
- [x] ✅ Realm state update: `state.realm.content.parsedFiles[fileId]` updated (via Runtime)

### Enforcement Implemented
- [ ] ⏳ ESLint rule: `no-direct-api-calls` (not yet implemented)
- [x] ✅ Runtime check: Runtime validates intent parameters
- [ ] ⏳ Proof test 1: `test_parse_content_direct_api_call_fails` (not yet implemented)
- [ ] ⏳ Proof test 2: `test_parse_content_invalid_file_reference` (not yet implemented)

### Idempotency Implemented
- [ ] ⏳ Parsing fingerprint calculation: `hash(file_id + file_reference + parse_options)` (not yet implemented)
- [ ] ⏳ Deterministic parsed_file_id: Same parsed_file_id for same parsing_fingerprint (not yet implemented)
- [ ] ⏳ Idempotency proof test: Execute twice with same parsing_fingerprint (not yet implemented)

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
- [x] Observable artifacts created - ✅ artifact_id (parsed_content), parsed_file_reference returned
- [x] Artifact registered in State Surface - ✅ ArtifactRegistry updated with parent_artifacts
- [x] Artifact indexed in Supabase - ✅ artifact_index table updated with lineage
- [x] Materialization created - ✅ GCS storage, materializations array populated
- [x] Lifecycle state correct - ✅ lifecycle_state: "PENDING"
- [x] Ingestion profile retrieved - ✅ From pending intent context (intent_executions)
- [x] State updates correctly - ✅ state.realm.content.parsedFiles updated

### Idempotency Verification
- [ ] Idempotency key defined - ⏳ parsing_fingerprint (needs explicit definition)
- [ ] Deterministic parsed_file_id - ⏳ Same parsed_file_id for same parsing_fingerprint - **FIX REQUIRED**
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
- **CRITICAL:** Idempotency key not implemented - Must use `parsing_fingerprint` (hash(file_id + file_reference + parse_options))
- **CRITICAL:** Deterministic parsed_file_id not implemented - Must return same parsed_file_id for same parsing_fingerprint
- Parameter validation missing - Should validate file_id and file_reference before submitIntent
- Proof tests not implemented:
  - `test_parse_content_direct_api_call_fails`
  - `test_parse_content_invalid_file_reference`
  - `test_parse_content_idempotency` (with parsing_fingerprint)
- Negative journey evidence not verified

**Next Steps:**
1. **Fix idempotency key:** Implement `parsing_fingerprint` calculation
2. **Fix deterministic parsed_file_id:** Implement memoization - return same parsed_file_id for same parsing_fingerprint
3. **Add parameter validation:** Validate file_id and file_reference before submitIntent
4. Implement all proof tests
5. Verify negative journey evidence
6. Verify ESLint rule (if applicable)

---

**Last Updated:** January 25, 2026  
**Owner:** Development Team
