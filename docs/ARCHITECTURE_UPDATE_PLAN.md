# Platform Architecture Update Plan

**Date:** January 20, 2026  
**Status:** 📋 **Architecture Alignment & Documentation Update**  
**Purpose:** Update architecture documents to reflect current platform state and four-class data framework

---

## Executive Summary

This document identifies:
1. **Architectural Evolutions** since last documentation update
2. **Four-Class Data Framework** integration requirements
3. **Open Architectural Questions** with recommended answers
4. **Documentation Updates** needed to align with current implementation

**Goal:** Ensure architecture documentation is bulletproof and captures the full platform vision.

---

## Part 1: Architectural Evolutions Since Last Update

### 1.1 Data Boundary Contracts (Implemented)

**Status:** ✅ **IMPLEMENTED** - Not fully documented in architecture guide

**What Changed:**
- Data Steward now owns boundary contract negotiation
- Two-phase materialization: `request_data_access()` → `authorize_materialization()`
- Boundary contracts stored in `data_boundary_contracts` table
- Materialization policy determines form (reference, partial, deterministic, semantic, full_artifact)

**Current Documentation:**
- `new_data_vision.md` describes the concept
- `data_boundary_implementation_summary.md` describes implementation
- `north_star.md` mentions Data Steward but doesn't detail boundary contracts

**Update Needed:**
- Add boundary contract flow to `north_star.md` Section 4.1 (Smart City)
- Document two-phase materialization pattern
- Clarify "data stays at door" principle

---

### 1.2 Artifact Plane (Implemented)

**Status:** ✅ **IMPLEMENTED** - Partially documented

**What Changed:**
- New `ArtifactPlane` civic system for Purpose-Bound Outcomes
- Outcomes Realm migrated (roadmaps, POCs)
- Journey Realm needs migration (blueprints, SOPs, workflows)
- Insights Realm needs migration (interpretations, reports)

**Current Documentation:**
- `ARTIFACT_PLANE_IMPLEMENTATION_PLAN.md` - Initial plan
- `ARTIFACT_PLANE_REALM_MIGRATION_PLAN.md` - Migration plan
- `north_star.md` - Doesn't mention Artifact Plane

**Update Needed:**
- Add Artifact Plane to `north_star.md` Section 2.2 (Civic Systems)
- Document Purpose-Bound Outcomes lifecycle
- Clarify Artifact Plane vs Execution State vs FMS

---

### 1.3 Four-Class Data Framework (Aligned, Not Documented)

**Status:** 🟡 **CONCEPTUALLY ALIGNED** - Not documented in architecture

**Framework:**
1. **Working Materials** - Temporary, time-bound (FMS)
2. **Records of Fact** - Persistent meaning (embeddings, interpretations)
3. **Purpose-Bound Outcomes** - Intentional deliverables (Artifact Plane)
4. **Platform DNA** - Generalized capabilities (Solution Registry, etc.)

**Current Documentation:**
- `new_data_vision.md` - Describes boundary contracts but not four-class framework
- `north_star.md` - Mentions Data Brain but doesn't detail four classes

**Update Needed:**
- Add four-class framework to `north_star.md` Section 7 (Data Brain)
- Document transitions between classes
- Map infrastructure to classes

---

### 1.4 Runtime Participation Contract (Implemented)

**Status:** ✅ **IMPLEMENTED** - Well documented

**What Changed:**
- All realms follow `handle_intent(intent, context) → { artifacts, events }` pattern
- Execution state stores artifact_id references, not full artifacts
- Artifacts stored in Artifact Plane

**Current Documentation:**
- `north_star.md` Section 3 - Documents contract well

**Update Needed:**
- ✅ Already documented - No changes needed

---

### 1.5 Materialization Policy (Moved to Smart City)

**Status:** 🟡 **PARTIALLY IMPLEMENTED** - Needs clarification

**What Changed:**
- Materialization policy evaluation moved to Data Steward Primitives
- Policy determines: type, scope, TTL, backing store
- Currently uses MVP defaults (needs real policy evaluation)

**Current Documentation:**
- `north_star.md` - Doesn't detail materialization policy
- `data_steward_primitives.py` - Has implementation but MVP defaults

**Update Needed:**
- Document materialization policy in `north_star.md` Section 4.1
- Clarify policy evaluation flow
- Document policy types (reference, partial, deterministic, semantic, full_artifact)

---

## Part 2: Four-Class Data Framework Integration

### 2.1 Framework Overview

**The Four Classes:**

