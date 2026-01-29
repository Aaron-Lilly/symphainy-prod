# Experience Civic System Refactor Plan

**Purpose:** Phased plan to refactor the Experience Civic System so it provides the **Experience SDK** as the single, named contract for the [solution_realm_refactoring_vision](../solution_realm_refactoring_vision.md). Takeoff (startup) owns this refactor; when it is done, landing agents build capabilities/experiences against the SDK.

**Prerequisite:** [EXPERIENCE_CIVIC_SYSTEM_AUDIT.md](EXPERIENCE_CIVIC_SYSTEM_AUDIT.md) — current state and gaps.

---

## Principles

1. **SDK-first:** The Experience SDK is the single surface experience surfaces use. All Experience API routes and future in-process callers go through the same contract.
2. **Fix before expand:** Align RuntimeClient with Runtime API (or extend Runtime) so existing flows work before adding new SDK operations.
3. **Document then code:** Lock the contract (operations + payloads) in docs and types before changing behavior.
4. **Takeoff owns:** platform_sdk and orchestrator_health decisions; refactor is done in the civic + runtime codebase without landing agents changing this layer.

---

## Phase 1: Contract and Alignment (No Breaking Changes)

**Goal:** Define the Experience SDK contract and fix RuntimeClient ↔ Runtime API mismatches so the current Experience service works against the real Runtime.

### 1.1 Define Experience SDK contract (doc + type)

- **Owner:** Takeoff.
- **Artifacts:**
  - `docs/architecture/EXPERIENCE_SDK_CONTRACT.md`: list of operations with names, intent, and minimal request/response shapes:
    - **query_state** — session + execution status + artifacts (tenant_id, session_id, optional execution_id).
    - **invoke_intent** — submit intent (intent_type, parameters, tenant_id, session_id, solution_id).
    - **trigger_journey** — same as invoke_intent with compose_journey (or document as alias).
    - **subscribe** — execution updates (execution_id) via stream or WebSocket; document current behavior (e.g. Experience WebSocket or polling) and target behavior.
  - Optional: Python protocol or ABC in `symphainy_platform/civic_systems/experience/sdk/` (e.g. `experience_sdk.py`) with methods matching the doc. No behavior change yet; types only.
- **Acceptance:** Doc exists; optional protocol exists; existing Experience API and Runtime unchanged.

### 1.2 Align RuntimeClient with Runtime API

- **Owner:** Takeoff.
- **Tasks:**
  - **Session state:** Runtime exposes GET /api/session/{session_id} (returns session state). RuntimeClient today calls GET /api/session/{session_id}/state. Either (A) add GET /api/session/{session_id}/state on Runtime that returns same payload, or (B) change RuntimeClient.get_session_state to use GET /api/session/{session_id} and map response to “state” shape. Prefer (B) to avoid duplicate routes.
  - **Execution stream:** Runtime has GET /api/execution/{id}/status only. Either (A) add GET /api/execution/{id}/stream (SSE or chunked JSON) on Runtime, or (B) document “subscribe” as polling status for now and change RuntimeClient.stream_execution to poll or remove until Runtime supports stream. Document in EXPERIENCE_SDK_CONTRACT.
  - **Realms:** RuntimeClient.get_realms() calls GET /api/realms. If Runtime does not expose this, either (A) add GET /api/realms on Runtime (from realm_registry or equivalent), or (B) remove get_realms from RuntimeClient and from any Experience route that uses it until Runtime supports it; document in contract.
- **Acceptance:** RuntimeClient works against current Runtime (or minimal Runtime changes); no 404s for session state; stream/realms either implemented or documented as deferred.

### 1.3 Boot docs: Φ3 → SDK ready, Φ4 = attach experience

