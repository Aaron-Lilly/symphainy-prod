# Why Genesis Works and How Boot Behaves

**Purpose:** Step 1 deliverable for MEET_IN_THE_MIDDLE_PLAN. One place that explains what runs when, what fails fast, and what is deferred so the next layer (foundations probe) and Team B can rely on it.

**References:** [genesis_protocol.md](genesis_protocol.md), [FOUNDATION_PLAN.md](FOUNDATION_PLAN.md), [BOOT_PHASES.md](architecture/BOOT_PHASES.md), [LIFECYCLE_HOOKS.md](architecture/LIFECYCLE_HOOKS.md), [STEP1_GENESIS_PROBE.md](testing/STEP1_GENESIS_PROBE.md).

---

## What runs when

1. **Entry:** `runtime_main.main()` (single entry point).
2. **Lifecycle: startup_begin** — Invoked first (no-op in MVP). Before any config or infra.
3. **G2 (Config):** `load_platform_config()` — Acquires env (`.env.secrets`, `config/development.env`, `.env`), builds canonical config. One source of truth; no env reads inside Public Works for platform infra.
4. **G3 (Pre-boot):** `pre_boot_validate(config)` — Checks Redis, Arango, Supabase, GCS, Meilisearch, DuckDB, Consul. **On first failure: process exits with code 1 and a clear message.** No partial init.
5. **Φ3 (Runtime graph):** `create_runtime_services(config)` — PublicWorks (adapters + abstractions) → StateSurface → WAL → IntentRegistry (register intent handlers) → initialize solutions/MCP → ExecutionLifecycleManager → RuntimeServices. If PublicWorks.initialize() returns False, **RuntimeError is raised** and process exits (no "continuing anyway").
6. **FastAPI app:** `create_fastapi_app(services)` — App receives services; does not create them. Routes registered.
7. **Lifecycle: startup_complete** — Invoked after app is created (no-op in MVP). Runtime graph + app ready.
8. **Server:** `uvicorn.run(app, host, port, log_level)` — Blocks until server stops. GET /health and other routes available once bound.
9. **On SIGTERM:** `shutdown_begin()` then `shutdown_complete()` then `sys.exit(0)` (no-ops in MVP).
10. **On unhandled exception in main:** `crash_detected(exc)` then log and `sys.exit(1)` (no-op in MVP).

---

## What fails fast

- **Pre-boot (G3):** If any required service (Redis, Arango, Supabase, GCS, Meilisearch, DuckDB, Consul) is unreachable or unauthorized, the process **exits immediately** with a clear message (e.g. "Platform contract violation: ArangoDB failed: ..."). We do not enter `create_runtime_services()`.
- **PublicWorks init:** If `public_works.initialize()` returns False, `create_runtime_services` raises RuntimeError and the process exits. We do not build a partial graph.
- **RuntimeServices validation:** If any required field (e.g. registry_abstraction) is None, `RuntimeServices.__post_init__` raises ValueError and the process exits before FastAPI is created.

---

## What is deferred

- **Lifecycle hook behavior:** All five hooks exist and are invoked at the documented points; in MVP they are no-ops. Enterprise may add telemetry, drain, WAL persist, recovery marking, etc., without refactoring control flow (PLATFORM_VISION_RECONCILIATION §2.3).
- **Graceful shutdown protocol:** MVP does not drain in-flight execution or run a formal checkpoint before exit; SIGTERM handler calls shutdown_begin/shutdown_complete (no-ops) then exits. Enterprise-gated.
- **Crash recovery / startup integrity:** No mandatory WAL replay, state consistency check, or zombie cleanup on startup. Pre-boot only validates backing service connectivity. Enterprise-gated.
- **Intent registration failures:** If an intent fails to register (e.g. extract_embeddings due to EmbeddingAgent import), we log a warning and continue. Other intents are registered. Fix or document per intent in later steps.
- **MCP server init failures:** If a solution MCP server fails to initialize (e.g. await on non-async), we log a warning and continue. Other MCP servers are registered. Fix or document per solution in later steps.

---

## Summary

- **Why it works:** One entry point; config before infra; pre-boot fails at the door; runtime graph built in fixed order with no partial init; lifecycle hooks at documented points so Enterprise can extend without refactoring.
- **How it behaves:** G2 → G3 → Φ3 → app → uvicorn. If G3 fails, we exit with a clear message. If Φ3 fails (PublicWorks or RuntimeServices), we raise and exit. Once uvicorn is running, the server serves until SIGTERM or exception; then shutdown hooks run (no-ops) and process exits.
