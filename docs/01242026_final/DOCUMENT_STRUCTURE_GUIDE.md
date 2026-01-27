# Document Structure Guide

**Date:** January 25, 2026  
**Status:** 📋 **REFERENCE**  
**Purpose:** Explain how all documents work together

---

## Document Hierarchy

### Master Execution Plan

**`END_OF_JOB_WORKPLAN.md`** - **PRIMARY EXECUTION PLAN**
- Day-by-day execution plan
- Detailed phase breakdown
- Daily checkpoints
- Risk mitigation
- **Use this as the main workplan**

---

### Supporting Documents

**`INTENT_JOURNEY_REFACTORING_WORKPLAN.md`** - **STRATEGIC OVERVIEW**
- High-level approach
- Workplan structure
- Execution phases
- Success criteria
- **Use this for strategic understanding**

**`INTENT_CONTRACT_TEMPLATE.md`** - **TEMPLATE FOR INTENT CONTRACTS**
- Template to fill out for each of 27 intents
- Sections: Contract, Enforcement, Journey Evidence, Violations, Fixes, Verification, Gate Status
- **Use this to create intent contracts**

**`JOURNEY_CONTRACT_TEMPLATE.md`** - **TEMPLATE FOR JOURNEY CONTRACTS**
- Template to fill out for each of 7 journeys
- Sections: Overview, 5 Scenarios (Happy Path, Injected Failure, Partial Success, Retry/Recovery, Boundary Violation), Verification, Gate Status
- **Use this to create journey contracts**

---

## How They Work Together

### Phase 1: Intent Audit & Contract Creation

**Use:**
- `INTENT_CONTRACT_TEMPLATE.md` - Create contract for each intent
- `COMPLETE_INTENT_CATALOG.md` - Reference for intent details
- `USER_JOURNEY_FLOWS.md` - Identify which journeys use each intent

**Output:**
- 27 intent contracts (one per intent, using template)
- Violation reports per intent
- Priority ranking

---

### Phase 2: Intent Fixes with Enforcement

**Use:**
- `INTENT_CONTRACT_TEMPLATE.md` - Track fixes and verification per intent
- `END_OF_JOB_WORKPLAN.md` - Day-by-day execution plan

**Output:**
- All intents fixed + enforced + verified
- Journey evidence for all intents

---

### Phase 3: Journey Testing with Adversarial Scenarios

**Use:**
- `JOURNEY_CONTRACT_TEMPLATE.md` - Create contract for each journey
- `USER_JOURNEY_FLOWS.md` - Reference for journey details
- `END_OF_JOB_WORKPLAN.md` - Day-by-day execution plan

**Output:**
- 7 journey contracts (one per journey, using template)
- All journeys tested (all 5 scenarios)
- Journey test results

---

### Phase 4: Platform Verification

**Use:**
- `END_OF_JOB_WORKPLAN.md` - Verification checklist
- All intent contracts - Verify all intents
- All journey contracts - Verify all journeys

**Output:**
- Platform verification report
- Test results (all passing)
- Independent verification

---

## Document Relationships

```
END_OF_JOB_WORKPLAN.md (Master Plan)
  ├── Uses: INTENT_CONTRACT_TEMPLATE.md (for each intent)
  ├── Uses: JOURNEY_CONTRACT_TEMPLATE.md (for each journey)
  ├── References: COMPLETE_INTENT_CATALOG.md (27 intents)
  └── References: USER_JOURNEY_FLOWS.md (7 journeys)

INTENT_JOURNEY_REFACTORING_WORKPLAN.md (Strategic Overview)
  └── Provides: High-level approach and structure

INTENT_CONTRACT_TEMPLATE.md (Template)
  └── Used to create: 27 intent contracts

JOURNEY_CONTRACT_TEMPLATE.md (Template)
  └── Used to create: 7 journey contracts
```

---

## Usage Guide

### Starting the Work

1. **Read:** `END_OF_JOB_WORKPLAN.md` - Understand the day-by-day plan
2. **Read:** `INTENT_JOURNEY_REFACTORING_WORKPLAN.md` - Understand the strategic approach
3. **Start Phase 1:** Use `INTENT_CONTRACT_TEMPLATE.md` to create contracts for all 27 intents

### During Execution

**For each intent:**
- Copy `INTENT_CONTRACT_TEMPLATE.md`
- Fill out contract details
- Track violations, fixes, verification
- Update gate status

**For each journey:**
- Copy `JOURNEY_CONTRACT_TEMPLATE.md`
- Fill out journey details
- Test all 5 scenarios
- Update gate status

**Daily:**
- Follow `END_OF_JOB_WORKPLAN.md` day-by-day plan
- Update progress
- Report blockers

---

## Key Documents Summary

| Document | Purpose | When to Use |
|----------|---------|-------------|
| `END_OF_JOB_WORKPLAN.md` | Master execution plan | Daily execution |
| `INTENT_JOURNEY_REFACTORING_WORKPLAN.md` | Strategic overview | Understanding approach |
| `INTENT_CONTRACT_TEMPLATE.md` | Intent contract template | Creating intent contracts |
| `JOURNEY_CONTRACT_TEMPLATE.md` | Journey contract template | Creating journey contracts |
| `COMPLETE_INTENT_CATALOG.md` | Intent reference | Looking up intent details |
| `USER_JOURNEY_FLOWS.md` | Journey reference | Looking up journey details |

---

**Prepared By:** Development Team  
**Date:** January 25, 2026  
**Status:** 📋 **REFERENCE DOCUMENT**
