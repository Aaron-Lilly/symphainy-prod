# Journey Contract: File Upload & Materialization

**Journey:** File Upload & Materialization  
**Journey ID:** `journey_content_file_upload_materialization`  
**Solution:** Content Realm Solution  
**Status:** ⏳ **IN PROGRESS**  
**Priority:** 🔴 **PRIORITY 1** - Foundation journey for Content Realm

---

## 1. Journey Overview

### Intents in Journey
1. `ingest_file` - Step 1: Upload file to GCS (Working Material, materialization pending)
2. `save_materialization` - Step 2: User explicitly saves file (Working Material → Records of Fact, creates pending parsing journey)

**Note:** `save_materialization` creates a pending parsing journey in PENDING status with ingest type and file type stored in intent context. This enables resumable parsing workflows.

### Journey Flow
```
[User selects content type (structured/unstructured/hybrid)]
    ↓
[User selects file type category (PDF, CSV, Binary, etc.)]
    ↓
[User uploads file (and copybook if binary)]
    ↓
[ingest_file] → file_artifact (artifact_id, artifact_type: "file", lifecycle_state: "PENDING")
    - Registered in State Surface (ArtifactRegistry)
    - Indexed in Supabase (artifact_index)
    - Materialization in GCS (materializations array)
    - File content type and file type known at this point
    ↓
[User clicks "Save File"]
    ↓
[save_materialization] → file_artifact lifecycle transition (lifecycle_state: "PENDING" → "READY")
    - Artifact Registry updated (State Surface)
    - Artifact Index updated (Supabase)
    - Materializations marked as persistent
    - **Pending parsing journey created** (intent_executions table)
    - **Ingest type and file type stored in pending intent context**
    - Parsing journey status: PENDING (ready to be resumed)
    ↓
[Journey Complete]
```

### Expected Observable Artifacts
- **Step 1 (ingest_file):** 
  - `artifact_id` (artifact_type: "file")
  - `boundary_contract_id`
  - `lifecycle_state: "PENDING"`
  - `materializations` array (GCS storage)
  - Content type and file type (from user selection)
  - Artifact registered in State Surface (ArtifactRegistry)
  - Artifact indexed in Supabase (artifact_index)
- **Step 2 (save_materialization):** 
  - `artifact_id` (file artifact)
  - `lifecycle_state: "READY"` (transitioned from PENDING)
  - `materializations` array updated (marked as persistent)
  - **Pending parsing journey created** (intent_executions table, status: PENDING)
  - **Ingest type and file type stored in pending intent context**
  - Artifact Registry updated (State Surface)
  - Artifact Index updated (Supabase)

### Artifact Lifecycle State Transitions
- **Step 1:** File artifact created with `lifecycle_state: "PENDING"` (Working Material)
- **Step 2:** File artifact transitions `lifecycle_state: "PENDING"` → `"READY"` (Records of Fact)
- **Step 2:** Pending parsing journey created (status: PENDING, ready to be resumed)

### Idempotency Scope (Per Intent)

| Intent               | Idempotency Key                                    | Scope                    |
| -------------------- | -------------------------------------------------- | ------------------------ |
| `ingest_file`        | `content_fingerprint` (hash(file_content) + session_id) | per tenant, per session  |
| `save_materialization` | `materialization_fingerprint` (hash(artifact_id + boundary_contract_id + session_id)) | per artifact, per boundary contract |

**Note:** Idempotency keys prevent duplicate file uploads. Same file content + session = same artifact_id.

### Journey Completion Definition

**Journey is considered complete when:**

* File is materialized (`save_materialization` succeeds) **AND** pending parsing journey is created

**Journey completion = file available for parsing (pending journey ready to be resumed).**

---


---

## 3. Scenario 2: Injected Failure

### Test Description
Journey handles failure gracefully when failure is injected at one step. User can see appropriate error and retry.

### Failure Injection Points (Test Each)
- **Option A:** Failure at [first intent] ([failure reason])
- **Option B:** Failure at [second intent] ([failure reason])

### Steps (Example: Failure at [first intent])
1. [ ] User triggers journey ✅
2. [ ] [First intent] intent executes → ❌ **FAILURE INJECTED** ([failure reason])
3. [ ] Journey handles failure gracefully
4. [ ] User sees appropriate error message ("[Error message]")
5. [ ] State remains consistent (no corruption)
6. [ ] User can retry failed step

