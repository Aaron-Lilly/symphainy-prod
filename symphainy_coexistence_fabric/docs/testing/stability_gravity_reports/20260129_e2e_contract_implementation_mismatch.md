# Stability & Gravity Report

**Artifact Type:** Architectural Stability & Gravity Report  
**Scope:** E2E demo paths / Solution–Journey contract vs implementation (recurring pattern)  
**Epoch:** 2026-01-29 (post fixture fix, Option B—document only)

---

## A. What Was Probed

- **Change introduced:** Root `tests/conftest.py` added so e2e demo paths get solution/execution_context fixtures from 3d conftest. No product code change.
- **Trigger:** Re-running E2E demo paths after fixing fixture scope.
- **Expected impact (in human terms):** E2E tests would run; some might pass, some might fail on behavior. Instead we see a **recurring pattern**: test/developer expectations vs implementation don’t match.

---

## B. Observed Behavior

- **What broke:** 5 tests failed (15 passed).
  - **Control tower (1):** `test_platform_monitoring` — journey returns `error: "Unknown action: get_stats"`. Journey supports `"stats"`, `"metrics"`, `"realm_health"`, `"system_health"`, `"full_dashboard"`. Test passes `action: "get_stats"`. Naming mismatch.
  - **Security (4):** All security e2e tests — `AttributeError: 'SecuritySolution' object has no attribute 'get_journey'`. Other solutions (Content, ControlTower, Coexistence, Outcomes, Insights) expose `get_journey(journey_id)` and `get_journeys()`. SecuritySolution has `_journeys` and `_initialize_journeys()` but does not expose the same API. SOLUTION_PATTERN.md documents `get_journey` / `get_journeys`; SecuritySolution was built without them.
- **Where symptoms appeared:** pytest (e2e demo paths).
- **Time to failure:** Immediate (at test execution).

---

## C. Stability Signals

Answer yes/no and describe:

- **Did unrelated components break?** No. Only tests that assume a specific solution/journey API failed.
- **Did restarting "fix" it temporarily?** No.
- **Did the failure move when we changed order of startup?** N/A.
- **Did configuration changes have outsized effects?** No. This is contract/implementation drift, not config.

---

## D. Gravity Signals

Answer yes/no and describe:

- **Did logic migrate back into a specific service/module?** Not yet—we’re not fixing. Pattern: some solutions follow SOLUTION_PATTERN.md (get_journey), SecuritySolution does not. Suggests implementation was built without that contract in view.
- **Did agents need extra context to compensate?** N/A.
- **Did responsibilities blur across layers?** Yes. “What a solution exposes” (get_journey, action names, result shape) is not consistently defined or enforced. Tests assume one contract; implementations vary.
- **Did fixes require touching many files?** Unknown (no fix yet). Fixing would touch: SecuritySolution (add get_journey/get_journeys), and/or e2e tests (align action names and expectations). The **recurring** nature suggests an underlying miss: if we fix only these 5, more mismatches will appear unless we align how we build.

---

## E. Hypotheses (Do NOT Resolve)

- **Suspected unstable boundary:** **Builder–platform contract boundary.** Tests and e2e flows assume: (1) every solution exposes `get_journey(journey_id)`; (2) journey action names and result shapes are consistent. Implementations were built at different times or by different paths; some follow SOLUTION_PATTERN.md, some don’t. No single source of truth that builders and tests both consume.
- **Suspected missing contract:** (1) **Solution API contract:** “All solutions SHALL expose get_journey / get_journeys” — documented in SOLUTION_PATTERN.md but not enforced; SecuritySolution predates or bypasses it. (2) **Journey action contract:** Action names (e.g. `stats` vs `get_stats`) and result shape (e.g. when to include `artifacts`) are not codified per journey; test authors and journey authors diverge.
- **Suspected premature abstraction:** Unclear. Could be the opposite: we may have under-specified. The platform expects a solution/journey pattern; we didn’t give builders a single, machine- or contract-driven way to stay in step (e.g. generated stubs from contract, or contract tests that run at build time).

*No fixes here. Only hypotheses.*

---

## F. Classification

- [ ] Collapsing abstraction
- [x] **Leaky boundary** (builder vs platform: tests/developers expect one API and shape; implementations vary)
- [ ] Stable seam
- [ ] Unknown / needs more probes

---

## G. Recommendation

**Probe again with variation.** Defer fixing these 5 failures. Gather more signal: run more layers (real_infrastructure, browser), and record every mismatch between “what tests or developers expect” and “what the platform does.” Goal: see if the pattern repeats (action names, missing get_journey, result shape, etc.) so we can decide:

- **Option A:** Keep builders in step with platform expectations — formalize solution/journey contract (e.g. base class or interface, contract tests), then fix implementations and tests to match.
- **Option B:** Align the platform with how developers want to build — if developers consistently expect get_journey and certain action names, make the platform enforce or generate that surface so builders don’t drift.

Document each new mismatch in this report (or a short appendix) so we have one place that describes the “recurring pattern” before we choose A or B.

---

## Appendix: Next-probe mismatches (2026-01-29)

After running real_infrastructure, 3d solution/journey/intent, and browser check. Full log: [20260129_next_probes_summary.md](20260129_next_probes_summary.md).

**Real infrastructure:** SRE 4 passed, functional/critical 7 passed 1 skipped. No failures. Warnings: Pydantic v1 deprecated, PyPDF2 deprecated, supabase params deprecated.

**3d solution/journey/intent:** 400 passed, 5 failed. New mismatches (same class):

| Area | Mismatch | Pattern |
|------|----------|--------|
| Content (experience SDK config) | Test expects top-level `available_journeys`; implementation has nested `integration_patterns.journey_invocation.available_journeys`. | Result shape (config structure). |
| Operations (workflow, SOP) | Journey requires `workflow_id` / `sop_id` or `bpmn_file_id` or `workflow_spec`; tests don't pass them. | Required params not codified or shared with tests. |
| Security (auth, registration) | Result on failure has `artifacts.authenticated: False`, `error`; no `success` key. Test asserts `"success" in result`. | Result shape when journey fails. |
| Multiple solutions (MCP) | Tests call `initialize_mcp_server()` without `await`; method is async. | Async API contract not reflected in tests. |

**Browser:** App reachable at localhost:8000 (/docs 200, openapi.json present). Manual or MCP browser probe can run critical flows and record any failure here.
