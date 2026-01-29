# Next Testing Steps (Resume Discovery)

**Context:** We are in **Hop 1 (Discovery)**. We already probed startup, integration, e2e demo_paths, 3d solution/journey/intent, real_infrastructure, and a light browser check. Failures were captured in [stability_gravity_reports](stability_gravity_reports/) and fed into [PLATFORM_FIX_EXECUTION_PLAN.md](../architecture/PLATFORM_FIX_EXECUTION_PLAN.md). This doc says **where to go next** with the new innovative (discovery-first) plan.

**Principle:** Discovery first, alignment second. **Probes** (not tests) trace and document how the platform actually operates; their output fills the [Platform Operation Map](PLATFORM_OPERATION_MAP.md) so we can state with **100% certainty** exactly how it operates. See [PROBE_DESIGN.md](PROBE_DESIGN.md) and [probes/README.md](../probes/README.md). Run probes in order: probe_01 → probe_02 → probe_03; then use tests for assertion only after convergence.

**Path to working platform:** For a hybrid approach (contract first, fail at the door, roadmap to working), see [PATH_TO_WORKING_PLATFORM.md](PATH_TO_WORKING_PLATFORM.md). Probes then document "what we built" when the contract holds.

**Platform inventory (single source of truth):** For "what's actually in our platform vs what we need" (containers, code requirements, env, config shape), see [PLATFORM_INVENTORY.md](PLATFORM_INVENTORY.md). Use it before implementing pre-boot or changing compose.

**Layer-by-layer probe run (2026-01-29):** Full suite run bottom→top recorded in [LAYER_BY_LAYER_PROBE_RESULTS.md](LAYER_BY_LAYER_PROBE_RESULTS.md). **535 passed, 21 failed, 2 skipped** (~96% pass rate). All failures are known and assigned; ≥85% confidence platform works as implemented. Next: execute PLATFORM_FIX_EXECUTION_PLAN, then re-run full suite.

---

## Recommended order

### Step 1: Execute the platform fix (then re-probe)

- **Why first:** The known failures (5 e2e + 5 from 3d solution/journey/intent) are already classified as contract/implementation mismatch. Fixing them via [PLATFORM_FIX_EXECUTION_PLAN.md](../architecture/PLATFORM_FIX_EXECUTION_PLAN.md) gives a **clean baseline** so the next probes reveal **new** signal, not the same 10 items.
- **Action:** Assign the execution plan to a Cursor (or other) agent. After it completes:
  - Re-run: `pytest tests/e2e/demo_paths/ -v` and `pytest tests/3d/solution/ tests/3d/journey/ tests/3d/intent/ -v --tb=short`.
  - If the former failures are gone → record in a short “Post-fix probe” note; then proceed to Step 2.
  - If new failures appear → create a Stability/Gravity report (scope = layer that failed); do not assume the fix was wrong until you map the new signal.

### Step 2: Curator layer probe

- **Goal:** Map implicit assumptions about artifacts, metadata, lineage. Ask: misconfiguration in foundation vs true architectural instability?
- **Commands:**
  ```bash
  pytest tests/3d/integration/test_solution_registry.py -v
  pytest tests/3d/artifacts/ -v
  ```
  Plus any journey tests that touch artifact/registry flows (e.g. file_upload, artifact export).
- **On failure or odd behavior:** Create a Stability/Gravity report; scope = `curator` or `solution_registry`. Hypotheses only; do not fix yet unless blocking the next probe.

### Step 3: Civic Systems layer probe *(probed 2026-01-29)*

- **Goal:** Policy enforcement, auth, agentic boundaries. Ask: contract mismatches at runtime?
- **Commands:**
  ```bash
  python3 -m pytest tests/3d/security/ tests/3d/agents/ -v
  ```
- **Latest result (2026-01-29):** 24 passed, 12 failed. One **new** finding: Guide Agent liaison handoff param mismatch (`pillar_type` vs `target_pillar`) → [20260129_guide_liaison_param_mismatch.md](stability_gravity_reports/20260129_guide_liaison_param_mismatch.md). Eleven security failures = same root (SecuritySolution get_journey/get_journeys, SOA surface); already in execution plan.
- **On failure:** Report; scope = `civic_security` or `civic_agents`. Classify: architectural signal vs operational noise.

