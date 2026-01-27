# Journey Contract: GuideAgent Interaction

**Journey:** GuideAgent Interaction  
**Journey ID:** `journey_coexistence_guide_agent`  
**Solution:** Coexistence Solution  
**Status:** ⏳ **IN PROGRESS**  
**Priority:** 🔴 **PRIORITY 1** - Foundation journey for Coexistence Solution

---

## 1. Journey Overview

### Intents in Journey
1. `initiate_guide_agent` - Step 1: Initialize GuideAgent conversation with platform-wide context and MCP tool access
2. `process_guide_agent_message` - Step 2: Process user message, generate response, optionally call orchestrator MCP tools
3. `route_to_liaison_agent` - Step 3: Route conversation to Liaison Agent with context sharing

### Journey Flow
```
[User sends message to GuideAgent or toggles to GuideAgent]
    ↓
[initiate_guide_agent] → guide_agent_conversation_artifact
    - GuideAgent initialized with platform-wide context
    - Access to all orchestrator MCP tools (via Curator)
    - Full conversation history loaded
    - Context shared from previous agent (if toggled)
    ↓
[process_guide_agent_message] → guide_agent_response_artifact
    - User message processed
    - GuideAgent generates response (with platform-wide knowledge)
    - Optionally: GuideAgent calls orchestrator MCP tool (governed)
    - MCP tool executes journey/intent
    - Response includes MCP tool results (if called)
    - Conversation context updated
    ↓
[Optionally: route_to_liaison_agent] → liaison_agent_activated
    - GuideAgent determines appropriate Liaison Agent
    - Context shared to Liaison Agent
    - User toggled to Liaison Agent
    ↓
[Journey Complete]
```

### Expected Observable Artifacts
- Navigation artifacts (logged for analytics)
- Conversation artifacts (stored if enabled)
- Solution context artifacts (ephemeral)

### Journey Completion Definition

**Journey is considered complete when:**

* GuideAgent processes user message and returns response **OR**
* GuideAgent routes to Liaison Agent with context sharing **OR**
* GuideAgent successfully calls orchestrator MCP tool and returns results

**Journey completion = user receives helpful response from GuideAgent (with optional MCP tool execution).**

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
Complete journey works end-to-end without failures.

### Steps
1. [ ] User triggers journey
2. [ ] Intents execute successfully
3. [ ] Journey completes successfully

### Verification
- [ ] Observable artifacts at each step
- [ ] Journey completes successfully

---

## 3. Integration Points

### Platform Services
- **Coexistence Realm:** Intent services
- **Journey Realm:** Orchestration services
- **Agent Framework:** GuideAgent, Liaison Agents

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
**Owner:** Coexistence Solution Team
