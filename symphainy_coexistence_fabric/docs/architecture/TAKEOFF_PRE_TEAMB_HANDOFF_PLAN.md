# Takeoff Pre–Team B Handoff: Detailed Implementation Plan

**Purpose:** Concrete steps for Takeoff to complete **before** handing off to Team B (Landing). When done, Team B “implements the intent contracts and uses the Experience SDK”; Takeoff “exposes the runtime contracts that plug into that.”

**References:**
- [solution_realm_refactoring_vision.md](../solution_realm_refactoring_vision.md) — target architecture
- [EXPERIENCE_CIVIC_REFACTOR_PLAN.md](EXPERIENCE_CIVIC_REFACTOR_PLAN.md) — Phase 1 & 2 source
- [EXPERIENCE_CIVIC_SYSTEM_AUDIT.md](EXPERIENCE_CIVIC_SYSTEM_AUDIT.md) — current state vs vision
- [LANDING_AGENT_TASKS.md](../LANDING_AGENT_TASKS.md) — what Team B does after handoff

---

## Handoff Statement (Target Outcome)

When this plan is complete:

1. **Experience Civic Phase 1 & 2 are locked** — Experience SDK contract is defined and implemented; all Experience routes go through the SDK facade; RuntimeClient is aligned with Runtime API.
2. **Intent contracts are reviewed** — Aligned with the vision; runtime obligations (registration, execution, state, artifacts) are documented per intent / per journey.
3. **Runtime contracts are documented** — A single doc describes the platform surfaces (IntentRegistry, ExecutionContext, state surface, artifact surface, execution lifecycle) that intent implementations plug into.
4. **Handoff package is published** — Team B receives: (a) Experience SDK contract, (b) Runtime contracts doc, (c) reviewed intent contracts + runtime obligations. Team B’s remit: “Implement the intent contracts and use the Experience SDK.” Takeoff’s remit: “Expose the runtime contracts that plug into that.”

---

## Part A: Lock Experience Civic Phase 1 & 2

Execute the following **atomic, assignable tasks** in order. Each has clear acceptance criteria.

### A.1 Phase 1: Contract and Alignment

#### Task A.1.1 — Define Experience SDK contract (doc + optional type)

| Item | Detail |
|------|--------|
| **Owner** | Takeoff |
| **Artifacts** | `docs/architecture/EXPERIENCE_SDK_CONTRACT.md`; optional Python protocol/ABC in `symphainy_platform/civic_systems/experience/sdk/experience_sdk.py` |
| **Content** | Document these operations with names, intent, and minimal request/response shapes: |
| | • **query_state** — session + execution status + artifacts (`tenant_id`, `session_id`, optional `execution_id`) |
| | • **invoke_intent** — submit intent (`intent_type`, `parameters`, `tenant_id`, `session_id`, `solution_id`) |
| | • **trigger_journey** — same as invoke_intent with compose_journey (or document as alias) |
| | • **subscribe** — execution updates (`execution_id`) via stream or WebSocket; document current behavior (e.g. Experience WebSocket or polling) and target behavior |
| **Optional** | Python protocol or ABC with methods matching the doc; types only, no behavior change |
| **Acceptance** | [ ] Doc exists; [ ] Optional protocol exists; [ ] Existing Experience API and Runtime unchanged |

#### Task A.1.2 — Align RuntimeClient with Runtime API

| Item | Detail |
|------|--------|
| **Owner** | Takeoff |
| **Session state** | Runtime exposes GET `/api/session/{session_id}`. RuntimeClient may call `/api/session/{session_id}/state`. Either (A) add `/state` on Runtime, or (B) change RuntimeClient to use GET `/api/session/{session_id}` and map response to “state” shape. **Prefer (B).** |
| **Execution stream** | Runtime has GET `/api/execution/{id}/status` only. Either (A) add stream on Runtime, or (B) document “subscribe” as polling status for now; change RuntimeClient.stream_execution to poll or remove until Runtime supports stream. Document in EXPERIENCE_SDK_CONTRACT. |
| **Realms** | RuntimeClient.get_realms() calls GET `/api/realms`. If Runtime does not expose this: (A) add GET `/api/realms` on Runtime, or (B) remove get_realms from RuntimeClient and from any Experience route that uses it; document in contract. |
| **Acceptance** | [ ] RuntimeClient works against current Runtime (or minimal Runtime changes); [ ] No 404s for session state; [ ] Stream/realms either implemented or documented as deferred |

#### Task A.1.3 — Boot docs: Φ3 → SDK ready, Φ4 = attach experience

