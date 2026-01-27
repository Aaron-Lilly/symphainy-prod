# Journey Contract: Solution Synthesis

**Journey:** Solution Synthesis  
**Journey ID:** `journey_solution_synthesis`  
**Solution:** Solution Realm Solution  
**Status:** ✅ **IMPLEMENTED**  
**Priority:** 🔴 **PRIORITY 1** - Foundation journey

---

## 1. Journey Overview

### Purpose
Synthesize business outcomes from Content, Insights, and Journey realms into a unified solution summary with visualizations. This journey aggregates pillar summaries from session state and generates a comprehensive synthesis with realm-specific visuals.

### Intents in Journey

| Step | Intent | Description |
|------|--------|-------------|
| 1 | `synthesize_outcome` | Synthesize outcomes from all realms with visualizations |

### Journey Flow
```
[User clicks "Generate Artifacts" in Business Outcomes]
    ↓
[Frontend calls OutcomesAPIManager.synthesizeOutcome()]
    ↓
[synthesize_outcome intent submitted to Runtime]
    ↓
[OutcomesOrchestrator._handle_synthesize_outcome()]
    ↓
[Read pillar summaries from session state]
    ↓
[OutcomesSynthesisAgent.process_request() - synthesize + generate visuals]
    ↓
[ReportGeneratorService.generate_pillar_summary() - generate report]
    ↓
[VisualGenerationService.generate_summary_visual() - generate visualization]
    ↓
[Return structured artifact with synthesis + renderings]
    ↓
[Frontend updates realm state with synthesis]
    ↓
[Journey Complete]
```

### Expected Observable Artifacts
- `solution` - Synthesized solution artifact
  - `semantic_payload`: solution_id, session_id, status
  - `renderings`: synthesis, content_summary, insights_summary, journey_summary, realm_visuals, summary_visual

### Artifact Lifecycle State Transitions
- Synthesis artifact created with lifecycle state: `READY`
- No intermediate states (single-intent journey)

### Idempotency Scope (Per Intent)

| Intent | Idempotency Key | Scope |
|--------|-----------------|-------|
| `synthesize_outcome` | `hash(session_id + timestamp)` | Per session, not idempotent (regenerates each time) |

### Journey Completion Definition

**Journey is considered complete when:**
- Pillar summaries successfully read from session state
- OutcomesSynthesisAgent generates synthesis successfully
- Summary visualization generated (or warning logged if failed)
- Structured artifact returned to frontend
- Frontend realm state updated with synthesis

---

## 2. Scenario 1: Happy Path

### Test Description
Complete journey works end-to-end without failures.

### Prerequisites
- User has completed work in Content, Insights, and/or Journey pillars
- Pillar summaries exist in session state
- Valid session with tenant_id and session_id

### Steps
1. [x] User navigates to Business Outcomes pillar
2. [x] User clicks "Generate Artifacts" button
3. [x] `synthesize_outcome` intent executes
4. [x] Pillar summaries read from session state
5. [x] OutcomesSynthesisAgent generates synthesis
6. [x] Summary visualization generated
7. [x] Structured artifact returned
8. [x] Frontend displays synthesis with realm visuals

### Verification
- [x] Observable artifacts: solution artifact with synthesis + renderings
- [x] Realm visuals include content, insights, journey summaries
- [x] Summary visualization (image) generated and included
- [x] Frontend state updated: `outcomes.syntheses`
- [x] Event emitted: `outcome_synthesized`

### Status
✅ Tested and working

---

## 3. Scenario 2: Injected Failure

### Test Description
Journey handles failure gracefully when synthesis fails.

### Failure Injection Points (Test Each)
- **Option A:** Session state read fails (state_surface unavailable)
- **Option B:** OutcomesSynthesisAgent fails (LLM timeout)
- **Option C:** Visual generation fails (VisualGenerationService error)

### Steps (Example: Agent failure)
1. [x] User triggers synthesis ✅
2. [x] `synthesize_outcome` intent executes
3. [x] OutcomesSynthesisAgent.process_request() → ❌ **FAILURE INJECTED** (LLM timeout)
4. [x] Journey handles failure gracefully
5. [x] User sees appropriate error message ("Failed to synthesize outcome")
6. [x] State remains consistent (no partial artifacts)
7. [x] User can retry

### Verification
- [x] Failure handled gracefully (no crash, no unhandled exception)
- [x] User sees appropriate error message (clear, actionable)
- [x] State remains consistent (no corruption)
- [x] User can retry synthesis
- [x] Error includes execution_id (for debugging)
- [x] Error logged with intent + execution_id

### Status
✅ Tested - graceful degradation implemented

---

## 4. Scenario 3: Partial Success

### Test Description
N/A - Single intent journey. Partial success not applicable.

### Notes
- This is a single-intent journey
- Either synthesis succeeds completely or fails
- Visual generation failure is logged but non-blocking (synthesis still returns)

