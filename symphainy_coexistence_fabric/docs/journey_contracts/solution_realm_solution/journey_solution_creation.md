# Journey Contract: Solution Creation

**Journey:** Solution Creation  
**Journey ID:** `journey_solution_creation`  
**Solution:** Solution Realm Solution  
**Status:** ✅ **IMPLEMENTED**  
**Priority:** 🔴 **PRIORITY 1** - Foundation journey

---

## 1. Journey Overview

### Purpose
Create a platform solution from an existing artifact (roadmap, POC, or blueprint). The platform solution is registered with domain bindings and intents, enabling it to be deployed and executed within the Symphainy platform.

### Intents in Journey

| Step | Intent | Description |
|------|--------|-------------|
| 1 | `create_solution` | Create platform solution from artifact |

### Journey Flow
```
[User selects source artifact (roadmap, POC, or blueprint)]
    ↓
[Frontend calls OutcomesAPIManager.createSolution(source, sourceId, sourceData)]
    ↓
[create_solution intent submitted to Runtime]
    ↓
[OutcomesOrchestrator._handle_create_solution()]
    ↓
[Validate solution_source and source_id]
    ↓
[Retrieve source artifact from Artifact Plane]
    ↓
[SolutionSynthesisService.create_solution_from_artifact()]
    ↓
[Generate solution_id and register solution]
    ↓
[Return solution with domain bindings and intents]
    ↓
[Frontend updates realm state with solution]
    ↓
[Journey Complete]
```

### Expected Observable Artifacts
- `platform_solution` - Registered platform solution
  - `solution_id`: Unique identifier
  - `name`: Solution name
  - `description`: Solution description
  - `domain_bindings`: Array of domain/system/adapter mappings
  - `intents`: Array of supported intents
  - `metadata`: Additional solution metadata

### Artifact Lifecycle State Transitions
- Solution artifact created with lifecycle state: `READY`
- Registered in Solution Registry

### Idempotency Scope (Per Intent)

| Intent | Idempotency Key | Scope |
|--------|-----------------|-------|
| `create_solution` | `hash(solution_source + source_id + session_id)` | Per source artifact - regenerates each time |

### Journey Completion Definition

**Journey is considered complete when:**
- Source artifact retrieved from Artifact Plane
- SolutionSynthesisService creates solution from artifact
- Solution registered with solution_id
- Frontend realm state updated with solution reference

---

## 2. Scenario 1: Happy Path

### Test Description
Complete journey works end-to-end without failures.

### Prerequisites
- Valid session with tenant_id and session_id
- Source artifact exists in Artifact Plane (roadmap, POC, or blueprint)
- Source artifact ID known

### Steps
1. [x] User selects source type: "roadmap", "poc", or "blueprint"
2. [x] User provides source_id of existing artifact
3. [x] User clicks "Create Solution" button
4. [x] `create_solution` intent executes with solution_source, source_id, source_data
5. [x] Source artifact retrieved from Artifact Plane
6. [x] SolutionSynthesisService creates platform solution
7. [x] Solution registered with domain bindings
8. [x] Frontend displays solution details

### Verification
- [x] Observable artifacts: platform_solution with solution_id
- [x] Solution includes domain_bindings and intents
- [x] Frontend state updated: `outcomes.solutions[solution_id]`
- [x] Event emitted: `solution_created`

### Status
✅ Tested and working

---

## 3. Scenario 2: Injected Failure

### Test Description
Journey handles failure gracefully when solution creation fails.

### Failure Injection Points (Test Each)
- **Option A:** Missing solution_source or source_id (validation failure)
- **Option B:** Invalid solution_source (not roadmap/poc/blueprint)
- **Option C:** Source artifact not found in Artifact Plane
- **Option D:** SolutionSynthesisService fails

### Steps (Example: Source not found)
1. [x] User provides invalid source_id ✅
2. [x] `create_solution` intent executes
3. [x] Artifact Plane lookup fails → tries execution state fallback
4. [x] Execution state lookup fails → ❌ **FAILURE**
5. [x] Journey returns error: "Source {type} with id {id} not found"
6. [x] User can select valid artifact and retry

