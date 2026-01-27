# Journey Contract: File Upload & Processing

**Journey:** File Upload & Processing  
**Journey Number:** 1  
**Status:** ⏳ **IN PROGRESS**  
**Priority:** 🔴 **PRIORITY 1** - Foundation journey for Content Realm

---

## 1. Journey Overview

### Intents in Journey
1. `ingest_file` - Step 1: User uploads file (Working Material, materialization pending)
2. `parse_content` - Step 2: Parse uploaded file (extract structure/chunks)
3. `extract_embeddings` - Step 3: Extract semantic embeddings from parsed file
4. `save_materialization` - Step 4: User explicitly saves file (Working Material → Records of Fact)
5. `get_semantic_interpretation` - Step 5: Retrieve semantic interpretation for display (optional, non-gating)

**Note:** `get_semantic_interpretation` **must not block journey completion** and must tolerate partial upstream state (e.g., embeddings exist but materialization not saved). It is a read-only query intent that can be called at any point after parsing, but journey completion does not depend on it.

### Journey Flow
```
[User uploads file]
    ↓
[ingest_file] → file_artifact (artifact_id, artifact_type: "file", lifecycle_state: "PENDING")
    - Registered in State Surface (ArtifactRegistry)
    - Indexed in Supabase (artifact_index)
    - Materialization in GCS (materializations array)
    ↓
[User selects ingestion_profile] → Pending intent created (intent_executions table)
    - ingestion_profile stored in intent context
    - Enables resumable workflows
    ↓
[User clicks "Parse"]
    ↓
[parse_content] → parsed_content_artifact (artifact_id, artifact_type: "parsed_content", parent_artifacts: [file_artifact_id], lifecycle_state: "PENDING")
    - Retrieves ingestion_profile from pending intent context
    - Registered in State Surface with lineage
    - Indexed in Supabase with lineage metadata
    - Materialization in GCS (parsed JSON)
    ↓
[extract_embeddings] → embeddings_artifact (artifact_id, artifact_type: "embeddings", parent_artifacts: [parsed_content_artifact_id], lifecycle_state: "PENDING")
    - Registered in State Surface with lineage
    - Indexed in Supabase with lineage metadata
    - Materializations in DuckDB/ArangoDB
    ↓
[User clicks "Save"]
    ↓
[save_materialization] → file_artifact lifecycle transition (lifecycle_state: "PENDING" → "READY")
    - Artifact Registry updated (State Surface)
    - Artifact Index updated (Supabase)
    - Materializations marked as persistent
    ↓
[get_semantic_interpretation] → Resolves artifacts via State Surface resolve_artifact() (optional, anytime after parsing)
    - Uses State Surface as single source of truth
    - Retrieves from artifact materializations
    ↓
[Journey Complete]
```

### Expected Observable Artifacts
- **Step 1 (ingest_file):** 
  - `artifact_id` (artifact_type: "file")
  - `boundary_contract_id`
  - `lifecycle_state: "PENDING"`
  - `materializations` array (GCS storage)
  - Artifact registered in State Surface (ArtifactRegistry)
  - Artifact indexed in Supabase (artifact_index)
- **Step 2 (parse_content):** 
  - `artifact_id` (artifact_type: "parsed_content")
  - `parent_artifacts: [file_artifact_id]` (lineage)
  - `lifecycle_state: "PENDING"`
  - `structure`, `chunks`
  - `materializations` array (GCS JSON)
  - `ingestion_profile` retrieved from pending intent context
  - Artifact registered in State Surface with lineage
  - Artifact indexed in Supabase with lineage metadata
- **Step 3 (extract_embeddings):** 
  - `artifact_id` (artifact_type: "embeddings")
  - `parent_artifacts: [parsed_content_artifact_id]` (lineage)
  - `lifecycle_state: "PENDING"`
  - `embeddings`, `metadata`
  - `materializations` array (DuckDB/ArangoDB)
  - Artifact registered in State Surface with lineage
  - Artifact indexed in Supabase with lineage metadata
- **Step 4 (save_materialization):** 
  - `artifact_id` (file artifact)
  - `lifecycle_state: "READY"` (transitioned from PENDING)
  - `materializations` array updated (marked as persistent)
  - Artifact Registry updated (State Surface)
  - Artifact Index updated (Supabase)
- **Step 5 (get_semantic_interpretation):** 
  - `artifact_id`
  - `interpretation`, `entities`, `relationships`
  - Resolved via State Surface `resolve_artifact()`

