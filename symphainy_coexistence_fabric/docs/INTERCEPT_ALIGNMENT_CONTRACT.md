# Intercept Alignment Contract

**Status:** Canonical (January 2026)  
**Purpose:** Single contract so Team A (Takeoff) and Team B (Landing) meet in the same middle. We build **to** this; they build **from** this.

**Related:** [PLATFORM_SDK_REQUIREMENT_SPEC.md](PLATFORM_SDK_REQUIREMENT_SPEC.md) (Team B build spec), [HANDOFF_TO_TEAM_B.md](HANDOFF_TO_TEAM_B.md), [PLATFORM_SDK_ABSTRACTS_FOR_B_TEAM.md](PLATFORM_SDK_ABSTRACTS_FOR_B_TEAM.md).

---

## 1. Ownership Boundary

| Side | Owns | Delivers |
|------|------|----------|
| **Team A (Takeoff)** | Everything **up to** the Platform SDK | **Platform Boundary** — Public Works (protocol getters), Curator (registry + governance), Civic (Smart City 9 roles, Agentic, Experience, Artifact Plane, Orchestrator Health), Runtime (StateSurface, WAL, ArtifactRegistry). We implement and expose the **intercept surface** the Platform SDK consumes. |
| **Team B (Landing)** | The **Platform SDK** and everything forward | **Platform SDK** (Semantic OS Kernel) — `ctx`, four services (`ctx.governance`, `ctx.reasoning`, `ctx.experience`, `ctx.platform`), `PlatformIntentService` base class, capability services, Four Frameworks. They consume our Platform Boundary and expose intent primitives to solutions/journeys/intents. |

**The intercept:** The **Platform Boundary** is the only surface between the two teams. Team A implements it; Team B consumes it to build the Platform SDK. No other coupling (no direct adapter access, no civic internals).

---

## 2. What “Meet in the Middle” Means

- **Team A builds to:** We deliver a **Platform Boundary** that satisfies the contract below. We do not deliver Platform SDK code (context, four services, intent base class). We deliver the **inputs** to the Platform SDK: protocol-typed capabilities, Curator/registry surface, and Runtime resources, in the exact shape specified.
- **Team B builds from:** They build the Platform SDK (ctx, four services, intent services) that **consumes only** the Platform Boundary. They never call Public Works internals, adapters, or Civic code except through the boundary. They type against the protocols and surfaces defined here and in the requirement spec.

**Single source of truth for the intercept:** This document plus [PLATFORM_SDK_REQUIREMENT_SPEC.md](PLATFORM_SDK_REQUIREMENT_SPEC.md).

---

## 3. Platform Boundary (The Intercept Surface)

Team A **implements** and **exposes**; Team B **consumes**. All types are protocol- or contract-typed; no adapters.

### 3.1 Public Works Protocol Access

The Platform SDK receives access to Public Works **only** via protocol-typed getters. The following getters are the **canonical** boundary. Team A ensures these return protocol types (or None when optional); Team B uses only these getters and types against the protocols.

