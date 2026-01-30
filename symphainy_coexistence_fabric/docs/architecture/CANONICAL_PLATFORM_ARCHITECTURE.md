# Canonical Platform Architecture

**Status:** Canonical (January 2026)  
**Purpose:** Single source of truth for platform structure, layer separation, and where new code goes.  
**Authority:** This document is authoritative for platform layout decisions. When in doubt, align here.

**References:**
- [PLATFORM_VISION_RECONCILIATION.md](../PLATFORM_VISION_RECONCILIATION.md) — Vision ↔ implementation mapping
- [updated_platform_vision.md](../updated_platform_vision.md) — CTO north star
- [solution_realm_refactoring_vision.md](../solution_realm_refactoring_vision.md) — Refactoring vision
- [BOOT_PHASES.md](BOOT_PHASES.md) — Boot sequence (Φ1–Φ4)
- [EXPERIENCE_SDK_CONTRACT.md](EXPERIENCE_SDK_CONTRACT.md) — Experience SDK boundary (adopted)
- [RUNTIME_CONTRACTS.md](RUNTIME_CONTRACTS.md) — Runtime participation contracts

**SDK Implementation:** `symphainy_platform/civic_systems/experience/sdk/experience_sdk.py`

---

## 1. The Three-Way Separation

The platform has three distinct architectural layers that **must not be conflated**:

| Layer | What It Is | What It Does | Where Code Lives |
|-------|-----------|--------------|------------------|
| **Capabilities** | What the platform *can do* | Execution primitives, domain logic, intent implementations | `capabilities/<name>/` |
| **Experience** | How users *touch* it | Product surfaces, UX, dashboards that consume the platform | `experience/<name>/` |
| **Solutions** | How value is *delivered* | Commercial packaging of journeys + experiences | `solutions/<name>/` |

### 1.1 Capabilities

Capabilities are the **Execution Plane** — the governed primitives that implement platform functionality.

**Examples:**
- `capabilities/content` — Content ingestion, parsing, embeddings
- `capabilities/insights` — Semantic interpretation, data quality, analysis
- `capabilities/journey_engine` — Workflow/SOP orchestration, saga execution
- `capabilities/solution_synthesis` — Outcome generation, roadmaps, POCs
- `capabilities/security` — Authentication, authorization, identity
- `capabilities/control_tower` — Platform introspection, governance, observability
- `capabilities/coexistence` — Human-AI collaboration, agent routing

**Rule:** Capabilities implement governed interfaces. They may access Public Works, State Surface, and foundations directly (they are below the SDK boundary).

### 1.2 Experience

Experiences are the **Solutions Plane** — how users and agents interact with the platform.

**Examples:**
- `experience/content` — Content pillar UI
- `experience/coexistence` — Landing page, guide agent, liaison agents
- `experience/operations` — Operations UI (lens into journey_engine capability)
- `experience/outcomes` — Outcomes UI (lens into solution_synthesis capability)
- `experience/control_tower` — Admin dashboard
- `experience/security` — Login, registration, account management

**Rule:** Experiences are **clients** of the runtime via the Experience SDK. They do NOT bootstrap the runtime. They do NOT access runtime internals, civic systems, or infrastructure directly.

### 1.3 Solutions

Solutions are commercial packaging — compositions of capabilities and experiences for specific domains.

**Examples:**
- `solutions/insurance_migration` — Insurance policy migration solution
- `solutions/energy_grid_modernization` — Energy grid solution

**Rule:** Solutions consume capabilities via governed interfaces. They do NOT implement new capabilities.

---

## 2. The SDK Boundary (Hard Platform Invariant)

This is a **hard platform invariant** that cannot be violated:

> **No solution, agent, MCP server, or experience may directly access runtime internals, civic systems, or infrastructure. All access must flow through the Experience SDK or governed capability interfaces.**

### 2.1 Layer Applicability

| Layer | Examples | Can Access Public Works / State Surface? |
|-------|----------|------------------------------------------|
| **Execution Plane / Capabilities** | Intent services (`realms/*/intent_services/`), journey engine, capability implementations | ✅ **Yes** — Below SDK boundary |
| **Solutions Plane / SDK Clients** | Solutions, experiences, agents, MCP servers | ❌ **No** — Must use Experience SDK only |

### 2.2 Rule of Thumb

- **Implements** a capability (Execution Plane) → May access foundations directly
- **Consumes** a capability (Solutions Plane) → Must access via Experience SDK

### 2.3 Experience SDK Operations

Experience surfaces use **only** these SDK operations:

| Operation | Purpose |
|-----------|---------|
| `query_state(session_id, tenant_id, execution_id?)` | Get session state, execution status |
| `invoke_intent(intent_type, parameters, ...)` | Submit an intent |
| `trigger_journey(journey_id, parameters, ...)` | Start a journey |
| `subscribe(execution_id, tenant_id)` | Follow execution progress |

