# Journey Contract: Coexistence Analysis

**Journey:** Coexistence Analysis  
**Journey ID:** `journey_journey_coexistence_analysis`  
**Solution:** Journey Realm Solution  
**Status:** ⏳ **IN PROGRESS**  
**Priority:** 🔴 **PRIORITY 1** - Foundation journey for Journey Realm

---

## 1. Journey Overview

### Intents in Journey
1. `analyze_coexistence` - Step 1: Analyze SOP and workflow for coexistence opportunities
2. `identify_opportunities` - Step 2: Identify specific coexistence opportunities and recommendations

**Note:** This journey analyzes coexistence between SOP and workflow. Blueprint creation is a separate journey (`journey_journey_create_coexistence_blueprint`) that follows this analysis.

### Journey Flow
```
[User selects both SOP and workflow files]
    ↓
[User clicks "Analyze Coexistence"]
    ↓
[analyze_coexistence] → analysis_results_artifact (artifact_id, artifact_type: "coexistence_analysis", lifecycle_state: "PENDING")
    - Analyzes SOP and workflow for coexistence opportunities
    - Identifies gaps, conflicts, and alignment opportunities
    - Registered in State Surface with lineage
    - Indexed in Supabase with lineage metadata
    ↓
[identify_opportunities] → Opportunities identified
    - Specific coexistence opportunities listed
    - Recommendations generated
    - Analysis results updated
    ↓
[Journey Complete]
    ↓
[User can proceed to create blueprint (separate journey)]
```

### Expected Observable Artifacts
- **Step 1 (analyze_coexistence):** 
  - `artifact_id` (artifact_type: "coexistence_analysis")
  - `parent_artifacts: [sop_artifact_id, workflow_artifact_id]` (lineage)
  - `lifecycle_state: "PENDING"`
  - `analysis_results` (gaps, conflicts, alignment opportunities)
  - Artifact registered in State Surface with lineage
  - Artifact indexed in Supabase with lineage metadata
- **Step 2 (identify_opportunities):** 
  - Opportunities identified
  - Recommendations generated
  - Analysis results updated

### Artifact Lifecycle State Transitions
- **Step 1:** Analysis artifact created with `lifecycle_state: "PENDING"` (Working Material)
- **Step 2:** Analysis artifact updated with opportunities and recommendations

### Idempotency Scope (Per Intent)

| Intent                  | Idempotency Key                                    | Scope                    |
| ----------------------- | -------------------------------------------------- | ------------------------ |
| `analyze_coexistence`   | `analysis_fingerprint` (hash(sop_artifact_id + workflow_artifact_id)) | per SOP-workflow pair    |
| `identify_opportunities` | `opportunities_fingerprint` (hash(analysis_artifact_id)) | per analysis artifact    |

**Note:** Idempotency keys prevent duplicate analysis. Same SOP + workflow = same analysis artifact.

### Journey Completion Definition

**Journey is considered complete when:**

* Coexistence analysis is complete and opportunities are identified (`analyze_coexistence` succeeds, `identify_opportunities` succeeds)

**Journey completion = analysis results available for blueprint creation.**

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
Complete coexistence analysis journey works end-to-end. User analyzes SOP and workflow, opportunities identified.

### Steps
1. [ ] User selects both SOP and workflow files
2. [ ] User clicks "Analyze Coexistence"
3. [ ] `analyze_coexistence` intent executes → Analysis artifact created (`artifact_id`, `artifact_type: "coexistence_analysis"`, `parent_artifacts: [sop_artifact_id, workflow_artifact_id]`, `lifecycle_state: "PENDING"`)
   - Gaps, conflicts, and alignment opportunities identified
4. [ ] `identify_opportunities` intent executes → Opportunities identified, recommendations generated
5. [ ] Journey completes successfully
6. [ ] Analysis results available for blueprint creation

### Verification
- [ ] Observable artifacts at each step (artifact_id, artifact_type, lifecycle_state, parent_artifacts)
- [ ] Artifacts registered in State Surface (ArtifactRegistry) with lineage
- [ ] Artifacts indexed in Supabase (artifact_index) with lineage metadata
- [ ] Gaps, conflicts, and alignment opportunities identified correctly
- [ ] Opportunities and recommendations generated correctly
- [ ] Analysis results available for blueprint creation

---

## 3. Integration Points

### Platform Services
- **Journey Realm:** Intent services (`analyze_coexistence`, `identify_opportunities`)
- **Journey Realm:** Orchestration services (compose analysis journey)
- **State Surface:** Artifact registry and lifecycle management

### Civic Systems
- **Smart City Primitives:** Data Steward (analysis storage policies)
- **Agent Framework:** GuideAgent, Journey Liaison Agent

### External Systems
- **Supabase:** Artifact index

---

## 4. Testing & Validation

### Business Acceptance Criteria
- [ ] Users can analyze coexistence between SOP and workflow
- [ ] Gaps, conflicts, and alignment opportunities identified correctly
- [ ] Opportunities and recommendations generated correctly
- [ ] Analysis results available for blueprint creation

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
**Owner:** Journey Realm Solution Team
