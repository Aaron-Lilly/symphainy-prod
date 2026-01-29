# Solution Contract Resolution: Strategic Recommendation

**Purpose:** Resolve the 10 documented contract/implementation mismatches (e2e + 3d probes) and establish a single source of truth to prevent drift. See [testing/stability_gravity_reports/20260129_e2e_contract_implementation_mismatch.md](../testing/stability_gravity_reports/20260129_e2e_contract_implementation_mismatch.md) and [20260129_next_probes_summary.md](../testing/stability_gravity_reports/20260129_next_probes_summary.md).

**Design choice:** Align with prior implementations (`symphainy_platform_old`, `symphainy_source` foundations): use a **concrete base class** (shared behavior, default implementations) and **typing.Protocol** for the contract—**no ABC** (no `@abstractmethod`). This matches:
- **symphainy_platform_old/realms/content**: `BaseContentHandler` is a concrete base (logger, clock, lazy services, `_index_artifact`); it inherits from ABC but has **no @abstractmethod**, so subclasses get behavior without forced overrides.
- **symphainy_platform_old/foundations/public_works**: Contracts are **typing.Protocol** (e.g. `FileParsingProtocol`, `StateManagementProtocol`); abstractions implement the protocol. Protocol = contract; base = shared implementation.

**Balance / discipline:** In the past, bases ballooned (1k+ lines), protocols drifted, and we got empty shells with "compliance complexity." We want a **balance** between that and "complete wild west." See **[SOLUTION_BASE_DISCIPLINE.md](./SOLUTION_BASE_DISCIPLINE.md)** for: **line cap** (solution_base.py under 250 lines; no compliance layers); **what NOT to add** (no lazy services in base, no validators/registries, no optional mixins); **protocol sync** (base is source of truth; Protocol is minimal subset updated in same PR, or drop Protocol and type-hint as BaseSolution only).

---

## 1. Strategic and Architectural Resolution of the 10 Mismatches

**Recommendation: Platform as single source of truth.** Formalize one contract (base class + SOLUTION_PATTERN.md), then bring all solutions, journeys, and tests into compliance. Do **not** align the platform to ad hoc “how developers want to build”; align developers and tests to the one contract so drift stops.

### 1.1 How Each Mismatch Is Resolved

| # | Mismatch | Resolution |
|---|----------|------------|
| 1 | **SecuritySolution has no get_journey / get_journeys** | All solutions MUST expose `get_journey(journey_id)` and `get_journeys()`. Enforce via **BaseSolution** (abstract or default impl). SecuritySolution (and any other) inherits from BaseSolution and implements or uses base defaults. |
| 2 | **E2E / tests expect action "get_stats"; journey expects "stats"** | **Single source of action names:** Document supported actions per journey in SOLUTION_PATTERN.md (or journey contract docs) and/or as constants on the journey class. Tests and frontend use those same names. Prefer short canonical names (e.g. `stats`) and document them; tests align. |
| 3 | **Result shape: test expects "success" in result; some journeys return no "success" on failure** | **Standard journey result shape:** Every journey `compose_journey` return MUST include: `success: bool`, `artifacts: dict`, `events: list`, `journey_id: str`, `journey_execution_id: str`. On failure, set `success: False` and put error details in `artifacts` or `events`. Provide a helper (e.g. on BaseSolution or a journey base) so all journeys build this shape. Tests and frontend assert on `success` and known keys. |
| 4 | **Experience SDK config: test expects top-level available_journeys; implementation has nested integration_patterns.journey_invocation.available_journeys** | **Standardize config shape:** Define the canonical shape in SOLUTION_PATTERN.md and in BaseSolution.get_experience_sdk_config(). Either (a) add top-level `available_journeys` for backward compatibility with tests/frontend, or (b) change tests/frontend to use the nested path. Recommendation: **(a)** — base class implementation includes both top-level `available_journeys` and nested for clarity; one source of truth in code, tests align. |
| 5 | **Operations journeys: required params (workflow_id, sop_id, etc.) not passed by tests** | **Required params as contract:** Each journey documents required `journey_params` (in journey contract doc or as schema on the journey class). BaseSolution or journey base can expose “required params” for validation. Tests use the same source (or fixture params) when invoking. Optionally: validate in journey and return standard result shape with `success: False` and error in artifacts when params missing. |
| 6 | **Security auth/registration: result on failure has no "success" key** | Same as #3: standard result shape. All journeys return the same shape; on failure `success: False`, error in artifacts/events. |
| 7 | **Tests call initialize_mcp_server() without await** | **Async contract:** SOLUTION_PATTERN.md and BaseSolution document that `initialize_mcp_server()` is async. Tests that call it MUST use `await` and be async (e.g. `@pytest.mark.asyncio`). No code change to solutions; test fix only. |
| 8–10 | (Content experience SDK config, Operations required params, Security result shape — same as above) | Covered by #3, #4, #5, #6. |