**Forbidden for SDK clients:**
- Direct Runtime HTTP API calls
- RuntimeClient internals
- service_factory access
- Civic system internals (Smart City SDK, Data Steward, etc.)
- Public Works abstractions
- Infrastructure (GCS, Arango, Redis, Supabase)
- State Surface direct access

---

## 3. Canonical Folder Layout

```
symphainy_platform/
├── capabilities/                    # What platform CAN DO (Execution Plane)
│   ├── content/                     # Content ingestion, parsing, embeddings
│   ├── coexistence/                 # Human-AI collaboration, agent routing
│   ├── insights/                    # Semantic interpretation, analysis
│   ├── journey_engine/              # Workflow/SOP orchestration, saga execution
│   ├── solution_synthesis/          # Outcome generation, roadmaps, POCs
│   ├── security/                    # Authentication, authorization, identity
│   └── control_tower/               # Platform introspection, observability
│
├── experience/                      # How users TOUCH it (Solutions Plane clients)
│   ├── content/                     # Content pillar UI
│   ├── coexistence/                 # Landing, guide agent
│   ├── operations/                  # Lens into journey_engine
│   ├── outcomes/                    # Lens into solution_synthesis
│   ├── control_tower/               # Admin dashboard
│   └── security/                    # Login, registration
│
├── solutions/                       # How value is DELIVERED (commercial packaging)
│   ├── insurance_migration/
│   └── energy_grid_modernization/
│
├── realms/                          # [CURRENT] Intent service implementations
│   ├── content/intent_services/     # → capabilities/content
│   ├── coexistence/intent_services/ # → capabilities/coexistence
│   ├── insights/intent_services/    # → capabilities/insights
│   ├── operations/intent_services/  # → capabilities/journey_engine
│   ├── outcomes/intent_services/    # → capabilities/solution_synthesis
│   ├── security/intent_services/    # → capabilities/security
│   └── control_tower/intent_services/ # → capabilities/control_tower
│
├── runtime/                         # Runtime Plane (Takeoff owns)
│   ├── execution_lifecycle_manager.py
│   ├── intent_registry.py
│   ├── execution_context.py
│   ├── state_surface.py
│   ├── artifact_registry.py
│   └── wal.py
│
├── civic_systems/                   # Civic Systems (Takeoff owns)
│   ├── experience/sdk/              # Experience SDK
│   ├── smart_city/                  # Governance roles
│   ├── agentic/                     # Agent runtime
│   └── platform_sdk/                # Platform SDK
│
└── foundations/                     # Foundations (Takeoff owns)
    └── public_works/                # Infrastructure abstractions
```

---

## 4. Boot Phases (Φ1–Φ4)

Implementation uses **Φ1–Φ4** (per [BOOT_PHASES.md](BOOT_PHASES.md)). The vision's Φ5/Φ6 map as per [PLATFORM_VISION_RECONCILIATION.md](../PLATFORM_VISION_RECONCILIATION.md).

| Phase | Name | What Happens |
|-------|------|--------------|
| **Φ1** | Infra | Backing services reachable (Redis, Arango, Consul, Supabase, GCS, Meilisearch, DuckDB). Pre-boot validates connectivity. |
| **Φ2** | Config | Canonical config acquired. No env reads inside Public Works for platform infra. |
| **Φ3** | Runtime Graph Construction | Public Works, StateSurface, WAL, IntentRegistry, ExecutionLifecycleManager built. **Experience SDK surface is available.** |
| **Φ4** | Experience Attachment | Experience surfaces attach to the SDK (Operations UI, Outcomes UI, dashboards, portals). No-op stub acceptable until bound. |

### 4.1 Service Factory Registration

**Φ3 registers (Takeoff):**
- Capabilities (intent services)
- IntentRegistry
- Journey engine
- Solution synthesis engine
- Security
- Control tower

**Φ4 attaches (clients):**
- Experience surfaces
- Solutions
- Agents
- MCP servers
- Dashboards / portals

**Rule:** Service factory registers capabilities/intents in Φ3. Experience surfaces **attach** in Φ4 as SDK clients — they do NOT register in service_factory.

---

## 5. Naming Conventions

### 5.1 Capability vs Experience Lens

| Capability | Experience Lens | Relationship |
|------------|-----------------|--------------|
| `journey_engine` | `operations` | Operations UI is the "lens" into journey_engine capability |
| `solution_synthesis` | `outcomes` | Outcomes UI is the "lens" into solution_synthesis capability |
| `content` | `content` | Direct mapping |
| `insights` | `insights` | Direct mapping |
| `security` | `security` | Direct mapping |
| `control_tower` | `control_tower` | Direct mapping |
| `coexistence` | `coexistence` | Direct mapping |

### 5.2 Intent Type Naming

Intent types follow the pattern: `<action>_<noun>`

**Examples:**
- `ingest_file`, `parse_content`, `create_deterministic_embeddings`
- `generate_sop`, `create_workflow`, `optimize_process`
- `synthesize_outcome`, `generate_roadmap`, `create_poc`
- `authenticate_user`, `create_session`, `validate_authorization`

