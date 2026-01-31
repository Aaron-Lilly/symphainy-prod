# Platform Seams

**Purpose:** Define where platform boundaries are and how the platform behaves at those seams with no ambiguity. Probe tests validate that behavior.

**Related:** [PUBLIC_WORKS_REALITY_MAP.md](PUBLIC_WORKS_REALITY_MAP.md), [PLATFORM_CONTRACT.md](../PLATFORM_CONTRACT.md) §8A, [TESTING_STRATEGY_PLATFORM_CONTRACT.md](TESTING_STRATEGY_PLATFORM_CONTRACT.md).

---

## Seam 1: Genesis gate (G3) → Public Works

**Boundary:** Genesis pre-boot validation (Gate G3) decides whether the process proceeds to create runtime services (and thus Public Works).

| Aspect | Description |
|--------|-------------|
| **When** | `pre_boot_validate(config)` runs before `create_runtime_services(config)`. |
| **Success** | All required backing services (Redis, Arango, Supabase, GCS, Meilisearch, DuckDB, Consul, Telemetry) pass connectivity/readiness checks → `_last_pre_boot_result["status"] = "passed"` → caller (e.g. `runtime_main`) proceeds to `create_runtime_services` → Public Works is created. |
| **Failure** | Any required check fails → `_fail(service, reason, hint)` → `sys.exit(1)` → process exits. **No** `create_runtime_services`, **no** Public Works. |
| **Implication** | Adapters are excluded from §8A silent-degradation scan because **if we reach Public Works, infra was already validated at this seam.** Adapters report connection state; Genesis is the gate. |

**Probe tests:** `tests/3d/compliance/test_seam_genesis_gate.py`  
- `pre_boot_validate(config)` with missing required infra (e.g. `supabase_url=""`) raises `SystemExit(1)` (with `_fail` patched to raise so test process does not exit).

---

## Seam 2: Caller → Platform (abstractions / components)

**Boundary:** Callers (runtime, intent services, libraries) invoke platform components (StateSurface, ArtifactRegistry, backends, intent services). Those components depend on wired abstractions/adapters.

| Aspect | Description |
|--------|-------------|
| **When** | Any call into a platform component that requires a dependency (e.g. `state_abstraction`, `file_storage`, `public_works`). |
| **Success** | Dependency wired → operation proceeds (or fails with domain/backend error, not silent default). |
| **Failure** | Required dependency missing at call time (e.g. `state_abstraction is None` with `use_memory=False`) → component raises **`RuntimeError`** with message containing **"Platform contract §8A"**. No silent return of `None`, `False`, empty list/dict, or in-memory fallback. |
| **Implication** | Upstream callers see an explicit failure at this seam; no silent degradation. |

**Probe tests:** `tests/3d/compliance/test_seam_section_8a_upstream.py`  
- StateSurface with `state_abstraction=None`, `use_memory=False`: `get_session_state` / `set_session_state` raise `RuntimeError` with §8A.  
- ArtifactRegistry with `state_abstraction=None`, `use_memory=False`: `resolve_artifact` raises `RuntimeError` with §8A.

---

## Summary

| Seam | Location | Success | Failure |
|------|----------|---------|---------|
| **Genesis → Public Works** | `pre_boot_validate` before `create_runtime_services` | All G3 checks pass → Public Works created | Any check fails → `sys.exit(1)` → no Public Works |
| **Caller → Platform** | Any platform component method using a required dependency | Dependency wired → operation proceeds | Dependency missing → `RuntimeError` with "Platform contract §8A" |

These seams are validated by probe tests so that megaprotocol refactors and 5 capability service composition proceed on proven behavior at the boundaries.

**Full testing approach:** [PLATFORM_PROBE_APPROACH.md](PLATFORM_PROBE_APPROACH.md) — layered probe strategy to guarantee "from nothing to protocols" and "protocols only when infra exists; all other paths fail" (Genesis gate, protocol presence, caller §8A, no adapter leak).
