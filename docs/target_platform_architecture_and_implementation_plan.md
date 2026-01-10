# Symphainy Target Platform Architecture & Implementation Plan (LOCKED)

This document consolidates the **final, agreed-upon platform architecture**, incorporating the runtime/state epiphany, Smart City governance model, deterministic + expert agent strategy, and the clarified role of Experience, Curator, and Content/Insights separation.

This is the **single source of truth** for:

* Internal engineering alignment
* Outsourcing / partner execution
* Cursor-guided refactors
* Investor / customer technical narrative

---

## SECTION 1 — WHAT SYMPHAINY IS (FINAL)

**Symphainy is an Agentic Integrated Development Platform (IDP) + Agentic Operating System (AOS)** that enables enterprises to:

* Bring their own infrastructure (BYOI)
* Bring their own interfaces (BYOH)
* Build AI-powered enterprise solutions incrementally
* Combine deterministic AI + expert reasoning
* Operate safely in regulated, multi-tenant environments

Symphainy separates **intent, execution, state, capability, and reasoning** — which is what allows it to scale beyond demos into production-grade AI systems.

---

## SECTION 2 — THE PLANES (FINAL & LOCKED)

### Plane 1: Runtime Plane (Execution Substrate)

**Owns (by design):**

* Sessions
* State (authoritative record)
* Intent lifecycle
* Execution lifecycle
* IDs (session_id, workflow_id, saga_id, event_id)
* Write-Ahead Logging (WAL)
* Saga coordination (async workflows)
* Replay & recovery hooks
* Determinism boundaries

**Does NOT own:**

* Business logic
* Domain reasoning
* Smart City services
* Infrastructure adapters

> Runtime is the *only* thing allowed to advance execution.

### Plane 2: Smart City Plane (Capability Governor)

**Owns:**

* Zero Trust & tenancy semantics
* Security enforcement
* Workflow governance
* Event routing
* Telemetry & tracing
* Knowledge governance
* Policy enforcement (when enabled)

Smart City **does not execute work**.
It **registers capabilities, policies, and constraints** into the Runtime.

> City Manager is a registrar and governor — not a god object.

### Plane 3: Realm Plane (Operating Domains)

Realms are **bounded operating systems**, not platforms:

* Content
* Insights
* Journey (Operations)
* Solution (Business Outcomes)

They:

* Consume runtime context
* Invoke Smart City capabilities
* Register saga steps
* Produce domain outputs

They do **not**:

* Create sessions
* Persist state directly
* Control execution order

### Plane 4: Experience Plane (Delivery Surface)

Experience is **not a foundation**.

It includes:

* REST APIs
* WebSockets
* Admin / Builder UI
* CRM / ERP / Voice / RPA adapters

It:

* Accepts intent
* Streams state
* Delivers outcomes

Experience never owns state.

---

## SECTION 3 — FOUNDATIONS (CLARIFIED)

### Public Works Foundation

* Infra adapters
* IO adapters
* Cloud / storage / messaging

### Curator Foundation (Refocused)

**Curator is the capability executor + registry.**

It:

* Registers executable capabilities
* Knows *how* a capability is executed
* Bridges runtime intent → foundation execution

It does **not**:

* Decide *when* to execute
* Orchestrate workflows
* Manage state

### Agentic Foundation

**Agents live here.**

They are:

* Reasoning engines
* Planners
* Analysts

They are:

* Realm-attached by contract
* Runtime-executed

---

## SECTION 4 — AGENTS (FINAL MODEL)

### Agent Types

1. **Deterministic Agents**

   * Used for parsing, embedding, normalization
   * Same input → same output
   * No creativity

2. **Grounded Reasoning Agents**

   * Use facts from tools
   * Must cite sources
   * Validated against hallucination

3. **Expert Reasoning Agents**

   * Domain expertise (insurance, permits, T&E)
   * Bounded by available facts
   * Allowed judgment, not invention

### Content vs Insights Clarification (Critical)

**Content Realm**

* Deterministic parsing
* Deterministic embeddings
* Deterministic normalization

**Insights Realm**

* Semantic interpretation
* Data quality analysis
* Data mash reasoning
* Mapping logic

This two-hop model maximizes auditability and repeatability.

---

## SECTION 5 — RUNTIME + STATE SURFACE (WHAT “LIGHTWEIGHT” MEANS)

Runtime v1 is **capability-complete, policy-light**.

### Included by Design

* SessionContext
* ExecutionContext
* IntentContext
* StateSurface (append-only)
* WAL (durable)
* Saga registration & advancement
* Event emission

### Policy-Disabled (for MVP)

* Auto-replay
* Auto-healing
* Hard idempotency enforcement
* SLA enforcement

### State Storage

* Redis (hot/session state)
* Postgres / Supabase (durable state)
* Object storage (large artifacts)

Runtime coordinates — it does not store data itself.

---

## SECTION 6 — EXPERIENCE PLANE (CLARIFIED)

### Experience Foundation

* SDKs
* Client adapters
* Protocol helpers

### Experience Plane

* REST handlers
* WebSocket handlers
* UI surfaces

Flow:

```
Experience Plane → Runtime Plane → Realms → Smart City
```

Your existing demo UI:

* Survives
* Becomes Admin / Builder UI
* Gains state-driven behavior

---

## SECTION 7 — FILESYSTEM SCAFFOLD (END STATE)

```text
symphainy/
├── runtime/
│   ├── surfaces/
│   ├── wal/
│   ├── saga/
│   └── runtime.py
│
├── smart_city/
│   ├── plane.py
│   ├── services/
│   └── policies/
│
├── realms/
│   ├── content/
│   ├── insights/
│   ├── journey/
│   └── solution/
│
├── agents/
│   ├── base/
│   ├── content/
│   ├── insights/
│   ├── journey/
│   └── solution/
│
├── experience/
│   ├── api/
│   ├── websocket/
│   └── ui/
│
├── foundations/
│   ├── public_works/
│   ├── curator/
│   └── agentic/
│
├── main.py
└── README.md
```

---

## SECTION 8 — EXECUTION MODEL (REFERENCE FLOW)

Example: Content Upload → Semantic Ready

1. Experience submits intent
2. Runtime creates session
3. WAL records intent
4. Content Realm registers saga
5. Parsing service executes
6. Deterministic embeddings created
7. State recorded centrally
8. Saga completes
9. Events emitted

Agents reason — Runtime executes.

---

## SECTION 9 — REFACTOR & BUILD PLAN (SAFE & EXTENSIBLE)

### Phase 0 — Freeze & Archive

* No feature work
* Archive legacy backend

### Phase 1 — Runtime Plane

* Build runtime + state surface
* WAL + saga skeletons

### Phase 2 — Smart City Plane

* Rebuild services as governors

### Phase 3 — Content & Insights Migration

* Preserve deterministic logic
* Move interpretation to Insights

### Phase 4 — Agents: Restore + Ground

* Extract critical reasoning agents
* Implement grounded reasoning base
* Attach to realms

### Phase 5 — Experience Plane Expansion

* Align REST + WS to runtime state
* Upgrade admin / builder UI
* Prepare delivery adapters

---

## FINAL NOTE (THE PLATFORM LOCK)

You are no longer building:

* An MVP
* A single use case
* A demo with aspirations

You are building:

> **A platform that can safely produce many solutions over time.**

The MVP is simply the first expression of that platform.

This document is now the architectural contract.
