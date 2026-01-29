# Layer-by-Layer Probe Results

**Date:** 2026-01-29  
**Principle:** Start at the bottom (startup), go layer by layer; verify what we think is there **is actually there** under the covers.  
**Target:** ≥85% confidence we have a working platform.

---

## Probe order (bottom → top)

As per [new_testing_mindset.md](../new_testing_mindset.md) and NEXT_TESTING_STEPS:

1. **Lock platform / startup** — purpose-built startup probes  
2. **Integration** — platform wiring (services, solution registry)  
3. **Curator** — solution registry + artifacts (metadata, lineage)  
4. **Real infrastructure** — SRE (Redis, Arango) + functional demo paths  
5. **Solution** — each solution loads, exposes journeys, SOA, MCP  
6. **MCP** — solution MCP servers initialize and expose tools  
7. **Journey + Intent** — solution/journey/intent contract and execution  
8. **Civic** — security, agents, tenant isolation  
9. **E2E demo paths** — horizontal flows (control tower, file-to-insight, guide agent, security, POC-to-roadmap)

---

## Results by layer

| Layer | Scope | Passed | Failed | Skipped | Notes |
|-------|--------|--------|--------|--------|-------|
| 1. Startup | `tests/3d/startup/` | 14 | 0 | 0 | All 8 solutions initialize; registry + intent registration; MCP init path. |
| 2. Integration | `tests/3d/integration/` | 13 | 0 | 0 | Platform services (Redis, Arango, Consul), solution registry, lifecycle. |
| 3. Curator | `test_solution_registry.py` + `tests/3d/artifacts/` | 20 | 0 | 0 | Registry + structured artifacts, validation, journey result shape. |
| 4. Real infra | `tests/3d/real_infrastructure/` (sre, functional) | 11 | 0 | 1 | Redis/Arango connectivity; demo paths (auth, file, guide, navigation). LLM call skipped. |
| 5a. Solution | `tests/3d/solution/` | 79 | 5 | 0 | See known failures below. |
| 5b. MCP | `tests/3d/mcp/` | 27 | 0 | 0 | All solution MCP servers; tool naming. (Warnings: `initialize_mcp_server` not awaited in tests.) |
| 6. Journey + Intent | `tests/3d/journey/` + `tests/3d/intent/` | 321 | 0 | 1 | Full journey and intent coverage. |
| 7. Civic | `tests/3d/security/` + `tests/3d/agents/` | 26 | 11 | 0 | Agents: all pass (liaison fix applied). Security: 11 failures → SecuritySolution contract (see below). |
| 8. E2E demo paths | `tests/e2e/demo_paths/` | 15 | 5 | 0 | Control tower (1: action name). Security (4: get_journey). |

---

## Full suite (single run)

- **Command:** `python3 -m pytest tests/3d/ tests/e2e/ -v --tb=no -q`
- **Result:** **535 passed**, 21 failed, 2 skipped.
- **Pass rate (excluding skipped):** 535 / (535 + 21) ≈ **96.2%**.

---

## Known failures (all documented; assigned)

All 21 failures map to **already documented** contract/implementation gaps in [stability_gravity_reports](stability_gravity_reports/) and [PLATFORM_FIX_EXECUTION_PLAN.md](../architecture/PLATFORM_FIX_EXECUTION_PLAN.md):

| Root cause | Count | Layer(s) | Fix plan |
|------------|--------|----------|----------|
| **SecuritySolution** missing `get_journey` / `get_journeys`; SOA surface no `compose_journey`; result shape (`success` key on failure); tenant_id in SOA schema | 11 civic + 4 e2e = 15 | Civic, E2E | PLATFORM_FIX_EXECUTION_PLAN Part B (align SecuritySolution to BaseSolution / platform contract). |
| **Control tower** platform_monitoring action name: test uses `get_stats`, journey expects `stats` (or similar) | 1 | E2E | Align test or journey action name. |
| **Content** experience_sdk_config: test expects top-level `available_journeys`; implementation uses nested `integration_patterns.journey_invocation.available_journeys` | 1 | Solution | Align test to actual shape or add top-level in config. |
| **Operations** compose_journey: tests don’t pass required params (`sop_id`/`bpmn_file_id`/`workflow_spec`; `workflow_id` for SOP) | 2 | Solution | Align test params to journey contract. |
| **Security** handle_compose_journey: tests expect `success` key; implementation returns `artifacts.authenticated`/`registered` + `error` on failure | 2 | Solution | Align test to accept failure shape or standardize result shape. |

No **new** instability discovered in this pass; all failures are the same seams already in the execution plan.

---

## Confidence statement

- **Pass rate:** ~96% of runnable tests pass.
- **Failure concentration:** 15/21 failures are SecuritySolution contract (get_journey, SOA surface, result shape); the rest are small contract/param/action-name mismatches.
- **Conclusion:** We have **≥85% confidence** that the platform is working **as implemented**: startup, integration, curator, real infra, solutions (except Security API shape), MCP, journeys, intents, and agents behave as coded. The remaining 21 failures are **known gaps** between tests/contracts and current implementation, not unknown breakage. Executing [PLATFORM_FIX_EXECUTION_PLAN.md](../architecture/PLATFORM_FIX_EXECUTION_PLAN.md) (and the small E2E/control-tower and content/operations alignments) should bring the suite to a passing state and support **Hop 2 (Architectural Commitment)**.

---

## Recommended next steps

1. **Execute** [PLATFORM_FIX_EXECUTION_PLAN.md](../architecture/PLATFORM_FIX_EXECUTION_PLAN.md) (RealmBase removal, SecuritySolution alignment, solution/journey/intent fixes).
2. **Re-run** full suite; confirm 21 → 0 failures (or document any new signal).
3. **Optional:** Add a lightweight browser probe (e.g. hit `/docs`, one critical path) and record in a Stability/Gravity report if anything surprises.
4. **Converge:** Once pass rate holds and patterns are stable, freeze and move to Hop 2 (contract map, CI enforcement).