```
Working Materials (Temporary)
    ↓ (policy + time)
Records of Fact (Persistent Meaning)
    ↓ (purpose + lifecycle)
Purpose-Bound Outcomes (Intentional Deliverables)
    ↓ (optional, deliberate promotion)
Platform DNA (Generalized Capability)
```

**Key Principle:**
> **Persistence of meaning ≠ persistence of material**

---

### 2.2 Class 1: Working Materials

**Definition:** Temporarily materialized data for understanding, parsing, and assessment.

**Properties:**
- Time-bound (TTL enforced)
- Policy-bound (boundary contract required)
- Explicitly non-archival
- Exists only to enable transformation

**Infrastructure:**
- **Storage:** GCS (temporary), Supabase (tracking, status, audit)
- **TTL:** Enforced by policy (via boundary contracts)
- **Purge:** Automated when TTL expires

**Platform Components:**
- **Content Realm FMS:** Handles file ingestion, parsing
- **Boundary Contracts:** Govern access and materialization
- **Materialization Policy:** Determines TTL and form

**Examples:**
- Raw uploaded files
- Parsed file results (temporary)
- Intermediate schemas
- Reviewable previews

**Documentation Location:**
- Add to `north_star.md` Section 7.1 (Data Brain - Working Materials)

---

### 2.3 Class 2: Records of Fact

**Definition:** Persistent, auditable, and reproducible conclusions or interpreted meaning.

**Properties:**
- Must persist (auditable, reproducible)
- Do NOT require original file to persist
- May reference expired source artifacts
- Represent "what the system concluded"

**Infrastructure:**
- **Storage:** Supabase (structured data), ArangoDB (graph/lineage)
- **No raw files required** (meaning persists independently)

**Platform Components:**
- **Data Steward:** Manages deterministic/semantic embeddings
- **SemanticDataAbstraction:** Stores embeddings in ArangoDB
- **Insights Realm:** Creates interpretations (Records of Fact)

**Examples:**
- Deterministic embeddings
- Semantic embeddings
- Interpreted meaning (entities, relationships)
- Data quality assessments (conclusions)

**Transition Trigger:**
- When embeddings are created OR when deterministic interpretation occurs
- Explicit "promote to Record of Fact" workflow needed

**Documentation Location:**
- Add to `north_star.md` Section 7.2 (Data Brain - Records of Fact)

---

### 2.4 Class 3: Purpose-Bound Outcomes

**Definition:** Intentional artifacts (deliverables) created for a specific purpose and audience.

**Properties:**
- Created for someone (owner: client/platform/shared)
- Exist for a reason (purpose: decision support, delivery, governance, learning)
- Lifecycle states (draft → accepted → obsolete)
- May be reused, revised, or discarded
- May feed platform but are not the platform

**Infrastructure:**
- **Storage:** Artifact Plane (Supabase metadata + GCS/document store for payloads)
- **Lifecycle:** Tracked in Artifact Plane registry

**Platform Components:**
- **Artifact Plane:** Manages Purpose-Bound Outcomes
- **Outcomes Realm:** Roadmaps, POCs, solutions
- **Journey Realm:** Blueprints, SOPs, workflows
- **Insights Realm:** Reports, visualizations (as deliverables)

**Examples:**
- Roadmaps
- POCs
- Blueprints
- SOPs
- Quality assessment reports (as deliverables)
- Business analysis reports

**Documentation Location:**
- Add to `north_star.md` Section 2.2 (Civic Systems - Artifact Plane)
- Update Section 7.3 (Data Brain - Purpose-Bound Outcomes)

---

### 2.5 Class 4: Platform DNA

**Definition:** Generalized, curated, de-identified capabilities promoted from outcomes.

**Properties:**
- De-identified (no client context)
- Generalizable (reusable across clients)
- Policy-approved (Curator validates)
- Abstracted away from client context
- Versioned, curated, immutable

**Infrastructure:**
- **Storage:** Supabase registries (versioned, immutable)
- **Promotion:** Via Curator role (deliberate act)

**Platform Components:**
- **Curator:** Validates promotion
- **Solution Registry:** Registered solutions
- **Intent Registry:** Registered intents
- **Realm Registry:** Registered realms

**Examples:**
- New intents (promoted from outcomes)
- New realms (promoted from outcomes)
- New journeys (promoted from outcomes)
- New solutions (promoted from outcomes)
- New capabilities (promoted from outcomes)

**Promotion Criteria:**
- De-identified
- Generalizable
- Policy-approved
- Abstracted from client context

