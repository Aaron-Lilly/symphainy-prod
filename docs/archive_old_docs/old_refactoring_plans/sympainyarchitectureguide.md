Absolutely. Below is a **clean, locked, canonical version** incorporating your edits *and* the final cleanup we discussed. This is ready to hand to the team as **the source of truth**.

I’ve kept the tone authoritative, removed ambiguity, and closed the doors that previously let behavior leak or evaporate.

---

# Platform Architecture Guide

**Status:** Canonical (Locked — January 2026)
**Applies to:** All platform code, demos, and production deployments

This guide defines the **authoritative architectural model** for the platform. It exists to ensure:

* Shared mental models across the team
* Clear ownership of logic and responsibility
* Functional substance does not evaporate into contracts
* Safe extensibility as Runtime and Civic Systems evolve

If there is ambiguity between code and this guide, **this guide wins**.

---

## 1. Architectural Thesis

The platform is built around a single core principle:

> **The platform is SDK-driven and governance-first, with a single execution authority.**

More explicitly:

* **Behavior lives in SDKs**
* **Governance is applied continuously**
* **Execution happens once**
* **Runtime validates and records — it does not coordinate**

This architecture exists to:

* Avoid a monolithic `main.py`
* Prevent logic from dissolving into empty contracts
* Keep SOA coordination strong without coupling to Runtime
* Scale from demos to 350k-policy production workloads

---

## 2. High-Level Architectural Layers

The platform is organized into **four architectural layers**.

Deployment is containerized-first and hybrid-ready, but **deployment topology is not an architectural boundary**.

```
A. Public Works (Foundations)
B. Civic Systems (Behavior & Governance)
C. Realm Services (Domain Execution)
D. Runtime Execution Engine (Validation & State)
```

Each layer has **explicit responsibilities and forbidden behaviors**.

---

## 3. Public Works (Foundations)

**Purpose:** Abstract underlying technology.

**Responsibilities:**

* Infrastructure adapters (storage, auth, messaging, compute)
* BYOI (Bring Your Own Infrastructure) support
* Replaceability and portability

**Hard Rule:**

> **Public Works abstracts technology only — never platform behavior.**

All infrastructure access flows **upward** through SDKs and primitives.

---

## 4. Civic Systems (Behavioral Backbone)

Civic Systems are the **platform’s behavioral center**.

They do not execute domain work.
They do not own infrastructure.
They **coordinate, govern, translate, and validate**.

Civic Systems are **SDK-first, not service-first**.

---

### 4.1 Experience System (SDK)

**Purpose:** Interface between users / external systems and the platform.

**Responsibilities:**

* Web UI
* WebSockets and streaming
* REST & external APIs
* Session awareness
* Intent formulation

**Hard Rules:**

* ❌ Never executes domain work
* ❌ Never enforces policy
* ❌ Never calls Runtime
* ❌ Never calls Realm services directly
* ✅ Always emits *intent* and consumes *results*

**Canonical Output:**

```json
{
  "intent": "content.parse",
  "inputs": {
    "file_id": "...",
    "solution_id": "..."
  }
}
```

The **Experience SDK** standardizes:

* Session lifecycle
* Streaming semantics
* Chat behavior
* External API consistency

---

### 4.2 Solution System (Civic System & SDK)

**Purpose:** Own platform flows and cross-realm composition.

Solution is a **Civic System** that exposes a **Solution SDK**.

**Responsibilities:**

* Define end-to-end flows (e.g. data → insights → journey → solution)
* Compose Realm capabilities
* Register composed flows with Curator at startup
* Prepare execution plans for Runtime validation

> **Solution decides *what happens*.**
> **Smart City decides *is this allowed*.**
> **Runtime decides *can this execute safely*.**

Solution is the **SOA-facing composition authority** of the platform.

---

### 4.3 Smart City (Governance & Coordination)

**Role:** Platform governance and operational coordination.

Smart City is **SDK-first**, with two complementary parts.

---

#### a. Smart City SDK (Primary)

**Used by:** Experience, Solution, Realm services

**Responsibilities:**

* Standardize platform behavior
* Coordinate SOA-facing operations
* Apply governance *before* execution
* Prepare execution contracts for Runtime

The SDK is composed of **role modules** (Traffic Cop, Librarian, Curator liaison, Conductor, etc.), implemented as **code**, not services.

