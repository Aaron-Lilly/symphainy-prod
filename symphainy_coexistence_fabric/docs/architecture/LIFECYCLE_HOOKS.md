# Platform Lifecycle Hooks

**Purpose:** Document where the five platform lifecycle hooks are invoked so Enterprise can add behavior without refactoring control flow. MVP: all hooks are no-ops (PLATFORM_VISION_RECONCILIATION §2.3).

**References:** [PLATFORM_VISION_RECONCILIATION.md](../PLATFORM_VISION_RECONCILIATION.md) §2.3, [BOOT_PHASES.md](BOOT_PHASES.md), `symphainy_platform/bootstrap/lifecycle_hooks.py`.

---

## Hook locations (runtime_main)

| Hook | When invoked | Code location |
|------|----------------|---------------|
| `startup_begin` | Before Φ1 / substrate init (before load_platform_config) | Start of `main()`, first thing in try block |
| `startup_complete` | After Φ3/Φ4 equivalent (runtime graph built, FastAPI app created) | After `create_fastapi_app(services)`, before `uvicorn.run()` |
| `shutdown_begin` | On graceful shutdown request (SIGTERM) | In SIGTERM signal handler; handler then calls `shutdown_complete()` and `sys.exit(0)` |
| `shutdown_complete` | After infrastructure released | (1) In SIGTERM handler after `shutdown_begin()`; (2) In `finally` after `uvicorn.run()` returns (normal server stop, e.g. SIGINT) |
| `crash_detected` | On unhandled exception in main path | In `main()` except block before `logger.error` and `sys.exit(1)` |

---

## Implementation

- **Module:** `symphainy_platform/bootstrap/lifecycle_hooks.py`
- **Bootstrap export:** `from symphainy_platform.bootstrap import startup_begin, startup_complete, shutdown_begin, shutdown_complete, crash_detected`
- **MVP:** All five functions are no-ops (pass). Enterprise may replace with telemetry, drain, WAL persist, recovery marking, etc., without changing call sites.

---

## Rule

Do not add new hook points or refactor control flow. When raising to Enterprise, replace no-op bodies with real behavior; keep the same five hooks and invocation points.