**Documentation Location:**
- Add to `north_star.md` Section 4.1 (Smart City - Curator)
- Add to Section 7.4 (Data Brain - Platform DNA)

---

## Part 3: Open Architectural Questions & Recommended Answers

### Q1: Where Does Materialization Policy Live?

**Question:** Should materialization policy evaluation live in Runtime, Smart City Primitives, or a separate Policy Store?

**Current State:**
- Policy evaluation in `DataStewardPrimitives.authorize_materialization()`
- Uses `MaterializationPolicyStore` (optional parameter)
- Currently has MVP defaults

**Recommended Answer:**
✅ **Smart City Primitives (Data Steward)** - This is correct.

**Rationale:**
- Materialization is a governance decision (Smart City domain)
- Data Steward owns boundary contracts (policy enforcement)
- Runtime should consume policy decisions, not make them
- Separation of concerns: Smart City decides, Runtime enforces

**Implementation:**
- Keep `authorize_materialization()` in Data Steward Primitives
- Remove MVP defaults, require actual policy evaluation
- Runtime calls Data Steward Primitives for authorization
- Policy Store (if needed) is accessed by Primitives, not Runtime

**Documentation Update:**
- Clarify in `north_star.md` Section 4.1 that materialization policy is Smart City responsibility

---

### Q2: How Do We Track Lifecycle States for Purpose-Bound Outcomes?

**Question:** Should lifecycle states (draft → accepted → obsolete) be tracked in Artifact Plane registry, or separately?

**Current State:**
- Artifact Plane registry has basic metadata
- No lifecycle state tracking
- No owner/purpose metadata

**Recommended Answer:**
✅ **Artifact Plane Registry with explicit lifecycle states** - Add lifecycle tracking to registry schema.

**Rationale:**
- Lifecycle is intrinsic to Purpose-Bound Outcomes
- Registry already tracks metadata (tenant, session, execution_id)
- Single source of truth for artifact state
- Enables querying by lifecycle state
- Reinforces that lifecycle is not just metadata but explicit state

**Implementation:**
- Add `lifecycle_state` field to Artifact Plane registry (enum: draft, accepted, obsolete)
- Add `owner` field (enum: client, platform, shared)
- Add `purpose` field (enum: decision_support, delivery, governance, learning)
- Add `lifecycle_transitions` array for audit trail

**Documentation Update:**
- Document lifecycle states in `north_star.md` Section 2.2 (Artifact Plane)
- Add lifecycle state machine diagram

---

### Q3: How Do We Implement "Promote to Record of Fact" Workflow?

**Question:** When does parsed content become a Record of Fact? Should this be explicit or automatic?

**Current State:**
- Parsed content stored as Working Material (GCS, TTL-bound)
- Embeddings should be Records of Fact but extraction is placeholder
- No explicit promotion workflow

**Recommended Answer:**
✅ **Explicit Promotion Workflow** - Make transition explicit and policy-governed.

**Rationale:**
- Clear boundary between Working Material and Record of Fact
- Policy can govern when promotion is allowed
- Audit trail of promotion decisions
- Enables "persistence of meaning ≠ persistence of material"

**Implementation:**
- Add `promote_to_record_of_fact()` method to Data Steward SDK
- Requires boundary contract with materialization_type="deterministic" or "semantic_embedding"
- Creates Record of Fact entry in Supabase/ArangoDB
- Links to source Working Material (which may expire)
- Policy determines if promotion is allowed

**Documentation Update:**
- Document promotion workflow in `north_star.md` Section 7.2
- Add workflow diagram showing Working Material → Record of Fact transition

---

### Q4: How Do We Handle Lineage When Source File Expires?

**Question:** If a source file (Working Material) expires, how do Records of Fact maintain lineage?

**Current State:**
- Records of Fact may reference source files
- No explicit handling of expired source references
- Lineage tracking may break if source expires

**Recommended Answer:**
✅ **Reference Preservation Without Material Dependency** - Store reference even if source expires, reinforcing that meaning persists independently.

**Rationale:**
- Records of Fact must persist even if source expires
- Lineage should show "source expired" rather than broken reference
- Enables "persistence of meaning ≠ persistence of material"
- Reinforces architectural principle that conclusions don't require material persistence

**Implementation:**
- Records of Fact store `source_file_id` and `source_expired_at` (nullable)
- When Working Material expires, update Records of Fact with `source_expired_at`
- Lineage queries show "source expired" status
- Records of Fact remain valid even if source expired
- No material dependency - meaning is independent