- **Owner:** Takeoff.
- **Tasks:**
  - In `docs/architecture/INIT_ORDER_SPEC.md` or new `BOOT_PHASES.md`: state that after Φ3 (runtime graph built), the **Experience SDK surface is available** (Runtime API and/or Experience service exposes it). Φ4 = attach experience surfaces to that SDK (no-op stub acceptable).
  - Optionally in code: after `create_runtime_services()` in experience_main (or runtime_main), add a single comment or no-op step “Φ4 — attach experience surfaces (see EXPERIENCE_SDK_CONTRACT).”
- **Acceptance:** Docs state north star (“Startup succeeds when Experience SDK is ready”); Φ4 is named; optional code stub.

---

## Phase 2: Experience SDK Facade and Route Wiring

**Goal:** Introduce an explicit Experience SDK implementation used by all Experience API routes. No new behavior; same behavior through one facade.

### 2.1 Implement Experience SDK facade

- **Owner:** Takeoff.
- **Tasks:**
  - Add `symphainy_platform/civic_systems/experience/sdk/experience_sdk.py` (or equivalent) that implements the contract from Phase 1. For **out-of-process** deployment, the implementation can delegate to RuntimeClient (HTTP to Runtime) and to SecurityGuard/TrafficCop for auth/session validation. For **in-process** deployment, it could call runtime_services directly (future). Start with RuntimeClient-based implementation.
  - Facade methods: e.g. `query_state(...)`, `invoke_intent(...)`, `trigger_journey(...)`, `subscribe(...)` (or `get_execution_updates`) matching EXPERIENCE_SDK_CONTRACT.
- **Acceptance:** Facade exists; unit tests or integration tests that call facade and assert it delegates to RuntimeClient (or Runtime) as expected.

### 2.2 Wire Experience routes through the facade

- **Owner:** Takeoff.
- **Tasks:**
  - Sessions: create_session, get_session, upgrade_session use `ExperienceSDK` (or equivalent) instead of raw RuntimeClient where it makes sense (e.g. create_session → sdk.invoke_intent or sdk.create_session if that’s the contract).
  - Intents: submit_intent uses sdk.invoke_intent (or sdk.submit_intent if that’s the name in the contract).
  - Guide agent and other routes that today use RuntimeClient or direct StateSurface/PublicWorks: refactor to use the SDK facade where they are “experience” operations (query state, invoke intent). Where they need lower-level access (e.g. guide logic), document why and keep minimal; prefer going through SDK for anything that is “what experience surfaces need.”
- **Acceptance:** Experience HTTP API behavior unchanged; all session/intent paths go through the SDK facade; no new 404s or regressions.

---

## Phase 3: platform_sdk and orchestrator_health Decisions

**Goal:** Decide whether platform_sdk and orchestrator_health are part of the future architecture and what they must provide. Document and, if needed, refactor.

### 3.1 platform_sdk

- **Owner:** Takeoff.
- **Tasks:**
  - Decide: (A) Keep platform_sdk for solution/capability discovery and admin; refactor names (e.g. SolutionRegistry → CapabilityRegistry or keep name and document as “solution registry = packaging + capability discovery”). (B) Deprecate and replace with a smaller “capability/solution list” API that the Experience SDK exposes (e.g. sdk.list_available_capabilities() or sdk.get_solution_config()). (C) Keep as internal only; Experience SDK does not expose it; admin dashboard uses internal APIs.
  - Document decision in `docs/architecture/PLATFORM_SDK_DECISION.md` (or section in CANONICAL_PLATFORM_ARCHITECTURE).
  - If (A) or (B): ensure Experience SDK contract (or admin-only extension) includes “list solutions/capabilities” and “get solution/capability config” if experience surfaces need them; implement via platform_sdk or new module.
- **Acceptance:** Decision documented; Experience admin routes (control_room, developer_view, business_user_view) still work; any new SDK operations for “list capabilities” are in the contract.

### 3.2 orchestrator_health

- **Owner:** Takeoff.
- **Tasks:**
  - Decide: (A) Keep OrchestratorHealthMonitor as part of control-tower/observability; metrics API (mounted on Experience or Runtime) continues to expose it. (B) Move under a dedicated “control_tower” capability and expose via a dedicated control-tower API. (C) Keep as-is; document as “observability for runtime orchestrators”; no change to Experience SDK contract.
  - Document in `docs/architecture/ORCHESTRATOR_HEALTH_DECISION.md` (or same place as platform_sdk).
