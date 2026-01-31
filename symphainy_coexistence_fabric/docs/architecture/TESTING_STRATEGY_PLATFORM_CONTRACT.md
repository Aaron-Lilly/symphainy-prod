# Testing Strategy: Reinforcing the Platform Contract

**Purpose:** Ensure testing supports and reinforces the [Platform Contract](PLATFORM_CONTRACT.md) (especially §8A No Silent Degradation, §8B Component Dependency Contract). Prevent test-induced anti-patterns where production code is relaxed (e.g. "if None: return False") to accommodate tests, which then hide contract violations in production.

**Status:** Canonical. Test authors, CI, and review must align with this strategy.

**Principle:** Tests must **reinforce** the contract — they must verify that we fail when we should, and succeed when we should. Tests must **not** require or encourage production code to hide missing dependencies or to fall back silently.

---

## 1. What We Are Protecting Against

**Test-induced anti-patterns** occur when:

- A test runs without real infrastructure (e.g. no Redis, no DB). To make the test pass, someone adds production code that "handles" the missing dependency (e.g. `if not self.event_log: return False`). The test passes, but production can now silently fail or behave incorrectly when the dependency is missing.
- Tests mock at the wrong boundary (e.g. mock the adapter instead of injecting a protocol implementation), and production code is changed to "tolerate" None or missing mocks.
- Integration tests are skipped or disabled when infra is absent, and no one adds **contract tests** that verify we fail correctly when infra is missing. So we never assert that "missing dependency → raise."

**Result:** The platform contract is weakened; silent failures and hard-to-diagnose bugs appear in production. Genesis and "we don't run without required infra" are undermined.

---

## 2. Testing Principles (Contract-Reinforcing)

1. **Fail-fast behavior is part of the contract.** Tests must verify that when a required dependency is missing, the system (or component) **raises** with a clear message — it does **not** return False, empty list, or default. Add **negative tests** (e.g. "when event_log is None, TransactionalOutbox.add_event raises") and **probe/contract tests** (e.g. "when pre-boot fails, process exits with non-zero and clear message").

2. **Do not relax production code to make tests pass.** If a test fails because "component X has no backend," the fix is **not** to add `if not backend: return default` in production. The fix is either: (a) inject a **contract-compliant fake** (e.g. an in-memory implementation of EventLogProtocol) in the test, or (b) skip the test when the real backend is absent and document why, or (c) test the **failure path** explicitly (assert that we raise when dependency is None).

3. **Fakes must implement the contract (protocol).** When testing without real infrastructure, use **protocol-compliant** fakes: e.g. an in-memory implementation of EventLogProtocol for WAL/Outbox tests, not "pass None and hope the code doesn't crash." Production code then receives a real (fake) implementation and behaves as in production; we never rely on production code "handling" None for the test to pass.

4. **Probes and contract tests are first-class.** Tests that verify **platform contract** behavior (pre-boot fails when Redis is down; Outbox raises when event_log is None; no silent fallbacks) are as important as feature tests. They prevent regressions that introduce silent degradation.

---

## 3. Test Layers and Their Role

| Layer | Purpose | Contract role | Anti-pattern to avoid |
|-------|---------|---------------|------------------------|
| **Unit** | Test a component in isolation. | Use protocol-compliant fakes (e.g. in-memory EventLogProtocol). Assert behavior and assert that required-call paths receive non-None. | Don't pass None and add "if None: return" in production to make the test pass. |
| **Contract / negative** | Verify we fail when we should. | Explicit tests: "when dependency is None, component raises with clear message"; "when pre-boot fails, process exits." | Don't skip or remove these tests because they "break" when we add silent fallbacks. |
| **Integration** | Test with real or near-real infra. | Verify full path with real backends (or contract-compliant fakes that behave like real). | Don't mock at the wrong boundary (e.g. don't mock adapter and then have production accept None). |
| **Probes** | Verify boot order, init, and runtime shape. | Probes assert that after boot, required services are wired (e.g. get_wal_backend() used for WAL; no adapter getters in use). | Don't change production to "optional" just so probes pass in a minimal env. |

---

## 4. Required Contract Tests (Minimum Set)

The following **must** be covered by tests or probes; add them if missing:

1. **Pre-boot:** When a required backing service (e.g. Redis) is unreachable, pre-boot **exits with a clear, actionable message** (non-zero exit). No partial init.