### Verification
- [ ] Failure handled gracefully (no crash, no unhandled exception)
- [ ] User sees appropriate error message (clear, actionable)
- [ ] State remains consistent (no corruption, completed artifacts remain valid)
- [ ] User can retry failed step
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
- **Steps 1-2:** ✅ Succeed ([first intents])
- **Step 3:** ❌ Fails ([failing intent])
- **Steps 4-5:** Not attempted ([remaining intents])

### Steps
1. [ ] User triggers journey ✅
2. [ ] [First intent] intent executes → ✅ Succeeds ✅
3. [ ] [Second intent] intent executes → ✅ Succeeds ✅
4. [ ] [Third intent] intent executes → ❌ **FAILS** ([failure reason])
5. [ ] Journey handles partial completion
6. [ ] User can retry failed step
7. [ ] Completed steps remain valid
8. [ ] User can proceed after retry succeeds

### Verification
- [ ] Partial state handled correctly (completed artifacts remain valid)
- [ ] User can retry failed step
- [ ] No state corruption (no duplicate artifacts, no inconsistent lifecycle states)
- [ ] Completed artifacts remain valid
- [ ] Failed step can be retried
- [ ] Lifecycle state transitions are monotonic

### Status
⏳ Not tested

**Result:** `[test_result]`

---

## 5. Scenario 4: Retry/Recovery

### Test Description
Journey recovers correctly when user retries after failure. Idempotency ensures no duplicate side effects.

### Retry Pattern
1. Journey fails at [intent]
2. User retries [intent]
3. Journey recovers and completes

### Steps
1. [ ] User triggers journey ✅
2. [ ] [First intent] intent executes → ✅ Succeeds ✅
3. [ ] [Second intent] intent executes → ❌ **FAILS** (first attempt, [failure reason])
4. [ ] User retries [second intent]
5. [ ] [Second intent] intent executes → ✅ **SUCCEEDS** (retry, idempotent)
6. [ ] Journey completes

### Verification
- [ ] Journey recovers correctly (retry succeeds, journey completes)
- [ ] No duplicate state (no duplicate artifacts)
- [ ] State consistency maintained
- [ ] Retry succeeds
- [ ] Journey completes after retry
- [ ] **Idempotency verified** (no duplicate side effects)

### Status
⏳ Not tested

**Result:** `[test_result]`

---

## 6. Scenario 5: Boundary Violation

### Test Description
Journey rejects invalid inputs and maintains state consistency. User sees clear error messages.

### Boundary Violation Points (Test Each)
- **Option A:** Invalid input ([invalid input type])
- **Option B:** Missing required fields ([missing fields])
- **Option C:** Invalid state ([invalid state])

### Steps (Example: Invalid input)
1. [ ] User triggers journey with invalid input
2. [ ] [First intent] intent executes → ❌ **BOUNDARY VIOLATION** ([violation type])
3. [ ] Journey rejects invalid input
4. [ ] User sees validation error message ("[Error message]")
5. [ ] State remains consistent (no partial state)
6. [ ] User can correct input and retry

### Verification
- [ ] Invalid inputs rejected (validation fails)
- [ ] User sees clear validation error messages
- [ ] State remains consistent (no partial state)
- [ ] User can correct input and retry

### Status
⏳ Not tested

**Result:** `[test_result]`

---

## 7. Integration Points

## 2. Scenario 1: Happy Path

### Test Description
Complete upload and materialization journey works end-to-end. File uploaded, saved, and pending parsing journey created.

### Steps
1. [ ] User selects content type (structured/unstructured/hybrid)
2. [ ] User selects file type category (PDF, CSV, Binary, etc.)
3. [ ] User uploads file (and copybook if binary)
4. [ ] `ingest_file` intent executes → File artifact created (`artifact_id`, `artifact_type: "file"`, `lifecycle_state: "PENDING"`)
5. [ ] User clicks "Save File"
6. [ ] `save_materialization` intent executes → File artifact lifecycle transition (`lifecycle_state: "PENDING"` → `"READY"`)
7. [ ] Pending parsing journey created (intent_executions table, status: PENDING)
8. [ ] Ingest type and file type stored in pending intent context
9. [ ] Journey completes successfully
10. [ ] File available for parsing (pending journey ready to be resumed)

### Verification
- [ ] Observable artifacts at each step (artifact_id, artifact_type, lifecycle_state)
- [ ] Artifacts registered in State Surface (ArtifactRegistry)
- [ ] Artifacts indexed in Supabase (artifact_index)
- [ ] Materializations created and stored correctly (GCS)
- [ ] Lifecycle state transitions correctly (`PENDING` → `READY`)
- [ ] **Pending parsing journey created** (intent_executions table)
- [ ] **Ingest type and file type stored in pending intent context**
- [ ] File available for parsing (pending journey can be resumed)

