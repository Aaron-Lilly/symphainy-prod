# Three-Layer Intent Model

**Status:** Canonical (January 2026)
**Authors:** Platform Architecture Team with C-Suite Alignment
**Purpose:** Define the fundamental intent classification that enables clean IP boundaries, reusable industry utilities, and infinite extensibility

---

## One-Sentence Summary

> **SymphAIny is the Intent-Driven Enterprise Operating System that transforms how organizations integrate, reason, and execute — using intent as the semantic kernel to modernize operations without rewrites and turn integration expertise into reusable products.**

---

## 1. The Core Realization

There are **three kinds of intent**, not two:

| Intent Type | Ownership | Purpose |
|-------------|-----------|---------|
| **Foundational Intents** | Platform-owned (Core IP) | Runtime mechanics |
| **Connective Intents** | Platform-owned, extensible (Product IP) | System integration & orchestration |
| **Domain Intents** | Client-owned, portable (Client IP) | Business logic & workflows |

**The key insight:** Integration patterns are NOT client differentiation. They are reusable connective tissue between enterprise systems. This is where the platform becomes **infrastructure** rather than tooling.

---

## 2. The Three-Layer Stack

```
┌────────────────────────────────────────────────────────────────┐
│                      DOMAIN INTENTS                            │
│                                                                │
│  • Claims workflows           • Policy servicing               │
│  • Underwriting rules         • Carrier-specific logic         │
│  • Business outcomes          • Operational processes          │
│                                                                │
│  Ownership: Client-Owned, Portable, Licensed                   │
│  IP Class: Client differentiation                              │
├────────────────────────────────────────────────────────────────┤
│                    CONNECTIVE INTENTS                          │
│                                                                │
│  • System adapters            • Migration pipelines            │
│  • Event normalization        • Schema mapping                 │
│  • Process choreography       • Legacy ingestion               │
│  • Dual-write orchestration   • Parallel-run governance        │
│                                                                │
│  Ownership: Platform-Owned, Extensible                         │
│  IP Class: Product IP — Industry Utility Infrastructure        │
├────────────────────────────────────────────────────────────────┤
│                 FOUNDATIONAL INTENT RUNTIME                    │
│                                                                │
│  • Intent language            • Execution engine               │
│  • Context resolution         • Governance                     │
│  • Security                   • Observability                  │
│  • Semantic compilation       • State management               │
│                                                                │
│  Ownership: Platform-Owned                                     │
│  IP Class: Core IP — The Operating System Kernel               │
└────────────────────────────────────────────────────────────────┘
```

---

## 3. Why This Model Resolves Previous Confusion

| Previous Confusion | How Three Layers Resolve It |
|-------------------|----------------------------|
| "Is this platform or client IP?" | It's CONNECTIVE IP — a third category |
| "Where do intents live?" | Wrong question. WHAT KIND of intent is it? |
| "Platform owns vs client owns" | Clean boundaries per layer |
| "How do we productize without IP bleed?" | Connective frameworks are reusable; implementations are client-specific |
| "Team A vs Team B responsibilities" | Team A = Foundational, Team B = Connective + Domain enablement |

---

## 4. IP Ownership Boundaries

### Platform Owns (SymphAIny IP)

**Foundational Layer:**
- Intent runtime and language
- Execution engine
- Governance and security
- Observability and state

**Connective Layer (Frameworks):**
- Integration pattern frameworks
- Migration choreography engines
- Event normalization frameworks
- Schema mapping infrastructure
- Industry reference connectors

### Partners Own (e.g., TPA IP)

**Connective Layer (Implementations):**
- System-specific adapters
- Vendor-specific mappings
- Deployment wiring
- Operational configurations

### Clients Own (e.g., Carrier IP)

**Domain Layer:**
- Business workflows
- Operational rules
- Domain-specific outcomes
- Competitive differentiators

---

## 5. The Platform as Semantic Control Plane