| Capability | Getter (Team A provides) | Protocol / type (Team B types against) |
|-------------|---------------------------|----------------------------------------|
| State | `get_state_abstraction()` | `StateManagementProtocol` |
| File storage | `get_file_storage_abstraction()` | `FileStorageProtocol` |
| Artifact storage | `get_artifact_storage_abstraction()` | `ArtifactStorageProtocol` |
| Registry / lineage | `get_registry_abstraction()` | Registry contract (TBD; Curator flow) |
| Auth | `get_auth_abstraction()` | `AuthenticationProtocol` |
| Tenant | `get_tenant_abstraction()` | `TenancyProtocol` |
| Document parsing | `get_document_parsing()` | `FileParsingProtocol` |
| Ingestion | `get_ingestion_abstraction()` | `IngestionProtocol` |
| Semantic data | `get_semantic_data_abstraction()` | `SemanticDataProtocol` |
| Vector store | `get_vector_store()` | `VectorStoreProtocol` |
| Full-text search | `get_full_text_search()` | `FullTextSearchProtocol` |
| Graph query | `get_graph_query()` | `GraphQueryProtocol` |
| Knowledge discovery | `get_knowledge_discovery_abstraction()` | `KnowledgeDiscoveryProtocol` |
| Event publisher | `get_event_publisher_abstraction()` | `EventPublisherProtocol` |
| Visual generation | `get_visual_generation_abstraction()` | `VisualGenerationProtocol` |
| Deterministic compute / embeddings | `get_deterministic_compute_abstraction()` | `DeterministicEmbeddingStorageProtocol` |
| Semantic search | `get_semantic_search_abstraction()` | `SemanticSearchProtocol` |
| Service discovery | `get_service_discovery_abstraction()` | `ServiceDiscoveryProtocol` |
| WAL | `get_wal_backend()` | `EventLogProtocol` |
| Boundary contract store | `get_boundary_contract_store()` | Per protocol |
| Guide registry | `get_guide_registry()` | Per protocol |
| Lineage backend | `get_lineage_backend()` | Per protocol |
| Extraction config registry | `get_extraction_config_registry()` | Per protocol |
| Telemetry | `get_telemetry_abstraction()` | Per protocol |

**Rule:** Team A does **not** expose adapter getters (`get_redis_adapter()`, `get_arango_adapter()`, `get_supabase_adapter()`, etc.) at the boundary. Those raise or are not part of the Platform Boundary. Team B never requests adapters.

### 3.2 Curator / Registry Surface

Team A provides the **Curator registry** surface that backs `ctx.governance.registry`. Team B’s Platform SDK exposes it as `ctx.governance.registry` and types against the following contract.

- **list_capabilities** (or equivalent) — list registered capabilities.
- **get_capability(id)** (or equivalent) — get capability by id.
- **register_capability(definition, tenant_id)** (or equivalent) — register capability; returns a registration contract.
- **discover_agents** (or equivalent) — discover agents per contract.

Exact method names and signatures are in [PLATFORM_SDK_REQUIREMENT_SPEC.md](PLATFORM_SDK_REQUIREMENT_SPEC.md) § Curator/Registry. Team A implements this surface (e.g. via CuratorSDK or foundation Curator); Team B consumes it only through the boundary.

- **Curator is required for the platform to run.** The platform does not start without Curator. If Curator cannot be built (e.g. Supabase or required abstractions missing), bootstrap fails with a clear error.
- **Curator is only valid with proper Supabase.** Local or in-memory storage is not a final answer for a database of that criticality. The promotion path is Supabase-backed; see [CURATOR_REAL_VS_STUB_EXPLAINED.md](CURATOR_REAL_VS_STUB_EXPLAINED.md).

### 3.3 Civic Surfaces (Smart City, Agentic)

Team A provides **Smart City** (9 roles) and **Agentic** (LLM, agents) as surfaces the Platform SDK can call. The Platform SDK’s `ctx.governance` wraps Smart City (Data Steward, Security Guard, Curator, Librarian, Traffic Cop, Post Office, Nurse, etc.); `ctx.reasoning` wraps Agentic (LLM, agents). Team A delivers these as **protocol- or SDK-typed** surfaces (no raw adapters). Team B builds GovernanceService and ReasoningService that **call** these surfaces only through the agreed interfaces.

### 3.4 Runtime-Provided Resources

Team A (Runtime) provides and injects:

- **state_surface** — StateSurface (state storage/retrieval).
- **wal** — WriteAheadLog (append-only event log).
- **artifacts** — ArtifactRegistry (artifact registration and resolution).

Team B’s Platform SDK receives these at context construction and exposes them on `ctx` as `ctx.state_surface`, `ctx.wal`, `ctx.artifacts`. Team B does not create them; Team A injects them.

---

## 4. Protocol-Only Rule (No Adapters)

- **Team A:** At the Platform Boundary we expose **only** protocol-typed getters and Civic/Curator surfaces. We do not pass adapters (Redis, Arango, Supabase, etc.) to the Platform SDK. Adapter getters either raise (e.g. RuntimeError per §8A) or are not part of the boundary.
- **Team B:** The Platform SDK consumes **only** the Platform Boundary. It does not call `get_*_adapter()` or import adapter classes. It types against protocols and the Curator/registry contract. If a required dependency is missing (None), it fails fast (e.g. RuntimeError with “Platform contract §8A”).

