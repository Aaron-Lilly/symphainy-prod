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

There are four Civic Systems:

1. **Smart City** — governance
2. **Experience** — exposure
3. **Agentic** — reasoning
4. **Platform SDK** — how solutions and domains are built correctly

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
| Curator        | Capability, agent, domain registries   |
| Data Steward   | Data boundaries, contracts, provenance |
| Librarian      | Semantic schemas & meaning             |
| Traffic Cop    | Sessions, execution IDs, correlation   |
| Post Office    | Event routing & ordering               |
| Conductor      | Workflow & saga primitives             |
| Nurse          | Telemetry, retries, self‑healing       |

**Smart City Architecture:**
* **SDK-First:** Smart City SDK provides coordination logic (used by Experience, Solution, Realms)
* **Primitives:** Smart City Primitives provide policy decisions (used by Runtime only)
* **Separation:** SDK coordinates, Primitives validate

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

## 7. The Data Brain (Runtime‑Native Data Cognition)

> **Data participates in execution without being centralized.**

The Data Brain lives **inside Runtime**.

It owns:
* data references & provenance
* semantic projection (deterministic + expert)
* virtualization & hydration
* mutation governance
* execution‑level attribution

It enables:
* data mash without ingestion
* explainable interpretation
* replayable migration
* safe bi‑directional sync

### 7.1 Data Brain Scaling Patterns

For large-scale deployments (e.g., 350k policies):

**1. Reference-First Architecture**
* Data Brain stores references, not data
* Hydration happens on-demand via domain services
* Virtual queries federate across external systems

**2. Bi-Directional Sync Strategy**
* Runtime tracks mutations in WAL
* Domain services implement sync adapters
* Data Brain coordinates sync without owning data

**3. Provenance at Scale**
* Provenance stored as execution-level metadata
* Lineage queries use indexed references
* Full history replayable from WAL

**4. Snapshot Strategy**
* Periodically snapshot state for performance
* Replay from snapshot + events since snapshot
* Critical for 350k policies (can't replay millions of events)

**Critical Rule:**
> **Phase 2 Data Brain never returns raw data by default — only references.**

That single rule preserves:
* scalability
* governance
* replayability

You can always add "hydration" later.

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
