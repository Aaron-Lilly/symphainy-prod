# Platform Vision Reconciliation

**Purpose:** Map [updated_platform_vision.md](updated_platform_vision.md) (north star) to current implementation and handoff so there is one coherent story. Use this doc when aligning boot, layers, lifecycle, and Team B instructions.

**Canonical reference:** This document is the canonical reference for Team B, boot work, and future platform expansion. When in doubt, align to this reconciliation and the authority chain in §8.

**References:** [updated_platform_vision.md](updated_platform_vision.md), [BOOT_PHASES.md](architecture/BOOT_PHASES.md), [INIT_ORDER_SPEC.md](architecture/INIT_ORDER_SPEC.md), [EXPERIENCE_SDK_CONTRACT.md](architecture/EXPERIENCE_SDK_CONTRACT.md), [HANDOFF_TO_TEAM_B.md](HANDOFF_TO_TEAM_B.md).

---

## 1. Boot phase mapping (Φ1–Φ6 ↔ Φ1–Φ4)

The vision describes **Φ1–Φ6**; our executable boot spec is **Φ1–Φ4** in BOOT_PHASES.md and INIT_ORDER_SPEC.md. Treat the table below as the single mapping. **Implementation order is always Φ1–Φ4**; the vision’s Φ5/Φ6 are either folded in or gated by capability level.

| Vision (Φ1–Φ6) | Implementation (Φ1–Φ4) | Notes |
|-----------------|-------------------------|--------|
| **Φ1 — Substrate Initialization** (hardware, network, OS, container, storage mounts) | **Φ1 — Infra** | Backing services reachable (Redis, Arango, Consul, Supabase, GCS, Meilisearch, DuckDB). Pre-boot validates connectivity. |
| **Φ2 — Foundation Bring-up** (Public Works, State, WAL, Registry, Identity) | **Φ2 — Config** + start of **Φ3** | Config acquired; Public Works, StateSurface, WAL, IntentRegistry built in Φ3 per INIT_ORDER_SPEC. |
| **Φ3 — Civic Systems Activation** (governance, agentic, Experience SDK, Platform SDK) | **Φ3 — Runtime Graph Construction** | Civic systems and Experience SDK surface are available when runtime graph is built. Experience service exposes SDK. |
| **Φ4 — Execution Plane Initialization** (intent engine, journey orchestration, capability registry) | **Φ3 — Runtime Graph Construction** | IntentRegistry, ExecutionLifecycleManager, journey execution are part of the same runtime graph (INIT_ORDER_SPEC). |
| **Φ5 — Solution Attachment** (solution loading, MCP, agent topology, experience binding) | **Φ4 — Experience attachment** | Experience surfaces (and solutions/agents) attach to the SDK here. No-op stub acceptable until bound. |
| **Φ6 — Operational Validation** (health checks, policy, observability, **shutdown & recovery**, **startup integrity**) | **Φ6-equivalent: lifecycle governance** | See §2 below. MVP: pre-boot + basic health. Enterprise: full graceful shutdown, crash recovery, startup integrity checks (feature-flagged). |

**Rule:** For startup sequence and Team B, **canonical source is BOOT_PHASES.md and INIT_ORDER_SPEC.md (Φ1–Φ4)**. When the vision mentions Φ5 or Φ6, interpret via this table; do not introduce a second boot sequence.

---

## 2. Shutdown, crash recovery, and startup integrity (Φ6 / lifecycle)

The vision calls out **Shutdown & Recovery** and **Startup Integrity Checks** as part of lifecycle governance. These map to a **Φ6-equivalent** behavior set. They are **gated by capability level**: MVP does not require full implementation; Enterprise does.

### 2.1 Behaviors (from vision)

**Graceful shutdown**

- Drain active execution  
- Persist WAL  
- Checkpoint state  
- Release infrastructure safely  

**Crash recovery**

- Replay WAL  
- Validate state integrity  
- Resume execution  
- Reconcile partial workflows  

**Startup integrity checks**

- Last shutdown status  
- State consistency  
- Zombie resource cleanup  
- Orphaned job recovery  

### 2.2 Capability level (MVP vs Enterprise)

| Behavior | MVP | Enterprise |
|----------|-----|------------|
| **Graceful shutdown** | Process exits; in-flight work may be interrupted. WAL and state are persisted where already implemented; no formal drain protocol. | Drain active execution, persist WAL, checkpoint state, release infrastructure safely (documented protocol + code path). |
| **Crash recovery** | Restart process; WAL exists for audit. No mandatory replay/validate/resume/reconcile on startup. | On startup after unclean exit: replay WAL, validate state integrity, resume execution, reconcile partial workflows (documented protocol + code path). |
| **Startup integrity checks** | Pre-boot (G3) validates backing services. No mandatory last-shutdown or zombie/orphan cleanup. | Before accepting work: last shutdown status, state consistency check, zombie resource cleanup, orphaned job recovery (documented protocol + code path). |

