# Runtime Contracts

**Purpose:** Define the platform runtime contracts that intent implementations plug into. Team B implements intents against these contracts; Takeoff owns the runtime that provides them.

**References:** [EXPERIENCE_SDK_CONTRACT.md](EXPERIENCE_SDK_CONTRACT.md), [solution_realm_refactoring_vision.md](../solution_realm_refactoring_vision.md), [TAKEOFF_PRE_TEAMB_HANDOFF_PLAN.md](TAKEOFF_PRE_TEAMB_HANDOFF_PLAN.md).

---

## 1. Intent registration contract

### IntentRegistry

- **Role:** Tracks which domain services (capabilities) support which intents. Runtime uses this registry to route intents to the correct handlers.
- **Registration:** Each intent handler registers with `IntentRegistry.register_intent(intent_type, handler_name, handler_function=None, metadata=None)`.
- **Contract:** An intent implementation registers with IntentRegistry at boot (via solution/realm registration). It receives **ExecutionContext** when invoked and returns a result shape (artifacts, events). Handlers are identified by `intent_type` (e.g. `ingest_file`, `compose_journey`) and `handler_name` (domain service name).
- **Boot:** Service factory (or solution initializer) registers intent services from each realm/capability with the IntentRegistry; each intent service is constructed with `public_works` and `state_surface`.

### Handler contract

- **Input:** Runtime creates an **ExecutionContext** (execution_id, intent, tenant_id, session_id, solution_id, state_surface, wal, metadata) and invokes the registered handler with it.
- **Output:** Handler returns a result that includes artifacts and/or events. Runtime records artifacts via State Surface / ArtifactRegistry and publishes events as configured.

---

## 2. Execution contract

### ExecutionContext

Passed to every intent handler. Implementers can rely on:

| Field | Type | Description |
|-------|------|-------------|
| `execution_id` | str | Unique execution identifier |
| `intent` | Intent | The intent (intent_type, tenant_id, session_id, solution_id, parameters, metadata) |
| `tenant_id` | str | Tenant identifier |
| `session_id` | str | Session identifier |
| `solution_id` | str | Solution/context identifier |
| `state_surface` | StateSurface | Read/write state (session, execution) |
| `wal` | WriteAheadLog | Audit trail (optional) |
| `metadata` | dict | Additional metadata |
| `created_at` | datetime | Creation time |

- **Validation:** Context is validated (execution_id, intent, tenant_id, session_id, solution_id present and consistent with intent) before handler invocation.
- **Contract:** Handlers are stateless with respect to execution storage; they do not create or persist execution records. Runtime creates the execution, invokes the handler, and updates lifecycle (created → running → completed/failed).

### Execution lifecycle

- **States:** created → running → completed | failed | cancelled.
- **Storage:** Execution state (execution_id, status, intent_id, artifacts, events, error) is stored and queryable via GET `/api/execution/{execution_id}/status` (Runtime) or Experience SDK query_state/subscribe.
- **Contract:** Runtime creates an execution, invokes the handler with ExecutionContext, and updates lifecycle; handlers do not directly update execution status.

---

## 3. State contract

### State surface

- **Role:** Single abstraction for session-scoped and execution-scoped state. Intent handlers read/write state only through the state surface; no direct DB or cache access for platform state.
- **Session state:** Keyed by tenant and session (e.g. `session:{tenant_id}:{session_id}`). Handlers use `state_surface.get_session_state(session_id, tenant_id)` and `state_surface.set_session_state(session_id, tenant_id, state)`.
- **Execution state:** Keyed by execution_id where applicable. Runtime and handlers use state surface for execution-scoped data as needed.
- **Contract:** Intent handlers must not bypass the state surface for platform state (session, execution). Backing stores (Redis, Arango, etc.) are not accessed directly by application code.

---

## 4. Artifact contract

### ArtifactRegistry (State Surface)

- **Role:** Authoritative artifact registration and resolution. Runtime (via State Surface / ArtifactRegistry) is the sole authority for resolving artifacts. Storage systems are not queried directly by application code.
- **Registration:** Handlers register artifacts via `state_surface.register_artifact(...)` (or ArtifactRegistry equivalent) with:
  - `artifact_id`, `artifact_type`, `tenant_id`
  - `produced_by`: intent name, execution_id
  - `lifecycle_state`: PENDING | READY | FAILED | ARCHIVED | DELETED
  - `semantic_descriptor`, `parent_artifacts`, `materializations`
- **Resolve / list:** Clients resolve artifacts via Experience SDK or Runtime API (e.g. POST `/api/artifact/resolve`, POST `/api/artifact/list`). Frontend/experience never talk to storage directly.
- **Contract:** Intent handlers register artifacts via the registry; artifacts are the canonical output of intents. Handlers do not write directly to GCS/Arango for platform artifact authority; they use the registry, which may delegate to storage abstractions.

---

## 5. Optional: WAL, telemetry, policy

- **WAL (Write-Ahead Log):** Audit trail for execution and critical state changes. Handlers may receive `wal` in ExecutionContext for appending domain events; runtime uses it for recovery and audit.
- **Telemetry:** Observability (metrics, tracing) is provided by the platform; handlers do not need to implement telemetry themselves.
- **Policy:** Governance and policy enforcement (e.g. Data Steward SDK, Traffic Cop) are applied at runtime; intent implementations comply with policy boundaries documented elsewhere.

---

## Summary

| Contract | What implementers rely on |
|----------|----------------------------|
| **Registration** | IntentRegistry.register_intent(intent_type, handler_name, handler_function?, metadata?); handlers invoked with ExecutionContext. |
| **Execution** | ExecutionContext (execution_id, intent, tenant_id, session_id, solution_id, state_surface, wal?, metadata); lifecycle owned by Runtime. |
| **State** | StateSurface for session and execution state; no direct DB/cache access. |
| **Artifacts** | ArtifactRegistry (via State Surface) for register, resolve, list; artifacts are canonical intent output. |

Intent implementations (Team B) depend only on these contracts. Takeoff ensures the runtime provides them and keeps them stable.
