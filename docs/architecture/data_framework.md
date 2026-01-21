# Data Framework: Four Classes by Time + Purpose

**Date:** January 20, 2026  
**Status:** Canonical  
**Purpose:** Detailed guide to the four-class data framework

---

## Overview

Symphainy classifies all data into four distinct classes based on **time** (how long it exists) and **purpose** (why it exists). This framework ensures proper lifecycle management, governance, and infrastructure allocation.

**Key Principle:**
> **Persistence of meaning ≠ persistence of material**

The platform is allowed to remember conclusions without remembering materials, and allowed to create outcomes without absorbing them into its DNA.

---

## The Four Classes

```
Working Materials (Temporary)
    ↓ (policy + time)
Records of Fact (Persistent Meaning)
    ↓ (purpose + lifecycle)
Purpose-Bound Outcomes (Intentional Deliverables)
    ↓ (optional, deliberate promotion)
Platform DNA (Generalized Capability)
```

**Each arrow is policy-mediated. Nothing moves automatically.**

---

## Class 1: Working Materials

### Definition

Temporarily materialized data for understanding, parsing, and assessment.

### Properties

- **Time-bound:** TTL enforced by policy
- **Policy-bound:** Boundary contract required
- **Explicitly non-archival:** Exists only to enable transformation
- **Purpose:** Inputs used to reach conclusions

### Infrastructure

**Storage:**
- GCS (temporary storage)
- Supabase (tracking, status, audit)

**TTL Enforcement:**
- Automated purge job (driven by policy + lifecycle state)
- Runs periodically (e.g., hourly)
- Logs all purges for audit

**Platform Components:**
- Content Realm FMS (file ingestion, parsing)
- Boundary contracts (govern access and TTL)
- Materialization policy (determines TTL)

### Examples

- Raw uploaded files
- Parsed file results (temporary)
- Intermediate schemas
- Reviewable previews
- Provisional analysis (not yet finalized)

### Classification Rule

> **By purpose, not format:**
> - Working Material = inputs used to reach conclusions
> - A "file" can become an outcome (e.g., generated SOP)
> - An "analysis" can still be working material if provisional

### Transition

**Working Materials → Records of Fact**

- Explicit `promote_to_record_of_fact()` workflow via Data Steward SDK
- Requires boundary contract with appropriate materialization type
- Creates persistent Record of Fact entry
- Links to source Working Material (which may expire later)

---

## Class 2: Records of Fact

### Definition

Persistent, auditable, and reproducible conclusions or interpreted meaning.

### Properties

- **Must persist:** Auditable, reproducible
- **Do NOT require original file to persist:** Meaning persists independently
- **May reference expired source artifacts:** Source expiration tracked but doesn't affect Record of Fact
- **Represent:** "What the system concluded, at that moment, under those policies"
- **Permanent:** No expiration (unlike Working Materials)

### Key Principle

> **Persistence of meaning ≠ persistence of material**

Records of Fact persist even if source Working Material expires. The meaning is independent of the material.

### Infrastructure

**Storage:**
- Supabase (structured data)
- ArangoDB (graph/lineage, embeddings)

**No raw files required:** Meaning persists independently

**Platform Components:**
- Data Steward (manages embeddings, interpretations)
- SemanticDataAbstraction (stores embeddings in ArangoDB, with pluggable vector backends)
- Insights Realm (creates interpretations)

### Examples

- Deterministic embeddings
- Semantic embeddings
- Interpreted meaning (entities, relationships)
- Data quality conclusions
- Semantic interpretations

### Promotion Workflow

1. Working Material exists (with boundary contract)
2. Explicit `promote_to_record_of_fact()` via Data Steward SDK
3. Requires boundary contract with `materialization_type="deterministic"` or `"semantic_embedding"`
4. Creates persistent Record of Fact entry
5. Links to source Working Material (which may expire later)
6. Record of Fact persists even if source expires

### Lineage

**Reference Preservation Without Material Dependency:**

- Records of Fact store `source_file_id` and `source_expired_at` (nullable)
- When Working Material expires, update Records of Fact with `source_expired_at`
- Records of Fact remain valid even if source expired
- Lineage queries show "source expired" status
- Meaning is independent of source material persistence

