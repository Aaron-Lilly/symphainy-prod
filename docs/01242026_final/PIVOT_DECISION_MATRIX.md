# Pivot Decision Matrix: Phase-Based vs Intent/Journey-Based

**Date:** January 25, 2026  
**Status:** 📋 **DECISION SUPPORT DOCUMENT**  
**Purpose:** Compare approaches to inform decision

---

## Comparison Matrix

| Aspect | Phase-Based Approach | Intent/Journey-Based Approach |
|--------|---------------------|------------------------------|
| **Alignment with Platform** | ❌ Arbitrary grouping | ✅ Matches platform structure (intents) |
| **Alignment with Users** | ❌ Users don't think in phases | ✅ Users think in journeys |
| **Alignment with 3D Testing** | ❌ SRE testing doesn't fit phases | ✅ 3D testing naturally fits journeys |
| **Uses Our Documentation** | ❌ Ignores intent/journey docs | ✅ Leverages all our documentation |
| **Enforcement** | ⚠️ Enforce per phase (arbitrary) | ✅ Enforce per intent (natural) |
| **Testing** | ⚠️ Test per phase (fragmented) | ✅ Test per journey (holistic) |
| **Verification** | ⚠️ Verify per phase (incomplete) | ✅ Verify per intent + journey (complete) |
| **Unknown Detection** | ❌ Hard to find unknowns | ✅ Boundary matrix, execution flow, chaos |
| **Maintenance** | ❌ Phases are temporary | ✅ Intents/journeys are permanent |

---

## Detailed Comparison

### 1. Alignment with Platform Architecture

**Phase-Based:**
- Phases are temporary organizational structure
- Platform is organized by intents (32+ intents)
- Mismatch: Fixing "Phase 1 violations" doesn't align with platform structure

**Intent/Journey-Based:**
- Intents are the atomic unit of the platform
- Platform is organized by intents
- Match: Fixing "all violations for `ingest_file` intent" aligns with platform structure

**Winner:** ✅ Intent/Journey-Based

---

### 2. Alignment with User Interaction

**Phase-Based:**
- Users don't think in phases
- Users think in journeys: "I want to upload a file and analyze it"
- Mismatch: Testing "Phase 1" doesn't match user experience

**Intent/Journey-Based:**
- Users think in journeys
- Our documentation maps 7 complete user journeys
- Match: Testing "File Upload & Processing" journey matches user experience

**Winner:** ✅ Intent/Journey-Based

---

### 3. Alignment with 3D Testing

**Phase-Based:**
- Functional: Can test per phase (but fragmented)
- Architectural: Can test per phase (but fragmented)
- SRE: **Doesn't fit phase boundaries** (system-wide)
- Problem: SRE testing is holistic, not phase-based

**Intent/Journey-Based:**
- Functional: Test journeys (user perspective) ✅
- Architectural: Test intent flow (system perspective) ✅
- SRE: Test boundaries (production perspective) ✅
- Match: All three dimensions test the same journey

**Winner:** ✅ Intent/Journey-Based

---

### 4. Uses Our Documentation

**Phase-Based:**
- Ignores `COMPLETE_INTENT_CATALOG.md` (27 intents)
- Ignores `USER_JOURNEY_FLOWS.md` (7 journeys)
- Ignores `INTENT_TO_EXECUTION_FLOW.md` (execution path)
- Problem: Doesn't leverage our comprehensive documentation

**Intent/Journey-Based:**
- Uses `COMPLETE_INTENT_CATALOG.md` as organizing principle
- Uses `USER_JOURNEY_FLOWS.md` as testing structure
- Uses `INTENT_TO_EXECUTION_FLOW.md` for verification
- Match: Leverages all our documentation

**Winner:** ✅ Intent/Journey-Based

---

### 5. Enforcement

**Phase-Based:**
- Enforce per phase (arbitrary grouping)
- Phase contracts exist but don't align with platform
- Problem: Enforcement doesn't match platform structure

**Intent/Journey-Based:**
- Enforce per intent (natural grouping)
- Intent contracts align with platform structure
- Match: Enforcement matches platform structure

**Winner:** ✅ Intent/Journey-Based

---

### 6. Testing

**Phase-Based:**
- Test per phase (fragmented)
- Phases don't represent complete user flows
- Problem: Testing phases doesn't ensure end-to-end correctness

**Intent/Journey-Based:**
- Test per journey (holistic)
- Journeys represent complete user flows
- Match: Testing journeys ensures end-to-end correctness

**Winner:** ✅ Intent/Journey-Based

---

### 7. Unknown Detection

**Phase-Based:**
- Hard to find unknowns across phases
- Phase boundaries are arbitrary
- Problem: Unknowns don't respect phase boundaries

**Intent/Journey-Based:**
- Boundary matrix: Test all intent combinations
- Execution flow: Trace complete journeys
- Chaos: Test journey failures
- Match: Unknown detection naturally fits journeys

**Winner:** ✅ Intent/Journey-Based

---

### 8. Maintenance

**Phase-Based:**
- Phases are temporary organizational structure
- Once phases are "complete", structure becomes irrelevant
- Problem: Phase contracts become legacy

**Intent/Journey-Based:**
- Intents/journeys are permanent platform structure
- Intent contracts remain relevant forever
- Match: Contracts align with permanent structure

**Winner:** ✅ Intent/Journey-Based

---

## Recommendation

### ✅ **PIVOT TO INTENT/JOURNEY-BASED APPROACH**

**Rationale:**
1. **Better Alignment:** Matches platform architecture, user interaction, and 3D testing
2. **Uses Documentation:** Leverages all our comprehensive documentation
3. **Natural Enforcement:** Enforcement per intent is natural
4. **Holistic Testing:** Testing per journey ensures end-to-end correctness
5. **Unknown Detection:** Boundary matrix, execution flow, chaos testing naturally fit journeys
6. **Maintainable:** Intent/journey contracts remain relevant forever

---

## Migration Path

### Keep Phase Contracts (High-Level Guidance)

**Phase contracts remain as:**
- High-level architectural guidance
- Overall platform principles
- Success criteria for platform readiness

**But organize work by:**
- Intent contracts (detailed, per intent)
- Journey contracts (detailed, per journey)

---

### Organize Work by Intent/Journey

**Refactoring:**
- Fix violations per intent (not per phase)
- Test per journey (not per phase)
- Verify per intent/journey (not per phase)

**But maintain:**
- Phase contracts as high-level guidance
- Enforcement mechanisms (still needed)
- Proof tests (still needed)

---

## Success Criteria

### Intent-Based Success

- ✅ All 27 intents have contracts
- ✅ All 27 intents enforced
- ✅ All 27 intents tested (3D)
- ✅ All 27 intents verified

---

### Journey-Based Success

- ✅ All 7 journeys have contracts
- ✅ All 7 journeys tested (3D)
- ✅ All 7 journeys verified
- ✅ All 7 journeys handle failures

---

### Platform Success

- ✅ No violations remaining
- ✅ All enforcement active
- ✅ All tests passing
- ✅ Platform verified

---

**Prepared By:** Development Team  
**Date:** January 25, 2026  
**Status:** 📋 **DECISION SUPPORT - RECOMMEND PIVOT**
