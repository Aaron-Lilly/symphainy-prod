# Platform Bases Review: What Else Do We Need?

**Purpose:** Review the rest of the platform for (1) other bases we might need (foundation_services, mcp_client_base, civic_system_base, SDK base?) and (2) non-base standardization (things that aren't services but need a common shape).

---

## 1. Other Bases We Might Need

### 1.1 Foundation services

- **Prior implementations:** We copied foundations from symphainy_platform_old (and that from symphainy_source). In the code we have:
  - **PublicWorksFoundationService**, **CuratorFoundationService** — concrete classes, no shared base.
  - In archive_v1 (symphainy_source): **AgentFoundationService**, **SmartCityFoundationService**, realm-level **XRealmFoundationService** — all concrete, no inheritance from a BaseFoundationService.
  So there is **no literal BaseFoundationService** in those codebases; the pattern was **naming** (XFoundationService) and **lifecycle** (initialize, optional shutdown), not a shared base class. If a base existed, it was in an earlier version not in this repo.

- **Current fabric:** Foundations = **PublicWorksFoundationService** (orchestrates adapters/abstractions), **CuratorFoundationService** (orchestrates registries). Public Works uses **typing.Protocol** for capability contracts (StateManagementProtocol, FileStorageProtocol, etc.) and **Abstractions** that implement those protocols; the foundation service exposes **get_X_abstraction()** returning the Protocol type.

- **Embrace protocol/abstraction:** Yes. The platform **naturally evolved** so that:
  - **Capability contract** = **Protocol** (typing.Protocol)
  - **Capability implementation** = **Abstraction** (implements Protocol)
  - **Orchestrator** = **FoundationService** (PublicWorks, Curator) — composes adapters/abstractions, exposes get_X_abstraction()
  We **embrace** that. The “base” for capabilities is the **Protocol**; the “base” for the orchestrator is the **FoundationService** class that holds and exposes them. No need to replace protocol/abstraction with a single fat base.

- **Optional BaseFoundationService:** If we want **type-hint consistency** with other platform bases (BaseSolution, BaseIntentService, etc.), we can add a **minimal BaseFoundationService** (concrete, no ABC, no Protocol) that **PublicWorksFoundationService** and **CuratorFoundationService** inherit from: logger, optional `async initialize() -> bool`. That would be for the **orchestrator** only; the protocol/abstraction pattern for capabilities stays as-is. Same discipline: lean base, no ballooning.

### 1.2 MCP client base

- **Current:** `MCPClientManager` in `civic_systems/agentic/mcp_client_manager.py` is a single concrete class—discovers servers, executes tools, manages connections. No MCPClientBase.
- **Recommendation:** **No MCPClientBase** unless we have multiple client implementations (e.g. different transports or backends) that need a shared contract. If we do, apply same principle: concrete base, no ABC, no Protocol; type-hint as BaseX. For now, MCPClientManager is sufficient.

### 1.3 Civic system base

- **Current:** Civic systems are `agentic`, `artifact_plane`, `experience`, `orchestrator_health`, `platform_sdk`, `smart_city`. They don't share a single base class; they use AgentBase, MCPServerBase, SDKs, etc. (RealmBase is unused in fabric.)
- **Recommendation:** **No CivicSystemBase.** "Civic system" is an organizational bucket, not a single runtime contract. The contracts we need are already covered by BaseSolution, AgentBase, MCPServerBase. Adding a CivicSystemBase would be a compliance layer without a clear fix for a documented mismatch.

### 1.4 SDK base

- **Current:** SDKs live under `civic_systems/smart_city/sdk/` (NurseSDK, CuratorSDK, etc.) and `civic_systems/platform_sdk/` (realm_sdk, solution_builder, solution_model). They are thin wrappers over abstractions; no shared base.
- **Recommendation:** **No SDK base** unless we see drift (e.g. some SDKs async, some sync; inconsistent method names). If we do, standardize via **docs + a minimal base** (e.g. "SDKs expose get_X_abstraction() and optional async initialize()")—again, concrete base, no ABC, no Protocol. Do not add preemptively.

### 1.5 RealmBase (platform_sdk/realm_sdk.py) — **Unused in fabric**

- **Current:** `RealmBase(ABC)` with `@abstractmethod declare_intents()`, `handle_intent()`. In **platform_old** we had ContentRealm(RealmBase), InsightsRealm(RealmBase), etc. In the **fabric** there are **no** realm classes that inherit from RealmBase. Realms in fabric = **solution + orchestrators + intent services** (folder structure and wiring only). RealmRegistry still types `register_realm(realm: RealmBase)` but nothing in fabric ever registers a RealmBase instance.
- **Recommendation:** **Treat as legacy/unused.** Do not convert to concrete or add to the "platform bases" list. Optionally deprecate RealmBase and RealmRegistry's RealmBase dependency, or leave as-is for the developer-view example (MyRealm) and possible future use. No action required for the current architecture.

---

## 2. Non-Base Standardization (Not Services)

Not everything is a "base class." Some things need a **common shape** without a base:

### 2.1 Config shapes

- **Experience SDK config:** Already standardized in BaseSolution.get_experience_sdk_config() (top-level `available_journeys`, nested `integration_patterns`). Document in SOLUTION_PATTERN.md; tests/frontend assert on that shape.
- **Other configs:** If we add more (e.g. agent config, MCP server config), define the shape in a **doc or schema** (e.g. CONFIG_SHAPES.md or JSON Schema) and have code/builders produce that shape. No need for a "ConfigBase" class unless we have many config builders sharing logic.

### 2.2 Result shapes

- **Journey result:** Standard shape (success, artifacts, events, journey_id, journey_execution_id) via BaseSolution.build_journey_result(). Document in SOLUTION_PATTERN.md.
- **Intent execution result:** If we want a standard intent result shape across intent services, define it in a doc and optionally a small helper (e.g. build_intent_result()) in BaseIntentService or a util module—not a whole new base.

### 2.3 Action names / constants

- **Journey actions:** Document supported actions per journey in SOLUTION_PATTERN.md or journey contract docs; optionally as constants on the journey class. Tests and frontend use those same names. No base needed.
- **Intent types:** Already declared per solution (SUPPORTED_INTENTS). No additional base.

### 2.4 Contracts in docs only

- **When to use doc-only contract:** When the "contract" is a small set of conventions (e.g. "all MCP tools accept user_context in params") or shapes (e.g. "health status returns status, service_name, tools"). Put in a **PATTERN.md or CONVENTIONS.md**; reference from code comments. Add a base or helper only when we have repeated code or a documented mismatch that a base would fix.

---

## 3. Summary

| Question | Answer |
|----------|--------|
| Foundation base? | **Embrace** protocol/abstraction for capabilities (Protocol = contract, Abstraction = impl, FoundationService = orchestrator). Optional: add minimal **BaseFoundationService** for PublicWorks/Curator orchestrators if we want type-hint consistency (logger, initialize). |
| MCP client base? | No, unless we have multiple client implementations. |
| Civic system base? | No; organizational bucket; existing bases cover contracts. |
| SDK base? | No, unless we see drift; then minimal base + docs. |
| RealmBase? | **Unused in fabric.** Realms = solution + orchestrators + intent services; no XRealm(RealmBase). Treat as legacy; optional deprecate. |
| Non-base standardization? | Config shapes, result shapes, action names, conventions in **docs** (and helpers like build_journey_result); add base only when it fixes a documented mismatch. |

**Principle:** Add a base only when it fixes a concrete problem or gives type-hint/lifecycle consistency. **Foundations:** We embrace the evolution to protocol/abstraction for capabilities; the orchestrator (FoundationService) can optionally share a minimal base with other platform bases.
