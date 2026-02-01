# Public Works: Contract → Protocol → Abstraction → Adapter (CTA)

**Status:** REQUIRED for Platform V1.0  
**Purpose:** Single, enforceable pattern for every capability at the foundation boundary. No fallbacks for required capabilities; no adapter leak; no half measures.

**Related:** [GETTING_ON_TRACK_ASSESSMENT_AND_PLAN.md](../GETTING_ON_TRACK_ASSESSMENT_AND_PLAN.md), [INTERCEPT_ALIGNMENT_CONTRACT.md](../INTERCEPT_ALIGNMENT_CONTRACT.md), [PLATFORM_CONTRACT.md](PLATFORM_CONTRACT.md).

---

## 1. The Pattern (REQUIRED)

Every capability that crosses the Public Works boundary **shall** follow this stack:

| Layer | Role | Rule |
|-------|------|------|
| **Contract** | What the platform guarantees | Required capability = boot fails if missing. Optional = may return None; callers fail fast if they need it and it’s missing. No silent fallback for required. |
| **Protocol** | The type at the boundary | Boundary getter returns **only** a protocol type (e.g. StateManagementProtocol, FileStorageProtocol). Callers type against the protocol. |
| **Abstraction** | The implementation | Implements the protocol. Uses the adapter(s) internally. Never exposes the adapter to callers. |
| **Adapter** | The raw technology | Supabase, Redis, Arango, GCS, etc. Lives inside Public Works. **Never** returned from a boundary getter. Adapter getters raise or don’t exist. |

**Flow:** Caller → boundary getter → returns **protocol** → implementation is **abstraction** → abstraction uses **adapter**. Adapter never crosses the boundary.

---

## 2. Rules (No Fallbacks, No Half Measures)

1. **Required = fail at boot.** If the contract says a capability is required, then when the adapter or dependency is missing, Public Works `initialize()` **raises** with a clear, actionable error. We do **not** create Public Works with that getter returning None and “hope the caller handles it.”
2. **Optional = explicit.** Only capabilities explicitly marked **optional** in the contract may return None. Callers that need an optional capability **must** check and raise (e.g. RuntimeError with “Platform contract §8A”) if it’s missing. No “return empty and log” for required.
3. **No adapter at the boundary.** No getter returns an adapter. No `get_supabase_adapter()`, `get_redis_adapter()`, etc. that return the raw client. Those either **raise** (e.g. RuntimeError: “Adapters must not escape Public Works”) or are not part of the boundary.
4. **One protocol per capability.** Each boundary getter is typed to a single protocol. The abstraction implements that protocol. No “return Any” or “return Optional[SomeConcreteClass]” when a protocol exists.
5. **MVP drives required.** If an MVP use case needs a capability, that capability is **required** in the contract. We don’t mark it optional “so the demo can run without it.”

---

## 3. What “No Fallback” Means

- **Required getter:** Dependency (adapter, config) missing → **raise in `initialize()`** (or in the getter if lazy init). Do **not** return None, do **not** return empty list/dict, do **not** log and continue.
- **Optional getter:** Dependency missing → may return None. Caller must check; if caller needs it and it’s None, caller raises. Foundation does not “degrade” by returning a stub or empty result for a required capability.
- **Table or resource missing:** If the contract says “registry_entries table must exist for semantic profiles,” then when the abstraction needs that table and it doesn’t exist, the abstraction **fails** (or the getter that returns the abstraction is not built). We don’t “return [] and log” as the production path.

---

## 4. Relation to Other Docs

- **INTERCEPT_ALIGNMENT_CONTRACT** — Defines the Platform Boundary and protocol getters. CTA is the **implementation rule** for how Public Works satisfies that boundary.
- **PLATFORM_CONTRACT** — Defines required infra (Redis, Arango, Supabase, GCS, etc.) and “no optional infra at boot.” CTA ensures we don’t expose adapters and we don’t silently degrade when infra is missing.
- **GETTING_ON_TRACK_ASSESSMENT_AND_PLAN** — Uses CTA as the required pattern for the “get on track” pass: define contract, audit against it, fix gaps, probe, then Curator with schema first.

---

## 5. Audit Question

For every boundary getter in Public Works: “Does it follow CTA?”  
- Does it return a **protocol** type (not an adapter)?  
- Is it **required** or **optional** in the contract?  
- If required, does it **fail boot** when the dependency is missing (no fallback)?  
- Does the **abstraction** use the adapter and never expose it?  

If any answer is no, it’s a gap to fix before we say “Public Works contract satisfied.”
