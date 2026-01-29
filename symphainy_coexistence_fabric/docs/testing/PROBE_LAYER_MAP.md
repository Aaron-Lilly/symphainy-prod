# Probe Layer Map: How the Platform Really Works

**Principle:** Every component needs a **clearly explainable purpose** and we must **know how it really works**—not assume, not wish. Probes trace and document; their output fills reality maps. Layer 1 (entry/exit, config, order/restart) is done; this map extends the same discovery to the rest of the platform.

**Run order:** Follow dependency order. Foundation layers first, then civic, then realms/runtime/solutions, then utilities.

---

## Layer 0: Lock platform behavior *(done)*

- **Probes:** probe_01 (entry/exit), probe_02 (config), probe_03 (order/restart).
- **Artifact:** [PLATFORM_OPERATION_MAP.md](PLATFORM_OPERATION_MAP.md) §1–§5.
- **Certainty:** Entry point, boot order, first request path, config contracts, order/restart failure modes.

---

## Foundations

### Public Works (foundations/public_works)

**Claimed purpose:** Infrastructure capabilities for all platform components; 5-layer architecture (adapters → abstractions → protocols).

**What we need to know (probe questions):**
- What are our **adapters** actually doing? Which are wired at boot? Which are used on first request vs never?
- How does the **5-layer pattern** actually work in code? (Layer 0 adapters, Layer 1 abstractions, Layer 2 protocols, Layer 3 …, Layer 4 foundation service.)
- Is it as “magical” as we think—or are some layers empty, duplicated, or bypassed?
- Who **calls** PublicWorks? What methods are invoked in a typical boot and first request?

**Probe artifact:** *Public Works Reality Map* — adapters (list, wired?, used?), 5-layer flow (evidence), callers and call sites.

**Probe:** probe_04_public_works (trace adapters, abstractions, protocols; trace callers; record what’s actually used).

---

### Curator – Foundation (foundations/curator)

**Claimed purpose:** Platform-wide registries (services, agents, tools, SOA APIs, capabilities). “Curator is NOT execution—it’s the platform’s capability ontology.”

**What we need to know (probe questions):**
- What is the **foundation Curator** actually curating? Which registries are populated, when, and by whom?
- Is **anyone** listening? Who reads from these registries at runtime?
- Is the foundation Curator **used at all** in the current boot path, or only the Smart City Curator?

**Probe artifact:** *Curator (Foundation) Reality Map* — registries (populated by whom, when), readers (who calls get/list), evidence from code and optional runtime trace.

**Probe:** probe_05_curator_foundation (trace registry writes and reads; list callers of CuratorFoundationService if any).

---

## Civic Systems

### Smart City (civic_systems/smart_city)

**Claimed purpose:** Primitives (low-level ops) and managers/SDKs (Security Guard, Traffic Cop, Curator, etc.); curator role here vs foundation.

**What we need to know (probe questions):**
- **Primitives vs managers:** What are primitives actually doing? What are the SDKs wrapping? Who calls which?
- **Curator role here vs foundation:** Is Smart City Curator the one that’s actually used (e.g. by Guide Agent for MCP tools)? How does it relate to foundations/curator?
- Which Smart City **SDKs** are wired into Experience/runtime? (Security Guard, Traffic Cop, Curator, etc.)

**Probe artifact:** *Smart City Reality Map* — primitives (list, used?), SDKs (who injects, who calls), Curator service (populates what, who reads).

**Probe:** probe_06_smart_city (trace primitives vs SDKs; trace Curator service; trace wiring in Experience/runtime).

---

### Agentic (civic_systems/agentic)

**Claimed purpose:** Agents (Guide, Liaison, etc.), telemetry, MCP.

**What we need to know (probe questions):**
- Which **agents** are actually instantiated and used in the request path?
- How does **telemetry** flow? Who records what? (Links to orchestrator_health.)
- How do **MCP** tools get discovered and invoked? (Curator? Solution MCP servers?)

**Probe artifact:** *Agentic Reality Map* — agents (created when, used by which routes), telemetry (record path), MCP discovery and invocation path.

**Probe:** probe_07_agentic (trace agent creation and use; trace telemetry record; trace MCP tool list and call).