### Artifact Lifecycle State Transitions
- **Step 1:** File artifact created with `lifecycle_state: "PENDING"` (Working Material)
- **Step 2:** Parsed content artifact created with `lifecycle_state: "PENDING"` (Working Material)
- **Step 3:** Embeddings artifact created with `lifecycle_state: "PENDING"` (Working Material)
- **Step 4:** File artifact transitions `lifecycle_state: "PENDING"` → `"READY"` (Records of Fact)

**Note:** Derived artifacts (parsed_content, embeddings) remain in `PENDING` state until explicitly materialized. Only the file artifact transitions to `READY` when user clicks "Save".

### Idempotency Scope (Per Intent)

| Intent               | Idempotency Key                                    | Scope                    |
| -------------------- | -------------------------------------------------- | ------------------------ |
| `ingest_file`        | `content_fingerprint` (hash(file_content) + session_id) | per tenant, per session  |
| `parse_content`      | `parsing_fingerprint` (hash(artifact_id + parse_options)) | per artifact, per parse config |
| `extract_embeddings` | `embedding_fingerprint` (hash(artifact_id + embedding_options)) | per artifact, per embedding config |
| `save_materialization` | `materialization_fingerprint` (hash(artifact_id + boundary_contract_id + session_id)) | per artifact, per boundary contract |

**Note:** Idempotency keys are defined to prevent duplicate side effects. Same key = same result, no duplicate artifacts. Artifact IDs are deterministic based on these fingerprints.

### Journey Completion Definition

**Journey 1 is considered complete when:**

* File is materialized (`save_materialization` succeeds) **OR**
* User intentionally abandons after parsing/embedding (explicit user action)

**Journey completion ≠ semantic interpretation displayed.**

`get_semantic_interpretation` is optional and does not gate journey completion. The journey can be considered successful even if semantic interpretation is never requested.

---

## 2. Scenario 1: Happy Path

### Test Description
Complete journey works end-to-end without failures. User uploads file, parses it, extracts embeddings, saves it, and views semantic interpretation.

### Steps
1. [ ] User selects file and clicks "Upload"
2. [ ] `ingest_file` intent executes → File artifact created (`artifact_id`, `artifact_type: "file"`, `lifecycle_state: "PENDING"`)
3. [ ] User selects ingestion_profile (parsing type) → Pending intent created in `intent_executions` table
4. [ ] User clicks "Parse"
5. [ ] `parse_content` intent executes → Parsed content artifact created (`artifact_id`, `artifact_type: "parsed_content"`, `parent_artifacts: [file_artifact_id]`, `lifecycle_state: "PENDING"`)
   - `ingestion_profile` retrieved from pending intent context
6. [ ] `extract_embeddings` intent executes → Embeddings artifact created (`artifact_id`, `artifact_type: "embeddings"`, `parent_artifacts: [parsed_content_artifact_id]`, `lifecycle_state: "PENDING"`)
7. [ ] User clicks "Save"
8. [ ] `save_materialization` intent executes → File artifact lifecycle transition (`lifecycle_state: "PENDING"` → `"READY"`)
9. [ ] User views semantic interpretation
10. [ ] `get_semantic_interpretation` intent executes → Artifacts resolved via State Surface `resolve_artifact()`, interpretation returned
11. [ ] Journey completes successfully

### Verification
- [ ] Observable artifacts at each step (artifact_id, artifact_type, lifecycle_state, parent_artifacts)
- [ ] Artifacts registered in State Surface (ArtifactRegistry) at each step
- [ ] Artifacts indexed in Supabase (artifact_index) with lineage metadata
- [ ] Materializations created and stored correctly (GCS, DuckDB, ArangoDB)
- [ ] Lifecycle state transitions correctly (`PENDING` → `READY`)
- [ ] Pending intent created with ingestion_profile in intent context
- [ ] ingestion_profile retrieved from pending intent context during parse_content
- [ ] State updates correctly (state.realm.content.files, state.realm.content.parsedFiles, etc.)
- [ ] All intents use intent-based API (submitIntent, no direct API calls)
- [ ] All intents flow through Runtime (ExecutionLifecycleManager)
- [ ] All intents have execution_id (tracked via platformState.trackExecution)
- [ ] Artifacts stored as Working Material initially (lifecycle_state: "PENDING")
- [ ] File artifact transitions to Records of Fact after save_materialization (lifecycle_state: "READY")
- [ ] Artifact Registry updated in State Surface after save_materialization
- [ ] Artifact Index updated in Supabase after save_materialization
- [ ] All execution_ids present in logs
- [ ] Journey trace reconstructable from logs

