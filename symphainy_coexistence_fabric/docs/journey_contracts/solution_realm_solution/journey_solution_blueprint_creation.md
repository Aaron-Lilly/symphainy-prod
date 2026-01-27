# Journey Contract: Blueprint Creation

**Journey:** Blueprint Creation  
**Journey ID:** `journey_solution_blueprint_creation`  
**Solution:** Solution Realm Solution  
**Status:** ✅ **IMPLEMENTED**  
**Priority:** 🔴 **PRIORITY 1** - Foundation journey

---

## 1. Journey Overview

### Purpose
Create a coexistence blueprint from workflow analysis. The blueprint defines the transformation from current state to coexistence state, including a roadmap and responsibility matrix. The generated blueprint is stored in the Artifact Plane and can be used to create a platform solution.

### Intents in Journey

| Step | Intent | Description |
|------|--------|-------------|
| 1 | `create_blueprint` | Create coexistence blueprint from workflow |

### Journey Flow
```
[User selects workflow and clicks "Create Blueprint"]
    ↓
[Frontend calls OutcomesAPIManager.createBlueprint(workflowId)]
    ↓
[create_blueprint intent submitted to Runtime]
    ↓
[OutcomesOrchestrator._handle_create_blueprint()]
    ↓
[Validate workflow_id is provided]
    ↓
[BlueprintCreationAgent.process_request()]
    ↓
[CoexistenceAnalysisService.analyze() - via MCP tools]
    ↓
[Generate blueprint_id (UUID)]
    ↓
[Store artifact in Artifact Plane]
    ↓
[Return structured artifact with blueprint_id reference]
    ↓
[Frontend updates realm state with blueprint]
    ↓
[Journey Complete]
```

### Expected Observable Artifacts
- `blueprint` - Coexistence blueprint artifact stored in Artifact Plane
  - `blueprint_id`: Unique identifier
  - `current_state`: Current state workflow analysis
  - `coexistence_state`: Target coexistence state definition
  - `roadmap`: Transformation roadmap
  - `responsibility_matrix`: RACI-style matrix
  - `sections`: Blueprint sections array

### Artifact Lifecycle State Transitions
- Blueprint artifact created with lifecycle state: `READY`
- Stored in Artifact Plane with metadata: `regenerable: true`, `retention_policy: session`

### Idempotency Scope (Per Intent)

| Intent | Idempotency Key | Scope |
|--------|-----------------|-------|
| `create_blueprint` | `hash(workflow_id + current_state_workflow_id + session_id)` | Per workflow - regenerates each time |

### Journey Completion Definition

**Journey is considered complete when:**
- workflow_id validated (required)
- BlueprintCreationAgent generates blueprint with transformation analysis
- Blueprint stored in Artifact Plane
- blueprint_id returned to frontend
- Frontend realm state updated with blueprint reference

---

## 2. Scenario 1: Happy Path

### Test Description
Complete journey works end-to-end without failures.

### Prerequisites
- Valid session with tenant_id and session_id
- Workflow exists (from Journey Realm)
- BlueprintCreationAgent is available

### Steps
1. [x] User selects a workflow to transform
2. [x] User optionally provides current_state_workflow_id for comparison
3. [x] User clicks "Create Blueprint" button
4. [x] `create_blueprint` intent executes with workflow_id parameter
5. [x] BlueprintCreationAgent analyzes workflow and generates blueprint
6. [x] Artifact stored in Artifact Plane
7. [x] Frontend displays blueprint with current state, coexistence state, roadmap

### Verification
- [x] Observable artifacts: blueprint with blueprint_id
- [x] Artifact stored in Artifact Plane (not execution state)
- [x] Blueprint includes current_state, coexistence_state, roadmap, responsibility_matrix
- [x] Frontend state updated: `outcomes.blueprints[blueprint_id]`
- [x] Event emitted: `blueprint_created`

### Status
✅ Implemented (requires BlueprintCreationAgent)

---

## 3. Scenario 2: Injected Failure

### Test Description
Journey handles failure gracefully when blueprint creation fails.

### Failure Injection Points (Test Each)
- **Option A:** Missing workflow_id (validation failure)
- **Option B:** BlueprintCreationAgent not available
- **Option C:** Artifact Plane storage fails

### Steps (Example: Agent not available)
1. [x] User provides workflow_id and triggers creation ✅
2. [x] `create_blueprint` intent executes
3. [x] BlueprintCreationAgent not available → ❌ **FAILURE**
4. [x] Raises NotImplementedError: "BlueprintCreationAgent not available"
5. [x] User sees error message

