# Architecture Documentation Updates Required

**Date:** January 20, 2026  
**Status:** 📋 **Documentation Alignment**  
**Purpose:** Specific updates needed for each architecture document

---

## Document 1: North Star Architecture Guide

**File:** `docs/architecture/north_star.md`

### Updates Required

#### ✅ Section 2.2: Civic Systems - ADD Artifact Plane

**Location:** After Smart City, Experience, Agentic, Platform SDK

**Add:**
```markdown
### Artifact Plane (Purpose-Bound Outcomes Management)

> **Artifact Plane manages intentional deliverables as first-class citizens.**

The Artifact Plane is a Civic System that provides lifecycle management for Purpose-Bound Outcomes.

**What It Manages:**
- Roadmaps, POCs, solutions (Outcomes Realm)
- Blueprints, SOPs, workflows (Journey Realm)
- Reports, visualizations as deliverables (Insights Realm)

**Key Properties:**
- Owner (client/platform/shared)
- Purpose (decision support, delivery, governance, learning)
- Lifecycle states (draft → accepted → obsolete)
- Optional persistence of source materials

**Infrastructure:**
- Supabase metadata registry
- GCS/document store for payloads
- ArangoDB for lineage

**Not For:**
- Source files (FMS handles these - Working Materials)
- Raw data (Data Steward handles these)
- Execution state (Runtime handles this)
- Platform DNA (Solution/Intent/Realm registries handle these)
```

---

#### ✅ Section 4.1: Smart City - EXPAND Data Steward

**Location:** In "Canonical Smart City Roles" table and add detailed section

**Update Table:**
- Add row for Data Steward with expanded responsibilities

**Add New Section After Table:**
```markdown
#### Data Steward (Data Boundaries & Materialization)

**Responsibilities:**
- Boundary contract negotiation (`request_data_access()`)
- Materialization authorization (`authorize_materialization()`)
- Materialization policy evaluation
- TTL enforcement for Working Materials
- "Data stays at door" enforcement

**Two-Phase Materialization Flow:**

1. **Request Data Access** (`request_data_access()`)
   - Negotiate boundary contract
   - Determine if access is granted
   - Create contract in `data_boundary_contracts` table
   - Returns: `DataAccessRequest` with `contract_id`

2. **Authorize Materialization** (`authorize_materialization()`)
   - Evaluate materialization policy
   - Determine materialization type
   - Set TTL and scope
   - Update boundary contract with materialization decision
   - Returns: `MaterializationAuthorization`

**Materialization Types:**
- `reference` - Reference only, no materialization
- `partial_extraction` - Extract specific fields
- `deterministic` - Deterministic representation (becomes Record of Fact)
- `semantic_embedding` - Semantic embedding (becomes Record of Fact)
- `full_artifact` - Full artifact (Working Material, TTL-bound)

**Policy Evaluation:**
- Materialization policy is tenant-scoped
- Policy determines: type, scope, TTL, backing store
- Policy evaluation happens in Data Steward Primitives (not Runtime)
- Runtime consumes policy decisions, doesn't make them
```

---

#### ✅ Section 7: Data Brain - REPLACE with Four-Class Framework

**Location:** Replace entire Section 7

