# Symphainy Architectural Guide - North Star

**Status:** Canonical (Locked — January 2026)  
**Applies to:** All platform code, demos, and production deployments  
**Version:** 2.0 (Breaking Changes - No Backwards Compatibility)

This guide defines the **authoritative architectural model** for the platform. It exists to ensure:

* Shared mental models across the team
* Clear ownership of logic and responsibility
* Functional substance does not evaporate into contracts
* Safe extensibility as Runtime and Civic Systems evolve
* Support for 350k-policy production workloads

**If there is ambiguity between code and this guide, this guide wins.**

---

## 0. The North Star (Lock This In)

> **Symphainy is a governed execution platform.**
> It runs **Solutions** safely — and those Solutions safely operate, connect to, and reason over external systems.
>
> It does this by binding **intent**, **policy**, **data cognition**, and **execution** under a **single runtime authority**.

Everything in this guide exists to make execution **explicit, governed, replayable, and explainable**.

---

## 1. First Principles (Non‑Negotiable)

### 1.1 We are not building an application

Symphainy is **not**:
* a web app
* a workflow engine
* a data lake
* an agent playground

Symphainy **is**:
* a **governed execution environment**
* that runs **domain services (SOA)**
* through **Solutions**
* under **explicit runtime control**

Most platforms fail because:
* execution is implicit
* state is scattered
* data meaning is inferred but not tracked
* agents act autonomously
* governance is bolted on later

Symphainy is designed so that:
* nothing executes without **intent**
* nothing executes without **policy**
* nothing executes without **attribution**
* nothing executes **outside the Runtime**

---

## 2. The Structural Model (What Exists in the Platform)

Symphainy is composed of **four distinct classes of things**.
Each exists for a different reason and must not collapse into the others.

### 2.1 Runtime (The Execution Authority)

> **Runtime is the only component allowed to own execution and state.**

Runtime is not a realm.
It is not a solution.
It is not a domain service.

Runtime owns:
* intent acceptance
* execution lifecycle
* session & tenant context
* write‑ahead log (WAL)
* saga orchestration
* retries & failure recovery
* deterministic replay
* state transitions
* **runtime‑native data cognition (Data Brain)**

If something runs and Runtime does not know about it, **it is a bug**.

### 2.2 Civic Systems (How Participation Is Governed)

> **Civic Systems define how things are allowed to participate in execution.**

They do **not** own business logic.
They do **not** own execution.
They define **capability by design, constrained by policy**.

Civic Systems expose **SDKs, planes, and surfaces** used by Runtime and domain services.

There are five Civic Systems:

1. **Smart City** — governance
2. **Experience** — exposure
3. **Agentic** — reasoning
4. **Platform SDK** — how solutions and domains are built correctly
5. **Artifact Plane** — Purpose-Bound Outcomes management

Civic Systems may depend on each other, but **Runtime remains the single execution authority**.

### 2.3 Domain Services (Formerly "Realms")

> **Domain Services define meaning, not mechanics.**

These are **SOA services** that contain the vast majority of your existing functional logic.

Canonical domains:

| Domain     | Owns                                          |
| ---------- | --------------------------------------------- |
| Content    | Ingest, parse, embeddings, canonical facts    |
| Insights   | Interpretation, analysis, mapping, querying   |
| Operations | SOPs, workflows, optimization recommendations |
| Outcomes   | Synthesis, roadmaps, POCs, proposals          |

Domain services:
* implement rich internal logic
* can be complex and opinionated
* **do not own execution or state**
* **do not orchestrate workflows**
* **do not persist authoritative data**

They participate in execution **only via Runtime contracts**.

### 2.4 Foundations (Pure Enablement)

Foundations are **pure libraries and adapters**.

They provide:
* schemas & contracts
* parsing libraries
* embeddings & models
* infrastructure adapters

They contain:
* no execution
* no orchestration
* no awareness of user intent

---

## 3. The Critical Unlock: SOA ↔ Runtime Boundary

> **We do NOT contract for functionality.**
> **We contract for execution semantics.**

