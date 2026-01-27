# Journey Contract: File Parsing

**Journey:** File Parsing  
**Journey ID:** `journey_content_file_parsing`  
**Solution:** Content Realm Solution  
**Status:** ⏳ **IN PROGRESS**  
**Priority:** 🔴 **PRIORITY 1** - Foundation journey for Content Realm

---

## 1. Journey Overview

### Intents in Journey
1. `parse_content` - Step 1: Resume pending parsing journey, parse file using ingest type and file type from intent context
2. `save_parsed_content` - Step 2: Save parsed content as artifact

**Note:** This journey **resumes** a pending parsing journey that was created during `save_materialization`. The ingest type and file type are retrieved from the pending intent context, so the user does not need to re-select them.

### Journey Flow
```
[User selects uploaded file from dropdown]
    ↓
[System identifies pending parsing journey for this file]
    ↓
[User clicks "Parse File"]
    ↓
[parse_content] → parsed_content_artifact (artifact_id, artifact_type: "parsed_content", parent_artifacts: [file_artifact_id], lifecycle_state: "PENDING")
    - **Retrieves ingest type and file type from pending intent context** (intent_executions table)
    - Uses ingest type and file type to select appropriate parser
    - Parses file content
    - Registered in State Surface with lineage
    - Indexed in Supabase with lineage metadata
    - Materialization in GCS (parsed JSON)
    - Pending parsing journey status: COMPLETED
    ↓
[save_parsed_content] → Parsed content artifact saved
    - Artifact Registry updated (State Surface)
    - Artifact Index updated (Supabase)
    - Parsed content available for embedding creation
    ↓
[Journey Complete]
```

### Expected Observable Artifacts
- **Step 1 (parse_content):** 
  - `artifact_id` (artifact_type: "parsed_content")
  - `parent_artifacts: [file_artifact_id]` (lineage)
  - `lifecycle_state: "PENDING"`
  - `structure`, `chunks`
  - `materializations` array (GCS JSON)
  - **Ingest type and file type retrieved from pending intent context**
  - Artifact registered in State Surface with lineage
  - Artifact indexed in Supabase with lineage metadata
  - Pending parsing journey status: COMPLETED
- **Step 2 (save_parsed_content):** 
  - Parsed content artifact saved
  - Artifact Registry updated (State Surface)
  - Artifact Index updated (Supabase)

### Artifact Lifecycle State Transitions
- **Step 1:** Parsed content artifact created with `lifecycle_state: "PENDING"` (Working Material)
- **Step 2:** Parsed content artifact saved (available for embedding creation)

### Idempotency Scope (Per Intent)

| Intent               | Idempotency Key                                    | Scope                    |
| -------------------- | -------------------------------------------------- | ------------------------ |
| `parse_content`      | `parsing_fingerprint` (hash(artifact_id + ingest_type + file_type)) | per artifact, per parse config |
| `save_parsed_content` | `parsed_content_fingerprint` (hash(artifact_id + boundary_contract_id)) | per artifact, per boundary contract |

**Note:** Idempotency keys prevent duplicate parsing. Same file + ingest type + file type = same parsed content artifact.

### Journey Completion Definition

**Journey is considered complete when:**

* File is parsed and parsed content is saved (`parse_content` succeeds, `save_parsed_content` succeeds)

**Journey completion = parsed content available for embedding creation.**

---

## 2. Scenario 1: Happy Path

### Test Description
Complete parsing journey works end-to-end. User selects file, resumes pending journey, file parsed successfully.

### Steps
1. [ ] User selects uploaded file from dropdown
2. [ ] System identifies pending parsing journey for this file (intent_executions table, status: PENDING)
3. [ ] System retrieves ingest type and file type from pending intent context
4. [ ] User clicks "Parse File"
5. [ ] `parse_content` intent executes → Parsed content artifact created (`artifact_id`, `artifact_type: "parsed_content"`, `parent_artifacts: [file_artifact_id]`, `lifecycle_state: "PENDING"`)
   - **Ingest type and file type retrieved from pending intent context**
   - Appropriate parser selected based on ingest type and file type
6. [ ] `save_parsed_content` intent executes → Parsed content saved
7. [ ] Pending parsing journey status: COMPLETED
8. [ ] Journey completes successfully
9. [ ] Parsed content available for embedding creation

### Verification
- [ ] Observable artifacts at each step (artifact_id, artifact_type, lifecycle_state, parent_artifacts)
- [ ] Artifacts registered in State Surface (ArtifactRegistry) with lineage
- [ ] Artifacts indexed in Supabase (artifact_index) with lineage metadata
- [ ] **Pending parsing journey identified correctly**
- [ ] **Ingest type and file type retrieved from pending intent context**
- [ ] Appropriate parser selected based on ingest type and file type
- [ ] Parsed content saved correctly
- [ ] Pending parsing journey status: COMPLETED

---

## 3. Scenario 2: Injected Failure

### Test Description
Journey handles failure gracefully when failure is injected at one step. User can see appropriate error and retry.

### Failure Injection Points (Test Each)
- **Option A:** Failure at `parse_content` (parsing error, unsupported file type, parser unavailable)
- **Option B:** Failure at `save_parsed_content` (storage failure, Supabase unavailable)

### Steps (Example: Failure at parse_content)
1. [ ] User selects uploaded file from dropdown ✅
2. [ ] System identifies pending parsing journey ✅
3. [ ] System retrieves ingest type and file type from pending intent context ✅
4. [ ] User clicks "Parse File"
5. [ ] `parse_content` intent executes → ❌ **FAILURE INJECTED** (parsing error)
6. [ ] Journey handles failure gracefully
7. [ ] User sees appropriate error message ("File parsing failed: [reason]")
8. [ ] State remains consistent (file artifact still valid, lifecycle_state: "READY", no corruption)
9. [ ] Pending parsing journey remains in PENDING status (can be resumed)
10. [ ] User can retry parsing

### Verification
- [ ] Failure handled gracefully (no crash, no unhandled exception)
- [ ] User sees appropriate error message (clear, actionable)
- [ ] State remains consistent (no corruption, completed artifacts remain valid)
- [ ] Pending parsing journey remains in PENDING status (can be resumed)
- [ ] User can retry parsing

---

## 4. Integration Points

### Platform Services
- **Content Realm:** Intent services (`parse_content`, `save_parsed_content`)
- **Journey Realm:** Orchestration services (resume pending parsing journey)
- **State Surface:** Artifact registry and lifecycle management
- **Intent Executions:** Retrieve pending intent context (ingest type, file type)

### Civic Systems
- **Smart City Primitives:** Data Steward (parsing policies), Security Guard (file access policies)
- **Agent Framework:** GuideAgent, Content Liaison Agent

### External Systems
- **GCS:** Parsed content storage
- **Supabase:** Artifact index, intent executions table

---

## 5. Testing & Validation

### Business Acceptance Criteria
- [ ] Users can parse files by resuming pending parsing journeys
- [ ] Ingest type and file type retrieved from pending intent context
- [ ] Appropriate parser selected based on ingest type and file type
- [ ] Parsed content saved correctly
- [ ] Pending parsing journey completed after successful parsing
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