### Verification
- [x] Missing artifact detected and reported
- [x] Clear error message with source type and id
- [x] Execution state fallback attempted
- [x] State remains consistent
- [x] User can retry with valid artifact

### Status
✅ Tested - graceful error handling with fallback attempts

---

## 4. Scenario 3: Partial Success

### Test Description
N/A - Single intent journey. Partial success not applicable.

---

## 5. Scenario 4: Retry/Recovery

### Test Description
Journey recovers correctly when user retries after failure.

### Steps
1. [x] User triggers solution creation → ❌ **FAILS** (artifact not found)
2. [x] User ensures artifact exists (creates roadmap/POC/blueprint first)
3. [x] User clicks "Create Solution" again with valid source_id
4. [x] `create_solution` intent executes → ✅ **SUCCEEDS**
5. [x] Journey completes

### Verification
- [x] Journey recovers correctly after artifact creation
- [x] Solution created successfully
- [x] Retry succeeds

### Status
✅ Tested

---

## 6. Scenario 5: Boundary Violation

### Test Description
Journey rejects invalid inputs.

### Boundary Violation Points
- **Option A:** No session (session_id or tenant_id missing)
- **Option B:** Missing solution_source or source_id
- **Option C:** Invalid solution_source value

### Steps (Example: Invalid solution_source)
1. [x] User triggers solution creation with solution_source: "invalid"
2. [x] `create_solution` intent executes → ❌ **BOUNDARY VIOLATION**
3. [x] Journey rejects request: "Invalid solution_source: invalid. Must be 'roadmap', 'poc', or 'blueprint'"
4. [x] User can select valid source type and retry

### Verification
- [x] Invalid solution_source rejected with clear error message
- [x] Valid values listed in error message
- [x] State remains consistent
- [x] User can correct issue and retry

### Status
✅ Tested

---

## 7. Integration Points

### Platform Services
- **Outcomes Realm:** `OutcomesOrchestrator._handle_create_solution()`
- **Artifact Plane:** Artifact retrieval
- **Solution Registry:** Solution registration
- **Runtime:** ExecutionLifecycleManager for intent execution

### Enabling Services
- `SolutionSynthesisService.create_solution_from_artifact()`

### Frontend
- `OutcomesAPIManager.createSolution(solutionSource, sourceId, sourceData, solutionOptions)`

---

## 8. Architectural Verification

### Intent Flow
- [x] All intents use intent-based API (submitIntent)
- [x] All intents flow through Runtime
- [x] All intents have execution_id
- [x] Parameter validation: solution_source, source_id required

### State Authority
- [x] Artifact Plane is authoritative for source artifacts
- [x] Solution Registry for solution registration
- [x] Frontend syncs solution reference after completion

### Artifact Retrieval Pattern
- [x] Primary: Artifact Plane lookup
- [x] Fallback: Execution state lookup (backward compatibility)
- [x] Clear error if both fail

### Observability
- [x] execution_id present in all logs
- [x] Detailed logging for retrieval attempts
- [x] Telemetry recorded

---

## 9. SRE Verification

### Error Handling
- [x] Missing artifact provides clear error with ID
- [x] Fallback attempts logged
- [x] Validation errors provide actionable messages

### State Persistence
- [x] Solution registered in Solution Registry
- [x] solution_id enables retrieval
- [x] Frontend caches solution reference

### Boundaries
- [x] Browser → Frontend: "Create Solution" with source selection
- [x] Frontend → Backend: submitIntent("create_solution", { solution_source, source_id, source_data })
- [x] Backend → Runtime: ExecutionLifecycleManager.execute()
- [x] Runtime → Realm: OutcomesOrchestrator.handle_intent()
- [x] Realm → Artifact Plane: get_artifact()
- [x] Realm → Solution Registry: register_solution()

---

## 10. Gate Status

**Journey is "done" only when:**
- [x] ✅ Happy path works
- [x] ✅ Injected failure handled
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
**Implementation:** `symphainy_platform/realms/outcomes/orchestrators/outcomes_orchestrator.py::_handle_create_solution`  
**Frontend:** `symphainy-frontend/shared/managers/OutcomesAPIManager.ts::createSolution()`