The platform does **not** require millions of fine‑grained contracts.

Instead, every domain service agrees to a **single execution contract**:

### Runtime Participation Contract

Each participating service must:
* declare which **intents** it supports
* accept a **runtime execution context**
* return **artifacts and events**, not side effects
* never bypass Runtime for state, retries, or orchestration

Example (conceptual):
```python
handle_intent(intent, runtime_context) → { artifacts, events }
```

Runtime does not care **how** a domain service works internally.
It cares **how it behaves while executing**.

This boundary allows:
* massive functional reuse
* zero contract explosion
* safe scaling to new solutions (e.g. 350k policy migration)

---

## 4. Civic Systems in Detail

### 4.1 Smart City (Execution Governance)

> **Smart City governs *how* execution is allowed to occur.**

Smart City is purpose‑agnostic.
It never decides *what* should happen or *why*.

It exposes policy‑aware primitives consumed by Runtime.

#### Canonical Smart City Roles

| Role           | Responsibility                         |
| -------------- | -------------------------------------- |
| City Manager   | Global policy, tenancy, escalation     |
| Security Guard | Identity, authN/Z, zero trust          |
| Curator        | Capability promotion, registries        |
| Data Steward   | Data boundaries, contracts, materialization |
| Librarian      | Semantic schemas & meaning             |
| Traffic Cop    | Sessions, execution IDs, correlation   |
| Post Office    | Event routing & ordering               |
| Conductor      | Workflow & saga primitives             |
| Nurse          | Telemetry, retries, self‑healing       |

**Smart City Architecture:**
* **SDK-First:** Smart City SDK provides coordination logic (used by Experience, Solution, Realms)
* **Primitives:** Smart City Primitives provide policy decisions (used by Runtime only)
* **Separation:** SDK coordinates, Primitives validate

#### Data Steward (Data Boundaries & Materialization)

**Responsibilities:**
- Boundary contract negotiation (`request_data_access()`)
- Materialization authorization (`authorize_materialization()`)
- Materialization policy evaluation (tenant-scoped with platform-level defaults)
- TTL enforcement for Working Materials (automated purge job driven by policy + lifecycle state)
- "Data stays at door" enforcement

**Two-Phase Materialization Flow:**

1. **Request Data Access** (`request_data_access()`)
   - Negotiate boundary contract
   - Determine if access is granted
   - Create contract in `data_boundary_contracts` table
   - Returns: `DataAccessRequest` with `contract_id`

2. **Authorize Materialization** (`authorize_materialization()`)
   - Evaluate materialization policy (tenant-scoped, with platform defaults)
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
- Materialization policy is tenant-scoped (with platform-level defaults)
- Policy determines: type, scope, TTL, backing store
- Policy evaluation happens in Data Steward Primitives (not Runtime)
- Runtime consumes policy decisions, doesn't make them

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

### 4.2 Experience (Exposure & Interaction)

> **Experience translates external interaction into intent.**

Experience:
* exposes REST, WebSockets, chat, adapters
* authenticates callers
* establishes sessions via Runtime
* translates user actions into **intents**
* streams execution updates back

**Experience → Runtime Flow:**
1. Experience establishes session via Runtime (`POST /api/session/create`)
2. Experience submits intents via Runtime (`POST /api/intent/submit`)
3. Experience subscribes to execution events (WebSocket `/api/execution/stream`)
4. Experience never calls domain services directly
5. Experience never manages workflows
6. Experience never owns state

Experience never:
* calls domain services directly
* manages workflows
* owns state

### 4.3 Agentic (Reasoning Under Constraint)

> **Agents reason. They do not execute.**

The Agentic Civic System provides:
* agent SDK
* agent registry & factory
* grounding, telemetry, policy hooks

Agents:
* consume artifacts
* produce interpretations or recommendations
* operate **only inside Runtime execution**

Agents never:
* write to databases
* call infrastructure directly
* orchestrate workflows

**Pattern Adoption:** Inspired by CrewAI/LangGraph patterns, but custom implementation (swappable, not dependent).