```
┌─────────────────────────────────────────────────────────────────┐
│                    SEMANTIC CONTROL PLANE                       │
│                         (SymphAIny)                             │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              INTENT RUNTIME (Foundational)               │   │
│  │  Intent Language → Execution Engine → State Management   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │         CONNECTIVE FRAMEWORKS (Product Surface)          │   │
│  │  Legacy Ingestion │ System Abstraction │ Migration       │   │
│  │  Event Normalization │ Process Choreography              │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              │                                  │
└──────────────────────────────┼──────────────────────────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│   TPA/VLP     │    │   AAR Client  │    │  PSO/Utility  │
│               │    │               │    │               │
│ • Adapters    │    │ • Adapters    │    │ • Adapters    │
│ • Mappings    │    │ • Mappings    │    │ • Mappings    │
│ • Workflows   │    │ • Workflows   │    │ • Workflows   │
└───────────────┘    └───────────────┘    └───────────────┘
```

---

## 6. Mapping to Platform SDK (ctx Services)

The Platform SDK becomes the **Intent Runtime + Connective Abstraction Layer**:

| ctx Service | Layer | Semantic Role |
|-------------|-------|---------------|
| `ctx.governance` | Foundational | Governance Semantics — policy, authority, trust |
| `ctx.reasoning` | Foundational | Reasoning Semantics — thinking, planning, decision |
| `ctx.interaction` | Foundational | Interaction Semantics — perception, conversation, presentation |
| `ctx.execution` | Foundational | Execution Semantics — compute, storage, orchestration |
| `ctx.enabling` | Connective | Intent Semantics — meaning, composition, control |

**The translation pattern:**

```python
# Instead of (low-level protocol):
smart_city_sdk.check_role("EmergencyManager")

# Intent sees (semantic primitive):
ctx.governance.assert_authority("EmergencyResponse")

# Instead of (low-level protocol):
agentic_sdk.spawn_agent(config)

# Intent sees (semantic primitive):
ctx.reasoning.delegate("damage_assessment")

# Instead of (low-level protocol):
runtime.execute_in_container(task)

# Intent sees (semantic primitive):
ctx.execution.schedule("data_ingest")
```

---

## 7. Mapping to Four Frameworks

The Four Frameworks represent **semantic output categories** that span the three intent layers:

| Framework | Primary Intent Layer | Semantic Role |
|-----------|---------------------|---------------|
| **Content** | Connective | System ingestion → Semantic normalization |
| **Insights** | Connective | Raw data → Semantic understanding |
| **Operations** | Connective + Domain | Process choreography + Business workflows |
| **Outcomes** | Domain | Business deliverables (client value) |

### Framework Delivery Model

| Framework | Delivery | Intent Layer |
|-----------|----------|--------------|
| **Content** | Fully functional (keys to castle) | Connective — platform owns |
| **Insights** | Fully functional (keys to castle) | Connective — platform owns |
| **Operations** | Demonstrative (teasers) | Connective frameworks + Domain implementation |
| **Outcomes** | Demonstrative (teasers) | Domain — client owns implementation |

---

## 8. Industry Utility: Connective Intent Packages

Because **Connective Intents are structurally reusable across entire industries**, the platform can productize:

### Life Insurance / TPA (VLP Demo)
- Legacy policy system ingestion
- Policy location abstraction
- Claims system normalization
- Migration orchestration (dual-write, parallel-run)
- Cutover choreography

### After Action Reports (AAR Demo)
- Incident data normalization
- Timeline reconstruction
- Multi-source correlation
- Lessons learned extraction
- Recommendation generation

### Permits / Utility (PSO Demo)
- Permit document extraction
- Field normalization
- Compliance mapping
- Workflow orchestration
- Status tracking

### Common Patterns (All Industries)
- Legacy system ingestion
- Schema mapping
- Event normalization
- Process choreography
- Migration orchestration

**This is the infrastructure moat.**

---

## 9. The Composition Model

```
SOLUTION (Productized meaning)
    │
    ├── JOURNEY (Orchestration logic)
    │       │
    │       ├── DOMAIN INTENT (Business logic)
    │       │       └── ctx.enabling.* (client-defined)
    │       │
    │       ├── CONNECTIVE INTENT (Integration)
    │       │       └── ctx.enabling.* (platform frameworks)
    │       │
    │       └── FOUNDATIONAL INTENT (Runtime)
    │               └── ctx.governance.*, ctx.reasoning.*, etc.
    │
    └── (Repeating journey pattern)
```