---

## 5. Scenario 4: Retry/Recovery

### Test Description
Journey recovers correctly when user retries after failure.

### Retry Pattern
1. Synthesis fails (any reason)
2. User retries via "Generate Artifacts" button
3. New synthesis attempt executes
4. Journey completes successfully

### Steps
1. [x] User triggers synthesis ✅
2. [x] `synthesize_outcome` intent executes → ❌ **FAILS** (first attempt)
3. [x] User clicks "Generate Artifacts" again
4. [x] `synthesize_outcome` intent executes → ✅ **SUCCEEDS** (retry)
5. [x] Journey completes

### Verification
- [x] Journey recovers correctly
- [x] No duplicate state issues (not idempotent - generates fresh each time)
- [x] Retry succeeds
- [x] Journey completes after retry

### Status
✅ Tested - retry works correctly

---

## 6. Scenario 5: Boundary Violation

### Test Description
Journey rejects invalid inputs and handles edge cases.

### Boundary Violation Points
- **Option A:** No session (session_id or tenant_id missing)
- **Option B:** Empty pillar summaries (user has no work in other pillars)
- **Option C:** Invalid session state format

### Steps (Example: No session)
1. [x] User triggers synthesis without valid session
2. [x] `synthesize_outcome` intent executes → ❌ **BOUNDARY VIOLATION** (session required)
3. [x] Journey rejects request
4. [x] User sees validation error message ("Session required to synthesize outcome")
5. [x] User can establish session and retry

### Verification
- [x] Invalid inputs rejected (validation fails)
- [x] User sees clear validation error messages
- [x] State remains consistent
- [x] User can correct issue and retry

### Status
✅ Tested - validation working

---

## 7. Integration Points

### Platform Services
- **Outcomes Realm:** `OutcomesOrchestrator._handle_synthesize_outcome()`
- **State Surface:** `get_session_state()` for pillar summaries
- **Runtime:** ExecutionLifecycleManager for intent execution

### Enabling Services
- `ReportGeneratorService.generate_pillar_summary()`
- `VisualGenerationService.generate_summary_visual()`

### Agents
- `OutcomesSynthesisAgent.process_request()` - main synthesis logic

### Frontend
- `OutcomesAPIManager.synthesizeOutcome()`
- `PlatformStateProvider` - realm state management

---

## 8. Architectural Verification

### Intent Flow
- [x] All intents use intent-based API (submitIntent via PlatformStateProvider)
- [x] All intents flow through Runtime (ExecutionLifecycleManager)
- [x] All intents have execution_id (tracked via platformState.trackExecution)
- [x] Parameter validation in frontend (validateSession)
- [x] Parameter validation in backend (session state check)

### State Authority
- [x] Runtime is authoritative (frontend syncs with Runtime state)
- [x] Session state is authoritative for pillar summaries
- [x] Frontend syncs with Runtime (state.outcomes.syntheses updated)
- [x] No state divergence

### Enforcement
- [x] Session validation required before intent submission
- [x] Direct API calls bypassed by intent-based architecture

### Observability
- [x] execution_id present in all logs
- [x] Telemetry recorded via AgenticTelemetryService
- [x] Health monitoring via OrchestratorHealthMonitor
- [x] Errors include intent + execution_id

---

## 9. SRE Verification

### Error Handling
- [x] Journey handles LLM timeout gracefully
- [x] Journey handles state read failure gracefully
- [x] Visual generation failure is non-blocking (logged, synthesis continues)

### State Persistence
- [x] Synthesis result stored in frontend realm state
- [x] Session state persists across steps
- [x] Result available after page refresh (via re-synthesis)

### Boundaries
- [x] Browser → Frontend: "Generate Artifacts" button click
- [x] Frontend → Backend: submitIntent("synthesize_outcome")
- [x] Backend → Runtime: ExecutionLifecycleManager.execute()
- [x] Runtime → Realm: OutcomesOrchestrator.handle_intent()
- [x] Realm → State Surface: get_session_state()

---

## 10. Gate Status

**Journey is "done" only when:**
- [x] ✅ Happy path works
- [x] ✅ Injected failure handled
- [x] ✅ N/A - Partial success (single-intent journey)
- [x] ✅ Retry/recovery works
- [x] ✅ Boundary violation rejected
- [x] ✅ Architectural verification passes
- [x] ✅ Observability guarantees met
- [x] ✅ SRE verification passes

**Current Status:** ✅ **IMPLEMENTED**

---

**Last Updated:** January 27, 2026  
**Owner:** Solution Realm Solution Team  
**Implementation:** `symphainy_platform/realms/outcomes/orchestrators/outcomes_orchestrator.py::_handle_synthesize_outcome`  
**Frontend:** `symphainy-frontend/shared/managers/OutcomesAPIManager.ts::synthesizeOutcome()`