### 1.2 Implementation Order

1. **Introduce BaseSolution** and standard journey result shape helper (see below).
2. **Update SOLUTION_PATTERN.md** to reference BaseSolution and the standard result shape and config shape.
3. **Migrate solutions** to inherit from BaseSolution; add `get_journey` / `get_journeys` to SecuritySolution (and any other missing).
4. **Standardize journey returns:** Have each journey use the result-shape helper so every return includes `success`, `artifacts`, `events`, `journey_id`, `journey_execution_id`.
5. **Standardize get_experience_sdk_config:** Base implementation (or shared helper) that includes top-level `available_journeys` and nested structure; all solutions use it or override consistently.
6. **Fix tests:** Align action names, required params, and async usage to the contract; assert on standard result shape.

---

## 2. Single Source of Truth: Base Class + SOLUTION_PATTERN.md

**Recommendation: Both.** Use a **base class as the enforcement mechanism** and **SOLUTION_PATTERN.md as the human-facing contract** that references the base. The doc alone does not prevent drift; the base class does.

### 2.1 Why a Base Class (Concrete, Not ABC)

- **Enforcement:** All solutions inherit from **BaseSolution** (concrete base, no ABC). Methods like `get_journey` and `get_journeys` have **default implementations** that use `_journeys`; subclasses get the contract for free and override only when needed. No `@abstractmethod`—aligns with prior platform_old style (e.g. BaseContentHandler: concrete behavior, no forced overrides).
- **Single implementation:** Standard result shape and standard experience SDK config shape live in the base (e.g. `build_journey_result()`, default `get_experience_sdk_config()`), so one place defines “what a solution returns” and “what config looks like.”
- **Prior implementations:** symphainy_platform_old and symphainy_source used base classes rigorously for shared behavior (logger, clock, lazy services); foundations used **typing.Protocol** for contracts. Here we **drop Protocol** and type-hint as **BaseSolution** only—single source of truth, nothing to sync; pattern doc describes what the base enforces.

### 2.2 Why Keep SOLUTION_PATTERN.md

- **Onboarding and “how to add a solution”:** The doc remains the place for structure, examples, and step-by-step instructions. It should state: “All solutions MUST inherit from BaseSolution” and “Journey returns MUST use the standard result shape.”
- **Contract in one place:** The doc lists the required methods (get_journeys, get_journey, handle_intent, get_soa_apis, get_experience_sdk_config, initialize_mcp_server), the standard result shape, and the standard config shape. Code (base class) and doc stay in sync; the base is the source of truth for behavior, the doc for narrative and examples.

### 2.3 What to Create

1. **BaseSolution** (concrete, no ABC, no Protocol) in `symphainy_platform/bases/solution_base.py`. Type-hint as **BaseSolution** only—single source of truth.
   - **BaseSolution:** Concrete base. Default implementations: `get_journeys()` / `get_journey()` from `_journeys`; `get_experience_sdk_config()` building from `get_journeys()` and `get_soa_apis()` with **top-level `available_journeys`** and nested structure for backward compatibility. Subclasses set `_journeys` in `_initialize_journeys()` and override only what they need.
   - **Standard journey result shape:** Static or class method `build_journey_result(success, journey_id, journey_execution_id, artifacts, events) -> Dict` so all journeys can return the same shape (success, artifacts, events, journey_id, journey_execution_id).
2. **SOLUTION_PATTERN.md** updated to:
   - State that all solutions MUST inherit from `BaseSolution`; type-hint as BaseSolution.
   - Document the standard journey result shape (success, artifacts, events, journey_id, journey_execution_id).
   - Document that `initialize_mcp_server()` is async and must be awaited.
   - Reference `bases/solution_base.py` for the canonical method list and behavior.

