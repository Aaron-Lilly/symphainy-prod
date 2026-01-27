# Intent-Based Refactoring Strategy

**Date:** January 25, 2026  
**Status:** 🔄 **PROPOSED PIVOT**  
**Priority:** 🔴 **HIGHEST** - Align with platform architecture

---

## Executive Summary

**Problem:** Phase-based refactoring doesn't align with how the platform actually works (intent-based) or how 3D testing works (holistic).

**Solution:** Pivot to **intent/user journey-based refactoring** that:
- Aligns with platform architecture (intent-based)
- Aligns with user interaction (journeys)
- Aligns with our comprehensive documentation
- Makes 3D testing natural (test each journey holistically)
- Makes enforcement natural (enforce per intent, not per phase)

**Key Insight:** The platform is organized by intents and journeys, not phases. Our refactoring should match.

---

## Why This Makes Sense

### 1. Platform Architecture is Intent-Based

**Reality:**
- Platform is organized around 32+ intents
- Every user action creates an intent
- Every intent flows through Runtime
- Intents are the atomic unit of the platform

**Current Approach:**
- Fix "Phase 1 violations" (arbitrary grouping)
- Fix "Phase 4 violations" (arbitrary grouping)

**Better Approach:**
- Fix "all violations for `ingest_file` intent"
- Fix "all violations for `analyze_structured_data` intent"
- Fix "all violations for `optimize_coexistence_with_content` intent"

---

### 2. User Interaction is Journey-Based

**Reality:**
- Users don't think in phases
- Users think in journeys: "I want to upload a file and analyze it"
- Our documentation already maps 7 complete user journeys

