# Stability & Gravity Report

**Artifact Type:** Architectural Stability & Gravity Report  
**Scope:** E2E demo paths / test harness (Solution–Journey fixtures vs e2e scope)  
**Epoch:** 2026-01-29 (first probe, inline)

---

## A. What Was Probed

- **Change introduced:** None. First run of Hop 1 probe sequence.
- **Trigger:** Running E2E demo path tests (`pytest tests/e2e/demo_paths/ -v`) after startup and integration layers passed.
- **Expected impact (in human terms):** E2E tests would run (pass or fail on behavior). Instead, all 20 tests errored at setup.

---

## B. Observed Behavior

- **What broke:** All 20 tests in `tests/e2e/demo_paths/` failed at **fixture resolution** (setup). Example: `fixture 'control_tower' not found`; same for `content_solution`, `insights_solution`, `coexistence_solution`, `execution_context`.
- **Where symptoms appeared:** pytest collection/setup (not runtime, not browser).
- **Time to failure:** Immediate (at test setup).

---

## C. Stability Signals

Answer yes/no and describe:

- **Did unrelated components break?** N/A (no other tests run in same session for e2e).
- **Did restarting "fix" it temporarily?** No (re-run same: same errors).
- **Did the failure move when we changed order of startup?** N/A.
- **Did configuration changes have outsized effects?** No. Fixtures are missing in scope, not misconfigured.

---

## D. Gravity Signals

Answer yes/no and describe:

- **Did logic migrate back into a specific service/module?** No.
- **Did agents need extra context to compensate?** N/A.
- **Did responsibilities blur across layers?** Yes. E2E tests assume they run in a context where solution/execution_context fixtures exist; those fixtures live in `tests/3d/conftest.py`. Pytest conftest scope: `tests/e2e/demo_paths/` does not automatically see `tests/3d/conftest.py`. So **test-harness boundary**: e2e vs 3d fixture scope is undefined.
- **Did fixes require touching many files?** Unknown (no fix yet). Likely one or two: either add a conftest at `tests/e2e/` that imports/reexports 3d fixtures, or run e2e with a root conftest that makes 3d fixtures available.

---

## E. Hypotheses (Do NOT Resolve)

- **Suspected unstable boundary:** Test harness boundary between `tests/3d/` (fixtures in conftest.py) and `tests/e2e/demo_paths/` (no access to those fixtures by default). E2E tests were written assuming they run under the same conftest as 3d journey tests, but they are in a different tree.
- **Suspected missing contract:** Explicit contract for "how do e2e tests get solution/execution_context fixtures?" Options: (1) e2e conftest pulls in 3d fixtures, (2) e2e tests live under 3d and run with 3d conftest, (3) e2e has its own fixtures that mirror 3d. Currently none is documented or enforced.
- **Suspected premature abstraction:** Possibly: "e2e" was separated from "3d" without defining the fixture/lifecycle contract. Not premature abstraction in product code—in test layout.

*No fixes here. Only hypotheses.*

---

## F. Classification

- [ ] Collapsing abstraction
- [x] **Leaky boundary** (test harness: e2e vs 3d fixture scope)
- [ ] Stable seam
- [ ] Unknown / needs more probes

---

## G. Recommendation

**Probe again with variation:** Run the same E2E flows from under `tests/3d/` (e.g. run the journey tests that mirror demo paths) to confirm they pass when fixtures are in scope. That tells us whether the only failure is fixture scope or if there are behavioral failures too. Then decide: **Isolate behind temporary adapter** (e.g. conftest at tests/e2e that imports 3d fixtures) or **Freeze and document** (decide where e2e lives and document the contract).