### Status
⏳ Not tested

**Result:** `[test_result]`

---

## 3. Scenario 2: Injected Failure

### Test Description
Journey handles failure gracefully when failure is injected at one step. User can see appropriate error and retry.

### Failure Injection Points (Test Each)
- **Option A:** Failure at `ingest_file` (network failure, file too large)
- **Option B:** Failure at `parse_content` (parsing error, unsupported file type)
- **Option C:** Failure at `extract_embeddings` (embedding service unavailable)
- **Option D:** Failure at `save_materialization` (storage failure, Supabase unavailable)

### Steps (Example: Failure at parse_content)
1. [ ] User selects file and clicks "Upload" ✅
2. [ ] `ingest_file` intent executes → File artifact created (`artifact_id`, `lifecycle_state: "PENDING"`) ✅
3. [ ] User selects ingestion_profile → Pending intent created ✅
4. [ ] User clicks "Parse"
5. [ ] `parse_content` intent executes → ❌ **FAILURE INJECTED** (parsing error)
6. [ ] Journey handles failure gracefully
7. [ ] User sees appropriate error message ("File parsing failed: [reason]")
8. [ ] State remains consistent (file artifact still valid, lifecycle_state: "PENDING", no corruption)
9. [ ] Pending intent remains in intent_executions table (can be resumed)
10. [ ] User can retry parsing or upload different file

### Verification
- [ ] Failure handled gracefully (no crash, no unhandled exception)
- [ ] User sees appropriate error message (clear, actionable)
- [ ] State remains consistent (no corruption, completed artifacts remain valid)
- [ ] Artifact lifecycle states remain correct (completed artifacts stay in their current state)
- [ ] Pending intents remain in intent_executions table (can be resumed)
- [ ] User can retry failed step (can retry parse_content with same artifact_id)
- [ ] No partial state left behind (no orphaned artifacts, no inconsistent lifecycle states)
- [ ] Error includes execution_id (for debugging)
- [ ] Error logged with intent + execution_id

### Status
⏳ Not tested

**Result:** `[test_result]`

---

## 4. Scenario 3: Partial Success

### Test Description
Journey handles partial completion when some steps succeed and some fail. User can retry failed steps without losing completed work.

### Partial Success Pattern
- **Steps 1-2:** ✅ Succeed (ingest_file, parse_content)
- **Step 3:** ❌ Fails (extract_embeddings)
- **Steps 4-5:** Not attempted (save_materialization, get_semantic_interpretation)

### Steps
1. [ ] User selects file and clicks "Upload" ✅
2. [ ] `ingest_file` intent executes → File uploaded, `file_id` returned ✅
3. [ ] User clicks "Parse" ✅
4. [ ] `parse_content` intent executes → File parsed, `parsed_file_id` returned ✅
5. [ ] `extract_embeddings` intent executes → ❌ **FAILS** (embedding service unavailable)
6. [ ] Journey handles partial completion
7. [ ] User can retry failed step (extract_embeddings)
8. [ ] Completed steps remain valid (file_id, parsed_file_id still accessible)
9. [ ] User can proceed after retry succeeds

