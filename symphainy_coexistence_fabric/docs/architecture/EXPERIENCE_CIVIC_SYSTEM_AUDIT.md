# Experience Civic System Audit: Today vs Vision

**Purpose:** Capture what the Experience Civic System provides today and what it must provide for the [solution_realm_refactoring_vision](../solution_realm_refactoring_vision.md) to work. Informs the refactor plan so takeoff (startup) can refactor the civic system first; then landing agents build capabilities/experiences against the resulting SDK.

**Ownership (per alignment):** Takeoff owns runtime + **all civic systems**, including whether platform_sdk and orchestrator_health are relevant and what they need to be. Landing owns capabilities and experiences. The Experience Civic System refactor is takeoff work; it proves the handshake (Experience SDK) before landing builds on it.

---

## 1. What the Vision Says the Experience Civic System Must Provide

From the vision and [LANDING_AGENT_TASKS.md](../LANDING_AGENT_TASKS.md):

- **Experience Civic System** = capability provider, runtime surface, platform service. It **exposes an SDK**. It is **not** the experience itself.
- **Experiences** (product surfaces) **attach to runtime** via that SDK. They:
  - **Query state** — read state for tenant/session/context
  - **Invoke intents** — submit intents
  - **Trigger journeys** — start journeys (e.g. compose_journey)
  - **Subscribe to signals** — receive runtime events/updates
- The Experience Civic System **registers** (in the platform); individual experience UIs do **not** register in service_factory. Experience surfaces are **clients** of the runtime, not part of it.
- **North star for startup:** "Startup succeeds when the Experience SDK is ready for clients." Φ3 builds runtime graph; the SDK is the typed surface over that graph; Φ4 attaches experience surfaces to it.

So the **Experience SDK** is the single, named contract that:
1. Takeoff implements (civic system + runtime surface).
2. Landing’s experience surfaces consume (capabilities/experience UIs).

---

## 2. What the Experience Civic System Provides Today

### 2.1 Entry and Boot

- **`experience_main.py`** (fabric root): Gate G2 (load config) → Gate G3 (pre_boot_validate) → **build full runtime graph** via `create_runtime_services(config)` → create Experience FastAPI app via `create_app()` → attach `security_guard_sdk` and `traffic_cop_sdk` (built from Public Works) → run uvicorn on EXPERIENCE_PORT (8001).
- Experience service **does not** register in service_factory. It is a **separate process** that builds the runtime graph only to obtain Public Works (auth, tenant, state abstractions) for SecurityGuard and TrafficCop. It then exposes its own HTTP API and uses **RuntimeClient** to call the **Runtime** service (another process) for session, intent, execution.

So today: **two processes** — Runtime (runtime_api on 8000) and Experience (create_app on 8001). Experience talks to Runtime over HTTP via `RuntimeClient(runtime_url="http://runtime:8000")`.

### 2.2 Experience FastAPI App (`civic_systems/experience/`)

**`create_app()`** (experience_service.py) creates a FastAPI app with:

| Area | What it provides |
|------|-------------------|
| **Middleware** | AuthenticationMiddleware, CORS |
| **Routers** | auth_router, sessions_router, intents_router, websocket_router, guide_agent_router, runtime_agent_websocket_router, metrics_router, control_room_router, developer_view_router, business_user_view_router |
| **State** | `app.state.security_guard_sdk`, `app.state.traffic_cop_sdk` (injected by experience_main) |
| **Health** | GET /health |

So the **surface** experience clients (e.g. frontend) use today is the **Experience service HTTP API** (auth, session, intent, guide, websocket, admin). That API in turn uses:
- **SecurityGuardSDK** / **TrafficCopSDK** for auth and session validation (from Public Works, in-process).
- **RuntimeClient** for session create/get/upgrade, intent submit, execution stream, realms (out-of-process HTTP to Runtime).

### 2.3 RuntimeClient (Experience → Runtime)

`sdk/runtime_client.py` — HTTP client to Runtime. Methods:

| Method | Runtime endpoint assumed | Notes |
|--------|---------------------------|--------|
| `get_session(session_id, tenant_id)` | GET /api/session/{session_id} | ✅ Runtime has this |
| `get_session_state(session_id, tenant_id)` | GET /api/session/{session_id}/state | ⚠️ Runtime has GET /api/session/{session_id} (returns state); no separate /state route |
| `create_session(session_intent)` | POST /api/session/create | ✅ Runtime has this |
| `upgrade_session(...)` | PATCH /api/session/{session_id}/upgrade | ✅ Runtime has this |
| `submit_intent(intent)` | POST /api/intent/submit | ✅ Runtime has this |
| `stream_execution(execution_id)` | GET /api/execution/{execution_id}/stream | ⚠️ Runtime has GET /api/execution/{id}/status only; no /stream in runtime_api |
| `get_realms()` | GET /api/realms | ⚠️ No GET /api/realms in runtime_api (likely 404) |

So there are **API shape mismatches**: RuntimeClient expects endpoints that Runtime does not expose (or uses a different path). Either Runtime must add these or Experience must use existing routes (e.g. get_session for state; status polling instead of stream if no stream).

### 2.4 Auth, Session, Intent Routes (Experience API)

- **Auth** (api/auth.py): login, register, etc.; uses SecurityGuardSDK, TrafficCopSDK, RuntimeClient.
- **Sessions** (api/sessions.py): create, get, upgrade; uses RuntimeClient + SecurityGuard + TrafficCop.
- **Intents** (api/intents.py): submit intent; validates session via TrafficCop, submits via RuntimeClient.
- **Guide agent** (api/guide_agent.py): chat, intent analysis, journey guidance; uses ExecutionContext, StateSurface, PublicWorksFoundationService (heavy in-process coupling to runtime concepts).
- **WebSocket / runtime_agent_websocket**: real-time and agent flows.

