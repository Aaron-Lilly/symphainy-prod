# Platform Operation Map

**Purpose:** Single source of truth for **how the platform actually operates**. Filled **only** by running probes. When complete, this document states with **100% certainty** the entry point, boot order, first request path, config contracts, and order/restart failure modes.

**Do not fill by guesswork.** Only by probe output.

**Phase 0 runtime evidence:** See [PHASE0_WHAT_WE_ACTUALLY_BUILT.md](PHASE0_WHAT_WE_ACTUALLY_BUILT.md). In one run, boot reached ELM then failed (registry_abstraction is None); first request was **not** observed (server never started). §1–§2 confirmed by log; §3 is code trace only until boot completes to uvicorn.

---

## §1. Entry point

**Exact file, function, line. What runs first.**

| Field | Value (filled by probe_01) |
|-------|----------------------------|
| Process entry | `python runtime_main.py` (or `main.py` → `runtime_main.main()`) |
| Code entry | `runtime_main.py`, `main()`, line 46 (`if __name__ == "__main__": main()`) |
| First executable statement | `get_env_contract()` at line 56 (load configuration) |
| Evidence | File: `runtime_main.py` |

*Status: [x] Filled by probe_01*

---

## §2. Boot order

**A → B → C → … with evidence (code path and/or runtime trace).**

| Step | Component | Evidence |
|------|-----------|----------|
| 1 | get_env_contract() | runtime_main.py:56 |
| 2 | create_runtime_services(config) | runtime_main.py:60 |
| 2.1 | PublicWorksFoundationService(config) | service_factory.py:62 |
| 2.2 | public_works.initialize() | service_factory.py:66 |
| 2.3 | StateSurface(...) | service_factory.py:74 |
| 2.4 | WriteAheadLog(...) | service_factory.py:82 |
| 2.5 | IntentRegistry() | service_factory.py:89 |
| 2.6 | Register Content Realm intents | service_factory.py:114-145 |
| 2.7 | Register Insights Realm intents | service_factory.py:149-175 |
| 2.8 | Register Operations Realm intents | service_factory.py:177-203 |
| 2.9 | Register Outcomes Realm intents | service_factory.py:205-231 |
| 2.10 | Register Security Realm intents | service_factory.py:233-259 |
| 2.11 | Register Control Tower Realm intents | service_factory.py:261-292 |
| 2.12 | Register Coexistence Realm intents | service_factory.py:294-322 |
| 2.13 | initialize_solutions(...) | service_factory.py:329-339 |
| 2.14 | ExecutionLifecycleManager(...) | service_factory.py:344-352 |
| 2.15 | RuntimeServices(...) | service_factory.py:360-371 |
| 3 | create_fastapi_app(services) | runtime_main.py:63 |
| 3.1 | create_runtime_app(...) | service_factory.py:401-407 |
| 4 | uvicorn.run(app, host, port) | runtime_main.py:72-77 |

*Status: [x] Filled by probe_01*

---

## §3. First request path

**What code runs when the first browser request hits (e.g. GET /health or GET /docs).**

| Request | Handler / code path | Evidence |
|---------|---------------------|----------|
| GET /health | runtime_api.py:1126-1129 — `create_runtime_app()` registers `@app.get("/health")`; `async def health()` returns `{"status": "healthy", "service": "runtime", "version": "2.0.0"}` | symphainy_platform/runtime/runtime_api.py:1126-1129 |

*Status: [x] Filled by probe_01 (code trace). Not yet runtime-confirmed in Phase 0 run—server did not reach uvicorn (see PHASE0_WHAT_WE_ACTUALLY_BUILT.md).*

---

## §4. Config contracts

**Which env vars, ports, or names change behavior or stability. What breaks when missing or wrong.**

Filled by probe_02. See probe output for full table. Summary:

- **Required for boot:** Config load (get_env_contract) — invalid LOG_LEVEL or port range → Pydantic ValidationError, process exits before any service creation.
- **Required for runtime:** REDIS_URL, ARANGO_URL (wrong URL → PublicWorks.initialize() or first use fails). RUNTIME_PORT (wrong → uvicorn binds elsewhere; client must use same port).
- **Optional:** SUPABASE_*, GCS_*, MEILI_* — feature disabled if missing.
- **Implicit:** All ports validated 1–65535 at load. REDIS_URL / ARANGO_URL not validated for reachability at load; failure appears at PublicWorks.initialize() or first use.

*Status: [x] Filled by probe_02*

---

## §5. Order / restart failure modes

**What breaks when startup order changes. What “fixes” on restart (and what that implies).**

| Trigger | Observed behavior | Hypothesis (do not resolve) |
|---------|-------------------|-----------------------------|
| *(To be filled by probe_03 — run procedure in probes/probe_03_order_restart.md)* | | |

*Status: [ ] Filled by probe_03 + Stability/Gravity reports*

---

## Implicit assumptions (from probe_01)

- Config is loaded synchronously at start; no hot reload of env.
- All services are created in one async run (create_runtime_services); no lazy init of core graph.
- Intent handlers are registered in fixed order: Content → Insights → Operations → Outcomes → Security → Control Tower → Coexistence.
- Solutions are initialized with initialize_mcp_servers=True (MCP servers started during boot).
- First HTTP request that typically hits is GET /health or GET /docs; no route before uvicorn.run.
- FastAPI app does not create services; it receives them (injected).

---

*Last updated by probes: 2026-01-29 (probe_01, probe_02). §5 pending probe_03.*
