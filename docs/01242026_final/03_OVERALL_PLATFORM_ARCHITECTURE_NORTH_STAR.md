# Overall Platform Architecture North Star

**Date:** January 24, 2026  
**Status:** ✅ **CANONICAL VISION**  
**Purpose:** Holistic architectural vision combining frontend and backend into unified platform

---

## Executive Summary

Symphainy is a **governed execution platform** — a **Coexistence Fabric** — that enables enterprises to build AI-powered solutions incrementally while maintaining safety, compliance, and control.

> **Symphainy is a governed execution platform.**
> It runs **Solutions** safely — and those Solutions safely operate, connect to, and reason over external systems.
>
> It does this by binding **intent**, **policy**, **data cognition**, and **execution** under a **single runtime authority**.

Everything in this architecture exists to make execution **explicit, governed, replayable, and explainable**.

---

## The Four-Class Structural Model

Symphainy is composed of **four distinct classes** that must not collapse into each other:

### 1. Runtime Foundation (Execution Authority)

> **Runtime is the sole authority for committed execution and durable system state.**
> Other components may hold ephemeral, local, or speculative state, but only Runtime can make reality true.

**Owns:**
- Intent acceptance
- Execution lifecycle
- Session & tenant context
- Write-ahead log (WAL)
- Saga orchestration
- Retries & failure recovery
- Deterministic replay
- State transitions
- Runtime-native data cognition (Data Brain)

**Key Principle:** If something runs and Runtime doesn't know about it, **it is a bug**.

### 2. Civic Systems (Governance & Coordination)

> **Civic Systems define how things are allowed to participate in execution.**

**Five Civic Systems:**

1. **Smart City** — Governance (Security Guard, Traffic Cop, Data Steward, Curator, etc.)
2. **Experience** — Exposure (translates user actions into intents)
3. **Agentic** — Reasoning (agents reason under constraint)
4. **Platform SDK** — How solutions and domains are built correctly
5. **Artifact Plane** — Purpose-Bound Outcomes management

**Key Principle:** Civic Systems do NOT own business logic. They do NOT own execution. They define **capability by design, constrained by policy**.

### 3. Domain Services (Realms) — Business Logic

> **Only Realm domain services perform data access and mutation, always via Public Works abstractions.**
> Runtime orchestrates; Realms execute.

**Canonical Realms:**
- **Content** — Ingest, parse, embeddings, canonical facts
- **Insights** — Interpretation, analysis, mapping, querying
- **Journey** — SOPs, workflows, optimization recommendations
- **Outcomes** — Synthesis, roadmaps, POCs, proposals

**Key Principle:** Realms implement rich internal logic, but **do not own execution or state**. They participate in execution **only via Runtime contracts**.

### 4. Foundations (Public Works) — Infrastructure

> **Public Works is a governance boundary, not a convenience layer.**

**Provides:**
- Infrastructure abstractions (swappable)
- Adapter pattern (Layer 0: Adapters, Layer 1: Abstractions)
- Dependency injection
- Governance enforcement

**Key Principle:** All infrastructure access must go through Public Works abstractions. No direct Redis, ArangoDB, GCS, or Supabase calls in business logic.

---

## Frontend-Backend Integration

### The Critical Boundary

**Frontend:** Platform runtime that renders state and compiles user interaction into intent.

**Backend:** Execution engine that orchestrates intent and manages durable state.

**Integration Pattern:**
```
Frontend (symphainy-frontend)
    ↓ (submits intent)
Experience Plane (Experience Service)
    ↓ (routes intent)
Runtime Foundation (Runtime Service)
    ↓ (orchestrates)
Domain Services (Realms)
    ↓ (returns artifacts)
Runtime Foundation
    ↓ (records execution)
State Surface
    ↓ (syncs state)
Frontend (renders updated state)
```

### Session-First Integration

**Pattern:**
1. Frontend creates anonymous session (no auth required)
2. Frontend authenticates user (upgrades session)
3. Frontend submits intents via Experience Plane
4. Runtime orchestrates execution
5. Frontend receives execution updates (WebSocket)
6. Frontend renders state changes

**Key Principle:** Sessions exist independently of authentication. Authentication upgrades sessions.

---

## Data Classification Framework

### Four Classes of Data