| Item | Detail |
|------|--------|
| **Owner** | Takeoff |
| **Location** | `docs/architecture/INIT_ORDER_SPEC.md` or new `docs/architecture/BOOT_PHASES.md` |
| **Content** | State that after Φ3 (runtime graph built), the **Experience SDK surface is available**. Φ4 = attach experience surfaces to that SDK (no-op stub acceptable). |
| **Optional** | In code, after `create_runtime_services()` in experience_main (or runtime_main), add comment or no-op step: “Φ4 — attach experience surfaces (see EXPERIENCE_SDK_CONTRACT).” |
| **Acceptance** | [ ] Docs state north star (“Startup succeeds when Experience SDK is ready”); [ ] Φ4 is named; [ ] Optional code stub |

---

### A.2 Phase 2: Experience SDK Facade and Route Wiring

#### Task A.2.1 — Implement Experience SDK facade

| Item | Detail |
|------|--------|
| **Owner** | Takeoff |
| **Location** | `symphainy_platform/civic_systems/experience/sdk/experience_sdk.py` (or equivalent) |
| **Behavior** | Implement contract from Phase 1. For out-of-process: delegate to RuntimeClient (HTTP to Runtime) and SecurityGuard/TrafficCop for auth/session. For in-process: future — call runtime_services directly; start with RuntimeClient-based implementation. |
| **Methods** | `query_state(...)`, `invoke_intent(...)`, `trigger_journey(...)`, `subscribe(...)` (or `get_execution_updates`) matching EXPERIENCE_SDK_CONTRACT. |
| **Acceptance** | [ ] Facade exists; [ ] Unit or integration tests: call facade, assert delegation to RuntimeClient (or Runtime) as expected |

#### Task A.2.2 — Wire Experience routes through the facade

| Item | Detail |
|------|--------|
| **Owner** | Takeoff |
| **Sessions** | create_session, get_session, upgrade_session use ExperienceSDK instead of raw RuntimeClient where applicable (e.g. create_session → sdk.invoke_intent or sdk.create_session per contract). |
| **Intents** | submit_intent uses sdk.invoke_intent (or sdk.submit_intent per contract). |
| **Other routes** | Guide agent and any route using RuntimeClient or direct StateSurface/PublicWorks: refactor to use SDK facade where they are “experience” operations (query state, invoke intent). Where lower-level access is required, document why and keep minimal; prefer SDK for “what experience surfaces need.” |
| **Acceptance** | [ ] Experience HTTP API behavior unchanged; [ ] All session/intent paths go through SDK facade; [ ] No new 404s or regressions |

---

### A.3 Phase 1 & 2 Completion Checklist

- [ ] **A.1.1** — EXPERIENCE_SDK_CONTRACT.md exists; optional protocol exists.
- [ ] **A.1.2** — RuntimeClient aligned with Runtime; session state works; stream/realms documented or implemented.
- [ ] **A.1.3** — Boot docs state Φ3 → SDK ready, Φ4 = attach experience.
- [ ] **A.2.1** — Experience SDK facade implemented and tested.
- [ ] **A.2.2** — All Experience routes wired through facade; no regressions.

**Note on MVP connectivity:** Phase 1–2 do not by themselves make the existing frontend work E2E. Execution status, artifact, and intent/pending live on Runtime only; Experience must proxy them for a single frontend URL. See [MVP_FRONTEND_BACKEND_CONNECTIVITY.md](MVP_FRONTEND_BACKEND_CONNECTIVITY.md). Include “Phase 2b: Experience proxy for execution/artifact/pending” when you want the frontend to work against one URL; that can be part of this handoff or a follow-on.

---

## Part B: Review Intent Contracts for Vision Alignment and Runtime Obligations

**Goal:** Ensure every intent contract in `docs/intent_contracts/` is aligned with the [solution_realm_refactoring_vision.md](../solution_realm_refactoring_vision.md), and that runtime obligations (what the platform must provide for each intent) are explicit and documented.

### B.1 Intent contract review process

#### Task B.1.1 — Audit intent contracts for vision alignment

| Item | Detail |
|------|--------|
| **Owner** | Takeoff |
| **Scope** | All folders under `docs/intent_contracts/` (control_tower_*, insights_*, journey_*, etc.). |
| **Actions** | For each intent contract: (1) Confirm **journey** and **realm** names map to vision (capabilities vs experience). (2) Confirm **capability** and **experience** mapping: e.g. journey_content_* → capabilities/content, experience/content; journey_security_* → capabilities/security, experience/security; journey_control_tower_* → capabilities/control_tower, experience/control_tower. (3) Flag any intents that assume “solution” or “realm” in the old sense and note the target capability/experience. |
| **Output** | A short **vision alignment summary** (e.g. `docs/intent_contracts/VISION_ALIGNMENT_SUMMARY.md`) listing: (a) mapping of current journey/realm folders to vision capabilities/experiences, (b) any gaps or renames needed (without changing code yet). |
| **Acceptance** | [ ] All intent contract folders reviewed; [ ] VISION_ALIGNMENT_SUMMARY.md exists and is linked from intent_contracts README or INTENT_CONTRACTS_PLAN.md |

