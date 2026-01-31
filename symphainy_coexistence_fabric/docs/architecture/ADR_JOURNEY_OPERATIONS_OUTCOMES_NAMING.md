# ADR: Journey Engine / Operations and Solution Synthesis / Outcomes Naming

**Status:** Accepted  
**Date:** January 29, 2026  
**Decision makers:** Platform Architecture Team

---

## Context

The platform has two key pairs of related concepts:
1. Workflow/SOP execution and the UI that manages it
2. Outcome generation and the UI that displays/manages outcomes

There has been confusion about which names refer to the **capability** (what the platform can do) versus the **experience** (how users interact with it).

This ADR locks the naming convention to prevent future confusion.

---

## Decision

### Capability vs Experience Naming

| Layer | Name | What It Is |
|-------|------|------------|
| **Capability** | **Journey Engine** | Execution system for workflows, SOPs, and sagas (DAG execution, WAL, state management) |
| **Experience** | **Operations** | UI/surface that observes and interacts with journey execution |
| **Capability** | **Solution Synthesis** | Computational generator of outcomes (roadmaps, POCs, blueprints) |
| **Experience** | **Outcomes** | UI/surface for viewing and managing generated outcomes |

### Definitions

#### Journey Engine (Capability)
- **What:** Execution system for multi-step workflows, SOPs, and sagas
- **Core functions:** DAG execution, saga management, WAL persistence, state transitions, workflow composition
- **Location:** `capabilities/journey_engine/` (target) or `realms/operations/intent_services/` (current)
- **Intent types:** `compose_journey`, `create_workflow`, `generate_sop`, `optimize_process`

#### Operations (Experience)
- **What:** User interface that observes and interacts with journey execution
- **Core functions:** Workflow management dashboard, SOP viewing, journey monitoring, process optimization UI
- **Location:** `experience/operations/` (target)
- **SDK operations:** `trigger_journey()`, `invoke_intent()`, `query_state()`, `subscribe()`
- **Relationship:** Operations is the "lens" into the Journey Engine capability

#### Solution Synthesis (Capability)
- **What:** Computational generator of outcomes — produces roadmaps, POCs, blueprints, and solution artifacts
- **Core functions:** Outcome synthesis, roadmap generation, POC creation, blueprint generation
- **Location:** `capabilities/solution_synthesis/` (target) or `realms/outcomes/intent_services/` (current)
- **Intent types:** `synthesize_outcome`, `generate_roadmap`, `create_poc`, `create_blueprint`

#### Outcomes (Experience)
- **What:** User interface for viewing and managing generated outcomes
- **Core functions:** Roadmap visualization, POC display, blueprint export, artifact management
- **Location:** `experience/outcomes/` (target)
- **SDK operations:** `trigger_journey()`, `invoke_intent()`, `query_state()`, `subscribe()`
- **Relationship:** Outcomes is the "lens" into the Solution Synthesis capability

---

## Current Mapping

| Current Module | Target Capability | Target Experience |
|----------------|-------------------|-------------------|
| `solutions/journey_solution/` | `capabilities/journey_engine/` | — |
| `solutions/operations_solution/` | `capabilities/journey_engine/` | `experience/operations/` |
| `realms/operations/intent_services/` | `capabilities/journey_engine/` | — |
| `solutions/outcomes_solution/` | `capabilities/solution_synthesis/` | `experience/outcomes/` |
| `realms/outcomes/intent_services/` | `capabilities/solution_synthesis/` | — |

---

## Rationale

1. **Prevents conflation:** Clearly separates what the platform *can do* (capability) from how users *see it* (experience).

2. **Supports multi-tenancy:** Different tenants or solutions can have different "Operations" experiences that all use the same Journey Engine capability.

3. **Enables white-labeling:** The experience layer can be customized (e.g., different branding) without touching the capability layer.

4. **Aligns with architecture:** Matches the three-way separation (Capabilities / Experience / Solutions) in [CANONICAL_PLATFORM_ARCHITECTURE.md](CANONICAL_PLATFORM_ARCHITECTURE.md).

---

## Consequences

### Must Do
- Use "Journey Engine" when referring to the workflow/SOP execution capability
- Use "Operations" when referring to the UI/experience that interacts with workflows
- Use "Solution Synthesis" when referring to the outcome generation capability
- Use "Outcomes" when referring to the UI/experience for outcome viewing

### Must Not
- Do not call the UI "Journey Engine UI" — it's "Operations"
- Do not call the capability "Operations Engine" — it's "Journey Engine"
- Do not call the UI "Solution Synthesis UI" — it's "Outcomes"
- Do not call the capability "Outcomes Engine" — it's "Solution Synthesis"

---

## References

- [CANONICAL_PLATFORM_ARCHITECTURE.md](CANONICAL_PLATFORM_ARCHITECTURE.md) — Three-way separation
- [solution_realm_refactoring_vision.md](../solution_realm_refactoring_vision.md) — Vision document
- [MIGRATION_MAP_CURRENT_TO_TARGET.md](MIGRATION_MAP_CURRENT_TO_TARGET.md) — Migration mapping

---

**Summary:**
- **Journey Engine** = capability (execution system)
- **Operations** = experience (UI lens into Journey Engine)
- **Solution Synthesis** = capability (outcome generator)
- **Outcomes** = experience (UI lens into Solution Synthesis)