**Documentation Update:**
- Document expiration handling in `north_star.md` Section 7.2
- Clarify that Records of Fact are independent of source material persistence

---

### Q5: What's the Promotion Workflow for Platform DNA?

**Question:** How do Purpose-Bound Outcomes become Platform DNA? What's the process?

**Current State:**
- Solution Registry exists but no promotion workflow
- Curator role exists but no promotion logic
- No de-identification/generalization logic

**Recommended Answer:**
✅ **Explicit Promotion via Curator** - Deliberate, policy-governed promotion.

**Rationale:**
- Promotion is a deliberate act, not automatic
- Requires validation (Curator role)
- Requires de-identification and generalization
- Must be policy-approved

**Implementation:**
1. **Promotion Request:** User/agent requests promotion of Purpose-Bound Outcome
2. **Curator Validation:** Curator validates promotion criteria:
   - Is it de-identified?
   - Is it generalizable?
   - Does it meet policy requirements?
3. **Generalization:** System generalizes outcome (removes client context)
4. **Registry Entry:** Creates entry in appropriate registry (Solution, Intent, Realm, etc.)
5. **Versioning:** Creates versioned, immutable registry entry

**Documentation Update:**
- Document promotion workflow in `north_star.md` Section 4.1 (Curator)
- Add promotion criteria and process
- Document registry structure

---

### Q6: Should TTL Enforcement Be Automated or Manual?

**Question:** How do we enforce TTL for Working Materials? Automated purge job or manual?

**Current State:**
- TTL tracked in boundary contracts (`materialization_expires_at`)
- No automated purge job
- No TTL enforcement

**Recommended Answer:**
✅ **Automated TTL Enforcement** - Scheduled job driven by policy + lifecycle state that purges expired Working Materials.

**Rationale:**
- TTL is policy-governed, should be automatically enforced
- Manual enforcement is error-prone
- Automated enforcement ensures compliance
- Policy + lifecycle state ensures correct enforcement (not just time-based)

**Implementation:**
- Create scheduled job (cron/scheduled task) that:
  1. Queries boundary contracts for expired materials (`materialization_expires_at < NOW()`)
  2. Validates lifecycle state (only purge if appropriate state)
  3. Purges expired materials from GCS
  4. Updates boundary contract status to "expired"
  5. Updates Records of Fact with `source_expired_at` if applicable
- Job runs periodically (e.g., hourly)
- Logs all purges for audit
- Policy determines TTL, lifecycle state determines purge eligibility

**Documentation Update:**
- Document TTL enforcement in `north_star.md` Section 7.1
- Add to Smart City responsibilities (Data Steward)

---

### Q7: How Do We Distinguish Between "Working Material" and "Purpose-Bound Outcome" in Content Realm?

**Question:** Content Realm has both files (Working Materials) and analysis results (Purpose-Bound Outcomes). How do we distinguish?

**Current State:**
- Files stored via FMS (Working Materials) ✅
- Analysis results not clearly classified
- Visualizations not clearly classified

**Recommended Answer:**
✅ **By Purpose, Not Format** - Classification is based on purpose, not file format.

**Rationale:**
- **Working Material** = inputs used to reach conclusions (temporary, time-bound)
- **Purpose-Bound Outcome** = conclusions created for a decision or delivery (intentional, lifecycle-managed)
- A "file" can become an outcome (e.g., generated SOP document)
- An "analysis" can still be working material if provisional
- This avoids edge-case confusion and ensures correct classification

**Implementation:**
- **FMS (Working Materials):**
  - Raw uploaded files (inputs)
  - Parsed file results (temporary, TTL-bound, used for processing)
  - Provisional analysis (not yet finalized)
- **Artifact Plane (Purpose-Bound Outcomes):**
  - Analysis results as deliverables (quality reports, interpretations created for decision/delivery)
  - Visualizations as deliverables (charts, diagrams created for decision/delivery)
  - Generated documents (SOPs, reports created for delivery)
  - Finalized conclusions

**Documentation Update:**
- Clarify in `north_star.md` Section 2.3 (Domain Services - Content)
- Document FMS vs Artifact Plane usage with purpose-based classification

---

### Q8: Should Artifact Plane Support Lifecycle State Transitions?

**Question:** How do artifacts move through lifecycle states? Who can transition them?

**Current State:**
- No lifecycle state tracking
- No transition logic

**Recommended Answer:**
✅ **Explicit State Machine with Policy Governance** - Lifecycle transitions are policy-governed.

