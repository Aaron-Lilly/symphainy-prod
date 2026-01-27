# Phase 5: Expertise Building Plan

**Date:** January 25, 2026  
**Goal:** Become absolute platform experts before creating holistic 3D test suite  
**Status:** 📋 **PLANNING**

---

## Executive Summary

To create a comprehensive holistic 3D test suite for all intents and user journeys, we need to deeply understand:
1. **Complete E2E system flow** - How data moves through the platform
2. **Four-class data architecture** - Working Materials, Records of Fact, Purpose-Bound Outcomes, Ephemeral
3. **TTL enforcement** - How temporary data is managed
4. **Records of Fact promotion** - How data becomes persistent
5. **Intent-to-execution flow** - Complete journey from user action to system state

This plan outlines a progressive approach to building this expertise while completing the remaining Phase 5 tasks.

---

## Recommended Approach: Progressive Expertise Building

### Phase 5.4 → 5.2 → 5.1 (Document → Understand Data Lifecycle → Understand Retention)

**Rationale:**
1. **Start with documentation** (5.4) to capture current understanding and identify gaps
2. **Understand data promotion** (5.2) to see how data becomes persistent
3. **Understand data retention** (5.1) to see how temporary data is managed
4. **Create comprehensive system flow documentation** as we learn
5. **Then create holistic 3D test suite** with complete understanding

---

## Task 5.4: Code Quality & Documentation (START HERE)

**Goal:** Document current state, identify gaps, create foundation for expertise

### Step 1: System Flow Documentation (2-3 hours)

**Action:**
1. **Map all intents** - Create comprehensive intent catalog
   - Content realm intents (ingest_file, parse_content, extract_embeddings, etc.)
   - Insights realm intents (visualize_lineage, map_relationships, assess_data_quality, etc.)
   - Journey realm intents (optimize_coexistence_with_content, create_workflow, etc.)
   - Outcomes realm intents (synthesize_outcome, create_poc, generate_roadmap, etc.)

2. **Map user journeys** - Document complete flows
   - File upload → Parse → Embeddings → Interpretation → Analysis
   - SOP/Workflow → Coexistence Analysis → Blueprint → Artifact
   - Content + Insights + Journey → Synthesis → Roadmap/POC

3. **Map data flow** - Document how data moves through system
   - Working Materials (temporary) → Records of Fact (persistent)
   - Ephemeral state → Realm state → Runtime state
   - Intent → Execution → Artifact → State update

4. **Create intent-to-execution flow diagrams**
   - Frontend → API Manager → Experience Plane Client → Runtime
   - Runtime → Realm Orchestrator → Realm Services → Public Works
   - Public Works → Infrastructure (Supabase, GCS, etc.)

### Step 2: Code Audit & Cleanup (1-2 hours)

**Action:**
1. Remove all remaining TODOs
2. Add comprehensive docstrings to new code
3. Document intent parameters (already done in INTENT_PARAMETER_SPECIFICATION.md)
4. Document state authority model (already done in STATE_AUTHORITY_MODEL.md)

### Step 3: Architecture Documentation Updates (1 hour)

**Action:**
1. Update architecture docs with learnings from Phases 0-4
2. Document four-class data architecture
3. Create system flow diagrams
4. Document intent-to-execution patterns

**Deliverables:**
- `COMPLETE_INTENT_CATALOG.md` - All intents documented
- `USER_JOURNEY_FLOWS.md` - All user journeys mapped
- `DATA_LIFECYCLE_FLOW.md` - How data moves through system
- `INTENT_TO_EXECUTION_FLOW.md` - Complete execution path
- Updated architecture documentation

**Estimated Time:** 4-6 hours

---

## Task 5.2: Complete Records of Fact Promotion (UNDERSTAND DATA PROMOTION)

**Goal:** Understand how temporary data (Working Materials) becomes persistent (Records of Fact)

### Step 1: Audit Current Implementation (1-2 hours)

**Action:**
1. **Find all embedding creation points**
   - Where are embeddings created? (extract_embeddings intent)
   - Are they stored as Working Materials or Records of Fact?
   - What triggers promotion to Records of Fact?

2. **Find all interpretation creation points**
   - Where are interpretations created? (interpret_data_self_discovery, interpret_data_guided)
   - Are they stored as Working Materials or Records of Fact?
   - What triggers promotion to Records of Fact?

3. **Document promotion workflow**
   - What conditions trigger promotion?
   - Is promotion automatic or manual?
   - Where does promotion happen? (Realm services, orchestrators?)

### Step 2: Understand Data Architecture (1-2 hours)

**Action:**
1. **Document four-class data architecture**
   - **Working Materials**: Temporary, TTL-based, purged automatically
   - **Records of Fact**: Persistent, promoted from Working Materials
   - **Purpose-Bound Outcomes**: Artifacts with lifecycle (roadmaps, POCs, blueprints)
   - **Ephemeral**: Session state, UI state, not persisted

2. **Map data transitions**
   - Working Materials → Records of Fact (promotion)
   - Records of Fact → Purpose-Bound Outcomes (artifact creation)
   - Ephemeral → Working Materials (intent execution)