---

## 5. ctx Shape (Four Services)

Both sides agree on the **shape** of `ctx` so that intent services see a stable contract.

- **ctx.platform** — Capability-oriented operations (parse, analyze, visualize, ingest, store/retrieve artifact, semantic operations, etc.). Backed by Public Works protocols via the boundary.
- **ctx.governance** — Smart City (9 roles): data_steward, auth, registry (Curator), search, policy, sessions, events, workflows, telemetry. Backed by Civic + Curator.
- **ctx.reasoning** — LLM and agents (complete, embed, get/invoke/list agents). Backed by Agentic + Public Works (e.g. LLM) via the boundary.
- **ctx.experience** — Narrow metadata surface for experience; mediated only.

Plus Runtime-owned on ctx: **ctx.state_surface**, **ctx.wal**, **ctx.artifacts**.

Capability placement (e.g. state/registry on Runtime vs platform) is fixed in [PLATFORM_SDK_REQUIREMENT_SPEC.md](PLATFORM_SDK_REQUIREMENT_SPEC.md). Team A does not change the **semantic** placement without aligning with Team B.

---

## 6. Wiring Point (Who Builds ctx)

- **Team B** owns the **Platform SDK** implementation: `PlatformContext`, `PlatformContextFactory`, `GovernanceService`, `ReasoningService`, `PlatformService`, `PlatformIntentService`.
- **Team A** owns **providing** the inputs: a “foundation” or “boundary” object (e.g. Public Works foundation service restricted to protocol getters), Curator/registry implementation, Civic implementations, and Runtime resources (state_surface, wal, artifact_registry).
- **Wiring:** At runtime, the **factory** that creates `ctx` (e.g. `PlatformContextFactory`) is called with: (1) the Platform Boundary (protocol getters + Curator/Civic surfaces), (2) state_surface, (3) wal, (4) artifact_registry. Team B’s factory builds the four services from (1) and attaches (2)–(4) to `ctx`. Team A is responsible for constructing and injecting (1)–(4) into that factory (e.g. from Runtime bootstrap). Exact constructor shape is in the requirement spec.

---

## 7. What We Align On

| Topic | Agreement |
|-------|-----------|
| **Ownership** | Team A: up to Platform SDK boundary. Team B: Platform SDK and forward. |
| **Intercept surface** | Platform Boundary = protocol getters + Curator/registry + Civic surfaces + Runtime resources. No adapters. |
| **ctx shape** | Four services (governance, reasoning, experience, platform) + state_surface, wal, artifacts. |
| **Curator/registry** | Contract in requirement spec; Team A implements, Team B consumes via ctx.governance.registry. |
| **Protocol-only** | Team A exposes only protocols at boundary; Team B uses only boundary; both fail fast if required dependency missing. |
| **Wiring** | Team A injects boundary + Runtime resources into Team B’s context factory; Team B builds ctx and four services. |

---

## 8. References

- [PLATFORM_SDK_REQUIREMENT_SPEC.md](PLATFORM_SDK_REQUIREMENT_SPEC.md) — Team B requirement spec (deep dive intercept).
- [PLATFORM_SDK_ABSTRACTS_FOR_B_TEAM.md](PLATFORM_SDK_ABSTRACTS_FOR_B_TEAM.md) — Protocol list and provisional guidance.
- [docs/architecture/PROTOCOL_REGISTRY.md](architecture/PROTOCOL_REGISTRY.md) — Protocol stability and getter names.
- [docs/architecture/PLATFORM_CONTRACT.md](architecture/PLATFORM_CONTRACT.md) — §8A, §8C, no silent degradation.
- [HANDOFF_TO_TEAM_B.md](HANDOFF_TO_TEAM_B.md) — Handoff and remit.

---

**Last updated:** January 2026  
**Owners:** Team A (Takeoff) + Team B (Landing); contract maintained jointly.