Example:

```python
traffic_cop.manage_session(ctx)
librarian.resolve_semantic_query(ctx)
conductor.build_execution_plan(ctx)
```

> **This is where the platform “does work” at the coordination level.**

SDKs define behavior.
SOA APIs expose that behavior — they never redefine it.

---

#### b. Smart City Primitives (Runtime-Time)

**Used by:** Runtime only

**Responsibilities:**

* Stateless validation
* Policy enforcement
* Go / No-Go decisions
* Execution annotations

Primitives operate only on **execution context**.

> **Primitives never coordinate.**
> **They only validate what SDKs already prepared.**

---

### 4.4 Curator (Smart City Module)

Curator is a **Smart City capability**, not a standalone system.

**Role:** Discovery, registries, and platform topology.

Curator owns **what exists and where it lives**.

**Responsibilities:**

* Service registry (interpreting Consul)
* Policy registry
* Solution registry
* Agent registry
* Capability projection

**Key Clarifications:**

* Consul is infrastructure
* Curator *interprets* Consul
* Registries describe **real, composed things** — not hypothetical atoms

Curator is accessed via the **Smart City SDK**, not business APIs.

---

## 5. Realm Services (Domain Execution)

**Purpose:** Perform domain-specific work.

Examples:

* Content
* Insights
* Journey
* Operations

> **Journeys compose Insights.
> Insights compose Content.**

**Responsibilities:**

* Domain business logic
* Data transformation
* Deterministic computation
* Domain persistence

**Rules:**

* Use **Civic System SDKs** (Solution, Smart City, Experience, Agentic)
* Expose SOA APIs
* ❌ Never call Runtime directly
* ❌ Never enforce governance independently

> Realms *do the work*, but never decide whether the work is allowed.

---

## 6. Runtime Execution Engine

**Purpose:** Single execution authority and state surface owner.

**Responsibilities:**

* Validate execution contracts
* Invoke Smart City primitives
* Execute domain work
* Maintain:

  * State surface
  * Data brain
  * Lineage & WAL
* Ensure deterministic replay

**Hard Rules:**

* ❌ No business logic
* ❌ No orchestration decisions
* ❌ No SOA awareness
* ❌ No agent reasoning

> Runtime never originates execution intent.
> It only validates and executes what Civic Systems define.

Runtime may decompose and recompose execution plans **ephemerally**, but never as a source of truth.

---

## 7. Agents & Agentic SDK

**Agents:**

* Reason only
* Never execute
* Never call Runtime
* Never own state

**Agentic SDK Provides:**

* Agent registry
* MCP tool wiring
* Reasoning scaffolds
* Structured outputs

**Critical Rule:**

> **MCP tools are not runtime concerns.**

Agents produce **conclusions and intent suggestions**, not side effects.

---

## 8. Libraries vs Registries

### Libraries

* Code
* Versioned
* Imported
* Behavioral

Examples:

* Smart City SDK
* Solution SDK
* Experience SDK
* Agentic SDK
* Policy libraries
* Execution context models

---

### Registries

* Data-backed
* Queried
* Runtime-visible
* Owned by Civic Systems

Canonical Registries:

* Policy Registry
* Service Registry
* Solution Registry
* Agent Registry
* Session / Tenant Registry

> If something does not exist independently at runtime, it does not belong in a registry.

---

## 9. Forbidden Patterns (Non-Negotiable)

* ❌ Realms calling Runtime
* ❌ Experience bypassing Solution composition
* ❌ Reimplementing Smart City behavior in services
* ❌ Runtime coordinating SOA flows
* ❌ Agents executing side effects
* ❌ Registry-first design without working behavior

If you feel tempted to do one of these, stop — the architecture is being violated.

---

## 10. Design Guarantees

If this guide is followed, the platform guarantees:

* SDKs remain the behavioral center
* SOA stays consistent without spaghetti
* Runtime remains scalable and deterministic
* Governance evolves without refactoring domains
* Functional substance is preserved

---

## 11. Canonical Mental Model

> **Behavior lives in SDKs.**
> **Governance validates continuously.**
> **Execution happens once.**
> **State is observed, not reinvented.**

Or even shorter:

> **Compose in Solution.
> Govern in Smart City.
> Execute in Runtime.
> Persist in Realms.**

If a design respects these statements, it is correct.

---

**End of Guide**