### 4.4 Platform SDK (Civic Front Door)

> **The Platform SDK defines how solutions and domain services are built correctly.**

This SDK:
* is the *front door* for building on Symphainy
* configures client‑specific policies, capabilities, and integrations
* composes Civic Systems into usable building blocks

It includes:
* **Solution Builder:** Creates Solutions (binds domain services to external systems)
* **Realm SDK:** Creates domain services (enforces Runtime Participation Contract)
* **Civic System Composition:** Composes Smart City, Experience, Agentic into building blocks

It is how:
* your team builds the MVP showcase
* external developers build their own solutions
* agentic coders generate compliant services

**Clarification:** Platform SDK = Solution SDK + Realm SDK + Composition helpers.

---

## 5. Solutions (The Vehicle for Running Systems)

> **The platform runs Solutions; Solutions run systems.**

A Solution:
* defines **solution context** (goals, constraints, risk)
* declares supported intents
* binds domain services to external systems

The platform never interacts with external systems directly — it does so **through Solutions**.

### 5.1 Solution Binding Model

A Solution declares:
* `domain_service_bindings`: Map of realm → external system configurations
* `sync_strategies`: How to keep external systems in sync
* `conflict_resolution`: How to handle concurrent updates

**Example (350k policies):**
```python
solution = Solution(
    solution_id="insurance_migration",
    solution_context={
        "goals": ["Migrate 350k policies", "Maintain auditability"],
        "constraints": ["No downtime", "Bi-directional sync"],
        "risk": "High - production data"
    },
    domain_service_bindings={
        "content": [
            {"system": "legacy_policy_db", "adapter": "mainframe_adapter"},
            {"system": "new_policy_api", "adapter": "rest_adapter"}
        ],
        "insights": {
            "data_mash_strategy": "virtual",  # No ingestion
            "query_federation": True
        }
    },
    sync_strategies={
        "bi_directional": True,
        "conflict_resolution": "last_write_wins"
    }
)
```

---

## 6. Runtime Execution Flow (Canonical)

1. Interaction enters via Experience
2. Experience emits an **intent**
3. Runtime validates session, tenant, policy
4. Runtime records intent in WAL
5. Runtime resolves domain capability via Curator
6. Domain service executes under runtime context
7. Artifacts & events are recorded
8. Updates stream back to Experience

If Runtime cannot see it, **it did not happen**.

---

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
- **TTL:** Enforced by automated purge job (driven by policy + lifecycle state)
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
- SemanticDataAbstraction (stores embeddings in ArangoDB, with pluggable vector backends)
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
- **Reference preservation without material dependency** - meaning is independent

**Vector Search:**
- SemanticDataAbstraction backed by ArangoDB (with pluggable vector backends)
- Preserves architectural flexibility and avoids vendor lock-in
- Business logic uses abstraction, not direct vector backend

**Permanence:**
- Records of Fact are **permanent** (no expiration)
- They represent audit trail and must persist
- Source expiration tracked but doesn't affect Record of Fact

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
- **Lifecycle:** Tracked in Artifact Plane registry with explicit lifecycle states

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

**Classification Rule:**
> **By purpose, not format:**
> - Working Material = inputs used to reach conclusions
> - Purpose-Bound Outcome = conclusions created for a decision or delivery

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
- **Past versions are immutable** (read-only)

**Cross-Realm Dependencies:**
- Artifact Plane as coordination and reference source of truth (not execution owner)
- All Purpose-Bound Outcomes stored in Artifact Plane
- Cross-realm dependencies work automatically
- Artifact Plane coordinates and references, but does NOT orchestrate logic

**Search:**
- Artifact Plane supports search via registry queries
- Filter by: type, tenant, session, lifecycle_state, owner, purpose
- Enables artifact discovery and reuse

**Dependencies:**
- Track artifact → artifact dependencies in Artifact Plane
- Dependencies enable impact analysis
- Lineage enables audit trail
- Validate dependencies before deletion

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

