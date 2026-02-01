# Intercept Validation (Team A)

**Status:** Validated (January 2026)  
**Purpose:** Record what was verified for the Runtime → Platform SDK intercept so we know "where we're meeting" before Curator/Civic/tenancy work.

**Related:** [INTERCEPT_ALIGNMENT_CONTRACT.md](../INTERCEPT_ALIGNMENT_CONTRACT.md), [PRACTICAL_REALITY_OVERLAY.md](../PRACTICAL_REALITY_OVERLAY.md).

---

## 1. Runtime → PlatformContextFactory → handler(ctx)

**Path:** Intent submit → Runtime API → ExecutionLifecycleManager.execute(intent) → resolve handler → if `uses_platform_context`: build ctx via PlatformContextFactory.create_context(intent, execution_id, metadata) → call handler.handler_function(platform_ctx).

**Verified:**

- **runtime_api.py:** `POST /api/intent/submit` → `runtime_api.submit_intent(request)` → `execution_lifecycle_manager.execute(intent)`.
- **execution_lifecycle_manager.py:** Handler metadata `uses_platform_context` from IntentRegistry (set in service_factory when registering PlatformIntentService). When True and `platform_context_factory` is set: `platform_ctx = self.platform_context_factory.create_context(intent, execution_id, metadata)`; then `handler_result = await handler.handler_function(platform_ctx)`.
- **service_factory.py:** PlatformContextFactory is created with `public_works`, `state_surface`, `wal`, `artifact_registry=state_surface.artifact_registry`. ELM is created with `platform_context_factory=platform_context_factory`.
- **context.py:** PlatformContextFactory.create_context builds PlatformContext with `state_surface`, `wal`, `artifacts=self.artifact_registry`, and the four services (governance, reasoning, platform, experience) built from public_works.

**Conclusion:** The wire is complete. ctx reaches PlatformIntentService handlers with state_surface, wal, artifacts, and the four SDK services.

---

## 2. Overlay API / WebSocket Endpoints

**Runtime API (create_runtime_app):**

| Overlay requirement | Route | Status |
|---------------------|--------|--------|
| Intent submit | `POST /api/intent/submit` | ✅ Registered |
| Session | `POST /api/session/create`, `GET /api/session/{session_id}`, `PATCH /api/session/{session_id}/upgrade` | ✅ Registered |
| Execution status | `GET /api/execution/{execution_id}/status` | ✅ Registered |

**WebSocket (Experience Plane):**

The overlay refers to "WebSocket /ws/chat and /ws/execution." Actual routes live in Experience, not in the Runtime app created by runtime_main:

| Logical name | Actual route | Owner |
|--------------|--------------|--------|
| Chat (guide agent) | `WebSocket /api/runtime/agent` | Experience (runtime_agent_websocket_router) |
| Execution streaming | `WebSocket /api/execution/{execution_id}/stream` | Experience (websocket_router) |

If the app started by runtime_main is Runtime-only, WebSocket endpoints are served by a separate Experience app or by composing Experience routers into the same app. For "wire validation" we only assert that Runtime intent submit and execution status exist; WebSocket gateway ownership is Experience.

---

## 3. Tenant Isolation (Baseline)

**StateSurface:** `get_execution_state(execution_id, tenant_id)` and `set_execution_state(execution_id, tenant_id, state)` use state_id `f"execution:{tenant_id}:{execution_id}"`. Tenant-scoped.

**ArtifactRegistry:** `_get_state_key(artifact_id, tenant_id)` returns `f"artifact:{tenant_id}:{artifact_id}"`. `register_artifact` and `resolve_artifact` take `tenant_id`. Tenant-scoped.

**Conclusion:** Baseline for "tenant isolation enforced in StateSurface and ArtifactRegistry" is in place. Policy enforcement (Supabase adapter, tenancy protocol, Security Guard) is separate work.

---

## 4. Checklist (Team A Practical Reality)

From PRACTICAL_REALITY_OVERLAY Part 2:

- [x] `/api/intent/submit` routes to Team B's capability services (via ELM → handler(ctx))
- [x] `/api/session/*` endpoints exist (create, get, upgrade)
- [x] `/api/execution/{id}/status` returns real status
- [x] WebSocket: Traefik routes `/api/execution` to Experience (status proxy + stream); `/api/runtime/agent` to Experience (see WEBSOCKET_TRAEFIK_DEPLOYMENT.md)
- [x] Tenant isolation baseline: StateSurface and ArtifactRegistry are tenant-scoped

---

**Last updated:** January 2026
