# Journey Contract: Coexistence Blueprint Creation

**Journey:** Coexistence Blueprint Creation  
**Journey ID:** `journey_journey_create_coexistence_blueprint`  
**Solution:** Journey Realm Solution  
**Status:** ⏳ **IN PROGRESS**  
**Priority:** 🔴 **PRIORITY 1** - Foundation journey for Journey Realm

---

## 1. Journey Overview

### Intents in Journey
1. `create_blueprint` - Step 1: Create coexistence blueprint from analysis results
2. `save_blueprint` - Step 2: Save blueprint as artifact

**Note:** This journey creates a blueprint artifact from coexistence analysis results. It follows the Coexistence Analysis journey and generates an optimized blueprint with metrics (efficiency gain, time savings, cost reduction).

### Journey Flow
```
[User has completed coexistence analysis]
    ↓
[User clicks "Optimize Coexistence" or "Create Blueprint"]
    ↓
[create_blueprint] → blueprint_artifact (artifact_id, artifact_type: "coexistence_blueprint", lifecycle_state: "PENDING")
    - Takes coexistence analysis results (SOP, workflow, opportunities)
    - Generates optimized SOP and workflow
    - Calculates metrics (efficiency gain, time savings, cost reduction)
    - Creates blueprint visualization
    - Registered in State Surface with lineage
    - Indexed in Supabase with lineage metadata
    - Materialization in GCS (blueprint JSON)
    ↓
[User clicks "Save Blueprint"]
    ↓
[save_blueprint] → Blueprint artifact saved
    - Artifact Registry updated (State Surface)
    - Artifact Index updated (Supabase)
    - Blueprint available for viewing and export
    ↓
[Journey Complete]
```

### Expected Observable Artifacts
- **Step 1 (create_blueprint):** 
  - `artifact_id` (artifact_type: "coexistence_blueprint")
  - `parent_artifacts: [sop_artifact_id, workflow_artifact_id]` (lineage)
  - `lifecycle_state: "PENDING"`
  - `optimized_sop`, `optimized_workflow`
  - `metrics` (efficiency_gain, time_savings, cost_reduction)
  - `blueprint_visualization`
  - `materializations` array (GCS JSON)
  - Artifact registered in State Surface with lineage
  - Artifact indexed in Supabase with lineage metadata
- **Step 2 (save_blueprint):** 
  - Blueprint artifact saved
  - Artifact Registry updated (State Surface)
  - Artifact Index updated (Supabase)

### Artifact Lifecycle State Transitions
- **Step 1:** Blueprint artifact created with `lifecycle_state: "PENDING"` (Working Material)
- **Step 2:** Blueprint artifact saved (available for viewing and export)

### Idempotency Scope (Per Intent)

| Intent               | Idempotency Key                                    | Scope                    |
| -------------------- | -------------------------------------------------- | ------------------------ |
| `create_blueprint`   | `blueprint_fingerprint` (hash(sop_artifact_id + workflow_artifact_id + analysis_results)) | per SOP-workflow pair    |
| `save_blueprint`      | `blueprint_save_fingerprint` (hash(artifact_id + boundary_contract_id)) | per artifact, per boundary contract |

**Note:** Idempotency keys prevent duplicate blueprint creation. Same SOP + workflow + analysis = same blueprint artifact.

### Journey Completion Definition

**Journey is considered complete when:**

* Blueprint is created and saved (`create_blueprint` succeeds, `save_blueprint` succeeds)

**Journey completion = blueprint available for viewing and export.**

---

## 2. Scenario 1: Happy Path

### Test Description
Complete blueprint creation journey works end-to-end. User creates blueprint from analysis results, saves it successfully.

### Steps
1. [ ] User has completed coexistence analysis (SOP and workflow analyzed)
2. [ ] User clicks "Optimize Coexistence" or "Create Blueprint"
3. [ ] `create_blueprint` intent executes → Blueprint artifact created (`artifact_id`, `artifact_type: "coexistence_blueprint"`, `parent_artifacts: [sop_artifact_id, workflow_artifact_id]`, `lifecycle_state: "PENDING"`)
   - Optimized SOP and workflow generated
   - Metrics calculated (efficiency gain, time savings, cost reduction)
   - Blueprint visualization created
4. [ ] User clicks "Save Blueprint"
5. [ ] `save_blueprint` intent executes → Blueprint saved
6. [ ] Journey completes successfully
7. [ ] Blueprint available for viewing and export

### Verification
- [ ] Observable artifacts at each step (artifact_id, artifact_type, lifecycle_state, parent_artifacts)
- [ ] Artifacts registered in State Surface (ArtifactRegistry) with lineage
- [ ] Artifacts indexed in Supabase (artifact_index) with lineage metadata
- [ ] Optimized SOP and workflow generated correctly
- [ ] Metrics calculated correctly (efficiency gain, time savings, cost reduction)
- [ ] Blueprint visualization created
- [ ] Blueprint saved correctly

---

## 3. Scenario 2: Injected Failure

### Test Description
Journey handles failure gracefully when failure is injected at one step. User can see appropriate error and retry.

### Failure Injection Points (Test Each)
- **Option A:** Failure at `create_blueprint` (analysis results invalid, optimization service unavailable)
- **Option B:** Failure at `save_blueprint` (storage failure, Supabase unavailable)

### Steps (Example: Failure at create_blueprint)
1. [ ] User has completed coexistence analysis ✅
2. [ ] User clicks "Create Blueprint"
3. [ ] `create_blueprint` intent executes → ❌ **FAILURE INJECTED** (optimization service unavailable)
4. [ ] Journey handles failure gracefully
5. [ ] User sees appropriate error message ("Blueprint creation failed: [reason]")
6. [ ] State remains consistent (analysis results still valid, no corruption)
7. [ ] User can retry blueprint creation

### Verification
- [ ] Failure handled gracefully (no crash, no unhandled exception)
- [ ] User sees appropriate error message (clear, actionable)
- [ ] State remains consistent (no corruption, analysis results remain valid)
- [ ] User can retry blueprint creation

---

## 4. Integration Points

### Platform Services
- **Journey Realm:** Intent services (`create_blueprint`, `save_blueprint`)
- **Journey Realm:** Orchestration services (compose blueprint creation journey)
- **State Surface:** Artifact registry and lifecycle management

### Civic Systems
- **Smart City Primitives:** Data Steward (blueprint storage policies), Security Guard (blueprint access policies)
- **Agent Framework:** GuideAgent, Journey Liaison Agent

### External Systems
- **GCS:** Blueprint storage
- **Supabase:** Artifact index

---

## 5. Testing & Validation

### Business Acceptance Criteria
- [ ] Users can create blueprints from coexistence analysis results
- [ ] Optimized SOP and workflow generated correctly
- [ ] Metrics calculated correctly (efficiency gain, time savings, cost reduction)
- [ ] Blueprint visualization created
- [ ] Blueprint saved correctly
- [ ] Blueprint available for viewing and export

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