- **Acceptance:** Decision documented; current metrics/health behavior preserved or intentionally simplified.

---

## Phase 4: Optional In-Process and Φ4 Stub

**Goal:** Support single-process deployment (Experience and Runtime in one process) if desired, and make Φ4 “attach experience surfaces” explicit in code.

### 4.1 Optional in-process SDK implementation

- **Owner:** Takeoff.
- **Tasks:**
  - If desired: add an alternate Experience SDK implementation that takes `RuntimeServices` (or runtime_api) and calls state_surface, execution_lifecycle_manager, intent_registry in-process instead of HTTP. experience_main can choose “in-process” vs “out-of-process” by config (e.g. USE_INPROCESS_RUNTIME=true).
  - Document in EXPERIENCE_SDK_CONTRACT: “Default: HTTP to Runtime. Optional: in-process when running in same process.”
- **Acceptance:** No regression for current (out-of-process) deployment; in-process path works when enabled and passes same contract tests.

### 4.2 Φ4 stub in boot

- **Owner:** Takeoff.
- **Tasks:**
  - In experience_main (and optionally runtime_main), after “runtime graph ready” / “Experience app created,” call a documented step: `attach_experience_surfaces(sdk, config)` (no-op or log only). Document that real implementations will register or bind experience UIs to the SDK here.
- **Acceptance:** Φ4 step exists in code and in BOOT_PHASES.md; startup and tests pass.

---

## Execution Order and Handoff to Landing

1. **Phase 1** — Do first. No breaking changes; contract + alignment. Unblocks clear spec for landing.
2. **Phase 2** — Next. Single facade and route wiring. Experience service behavior unchanged; contract is the single path.
3. **Phase 3** — In parallel or after Phase 2. Decisions and docs; refactor platform_sdk/orchestrator_health only if needed.
4. **Phase 4** — Optional; can follow after Phase 2–3.

**MVP connectivity (frontend ↔ backend):** Phase 1–2 do **not** by themselves make the existing frontend work end-to-end. The frontend uses one base URL and expects execution status, artifact, and intent/pending; today those live only on Runtime. So Experience must **proxy** those routes (or the frontend will 404 when pointing at Experience). See [MVP_FRONTEND_BACKEND_CONNECTIVITY.md](MVP_FRONTEND_BACKEND_CONNECTIVITY.md) for the full checklist. Include “Phase 2b: Experience proxy for execution/artifact/pending” (or add proxy routes in Phase 2) so that when the frontend points at Experience, all calls work; then one critical path E2E (session → intent → execution status → result) and env/CORS/deployment complete the MVP “on the other side.”

**Detailed implementation plan (pre–Team B):** For concrete tasks to lock Phase 1 & 2, review intent contracts, document runtime contracts, and publish the handoff, see [TAKEOFF_PRE_TEAMB_HANDOFF_PLAN.md](TAKEOFF_PRE_TEAMB_HANDOFF_PLAN.md).

**Handoff:** When Phase 1 and Phase 2 (and proxy/MVP connectivity) are done (and Phase 3 decided), the Experience SDK is the **inflection point**. Landing agents then:
- Read `EXPERIENCE_SDK_CONTRACT.md` and the canonical architecture.
- Build capabilities and experiences that consume the SDK (HTTP to Experience service, or in-process SDK when available).
- Do **not** change the civic system or Runtime contract; they only add capabilities/, experience/, and solutions packaging per LANDING_AGENT_TASKS.

**Proof that two worlds meet:** The holistic refactor of the agentic civic system (this plan) delivers the SDK; landing’s experience surfaces and capabilities use it. Integration tests: Experience service up → SDK operations (query state, invoke intent, trigger journey, subscribe) succeed → landing-built clients (or stub clients) pass the same contract.