**Rationale:**
- Lifecycle transitions are governance decisions
- Different roles may have different transition permissions
- Audit trail of transitions

**Implementation:**
- Define lifecycle state machine:
  - `draft` → `accepted` (owner or authorized user)
  - `draft` → `obsolete` (owner or authorized user)
  - `accepted` → `obsolete` (owner or authorized user)
- Policy determines who can transition
- Track transitions in `lifecycle_transitions` array
- Transitions recorded in WAL for audit

**Documentation Update:**
- Document lifecycle state machine in `north_star.md` Section 2.2
- Add transition rules and permissions

---

### Q9: How Do We Handle Cross-Realm Artifact Dependencies?

**Question:** If Outcomes Realm needs a blueprint from Journey Realm, how do we ensure it's available?

**Current State:**
- Outcomes Realm retrieves blueprints from Artifact Plane
- Journey Realm doesn't store blueprints in Artifact Plane yet
- Dependency not guaranteed

**Recommended Answer:**
✅ **Artifact Plane as Coordination and Reference Source of Truth** - All Purpose-Bound Outcomes in Artifact Plane (not execution owner).

**Rationale:**
- Single source of truth for artifact coordination and reference
- Cross-realm dependencies work automatically
- Consistent retrieval pattern
- **Critical:** Artifact Plane coordinates and references, but does NOT orchestrate logic or execution

**Implementation:**
- Complete Artifact Plane migration:
  - Journey Realm: Blueprints, SOPs, workflows
  - Insights Realm: Interpretations, reports, visualizations
- All realms retrieve from Artifact Plane
- No execution state artifacts (only references)
- Artifact Plane provides coordination and reference, not execution orchestration

**Documentation Update:**
- Document cross-realm artifact dependencies in `north_star.md` Section 2.2
- Clarify that Artifact Plane enables cross-realm composition via coordination/reference, not execution

---

### Q10: How Do We Handle Vector Search in Records of Fact?

**Question:** Should vector similarity search be part of SemanticDataAbstraction or a separate service?

**Current State:**
- `SemanticDataAbstraction.vector_search()` is placeholder
- Embeddings stored in ArangoDB `structured_embeddings` collection
- No actual vector search implementation

**Recommended Answer:**
✅ **SemanticDataAbstraction Backed by ArangoDB with Pluggable Vector Backends** - Keep in abstraction, implement via pluggable adapters.

**Rationale:**
- Vector search is infrastructure concern (abstraction layer)
- ArangoDB supports vector search (when configured)
- Keeps business logic separate from infrastructure
- **Critical:** Pluggable backends preserve architectural flexibility and avoid vendor lock-in assumptions

**Implementation:**
- Implement ArangoDB vector search in `ArangoAdapter`
- Use ArangoDB vector similarity functions
- Design adapter interface to support other vector backends (e.g., Pinecone, Weaviate)
- `SemanticDataAbstraction.vector_search()` delegates to adapter
- Business logic (Librarian, Insights Realm) uses abstraction
- Adapter pattern enables swapping vector backends without changing business logic

**Documentation Update:**
- Document vector search in `north_star.md` Section 7.2
- Clarify that vector search is infrastructure with pluggable backends, not business logic

---

## Part 4: Documentation Updates Required

### 4.1 North Star Architecture Guide Updates

**File:** `docs/architecture/north_star.md`

**Updates Needed:**

#### Section 2.2: Civic Systems - Add Artifact Plane

**Add:**
```markdown
### Artifact Plane (Purpose-Bound Outcomes Management)

> **Artifact Plane manages intentional deliverables as first-class citizens.**

The Artifact Plane provides lifecycle management for Purpose-Bound Outcomes:
- Roadmaps, POCs, solutions (Outcomes Realm)
- Blueprints, SOPs, workflows (Journey Realm)
- Reports, visualizations (Insights Realm)

**Key Properties:**
- Owner (client/platform/shared)
- Purpose (decision support, delivery, governance, learning)
- Lifecycle states (draft → accepted → obsolete)
- Optional persistence of source materials

**Infrastructure:**
- Supabase metadata registry
- GCS/document store for payloads
- ArangoDB for lineage

**Not for:**
- Source files (FMS handles these)
- Raw data (Data Steward handles these)
- Execution state (Runtime handles this)
```

#### Section 4.1: Smart City - Expand Data Steward

