# Intent/Journey-Based Refactoring Workplan

**Date:** January 25, 2026  
**Status:** 🔴 **CRITICAL - EXECUTION PLAN**  
**Priority:** 🔴 **HIGHEST** - Align with platform architecture

---

## Executive Summary

**Approach:** Intent/journey-based refactoring with strict gates and adversarial testing.

**Key Principles:**
1. **No intent without enforcement** - Intent is "done" only when contract + enforcement + journey evidence exist
2. **No journey without failure** - Journey must survive happy path + failures + recovery + boundary violations
3. **Fix AND verify** - Every fix must be verified to actually work

**Goal:** Real working platform with enforceable contracts, not another round of false confidence.

---

## Workplan Structure

### Level 1: Intent Contracts (27 intents)

**For each intent:**
1. **Contract** - Required inputs, forbidden behaviors, guaranteed outputs
2. **Runtime Enforcement** - What physically prevents violation
3. **Journey Evidence** - At least one real journey proves it works end-to-end

**Gate:** Intent is "done" only when all three exist.

---

### Level 2: Journey Contracts (7 journeys)

**For each journey:**
1. **Happy Path** - Complete journey works
2. **Injected Failure** - Journey handles failure gracefully
3. **Partial Success** - Journey handles partial completion
4. **Retry/Recovery** - Journey recovers from failure
5. **Boundary Violation** - Journey rejects invalid inputs

**Gate:** Journey is "done" only when all five scenarios pass.

---

### Level 3: Platform Verification

**Holistic verification:**
1. All intents verified (contract + enforcement + evidence)
2. All journeys verified (all 5 scenarios)
3. Platform verified (no violations, all enforcement active)

---

## Execution Plan

### Phase 1: Intent Audit & Contract Creation (3-4 days)

**Goal:** Create contracts for all 27 intents, identify all violations

**Approach:**
1. For each intent in `COMPLETE_INTENT_CATALOG.md`:
   - Create intent contract (required inputs, forbidden behaviors, guaranteed outputs)
   - Audit for violations (direct API calls, missing validation, etc.)
   - Identify which journeys use this intent
   - Create violation report

2. Prioritize by journey usage:
   - Intents used in Journeys 1-2 (most critical) → Fix first
   - Intents used in Journeys 3-4 → Fix second
   - Intents used in Journeys 5-7 → Fix third
   - Intents not in journeys → Fix last

**Deliverable:** 
- Intent contracts for all 27 intents
- Violation report per intent
- Priority ranking

**Gate:** All contracts created, all violations identified

---

### Phase 2: Intent Fixes with Enforcement (7-10 days)

**Goal:** Fix all violations AND implement enforcement for each intent

**Approach:**
1. For each intent (in priority order):
   - **Fix violations:**
     - Migrate to intent-based API
     - Add parameter validation
     - Add session validation
     - Add state updates
     - Add error handling
   
   - **Implement enforcement:**
     - ESLint rule (if applicable)
     - Runtime check (required)
     - Proof test (intentional violation must fail)
   
   - **Verify fix works:**
     - Test intent works correctly
     - Test enforcement actually prevents violations
     - Test intentional violation fails
   
   - **Create journey evidence:**
     - Identify at least one journey using this intent
     - Verify intent works in that journey context
     - Document evidence

2. **Gate per intent:**
   - ✅ Contract exists
   - ✅ Enforcement implemented
   - ✅ Proof test passes (violation fails)
   - ✅ Journey evidence exists
   - ✅ Intent works correctly

**Deliverable:**
- All intents fixed
- All intents enforced
- All intents verified
- Journey evidence for all intents

**Gate:** All intents have contract + enforcement + journey evidence

---

### Phase 3: Journey Testing with Adversarial Scenarios (4-5 days)

**Goal:** Test all 7 journeys with happy path + failures + recovery + boundary violations

**Approach:**
1. For each journey in `USER_JOURNEY_FLOWS.md`:
   
   **Scenario 1: Happy Path**
   - Test complete journey works end-to-end
   - Verify observable artifacts at each step
   - Verify state updates correctly
   - Verify all intents use intent-based API
   
   **Scenario 2: Injected Failure**
   - Inject failure at one step (network failure, storage failure, etc.)
   - Verify journey handles failure gracefully
   - Verify user sees appropriate error
   - Verify state remains consistent
   
   **Scenario 3: Partial Success**
   - Journey partially completes (some steps succeed, some fail)
   - Verify journey handles partial completion
   - Verify state reflects partial completion
   - Verify user can recover/retry
   
   **Scenario 4: Retry/Recovery**
   - Journey fails, user retries
   - Verify journey recovers correctly
   - Verify no duplicate state
   - Verify state consistency
   
   **Scenario 5: Boundary Violation**
   - Attempt journey with invalid inputs
   - Verify journey rejects invalid inputs
   - Verify clear error messages
   - Verify no state corruption