---

### Experience (civic_systems/experience)

**Claimed purpose:** User-facing API (auth, sessions, intents, guide agent, websocket, admin dashboard).

**What we need to know (probe questions):**
- What **routes** exist and what do they depend on? (app.state.*)
- What is the **first user request path** (e.g. login, or guide agent message)? Which services are required?
- How does Experience **differ** from Runtime API? (Two apps or one? Who mounts what?)

**Probe artifact:** *Experience Reality Map* — routes, dependencies (which SDKs/services), first user path, relationship to Runtime.

**Probe:** probe_08_experience (trace routes and app.state; trace first user path; document Runtime vs Experience boundary).

---

### Artifact Plane (civic_systems/artifact_plane)

**Claimed purpose:** Artifact resolution, lifecycle, registry interaction.

**What we need to know (probe questions):**
- What does the **artifact plane** actually do? Resolve how? Who calls it?
- Are artifacts **real** (storage, IDs, content) or **empty shells** (placeholders)?
- How does it connect to StateSurface, ArtifactRegistry, Curator?

**Probe artifact:** *Artifact Plane Reality Map* — responsibilities (list), callers, artifact flow (create → store → resolve), real vs shell (evidence).

**Probe:** probe_09_artifact_plane (trace artifact_plane methods; trace callers; trace one artifact from create to resolve).

---

### Orchestrator Health (civic_systems/orchestrator_health)

**Claimed purpose:** (Unclear—user: “I have no idea where this came from or what it’s doing.”)

**What we need to know (probe questions):**
- **Where** is it wired? (metrics_api.py: OrchestratorHealthMonitor; telemetry_service.record_orchestrator_health.) **Origin:** Wired in runtime/metrics_api.py; OrchestratorHealthMonitor(telemetry_service=...) created there; tracks _monitored_orchestrators and record_orchestrator_health(); probe_10 confirms callers and whether any orchestrator is monitored in current flow.
- **What** does it do? (Monitors orchestrator health/performance; stores in _monitored_orchestrators; can record to telemetry.)
- **Who** calls start_monitoring / get_health? (metrics_api endpoints.)
- **Why** does it exist? (Hypothesis: metrics/observability for “orchestrators” as logical units; need to confirm if any orchestrator is actually registered.)

**Probe artifact:** *Orchestrator Health Reality Map* — origin (file, wiring), behavior (what it monitors, where data goes), callers, whether any orchestrator is actually monitored in current flow.

**Probe:** probe_10_orchestrator_health (trace wiring in metrics_api; trace start_monitoring/get_health callers; list monitored orchestrators in a run).

---

### Platform SDK (civic_systems/platform_sdk)

**Claimed purpose:** Solution registry, solution model, realm SDK, guide registry, civic composition, solution builder.

**What we need to know (probe questions):**
- What is the **platform SDK** actually used for? Who imports it? (Runtime? Experience? Solutions?)
- **SolutionRegistry** — where is it created and who uses it? (service_factory creates it; solutions register.)
- **Realm SDK / RealmBase** — still used or legacy? (RealmBase deprecated in fabric.)
- Does this affect **base strategy** (bases, contracts)?

**Probe artifact:** *Platform SDK Reality Map* — modules (purpose), callers, SolutionRegistry lifecycle, Realm SDK status.

**Probe:** probe_11_platform_sdk (trace imports and callers; trace SolutionRegistry; document Realm SDK usage).

---

## Realms

**Claimed purpose:** Intent services per realm (content, insights, operations, outcomes, security, control_tower, coexistence); “do they actually work?”

**What we need to know (probe questions):**
- Do realms **actually work**? Can agents reason? Are **artifacts** real or empty shells?
- What can we **reasonably expect to see** on the other side? (User: “We’ve never actually made it past parsing in our browser testing.”)
- Per realm: which intents are **registered**? Which are **invoked** in a typical flow? What do they **return** (shape, real data vs stub)?

**Probe artifact:** *Realms Reality Map* — per realm: intents registered, intents invoked in at least one path, artifact shape (real vs shell), “what we can expect to see” (evidence from one flow, e.g. file upload → parse → artifact).