**Replace With:**
```markdown
## 7. The Data Framework (Four Classes by Time + Purpose)

> **Data is classified by time (how long it exists) and purpose (why it exists).**

The platform manages four distinct classes of data, each with different lifecycle, governance, and infrastructure.

### 7.1 Working Materials (Temporary)

**Definition:** Temporarily materialized data for understanding, parsing, and assessment.

**Properties:**
- Time-bound (TTL enforced by policy)
- Policy-bound (boundary contract required)
- Explicitly non-archival
- Exists only to enable transformation

**Infrastructure:**
- **Storage:** GCS (temporary), Supabase (tracking, status, audit)
- **TTL:** Enforced by automated purge job
- **Purge:** Automated when TTL expires

**Platform Components:**
- Content Realm FMS (file ingestion, parsing)
- Boundary contracts (govern access and TTL)
- Materialization policy (determines TTL)

**Examples:**
- Raw uploaded files
- Parsed file results (temporary)
- Intermediate schemas
- Reviewable previews

**Transition:** Working Materials → Records of Fact (via explicit `promote_to_record_of_fact()` workflow)

---

### 7.2 Records of Fact (Persistent Meaning)

**Definition:** Persistent, auditable, and reproducible conclusions or interpreted meaning.

**Properties:**
- Must persist (auditable, reproducible)
- Do NOT require original file to persist
- May reference expired source artifacts
- Represent "what the system concluded, at that moment, under those policies"

**Key Principle:**
> **Persistence of meaning ≠ persistence of material**

**Infrastructure:**
- **Storage:** Supabase (structured data), ArangoDB (graph/lineage, embeddings)
- **No raw files required** (meaning persists independently)

**Platform Components:**
- Data Steward (manages embeddings, interpretations)
- SemanticDataAbstraction (stores embeddings in ArangoDB)
- Insights Realm (creates interpretations)

**Examples:**
- Deterministic embeddings
- Semantic embeddings
- Interpreted meaning (entities, relationships)
- Data quality conclusions

**Promotion Workflow:**
1. Working Material exists (with boundary contract)
2. Explicit `promote_to_record_of_fact()` via Data Steward SDK
3. Requires boundary contract with `materialization_type="deterministic"` or `"semantic_embedding"`
4. Creates persistent Record of Fact entry
5. Links to source Working Material (which may expire later)
6. Record of Fact persists even if source expires

**Lineage:**
- Records of Fact store `source_file_id` and `source_expired_at` (nullable)
- When Working Material expires, update Records of Fact with `source_expired_at`
- Records of Fact remain valid even if source expired

---

### 7.3 Purpose-Bound Outcomes (Intentional Deliverables)

**Definition:** Intentional artifacts created for a specific purpose and audience.

**Properties:**
- Owner (client/platform/shared)
- Purpose (decision support, delivery, governance, learning)
- Lifecycle states (draft → accepted → obsolete)
- May be reused, revised, or discarded
- May feed platform but are not the platform

**Infrastructure:**
- **Storage:** Artifact Plane (Supabase metadata + GCS/document store for payloads)
- **Lifecycle:** Tracked in Artifact Plane registry

**Platform Components:**
- Artifact Plane (manages Purpose-Bound Outcomes)
- Outcomes Realm (roadmaps, POCs, solutions)
- Journey Realm (blueprints, SOPs, workflows)
- Insights Realm (reports, visualizations as deliverables)

**Examples:**
- Roadmaps
- POCs
- Blueprints
- SOPs
- Quality assessment reports (as deliverables)
- Business analysis reports

**Lifecycle State Machine:**
- `draft` → `accepted` (owner or authorized user)
- `draft` → `obsolete` (owner or authorized user)
- `accepted` → `obsolete` (owner or authorized user)
- Transitions are policy-governed
- Tracked in Artifact Plane registry
- Transitions recorded in WAL for audit

**Versioning:**
- When artifact transitions to `accepted`, create immutable version
- Store versions in Artifact Plane registry
- Link versions via `parent_artifact_id`
- Current version tracked in registry

---

### 7.4 Platform DNA (Generalized Capability)

**Definition:** Generalized, curated, de-identified capabilities promoted from outcomes.

**Properties:**
- De-identified (no client context)
- Generalizable (reusable across clients)
- Policy-approved (Curator validates)
- Abstracted from client context
- Versioned, curated, immutable

**Infrastructure:**
- **Storage:** Supabase registries (versioned, immutable)
- **Promotion:** Via Curator role (deliberate act)

**Platform Components:**
- Curator (validates promotion)
- Solution Registry
- Intent Registry
- Realm Registry

**Examples:**
- New intents (promoted from outcomes)
- New realms (promoted from outcomes)
- New journeys (promoted from outcomes)
- New solutions (promoted from outcomes)
- New capabilities (promoted from outcomes)

**Promotion Workflow:**
1. **Promotion Request:** User/agent requests promotion of Purpose-Bound Outcome
2. **Curator Validation:** Curator validates promotion criteria:
   - Is it de-identified?
   - Is it generalizable?
   - Does it meet policy requirements?
3. **Generalization:** System generalizes outcome (removes client context)
4. **Registry Entry:** Creates entry in appropriate registry (Solution, Intent, Realm, etc.)
5. **Versioning:** Creates versioned, immutable registry entry

**Promotion Criteria:**
- De-identified
- Generalizable
- Policy-approved
- Abstracted from client context

---

### 7.5 Data Flow (End-to-End)

```
Client Working Material (External)
    ↓ (Experience → Smart City)
Boundary Contract Negotiation
    ↓ (Data Steward: request_data_access)
Access Granted?
    ↓ (Data Steward: authorize_materialization)
Materialization Decision
    ├─ reference (no materialization)
    ├─ partial_extraction (Working Material)
    ├─ deterministic (→ Record of Fact)
    ├─ semantic_embedding (→ Record of Fact)
    └─ full_artifact (Working Material, TTL-bound)
    ↓
Working Material (FMS: GCS + Supabase, TTL-bound)
    ↓ (explicit promotion via Data Steward SDK)
Records of Fact (Supabase + ArangoDB, persistent)
    ↓ (realm processing)
Purpose-Bound Outcomes (Artifact Plane)
    ↓ (optional, deliberate promotion via Curator)
