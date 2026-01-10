Symphainy Platform — v1 Execution Plan (Clean Rebuild)
Executive Framing (for the team)

We are building a platform-first execution spine and expressing use cases on top of it.

This is not:

an MVP-first build

a feature grab-bag

a refactor of legacy code

This is:

a clean platform build

with deterministic execution

grounded agent reasoning

multi-tenant by design

extensible to multiple enterprise solutions

Core Architectural Decisions (Locked)

These decisions resolve all prior ambiguity.

1. Clean Rebuild

New project / repo

No legacy code

Anything brought in is already refactored to platform standards

No “legacy adapters” exist

2. Execution Ownership

Runtime Plane owns execution

Curator owns capability registration

Realms compose logic

Agents reason, not execute

Experience submits intents, never runs logic

3. Capability by Design, Enabled by Policy

WAL, Saga, Zero Trust, multi-tenancy exist structurally from day one

Policies may be permissive in MVP

Enforcement tightens later without architectural change

Week-by-Week Execution Plan
Week 0 — Stabilize & Scaffold (2–3 days)

Goals

Lock structure

Eliminate ambiguity

Create a stable execution target

Deliverables

New repo scaffolded with agreed structure

Archived prior experiments (out of tree)

Tagged baseline (platform-v0)

CI boots (even if trivial)

Rules

No feature work

No realm logic

No agents yet

### Week 0.5 — Discovery & Mapping (Optional but Recommended)

**Purpose:** Understand what exists before building new

