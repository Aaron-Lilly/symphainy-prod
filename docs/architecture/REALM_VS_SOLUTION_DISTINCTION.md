# Realm vs Solution (Platform Capability) Distinction

**Status:** Canonical  
**Last Updated:** January 27, 2026

---

## Overview

The Symphainy platform has a critical architectural distinction between **Realms** and **Solutions** that can cause confusion if not properly understood.

### Key Insight

> **Realms** produce artifacts that showcase or enable **Solutions**.  
> **Solutions** (platform capabilities) compose journeys and orchestrate execution.

---

## The Two Layers

### 1. Realms (Artifact Layer)

Realms are responsible for **creating and managing artifacts** - the tangible outputs that users work with.

| Realm | Artifacts Produced | Purpose |
|-------|-------------------|---------|
| **Content Realm** | Files, parsed documents, embeddings | Working materials for analysis |
| **Insights Realm** | Data quality reports, interpretations, lineage | Understanding of content |
| **Operations Realm** | SOPs, Workflows, Process optimizations | Operational artifacts |
| **Outcomes Realm** | Blueprints, Roadmaps, POC Proposals | Deliverable outcomes |

**Key Point:** Realm artifacts are *what users create and export* - they're the visible outputs of the platform.

### 2. Solutions (Platform Capability Layer)

Solutions are **platform capabilities** that compose journeys and orchestrate intent execution.

| Solution | Journeys Composed | Purpose |
|----------|-------------------|---------|
| **ContentSolution** | File upload, parsing, embedding | Handle content lifecycle |
| **InsightsSolution** | Data analysis, quality, lineage | Handle insights generation |
| **OperationsSolution** | SOP management, workflow creation | Handle operations |
| **OutcomesSolution** | Synthesis, roadmaps, POCs, blueprints | Handle outcome delivery |
| **SecuritySolution** | Authentication, sessions | Handle security |
| **ControlTower** | Platform monitoring, solution registry | Handle platform management |

**Key Point:** Solutions are *what the platform can do* - they're the operational capabilities.

---

## The Bridge: Outcomes → Solutions

The platform includes a powerful capability to **transform outcome artifacts into platform solutions**.

### User Journey

```
1. User generates Outcome Artifacts
   - Coexistence Blueprint
   - POC Proposal
   - Strategic Roadmap

2. User clicks "Create Platform Solution"
   - UI calls OutcomesAPIManager.createSolution()
   - Intent: create_solution
   - Parameters: { solution_source: "blueprint", source_id: "...", source_data: {...} }

3. CreateSolutionService processes the artifact
   - Extracts goals and constraints from artifact
   - Creates domain service bindings
   - Registers solution intents
   - Stores in Solution Registry

4. Solution appears in Control Tower
   - User can view registered solutions
   - Solutions can compose journeys
   - Solutions can be executed
```

### Why This Matters

This capability allows users to:

1. **Document their work** - Create blueprints, roadmaps, POCs
2. **Operationalize their work** - Turn documents into platform capabilities
3. **Scale their work** - Registered solutions can be reused and composed

---

## Operations Realm vs Journey (Platform Capability)

### Operations Realm

The **Operations Realm** creates and manages operational artifacts:
- SOPs (Standard Operating Procedures)
- Workflows (BPMN, visual diagrams)
- Process optimizations
- Coexistence analysis

These are *documents* that describe how things should work.

### Journey (Platform Capability)

A **Journey** is a platform capability that composes intents:
- Journeys define the sequence of intents to execute
- Journeys can be triggered by user actions or automation
- Journeys are registered in the platform and can be composed

### The Bridge: SOPs/Workflows → Platform Journeys

Similar to Outcomes → Solutions, the platform can:

1. Take a user-created SOP or Workflow
2. Parse it for structure and steps
3. Generate a platform Journey that executes those steps
4. Register the Journey for execution

**Note:** The coexistence blueprint capability has moved to OutcomesSolution since blueprints are strategic outcome artifacts.

---

## Frontend Naming

To avoid confusion, the frontend uses these conventions:

| Backend | Frontend API Manager | State Key |
|---------|---------------------|-----------|
| Operations Realm | `OperationsAPIManager` | `journey` |
| Outcomes Realm | `OutcomesAPIManager` | `outcomes` |
| Content Realm | `ContentAPIManager` | `content` |
| Insights Realm | `InsightsAPIManager` | `insights` |

**Why "journey" state key for Operations?**  
The internal state key `journey` is retained for backwards compatibility. It represents the Operations Realm data in PlatformStateProvider.

---

## UI Triggers

### Create Platform Solution (Outcomes → Solutions)

Located in: `Business Outcomes Pillar → Generated Artifacts Modal`

Each artifact tab (Blueprint, POC, Roadmap) has a "Create Platform Solution" button that:
1. Calls `OutcomesAPIManager.createSolution(source, sourceId, sourceData)`
2. Shows loading state during creation
3. On success, shows "View in Control Tower" link
4. Toast notification with Control Tower navigation

### View Platform Solutions

Located in: `Control Tower → Platform Journeys & Solutions Card`

The Control Tower displays:
- All registered Solutions with status
- Source artifact information
- Creation date
- Links to view solution details

---

## Architecture Alignment

This distinction aligns with the platform's core principles:

1. **Runtime owns execution** - Solutions are registered capabilities that Runtime can execute
2. **Intent-based architecture** - Solutions declare supported intents
3. **Public Works pattern** - Solutions use abstractions (Artifact Plane, Solution Registry)
4. **Working code only** - Solutions are functional, not stubs

---

## Summary

| Concept | Layer | What It Is | Example |
|---------|-------|------------|---------|
| **Realm** | Artifact | Produces outputs | Outcomes Realm creates blueprints |
| **Solution** | Capability | Composes journeys | OutcomesSolution orchestrates synthesis |
| **Artifact** | Output | User deliverable | Coexistence Blueprint document |
| **Journey** | Execution | Intent sequence | BlueprintCreationJourney |

**Remember:** Realms create artifacts. Solutions orchestrate execution. The platform bridges them.
