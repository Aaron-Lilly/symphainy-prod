#!/usr/bin/env python3
"""
Script to enhance journey contract templates with comprehensive test scenarios
and implementation details based on the pattern from journey_1_file_upload_processing.md
"""

import os
import re

def enhance_journey_contract(filepath):
    """Enhance a journey contract with comprehensive test scenarios"""
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Check if already has comprehensive scenarios
    if "## 3. Scenario 2: Injected Failure" in content and "## 4. Scenario 3: Partial Success" in content:
        return False  # Already enhanced
    
    # Find the Integration Points section (or create it)
    integration_section = """
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
"""
    
    # Replace the simple Integration Points section with comprehensive scenarios
    if "## 3. Integration Points" in content:
        # Replace existing Integration Points with enhanced version
        content = re.sub(
            r'## 3\. Integration Points.*?## 2\. Scenario 1: Happy Path',
            r'## 2. Scenario 1: Happy Path',
            content,
            flags=re.DOTALL
        )
        # Insert enhanced scenarios before Integration Points
        content = content.replace("## 2. Scenario 1: Happy Path", integration_section + "\n## 2. Scenario 1: Happy Path")
    
    # Add Architectural Verification section if not present
    if "## 8. Architectural Verification" not in content:
        arch_verification = """
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

"""
        
        # Insert before the last "Last Updated" line
        content = re.sub(
            r'(\n---\n\n\*\*Last Updated:.*)',
            arch_verification + r'\1',
            content
        )
    
    with open(filepath, 'w') as f:
        f.write(content)
    
    return True

if __name__ == "__main__":
    # Find all template journey contracts
    base_dir = "."
    template_files = []
    
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".md") and file.startswith("journey_"):
                filepath = os.path.join(root, file)
                # Skip summary and already comprehensive contracts
                if "SUMMARY" not in filepath and "security" not in filepath.lower():
                    template_files.append(filepath)
    
    enhanced = 0
    for filepath in sorted(template_files):
        if enhance_journey_contract(filepath):
            enhanced += 1
            print(f"✅ Enhanced: {filepath}")
    
    print(f"\n✅ Enhanced {enhanced} journey contract templates")
