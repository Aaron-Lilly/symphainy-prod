# Platform Fix Execution Plan

**Purpose:** Single execution-ready doc for a Cursor web agent (or human) to: (1) remove RealmBase and natively embrace the fabric’s platform nature (realms = solution + orchestrators + intent services); (2) execute the solution-fix action list; (3) keep docs and code aligned so the platform follows the intended pattern.

**Context:** See [SOLUTION_CONTRACT_RESOLUTION.md](./SOLUTION_CONTRACT_RESOLUTION.md), [PLATFORM_BASES_REVIEW.md](./PLATFORM_BASES_REVIEW.md), [PLATFORM_BASES_DISCIPLINE.md](./PLATFORM_BASES_DISCIPLINE.md). E2E/3d probe mismatches: [testing/stability_gravity_reports/20260129_e2e_contract_implementation_mismatch.md](../testing/stability_gravity_reports/20260129_e2e_contract_implementation_mismatch.md).

---

## Goal

- **Native platform:** Realms = solution + orchestrators + intent services (no RealmBase).
- **Solution consistency:** All solutions inherit from BaseSolution; standard journey result shape; tests aligned to contract.
- **Bases:** BaseSolution, BaseIntentService, BaseOrchestrator, AgentBase, MCPServerBase only; no RealmBase.

---

## Part A: Breaking change — Remove RealmBase and embrace native platform

### A.1 Simplify RealmRegistry (no RealmBase)

- **File:** `symphainy_platform/runtime/realm_registry.py`
- **Current:** Holds `Dict[str, RealmBase]`; `register_realm(realm: RealmBase)`; `get_realm(name)` → `Optional[RealmBase]`; registers intent handlers from `realm.declare_intents()` / `realm.handle_intent`.
- **Target:** RealmRegistry becomes a **realm-name registry** only (no RealmBase). Options:
  - **Option 1 (minimal):** Store `Dict[str, Dict[str, Any]]` (realm_name → metadata). `register_realm(name: str, metadata: Optional[Dict] = None)`. `get_realm(name)` returns `Optional[Dict]`. `list_realms()` returns list of names. Remove intent registration from RealmRegistry (intents are already registered via solutions/intent registry elsewhere). Populate realm names from a known list (e.g. `content`, `insights`, `operations`, `outcomes`, `security`, `coexistence`, `control_tower`) at runtime init or from solution registry.
  - **Option 2:** Remove RealmRegistry’s storage of instances; keep only `list_realms()` returning a fixed or config-driven list of realm names; remove `register_realm`/`get_realm` or make `get_realm(name)` return a simple `{"name": name}` dict.
- **Action:** Implement Option 1 or 2; remove all imports and types referencing `RealmBase` from `realm_registry.py`. Ensure `list_realms()` and, if kept, `get_realm(name)` return data that does not reference RealmBase.

### A.2 Update control_room_service fallback

- **File:** `symphainy_platform/civic_systems/experience/admin_dashboard/services/control_room_service.py`
- **Current:** Fallback uses `realm_registry.list_realms()` and `realm_registry.get_realm(realm_name)` and calls `realm.declare_intents()` on the result.
- **Target:** When using realm_registry fallback, do not call `.declare_intents()`. Build realm health list from `list_realms()` and, if `get_realm(name)` returns a dict, use that dict (e.g. `intents` key if present); otherwise `intents_supported: 0`, `intents: []` for each realm name.

### A.3 Remove or slim realm_sdk.py

- **File:** `symphainy_platform/civic_systems/platform_sdk/realm_sdk.py`
- **Current:** Defines `RealmBase(ABC)`, `RealmSDK.create_realm`, `validate_realm_contract(realm: RealmBase)`, `register_realm_with_runtime(realm: RealmBase, ...)`.
- **Target:** **Remove** `RealmBase` and all helpers that take or return `RealmBase`. If other code imports `RealmSDK` or `create_realm`/`validate_realm_contract`/`register_realm_with_runtime`, either remove those call sites or replace with a slim helper that works with realm name + metadata only. End state: no RealmBase in the codebase; realm_sdk.py can be removed entirely or reduced to a small module that only exports e.g. a list of known realm names or a docstring describing the native pattern (realms = solution + orchestrators + intent services).

### A.4 Update developer_view_service (remove MyRealm(RealmBase) example)

- **File:** `symphainy_platform/civic_systems/experience/admin_dashboard/services/developer_view_service.py`
- **Current:** Imports `RealmBase`, defines `MyRealm(RealmBase)` as example.
- **Target:** Remove `RealmBase` import and `MyRealm(RealmBase)` class. Replace with a short example or doc reference that shows the **native** pattern: e.g. “Realms = solution + orchestrators + intent services; see SOLUTION_PATTERN.md and BaseSolution.”

### A.5 Update docs that reference RealmBase / realm_sdk

- **Files:**  
  - `docs/intent_contracts/control_tower_developer/intent_admin_get_code_examples.md`  
  - `docs/intent_contracts/control_tower_developer/intent_admin_get_documentation.md`  
  - Any other doc that says “implement realms using RealmBase” or “RealmBase”.
- **Target:** Replace with the native pattern (solution + orchestrators + intent services; BaseSolution, SOLUTION_PATTERN.md). Remove or rewrite code snippets that use RealmBase.

### A.6 Grep and fix remaining references

- **Action:** Run grep for `RealmBase`, `realm_sdk`, `RealmRegistry` (and `register_realm` if signature changes). Fix imports, type hints, and call sites so nothing references RealmBase. Ensure tests and runtime init still pass (e.g. RealmRegistry instantiated with no RealmBase; control_room and control_tower get realm_registry where used).