Platform DNA (Supabase registries)
```

**Key Principles:**
- Each arrow is **policy-mediated**. Nothing moves automatically.
- **Persistence of meaning ≠ persistence of material**
- Working Materials expire, Records of Fact persist
- Purpose-Bound Outcomes have lifecycle, Platform DNA is immutable
```

---

#### ✅ Section 4.1: Smart City - ADD Curator Promotion Details

**Location:** In Curator role description

**Add:**
```markdown
#### Curator (Capability Promotion)

**Responsibilities:**
- Validates promotion of Purpose-Bound Outcomes → Platform DNA
- Manages capability registries (Solution, Intent, Realm)
- Ensures de-identification and generalization
- Policy approval for promotions

**Promotion Process:**
1. Receive promotion request
2. Validate promotion criteria (de-identified, generalizable, policy-approved)
3. Generalize outcome (remove client context)
4. Create registry entry (versioned, immutable)
5. Return promotion result
```

---

### Summary of Changes to `north_star.md`

1. ✅ Add Artifact Plane to Section 2.2 (Civic Systems)
2. ✅ Expand Data Steward in Section 4.1 (Smart City)
3. ✅ Replace Section 7 (Data Brain) with Four-Class Framework
4. ✅ Add Curator promotion details to Section 4.1
5. ✅ Document materialization policy flow
6. ✅ Document lifecycle state machine
7. ✅ Document promotion workflows

---

## Document 2: Platform Overview

**File:** `docs/PLATFORM_OVERVIEW.md`

### Updates Required

#### ✅ Add Section: Data Framework

**Location:** After "How Does It Work?" section (after line 125)

**Add:**
```markdown
## Data Framework: Four Classes by Time + Purpose

Symphainy classifies all data into four distinct classes based on **time** (how long it exists) and **purpose** (why it exists):

### Working Materials (Temporary)
- **What:** Raw files, parsed results, intermediate schemas
- **Properties:** Time-bound, policy-governed, non-archival
- **Storage:** FMS (GCS + Supabase tracking)
- **Lifecycle:** TTL enforced, automated purge when expired

### Records of Fact (Persistent Meaning)
- **What:** Embeddings, interpretations, conclusions
- **Properties:** Persistent, auditable, reproducible
- **Storage:** Supabase (structured) + ArangoDB (graph/embeddings)
- **Key Principle:** Persistence of meaning ≠ persistence of material
- **Lifecycle:** Permanent (no expiration)

### Purpose-Bound Outcomes (Intentional Deliverables)
- **What:** Roadmaps, POCs, blueprints, SOPs, reports
- **Properties:** Created for someone, exist for a reason, lifecycle-managed
- **Storage:** Artifact Plane (Supabase metadata + GCS/document store)
- **Lifecycle:** draft → accepted → obsolete (policy-governed transitions)

### Platform DNA (Generalized Capability)
- **What:** Promoted solutions, intents, realms, capabilities
- **Properties:** De-identified, generalizable, curated, immutable
- **Storage:** Supabase registries (versioned)
- **Lifecycle:** Immutable once promoted

**Key Insight:**
> **The platform is allowed to remember conclusions without remembering materials, and allowed to create outcomes without absorbing them into its DNA.**
```

---

#### ✅ Update Section: "How Does It Work?"

**Location:** Section "2. Civic Systems — How work is coordinated safely"

**Update:**
- Add Artifact Plane to list of Civic Systems
- Clarify that Artifact Plane manages Purpose-Bound Outcomes

---

### Summary of Changes to `PLATFORM_OVERVIEW.md`

1. ✅ Add Data Framework section
2. ✅ Update Civic Systems section to include Artifact Plane
3. ✅ Add examples of each data class

---

## Document 3: Platform Rules

**File:** `docs/PLATFORM_RULES.md`

### Updates Required

#### ✅ Add Section: Data Classification Rules

**Location:** After "Public Works Pattern" section (after line 136)

**Add:**
```markdown
## 📊 Data Classification Rules

### Four-Class Framework

All data must be classified into one of four classes based on time and purpose:

1. **Working Materials** - Temporary, time-bound (FMS)
2. **Records of Fact** - Persistent meaning (Supabase + ArangoDB)
3. **Purpose-Bound Outcomes** - Intentional deliverables (Artifact Plane)
4. **Platform DNA** - Generalized capabilities (Supabase registries)

**Classification Rules:**
- ✅ Source files → Working Materials (FMS)
- ✅ Derived artifacts → Purpose-Bound Outcomes (Artifact Plane)
- ✅ Embeddings/interpretations → Records of Fact
- ✅ Promoted capabilities → Platform DNA
- ❌ No mixing classes in same storage
- ❌ No artifacts in execution state (only references)
- ❌ No Working Materials without TTL
- ❌ No Records of Fact with expiration

**Storage Rules:**
- Working Materials: FMS (GCS + Supabase)
- Records of Fact: Supabase + ArangoDB
- Purpose-Bound Outcomes: Artifact Plane
- Platform DNA: Supabase registries

**Transition Rules:**
- Working Material → Record of Fact: Explicit promotion via Data Steward SDK
- Purpose-Bound Outcome → Platform DNA: Explicit promotion via Curator
- All transitions are policy-governed
- All transitions recorded in WAL for audit
```