1. **Working Materials** - Temporary, time-bound (FMS, GCS)
   - TTL enforced by policy
   - Purged when expired
   - Examples: Raw uploaded files, parsed results (temporary)

2. **Records of Fact** - Persistent meaning (Supabase + ArangoDB)
   - Must persist (auditable, reproducible)
   - Do NOT require original file to persist
   - Examples: Deterministic embeddings, semantic embeddings, interpretations

3. **Purpose-Bound Outcomes** - Intentional deliverables (Artifact Plane)
   - Owner, purpose, lifecycle states
   - Examples: Roadmaps, POCs, blueprints, SOPs

4. **Platform DNA** - Generalized capability (Supabase registries)
   - De-identified, generalizable, policy-approved
   - Examples: Promoted intents, realms, solutions

**Key Principle:** Classification by purpose, not format.

---

## Agent Architecture (4-Layer Model)

### Layer 1: AgentDefinition (Platform DNA)

**Location:** Supabase registry

**Contains:**
- Stable identity
- Constitution
- Capabilities
- Permissions

### Layer 2: AgentPosture (Tenant/Solution)

**Location:** Supabase registry

**Contains:**
- Behavioral tuning
- LLM defaults
- Compliance mode

### Layer 3: AgentRuntimeContext (Journey/Session)

**Location:** Assembled at runtime (never stored)

**Contains:**
- Session context
- Business context
- User journey state
- Ephemeral context

### Layer 4: Prompt Assembly

**Location:** Derived from layers 1-3

**Process:**
1. Load AgentDefinition (Layer 1)
2. Load AgentPosture (Layer 2)
3. Assemble AgentRuntimeContext (Layer 3)
4. Assemble system message from layers 1-3
5. Assemble user message from request + runtime context
6. Call `_process_with_assembled_prompt()`

**Key Principle:** All agents must implement `_process_with_assembled_prompt()`.

---

## Execution Flow (End-to-End)

### User Journey Example: File Upload → Parse → Embed → Analyze

1. **Frontend:** User uploads file
   - Component expresses intent: `submitIntent({ type: "upload_file", file: ... })`
   - Service layer hook submits intent via Experience Plane

2. **Experience Plane:** Receives intent
   - Validates session
   - Routes intent to Runtime

3. **Runtime:** Orchestrates execution
   - Records intent in WAL
   - Routes to Content Realm orchestrator
   - Creates execution context

4. **Content Realm:** Handles intent
   - Uses FileParserService (via Public Works abstractions)
   - Parses file
   - Returns artifact (not side effect)

5. **Runtime:** Records execution
   - Updates WAL
   - Stores artifact
   - Publishes events

6. **Frontend:** Receives update
   - WebSocket receives execution event
   - PlatformStateProvider updates state
   - Component re-renders with new state

**Key Principle:** All execution flows through Runtime. Frontend expresses intent. Realms execute. Runtime orchestrates.

---

## What This Architecture Protects Us From

- Demo-ware architectures
- Agent frameworks that can't be audited
- UX-driven execution bugs
- Tool lock-in
- Non-replayable outcomes
- "Magic" behavior no one can explain later

**They are not academic. They are defensive.**

---

## Key Architectural Invariants

### Invariant 1: Runtime as Single Execution Authority

**Rule:** Only Runtime can make committed, durable changes.

**Allows:**
- Ephemeral UI state in frontend
- Speculative agent reasoning
- Session-local context

**Prevents:**
- Execution outside Runtime
- State mutations without Runtime knowledge
- Non-auditable operations

### Invariant 2: Only Realms Touch Data

**Rule:** Only Realm domain services perform data access and mutation, always via Public Works abstractions.

**Allows:**
- Runtime to query metadata
- Experience to submit intents
- Agents to reason (but not access data directly)

**Prevents:**
- Data logic in Runtime
- Direct database calls outside Realms
- Data access without abstractions

### Invariant 3: Public Works as Governance Boundary

**Rule:** All infrastructure access must go through Public Works abstractions.