**Current Approach:**
- Fix violations across phases (fragmented)
- Test phases independently (doesn't match reality)

**Better Approach:**
- Fix "File Upload & Processing" journey end-to-end
- Fix "Data Quality & Interpretation" journey end-to-end
- Test each journey holistically (matches reality)

---

### 3. 3D Testing is Naturally Holistic

**Reality:**
- Functional testing: Test complete user journeys
- Architectural testing: Test intent flow end-to-end
- SRE testing: Test system boundaries (not phase boundaries)

**Current Approach:**
- Try to do 3D testing per-phase (doesn't work)
- SRE testing doesn't fit phase boundaries

**Better Approach:**
- Test each journey across all 3 dimensions
- SRE testing naturally fits journey boundaries
- Functional/Architectural/SRE all test the same journey

---

### 4. Our Documentation is Already Intent/Journey-Based

**Reality:**
- `COMPLETE_INTENT_CATALOG.md` - 32+ intents documented
- `USER_JOURNEY_FLOWS.md` - 7 journeys mapped
- `INTENT_TO_EXECUTION_FLOW.md` - 17-step execution path
- `DATA_LIFECYCLE_FLOW.md` - Four-class architecture

**Current Approach:**
- Ignore our comprehensive documentation
- Organize by arbitrary phases

**Better Approach:**
- Use our documentation as the organizing principle
- Fix violations per intent/journey
- Test per intent/journey

---

## Proposed Structure

### Intent-Based Refactoring

**Organize by Intent:**
- For each intent in `COMPLETE_INTENT_CATALOG.md`:
  1. Find all violations related to this intent
  2. Fix all violations for this intent
  3. Verify intent works correctly (3D testing)
  4. Enforce intent contract (phase contract per intent)

**Example:**
- Intent: `ingest_file`
  - Find violations: Direct API calls, missing validation, etc.
  - Fix violations: Migrate to intent-based API, add validation
  - Verify: Test file upload journey (3D)
  - Enforce: Intent contract (enforcement mechanisms)

---

### Journey-Based Testing

**Organize by User Journey:**
- For each journey in `USER_JOURNEY_FLOWS.md`:
  1. Test journey functionally (observable artifacts)
  2. Test journey architecturally (intent flow, enforcement)
  3. Test journey SRE (boundaries, chaos, state authority)

**Example:**
- Journey: "File Upload & Processing"
  - Functional: File uploaded, parsed, stored, visible in UI
  - Architectural: All intents use intent-based API, Runtime authority
  - SRE: Handles failures, state persists, boundaries work

---

## Intent Contract Structure

### Per-Intent Contract

Each intent must have:

1. **Invariants** (Positive + Negative)
   - Negative: No direct API calls, no missing validation
   - Positive: Intent flows through Runtime, has execution_id, updates realm state

2. **Enforcement Mechanism**
   - ESLint: Ban direct API calls for this intent
   - Runtime: Reject intent without required parameters
   - Test: Intentional violation must fail

3. **Proof**
   - Test: Intent works correctly (functional)
   - Test: Intent follows architecture (architectural)
   - Test: Intent handles failures (SRE)

---

## Journey Contract Structure

### Per-Journey Contract

Each journey must have:

1. **Invariants** (Positive + Negative)
   - Negative: No broken steps, no missing artifacts
   - Positive: Complete flow, observable artifacts, state persistence

2. **Enforcement Mechanism**
   - Test: Journey works end-to-end
   - Test: All intents in journey use intent-based API
   - Test: Journey handles failures gracefully

3. **Proof**
   - Test: Journey functionally (observable artifacts)
   - Test: Journey architecturally (intent flow)
   - Test: Journey SRE (boundaries, chaos)

---

## Refactoring Plan: Intent-Based

### Step 1: Audit by Intent

**For each intent in `COMPLETE_INTENT_CATALOG.md`:**

1. **Find violations:**
   - Direct API calls for this intent
   - Missing parameter validation
   - Missing session validation
   - Missing state updates
   - Missing error handling

2. **Categorize violations:**
   - Critical: Blocks intent execution
   - High: Breaks architectural compliance
   - Medium: Missing features
   - Low: Code quality

3. **Create intent contract:**
   - Define invariants
   - Design enforcement mechanisms
   - Create proof tests

**Deliverable:** Intent violation report + intent contracts

---

### Step 2: Fix by Intent

**For each intent:**

1. **Fix violations:**
   - Migrate to intent-based API
   - Add parameter validation
   - Add session validation
   - Add state updates
   - Add error handling

2. **Implement enforcement:**
   - ESLint rules
   - Runtime checks
   - Proof tests

3. **Verify intent works:**
   - Functional test: Observable artifacts
   - Architectural test: Intent flow
   - SRE test: Error handling

**Deliverable:** All intents fixed + enforced

---

### Step 3: Test by Journey

**For each journey in `USER_JOURNEY_FLOWS.md`:**

1. **Functional testing:**
   - Test complete journey
   - Verify observable artifacts
   - Verify state updates

2. **Architectural testing:**
   - Test intent flow
   - Verify Runtime authority
   - Verify enforcement mechanisms

3. **SRE testing:**
   - Test boundaries
   - Test chaos scenarios
   - Test state authority

**Deliverable:** Journey test results

---

### Step 4: Verify Platform

**Holistic verification:**

1. **All intents verified:**
   - All intents work correctly
   - All intents enforced
   - All intents tested

2. **All journeys verified:**
   - All journeys work end-to-end
   - All journeys tested (3D)
   - All journeys handle failures

3. **Platform verified:**
   - No violations remaining
   - All enforcement active
   - All tests passing

**Deliverable:** Platform verification report

---

## Benefits of This Approach

### 1. Aligns with Platform Architecture

- Intents are the atomic unit
- Fixing by intent matches platform structure
- Enforcement per intent is natural

---

### 2. Aligns with User Interaction

- Users think in journeys
- Testing by journey matches user experience
- Fixing by journey ensures end-to-end correctness

---

### 3. Aligns with 3D Testing

- Functional: Test journeys (user perspective)
- Architectural: Test intent flow (system perspective)
- SRE: Test boundaries (production perspective)
- All three dimensions test the same journey

---

### 4. Uses Our Documentation

- Leverages `COMPLETE_INTENT_CATALOG.md`
- Leverages `USER_JOURNEY_FLOWS.md`
- Leverages `INTENT_TO_EXECUTION_FLOW.md`
- Leverages `DATA_LIFECYCLE_FLOW.md`

---

### 5. Makes Enforcement Natural

- Enforce per intent (not per phase)
- Intent contracts are natural
- Journey contracts are natural
- Enforcement aligns with platform structure

---

## Example: `ingest_file` Intent Refactoring

### Step 1: Audit

**Find violations:**
- Direct API calls to `/api/v1/content/upload-file`
- Missing parameter validation
- Missing session validation
- Missing state updates

**Create intent contract:**
- Invariants: No direct API calls, must use `submitIntent()`, must update realm state
- Enforcement: ESLint rule, Runtime check
- Proof: Test intentional violation fails

---

### Step 2: Fix

**Fix violations:**
- Migrate to `ContentAPIManager.uploadFile()` using `submitIntent()`
- Add parameter validation: `if (!file) throw new Error(...)`
- Add session validation: `validateSession(platformState, "upload file")`
- Add state update: `setRealmState("content", "files", ...)`

**Implement enforcement:**
- ESLint rule: Ban `fetch('/api/v1/content/upload-file')`
- Runtime check: Reject intent without file parameter
- Proof test: Try direct API call → Must fail

---

### Step 3: Test

**Functional:**
- Upload file → File appears in UI
- Upload file → File stored in realm state
- Upload file → File metadata visible

**Architectural:**
- Upload file → Intent flows through Runtime
- Upload file → Execution_id traceable
- Upload file → State updates correctly

**SRE:**
- Upload file → Handles network failure
- Upload file → Handles storage failure
- Upload file → State persists across refresh

---

## Example: "File Upload & Processing" Journey

### Journey Steps

1. User uploads file (`ingest_file` intent)
2. File parsed (`parse_file` intent)
3. File analyzed (`analyze_structured_data` intent)
4. Results displayed (realm state → UI)

### 3D Testing

**Functional:**
- Complete journey works
- Observable artifacts at each step
- State updates correctly

**Architectural:**
- All intents use intent-based API
- All intents flow through Runtime
- All intents have execution_id

**SRE:**
- Journey handles failures
- State persists across steps
- Boundaries work correctly

---

## Migration from Phase-Based to Intent-Based

### Phase Contracts → Intent Contracts

**Keep:**
- Phase contracts as high-level guidance
- Enforcement mechanisms (still needed)
- Proof tests (still needed)

**Change:**
- Organize work by intent, not phase
- Test by journey, not phase
- Verify by intent/journey, not phase

---

### Phase Verification → Intent/Journey Verification

**Keep:**
- Comprehensive verification
- Automated testing
- Independent review

**Change:**
- Verify per intent (not per phase)
- Test per journey (not per phase)
- Report per intent/journey (not per phase)

---

## Success Criteria

### Intent-Based Criteria

- ✅ All intents have contracts
- ✅ All intents enforced
- ✅ All intents tested (3D)
- ✅ All intents verified

---

### Journey-Based Criteria

- ✅ All journeys have contracts
- ✅ All journeys tested (3D)
- ✅ All journeys verified
- ✅ All journeys handle failures

---

### Platform Criteria

- ✅ No violations remaining
- ✅ All enforcement active
- ✅ All tests passing
- ✅ Platform verified

---

## Next Steps

1. ✅ **Acknowledge pivot** - Intent/journey-based approach
2. ⏭️ **Create intent contracts** - For all 32+ intents
3. ⏭️ **Create journey contracts** - For all 7 journeys
4. ⏭️ **Audit by intent** - Find violations per intent
5. ⏭️ **Fix by intent** - Fix violations per intent
6. ⏭️ **Test by journey** - Test journeys (3D)
7. ⏭️ **Verify platform** - Holistic verification

---

**Prepared By:** Development Team  
**Date:** January 25, 2026  
**Status:** 🔄 **PROPOSED PIVOT - INTENT/JOURNEY-BASED APPROACH**