---

### Summary of Changes to `PLATFORM_RULES.md`

1. ✅ Add Data Classification Rules section
2. ✅ Document storage rules for each class
3. ✅ Document transition rules

---

## Document 4: Executive Narrative

**File:** `docs/PLATFORM_OVERVIEW_EXECUTIVE_NARRATIVE.md`

### Updates Required

#### ✅ Update Section: "2. Civic Systems"

**Location:** In list of Civic Systems

**Add:**
- Artifact Plane to list (manages Purpose-Bound Outcomes)

---

## Document 5: New Document: Data Framework Guide

**File:** `docs/architecture/data_framework.md` (NEW)

### Create New Document

**Purpose:** Detailed guide to the four-class data framework

**Content:**
- Full framework explanation
- Infrastructure mapping
- Transition workflows
- Examples for each class
- Policy governance
- Lifecycle management

**Estimated Time:** 4-6 hours

---

## Part 6: Open Questions Summary

### All Questions Answered

| Question | Recommended Answer | Status |
|----------|-------------------|--------|
| **Q1:** Where does materialization policy live? | Smart City Primitives (Data Steward) | ✅ Answered |
| **Q2:** How do we track lifecycle states? | Artifact Plane registry | ✅ Answered |
| **Q3:** How do we implement "promote to Record of Fact"? | Explicit workflow via Data Steward SDK | ✅ Answered |
| **Q4:** How do we handle lineage when source expires? | Reference preservation with expiration metadata | ✅ Answered |
| **Q5:** What's the promotion workflow for Platform DNA? | Explicit promotion via Curator | ✅ Answered |
| **Q6:** Should TTL enforcement be automated? | Yes, automated purge job | ✅ Answered |
| **Q7:** How do we distinguish Working Material vs Purpose-Bound Outcome? | By purpose: files = Working Material, analysis = Purpose-Bound Outcome | ✅ Answered |
| **Q8:** Should Artifact Plane support lifecycle transitions? | Yes, explicit state machine with policy governance | ✅ Answered |
| **Q9:** How do we handle cross-realm dependencies? | Artifact Plane as single source of truth | ✅ Answered |
| **Q10:** How do we handle vector search? | SemanticDataAbstraction with ArangoDB | ✅ Answered |
| **Q11:** Should materialization policy be tenant-scoped? | Yes, tenant-specific policies | ✅ Answered |
| **Q12:** How do we handle artifact versioning? | Versioning for accepted artifacts | ✅ Answered |
| **Q13:** Should Artifact Plane support search? | Yes, via registry queries | ✅ Answered |
| **Q14:** How do we handle artifact dependencies? | Lineage tracking in Artifact Plane | ✅ Answered |
| **Q15:** Should Records of Fact support expiration? | No, they are permanent | ✅ Answered |

---

## Part 7: Implementation Priority

### Phase 1: Documentation Updates (This Week)

**Priority:** 🔴 **CRITICAL** - Foundation for all future work

1. Update `north_star.md`:
   - Add Artifact Plane to Section 2.2
   - Expand Data Steward in Section 4.1
   - Replace Section 7 with Four-Class Framework
   - Add Curator promotion details

2. Update `PLATFORM_OVERVIEW.md`:
   - Add Data Framework section
   - Update Civic Systems section

3. Update `PLATFORM_RULES.md`:
   - Add Data Classification Rules

4. Create `data_framework.md`:
   - Detailed framework guide

**Estimated Time:** 12-16 hours

---

### Phase 2: Architecture Alignment (Next Week)

**Priority:** 🟡 **HIGH** - Aligns implementation with architecture

1. Implement lifecycle state tracking
2. Implement promotion workflows
3. Implement TTL enforcement
4. Remove MVP defaults

**Estimated Time:** 20-30 hours

---

## Success Criteria

### Documentation Complete When:
- ✅ All architectural evolutions documented in `north_star.md`
- ✅ Four-class framework fully integrated
- ✅ All open questions answered with recommended solutions
- ✅ Platform overview reflects current state
- ✅ Platform rules include data classification

### Architecture Bulletproof When:
- ✅ No MVP fallbacks in production code
- ✅ All data properly classified
- ✅ All transitions policy-governed
- ✅ All lifecycle states tracked
- ✅ All promotion workflows implemented

---

**Last Updated:** January 20, 2026