### Vector Search

- SemanticDataAbstraction backed by ArangoDB (with pluggable vector backends)
- Preserves architectural flexibility and avoids vendor lock-in
- Business logic uses abstraction, not direct vector backend

---

## Class 3: Purpose-Bound Outcomes

### Definition

Intentional artifacts created for a specific purpose and audience.

### Properties

- **Owner:** client/platform/shared
- **Purpose:** decision support, delivery, governance, learning
- **Lifecycle states:** draft → accepted → obsolete
- **May be reused, revised, or discarded**
- **May feed platform but are not the platform**

### Infrastructure

**Storage:**
- Artifact Plane (Supabase metadata + GCS/document store for payloads)

**Lifecycle:**
- Tracked in Artifact Plane registry with explicit lifecycle states

**Platform Components:**
- Artifact Plane (manages Purpose-Bound Outcomes)
- Outcomes Realm (roadmaps, POCs, solutions)
- Journey Realm (blueprints, SOPs, workflows)
- Insights Realm (reports, visualizations as deliverables)

### Examples

- Roadmaps
- POCs
- Blueprints
- SOPs
- Quality assessment reports (as deliverables)
- Business analysis reports
- Generated documents (SOPs, reports created for delivery)

### Classification Rule

> **By purpose, not format:**
> - Purpose-Bound Outcome = conclusions created for a decision or delivery
> - A "file" can become an outcome (e.g., generated SOP document)
> - An "analysis" can still be working material if provisional

### Lifecycle State Machine

**States:**
- `draft` - Initial state, can be modified
- `accepted` - Finalized, creates immutable version
- `obsolete` - No longer active

**Transitions:**
- `draft` → `accepted` (owner or authorized user)
- `draft` → `obsolete` (owner or authorized user)
- `accepted` → `obsolete` (owner or authorized user)

**Rules:**
- Transitions are policy-governed
- Tracked in Artifact Plane registry
- Transitions recorded in WAL for audit
- **MVP Approach:** Permissive transition policies (any user can transition)
- **Production:** Can add transition restrictions via policy

### Versioning

**For Accepted Artifacts (Immutable Past Versions):**

- When artifact transitions to `accepted`, create immutable version
- Store versions in Artifact Plane registry
- Link versions via `parent_artifact_id`
- Current version tracked in registry
- **Past versions are immutable** (read-only)
- Only current version can transition states or be modified

### Cross-Realm Dependencies

**Artifact Plane as Coordination and Reference Source of Truth:**

- All Purpose-Bound Outcomes stored in Artifact Plane
- Cross-realm dependencies work automatically
- Artifact Plane coordinates and references, but does NOT orchestrate logic
- Artifact Plane is not execution owner

### Search & Query

- Artifact Plane supports search via registry queries
- Filter by: type, tenant, session, lifecycle_state, owner, purpose
- Enables artifact discovery and reuse

### Dependencies

- Track artifact → artifact dependencies in Artifact Plane
- Dependencies enable impact analysis
- Lineage enables audit trail
- Validate dependencies before deletion

---

## Class 4: Platform DNA

### Definition

Generalized, curated, de-identified capabilities promoted from outcomes.

### Properties

- **De-identified:** No client context
- **Generalizable:** Reusable across clients
- **Policy-approved:** Curator validates
- **Abstracted from client context**
- **Versioned, curated, immutable**

### Infrastructure

**Storage:**
- Supabase registries (versioned, immutable)

**Promotion:**
- Via Curator role (deliberate act)

**Platform Components:**
- Curator (validates promotion)
- Solution Registry
- Intent Registry
- Realm Registry

### Examples

- New intents (promoted from outcomes)
- New realms (promoted from outcomes)
- New journeys (promoted from outcomes)
- New solutions (promoted from outcomes)
- New capabilities (promoted from outcomes)

### Promotion Workflow

1. **Promotion Request:** User/agent requests promotion of Purpose-Bound Outcome
2. **Curator Validation:** Curator validates promotion criteria:
   - Is it de-identified?
   - Is it generalizable?
   - Does it meet policy requirements?
3. **Generalization:** System generalizes outcome (removes client context)
4. **Registry Entry:** Creates entry in appropriate registry (Solution, Intent, Realm, etc.)
5. **Versioning:** Creates versioned, immutable registry entry