---

## 3. Integration Points

### Platform Services
- **Content Realm:** Intent services (`ingest_file`, `save_materialization`)
- **Journey Realm:** Orchestration services (compose upload journey, create pending parsing journey)
- **State Surface:** Artifact registry and lifecycle management

### Civic Systems
- **Smart City Primitives:** Data Steward (file upload policies), Security Guard (file access policies)
- **Agent Framework:** GuideAgent, Content Liaison Agent

### External Systems
- **GCS:** File storage
- **Supabase:** Artifact index, intent executions table

---

## 4. Testing & Validation

### Business Acceptance Criteria
- [ ] Users can upload files with content type and file type selection
- [ ] Users can save files (materialization)
- [ ] File lifecycle is managed correctly (PENDING → READY)
- [ ] Pending parsing journey created during save
- [ ] Ingest type and file type stored in pending intent context
- [ ] Copybook validation works for binary files

---

## 8. Architectural Verification

### Intent Flow
- [ ] All intents use intent-based API (submitIntent, no direct API calls)
- [ ] All intents flow through Runtime (ExecutionLifecycleManager)
- [ ] All intents have execution_id (tracked via platformState.trackExecution)
- [ ] All intents have parameter validation (before submitIntent)
- [ ] All intents have session validation (validateSession)

### State Authority
- [ ] Runtime is authoritative (frontend syncs with Runtime state)
- [ ] State Surface is authoritative for artifact resolution (resolve_artifact())
- [ ] Artifact Index is authoritative for artifact discovery (list_artifacts())
- [ ] Frontend syncs with Runtime (state.realm.* updated from Runtime)
- [ ] No state divergence (frontend state matches Runtime state)
- [ ] Artifacts persist across steps (artifact_id available in subsequent steps)

### Enforcement
- [ ] All intents have enforcement (Runtime validates parameters)
- [ ] Enforcement prevents violations (direct API calls blocked, invalid parameters rejected)
- [ ] Intentional violations fail (proof tests pass)

### Observability
- [ ] execution_id present in all logs (via Runtime submitIntent)
- [ ] execution_id propagated across intent boundaries (via Runtime execution tracking)
- [ ] Errors include intent + execution_id (via Runtime error handling)
- [ ] Journey trace reconstructable from logs (all execution_ids linked, trace continuity)

---

## 9. SRE Verification

### Error Handling
- [ ] Journey handles network failure ([intent] fails, user can retry)
- [ ] Journey handles storage failure ([intent] fails, user can retry)
- [ ] Journey handles timeout (long-running operations timeout gracefully)

### State Persistence
- [ ] State persists across steps ([artifact_id] available in subsequent steps)
- [ ] State persists across refresh ([artifact_id] persists after browser refresh)
- [ ] State persists across navigation ([artifact_id] persists when navigating away and back)

### Boundaries
- [ ] Browser → Frontend boundary works ([operation] from browser to frontend)
- [ ] Frontend → Backend boundary works (submitIntent from frontend to Runtime)
- [ ] Backend → Runtime boundary works (Runtime executes intents)
- [ ] Runtime → Realm boundary works (Runtime calls Realm handlers)
- [ ] Realm → State Surface boundary works (Realm registers artifacts in ArtifactRegistry)
- [ ] Realm → Artifact Index boundary works (Realm indexes artifacts in Supabase artifact_index)

---

## 10. Gate Status

**Journey is "done" only when:**
- [ ] ✅ Happy path works
- [ ] ✅ Injected failure handled (all failure points tested)
- [ ] ✅ Partial success handled
- [ ] ✅ Retry/recovery works (with idempotency verified)
- [ ] ✅ Boundary violation rejected (all violation types tested)
- [ ] ✅ Architectural verification passes
- [ ] ✅ Observability guarantees met
- [ ] ✅ SRE verification passes (error handling, state persistence, boundaries)

**Current Status:** ⏳ **IN PROGRESS**

**Next Steps:**
1. ⏭️ **NEXT:** Enhance with implementation-specific details
2. ⏭️ **NEXT:** Add real infrastructure testing
3. ⏭️ **NEXT:** Browser E2E tests
4. ⏭️ **NEXT:** Production readiness testing


---

**Last Updated:** January 27, 2026  
**Owner:** Content Realm Solution Team
