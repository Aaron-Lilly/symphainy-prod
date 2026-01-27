# Journey Contract: Roadmap Generation

**Journey:** Roadmap Generation  
**Journey ID:** `journey_solution_roadmap_generation`  
**Solution:** Solution Realm Solution  
**Status:** ✅ **IMPLEMENTED**  
**Priority:** 🔴 **PRIORITY 1** - Foundation journey

---

## 1. Journey Overview

### Purpose
Generate a strategic roadmap from user-provided goals. The roadmap includes phases, timeline, milestones, and visualization. The generated roadmap is stored in the Artifact Plane for retrieval and can be used to create a platform solution.

### Intents in Journey

| Step | Intent | Description |
|------|--------|-------------|
| 1 | `generate_roadmap` | Generate strategic roadmap from goals |

### Journey Flow
```
[User provides goals and clicks "Generate Roadmap"]
    ↓
[Frontend calls OutcomesAPIManager.generateRoadmap(goals)]
    ↓
[generate_roadmap intent submitted to Runtime]
    ↓
[OutcomesOrchestrator._handle_generate_roadmap()]
    ↓
[Validate goals array is non-empty]
    ↓
[RoadmapGenerationAgent.process_request() OR RoadmapGenerationService.generate_roadmap()]
    ↓
[Generate roadmap_id (UUID)]
    ↓
[VisualGenerationService.generate_roadmap_visual() - optional]
    ↓
[Store artifact in Artifact Plane]
    ↓
[Return structured artifact with roadmap_id reference]
    ↓
[Frontend updates realm state with roadmap]
    ↓
[Journey Complete]
```

### Expected Observable Artifacts
- `roadmap` - Strategic roadmap artifact stored in Artifact Plane
  - `roadmap_id`: Unique identifier
  - `goals`: User-provided goals array
  - `status`: Generation status
  - `plan`: Array of phases with descriptions
  - `strategic_plan`: Detailed strategic plan
  - `metrics`: estimated_duration_weeks, estimated_cost_usd
  - `roadmap_visual`: Optional visualization (image_base64, storage_path)

### Artifact Lifecycle State Transitions
- Roadmap artifact created with lifecycle state: `READY`
- Stored in Artifact Plane with metadata: `regenerable: true`, `retention_policy: session`

### Idempotency Scope (Per Intent)

| Intent | Idempotency Key | Scope |
|--------|-----------------|-------|
| `generate_roadmap` | `hash(goals + session_id)` | Per goals input - regenerates each time |

### Journey Completion Definition

**Journey is considered complete when:**
- Goals validated (non-empty array)
- RoadmapGenerationAgent/Service generates roadmap
- Roadmap stored in Artifact Plane
- roadmap_id returned to frontend
- Frontend realm state updated with roadmap reference

---

## 2. Scenario 1: Happy Path

### Test Description
Complete journey works end-to-end without failures.

### Prerequisites
- Valid session with tenant_id and session_id
- User provides at least one goal

### Steps
1. [x] User enters goals (e.g., ["Modernize legacy system", "Improve efficiency"])
2. [x] User clicks "Generate Roadmap" button
3. [x] `generate_roadmap` intent executes with goals parameter
4. [x] RoadmapGenerationAgent generates strategic roadmap
5. [x] Roadmap visualization generated (optional)
6. [x] Artifact stored in Artifact Plane
7. [x] Frontend displays roadmap with phases and timeline

### Verification
- [x] Observable artifacts: roadmap with roadmap_id
- [x] Artifact stored in Artifact Plane (not execution state)
- [x] Roadmap includes phases, timeline, milestones
- [x] Frontend state updated: `outcomes.roadmaps[roadmap_id]`
- [x] Event emitted: `roadmap_generated`

### Status
✅ Tested and working

---

## 3. Scenario 2: Injected Failure

### Test Description
Journey handles failure gracefully when roadmap generation fails.

### Failure Injection Points (Test Each)
- **Option A:** Empty goals array (validation failure)
- **Option B:** RoadmapGenerationAgent fails (LLM timeout)
- **Option C:** Artifact Plane storage fails