**Allows:**
- Adapters to call infrastructure directly (that's their job)
- Abstractions to be swappable

**Prevents:**
- Direct infrastructure calls in business logic
- Tool lock-in
- "It's just a wrapper" thinking

### Invariant 4: Intent-Based Execution

**Rule:** Frontend submits intents. Runtime orchestrates execution. Domain services handle intents.

**Allows:**
- Frontend to express user intent
- Agents to propose actions (via AGUI)

**Prevents:**
- Direct capability calls from frontend
- RPC thinking (intents ≠ function calls)
- Non-deterministic execution

### Invariant 5: Policy-Governed Sagas

**Rule:** Execution is governed by policy. Sagas replace ACID transactions.

**Allows:**
- Intent-bounded execution
- Explicit promotion workflows
- Compensatable failure patterns

**Prevents:**
- ACID transaction thinking
- Commits in agents
- Commits in domain services

---

## Service Communication Patterns

### Frontend → Experience Plane

**Pattern:** HTTP API + WebSocket

**Examples:**
- `POST /api/session/create` - Create session
- `POST /api/intent/submit` - Submit intent
- `WebSocket /api/runtime/agent` - Agent communication

### Experience Plane → Runtime

**Pattern:** HTTP API

**Examples:**
- `POST /api/session/create` - Create session
- `POST /api/intent/submit` - Submit intent
- `GET /api/execution/{id}/status` - Get execution status

### Runtime → Realms

**Pattern:** Direct invocation

**Flow:**
1. Runtime receives intent
2. Runtime routes to appropriate realm orchestrator
3. Orchestrator handles intent
4. Orchestrator returns artifacts
5. Runtime records execution in WAL

### Realms → Public Works

**Pattern:** Dependency injection

**Example:**
```python
class ContentOrchestrator:
    def __init__(self, public_works: PublicWorksFoundationService):
        self.file_storage = public_works.get_file_storage_abstraction()
        self.semantic_data = public_works.get_semantic_data_abstraction()
```

---

## Data Flow (End-to-End Example)

### File Upload → Parse → Embed → Analyze

1. **Frontend:** User uploads file
   - Component: `FileUploader.tsx`
   - Hook: `useFileAPI().uploadAndProcessFile()`
   - Service: `ExperiencePlaneClient.submitIntent()`

2. **Experience Plane:** Receives intent
   - Endpoint: `POST /api/intent/submit`
   - Validates session
   - Routes to Runtime

3. **Runtime:** Orchestrates execution
   - Records intent in WAL
   - Routes to Content Realm
   - Creates execution context

4. **Content Realm:** Handles intent
   - Orchestrator: `ContentOrchestrator.handle_intent()`
   - Service: `FileParserService.parse_file()`
   - Uses: `FileStorageAbstraction` (Public Works)
   - Returns: Artifact

5. **Runtime:** Records execution
   - Updates WAL
   - Stores artifact
   - Publishes events

6. **Frontend:** Receives update
   - WebSocket receives event
   - `PlatformStateProvider` updates state
   - Component re-renders

**Key Principle:** All execution flows through Runtime. All data access through Realms. All infrastructure through Public Works.

---

## What Makes This Different

### Traditional Platforms

- Execution is implicit
- State is scattered
- Data meaning is inferred but not tracked
- Agents act autonomously
- Governance is bolted on later

### Symphainy Platform

- Nothing executes without **intent**
- Nothing executes without **policy**
- Nothing executes without **attribution**
- Nothing executes **outside the Runtime**
- Everything is **explicit, governed, replayable, and explainable**

---

## Platform Capabilities

### Content Realm

- File ingestion (upload, EDI, API)
- File parsing (PDF, Excel, binary, images, BPMN, DOCX)
- Deterministic embeddings
- Semantic embeddings
- File lifecycle management

### Insights Realm

- Data quality assessment
- Semantic interpretation
- Interactive analysis (structured and unstructured)
- Guided discovery
- Lineage tracking
- Business analysis

### Journey Realm

- Workflow creation from BPMN
- SOP generation from interactive chat
- Visual workflow generation
- Coexistence analysis
- Blueprint creation

### Outcomes Realm

- Solution synthesis
- Roadmap generation
- POC (Proof of Concept) creation
- Artifact export
- Business outcome tracking

---

## Next Steps

1. Understand the four-class model
2. Follow the architectural principles
3. Use Public Works abstractions
4. Submit intents, don't call capabilities
5. Return artifacts, not side effects

---

**Last Updated:** January 24, 2026  
**Status:** ✅ **CANONICAL VISION**