3. **Document storage locations**
   - Where are Working Materials stored? (Supabase? GCS?)
   - Where are Records of Fact stored? (Supabase? GCS?)
   - How are they differentiated?

### Step 3: Verify/Implement Promotion (2-3 hours)

**Action:**
1. **Verify embeddings promotion**
   - Check if embeddings are stored as Records of Fact
   - If not, implement promotion logic
   - Test promotion workflow

2. **Verify interpretations promotion**
   - Check if interpretations are stored as Records of Fact
   - If not, implement promotion logic
   - Test promotion workflow

3. **Create promotion tests**
   - Test Working Materials → Records of Fact transition
   - Test promotion conditions
   - Test persistence

**Deliverables:**
- `DATA_PROMOTION_WORKFLOW.md` - How data is promoted
- `FOUR_CLASS_DATA_ARCHITECTURE.md` - Complete data architecture
- Promotion implementation (if needed)
- Promotion tests

**Estimated Time:** 4-7 hours

---

## Task 5.1: Implement TTL Enforcement (UNDERSTAND DATA RETENTION)

**Goal:** Understand how temporary data (Working Materials) is managed and purged

### Step 1: Understand TTL Tracking (1-2 hours)

**Action:**
1. **Find TTL tracking implementation**
   - Where is TTL tracked? (boundary contracts? database?)
   - How is TTL calculated? (from creation time? from last access?)
   - What TTL values are used? (different for different data types?)

2. **Document TTL model**
   - What data has TTL? (Working Materials only?)
   - How is TTL stored? (metadata? separate table?)
   - What happens when TTL expires? (marked for deletion? auto-deleted?)

3. **Map TTL enforcement points**
   - Where should TTL be enforced? (background job? on access?)
   - Who enforces TTL? (Public Works? Realm services?)

### Step 2: Design TTL Enforcement (1-2 hours)

**Action:**
1. **Design purge job**
   - When should it run? (scheduled? on-demand?)
   - How should it identify expired data? (query by TTL? scan all?)
   - What should it do? (delete? archive? mark as expired?)

2. **Design enforcement logic**
   - Should enforcement be automatic or manual?
   - Should there be safeguards? (don't purge if referenced?)
   - Should there be notifications? (log? alert?)

3. **Design testing strategy**
   - How to test TTL enforcement?
   - How to test purge job?
   - How to test safeguards?

### Step 3: Implement TTL Enforcement (2-3 hours)

**Action:**
1. **Create automated purge job**
   - Implement scheduled job
   - Implement purge logic
   - Add safeguards

2. **Enforce TTL based on boundary contracts**
   - Read TTL from boundary contracts
   - Apply TTL to Working Materials
   - Enforce TTL on access (if needed)

3. **Test purge automation**
   - Test purge job execution
   - Test TTL enforcement
   - Test safeguards

**Deliverables:**
- `TTL_ENFORCEMENT_DESIGN.md` - TTL enforcement design
- `TTL_PURGE_JOB.md` - Purge job implementation
- TTL enforcement implementation
- TTL enforcement tests

**Estimated Time:** 4-7 hours

---

## Comprehensive System Flow Documentation

**After completing all three tasks, create:**

### 1. Complete E2E System Flow Document

**Content:**
- All intents mapped to execution paths
- All user journeys documented
- All data flows documented
- All state transitions documented
- All boundary crossings documented

### 2. Holistic 3D Test Suite Design

**Content:**
- Test matrix for all intents
- Test matrix for all user journeys
- Test matrix for all data flows
- Test matrix for all state transitions
- Test matrix for all boundary crossings

**Estimated Time:** 4-6 hours

---

## Total Estimated Time

- **Task 5.4:** 4-6 hours
- **Task 5.2:** 4-7 hours
- **Task 5.1:** 4-7 hours
- **System Flow Documentation:** 4-6 hours
- **Holistic 3D Test Suite Design:** 4-6 hours

**Total:** 20-32 hours (2.5-4 days)

---

## Success Criteria

### Task 5.4
- ✅ Complete intent catalog created
- ✅ All user journeys documented
- ✅ All data flows documented
- ✅ All code documented
- ✅ Architecture documentation updated

### Task 5.2
- ✅ Four-class data architecture documented
- ✅ Promotion workflow understood and documented
- ✅ All embeddings stored as Records of Fact
- ✅ All interpretations stored as Records of Fact
- ✅ Promotion tests passing

### Task 5.1
- ✅ TTL tracking understood and documented
- ✅ TTL enforcement designed and documented
- ✅ Automated purge job implemented
- ✅ TTL enforcement tests passing

### Overall
- ✅ Complete E2E system flow documented
- ✅ Platform expertise achieved
- ✅ Ready to create holistic 3D test suite

---

## Next Steps

1. **Start with Task 5.4** - Document current state
2. **Proceed to Task 5.2** - Understand data promotion
3. **Proceed to Task 5.1** - Understand data retention
4. **Create comprehensive system flow documentation**
5. **Design holistic 3D test suite**
6. **Implement holistic 3D test suite**

---

**Prepared By:** Development Team  
**Date:** January 25, 2026  
**Status:** 📋 **READY TO BEGIN**