---

## Part B: Solution fix action list

Execute in order; see SOLUTION_CONTRACT_RESOLUTION.md §4.1 and §4.3.

### B.1 Migrate solutions to BaseSolution

- **Target:** Every solution class inherits from `BaseSolution` (from `symphainy_platform.bases.solution_base` or `symphainy_platform.bases`).
- **Known gap:** `SecuritySolution` (and any other that does not yet) must inherit from `BaseSolution` so it has `get_journey` and `get_journeys` (and can use default `get_experience_sdk_config` if desired).
- **Action:** For each solution module under `symphainy_platform/solutions/`, add `BaseSolution` to the class bases and ensure `_initialize_journeys()` is used to populate `_journeys`. Remove any duplicate `get_journey`/`get_journeys` that only mirror the base; keep overrides only if behavior differs.

### B.2 Standardize journey returns (standard result shape)

- **Target:** Every journey’s `compose_journey` return includes `success`, `artifacts`, `events`, `journey_id`, `journey_execution_id`. Use `BaseSolution.build_journey_result(...)` where possible.
- **Action:** For each journey that currently returns a dict without `success` (or with inconsistent shape), change the return to use `BaseSolution.build_journey_result(success=..., journey_id=..., journey_execution_id=..., artifacts=..., events=..., error=...)` or build an equivalent dict. Focus on journeys that failed probes (e.g. security auth/registration, platform_monitoring) and any other that tests assert on `result["success"]`.

### B.3 Fix tests (action names, params, async, asserts)

- **Action names:** Tests and stubs must use the **canonical** action names (e.g. `stats` not `get_stats` for platform_monitoring). Align with journey’s supported actions (see SOLUTION_PATTERN.md or journey contract).
- **Required params:** Operations (and any other) journeys that require `workflow_id`, `sop_id`, etc.: pass those in test `journey_params` or fixtures; or document and skip with a clear reason if not yet implemented.
- **Async:** Any test that calls `initialize_mcp_server()` must use `await` and be in an async test (e.g. `@pytest.mark.asyncio`).
- **Asserts:** Tests that check journey or solution results should assert on the standard shape: `success`, `artifacts`, `events`, and optionally `journey_id`, `journey_execution_id`.

### B.4 Docs and SOLUTION_PATTERN

- **Target:** SOLUTION_PATTERN.md and any “how to add a solution” docs stay in sync with BaseSolution and the standard result/config shapes.
- **Action:** After B.1–B.3, skim SOLUTION_PATTERN.md and solution-related docs; add a one-line note or link to the execution plan or SOLUTION_CONTRACT_RESOLUTION if useful for future readers.

---

## Part C: Final checks and platform pattern

### C.1 No RealmBase left

- Grep for `RealmBase`, `realm_sdk` (where it referred to the base), and fix or remove.

### C.2 Bases and discipline

- Confirm only these bases are the “platform bases”: BaseSolution, BaseIntentService, BaseOrchestrator, AgentBase, MCPServerBase. Docs (PLATFORM_BASES_DISCIPLINE, PLATFORM_BASES_REVIEW, bases/README) already state RealmBase is removed/legacy; update to “removed” after Part A.

### C.3 Run relevant tests

- Run solution/journey/e2e tests that previously failed or touched solutions and realm health (e.g. `pytest tests/3d/solution/ tests/3d/journey/ tests/e2e/demo_paths/ -v --tb=short` or the subset from the stability/gravity reports). Fix any regressions introduced by Part A or B.

### C.4 Update execution plan status (optional)

- At the end of this doc, add a short “Execution log” or “Done” section with date and what was done (e.g. “RealmBase removed; RealmRegistry simplified; SecuritySolution migrated; tests X,Y,Z fixed”).

---

## Execution order (recommended)

1. **Part A.1** — Simplify RealmRegistry (no RealmBase).
2. **Part A.2** — Update control_room_service fallback.
3. **Part A.3** — Remove/slim realm_sdk.py (remove RealmBase and RealmBase-dependent helpers).
4. **Part A.4** — developer_view_service: remove MyRealm(RealmBase).
5. **Part A.5** — Update intent_contracts and other docs that reference RealmBase.
6. **Part A.6** — Grep and fix remaining references; run tests.
7. **Part B.1** — Migrate solutions to BaseSolution (SecuritySolution and any other).
8. **Part B.2** — Standardize journey returns (build_journey_result / standard shape).
9. **Part B.3** — Fix tests (action names, params, await, asserts).
10. **Part B.4** — Docs/SOLUTION_PATTERN in sync.
11. **Part C** — Final checks, test run, doc updates (“RealmBase removed”).

---

## References

- [SOLUTION_CONTRACT_RESOLUTION.md](./SOLUTION_CONTRACT_RESOLUTION.md) — §4 (solution inconsistency, existing bases, action list).
- [SOLUTION_BASE_DISCIPLINE.md](./SOLUTION_BASE_DISCIPLINE.md) — Lean base; no ballooning.
- [PLATFORM_BASES_DISCIPLINE.md](./PLATFORM_BASES_DISCIPLINE.md) — Common pattern (concrete base, type-hint as BaseX).
- [PLATFORM_BASES_REVIEW.md](./PLATFORM_BASES_REVIEW.md) — RealmBase unused; foundations embrace protocol/abstraction.
- [SOLUTION_PATTERN.md](../../symphainy_platform/solutions/SOLUTION_PATTERN.md) — How to add a solution; standard result/config shapes.
- Base implementation: `symphainy_platform/bases/solution_base.py` — BaseSolution, build_journey_result(), get_experience_sdk_config().
