# Stability / Gravity Reports

**Purpose:** Capture architectural signal from every failure or instability during Hop 1 (Discovery). Do not fix here—record hypotheses and classify.

**When to create a report:** Any failure or unexpected behavior in:
- pytest (any layer)
- Docker / startup / config
- Browser or E2E

**Naming:** `YYYYMMDD_<layer>_<short_description>.md`  
Examples:
- `20260129_platform_startup_order.md`
- `20260129_public_works_redis_connection.md`
- `20260129_browser_guide_agent_websocket.md`

**Template:** Copy [\_TEMPLATE.md](_TEMPLATE.md) and fill. Link from [HOLISTIC_TESTING_STRATEGY.md](../../HOLISTIC_TESTING_STRATEGY.md) and [new_testing_mindset.md](../../new_testing_mindset.md).

**Convergence:** When reports stop producing new hypotheses for a given seam, that seam is ready for Hop 2 (freeze and document).

**Recurring pattern (builder vs platform):** We are deliberately not fixing e2e contract/implementation mismatches yet. New mismatches (test/developer expectation vs implementation) should be recorded in or linked from [20260129_e2e_contract_implementation_mismatch.md](20260129_e2e_contract_implementation_mismatch.md) so we can see the full pattern before deciding: align builders to platform contract, or align platform to how developers want to build.

---

## First probe (2026-01-29)

| Layer | Result | Note |
|-------|--------|------|
| Startup | 14 passed | `tests/3d/startup/` |
| Integration | 13 passed | `tests/3d/integration/` |
| E2E demo paths | 20 errors (fixture not found) | See [20260129_e2e_fixture_scope.md](20260129_e2e_fixture_scope.md) → **fixed** via root `tests/conftest.py`. |
| Same flows from 3d | 20 passed | `tests/3d/journey/` (guide_agent, file_upload, auth) — confirms leaky boundary was test-harness scope. |
| E2E demo paths (post-fix) | 15 passed, 5 failed | See [20260129_e2e_contract_implementation_mismatch.md](20260129_e2e_contract_implementation_mismatch.md). **Option B:** defer fixes; treat as recurring pattern (builder vs platform contract). Gather more mismatches before aligning. |
| **Next probes** | Real infra, 3d solution/journey/intent, browser check | [20260129_next_probes_summary.md](20260129_next_probes_summary.md). Real infra: SRE + functional passed. 3d: 400 passed, 5 failed (config shape, required params, result-on-failure shape, async MCP). Browser: app reachable at localhost:8000. New mismatches appended to recurring-pattern report. |