2. **Gate per journey:**
   - ✅ Happy path works
   - ✅ Injected failure handled
   - ✅ Partial success handled
   - ✅ Retry/recovery works
   - ✅ Boundary violation rejected

**Deliverable:**
- All journeys tested (all 5 scenarios)
- Journey test results
- Journey fixes (if needed)

**Gate:** All journeys pass all 5 scenarios

---

### Phase 4: Platform Verification (2-3 days)

**Goal:** Verify platform holistically - no violations, all enforcement active, all tests passing

**Approach:**
1. **Intent Verification:**
   - Verify all 27 intents have contracts
   - Verify all 27 intents have enforcement
   - Verify all 27 intents have journey evidence
   - Verify all 27 intents work correctly
   - Verify intentional violations fail

2. **Journey Verification:**
   - Verify all 7 journeys pass all 5 scenarios
   - Verify all journeys use intent-based API
   - Verify all journeys handle failures
   - Verify all journeys maintain state consistency

3. **Platform Verification:**
   - Run comprehensive audit (0 violations)
   - Run E2E 3D tests (0 warnings)
   - Run enforcement tests (all pass)
   - Run journey tests (all pass)
   - Verify CI/CD gates (all pass)

4. **Independent Verification:**
   - CTO/CIO code review
   - Independent audit
   - Documentation review

**Deliverable:**
- Platform verification report
- Test results (all passing)
- Enforcement verification (all active)
- Independent verification report

**Gate:** Platform verified, all tests passing, all enforcement active, independent verification complete

---

## Preventing the Two Traps

### Trap #1: Treating Intents Like "Micro-Phases"

**Prevention:**
- **Gate per intent:** Contract + Enforcement + Journey Evidence (all three required)
- **No partial completion:** Intent is either "done" or "not done" (no "mostly done")
- **Proof test required:** Intentional violation must fail
- **Journey evidence required:** At least one journey proves it works

**Verification:**
- Check: Does intent have all three (contract + enforcement + evidence)?
- If no → Intent is not done, cannot proceed

---

### Trap #2: Letting Journeys Become "Demo Flows"

**Prevention:**
- **5 scenarios required:** Happy path + Injected failure + Partial success + Retry/recovery + Boundary violation
- **Adversarial by design:** Journeys must survive intentional failures
- **No happy-path-only:** Journey is either "done" (all 5 scenarios) or "not done"

**Verification:**
- Check: Does journey pass all 5 scenarios?
- If no → Journey is not done, cannot proceed

---

## Success Criteria

### Intent Success (Per Intent)

- ✅ Contract exists (required inputs, forbidden behaviors, guaranteed outputs)
- ✅ Enforcement implemented (ESLint, runtime, proof test)
- ✅ Journey evidence exists (at least one journey proves it works)
- ✅ Intent works correctly (functional verification)
- ✅ Intentional violation fails (enforcement verification)

**Gate:** All criteria met → Intent is "done"

---

### Journey Success (Per Journey)

- ✅ Happy path works (complete journey end-to-end)
- ✅ Injected failure handled (journey survives failure)
- ✅ Partial success handled (journey handles partial completion)
- ✅ Retry/recovery works (journey recovers from failure)
- ✅ Boundary violation rejected (journey rejects invalid inputs)

**Gate:** All criteria met → Journey is "done"

---

### Platform Success (Holistic)

- ✅ All 27 intents verified (contract + enforcement + evidence)
- ✅ All 7 journeys verified (all 5 scenarios)
- ✅ No violations remaining (comprehensive audit)
- ✅ All enforcement active (enforcement verification)
- ✅ All tests passing (E2E 3D tests)
- ✅ Independent verification (CTO/CIO review)

**Gate:** All criteria met → Platform is "done"

---

## Timeline

**Total Estimated Time:** 16-22 days

**Breakdown:**
- Phase 1: Intent Audit & Contract Creation - 3-4 days
- Phase 2: Intent Fixes with Enforcement - 7-10 days
- Phase 3: Journey Testing with Adversarial Scenarios - 4-5 days
- Phase 4: Platform Verification - 2-3 days

**Priority:** 🔴 **HIGHEST** - Start immediately

---

## Next Steps

1. ✅ **Acknowledge pivot** - Intent/journey-based approach
2. ✅ **Acknowledge traps** - Prevent micro-phases and demo flows
3. ✅ **Create workplan** - This document
4. ⏭️ **Get approval** - Review with CTO/CIO
5. ⏭️ **Start Phase 1** - Intent audit & contract creation
6. ⏭️ **Execute workplan** - Fix platform + verify fixes work

---

**Prepared By:** Development Team  
**Date:** January 25, 2026  
**Status:** 🔴 **CRITICAL - READY FOR EXECUTION**