### Promotion Criteria

- De-identified
- Generalizable
- Policy-approved
- Abstracted from client context

---

## Data Flow (End-to-End)

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

---

## Classification Transitions

### Allowed Transitions

1. **Working Material → Record of Fact**
   - Explicit `promote_to_record_of_fact()` workflow
   - Requires boundary contract with appropriate materialization type
   - Policy-governed

2. **Purpose-Bound Outcome → Platform DNA**
   - Explicit promotion via Curator
   - Requires validation (de-identified, generalizable, policy-approved)
   - Policy-governed

### Not Allowed

- ❌ Automatic transitions
- ❌ Silent mutations
- ❌ Transitions without policy approval

### Transition Rules

- All transitions are explicit and policy-governed
- All transitions recorded in WAL for audit
- Transitions are idempotent (can be retried safely)

---

## Infrastructure Mapping

| Class | Storage | Lifecycle | Governance |
|-------|---------|-----------|------------|
| **Working Materials** | GCS + Supabase | TTL-bound, automated purge | Boundary contracts, materialization policy |
| **Records of Fact** | Supabase + ArangoDB | Permanent (no expiration) | Data Steward, promotion workflow |
| **Purpose-Bound Outcomes** | Artifact Plane | Lifecycle states (draft → accepted → obsolete) | Artifact Plane, lifecycle policies |
| **Platform DNA** | Supabase registries | Immutable once promoted | Curator, promotion workflow |

---

## Policy Governance

### Materialization Policy

- **Location:** Smart City Primitives (Data Steward)
- **Scope:** Tenant-scoped with platform defaults
- **Types:** reference, partial_extraction, deterministic, semantic_embedding, full_artifact
- **MVP Approach:** Permissive policies (allow all types)
- **Production:** Can tighten policies without code changes

### Lifecycle Transitions

- **Location:** Artifact Plane
- **Scope:** Policy-governed transitions
- **MVP Approach:** Permissive transition policies (any user can transition)
- **Production:** Can add transition restrictions via policy

### Promotion Workflows

- **Working Material → Record of Fact:** Data Steward SDK
- **Purpose-Bound Outcome → Platform DNA:** Curator
- **Both:** Explicit, policy-governed, recorded in WAL

---

## Examples by Use Case

### File Upload Scenario

1. **Client uploads PDF** → Working Material (FMS, TTL-bound)
2. **PDF parsed** → Working Material (parsed results, temporary)
3. **Embeddings extracted** → Record of Fact (persistent, meaning)
4. **Quality report generated** → Purpose-Bound Outcome (Artifact Plane, lifecycle-managed)
5. **Report accepted** → Purpose-Bound Outcome (accepted state, immutable version)
6. **Report promoted** → Platform DNA (if generalized and de-identified)

### Analysis Scenario

1. **Data ingested** → Working Material (FMS, TTL-bound)
2. **Analysis performed** → Working Material (provisional results)
3. **Interpretations created** → Record of Fact (persistent meaning)
4. **Report generated** → Purpose-Bound Outcome (Artifact Plane, draft)
5. **Report accepted** → Purpose-Bound Outcome (accepted, immutable version)

---

## Key Takeaways

1. **Classification by Purpose, Not Format**
   - Working Material = inputs
   - Purpose-Bound Outcome = conclusions

2. **Persistence of Meaning ≠ Persistence of Material**
   - Records of Fact persist even if source expires
   - Meaning is independent of material

3. **Policy-Mediated Transitions**
   - Nothing moves automatically
   - All transitions are explicit and policy-governed

4. **Capability by Design, Implementation by Policy**
   - Build real infrastructure
   - Use permissive policies for MVP
   - Tighten policies for production without code changes

---

## References

- [Architecture Guide](north_star.md) - Section 7: The Data Framework
- [Platform Overview](../PLATFORM_OVERVIEW.md) - Data Framework section
- [Platform Rules](../PLATFORM_RULES.md) - Data Classification Rules
- [MVP Approach](../MVP_APPROACH_CAPABILITY_BY_DESIGN.md) - Capability by Design, Implementation by Policy

---

**Last Updated:** January 20, 2026