2. **Composition:** When pre-boot has passed, `create_runtime_services()` builds WAL with a non-None event log backend (get_wal_backend()). WAL is not constructed with event_log=None in production code paths.

3. **At-use failure:** When a component that has a required dependency is invoked with that dependency None (e.g. TransactionalOutbox.add_event when event_log is None), the component **raises** (e.g. RuntimeError) with a message that includes "contract" or "wired" or equivalent. It does **not** return False or empty.

4. **No silent fallback:** No production code path that implements "if required_dependency is None: return default_or_false" for a component that lists that dependency as required in the platform contract. Code review and/or static checks should flag such patterns.

---

## 5. Guidelines for Test Authors

- **If a test needs "no Redis" or "no backend":** Inject a **fake that implements the protocol** (e.g. InMemoryEventLog for EventLogProtocol). Do not pass None and rely on production code to "handle" it.
- **If you cannot provide a fake:** Skip the test when the real backend is absent (e.g. `pytest.mark.skipif(no_redis)`), and add a **separate** test that asserts "when backend is None, we raise." That way we both (a) test behavior with real/fake when available, and (b) test that we fail correctly when not.
- **If a test fails with "NoneType has no attribute X":** The fix is **not** to add `if x is None: return` in production. The fix is to ensure the test injects a valid dependency (real or protocol-compliant fake).
- **Code review:** Reject production changes that add "if required_dependency is None: return ..." for components that document that dependency as required. Require a raise or a documented optional dependency instead.

---

## 6. CI and Enforcement

- **Run contract/negative tests** in CI (e.g. "outbox raises when event_log is None"; "pre-boot exits when Redis down"). These must pass; they protect against silent-degradation regressions.
- **Probes:** Run boot and Public Works probes in CI where possible; fail the build if probes show adapter leakage or optional wiring of required components.
- **Static scan for silent-degradation patterns:** The compliance test `tests/3d/compliance/test_silent_degradation_patterns.py` scans `symphainy_platform` for "if not self.<dep>:" followed by return default or fallback/in-memory behavior. It fails the build when any violation is found and reports file:line and snippet. Run with: `pytest tests/3d/compliance/test_silent_degradation_patterns.py -v`. Fix violations by replacing return/fallback with raise (or by documenting the dependency as optional and accepting the pattern only where explicitly allowed).

---

## 7. Summary

| Do | Don't |
|----|--------|
| Add tests that verify we **raise** when a required dependency is missing. | Add production code that **returns** (False, empty) when a required dependency is missing. |
| Use **protocol-compliant fakes** (e.g. InMemoryEventLog) in unit tests. | Pass **None** and change production to "if None: return" to make tests pass. |
| Skip integration tests when infra is absent, and document; add contract tests for "fail when missing." | Remove or skip contract tests because they "fail" after someone added silent fallbacks. |
| Treat contract tests and probes as first-class; they prevent deadly anti-patterns. | Treat "tests pass" as the only goal; allow relaxing production code to get there. |

---

## 8. Canonical Testing Path (Genesis-based)

**One way to test:** Use the same Genesis path as production (load_platform_config → pre_boot_validate → create_runtime_services → create_fastapi_app) so **what works in test also works in prod.**

- **Fixtures:** `genesis_app`, `genesis_client` (TestClient), `genesis_services` (app.state.runtime_services). Defined in `tests/3d/conftest.py`. Require env with all backing services (e.g. from `docker-compose.3d-test` or `.env.secrets`).
- **Test Supabase:** Set `USE_SUPABASE_TEST=1` and `SUPABASE_TEST_URL`, `SUPABASE_TEST_PUBLISHABLE_KEY`, `SUPABASE_TEST_SECRET_KEY` so tests hit the test project (rate limits disabled) without overriding prod vars. Genesis (platform_config) and get_env_contract() use TEST vars when `USE_SUPABASE_TEST=1`.
- **Real-infrastructure tests:** `tests/3d/real_infrastructure/` use `genesis_services` (real_solutions, real_execution_context, real_public_works come from Genesis app). No partial config or bypass of pre-boot.
- **API tests:** Use `genesis_client.get/post(...)` for session, intent, execution endpoints.
- **Legacy:** Mock fixtures (mock_public_works, content_solution, etc.) are deprecated; migrate tests to genesis_client or genesis_services.

This strategy ensures that testing **reinforces** the platform contract and does not accidentally introduce or encourage silent degradation or contract violations.
