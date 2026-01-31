# Platform Probe Approach: From Nothing to Protocols

**Purpose:** Testing strategy that gets as close as humanly possible to guaranteeing (1) the platform properly works from nothing to exposing protocols, and (2) protocols only exist when infrastructure is there to support them—all other pathways fail in predictable ways.

**Principle:** Public Works stops at the **protocol layer**. Civic systems and Platform SDK compose and expose those protocols. We do not edit Public Works for new composition patterns—only for new protocols or new infrastructure. Tests validate each seam so success and failure are unambiguous and asserted.

**References:** [PLATFORM_SEAMS.md](PLATFORM_SEAMS.md), [PROTOCOL_REGISTRY.md](../architecture/PROTOCOL_REGISTRY.md), [PLATFORM_CONTRACT.md](../architecture/PLATFORM_CONTRACT.md) §8A/§8C, [PUBLIC_WORKS_STRATEGIC_FIX_PLAN.md](../architecture/PUBLIC_WORKS_STRATEGIC_FIX_PLAN.md).

---

## 1. Guarantee we’re testing for

| Guarantee | Meaning |
|-----------|--------|
| **From nothing to protocols** | Boot (Genesis G2→G3→Φ3) with required infra → Public Works is created → required protocol getters return non-None, and a minimal use of each required protocol does not throw (or returns a defined shape). |
| **Protocols only when infra exists** | A protocol is “available” only when its backing infra was validated at boot and wired. If required infra is missing, we never create Public Works (Genesis fails). If optional infra is missing, get_* returns None and any use must fail fast. |
| **All other pathways fail** | Every path that could expose capability without infra must fail in a predictable way: boot fails (exit 1), getter returns None and caller fails (§8A), or direct adapter access is impossible (raised / not exposed). |

---

## 2. Seam layers and what each probe proves

### Layer A: Boot seam (Genesis gate)

**Seam:** `pre_boot_validate(config)` → decision to run `create_runtime_services(config)` or exit.

| Criterion | Expected behavior | Probe test(s) |
|-----------|-------------------|---------------|
| **Success** | All required backing services pass G3 → `create_runtime_services` runs → Public Works exists. | Boot with full config (or real infra); assert Public Works created and required get_* non-None (see Layer B). |
| **Failure** | Any required service missing/unreachable → `_fail` → `sys.exit(1)` → no `create_runtime_services`, no Public Works. | `test_seam_genesis_gate`: `pre_boot_validate(config_with_missing_required)` raises `SystemExit(1)` (with `_fail` patched to raise). |

**Location:** `tests/3d/compliance/test_seam_genesis_gate.py`

---

### Layer B: Protocol existence (only when infra is there)

**Seam:** For each protocol, “it exists” means: backing infra was validated at boot and the getter returns a working implementation (non-None for required; None allowed for optional).

| Criterion | Expected behavior | Probe test(s) |
|-----------|-------------------|---------------|
| **Required protocols** | When Genesis succeeds (full required infra), every required protocol getter returns non-None. Optional: one minimal “smoke” call per required protocol (e.g. no-op or read that doesn’t throw). | **To add:** `test_seam_protocol_presence`: with `genesis_services` (or Public Works built from full config), assert `get_state_abstraction()`, `get_file_storage_abstraction()`, … (list from PROTOCOL_REGISTRY “required”) are not None. Optionally assert protocol methods exist (e.g. `hasattr(get_state_abstraction(), 'retrieve_state')`). |
| **Optional protocols** | When a protocol is optional (e.g. LLM, HuggingFace) and its infra is not configured, getter returns None. Any caller that assumes presence must fail fast (§8A or clear error). | **To add:** Document which getters are optional; test that with config omitting optional infra, get_* returns None; and that a representative caller using it fails (not silent). |
| **No protocol without infra** | Required protocols are only ever “present” after a successful G3. So “protocol exists” is implied by “we booted”; no separate “protocol exists with missing infra” for required—boot already failed. | Covered by Layer A failure + Layer B success. |

**Backing infra per protocol:** See [PROTOCOL_REGISTRY.md](../architecture/PROTOCOL_REGISTRY.md) and PLATFORM_CONTRACT §3. Required infra (Redis, Arango, Consul, Supabase, GCS, Meilisearch, DuckDB, OTLP) backs the required protocols; if any is missing, G3 fails and no protocols are exposed.

**Location:** `tests/3d/compliance/` — add `test_seam_protocol_presence.py` (and optional `test_seam_optional_protocol_absence.py`).

---

### Layer C: Caller → protocol (no silent degradation)

**Seam:** A caller uses a component (StateSurface, ArtifactRegistry, intent service, etc.) that depends on a protocol. If the dependency was not wired (None), the call must not succeed silently.