### 2.3 Platform lifecycle hooks (required in MVP)

Even in MVP, **platform lifecycle hooks must exist as no-ops** so Enterprise behaviors can be added without refactoring control flow. The following hooks are part of the platform contract:

| Hook | When invoked | MVP | Enterprise |
|------|----------------|-----|------------|
| `startup_begin` | Before Φ1 / substrate init | No-op | Optional: telemetry, pre-flight |
| `startup_complete` | After Φ4 / experience attachment | No-op | Optional: readiness declaration, health registration |
| `shutdown_begin` | On graceful shutdown request | No-op | Drain active execution, persist WAL, checkpoint state |
| `shutdown_complete` | After infrastructure released | No-op | Optional: finalize WAL, release resources |
| `crash_detected` | On unhandled exception / unclean exit path | No-op | Optional: mark state for recovery, trigger recovery path |

**Rule:** Implement these five hooks in the boot/lifecycle path with no-op bodies in MVP. When raising to Enterprise, replace no-ops with real behavior; do not add new hook points or refactor control flow.

### 2.4 Implementation stance

- **MVP:** Pre-boot (G3), runtime graph build (Φ3), experience attachment (Φ4). Lifecycle hooks exist as no-ops (§2.3). No requirement to implement full graceful shutdown, crash recovery, or startup integrity checks.
- **Enterprise:** When `PLATFORM_CAPABILITY_LEVEL=Enterprise` (or equivalent), the platform must implement the protocols in §2.1 (or a documented subset) via the same hooks. Design and implementation can be phased.
- **Documentation:** The target behavior is documented here and in the vision; implementation is tracked in backlog or ADRs. Team B is **not** required to implement these for the handoff; Takeoff owns lifecycle governance and may implement when moving to Enterprise.

---

## 3. Terminology: vision ↔ current implementation

Use this mapping so the vision and handoff/docs speak the same language.