**Classification Transitions:**
- **Allowed:** Working Material → Record of Fact (explicit `promote_to_record_of_fact()`)
- **Allowed:** Purpose-Bound Outcome → Platform DNA (explicit Curator promotion)
- **Not Allowed:** Automatic transitions, silent mutations, or transitions without policy approval
- All transitions are explicit, policy-governed, and recorded in WAL for audit

---

## 8. What Happens to Our Existing Code

### What we keep

* parsers
* embeddings
* analyzers
* SOP logic
* insight queries
* proposal generators
* **Public Works abstraction pattern** (validates swappability)

### What we strip out or relocate

* direct DB writes → Runtime artifacts
* internal retries → Runtime sagas
* implicit workflows → explicit intents
* ad‑hoc sessions → Runtime sessions
* **Current Runtime/Smart City/Realms implementations** → Archive (rebuild cleanly)

**Most logic stays. Control moves. Architecture rebuilds.**

---

## 9. Execution Plan (From Archive to MVP)

### Phase 0 — Foundation & Assessment

* Archive current implementations
* Audit Public Works (what to keep/update)
* Establish baseline
* Create execution plans

### Phase 1 — Tech Stack Evolution (via Public Works)

* Migrate Redis Graph → ArangoDB (adapter swap)
* Refactor WAL Lists → Streams (adapter enhancement)
* Remove Celery (cleanup)
* Add metrics export (OTEL config)

### Phase 2 — Runtime Execution Engine

* Intent Model
* Execution Context
* Execution Lifecycle Manager
* WAL integration (Streams)
* Saga orchestration (with outbox)
* Data Brain scaffolding

### Phase 3 — Civic Systems

* Smart City SDK + Primitives
* Experience Plane (separate service)
* Agentic SDK
* Platform SDK (Solution Builder + Realm SDK)

### Phase 4 — Domain Services (Rebuild with Contract)

* Content Realm (Runtime Participation Contract)
* Insights Realm (Runtime Participation Contract)
* Operations Realm (Runtime Participation Contract)
* Outcomes Realm (Runtime Participation Contract)

### Phase 5 — MVP Showcase Solution

* Build using Platform SDK
* Validate full execution flow
* Deploy for investors/customers

---

## 10. Pattern Adoption Principles

### Adopt Patterns, Not Products

**Key Principle:** Adopt patterns, not products. Keep implementations swappable.

**Examples:**
* **Durable Execution:** Temporal-inspired patterns, not Temporal product
* **Event Sourcing:** Event store pattern, swappable storage
* **Service Mesh:** Consul/Istio patterns, swappable mesh
* **Saga Pattern:** Standard saga pattern, swappable coordinator
* **Agentic SDK:** CrewAI/LangGraph-inspired, but custom implementation

**Why:** Clients may have requirements/limitations. We stay flexible.

**How:** All infrastructure via Public Works abstractions (swappable adapters).

---

## 11. Multi-Tenancy Requirements

**Context:** Multiple investors/customers will use the platform simultaneously.

**Requirements:**
1. **Tenant Isolation**
   * All data isolated by tenant_id
   * All execution isolated by tenant_id
   * All WAL events tagged with tenant_id

2. **Session Management**
   * Sessions are tenant-scoped
   * Users can only access their tenant's data
   * Admin dashboard per tenant

3. **Authentication**
   * User accounts are tenant-scoped
   * Login returns tenant_id
   * All API calls include tenant_id

**Implementation:**
* Runtime validates tenant_id on all intents
* State Surface isolates by tenant_id
* WAL isolates by tenant_id
* Frontend passes tenant_id with all requests

---

## Final Anchor

> **We are not defining everything the platform can do.**
> **We are defining the rules by which anything is allowed to happen.**

Symphainy is not an app.
It is a **governed execution substrate**.

Everything you build should make execution more explicit — not more clever.

---

## References

* [Platform Rules](PLATFORM_RULES.md) - Development standards
* [Patterns](patterns/) - Pattern documentation
* [Decisions](decisions/) - Architecture Decision Records
* [Execution Plans](../execution/) - Detailed implementation plans
