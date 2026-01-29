# Platform Bases Discipline: Common Pattern

**Purpose:** Apply the same principle across all platform bases—**concrete base, no ABC, no Protocol; type-hint as BaseX**. Prevents ballooning, protocol drift, and compliance complexity. See [SOLUTION_BASE_DISCIPLINE.md](./SOLUTION_BASE_DISCIPLINE.md) for the solution-specific rules.

---

## 1. Common Pattern (All Bases)

| Principle | Apply to |
|-----------|----------|
| **No ABC** | BaseSolution, BaseIntentService, BaseOrchestrator, AgentBase, MCPServerBase (RealmBase unused in fabric) |
| **No Protocol** | Type-hint as the base class (e.g. BaseSolution, BaseIntentService). Single source of truth; nothing to sync. |
| **Concrete base** | Default implementations where possible; methods subclasses must implement raise NotImplementedError (or return safe default like {} / False). |
| **Lean** | Line cap per base. Only what fixes documented mismatches or provides shared behavior; no compliance layers. |
| **What NOT to add** | No lazy service initialization in base, no validators/registries in base, no optional mixins. New behavior goes in subclasses or docs. |

---

## 2. Platform Bases (Current)

| Base | Location | Subclass must implement |
|------|----------|-------------------------|
| BaseSolution | symphainy_platform/bases/solution_base.py | handle_intent, get_soa_apis; override _initialize_journeys, initialize_mcp_server as needed |
| BaseIntentService | symphainy_platform/bases/intent_service_base.py | execute |
| BaseOrchestrator | symphainy_platform/bases/orchestrator_base.py | compose_journey |
| AgentBase | symphainy_platform/civic_systems/agentic/agent_base.py | _process_with_assembled_prompt, get_agent_description |
| MCPServerBase | symphainy_platform/civic_systems/agentic/mcp_server_base.py | initialize, get_usage_guide (defaults: False, {}) |
| RealmBase | symphainy_platform/civic_systems/platform_sdk/realm_sdk.py | **Unused in fabric** — realms = solution + orchestrators + intent services; no XRealm(RealmBase). Legacy. |

When adding or changing a base: same PR updates the base and any doc that lists it; no separate Protocol.

---

## 3. References

- Solution-specific: [SOLUTION_BASE_DISCIPLINE.md](./SOLUTION_BASE_DISCIPLINE.md)
- Solution contract: [SOLUTION_CONTRACT_RESOLUTION.md](./SOLUTION_CONTRACT_RESOLUTION.md)
- Other bases / gaps: [PLATFORM_BASES_REVIEW.md](./PLATFORM_BASES_REVIEW.md)