### Steps (Example: Agent failure)
1. [x] User provides goals and triggers generation ✅
2. [x] `generate_roadmap` intent executes
3. [x] RoadmapGenerationAgent.process_request() → ❌ **FAILURE INJECTED** (LLM timeout)
4. [x] Fallback to RoadmapGenerationService (if agent unavailable)
5. [x] Journey handles failure gracefully
6. [x] User sees appropriate error message

### Verification
- [x] Failure handled gracefully (fallback to service if agent fails)
- [x] User sees appropriate error message (clear, actionable)
- [x] State remains consistent
- [x] User can retry
- [x] Error includes execution_id

### Status
✅ Tested - graceful fallback to service

---

## 4. Scenario 3: Partial Success

### Test Description
N/A - Single intent journey. Partial success not applicable.

### Notes
- Visual generation failure is non-blocking (roadmap still saved)
- Artifact Plane failure falls back to execution state (logged as warning)

---

## 5. Scenario 4: Retry/Recovery

### Test Description
Journey recovers correctly when user retries after failure.

### Steps
1. [x] User triggers roadmap generation → ❌ **FAILS** (first attempt)
2. [x] User clicks "Generate Roadmap" again with same/modified goals
3. [x] `generate_roadmap` intent executes → ✅ **SUCCEEDS** (retry)
4. [x] New roadmap generated with new roadmap_id
5. [x] Journey completes

### Verification
- [x] Journey recovers correctly
- [x] New roadmap_id generated (not idempotent)
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
- **Option B:** Empty goals array
- **Option C:** Goals array with invalid types

### Steps (Example: Empty goals)
1. [x] User triggers roadmap generation with empty goals
2. [x] `generate_roadmap` intent executes → ❌ **BOUNDARY VIOLATION**
3. [x] Journey rejects request: "Goals are required for roadmap generation"
4. [x] User can add goals and retry

### Verification
- [x] Empty goals rejected with clear error message
- [x] Validation happens in both frontend and backend
- [x] State remains consistent
- [x] User can correct issue and retry

### Status
✅ Tested

---

## 7. Integration Points

### Platform Services
- **Outcomes Realm:** `OutcomesOrchestrator._handle_generate_roadmap()`
- **Artifact Plane:** Artifact storage and retrieval
- **Runtime:** ExecutionLifecycleManager for intent execution

### Enabling Services
- `RoadmapGenerationService.generate_roadmap()`
- `VisualGenerationService.generate_roadmap_visual()`

### Agents
- `RoadmapGenerationAgent.process_request()` - optional, falls back to service

### Frontend
- `OutcomesAPIManager.generateRoadmap(goals, roadmapOptions)`
- `ensureArtifactLifecycle()` - adds lifecycle state

---

## 8. Architectural Verification

### Intent Flow
- [x] All intents use intent-based API (submitIntent)
- [x] All intents flow through Runtime
- [x] All intents have execution_id
- [x] Parameter validation: goals required, non-empty

### State Authority
- [x] Artifact Plane is authoritative for roadmap storage
- [x] Frontend syncs roadmap reference after completion
- [x] Roadmap_id enables retrieval across sessions

### Artifact Plane Storage
- [x] Roadmap stored as artifact (not execution state)
- [x] Metadata includes: regenerable, retention_policy
- [x] Fallback to execution state if Artifact Plane unavailable

### Observability
- [x] execution_id present in all logs
- [x] Telemetry recorded
- [x] Health monitoring active

---

## 9. SRE Verification

### Error Handling
- [x] Agent failure falls back to service
- [x] Artifact Plane failure falls back to execution state
- [x] Visual generation failure is non-blocking

### State Persistence
- [x] Roadmap persists in Artifact Plane
- [x] roadmap_id enables retrieval
- [x] Frontend caches roadmap reference

### Boundaries
- [x] Browser → Frontend: "Generate Roadmap" with goals
- [x] Frontend → Backend: submitIntent("generate_roadmap", { goals })
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
**Implementation:** `symphainy_platform/realms/outcomes/orchestrators/outcomes_orchestrator.py::_handle_generate_roadmap`  
**Frontend:** `symphainy-frontend/shared/managers/OutcomesAPIManager.ts::generateRoadmap()`