### Verification
- [ ] Partial state handled correctly (completed artifacts remain valid)
- [ ] User can retry failed step (can retry extract_embeddings)
- [ ] No state corruption (no duplicate artifacts, no inconsistent lifecycle states)
- [ ] Completed artifacts remain valid (file artifact, parsed_content artifact still accessible via State Surface)
- [ ] Failed step can be retried (extract_embeddings can be retried with same parsed_content artifact_id)
- [ ] Lifecycle state transitions are monotonic (can't go backwards, can only progress: PENDING → READY)
- [ ] No duplicate artifacts (no duplicate artifact_id, idempotency keys prevent duplicates)
- [ ] Artifact Registry remains consistent (State Surface has correct artifact records)
- [ ] Artifact Index remains consistent (Supabase artifact_index has correct metadata)

### Status
⏳ Not tested

**Result:** `[test_result]`

---

## 5. Scenario 4: Retry/Recovery

### Test Description
Journey recovers correctly when user retries after failure. Idempotency ensures no duplicate side effects.

### Retry Pattern
1. Journey fails at extract_embeddings
2. User retries extract_embeddings
3. Journey recovers and completes

### Steps
1. [ ] User selects file and clicks "Upload" ✅
2. [ ] `ingest_file` intent executes → File artifact created (`artifact_id`, `lifecycle_state: "PENDING"`) ✅
3. [ ] User clicks "Parse" ✅
4. [ ] `parse_content` intent executes → Parsed content artifact created (`artifact_id`, `parent_artifacts: [file_artifact_id]`, `lifecycle_state: "PENDING"`) ✅
5. [ ] `extract_embeddings` intent executes → ❌ **FAILS** (first attempt, network timeout)
6. [ ] User retries extract_embeddings
7. [ ] `extract_embeddings` intent executes → ✅ **SUCCEEDS** (retry, same parsed_content artifact_id, idempotent)
8. [ ] User clicks "Save" ✅
9. [ ] `save_materialization` intent executes → File artifact lifecycle transition (`PENDING` → `READY`) ✅
10. [ ] Journey completes

### Verification
- [ ] Journey recovers correctly (retry succeeds, journey completes)
- [ ] No duplicate state (no duplicate artifacts, no duplicate embeddings)
- [ ] State consistency maintained (same artifact_id, same parent_artifacts)
- [ ] Retry succeeds (extract_embeddings succeeds on retry)
- [ ] Journey completes after retry (all steps complete)
- [ ] **Idempotency verified** (no duplicate side effects - same artifact_id returned if same embedding_fingerprint)
- [ ] **Same execution_id reused safely** (or new execution_id doesn't cause duplicates)
- [ ] **Lifecycle state transitions are monotonic** (can't go backwards, can only progress: PENDING → READY)
- [ ] **Content fingerprint/idempotency keys work** (same file content + session = same artifact_id)
- [ ] **Artifact Registry consistency** (State Surface has correct artifact records)
- [ ] **Artifact Index consistency** (Supabase artifact_index has correct metadata)

### Status
⏳ Not tested

**Result:** `[test_result]`

---

## 6. Scenario 5: Boundary Violation

### Test Description
Journey rejects invalid inputs and maintains state consistency. User sees clear error messages.

### Boundary Violations (Test Each)
- **Type A:** Invalid file (file too large > 100MB, unsupported format)
- **Type B:** Invalid parameters (missing file_id, invalid file_reference)
- **Type C:** Invalid state (trying to save file that wasn't ingested, trying to parse file that doesn't exist)
- **Type D:** Cross-tenant access (trying to access file from different tenant)

### Steps (Example: File too large)
1. [ ] User selects file > 100MB
2. [ ] User clicks "Upload"
3. [ ] `ingest_file` intent rejects invalid input (file size > 100MB limit)
4. [ ] User sees clear error message ("File size exceeds 100MB limit. Maximum allowed size is 100MB.")
5. [ ] State remains consistent (no file_id created, no partial state)
6. [ ] User can correct input (select smaller file) and retry

### Verification
- [ ] Invalid input rejected (file too large, invalid parameters, invalid state)
- [ ] Clear error message displayed (actionable, specific)
- [ ] No state corruption (no partial file_id, no orphaned records)
- [ ] User can correct input and retry (can upload smaller file, can fix parameters)
- [ ] No partial state left behind (no file_id if validation fails)
- [ ] Error includes execution_id (for debugging)
- [ ] Error logged with intent + execution_id

### Status
⏳ Not tested

**Result:** `[test_result]`

---

## 7. Architectural Verification

### Intent Flow
- [x] All intents use intent-based API (submitIntent, no direct API calls)
- [x] All intents flow through Runtime (ExecutionLifecycleManager)
- [x] All intents have execution_id (tracked via platformState.trackExecution)
- [x] All intents have parameter validation (before submitIntent)
- [x] All intents have session validation (validateSession)

### State Authority
- [ ] Runtime is authoritative (frontend syncs with Runtime state)
- [ ] State Surface is authoritative for artifact resolution (resolve_artifact())
- [ ] Artifact Index is authoritative for artifact discovery (list_artifacts())
- [ ] Frontend syncs with Runtime (state.realm.content.* updated from Runtime)
- [ ] No state divergence (frontend state matches Runtime state)
- [ ] Artifacts persist across steps (artifact_id available in subsequent steps)
- [ ] Artifact Registry (State Surface) maintains artifact lifecycle states
- [ ] Artifact Index (Supabase) maintains artifact metadata for discovery

### Enforcement
- [x] All intents have enforcement (Runtime validates parameters)
- [ ] Enforcement prevents violations (direct API calls blocked, invalid parameters rejected)
- [ ] Intentional violations fail (proof tests pass)

### Observability
- [x] execution_id present in all logs (via Runtime submitIntent)
- [x] execution_id propagated across intent boundaries (via Runtime execution tracking)
- [x] Errors include intent + execution_id (via Runtime error handling)
- [ ] Journey trace reconstructable from logs (all execution_ids linked, trace continuity)

---

## 8. SRE Verification

### Error Handling
- [ ] Journey handles network failure (ingest_file fails, user can retry)
- [ ] Journey handles storage failure (save_materialization fails, user can retry)
- [ ] Journey handles analysis failure (parse_content fails, user can retry)
- [ ] Journey handles timeout (long-running operations timeout gracefully)

### State Persistence
- [ ] State persists across steps (file_id available in parse_content)
- [ ] State persists across refresh (file_id persists after browser refresh)
- [ ] State persists across navigation (file_id persists when navigating away and back)

### Boundaries
- [ ] Browser → Frontend boundary works (file upload from browser to frontend)
- [ ] Frontend → Backend boundary works (submitIntent from frontend to Runtime)
- [ ] Backend → Runtime boundary works (Runtime executes intents)
- [ ] Runtime → Realm boundary works (Runtime calls Content Realm handlers)
- [ ] Realm → State Surface boundary works (Content Realm registers artifacts in ArtifactRegistry)
- [ ] Realm → Artifact Index boundary works (Content Realm indexes artifacts in Supabase artifact_index)
- [ ] Realm → Public Works boundary works (Content Realm accesses GCS, Supabase via Public Works abstractions)
- [ ] State Surface → Storage boundary works (State Surface resolves artifacts, retrieves from materializations)

### Browser-Only Tests (CIO Feedback)
- [ ] Hard refresh test (refresh page, state persists)
- [ ] Network throttling test (slow network, journey still works)
- [ ] Session expiration test (session expires, user can re-authenticate and continue)

### Chaos Tests (CIO Feedback)
- [ ] Random failure injection (random step fails, journey recovers)
- [ ] Concurrent execution (multiple users upload files simultaneously)
- [ ] Resource exhaustion (large files, many files, journey handles gracefully)

---

## 9. Gate Status

**Journey is "done" only when:**
- [ ] ✅ Happy path works
- [ ] ✅ Injected failure handled (all failure points tested)
- [ ] ✅ Partial success handled
- [ ] ✅ Retry/recovery works (with idempotency verified)
- [ ] ✅ Boundary violation rejected (all violation types tested)
- [ ] ✅ Architectural verification passes
- [ ] ✅ Observability guarantees met
- [ ] ✅ SRE verification passes (error handling, state persistence, boundaries, browser-only, chaos)

**Current Status:** ✅ **FOUNDATION COMPLETE** (Mock Tests Passing)

**✅ Completed (Mock Tests):**
- [x] Scenario 1: Happy Path (✅ PASSING)
- [x] Scenario 2: Injected Failure (✅ PASSING)
- [x] Scenario 3: Partial Success (✅ PASSING)
- [x] Scenario 4: Retry/Recovery (✅ PASSING)
- [x] Scenario 5: Boundary Violation (✅ PASSING)

**⏳ Remaining (Real Infrastructure Testing):**
- [ ] Backend integration tests (real Runtime execution)
- [ ] Database/storage tests (real Supabase/GCS)
- [ ] Browser E2E tests (Playwright/Cypress)
- [ ] Network condition tests
- [ ] Session expiration tests
- [ ] Chaos testing
- [ ] Boundary matrix testing

**Next Steps:**
1. ✅ **DONE:** All 5 scenarios tested with mocks (foundation complete)
2. ⏭️ **NEXT:** Set up backend integration test environment
3. ⏭️ **NEXT:** Create first real backend test (Journey 1 Happy Path)
4. ⏭️ **NEXT:** Verify real Runtime execution
5. ⏭️ **NEXT:** Browser E2E tests
6. ⏭️ **NEXT:** Production readiness testing (chaos, boundary matrix)

---

**Last Updated:** January 25, 2026  
**Owner:** Development Team
