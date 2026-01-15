# Symphainy Architectural Flow Guide

**How the Platform Runs Solutions Safely — and How Solutions Safely Interact with Systems**

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

---

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

---

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
4. **Platform SDK (Realm SDK)** — how solutions and domains are built correctly

Civic Systems may depend on each other, but **Runtime remains the single execution authority**.

---

### 2.3 Domain Services (Formerly “Realms”)

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

---

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

```text
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

---

### 4.2 Experience (Exposure & Interaction)

> **Experience translates external interaction into intent.**

Experience:

* exposes REST, WebSockets, chat, adapters
* authenticates callers
* establishes sessions via Runtime
* translates user actions into **intents**
* streams execution updates back

Experience never:

* calls domain services directly
* manages workflows
* owns state

---

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

---

### 4.4 Platform SDK (Realm SDK / Civic Front Door)

> **The Platform SDK defines how solutions and domain services are built correctly.**

This SDK:

* is the *front door* for building on Symphainy
* configures client‑specific policies, capabilities, and integrations
* composes Civic Systems into usable building blocks

It is how:

* your team builds the MVP showcase
* external developers build their own solutions
* agentic coders generate compliant services

---

## 5. Solutions (The Vehicle for Running Systems)

> **The platform runs Solutions; Solutions run systems.**

A Solution:

* defines **solution context** (goals, constraints, risk)
* declares supported intents
* binds domain services to external systems

The platform never interacts with external systems directly — it does so **through Solutions**.

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

---

## 8. What Happens to Our Existing Code

### What we keep

* parsers
* embeddings
* analyzers
* SOP logic
* insight queries
* proposal generators

### What we strip out or relocate

* direct DB writes → Runtime artifacts
* internal retries → Runtime sagas
* implicit workflows → explicit intents
* ad‑hoc sessions → Runtime sessions

**Most logic stays. Control moves.**

---

## 9. Execution Plan (From Blank Repo to MVP)

### Phase 1 — Platform Scaffolding

* pyproject.toml / requirements.txt
* Docker compose & base containers
* repo structure aligned to this guide

### Phase 2 — Runtime Execution Engine

* intent model
* execution context
* WAL
* saga orchestration
* Data Brain scaffolding

### Phase 3 — Civic Systems

* Smart City primitives
* Experience adapters
* Agentic SDK
* Platform SDK (front door)

### Phase 4 — Domain Services (Refactor, not rewrite)

* wrap existing Content logic as Runtime participants
* do the same for Insights, Operations, Outcomes

### Phase 5 — MVP Showcase Solution

* build using the Platform SDK
* validate full execution flow
* ship

---

## Final Anchor

> **We are not defining everything the platform can do.**
> **We are defining the rules by which anything is allowed to happen.**

Symphainy is not an app.
It is a **governed execution substrate**.

Everything you build should make execution more explicit — not more clever.