#### Task B.1.2 — Document runtime obligations per intent (and per journey)

| Item | Detail |
|------|--------|
| **Owner** | Takeoff |
| **Purpose** | Each intent implementation (built by Team B or existing) plugs into the **runtime**. The runtime must provide clear contracts: registration, execution, state, artifacts. |
| **Actions** | For each intent contract (or at least each journey), document **runtime obligations**: |
| | • **Registration** — How the intent is registered (IntentRegistry; intent_type; parameters schema if any). |
| | • **Execution** — What the runtime provides at execution time (ExecutionContext: tenant_id, session_id, solution_id, user context, etc.; execution_id; lifecycle). |
| | • **State** — What state surface the intent can read/write (session state, execution state, keys, TTL if relevant). |
| | • **Artifacts** — What artifact surface the intent uses (ArtifactRegistry; register artifact, resolve, list; lifecycle_state; semantic_payload). |
| **Output** | Either (a) a **runtime obligations** section added to each intent contract, or (b) a single **runtime obligations index** (e.g. `docs/intent_contracts/RUNTIME_OBLIGATIONS_INDEX.md`) that references each intent/journey and lists registration, execution, state, artifact obligations in a table or structured list. |
| **Acceptance** | [ ] Every intent (or every journey) has documented runtime obligations; [ ] Index or in-doc sections exist and are linked from Part C (Runtime contracts doc) |

### B.2 Optional: Map intents to capabilities/experiences (table)

| Item | Detail |
|------|--------|
| **Owner** | Takeoff |
| **Output** | A table or matrix: Intent (or journey) → Capability → Experience (e.g. create_session → capabilities/security → experience/security). Can be part of VISION_ALIGNMENT_SUMMARY.md or a separate INTENT_CAPABILITY_EXPERIENCE_MAP.md. |
| **Acceptance** | [ ] Mapping exists so Team B knows where each intent “lives” in the target layout |

---

## Part C: Document Runtime Contracts (Registration, Execution, State, Artifacts)

**Goal:** One document that defines the **platform runtime contracts** that intent implementations plug into. Team B implements intents against these contracts; Takeoff owns the runtime that provides them.

### Task C.1 — Create Runtime Contracts document

| Item | Detail |
|------|--------|
| **Owner** | Takeoff |
| **Artifact** | `docs/architecture/RUNTIME_CONTRACTS.md` |
| **Content** | Describe the following as **contracts** (names, responsibilities, and what implementers can rely on): |

**1. Intent registration contract**

- **IntentRegistry** (or equivalent): how intents are registered (intent_type, handler, optional schema).
- How realms/solutions (or capabilities) register their intents at boot (e.g. IntentRegistry.register from each capability).
- Contract: “An intent implementation registers with IntentRegistry; it receives ExecutionContext and returns a result shape (artifacts, events).”

**2. Execution contract**

- **ExecutionContext**: what is passed to every intent handler (tenant_id, session_id, solution_id, user_id, request_id, execution_id, etc.).
- **Execution lifecycle**: created → running → completed/failed; execution_id; status endpoint.
- Contract: “The runtime creates an execution, invokes the handler with ExecutionContext, and updates lifecycle; handlers are stateless with respect to execution storage.”

**3. State contract**

- **State surface** (StateSurface / session state / execution state): what keys, namespaces, or abstractions are available (e.g. session-scoped state, execution-scoped state).
- Read/write guarantees (e.g. session state per session_id; execution state per execution_id).
- Contract: “Intent handlers read/write state only through the state surface; no direct DB or cache access for platform state.”

**4. Artifact contract**

- **ArtifactRegistry** (or equivalent): register artifact (artifact_id, type, lifecycle_state, produced_by, semantic_payload, parent_artifacts, materializations).
- Resolve, list, update lifecycle.
- Contract: “Intent handlers register artifacts via ArtifactRegistry; artifacts are the canonical output of intents; frontend/experience resolve artifacts via Experience SDK or Runtime API.”

**5. Optional: WAL, telemetry, policy**

- One sentence each: WAL for audit; telemetry for observability; policy for governance. Detail only if Team B needs to depend on them for intent implementation.