**Probe:** probe_12_realms (trace intent registration and invocation; pick one flow e.g. content upload→parse; trace artifact creation and content; document “what’s on the other side”).

---

## Runtime

**Claimed purpose:** Execution lifecycle, intent submission, state surface, WAL, artifact resolution.

**What we need to know (probe questions):**
- How does **submitIntent** actually flow? (Route → ELM → IntentRegistry → handler → StateSurface/WAL?)
- Who uses **StateSurface** vs **ArtifactRegistry** vs WAL? Overlap?
- What is the **runtime** boundary? (One process? Two? Experience vs Runtime API?)

**Probe artifact:** *Runtime Reality Map* — submitIntent path (step-by-step with evidence), StateSurface/ArtifactRegistry/WAL usage, runtime boundary.

**Probe:** probe_13_runtime (trace submitIntent; trace StateSurface/registry/WAL callers; document boundary).

---

## Solutions

**Claimed purpose:** Coexistence, Content, Insights, Operations, Outcomes, Security, Control Tower; journeys, MCP servers, SOA APIs.

**What we need to know (probe questions):**
- Which solutions are **loaded** at boot? Which expose **journeys**? Which expose **MCP**?
- How does **compose_journey** reach a solution? (Intent? Direct call?)
- Are solution **contracts** (get_journey, get_journeys, SOA shape) actually satisfied by every solution? (We already know SecuritySolution diverges.)

**Probe artifact:** *Solutions Reality Map* — per solution: loaded?, journeys (list), MCP (yes/no), compose_journey path, contract compliance (evidence).

**Probe:** probe_14_solutions (trace solution init; trace compose_journey; document contract compliance per solution).

---

## Utilities

**Claimed purpose:** clock, errors, ids, logging (and any others).

**What we need to know (probe questions):**
- What are these **doing**? Who uses them?
- Do we **need** them? Are we **properly** using them (e.g. clock for timestamps, ids for event_id)?
- Does usage affect **base strategy** (e.g. all IDs from utilities.ids)?

**Probe artifact:** *Utilities Reality Map* — per utility: purpose, callers, “need?” and “proper use?” (evidence).

**Probe:** probe_15_utilities (trace imports and callers of utilities; document purpose and necessity).

---

## Probe dependency order (recommended)

| Order | Layer / probe | Depends on |
|-------|----------------|------------|
| 0 | probe_01–03 (entry, config, order/restart) | — |
| 1 | probe_04_public_works | 0 |
| 2 | probe_05_curator_foundation | 0, 1 (PublicWorks may feed Curator) |
| 3 | probe_06_smart_city | 0, 1 |
| 4 | probe_07_agentic | 0, 1, 2, 3 |
| 5 | probe_08_experience | 0, 1, 3, 4 |
| 6 | probe_09_artifact_plane | 0, 1, 13 (runtime) optional |
| 7 | probe_10_orchestrator_health | 0, 4 (agentic telemetry) |
| 8 | probe_11_platform_sdk | 0, 1, 14 (solutions) optional |
| 9 | probe_12_realms | 0, 1, 13, 14 |
| 10 | probe_13_runtime | 0, 1, 2, 12 (realms) |
| 11 | probe_14_solutions | 0, 1, 12 |
| 12 | probe_15_utilities | 0 |

*(Some probes can run in parallel once 0 is done; 13/14/12 are intertwined so order can be adjusted.)*

---

## Artifacts summary

| Artifact | Filled by |
|----------|-----------|
| Platform Operation Map (§1–§5) | probe_01–03 |
| Public Works Reality Map | probe_04 |
| Curator (Foundation) Reality Map | probe_05 |
| Smart City Reality Map | probe_06 |
| Agentic Reality Map | probe_07 |
| Experience Reality Map | probe_08 |
| Artifact Plane Reality Map | probe_09 |
| Orchestrator Health Reality Map | probe_10 |
| Platform SDK Reality Map | probe_11 |
| Realms Reality Map | probe_12 |
| Runtime Reality Map | probe_13 |
| Solutions Reality Map | probe_14 |
| Utilities Reality Map | probe_15 |

When all are filled, we have **one coherent map of how the platform really works** and a **clearly explainable purpose** for each part. No component exists without a stated purpose and evidenced behavior.
