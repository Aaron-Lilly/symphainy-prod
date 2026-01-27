# Journey Contract Template

**Journey:** `[journey_name]`  
**Journey Number:** `[number]`  
**Status:** ⏳ **IN PROGRESS** | ✅ **COMPLETE** | ❌ **BLOCKED**

---

## 1. Journey Overview

### Intents in Journey
1. `[intent_1]` - Step `[step_description]`
2. `[intent_2]` - Step `[step_description]`
3. `[intent_3]` - Step `[step_description]`
...

### Journey Flow
```
[Step 1] → [Step 2] → [Step 3] → ... → [Completion]
```

### Expected Observable Artifacts
- Step 1: `[artifact_description]`
- Step 2: `[artifact_description]`
- Step 3: `[artifact_description]`
...

---

## 2. Scenario 1: Happy Path

### Test Description
Complete journey works end-to-end without failures.

### Steps
1. [ ] `[step_1_description]`
2. [ ] `[step_2_description]`
3. [ ] `[step_3_description]`
...

### Verification
- [ ] Observable artifacts at each step
- [ ] State updates correctly
- [ ] All intents use intent-based API
- [ ] All intents flow through Runtime
- [ ] All intents have execution_id

### Status
⏳ Not tested | ✅ Passing | ❌ Failing

**Result:** `[test_result]`

---

## 3. Scenario 2: Injected Failure

### Test Description
Journey handles failure gracefully when failure is injected at one step.

### Failure Injection Point
- **Step:** `[step_number]` - `[step_description]`
- **Failure Type:** `[network_failure | storage_failure | analysis_failure | etc.]`

### Steps
1. [ ] `[step_1_description]` ✅
2. [ ] `[step_2_description]` ✅
3. [ ] `[step_3_description]` ❌ **FAILURE INJECTED**
4. [ ] Journey handles failure
5. [ ] User sees appropriate error

### Verification
- [ ] Failure handled gracefully
- [ ] User sees appropriate error message
- [ ] State remains consistent (no corruption)
- [ ] User can retry
- [ ] No partial state left behind

### Status
⏳ Not tested | ✅ Passing | ❌ Failing

**Result:** `[test_result]`

---

## 4. Scenario 3: Partial Success

### Test Description
Journey handles partial completion when some steps succeed and some fail.

### Partial Success Pattern
- **Steps 1-2:** ✅ Succeed
- **Step 3:** ❌ Fails
- **Steps 4-5:** Not attempted

### Steps
1. [ ] `[step_1_description]` ✅
2. [ ] `[step_2_description]` ✅
3. [ ] `[step_3_description]` ❌
4. [ ] Journey handles partial completion
5. [ ] User can retry failed step

### Verification
- [ ] Partial state handled correctly
- [ ] User can retry failed step
- [ ] No state corruption
- [ ] Completed steps remain valid
- [ ] Failed step can be retried

### Status
⏳ Not tested | ✅ Passing | ❌ Failing

**Result:** `[test_result]`

---

## 5. Scenario 4: Retry/Recovery

### Test Description
Journey recovers correctly when user retries after failure.

### Retry Pattern
1. Journey fails at step 3
2. User retries
3. Journey recovers and completes

### Steps
1. [ ] `[step_1_description]` ✅
2. [ ] `[step_2_description]` ✅
3. [ ] `[step_3_description]` ❌ (first attempt)
4. [ ] User retries
5. [ ] `[step_3_description]` ✅ (retry succeeds)
6. [ ] `[step_4_description]` ✅
7. [ ] Journey completes

### Verification
- [ ] Journey recovers correctly
- [ ] No duplicate state (no duplicate files, no duplicate analysis, etc.)
- [ ] State consistency maintained
- [ ] Retry succeeds
- [ ] Journey completes after retry
- [ ] Idempotency verified (no duplicate side effects)
- [ ] Same execution_id reused safely
- [ ] State transitions are monotonic

### Status
⏳ Not tested | ✅ Passing | ❌ Failing

**Result:** `[test_result]`

---

## 6. Scenario 5: Boundary Violation

### Test Description
Journey rejects invalid inputs and maintains state consistency.

### Boundary Violation
- **Type:** `[invalid_file | invalid_parameters | invalid_state | etc.]`
- **Input:** `[invalid_input_description]`

### Steps
1. [ ] User attempts journey with invalid input
2. [ ] Journey rejects invalid input
3. [ ] User sees clear error message
4. [ ] State remains consistent (no corruption)

### Verification
- [ ] Invalid input rejected
- [ ] Clear error message displayed
- [ ] No state corruption
- [ ] User can correct input and retry
- [ ] No partial state left behind

### Status
⏳ Not tested | ✅ Passing | ❌ Failing

**Result:** `[test_result]`

---

## 7. Architectural Verification

### Intent Flow
- [ ] All intents use intent-based API
- [ ] All intents flow through Runtime
- [ ] All intents have execution_id
- [ ] All intents have parameter validation
- [ ] All intents have session validation

### State Authority
- [ ] Runtime is authoritative
- [ ] Frontend syncs with Runtime
- [ ] No state divergence
- [ ] State persists across steps

### Enforcement
- [ ] All intents have enforcement
- [ ] Enforcement prevents violations
- [ ] Intentional violations fail

### Observability
- [ ] execution_id present in all logs
- [ ] execution_id propagated across intent boundaries
- [ ] Errors include intent + execution_id
- [ ] Journey trace reconstructable from logs

---

## 8. SRE Verification

### Error Handling
- [ ] Journey handles network failure
- [ ] Journey handles storage failure
- [ ] Journey handles analysis failure
- [ ] Journey handles timeout

### State Persistence
- [ ] State persists across steps
- [ ] State persists across refresh
- [ ] State persists across navigation

### Boundaries
- [ ] Browser → Frontend boundary works
- [ ] Frontend → Backend boundary works
- [ ] Backend → Runtime boundary works
- [ ] Runtime → Realm boundary works
- [ ] Realm → Public Works boundary works

---

## 9. Gate Status

**Journey is "done" only when:**
- ✅ Happy path works
- ✅ Injected failure handled
- ✅ Partial success handled
- ✅ Retry/recovery works (with idempotency verified)
- ✅ Boundary violation rejected
- ✅ Architectural verification passes
- ✅ Observability guarantees met
- ✅ SRE verification passes

**Current Status:** ⏳ **IN PROGRESS** | ✅ **COMPLETE** | ❌ **BLOCKED**

**Blockers:**
- `[blocker_description]`

---

**Last Updated:** [date]  
**Owner:** [team_member]