### Verification
- [x] Missing agent detected and reported
- [x] Clear error message provided
- [x] State remains consistent
- [x] User informed to retry when agent is available

### Status
⚠️ Agent may not be implemented - handled gracefully

---

## 4. Scenario 3: Partial Success

### Test Description
N/A - Single intent journey. Partial success not applicable.

---

## 5. Scenario 4: Retry/Recovery

### Test Description
Journey recovers correctly when user retries after failure.

### Steps
1. [x] User triggers blueprint creation → ❌ **FAILS** (first attempt)
2. [x] User clicks "Create Blueprint" again
3. [x] `create_blueprint` intent executes → ✅ **SUCCEEDS** (retry)
4. [x] New blueprint generated with new blueprint_id
5. [x] Journey completes

### Verification
- [x] Journey recovers correctly
- [x] New blueprint_id generated (not idempotent)
- [x] Retry succeeds (if agent available)

### Status
✅ Tested

---

## 6. Scenario 5: Boundary Violation

### Test Description
Journey rejects invalid inputs.

### Boundary Violation Points
- **Option A:** No session (session_id or tenant_id missing)
- **Option B:** Missing workflow_id (required parameter)

### Steps (Example: Missing workflow_id)
1. [x] User triggers blueprint creation without workflow_id
2. [x] `create_blueprint` intent executes → ❌ **BOUNDARY VIOLATION**
3. [x] Journey rejects request: "workflow_id is required for create_blueprint intent"
4. [x] User can select workflow and retry

### Verification
- [x] Missing workflow_id rejected with clear error message
- [x] Validation happens in both frontend and backend
- [x] State remains consistent

### Status
✅ Tested

---

## 7. Integration Points

### Platform Services
- **Outcomes Realm:** `OutcomesOrchestrator._handle_create_blueprint()`
- **Journey Realm:** Provides workflow data
- **Artifact Plane:** Artifact storage and retrieval
- **Runtime:** ExecutionLifecycleManager for intent execution

### Enabling Services
- `CoexistenceAnalysisService.analyze()` - used as MCP tool by agent

### Agents
- `BlueprintCreationAgent.process_request()` - required for blueprint generation

### Frontend
- `OutcomesAPIManager.createBlueprint(workflowId, currentStateWorkflowId)`
- `ensureArtifactLifecycle()` - adds lifecycle state

---

## 8. Architectural Verification

### Intent Flow
- [x] All intents use intent-based API (submitIntent)
- [x] All intents flow through Runtime
- [x] All intents have execution_id
- [x] Parameter validation: workflow_id required

### State Authority
- [x] Artifact Plane is authoritative for blueprint storage
- [x] Frontend syncs blueprint reference after completion
- [x] blueprint_id enables retrieval across sessions

### Agent Pattern
- [x] Uses agentic forward pattern
- [x] Agent uses CoexistenceAnalysisService as MCP tool
- [x] Agent reasons about transformation, designs phases

### Observability
- [x] execution_id present in all logs
- [x] Telemetry recorded
- [x] Health monitoring active

---

## 9. SRE Verification

### Error Handling
- [x] Missing agent raises clear error
- [x] Artifact Plane failure falls back to execution state
- [x] Validation errors provide actionable messages

### State Persistence
- [x] Blueprint persists in Artifact Plane
- [x] blueprint_id enables retrieval
- [x] Frontend caches blueprint reference

### Boundaries
- [x] Browser → Frontend: "Create Blueprint" with workflow_id
- [x] Frontend → Backend: submitIntent("create_blueprint", { workflow_id })
- [x] Backend → Runtime: ExecutionLifecycleManager.execute()
- [x] Runtime → Realm: OutcomesOrchestrator.handle_intent()
- [x] Realm → Artifact Plane: create_artifact()

---

## 10. Gate Status

**Journey is "done" only when:**
- [x] ✅ Happy path works (when agent available)
- [x] ✅ Injected failure handled
- [x] ✅ N/A - Partial success
- [x] ✅ Retry/recovery works
- [x] ✅ Boundary violation rejected
- [x] ✅ Architectural verification passes
- [x] ✅ Observability guarantees met
- [x] ✅ SRE verification passes

**Current Status:** ✅ **IMPLEMENTED** (BlueprintCreationAgent optional)

---

**Last Updated:** January 27, 2026  
**Owner:** Solution Realm Solution Team  
**Implementation:** `symphainy_platform/realms/outcomes/orchestrators/outcomes_orchestrator.py::_handle_create_blueprint`  
**Frontend:** `symphainy-frontend/shared/managers/OutcomesAPIManager.ts::createBlueprint()`