**Add:**
```markdown
#### Data Steward (Data Boundaries & Materialization)

**Responsibilities:**
- Boundary contract negotiation (`request_data_access()`)
- Materialization authorization (`authorize_materialization()`)
- Materialization policy evaluation
- TTL enforcement
- "Data stays at door" enforcement

**Materialization Types:**
- `reference` - Reference only, no materialization
- `partial_extraction` - Extract specific fields
- `deterministic` - Deterministic representation (becomes Record of Fact)
- `semantic_embedding` - Semantic embedding (becomes Record of Fact)
- `full_artifact` - Full artifact (Working Material, TTL-bound)

**Two-Phase Flow:**
1. `request_data_access()` - Negotiate boundary contract
2. `authorize_materialization()` - Determine materialization form and TTL
```

#### Section 7: Data Brain - Replace with Four-Class Framework

**Replace Section 7 with:**

```markdown
## 7. The Data Framework (Four Classes by Time + Purpose)

> **Data is classified by time (how long it exists) and purpose (why it exists).**

The platform manages four distinct classes of data, each with different lifecycle and governance:

### 7.1 Working Materials (Temporary)

**Definition:** Temporarily materialized data for understanding, parsing, and assessment.

**Properties:**
- Time-bound (TTL enforced by policy)
- Policy-bound (boundary contract required)
- Explicitly non-archival
- Exists only to enable transformation

**Infrastructure:**
- GCS (temporary storage)
- Supabase (tracking, status, audit)
- TTL enforced by automated purge job

**Platform Components:**
- Content Realm FMS (file ingestion, parsing)
- Boundary contracts (govern access and TTL)

**Examples:**
- Raw uploaded files
- Parsed file results (temporary)
- Intermediate schemas

**Transition:** Working Materials → Records of Fact (via explicit promotion)

---

### 7.2 Records of Fact (Persistent Meaning)

**Definition:** Persistent, auditable, and reproducible conclusions or interpreted meaning.

**Properties:**
- Must persist (auditable, reproducible)
- Do NOT require original file to persist
- May reference expired source artifacts
- Represent "what the system concluded"

**Key Principle:**
> **Persistence of meaning ≠ persistence of material**

**Infrastructure:**
- Supabase (structured data)
- ArangoDB (graph/lineage, embeddings)
- No raw files required

**Platform Components:**
- Data Steward (manages embeddings)
- SemanticDataAbstraction (stores embeddings)
- Insights Realm (creates interpretations)

**Examples:**
- Deterministic embeddings
- Semantic embeddings
- Interpreted meaning (entities, relationships)
- Data quality conclusions

**Promotion Workflow:**
- Explicit `promote_to_record_of_fact()` via Data Steward SDK
- Requires boundary contract with appropriate materialization type
- Creates persistent Record of Fact entry
- Links to source (which may expire)

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
- Artifact Plane (Supabase metadata + GCS/document store)
- Lifecycle tracking in registry

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
- Quality reports (as deliverables)
- Business analysis reports

**Lifecycle:**
- `draft` → `accepted` → `obsolete`
- Transitions are policy-governed
- Tracked in Artifact Plane registry

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
- Supabase registries (versioned, immutable)
- Promotion via Curator role

**Platform Components:**
- Curator (validates promotion)
- Solution Registry
- Intent Registry
- Realm Registry

**Examples:**
- New intents (promoted from outcomes)
- New realms (promoted from outcomes)
- New solutions (promoted from outcomes)
- New capabilities (promoted from outcomes)

**Promotion Workflow:**
1. Promotion request (user/agent)
2. Curator validation (de-identification, generalizability, policy)
3. Generalization (remove client context)
4. Registry entry (versioned, immutable)

---

### 7.5 Data Flow (End-to-End)

```
Client Working Material (FMS)
    ↓ (boundary contract + materialization policy)
Materialized Working Material (GCS, TTL-bound)
    ↓ (explicit promotion via Data Steward)
Records of Fact (Supabase + ArangoDB, persistent)
    ↓ (realm processing)
Purpose-Bound Outcomes (Artifact Plane)
    ↓ (optional, deliberate promotion via Curator)
Platform DNA (Supabase registries)
```

**Key Principle:**
> **Each arrow is policy-mediated. Nothing moves automatically.**
```

---

### 4.2 Platform Overview Updates

**File:** `docs/PLATFORM_OVERVIEW.md`

**Updates Needed:**

#### Add Section: Data Framework

**Add after "How Does It Work?" section:**

