# Platform Architecture Document

*(Current State + Target Vision)*

## Executive Summary

You are building an **Enterprise-grade Agentic Platform** that serves as:

* A **technical front door** for enterprises to build, operate, and evolve AI-enabled systems
* A **business front door** where solutions are designed, reasoned about, audited, and delivered
* A **headless, production runtime** that executes deterministic + agentic workflows safely at scale

This is not an “AI app.”
It is an **Agentic Integrated Development + Execution Platform (A-IDEP)**.

---

## Core Architectural Principles

1. **Separation of concerns**

   * Deterministic execution ≠ reasoning ≠ delivery
2. **Capability by design, enabled by policy**

   * Runtime ships *complete*
   * Tenancy, auth, guardrails, scale are policy-gated
3. **Determinism where required, expertise where valuable**

   * Data mash ≠ creative reasoning
4. **Everything is inspectable**

   * WAL, Saga, grounding, lineage, auditability
5. **Solutions are configurations of platform capabilities**

   * Not bespoke code paths

---

## Platform Layers (Authoritative Model)

### 1️⃣ Runtime Plane (Execution Core)

**Purpose:**
Owns *stateful execution* of workflows, agents, and side effects.

**Responsibilities**

* Workflow execution engine
* Write-Ahead Log (WAL)
* Saga orchestration (async, compensating actions)
* Deterministic replay
* Multi-tenant isolation
* Zero-trust boundaries
* State Surface (authoritative execution state)

**Key properties**

* LLM-agnostic
* Agent-agnostic
* UI-agnostic
* Headless

> If Experience disappears tomorrow, Runtime still runs the business.

---

### 2️⃣ Agentic Foundation (Shared Reasoning Substrate)

**Purpose:**
Provide *how agents reason*, not *where they live*.

**Contains**

* Agent SDK
* GroundedReasoningAgentBase
* Tool composition
* Fact extraction
* Validation & hallucination detection
* Memory adapters (short / long / vector)
* Determinism controls

**Important clarification**

* Agents are **not owned by realms**
* Agents are **attached to realms**
* Agents are **executed by the runtime**

This is the fix for your earlier brittleness.

---

### 3️⃣ Realms (Semantic Ownership Zones)

Realms define *intent and semantics*, not infrastructure.

#### Content Realm

* Deterministic extraction & normalization
* Parsing (binary, structured, unstructured, hybrid)
* Copybook → fields
* Embeddings creation (stateless, deterministic)
* No interpretation

#### Insights Realm

* Data quality analysis
* Semantic interpretation
* Structured ↔ structured mapping
* Unstructured → structured meaning
* Data mash *finalization*

#### Operations Realm

* SOP ↔ Workflow dual views
* SOP Builder (chat + structured)
* Workflow orchestration design
* Coexistence analysis & blueprints

#### Solution Realm

* Solution landing
* Pillar synthesis
* Roadmaps
* POC proposals
* Business-facing narrative outputs

---

### 4️⃣ Curator (Refocused)

**Curator = Capability Registry + Executor Router**

What it **is**:

* Registry of platform capabilities
* Maps “intent” → runtime executable units
* Knows *what exists*, not *how to reason*

What it is **not**:

* Not a planner
* Not an orchestrator
* Not a UI brain

Think: **capability catalog + dispatch table**.

---

### 5️⃣ Experience Plane (Delivery Layer)

**Purpose:**
Deliver platform capabilities to *humans and systems*.

**Includes**

* Admin / Builder UI (clients)
* Solution UIs (customer-facing)
* REST APIs
* WebSockets
* Event streams

**Key rule**

> Experience reflects runtime state — it never invents it.

Your existing demo UI survives here and becomes *stronger*, not weaker.

---

## Current State (MVP Showcase)

You already have:

* Parsing logic (Content)
* Embedding pipelines
* Early agents
* SOP / workflow visualization
* Roadmap / proposal outputs
* Containerization foundations

What you’re adding:

* Proper Runtime Plane
* Agent grounding
* Clean realm boundaries
* Durable state + replay
* Execution-first design

---

## Future Vision

This platform supports:

* Regulated AI systems
* Auditable automation
* AI as infrastructure, not novelty
* Multiple industries without re-architecture
* Internal agents building internal capabilities