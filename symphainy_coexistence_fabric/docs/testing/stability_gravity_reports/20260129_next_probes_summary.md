# Next Probes Summary (2026-01-29)

**Purpose:** Log results of recommended next probes (real infrastructure, 3d solution/journey/intent, browser check). New contract/implementation mismatches are appended to the [recurring-pattern report](20260129_e2e_contract_implementation_mismatch.md).

---

## 1. Real infrastructure

**Commands run:**
- `pytest tests/3d/real_infrastructure/ -v -m sre`
- `pytest tests/3d/real_infrastructure/ -v -m "functional or critical"`

**Results:**
- **SRE:** 4 passed (Redis connection, set/get; ArangoDB connection, create/read). Services reachable in this environment.
- **Functional/critical:** 7 passed, 1 skipped (real LLM call). Demo paths: auth, file upload, parsing, guide agent, navigation; LLM key check and GuideAgent LLM use passed.

**Warnings (signal, not failure):**
- Pydantic V1 style `@validator` deprecated (env_contract.py).
- PyPDF2 deprecated (move to pypdf).
- Supabase `timeout` / `verify` params deprecated.

**Conclusion:** Real infrastructure layer is healthy. Deprecation warnings are future tech-debt signal.

---

## 2. 3d solution / journey / intent

**Command run:** `pytest tests/3d/solution/ tests/3d/journey/ tests/3d/intent/ -v --tb=short`

**Results:** 400 passed, 5 failed, 1 skipped, 9 warnings.

**Failures (add to recurring-pattern narrative):**

| Test | What broke | Pattern |
|------|------------|--------|
| `test_experience_sdk_config_has_required_fields` (content) | AssertionError: `'available_journeys'` not at top level of config. Actual: nested under `integration_patterns.journey_invocation.available_journeys`. | **Result shape:** test expects flat key; implementation returns nested structure. |
| `test_handle_compose_journey_workflow` (operations) | ValueError: One of sop_id, bpmn_file_id, or workflow_spec is required. | **Required params:** test doesn’t pass params that journey mandates. Contract for journey params not aligned with test. |
| `test_handle_compose_journey_sop` (operations) | ValueError: workflow_id is required for SOP generation. | Same: **required params** not in test. |
| `test_handle_compose_journey_authentication` (security) | AssertionError: `'success' in result`. Result has `artifacts.authenticated: False`, `error: 'Authentication service unavailable'`; no `success` key when auth fails (mock auth can’t be awaited). | **Result shape when failure:** test expects `success` key; implementation returns different shape on failure. |
| `test_handle_compose_journey_registration` (security) | Same: no `success` key when registration fails (mock). | Same: **result shape on failure**. |

**Warnings (signal):**
- `coroutine 'X.initialize_mcp_server' was never awaited` — multiple solution tests (Coexistence, Content, ControlTower, Insights, Outcomes). Tests call async `initialize_mcp_server` without `await`. **Pattern:** sync test calling async API; test/solution contract for async lifecycle not enforced.

**Conclusion:** More of the same class: (1) **result shape** (config structure, success/failure shape), (2) **required params** (journey contract vs what tests pass), (3) **async API** (tests not awaiting async methods). Feed into decision: align builders to platform contract or platform to how developers expect to build.

---

## 3. Browser probe

**Check:** Runtime app reachable at `http://localhost:8000`.

**Results:**
- `GET /` → 404 (no root route; expected).
- `GET /docs` → 200 (Swagger UI).
- `GET /openapi.json` → 200 (OpenAPI 3.1.0, Symphainy Runtime API 2.0.0).

**Conclusion:** App is up. Browser probe can proceed manually or via MCP browser: open `http://localhost:8000/docs` (or frontend URL if different), run critical flows (login, guide agent, file upload), and record any failure in a Stability/Gravity report or appendix to the recurring-pattern report.

---

## 4. Summary for recurring-pattern report

**New mismatches to append to [20260129_e2e_contract_implementation_mismatch.md](20260129_e2e_contract_implementation_mismatch.md):**

1. **Experience SDK config shape:** Test expects top-level `available_journeys`; implementation uses nested `integration_patterns.journey_invocation.available_journeys`.
2. **Journey required params:** Operations journeys require `workflow_id` / `sop_id` or `bpmn_file_id` or `workflow_spec`; tests don’t pass them. No single contract for “what params this journey needs” that tests and implementation share.
3. **Result shape on failure:** Security auth/registration return `artifacts.authenticated: False` and `error`; no `success` key. Tests assert `"success" in result`. Contract for “what does a failed journey return?” not consistent.
4. **Async API in tests:** `initialize_mcp_server` is async; tests call it without `await`. Pattern: async lifecycle not reflected in test/solution contract.

---

## 5. Civic layer probe (agents + security)

**Commands run:**
- `python3 -m pytest tests/3d/agents/ tests/3d/security/ -v --tb=line`

**Results:** 24 passed, 12 failed.

**Failures:**

| Layer | Count | Root cause | Already assigned? |
|-------|--------|------------|--------------------|
| Agents | 1 | `test_route_to_liaison_with_context`: test passes `pillar_type`; journey expects `target_pillar` → `ValueError: target_pillar is required`. | **No — new.** See [20260129_guide_liaison_param_mismatch.md](20260129_guide_liaison_param_mismatch.md). |
| Security | 11 | SecuritySolution missing `get_journey` / `get_journeys`; SOA surface has no `compose_journey` key; tenant_id not in SOA param schema. | **Yes.** Same root as E2E/Solution contract; covered by PLATFORM_FIX_EXECUTION_PLAN. |

**New finding (assigned):** Guide Agent → Liaison handoff param contract: test uses `pillar_type`, journey uses `target_pillar`. Recommendation: align callers to `target_pillar` (canonical per intent service) and add/keep a probe that calls `_route_to_liaison_agent` with canonical params.

**Next:** Execute platform fix (RealmBase removal + solution/journey alignment); re-run Civic probe. Any remaining failures after that are new signal.

---

**Recommendation:** Continue to defer fixes. Use this plus the 5 e2e failures as the full “recurring pattern” evidence before choosing: (A) formalize and enforce solution/journey/result contract so builders stay in step, or (B) align platform (result shape, required params, async contract) to how developers are building and testing.