| **Acceptance** | [ ] RUNTIME_CONTRACTS.md exists; [ ] Registration, execution, state, artifact sections are clear and implementable; [ ] Linked from EXPERIENCE_SDK_CONTRACT or handoff package |
|----------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

---

## Part D: Publish as the Handoff

**Goal:** Package the deliverables so Team B has a single handoff and a clear remit.

### Task D.1 — Assemble handoff package

| # | Deliverable | Location | Owner |
|---|-------------|----------|--------|
| 1 | Experience SDK contract | `docs/architecture/EXPERIENCE_SDK_CONTRACT.md` | Takeoff |
| 2 | Runtime contracts | `docs/architecture/RUNTIME_CONTRACTS.md` | Takeoff |
| 3 | Reviewed intent contracts | `docs/intent_contracts/` (existing) + vision alignment + runtime obligations | Takeoff |
| 4 | Vision alignment summary | `docs/intent_contracts/VISION_ALIGNMENT_SUMMARY.md` (or equivalent) | Takeoff |
| 5 | Runtime obligations (per intent/journey) | In-doc sections or `docs/intent_contracts/RUNTIME_OBLIGATIONS_INDEX.md` | Takeoff |
| 6 | Boot phases (Φ3 / Φ4) | `INIT_ORDER_SPEC.md` or `BOOT_PHASES.md` | Takeoff |

### Task D.2 — Write handoff README for Team B

| Item | Detail |
|------|--------|
| **Artifact** | `docs/HANDOFF_TO_TEAM_B.md` (or `docs/architecture/HANDOFF_TO_TEAM_B.md`) |
| **Content** | • **What you’re getting:** Links to EXPERIENCE_SDK_CONTRACT, RUNTIME_CONTRACTS, intent contracts (with vision alignment and runtime obligations). • **Your remit:** “Implement the intent contracts and use the Experience SDK.” You build capabilities and experiences that consume the SDK; you do not change the civic system or Runtime contract. • **Our remit:** “We expose the runtime contracts that plug into that.” Takeoff owns runtime, boot, and Experience Civic System; we ensure the runtime contracts (registration, execution, state, artifacts) are stable and documented. • **Where to start:** LANDING_AGENT_TASKS.md Task 0 (canonical architecture) and Task 1 (Experience SDK contract adoption); then implement intents against RUNTIME_CONTRACTS and call the Experience SDK for all experience-layer operations. |
| **Acceptance** | [ ] HANDOFF_TO_TEAM_B.md exists; [ ] Team B can read it and know exactly what to implement and what to depend on |

### Task D.3 — Optional: Backend-only E2E before handoff

| Item | Detail |
|------|--------|
| **Purpose** | Prove the platform and internal contracts work before Team B starts: startup and backend critical path using existing intents/journeys. |
| **Actions** | (1) Start Runtime + Experience; (2) Create session (e.g. anonymous or auth); (3) Submit intent (e.g. compose_journey or content parse); (4) Get execution status; (5) Resolve artifact or result. All via direct calls to Runtime (8000) and Experience (8001), no frontend. |
| **Output** | Document the path (e.g. in PATH_TO_WORKING_PLATFORM or “MVP critical path (backend-only)”) and any fixes made. |
| **Acceptance** | [ ] Backend-only E2E path runs and is documented (optional but recommended) |

---

## Execution Order Summary

| Order | Part | Tasks | Dependency |
|-------|------|-------|------------|
| 1 | **A** | A.1.1 → A.1.2 → A.1.3 → A.2.1 → A.2.2 | None |
| 2 | **B** | B.1.1 (vision alignment) → B.1.2 (runtime obligations); optional B.2 (mapping table) | Can start after A.1.1 (contract exists); best after A complete |
| 3 | **C** | C.1 (RUNTIME_CONTRACTS.md) | After A.1.2 (runtime shapes known); can parallel B |
| 4 | **D** | D.1 (package) → D.2 (handoff README); optional D.3 (backend E2E) | After A, B, C complete |

---

## Success Criteria (Definition of Done)

- [ ] **Experience Civic Phase 1 & 2 locked:** SDK contract doc + facade + routes wired; RuntimeClient aligned; boot docs updated.
- [ ] **Intent contracts reviewed:** Vision alignment summary and runtime obligations (per intent or per journey) documented.
- [ ] **Runtime contracts documented:** RUNTIME_CONTRACTS.md describes registration, execution, state, artifacts.
- [ ] **Handoff published:** HANDOFF_TO_TEAM_B.md and links to all deliverables; Team B remit and Takeoff remit clearly stated.

When all checkboxes above are done, the handoff is complete and Team B can “implement the intent contracts and use the Experience SDK” while Takeoff “exposes the runtime contracts that plug into that.”