| Vision term | Current implementation term | Where it lives |
|-------------|-----------------------------|----------------|
| **Solutions Plane** (experiences, agents, MCP servers) | **Experience surfaces** (UX, dashboards, portals) + **solutions** (packaging) + agents/MCP that consume the platform | experience/, solutions/; clients of Experience SDK |
| **Execution Plane** (intents, journeys, capabilities) | **Runtime graph**: IntentRegistry, ExecutionLifecycleManager, State Surface, WAL, capability execution | Runtime; INIT_ORDER_SPEC |
| **Civic Systems** (Agentic, Experience SDK, Governance) | **Experience Civic System** (Experience SDK), **Smart City** (Security Guard, Traffic Cop, etc.), agentic runtime | civic_systems/experience (SDK), smart_city, agentic |
| **Foundations** (Public Works, Curator, State, Identity) | **Public Works**, **State Surface + WAL**, **registry_abstraction** (+ IntentRegistry, realm_registry), **Identity/Auth** | Public Works, state_surface, wal, registry, auth |
| **Capabilities** (what platform can do) | **capabilities/** (content, coexistence, insights, journey_engine, solution_synthesis, security, control_tower) | capabilities/; intent implementations |
| **Experience** (how users touch it) | **experience/** (content, coexistence, operations, outcomes, control_tower, security) | experience/; clients of Experience SDK |
| **Solutions** (packaging) | **solutions/** (e.g. insurance_migration, energy_grid_modernization) | solutions/ |

**Curator:** In the vision, Curator is “platform registry & metadata authority” (capability registry, policy registry, schema registry, runtime configuration registry). **In current implementation:** Curator is **not** a new service. It is the **umbrella name** for existing registry and config responsibilities: registry_abstraction, IntentRegistry, realm_registry, config loaders, and (where applicable) policy/schema registries. No separate “Curator” component is required unless we explicitly add one later.

---

## 4. Experience SDK boundary (hard platform invariant)

This is a **hard platform invariant**:

**No solution, agent, MCP server, or experience may directly access runtime internals, civic systems, or infrastructure. All access must flow through the Experience SDK or governed capability interfaces.**

Concretely:

- **Experience SDK** is the **contract boundary** between platform core and experience/solutions. Experience surfaces, solutions, agents, and MCP servers **consume only** the Experience SDK (query_state, invoke_intent, trigger_journey, subscribe) or other **governed capability interfaces** exposed by the platform. They do **not** call the Runtime API, civic internals, Public Works, or infrastructure directly.
- **Takeoff** owns the Experience SDK implementation and the Experience service that exposes it.
- **Team B (Landing)** builds experiences and capabilities that **use** the SDK and implement intent contracts; they do **not** change the civic system or the Runtime contract, and they do **not** bypass the SDK or governed interfaces.

When docs or code conflict with this rule, the invariant wins: executable truth must be reconciled so that no solution, agent, MCP server, or experience holds direct references to runtime internals, civic systems, or infrastructure. Full contract: [EXPERIENCE_SDK_CONTRACT.md](architecture/EXPERIENCE_SDK_CONTRACT.md). Handoff: [HANDOFF_TO_TEAM_B.md](HANDOFF_TO_TEAM_B.md).

---

## 5. Progressive capability flags (MVP / Enterprise / Future)

The vision’s capability matrix is adopted with one addition: **lifecycle (shutdown, recovery, integrity)** is Enterprise-gated as in §2.

| Capability | MVP | Enterprise | Future |
|-------------|-----|------------|--------|
| Policy enforced / governance enforcement | ✓ | ✓ | ✓ (deferred where noted) |
| Fine-grained auditing | ✗ | ✓ | ✓ |
| Auto-healing | ✗ | ✗ | ✓ |
| Regulatory compliance | ✗ | ✗ | ✓ |
| **Graceful shutdown** (drain, persist WAL, checkpoint, release) | ✗ | ✓ | ✓ |
| **Crash recovery** (replay WAL, validate, resume, reconcile) | ✗ | ✓ | ✓ |
| **Startup integrity checks** (last shutdown, consistency, zombie/orphan cleanup) | ✗ | ✓ | ✓ |

**Mechanism:** Use a single capability level (e.g. `PLATFORM_CAPABILITY_LEVEL=MVP|Enterprise|Future`) or equivalent feature flags. When adding or changing a subsystem, document its MVP vs Enterprise vs Future behavior and gate accordingly. MVP remains the default until explicitly raised.

---

## 6. Current state vs target (additive rule)

- **Target:** Layout and behavior described in the vision and in solution_realm_refactoring_vision (capabilities/, experience/, solutions/).
- **Current state:** Existing symphainy_platform/solutions, realms, and runtime remain in place.
- **Rule:** Add new structure (capabilities/, experience/) **alongside** existing code. Do **not** delete or rename existing solutions/realms until an explicit migration phase. Team B follows this rule per LANDING_AGENT_TASKS.

---

## 7. Where to look for what

| Need | Document |
|------|----------|
| High-level vision, principles, scaffold, reassembly protocol | updated_platform_vision.md |
| Boot sequence (what actually runs) | BOOT_PHASES.md, INIT_ORDER_SPEC.md (Φ1–Φ4) |
| Shutdown, recovery, integrity (Φ6) and MVP vs Enterprise | This doc (§2, §5) |
| Lifecycle hooks (no-ops in MVP) | This doc (§2.3) |
| Experience SDK contract | EXPERIENCE_SDK_CONTRACT.md |
| Runtime contracts for intents | RUNTIME_CONTRACTS.md |
| What Team B does and receives | HANDOFF_TO_TEAM_B.md, LANDING_AGENT_TASKS.md |
| Mapping vision ↔ implementation | This doc |
| When docs conflict (authority order) | This doc (§8) |

---

## 8. Architectural authority chain

When docs conflict, use this order to resolve:

1. **Platform Vision** ([updated_platform_vision.md](updated_platform_vision.md)) — north star and principles.
2. **INIT_ORDER_SPEC / BOOT_PHASES** — executable boot and lifecycle (Φ1–Φ4).
3. **Experience SDK Contract** ([EXPERIENCE_SDK_CONTRACT.md](architecture/EXPERIENCE_SDK_CONTRACT.md)) — boundary and operations.
4. **Runtime Contracts** ([RUNTIME_CONTRACTS.md](architecture/RUNTIME_CONTRACTS.md)) — intent registration, execution, state, artifacts.

**Rule:** Executable truth (what the code and boot spec do) **always wins** in the short term. When executable truth diverges from the vision or a contract, it must be **reconciled back** into the vision or the relevant doc (e.g. update the vision, or change the code to match the contract). Do not leave conflicts unresolved; use this reconciliation doc and the authority chain to decide and then update the losing side.

---

## Summary

- **Boot:** Implementation uses **Φ1–Φ4** (BOOT_PHASES, INIT_ORDER_SPEC). Vision Φ5/Φ6 map as in §1; Φ6 lifecycle (shutdown, recovery, integrity) is **Enterprise**-gated (§2, §5).
- **Lifecycle:** In MVP, **lifecycle hooks** (startup_begin, startup_complete, shutdown_begin, shutdown_complete, crash_detected) **must exist as no-ops** (§2.3). Full graceful shutdown, crash recovery, and startup integrity checks are **Enterprise** (feature-flagged).
- **Terms:** Solutions Plane / Execution Plane / Curator map to current layers and existing registries (§3).
- **Experience SDK boundary:** **Hard invariant** — no solution, agent, MCP server, or experience may directly access runtime internals, civic systems, or infrastructure; all access via Experience SDK or governed capability interfaces (§4).
- **Authority chain:** When docs conflict: Platform Vision → INIT_ORDER_SPEC / BOOT_PHASES → Experience SDK Contract → Runtime Contracts. Executable truth wins; reconcile back into the vision (§8).
- **Flags:** One capability matrix including lifecycle; one mechanism (e.g. PLATFORM_CAPABILITY_LEVEL); MVP default (§5).