### Step 4: Browser / horizontal journey (critical path)

- **Goal:** “Where symptoms appeared (browser)” — the lens that previously revealed real issues. Does the end-to-end experience match the emergent reality we’ve documented?
- **Action:**
  1. Start the app (e.g. `python runtime_main.py` or your usual run).
  2. Open browser (or use MCP browser): hit `/docs`, then exercise **one** critical path, e.g.:
     - Login (auth flow)
     - Guide agent (one turn)
     - File upload → materialization (content path)
     - Control tower: get realm health or platform stats
  3. For **any** failure or unexpected behavior (wrong response, 500, missing data, wrong shape): create a **Stability/Gravity report**. Scope = layer you think it belongs to (e.g. `browser_auth`, `browser_guide_agent`, `browser_content`). Trigger = “Browser critical path”; expected impact = “User can complete flow.”
- **Then:** Run horizontal demo paths as pytest if you have them: `pytest tests/3d/real_infrastructure/test_demo_critical_paths.py -v -m functional` (with app/infra up). Feed any failure into a report.

### Step 5: Contracts vs reality (manual + Cursor)

- **Goal:** Compare declared contracts to observed behavior. Decide per contract: foundation fragile vs contract overambitious.
- **Action:** Open `docs/solution_contracts/`, `docs/journey_contracts/`, `docs/intent_contracts/` and compare to:
  - What actually passed/failed in Steps 1–4.
  - What the platform allows (from startup, integration, solution/journey/intent probes).
- List mismatches in a short “Contracts vs reality” note or appendix to an existing report. No fix yet—record.

### Step 6: Converge and decide

- **When:** After Steps 1–5 (and optionally more variation: different env, Docker, order).
- **Ask:** Do failures repeat in recognizable patterns? Do certain files/services look like “centers of gravity”? Can you predict what will break?
- **If yes:** You’re approaching Hop 1 convergence. Freeze and document (Stability/Gravity + Contracts vs reality); then move to Hop 2 (enforce intent, CI, contract map).
- **If no:** Iterate: run more probes (other layers, different triggers), keep reporting. The “next aha moment” is the next failure that fits a pattern or reveals a new boundary.

---

## Quick reference: probe commands

| Layer / goal              | Command(s) |
|---------------------------|------------|
| Platform (startup)        | `pytest tests/3d/startup/ -v` |
| Integration               | `pytest tests/3d/integration/ -v` |
| Curator                   | `pytest tests/3d/integration/test_solution_registry.py tests/3d/artifacts/ -v` |
| Civic (security, agents)  | `pytest tests/3d/security/ tests/3d/agents/ -v` |
| Solution / journey / intent | `pytest tests/3d/solution/ tests/3d/journey/ tests/3d/intent/ -v --tb=short` |
| E2E demo paths            | `pytest tests/e2e/demo_paths/ -v` |
| Real infra (SRE / functional) | `pytest tests/3d/real_infrastructure/ -v -m sre`; `-m "functional or critical"` |
| Browser                   | Start app → open `/docs` and critical path (login, guide agent, file upload); record failures in Stability/Gravity report. |

---

## Where to record

- **Stability/Gravity reports:** [stability_gravity_reports/](stability_gravity_reports/). Copy [_TEMPLATE.md](stability_gravity_reports/_TEMPLATE.md); name like `YYYYMMDD_<layer>_<brief>.md`.
- **Post-fix / contracts vs reality:** New report or appendix in an existing report; or a short `YYYYMMDD_post_fix_probes.md` / `YYYYMMDD_contracts_vs_reality.md`.

---

## Summary

1. **Execute** [PLATFORM_FIX_EXECUTION_PLAN.md](../architecture/PLATFORM_FIX_EXECUTION_PLAN.md); **re-run** e2e + 3d solution/journey/intent to confirm known failures are addressed.
2. **Probe** Curator → Civic → **Browser / horizontal journey** (critical path + demo paths). Report every failure; hypotheses only.
3. **Compare** contracts to reality; list mismatches.
4. **Converge** when patterns stabilize; then lock intent (Hop 2) and move to enforcement.

The “next aha moment” is the next failure that either fits a recurring pattern or reveals a new seam—capture it in a Stability/Gravity report and feed it into the same decision: align to platform contract or adjust the contract.