```markdown
## Data Framework: Four Classes by Time + Purpose

Symphainy classifies data into four distinct classes based on **time** (how long it exists) and **purpose** (why it exists):

### Working Materials (Temporary)
- Raw files, parsed results, intermediate schemas
- Time-bound, policy-governed, non-archival
- Stored via FMS (GCS + Supabase tracking)

### Records of Fact (Persistent Meaning)
- Embeddings, interpretations, conclusions
- Persistent, auditable, reproducible
- Stored in Supabase + ArangoDB
- **Key Principle:** Persistence of meaning ≠ persistence of material

### Purpose-Bound Outcomes (Intentional Deliverables)
- Roadmaps, POCs, blueprints, SOPs, reports
- Created for someone, exist for a reason
- Stored in Artifact Plane
- Lifecycle: draft → accepted → obsolete

### Platform DNA (Generalized Capability)
- Promoted solutions, intents, realms, capabilities
- De-identified, generalizable, curated
- Stored in Supabase registries
- Promotion via Curator role
```

---

### 4.3 Platform Rules Updates

**File:** `docs/PLATFORM_RULES.md`

**Updates Needed:**

#### Add Section: Data Classification Rules

**Add after "Public Works Pattern" section:**

```markdown
## 📊 Data Classification Rules

### Four-Class Framework

All data must be classified into one of four classes:

1. **Working Materials** - Temporary, time-bound (FMS)
2. **Records of Fact** - Persistent meaning (Supabase + ArangoDB)
3. **Purpose-Bound Outcomes** - Intentional deliverables (Artifact Plane)
4. **Platform DNA** - Generalized capabilities (Supabase registries)

**Rules:**
- ✅ Source files → Working Materials (FMS)
- ✅ Derived artifacts → Purpose-Bound Outcomes (Artifact Plane)
- ✅ Embeddings/interpretations → Records of Fact
- ✅ Promoted capabilities → Platform DNA
- ❌ No mixing classes in same storage
- ❌ No artifacts in execution state (only references)
- ❌ No Working Materials without TTL
```

---

## Part 5: Remaining Open Questions

### Q11: Should Materialization Policy Be Configurable Per Tenant?

**Question:** Can different tenants have different materialization policies?

**Recommended Answer:**
✅ **Yes, Policy Should Be Tenant-Scoped with Platform-Level Defaults** - Different tenants may have different requirements.

**Rationale:**
- Multi-tenant platform requires tenant-specific policies
- Some tenants may require stricter policies (e.g., healthcare, finance)
- Policy evaluation should consider tenant context
- Platform-level defaults ensure consistent behavior when tenant-specific policy doesn't exist

**Implementation:**
- Materialization policy evaluation includes `tenant_id`
- Policy Store (if implemented) should support tenant-specific policies
- Platform-level default policy applies if no tenant-specific policy exists
- Tenant-specific policies override platform defaults

**Documentation:**
- Document tenant-scoped policies in `north_star.md` Section 4.1
- Document platform-level defaults

---

### Q12: How Do We Handle Artifact Versioning?

**Question:** Should Purpose-Bound Outcomes support versioning? How?

**Recommended Answer:**
✅ **Yes, Versioning for Accepted Artifacts (Immutable Past Versions)** - Once accepted, create immutable version.

**Rationale:**
- Accepted artifacts may need to be revised
- Versioning enables audit trail
- Immutable versions enable reproducibility
- **Critical:** Past versions are immutable - only current version can be modified

**Implementation:**
- When artifact transitions to `accepted`, create immutable version
- Store versions in Artifact Plane registry
- Link versions via `parent_artifact_id`
- Current version tracked in registry
- Past versions are immutable (read-only)
- Only current version can transition states or be modified

**Documentation:**
- Document versioning in `north_star.md` Section 2.2
- Clarify immutability expectations for past versions

---

### Q13: Should Artifact Plane Support Search/Query?

**Question:** How do users find artifacts? Should Artifact Plane have search capability?

**Recommended Answer:**
✅ **Yes, Search via Registry Queries** - Artifact Plane should support querying by metadata.

**Rationale:**
- Users need to find artifacts
- Cross-realm composition requires artifact discovery
- Search enables reuse

**Implementation:**
- Add `list_artifacts()` with filters (type, tenant, session, lifecycle_state, owner, purpose)
- Use Supabase queries for metadata search
- Use ArangoDB for graph-based discovery (if needed)

**Documentation:**
- Document search capability in `north_star.md` Section 2.2

---

### Q14: How Do We Handle Artifact Dependencies?

**Question:** If a solution depends on a roadmap and POC, how do we track dependencies?

**Recommended Answer:**
✅ **Lineage Tracking in Artifact Plane** - Track artifact → artifact dependencies.

