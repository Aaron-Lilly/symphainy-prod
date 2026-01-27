# Journey Contract: POC Proposal Creation

**Journey:** POC Proposal Creation  
**Journey ID:** `journey_solution_poc_proposal`  
**Solution:** Solution Realm Solution  
**Status:** ✅ **IMPLEMENTED**  
**Priority:** 🔴 **PRIORITY 1** - Foundation journey

---

## 1. Journey Overview

### Purpose
Create a Proof of Concept (POC) proposal from a user-provided description. The POC proposal includes objectives, scope, deliverables, timeline, and visualization. The generated POC is stored in the Artifact Plane for retrieval and can be used to create a platform solution.

### Intents in Journey

| Step | Intent | Description |
|------|--------|-------------|
| 1 | `create_poc` | Create POC proposal from description |

### Journey Flow
```
[User provides POC description and clicks "Create POC"]
    ↓
[Frontend calls OutcomesAPIManager.createPOC(description)]
    ↓
[create_poc intent submitted to Runtime]
    ↓
[OutcomesOrchestrator._handle_create_poc()]
    ↓
[Validate description is non-empty]
    ↓
[POCGenerationAgent.process_request() OR POCGenerationService.generate_poc_proposal()]
    ↓
[Generate poc_id/proposal_id (UUID)]
    ↓
[VisualGenerationService.generate_poc_visual() - optional]
    ↓
[Store artifact in Artifact Plane]
    ↓
[Return structured artifact with poc_id reference]
    ↓
[Frontend updates realm state with POC]
    ↓
[Journey Complete]
```

### Expected Observable Artifacts
- `poc` - POC proposal artifact stored in Artifact Plane
  - `poc_id` / `proposal_id`: Unique identifier
  - `description`: User-provided description
  - `status`: Generation status
  - `objectives`: Array of objectives
  - `scope`: Scope definition
  - `deliverables`: Array of deliverables
  - `estimated_duration_weeks`: Timeline estimate
  - `poc_visual`: Optional visualization (image_base64, storage_path)

### Artifact Lifecycle State Transitions
- POC artifact created with lifecycle state: `READY`
- Stored in Artifact Plane with metadata: `regenerable: true`, `retention_policy: session`

### Idempotency Scope (Per Intent)

| Intent | Idempotency Key | Scope |
|--------|-----------------|-------|
| `create_poc` | `hash(description + session_id)` | Per description input - regenerates each time |

### Journey Completion Definition

**Journey is considered complete when:**
- Description validated (non-empty string)
- POCGenerationAgent/Service generates POC proposal
- POC stored in Artifact Plane
- poc_id returned to frontend
- Frontend realm state updated with POC reference

---

## 2. Scenario 1: Happy Path

### Test Description
Complete journey works end-to-end without failures.

### Prerequisites
- Valid session with tenant_id and session_id
- User provides POC description

### Steps
1. [x] User enters POC description (e.g., "Migrate legacy insurance system to cloud")
2. [x] User clicks "Create POC" button
3. [x] `create_poc` intent executes with description parameter
4. [x] POCGenerationAgent generates POC proposal
5. [x] POC visualization generated (optional)
6. [x] Artifact stored in Artifact Plane
7. [x] Frontend displays POC with objectives, scope, deliverables

### Verification
- [x] Observable artifacts: poc with poc_id/proposal_id
- [x] Artifact stored in Artifact Plane (not execution state)
- [x] POC includes objectives, scope, deliverables, timeline
- [x] Frontend state updated: `outcomes.pocProposals[poc_id]`
- [x] Event emitted: `poc_proposal_created`

### Status
✅ Tested and working

---

## 3. Scenario 2: Injected Failure

### Test Description
Journey handles failure gracefully when POC generation fails.

### Failure Injection Points (Test Each)
- **Option A:** Empty description (validation failure)
- **Option B:** POCGenerationAgent fails (LLM timeout)
- **Option C:** Artifact Plane storage fails

### Steps (Example: Agent failure)
1. [x] User provides description and triggers creation ✅
2. [x] `create_poc` intent executes
3. [x] POCGenerationAgent.process_request() → ❌ **FAILURE INJECTED** (LLM timeout)
4. [x] Fallback to POCGenerationService
5. [x] Fallback result includes: `generation_mode: "agent_fallback"`, `confidence: "degraded"`
6. [x] Journey completes with degraded confidence

### Verification
- [x] Failure handled gracefully (fallback to service)
- [x] Fallback maintains same semantic contract
- [x] User sees POC (with degraded confidence indicator)
- [x] State remains consistent
- [x] User can retry for full-confidence result

