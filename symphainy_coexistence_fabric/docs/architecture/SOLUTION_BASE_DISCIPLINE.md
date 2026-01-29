# Solution Base Discipline: Lean Base, No Ballooning

**Purpose:** Prevent the pattern that bit us before—bases ballooning (1k+ lines), protocols drifting out of sync, and empty shells buried under "compliance complexity." We want a **balance**: enough structure to fix the 10 mismatches and stop drift, but **not** a second platform inside the base.

**References:** [SOLUTION_CONTRACT_RESOLUTION.md](./SOLUTION_CONTRACT_RESOLUTION.md), [SOLUTION_PATTERN.md](../../symphainy_platform/solutions/SOLUTION_PATTERN.md).

---

## 1. What Went Wrong Before

- **Bases ballooned** — 1k+ lines, lazy services, helpers for everything.
- **Protocols drifted** — Protocol said one thing, base did another; two sources of truth.
- **Compliance complexity** — Layers of "must implement X, validate Y, register Z" with empty shells and boilerplate; real behavior lived elsewhere.

We are **not** recreating that. The base exists to:

1. Fix the 10 documented mismatches (get_journey/get_journeys, standard result shape, config shape, async contract).
2. Give one place for "what a solution looks like" so tests and frontend can rely on it.
3. Stay **small and stable** so it never becomes a second platform.

---

## 2. The Balance

| Wild west (before base) | Over-engineered (past mistake) | **Target balance** |
|------------------------|--------------------------------|--------------------|
| No contract; drift; tests break | Fat base + protocol drift + compliance layers | **Lean base** + **minimal contract** + **no compliance layers** |
| Every solution does its own thing | Base does everything; subclasses are shells | Base does **only** what fixes the 10 mismatches; solutions own real behavior |
| No get_journey, no standard result shape | Protocol + base + validators + registries | **One source of truth** (base); protocol is optional and must stay in sync or be dropped |

**Principles:**

- **Lean base:** Only what’s needed for the 10 mismatches: `get_journeys`, `get_journey`, `build_journey_result`, default `get_experience_sdk_config`, and the async contract. No more.
- **Minimal contract:** Either type-hint as `BaseSolution` (single source of truth, nothing to sync) or keep a **tiny** Protocol that is a **strict subset** of what the base implements and is updated in the same PR as the base.
- **No compliance complexity:** No validators, registries, or "must implement X or fail at runtime" layers in the base. Subclasses implement `handle_intent` and `get_soa_apis`; the base does not add compliance machinery.

---

## 3. Hard Limits

### 3.1 Line cap

- **`solution_base.py` stays under 250 lines** (including comments and docstrings).
- If we need more: **move behavior to solutions or journeys**, or to a shared util module—**not** into the base.
- When adding a method, ask: "Does this directly fix one of the 10 mismatches?" If no, it doesn’t go in the base.

### 3.2 What NOT to add to the base

- **No lazy service initialization** (no `_file_parser_service`, `_embedding_service`, etc.). Solutions create and hold their own services.
- **No validation/registration layers** (no "register journey with platform," "validate contract at runtime"). Contract is "inherit and implement handle_intent/get_soa_apis."
- **No optional mixins or compliance helpers** beyond `build_journey_result` and the 5–6 methods we have. No "SolutionComplianceMixin" or similar.
- **No journey base in this file** — If we add a journey base later, it lives in its own small file with its own line cap; it does not expand the solution base.

### 3.3 No Protocol—type-hint as BaseSolution

- **We drop Protocol.** Type-hint as `BaseSolution` only. Single source of truth; nothing to sync.
- **No separate Protocol:** Any change to the base’s public surface must update the Protocol in the same PR, or we drop the Protocol and type-hint as `BaseSolution` only.
- **No extra methods in Protocol** that the base doesn’t implement. Protocol = "what callers use," not "what we might want someday."

---

## 4. What the base DOES contain (and only this)

| Item | Why |
|------|-----|
| `get_journeys()` / `get_journey(journey_id)` | Fixes mismatch #1 (e.g. SecuritySolution); single place for journey access. |
| `build_journey_result(...)` | Fixes mismatches #3, #6; standard result shape. |
| Default `get_experience_sdk_config()` with top-level `available_journeys` | Fixes mismatch #4; tests/frontend can rely on one shape. |
| `get_soa_apis()` default `{}`, `handle_intent` raises NotImplementedError | Contract shape without compliance machinery. |
| `initialize_mcp_server()` async, default `None` | Documents async contract; fixes mismatch #7 (tests use await). |
| Logger, clock, `_journeys`, `_initialize_journeys()` | Minimal shared state; no services. |

Anything else (required params for journeys, action name constants, etc.) lives in **SOLUTION_PATTERN.md** or in **journey/solution code**, not in the base.

---

## 5. When in doubt

- **"Should this go in the base?"** → Only if it directly fixes one of the 10 mismatches and keeps the file under the line cap. Otherwise: solution, journey, or doc.
- **"Protocol and base are drifting."** → Update both in one PR or remove the Protocol and use `BaseSolution` as the type.
- **"We need a new shared behavior."** → Prefer a **small util module** or **documentation in SOLUTION_PATTERN.md**; add to the base only if it’s the *only* way to fix a documented mismatch.

This keeps us between "complete wild west" and "1k-line base + protocol drift + compliance complexity."