**Rationale:**
- Dependencies enable impact analysis
- Lineage enables audit trail
- Dependencies enable validation (can't delete if referenced)

**Implementation:**
- Add `source_artifact_ids` array to artifact registry
- Track dependencies in ArangoDB graph (if needed)
- Validate dependencies before deletion
- Show dependency graph in lineage visualization

**Documentation:**
- Document dependency tracking in `north_star.md` Section 2.2

---

### Q15: Should Records of Fact Support Expiration?

**Question:** Can Records of Fact expire, or are they always permanent?

**Recommended Answer:**
✅ **Records of Fact Are Permanent** - They represent "what the system concluded" and must persist.

**Rationale:**
- Records of Fact are audit trail
- "Persistence of meaning ≠ persistence of material" means meaning persists even if source expires
- Expiration would break auditability

**Implementation:**
- Records of Fact have no TTL
- They persist even if source Working Material expires
- Source expiration tracked but doesn't affect Record of Fact

**Documentation:**
- Clarify in `north_star.md` Section 7.2 that Records of Fact are permanent

---

### Q16: Can Artifacts Change Classification After Creation?

**Question:** Can an artifact move from one data class to another after it's been created?

**Recommended Answer:**
✅ **Yes, but Only Via Explicit, Policy-Governed Lifecycle Transitions** - Classification changes are deliberate, not automatic.

**Rationale:**
- Prevents silent mutation
- Reinforces deliberate promotion
- Protects governance story
- Ensures audit trail of classification changes

**Allowed Transitions:**
- Working Material → Record of Fact (via explicit `promote_to_record_of_fact()` workflow)
- Purpose-Bound Outcome → Platform DNA (via explicit Curator promotion)
- **Not Allowed:** Automatic transitions, silent mutations, or transitions without policy approval

**Implementation:**
- All classification changes must go through explicit workflows
- Policy governs whether transition is allowed
- All transitions recorded in WAL for audit
- Transitions are idempotent (can be retried safely)

**Documentation:**
- Document allowed transitions in `north_star.md` Section 7.5
- Clarify that transitions are explicit and policy-governed

---

## Part 6: Implementation Checklist

### Phase 1: Documentation Updates (Week 1)

- [ ] Update `north_star.md` Section 2.2 (Add Artifact Plane)
- [ ] Update `north_star.md` Section 4.1 (Expand Data Steward, Materialization Policy)
- [ ] Replace `north_star.md` Section 7 (Four-Class Data Framework)
- [ ] Update `PLATFORM_OVERVIEW.md` (Add Data Framework section)
- [ ] Update `PLATFORM_RULES.md` (Add Data Classification Rules)
- [ ] Create architecture decision records (ADRs) for open questions

**Estimated Time:** 8-12 hours

---

### Phase 2: Architecture Alignment (Week 2)

- [ ] Implement lifecycle state tracking in Artifact Plane
- [ ] Implement promotion workflow (Working Material → Record of Fact)
- [ ] Implement TTL enforcement job
- [ ] Remove MVP defaults from materialization policy
- [ ] Document promotion workflow (Purpose-Bound Outcome → Platform DNA)

**Estimated Time:** 16-20 hours

---

### Phase 3: Complete Artifact Plane Migration (Week 3)

- [ ] Migrate Journey Realm artifacts to Artifact Plane
- [ ] Migrate Insights Realm artifacts to Artifact Plane
- [ ] Remove artifact storage from execution state
- [ ] Update all tests to use Artifact Plane

**Estimated Time:** 12-16 hours

---

## Part 7: Success Criteria

### Documentation Complete When:
- ✅ All architectural evolutions documented
- ✅ Four-class data framework fully integrated
- ✅ All open questions answered
- ✅ Architecture guide matches implementation
- ✅ Platform overview reflects current state

### Architecture Bulletproof When:
- ✅ No MVP fallbacks in production code
- ✅ All data properly classified into four classes
- ✅ All transitions are policy-governed
- ✅ All lifecycle states tracked
- ✅ All promotion workflows implemented

---

## Conclusion

**Status:** 📋 **READY FOR ARCHITECTURE UPDATE**

**Key Actions:**
1. Update `north_star.md` with four-class framework and Artifact Plane
2. Document materialization policy and boundary contracts
3. Answer all open architectural questions
4. Align documentation with current implementation

**Timeline:** 3-4 weeks to complete architecture alignment

---

**Last Updated:** January 20, 2026  
**Next Review:** After Phase 1 completion