**Deliverables:**
- Map current services → platform structure
- Identify "valuable logic" vs "orchestration to replace"
- Document adapter interface contracts (if any legacy code will be referenced)
- Create capability inventory (what exists, what's needed)

**Output:**
- `docs/week0_discovery.md` - Service mapping document
- `docs/capability_inventory.md` - What exists vs what's needed (if needed)
- Adapter interface contracts (if needed)

**Rules:**
- No code changes
- Documentation only
- Reference only (no imports)

**Status:** ✅ **COMPLETE** - See `docs/week0_discovery.md`

Week 1 — Runtime Plane v0 (Execution Spine)

This week is the most important week of the entire build.

Runtime Plane Scope (Expanded per feedback)

Runtime owns:

Session lifecycle

Tenant context

Execution lifecycle

State surface

WAL

Saga coordination

Intent ingestion

Deterministic replay boundaries

Components to implement
1. Runtime Service (FastAPI)

/intent/submit

/session/create

/session/{id}

/execution/{id}/status

No business logic. No realms imported.

2. Session Lifecycle (Added per feedback)

Sessions are first-class, not incidental.

Session includes:

{
  "session_id": "...",
  "tenant_id": "...",
  "user_id": "...",
  "created_at": "...",
  "context": {},
  "active_sagas": []
}


Rules:

Every intent requires a session

Tenant is mandatory from day one

Single tenant allowed, but schema enforces isolation

3. Runtime State Surface

Purpose

Centralized recording of execution state

Runtime-owned, not realm-owned

Storage choice (aligned with your note):

Redis → hot, mutable execution state

ArangoDB → durable, queryable state graphs (later)

Week 1:

Redis-backed state surface

In-memory fallback allowed for tests

4. Write-Ahead Log (WAL)

Append-only log:

session_created

intent_received

saga_started

step_completed

step_failed

This enables:

Audit

Replay

Recovery

Deterministic debugging

5. Saga Skeleton

SagaCoordinator

SagaStep (interface)

SagaState tracked via state surface

No retries yet. No compensation logic yet. Just structure.

End-of-Week Deliverables

✅ Runtime Service running
✅ Session lifecycle working
✅ Intent ingestion working
✅ WAL writing events
✅ Saga skeleton registered
✅ State surface recording
✅ Integration tests passing (Week 1.5)

No realms yet. No agents yet. That's intentional.

### Week 1.5 — Integration Test (Critical Validation)

**Purpose:** Validate execution spine works end-to-end

**Deliverables:**
- End-to-end integration test:
  - Experience → Runtime → State → WAL
  - Session creation → Intent submission → Saga registration → State recording
- Test fixtures for Redis/ArangoDB
- Test utilities for WAL replay validation

**Test Scenarios:**
1. Create session → Submit intent → Verify WAL entry → Verify state
2. Replay execution from WAL → Verify deterministic replay
3. Multi-tenant isolation test (even if single tenant)

**Output:**
- `tests/integration/test_runtime_spine.py`
- Test utilities in `tests/utils/`
- CI integration (runs on every commit)

**Rules:**
- Must pass before Week 2 starts
- Tests are part of Week 1, not optional

Week 2 — Curator + Agent Foundation + Realm Wiring
2.1 Curator (Clarified)

Curator is NOT an executor.

Curator:

Registers capabilities

Defines capability metadata

Maps intent → capability reference

Example:

Curator.register(
  name="content.parse_and_embed",
  inputs=["binary_file"],
  outputs=["embeddings", "normalized_fields"],
  deterministic=True,
  realm="content"
)


Runtime:

Receives intent

Asks Curator: “what capability handles this?”

Executes via runtime-controlled flow

Routing happens in Runtime, resolution happens in Curator.

2.2 Agent Foundation (Clarified)

Agents are shared, not buried in realms.

Agent Foundation provides:

BaseAgent

GroundedReasoningAgentBase

Tool invocation via Runtime

Validation hooks

Agents:

Do not execute side effects

Do not manage state

Do not call infra directly

2.3 Grounded Reasoning (Incorporated)

Two-tier reasoning model (as you described):

Deterministic extraction

Content pillar agents

Normalization, embeddings

No inference beyond facts

Expert reasoning

Uses extracted facts

Can apply domain expertise

Must cite facts when determinism matters

This is implemented via:

Fact gathering phase

Reasoning phase

Optional validation phase (policy-controlled)

2.4 Realm Wiring (Thin Slice)

Pick Content Realm only this week.

Manager

Orchestrator

Services (parsing, embeddings)

Deterministic agents already exist here

Content Realm:

Registers saga steps

Emits facts

Writes no state directly

End-of-Week Deliverables

✅ Curator registering capabilities
✅ Agent Foundation base classes
✅ Grounded reasoning working
✅ Content Realm wired
✅ File upload → parsing → embeddings flow
✅ Saga completing end-to-end
✅ Observability metrics visible (Week 2.5)
✅ State inspectable via API

### Week 2.5 — Observability (Essential for Platform)

**Purpose:** Make execution inspectable and debuggable

**Deliverables:**
- Basic metrics collection:
  - Execution time per saga step
  - Success/failure rates
  - State surface size
  - WAL growth rate
- WAL replay validation tool
- State inspection API endpoints:
  - `/runtime/state/{execution_id}`
  - `/runtime/wal/{session_id}`
  - `/runtime/metrics`

**Metrics to Track:**
- Execution duration
- Saga step success rate
- State surface operations (get/set/delete counts)
- WAL event counts by type

**Output:**
- `platform/runtime/observability.py`
- Metrics endpoints in Runtime Service
- Basic dashboard (or API responses) for metrics

**Rules:**
- Metrics are lightweight (no heavy instrumentation)
- Focus on execution correctness, not performance tuning

Week 3 — Experience Plane (Thin but Real)
Experience Plane vs Foundation (Explicit)

Experience Foundation

SDKs

Client helpers

Auth helpers

Event helpers

Experience Plane

REST handlers

WebSocket handlers

Future delivery adapters (CRM, email, etc.)

Plane uses Foundation SDKs.

Intent Contract (Defined Early)
{
  "intent_type": "content.upload",
  "realm": "content",
  "session_id": "...",
  "tenant_id": "...",
  "payload": {...}
}


Responses:

Sync: acknowledgment + execution_id

Async: WS events or polling

MVP UI Integration

Existing demo UI survives

Points to new Runtime APIs

Admin / builder UI only

Not customer delivery yet

End-of-Week Demo

Multi-user sessions

Parallel uploads

Real-time progress via WS

Stable, repeatable execution

Multi-Tenancy (Your Note Addressed)

You’re right — include it from Week 1.

Implementation:

tenant_id required everywhere

Namespacing in Redis

WAL tagged by tenant

No cross-tenant reads allowed (even if single tenant)

Policy can be permissive. Architecture is not.

Final Notes to the Team

This plan intentionally avoids over-optimization

It prioritizes execution correctness

It keeps the platform extensible

It supports all three 2026 use cases without re-architecture

If something feels “missing,” it probably belongs in Runtime or Curator — not in a realm.