---

## 6. Current State vs Target State

### 6.1 Mapping Table

| Current Module | Target Capability | Target Experience | Migration Phase |
|----------------|-------------------|-------------------|-----------------|
| `realms/content/intent_services/` | `capabilities/content/` | `experience/content/` | Phase A (layout) |
| `realms/coexistence/intent_services/` | `capabilities/coexistence/` | `experience/coexistence/` | Phase A |
| `realms/insights/intent_services/` | `capabilities/insights/` | `experience/insights/` | Phase A |
| `realms/operations/intent_services/` | `capabilities/journey_engine/` | `experience/operations/` | Phase A |
| `realms/outcomes/intent_services/` | `capabilities/solution_synthesis/` | `experience/outcomes/` | Phase A |
| `realms/security/intent_services/` | `capabilities/security/` | `experience/security/` | Phase A |
| `realms/control_tower/intent_services/` | `capabilities/control_tower/` | `experience/control_tower/` | Phase A |
| `solutions/content_solution/` | — | `experience/content/` | Phase B |
| `solutions/operations_solution/` | — | `experience/operations/` | Phase B |
| `solutions/outcomes_solution/` | — | `experience/outcomes/` | Phase B |
| `solutions/journey_solution/` | `capabilities/journey_engine/` | — | Phase B |

### 6.2 Migration Phases

| Phase | Description | Code Changes |
|-------|-------------|--------------|
| **Phase A** | Create layout + READMEs | No code moves. Add `capabilities/` and `experience/` directories with documentation. |
| **Phase B** | Document references | READMEs reference existing `realms/` and `solutions/` implementations. |
| **Phase C** | Refactor registration | service_factory registers from `capabilities/` namespace. |
| **Phase D** | Move code | Actual code moves from `realms/` to `capabilities/`. |

**Current:** Phase A (additive structure only)

---

## 7. Platform Layout Decision (ADR)

### Decision

All new platform code must follow the three-way separation:
1. **Capability implementations** → `capabilities/<name>/`
2. **Experience surfaces** → `experience/<name>/`
3. **Solution packaging** → `solutions/<name>/`

### Rationale

- **Prevents conflation** of what platform can do vs how users touch it
- **Enables SDK boundary enforcement** — experiences are clients, not implementers
- **Supports multi-tenancy** — experiences can be customized per tenant/solution
- **Enables white-labeling** — swap experience without touching capabilities

### Consequences

- Existing `realms/` and `solutions/` folders remain until explicit migration
- New capabilities go in `capabilities/`
- New experiences go in `experience/`
- PRs that register "experience" in service_factory will be rejected

---

## 8. Authority Chain (When Docs Conflict)

Resolve conflicts in this order:

1. **Platform Vision** ([updated_platform_vision.md](../updated_platform_vision.md))
2. **INIT_ORDER_SPEC / BOOT_PHASES** (Φ1–Φ4)
3. **Experience SDK Contract** ([EXPERIENCE_SDK_CONTRACT.md](EXPERIENCE_SDK_CONTRACT.md))
4. **Runtime Contracts** ([RUNTIME_CONTRACTS.md](RUNTIME_CONTRACTS.md))

**Rule:** Executable truth (what code and boot spec do) **always wins** in short term. When divergent, **reconcile back** into the vision or contract. Do not leave conflicts unresolved.

---

## 9. Quick Reference

### What Goes Where

| I want to... | Put it in... | Access pattern |
|--------------|--------------|----------------|
| Implement a new intent | `capabilities/<name>/` or `realms/<name>/intent_services/` | Direct Public Works/State Surface |
| Build a new UI surface | `experience/<name>/` | Experience SDK only |
| Package for a customer | `solutions/<name>/` | Experience SDK only |
| Add a new agent | `civic_systems/agentic/agents/` + consume via Experience SDK | Experience SDK only |
| Add an MCP server | `solutions/<name>/mcp_server/` | Experience SDK only |

### Hard Rules

1. ❌ Experience surfaces do NOT call runtime internals
2. ❌ Solutions do NOT implement capabilities
3. ❌ Agents do NOT access infrastructure directly
4. ❌ MCP servers do NOT bypass Experience SDK
5. ✅ All SDK clients use query_state, invoke_intent, trigger_journey, subscribe

---

## Summary

- **Three layers:** Capabilities (what) / Experience (how users touch) / Solutions (packaging)
- **SDK boundary:** Hard invariant. Capabilities below, SDK clients above.
- **Boot:** Φ1–Φ4 (Infra → Config → Runtime Graph → Experience Attachment)
- **Service factory:** Registers capabilities in Φ3, not experience surfaces
- **Naming:** journey_engine (capability) ↔ operations (experience); solution_synthesis (capability) ↔ outcomes (experience)
- **Current state:** Additive only. Do not delete/rename existing code until explicit migration.

---

**Last Updated:** January 29, 2026  
**Owner:** Platform Architecture Team  
**Status:** Canonical