These together form the **current** “SDK” in practice: the set of HTTP (and WebSocket) operations the frontend calls. There is no single **named** “Experience SDK” type or document; the contract is implicit in the routes and request/response shapes.

### 2.5 Admin Dashboard

- **control_room**, **developer_view**, **business_user_view**: use **platform_sdk** (SolutionRegistry, SolutionBuilder) to list solutions, get config, etc. So the Experience civic system **depends on platform_sdk** for admin/control-tower-style features.

### 2.6 Orchestrator Health

- **orchestrator_health** (OrchestratorHealthMonitor): used by **runtime/metrics_api.py**, not by the Experience app directly. Metrics API is **mounted on the Experience app** (experience_service.py includes metrics_router). So Experience exposes orchestrator health metrics as part of its API surface; the monitor lives in civic_systems/orchestrator_health and is used by the runtime/metrics layer when reporting health. Relevance for the vision: if “control tower” is a capability and its MVP exposure is the admin dashboard, then orchestrator health may remain as part of observability/governance that the Experience layer exposes (or that Runtime exposes and Experience proxies). Takeoff owns the decision.

### 2.7 Platform SDK

- **platform_sdk**: solution_registry, solution_builder, solution_model, guide_registry, realm_sdk (largely unused in fabric per bases/README). Used by: service_factory (SolutionRegistry), solution_initializer, developer_view_service, business_user_view_service, control_room_service, outcomes_solution, content_solution, insights_solution, create_solution_service, seed_default_guides. So platform_sdk is central to **solution discovery and admin views**. For the vision, “solutions” become packaging and “capabilities” are what the platform can do; the Experience Civic System may still need a way to list “what’s available” (solutions/capabilities) for admin and for experience composition. Takeoff owns whether platform_sdk stays, is renamed, or is replaced by a capability registry that the SDK exposes.

---

## 3. Gap Analysis: Today vs Vision

| Vision requirement | Today | Gap |
|--------------------|--------|-----|
| **Single named “Experience SDK” contract** | No named SDK; contract is implicit in Experience HTTP API + RuntimeClient. | Define and document the Experience SDK (operations + payloads). Implement it explicitly (e.g. a facade used by Experience routes and by future in-process clients). |
| **Query state** | get_session, get_session_state (RuntimeClient); get_execution_status not exposed as “query state” from Experience. | Align “query state” with existing session + execution status (+ artifacts). Fix RuntimeClient vs Runtime API mismatches (session state, stream, realms). |
| **Invoke intents** | submit_intent (Experience API → RuntimeClient → Runtime). | Already present; ensure it’s the single path and document as SDK operation. |
| **Trigger journeys** | Same as invoke intent (compose_journey intent). | Document as SDK operation; no new backend needed if compose_journey is the mechanism. |
| **Subscribe to signals** | WebSocket + stream_execution (RuntimeClient); Runtime may not have /stream. | Either add execution stream (or equivalent) on Runtime or standardize on WebSocket/SSE from Experience; document as SDK “subscribe” contract. |
| **Experience surfaces as clients only** | Experience service is a client of Runtime (HTTP). Frontend is client of Experience (HTTP). No experience surfaces registered in service_factory. | Align with vision: document that experience surfaces only attach via SDK; no registration in service_factory. Ensure boot/docs say Φ4 = attach experience to SDK. |
| **Experience Civic System “registers”** | Experience does not register in service_factory today; it’s a separate process. | Decide: does “register” mean “is part of the platform and appears in a registry of civic systems” (e.g. for admin) or “is created after Φ3 and exposes the SDK”? Latter is already true; former may be a small doc/registry addition. |
| **RuntimeClient ↔ Runtime API consistency** | RuntimeClient calls /state, /stream, /realms; Runtime does not expose all. | Either add missing routes to Runtime or change RuntimeClient to use existing routes (e.g. get_session for state; document stream/realms as future or remove from SDK until implemented). |
| **platform_sdk** | Used for solution registry, admin views, solutions. | Takeoff decides: keep and refactor for “capability/solution” model, or replace with capability registry; document decision and any new API the SDK exposes (e.g. list_capabilities / list_solutions). |
| **orchestrator_health** | Used by metrics API (mounted on Experience). | Takeoff decides: keep as-is for control-tower observability, or move under a dedicated control_tower capability; document. |

---

## 4. Summary: What Must Change for the Vision to Work

1. **Define and document the Experience SDK** as the single contract (query state, invoke intent, trigger journey, subscribe). Implement it as a clear facade (e.g. `ExperienceSDK` class or module) used by Experience routes and, where useful, by in-process callers.
2. **Align RuntimeClient with Runtime API** (or extend Runtime): fix session state, execution stream, and realms so that the SDK’s behavior is implementable and testable.
3. **Boot/docs:** State that Φ3 completes → Experience SDK is available; Φ4 = attach experience surfaces to the SDK. Optionally add a Φ4 stub in code (e.g. `attach_experience_surfaces()` after runtime graph ready).
4. **platform_sdk and orchestrator_health:** Takeoff decides their future role and whether they are part of the “Experience SDK” surface (e.g. list solutions/capabilities, health) or internal only; document and refactor accordingly.
5. **Guide agent and other experience routes:** Ensure they use the Experience SDK (or the same contract) rather than ad-hoc coupling to StateSurface/PublicWorks so that the civic system has one consistent surface for “what experience can do.”

This audit feeds the refactor plan (next doc).