| Criterion | Expected behavior | Probe test(s) |
|-----------|-------------------|---------------|
| **Success** | Dependency wired → operation proceeds (or fails with domain/backend error, not “missing dependency”). | Covered by integration/journey tests that use real or fixture Public Works. |
| **Failure** | Required dependency is None (and use_memory=False where applicable) → method raises `RuntimeError` with “Platform contract §8A”. No return of None, False, [], {} as success. | `test_seam_section_8a_upstream`: StateSurface/ArtifactRegistry with `state_abstraction=None`, `use_memory=False` → get/set/resolve raises RuntimeError with §8A. Extend to other components that take protocol dependencies (e.g. intent services with `public_works=None`). |

**Location:** `tests/3d/compliance/test_seam_section_8a_upstream.py` (extend as needed).

---

### Layer D: No escape hatches (adapters / raw getters)

**Seam:** No code path outside Public Works can obtain an adapter or bypass the protocol layer.

| Criterion | Expected behavior | Probe test(s) |
|-----------|-------------------|---------------|
| **No adapter leak** | No file outside `foundations/public_works/` imports adapter classes (RedisAdapter, ArangoAdapter, SupabaseAdapter, etc.). No caller uses `get_redis_adapter()`, `get_arango_adapter()`, `get_supabase_adapter()` for capability—those getters raise RuntimeError. | **To add:** (1) Grep/CI: no import of adapter class from outside public_works. (2) Test: `public_works.get_arango_adapter()` and `public_works.get_supabase_adapter()` raise RuntimeError. (Already true in code; add explicit test if not present.) |
| **Protocols are the only surface** | Civic systems / Platform SDK receive protocol-typed capabilities (get_* returning protocol), not adapters. | Enforced by architecture + Layer D tests; composition tests live in Civic/SDK suites. |

**Location:** `tests/3d/compliance/` — add `test_seam_no_adapter_leak.py` (grep-based or import scan + getter-raise test).

---

## 3. Guarantee matrix (seam × success × failure)

| Seam | Success probe | Failure probe |
|------|----------------|----------------|
| **A. Genesis gate** | Full config → pre_boot passes → create_runtime_services runs (or: genesis_app exists and /health 200). | Config missing required infra → pre_boot_validate raises SystemExit(1). |
| **B. Protocol presence** | After boot, required get_* return non-None (and optional smoke per protocol if desired). | N/A for required (boot fails first). Optional: config without optional infra → get_* returns None; use → fails. |
| **C. Caller → protocol** | Component with wired dependency → call succeeds or fails with domain error. | Component with dependency=None → RuntimeError §8A. |
| **D. No escape** | Callers use get_* only; no adapter imports outside Public Works. | get_*_adapter() raise; grep finds no adapter leak. |

---

## 4. Test inventory (existing vs to add)

| Test / check | Status | Location |
|--------------|--------|----------|
| Genesis fails when required infra missing | Done | `test_seam_genesis_gate.py` |
| Caller with None dependency raises §8A (StateSurface, ArtifactRegistry) | Done | `test_seam_section_8a_upstream.py` |
| No silent degradation patterns in platform code | Done | `test_silent_degradation_patterns.py` |
| Required protocol getters non-None after successful boot | Done | `test_seam_protocol_presence.py` (runs when genesis_services available; skips when infra missing) |
| Optional protocol getter returns None when infra absent; use fails | To add | `test_seam_optional_protocol_absence.py` (if we have optional protocols to cover) |
| get_arango_adapter / get_supabase_adapter raise RuntimeError | Done | `test_seam_no_adapter_leak.py` |
| CI/grep: no adapter import outside public_works | To add | CI step or pytest that scans imports |

---

## 5. Running the probe stack

- **Fast (no real infra):** Layer A failure, Layer C failure, Layer D getter-raise, silent-degradation scan. Use patched config and None-dependency fixtures.
- **With real infra (e.g. 3d-test compose):** Layer A success (genesis_app), Layer B success (required get_* non-None, optional smoke). Run as part of 3d/real_infrastructure or compliance when env is up.
- **CI:** Run all compliance tests (seam + silent degradation); run adapter-leak grep/scan. Run “with real infra” suite when infra is available (e.g. in a dedicated pipeline or nightly).

---

## 6. Summary

- **Public Works = protocol layer only.** Composition is Civic/Platform SDK; we don’t change Public Works for new composition patterns.
- **Probes per seam:** Genesis (boot fail/success), protocol presence (getters non-None when boot succeeded), caller with None dependency (§8A), no adapter leak (raise + grep).
- **Guarantee:** “From nothing to protocols” and “protocols only when infra exists; all other paths fail” are enforced by (1) G3 gate, (2) protocol-presence assertions after boot, (3) §8A upstream probes, (4) no adapter escape. Filling the “to add” tests and CI steps gets as close as possible to that guarantee.