This mirrors Anthropic's GSD architecture:

| SymphAIny | Anthropic GSD |
|-----------|---------------|
| Solution | Goal / Outcome |
| Journey | Task Tree / Milestones |
| Intent | Atomic Task |

**This convergence validates the architecture.**

---

## 10. Team Responsibilities

| Team | Layer Ownership | Deliverables |
|------|-----------------|--------------|
| **Team A (Takeoff)** | Foundational | Protocols, runtime, boot, infrastructure |
| **Team B (Landing)** | Connective + Domain enablement | Frameworks, capability services, SDK surface |
| **Partners (e.g., TPA)** | Connective implementations | Adapters, mappings, configurations |
| **Clients (e.g., Carriers)** | Domain | Business workflows, operational rules |

---

## 11. Why This Will Stick

1. **The axis is stable** — "What kind of intent?" not "Where does it live?"
2. **IP boundaries are clean** — Platform owns frameworks, partners own implementations, clients own domain
3. **The product surface is clear** — Connective Intent Packages = industry utility
4. **It validates everything we built** — Four Frameworks map cleanly to three layers
5. **Infinite extensibility** — New industries = new Connective Intent Packages on same runtime

---

## 12. Implementation Status (January 2026)

### Foundational Layer ✅ Complete
- Platform SDK with ctx services
- Runtime (StateSurface, WAL, IntentRegistry, ExecutionLifecycleManager)
- Security (Auth, Sessions, Tenancy)
- Governance (Smart City roles and SDKs)

### Connective Layer ✅ Frameworks Complete
- Content Framework (ingestion, parsing, embedding)
- Insights Framework (analysis, quality, lineage)
- Coexistence (agent orchestration, process choreography)
- Operations Framework (workflow, SOP, migration patterns)

### Domain Layer ✅ Enablement Ready
- Outcomes Framework (blueprint, POC, roadmap generation)
- Demo implementations (VLP, AAR, PSO)
- Client composition surface ready

---

## 13. References

- [FOUR_FRAMEWORKS_ARCHITECTURE.md](FOUR_FRAMEWORKS_ARCHITECTURE.md) — Semantic output categories
- [PLATFORM_SDK_ARCHITECTURE.md](PLATFORM_SDK_ARCHITECTURE.md) — Intent runtime and ctx services
- [PLATFORM_VISION_RECONCILIATION.md](PLATFORM_VISION_RECONCILIATION.md) — Vision alignment
- [MEET_IN_THE_MIDDLE_PLAN.md](../MEET_IN_THE_MIDDLE_PLAN.md) — Team integration

---

## 14. The Final Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        SOLUTIONS                                │
│              (Productized meaning — client value)               │
├─────────────────────────────────────────────────────────────────┤
│                        JOURNEYS                                 │
│                   (Orchestration logic)                         │
├─────────────────────────────────────────────────────────────────┤
│                         INTENTS                                 │
│    Domain          │    Connective      │    Foundational       │
│  (Client IP)       │   (Product IP)     │     (Core IP)         │
├────────────────────┴────────────────────┴───────────────────────┤
│              PLATFORM SDK — SEMANTIC OS KERNEL                  │
│     ctx.governance │ ctx.reasoning │ ctx.interaction │          │
│     ctx.execution  │ ctx.enabling                               │
├─────────────────────────────────────────────────────────────────┤
│                     CIVIC PROTOCOLS                             │
│     Smart City  │  Agentic  │  Experience  │  Runtime           │
├─────────────────────────────────────────────────────────────────┤
│                   INFRASTRUCTURE LAYER                          │
│     (Public Works — adapters, abstractions, protocols)          │
└─────────────────────────────────────────────────────────────────┘
```

---

**SymphAIny is the Intent-Driven Enterprise Operating System that transforms how organizations integrate, reason, and execute — using intent as the semantic kernel to modernize operations without rewrites and turn integration expertise into reusable products.**
