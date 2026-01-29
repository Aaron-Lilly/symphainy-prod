# Experience SDK Contract

**Purpose:** Single, named contract for experience surfaces. All Experience API routes and future in-process callers use this surface. Takeoff owns the implementation; Team B (Landing) builds experience surfaces that consume it.

**References:** [EXPERIENCE_CIVIC_REFACTOR_PLAN.md](EXPERIENCE_CIVIC_REFACTOR_PLAN.md), [solution_realm_refactoring_vision.md](../solution_realm_refactoring_vision.md).

---

## 1. Operations Overview

| Operation | Intent | Default transport |
|-----------|--------|-------------------|
| **query_state** | Session + execution status + artifacts for a tenant/session/context | HTTP (Experience or Runtime) |
| **invoke_intent** | Submit an intent (intent_type, parameters, context) | HTTP POST to Runtime |
| **trigger_journey** | Start a journey (alias for invoke_intent with compose_journey or equivalent) | Same as invoke_intent |
| **subscribe** | Execution updates for an execution_id | Polling status (current); target: WebSocket or SSE when Runtime supports stream |

---

## 2. query_state

**Intent:** Return session state, optional execution status, and optional artifact references for a given tenant/session (and optionally execution_id).

### Request (minimal)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `tenant_id` | string | No* | Tenant identifier (*required for authenticated sessions) |
| `session_id` | string | Yes | Session identifier |
| `execution_id` | string | No | If provided, include execution status for this execution |

### Response (minimal)

- **Session:** Same shape as Runtime GET `/api/session/{session_id}` (session state dict: session_id, tenant_id, user_id, solution_id, metadata, etc.).
- **Execution (if execution_id provided):** Same shape as Runtime GET `/api/execution/{execution_id}/status` (status, lifecycle_state, artifacts, etc.).
- **Artifacts:** Optional list or resolve-by-id; can be derived from execution status when `include_artifacts=true`.

### Current behavior

- Experience service uses RuntimeClient to call Runtime GET `/api/session/{session_id}` for session state (no separate `/state` path; session and state are the same).
- Execution status: GET `/api/execution/{execution_id}/status` (tenant_id required as query param).

---

## 3. invoke_intent

**Intent:** Submit an intent for execution. Runtime creates an execution, enqueues the intent, and returns execution_id.

### Request (minimal)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `intent_type` | string | Yes | Intent type (e.g. create_session, compose_journey, parse_content) |
| `parameters` | object | No | Intent parameters |
| `tenant_id` | string | Yes | Tenant identifier |
| `session_id` | string | Yes | Session identifier |
| `solution_id` | string | No | Solution/context (default: "default") |
| `metadata` | object | No | Optional metadata |

### Response (minimal)

| Field | Type | Description |
|-------|------|-------------|
| `execution_id` | string | Execution identifier |
| `status` | string | e.g. "accepted", "running" |
| `created_at` | string | ISO timestamp |

### Current behavior

- Experience POST `/api/intent/submit` → RuntimeClient.submit_intent(intent) → Runtime POST `/api/intent/submit`.

---

## 4. trigger_journey

**Intent:** Start a journey. Documented as alias for **invoke_intent** with an intent that composes or triggers a journey (e.g. `compose_journey` with journey_id and params). Same request/response shape as invoke_intent.

### Current behavior

- Use invoke_intent with intent_type such as `compose_journey` and parameters containing journey_id and journey parameters.

---

## 5. subscribe (execution updates)

**Intent:** Deliver execution updates for an execution_id (e.g. status changes, completion, artifacts).

### Current behavior

- **Stream:** Runtime does **not** yet expose GET `/api/execution/{execution_id}/stream`. Experience WebSocket route uses RuntimeClient.stream_execution(), which calls that path; if Runtime returns 404, streaming is unavailable.
- **Polling:** Clients can poll GET `/api/execution/{execution_id}/status` (via Experience proxy when available, or Runtime). The SDK contract documents **subscribe** as “polling status” until Runtime supports a stream endpoint.
- **Target:** When Runtime adds GET `/api/execution/{id}/stream` (SSE or chunked JSON), Experience SDK will use it for subscribe; until then, subscribe is implemented as polling (e.g. SDK or client polls status at an interval until terminal state).

### Contract

- **subscribe(execution_id, tenant_id, ...)** may be implemented as:
  - (A) HTTP stream to Runtime `/api/execution/{id}/stream` when available, or
  - (B) Polling GET `/api/execution/{id}/status` until lifecycle is terminal, yielding status events.
- Experience WebSocket that today calls RuntimeClient.stream_execution: if Runtime returns 404, client receives error or fallback to polling; document this in API docs.

---

## 6. Session and Realms (deferred / optional)

- **Session create/upgrade:** Create session and upgrade session are part of the Experience API and delegate to Runtime (POST `/api/session/create`, PATCH `/api/session/{id}/upgrade`). They can be considered part of the SDK surface (e.g. **create_session**, **upgrade_session**) or as convenience endpoints that sit on top of invoke_intent + query_state; current implementation uses direct Runtime calls.
- **Realms:** Runtime does **not** currently expose GET `/api/realms`. RuntimeClient.get_realms() may 404. When used (e.g. control room), Experience can fall back to local realm registry or return empty list; **list_realms** (or equivalent) is documented as deferred until Runtime exposes a realms endpoint.

---

## 7. Summary Table

| SDK operation | HTTP / behavior | Notes |
|---------------|-----------------|--------|
| query_state(session_id, tenant_id?, execution_id?) | GET session; GET execution/status if execution_id | Session state = GET /api/session/{id} |
| invoke_intent(...) | POST /api/intent/submit | |
| trigger_journey(...) | Alias invoke_intent | |
| subscribe(execution_id, ...) | Poll GET /api/execution/{id}/status until terminal | Stream deferred until Runtime has /stream |
| create_session / upgrade_session | POST/PATCH session on Runtime | Part of SDK or convenience layer |
| list_realms (optional) | Deferred; fallback to empty or local registry | Runtime /api/realms not yet exposed |

---

**Last updated:** Per TAKEOFF_PRE_TEAMB_HANDOFF_PLAN.md (Phase 1). Implementation: Experience SDK facade in `symphainy_platform/civic_systems/experience/sdk/experience_sdk.py`; routes wired in Phase 2.