### 2.4 Optional: Journey Base

A **BaseJourney** (or reuse of `BaseOrchestrator`) that enforces `compose_journey` return shape (via the helper above) and optional required-params validation would extend the single source of truth to journeys. Recommendation: add once BaseSolution and standard result shape are in place; journeys can then call the result-shape helper and, if desired, declare required params for validation.

---

## 3. Summary

- **Resolve the 10 mismatches** by making the platform the single source of truth: one contract (BaseSolution + standard result shape + SOLUTION_PATTERN.md), then align all solutions, journeys, and tests to it.
- **Single source of truth** = **BaseSolution** (concrete base, no ABC, no Protocol; type-hint as BaseSolution) + **SOLUTION_PATTERN.md** (human-facing contract). Update SOLUTION_PATTERN.md to reference the base and the standard result and config shapes. Migrate solutions to inherit from BaseSolution (e.g. SecuritySolution gets `get_journey`/`get_journeys` from base); fix tests to use correct action names, required params, and async usage.
- **Best practices (from prior codebases):** Concrete base for shared behavior; Protocol for interface contract; one canonical result shape and config shape in the base to prevent drift.
- **Discipline:** Lean base, no ballooning—see [SOLUTION_BASE_DISCIPLINE.md](./SOLUTION_BASE_DISCIPLINE.md). Base contains only what fixes the 10 mismatches; no compliance complexity.

---

## 4. What This Means for Solution Inconsistency and Existing Bases

### 4.1 Solution inconsistency (the 10 mismatches)

**Nothing changes.** The fix is the same:

- **BaseSolution** is the single source of truth (already created). All solutions must inherit from it so `get_journey`/`get_journeys` exist; standard result shape via `build_journey_result()`; standard config shape via default `get_experience_sdk_config()`.
- **Remaining work:** (1) **Migrate solutions** — SecuritySolution (and any other that doesn’t yet) inherit from BaseSolution. (2) **Standardize journey returns** — Each journey uses `BaseSolution.build_journey_result()` so every return has `success`, `artifacts`, `events`, `journey_id`, `journey_execution_id`. (3) **Fix tests** — Use correct action names (e.g. `stats` not `get_stats`), pass required params for operations journeys, `await` `initialize_mcp_server()`, assert on standard result shape.

Foundations embracing protocol/abstraction does **not** affect this. Solutions stay **base-class-as-contract** (BaseSolution); foundations stay **Protocol-as-contract** for capabilities.

### 4.2 Existing base classes (intent, orchestrator, agent, MCP server)

**Keep them as-is.** We already converted them to **concrete base, no ABC, no Protocol; type-hint as BaseX**:

| Base | Status | What to do |
|------|--------|------------|
| BaseIntentService | Concrete; subclass implements `execute` | Nothing; use as-is. |
| BaseOrchestrator | Concrete; subclass implements `compose_journey` | Nothing; use as-is. |
| AgentBase | Concrete; subclass implements `_process_with_assembled_prompt`, `get_agent_description` | Nothing; use as-is. |
| MCPServerBase | Concrete; subclass implements `initialize`, `get_usage_guide` (defaults: False, {}) | Nothing; use as-is. |

Do **not** introduce Protocols for these. The split is:

- **Foundations (capabilities):** Contract = **Protocol** (StateManagementProtocol, etc.); many abstractions implement it; FoundationService orchestrates. We embrace that.
- **Solutions, intent, orchestrator, agent, MCP server:** Contract = **base class** (BaseSolution, BaseIntentService, BaseOrchestrator, AgentBase, MCPServerBase). Single source of truth; type-hint as BaseX. No separate Protocol.

**RealmBase:** Unused in fabric—realms are solution + orchestrators + intent services; no XRealm(RealmBase) classes. Treat as legacy; no action.

### 4.3 Action list (solution fix)

1. **Migrate solutions** to inherit from BaseSolution (SecuritySolution and any other missing).
2. **Journey returns** — Use `BaseSolution.build_journey_result()` in each journey’s `compose_journey` return (or equivalent shape).
3. **Tests** — Align action names, required params, `await initialize_mcp_server()`, assert on `success` and standard keys.
4. **Docs** — SOLUTION_PATTERN.md already references BaseSolution and standard shapes; keep in sync as you migrate.