### Status
✅ Tested - graceful fallback to service with semantic contract compliance

---

## 4. Scenario 3: Partial Success

### Test Description
N/A - Single intent journey. Partial success not applicable.

### Notes
- Visual generation failure is non-blocking (POC still saved)
- Artifact Plane failure falls back to execution state (logged as warning)

---

## 5. Scenario 4: Retry/Recovery

### Test Description
Journey recovers correctly when user retries after failure.

### Steps
1. [x] User triggers POC creation → ❌ **FAILS** (first attempt)
2. [x] User clicks "Create POC" again with same/modified description
3. [x] `create_poc` intent executes → ✅ **SUCCEEDS** (retry)
4. [x] New POC generated with new poc_id
5. [x] Journey completes

### Verification
- [x] Journey recovers correctly
- [x] New poc_id generated (not idempotent)
- [x] Retry succeeds
- [x] Journey completes after retry

### Status
✅ Tested

---

## 6. Scenario 5: Boundary Violation

### Test Description
Journey rejects invalid inputs.

### Boundary Violation Points
- **Option A:** No session (session_id or tenant_id missing)
- **Option B:** Empty description
- **Option C:** Description too short

### Steps (Example: Empty description)
1. [x] User triggers POC creation with empty description
2. [x] `create_poc` intent executes → ❌ **BOUNDARY VIOLATION**
3. [x] Journey rejects request: "Description is required for POC creation"
4. [x] User can add description and retry

### Verification
- [x] Empty description rejected with clear error message
- [x] Validation happens in both frontend and backend
- [x] State remains consistent
- [x] User can correct issue and retry

### Status
✅ Tested

---

## 7. Integration Points

### Platform Services
- **Outcomes Realm:** `OutcomesOrchestrator._handle_create_poc()`
- **Artifact Plane:** Artifact storage and retrieval
- **Runtime:** ExecutionLifecycleManager for intent execution

### Enabling Services
- `POCGenerationService.generate_poc_proposal()`
- `VisualGenerationService.generate_poc_visual()`

### Agents
- `POCGenerationAgent.process_request()` - primary, falls back to service on failure

### Frontend
- `OutcomesAPIManager.createPOC(description, pocOptions)`
- `ensureArtifactLifecycle()` - adds lifecycle state

---

## 8. Architectural Verification

### Intent Flow
- [x] All intents use intent-based API (submitIntent)
- [x] All intents flow through Runtime
- [x] All intents have execution_id
- [x] Parameter validation: description required

### State Authority
- [x] Artifact Plane is authoritative for POC storage
- [x] Frontend syncs POC reference after completion
- [x] poc_id enables retrieval across sessions

### Semantic Contract Compliance
- [x] Agent fallback produces same semantic contract
- [x] Fallback includes: `generation_mode: "agent_fallback"`, `confidence: "degraded"`
- [x] Frontend can distinguish between agent and fallback results

### Observability
- [x] execution_id present in all logs
- [x] Telemetry recorded
- [x] Health monitoring active

---

## 9. SRE Verification

### Error Handling
- [x] Agent failure falls back to service (with semantic contract)
- [x] Artifact Plane failure falls back to execution state
- [x] Visual generation failure is non-blocking

### State Persistence
- [x] POC persists in Artifact Plane
- [x] poc_id enables retrieval
- [x] Frontend caches POC reference

### Boundaries
- [x] Browser → Frontend: "Create POC" with description
- [x] Frontend → Backend: submitIntent("create_poc", { description })
- [x] Backend → Runtime: ExecutionLifecycleManager.execute()
- [x] Runtime → Realm: OutcomesOrchestrator.handle_intent()
- [x] Realm → Artifact Plane: create_artifact()

---

## 10. Gate Status

**Journey is "done" only when:**
- [x] ✅ Happy path works
- [x] ✅ Injected failure handled (with fallback)
- [x] ✅ N/A - Partial success
- [x] ✅ Retry/recovery works
- [x] ✅ Boundary violation rejected
- [x] ✅ Architectural verification passes
- [x] ✅ Observability guarantees met
- [x] ✅ SRE verification passes

**Current Status:** ✅ **IMPLEMENTED**

---

**Last Updated:** January 27, 2026  
**Owner:** Solution Realm Solution Team  
**Implementation:** `symphainy_platform/realms/outcomes/orchestrators/outcomes_orchestrator.py::_handle_create_poc`  
**Frontend:** `symphainy-frontend/shared/managers/OutcomesAPIManager.ts::createPOC()`
