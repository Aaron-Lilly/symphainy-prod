# Platform SDK Requirement Spec (Team B)

**Status:** Canonical (January 2026)  
**Audience:** Team B (Landing) — build the Platform SDK against this spec.  
**Purpose:** Deep-dive definition of the intercept so the Platform SDK is built to consume the Platform Boundary and expose a stable `ctx` to intent services.

**Related:** [INTERCEPT_ALIGNMENT_CONTRACT.md](INTERCEPT_ALIGNMENT_CONTRACT.md) (alignment contract), [PLATFORM_SDK_ABSTRACTS_FOR_B_TEAM.md](PLATFORM_SDK_ABSTRACTS_FOR_B_TEAM.md), [docs/architecture/PLATFORM_SDK_ARCHITECTURE.md](architecture/PLATFORM_SDK_ARCHITECTURE.md).

---

## 1. What You Are Building

You own the **Platform SDK** (Semantic OS Kernel): the layer that intent services see. You build:

1. **PlatformContext (`ctx`)** — The unified execution context passed to every intent service.
2. **Four services on ctx** — `ctx.governance`, `ctx.reasoning`, `ctx.experience`, `ctx.platform`.
3. **PlatformContextFactory** — Constructs `ctx` from the Platform Boundary and Runtime resources provided by Team A.
4. **PlatformIntentService** — Base class for intent services that receive `ctx` and use only the four services + Runtime resources.
5. **Capability services** — Intent implementations that subclass `PlatformIntentService` and use `ctx` only.

You do **not** own: Public Works (adapters, abstractions, protocols), Curator (foundation or Smart City), Smart City 9 roles, Agentic internals, Experience internals, Runtime (StateSurface, WAL, ArtifactRegistry). You **consume** those via the **Platform Boundary** only.

---

## 2. The Intercept: What You Receive

At runtime, **Team A** injects the following into your **PlatformContextFactory** (or equivalent constructor). You must build the Platform SDK to accept and use **only** these inputs.

### 2.1 Platform Boundary (Foundation Access)

You receive a **foundation object** that exposes **protocol-typed getters only**. You must **not** call any getter that returns an adapter (e.g. `get_redis_adapter()`, `get_arango_adapter()`, `get_supabase_adapter()`). Those are not part of the boundary; they may raise.

**Required getters (you may call these; type against the protocol):**

| Getter | Returns (protocol type) | Use in Platform SDK |
|--------|--------------------------|----------------------|
| `get_state_abstraction()` | `StateManagementProtocol` | State (or rely on Runtime state_surface) |
| `get_file_storage_abstraction()` | `FileStorageProtocol` | ctx.platform file operations |
| `get_artifact_storage_abstraction()` | `ArtifactStorageProtocol` | ctx.platform artifact store/retrieve |
| `get_registry_abstraction()` | Registry contract | Curator/registry; ctx.governance.registry |
| `get_auth_abstraction()` | `AuthenticationProtocol` | ctx.governance.auth |
| `get_tenant_abstraction()` | `TenancyProtocol` | ctx.governance tenant/policy |
| `get_document_parsing()` | `FileParsingProtocol` | ctx.platform.parse |
| `get_ingestion_abstraction()` | `IngestionProtocol` | ctx.platform.ingest |
| `get_semantic_data_abstraction()` | `SemanticDataProtocol` | ctx.platform semantic ops |
| `get_vector_store()` | `VectorStoreProtocol` | ctx.platform / ctx.reasoning |
| `get_full_text_search()` | `FullTextSearchProtocol` | ctx.reasoning search |
| `get_graph_query()` | `GraphQueryProtocol` | ctx.reasoning / ctx.platform |
| `get_knowledge_discovery_abstraction()` | `KnowledgeDiscoveryProtocol` | ctx.reasoning knowledge |
| `get_event_publisher_abstraction()` | `EventPublisherProtocol` | ctx.governance.events |
| `get_visual_generation_abstraction()` | `VisualGenerationProtocol` | ctx.platform.visualize |
| `get_deterministic_compute_abstraction()` | `DeterministicEmbeddingStorageProtocol` | ctx.platform.embed / analytics |
| `get_semantic_search_abstraction()` | `SemanticSearchProtocol` | ctx.reasoning search |
| `get_service_discovery_abstraction()` | `ServiceDiscoveryProtocol` | ctx.governance / discovery |
| `get_wal_backend()` | `EventLogProtocol` | WAL (or use Runtime wal) |
| `get_boundary_contract_store()` | Boundary contract | ctx.governance |
| `get_guide_registry()` | Guide registry contract | ctx.reasoning agents / guide |
| `get_lineage_backend()` | Lineage contract | ctx.platform / governance |
| `get_extraction_config_registry()` | Extraction config | ctx.platform |
| `get_telemetry_abstraction()` | Telemetry contract | ctx.governance.telemetry |

**Rule:** If a getter returns `None` and the capability is **required** for the operation you are performing, you **must** raise `RuntimeError` with message containing `"Platform contract §8A"`. Do not return empty results or default values when a required dependency is missing.

### 2.2 Curator / Registry Surface

Team A provides the **Curator registry** implementation. You expose it as **ctx.governance.registry**. The surface you must support (and type against) is:

- **register_capability(capability_definition, tenant_id)** → returns a registration result (e.g. capability_id, execution_contract). Async.
- **discover_agents(agent_type=None, tenant_id=None)** → returns agents list + execution_contract. Async.
- **get_domain_registry(domain_name=None, tenant_id=None)** → returns domains + execution_contract. Async.
- **promote_to_platform_dna(...)** — optional; for promoting artifacts to platform DNA. Signature per Team A’s CuratorSDK/Curator service.

You receive this either as (a) a pre-built Curator SDK instance (backed by Team A’s Curator + registry_abstraction), or (b) the registry_abstraction and you build a thin wrapper that exposes the above methods. The **contract** is the method names and semantics above; Team A implements the backing logic.

### 2.3 Smart City (Governance) Surfaces

Team A provides Smart City 9 roles (Data Steward, Security Guard, Curator, Librarian, City Manager, Traffic Cop, Post Office, Nurse, Conductor, Auditor). You build **GovernanceService** that **wraps** these and exposes:

- **ctx.governance.data_steward** — Data boundaries, materialization, Records of Fact.
- **ctx.governance.auth** — Authentication, authorization (from get_auth_abstraction()).
- **ctx.governance.registry** — Curator capability/agent/domain registry (see §2.2).
- **ctx.governance.search** — Knowledge search (from semantic/search protocols).
- **ctx.governance.policy** — Global policy, tenancy (from get_tenant_abstraction(), etc.).
- **ctx.governance.sessions** — Session management (Traffic Cop).
- **ctx.governance.events** — Event routing (Post Office; from get_event_publisher_abstraction()).
- **ctx.governance.workflows** — Workflow/saga primitives (Conductor).
- **ctx.governance.telemetry** — Telemetry (from get_telemetry_abstraction()).

You **initialize** GovernanceService using **only** protocol-typed getters from the Platform Boundary (and the Curator/registry surface). You must **not** take adapter references (e.g. supabase_adapter) in GovernanceService. If Team A passes a pre-built governance surface, you may use that; otherwise you construct GovernanceService from the boundary getters only.

### 2.4 Reasoning (Agentic) Surface

Team A provides Agentic (LLM, agents) via Public Works (e.g. LLM adapters) and Agentic civic components. You build **ReasoningService** that exposes:

- **ctx.reasoning.llm** — complete(prompt, model, temperature, max_tokens), embed(content, model).
- **ctx.reasoning.agents** — get(id), invoke(id, params), invoke_by_type(type, params), collaborate(agent_ids, task), list(), list_types().

You initialize ReasoningService from the Platform Boundary (e.g. LLM/embedding capabilities via protocol getters or a pre-built Agentic surface). No adapter references.

### 2.5 Runtime-Provided Resources (Injected by Team A)

Team A (Runtime) injects these **directly** into your context factory; you do not create them:

- **state_surface** — StateSurface instance. Expose as **ctx.state_surface**.
- **wal** — WriteAheadLog instance. Expose as **ctx.wal**.
- **artifacts** — ArtifactRegistry instance. Expose as **ctx.artifacts**.

Your factory signature must accept these three plus the Platform Boundary (foundation object). You attach them to `PlatformContext` as-is.

---

## 3. What You Must Expose: ctx Shape

### 3.1 PlatformContext Fields

| Field | Type | Owner | Notes |
|-------|------|-------|--------|
| execution_id | str | — | Unique execution id |
| intent | Intent | — | The intent being executed |
| tenant_id | str | — | Tenant id |
| session_id | str | — | Session id |
| solution_id | str | — | Solution id |
| state_surface | StateSurface \| None | Runtime (Team A) | Injected |
| wal | WriteAheadLog \| None | Runtime (Team A) | Injected |
| artifacts | ArtifactRegistry \| None | Runtime (Team A) | Injected |
| platform | PlatformService | Platform SDK (you) | Capability operations |
| governance | GovernanceService | Platform SDK (you) | Smart City 9 roles |
| reasoning | ReasoningService | Platform SDK (you) | LLM, agents |
| experience | dict or narrow type | Platform SDK (you) | Metadata only |
| metadata | dict | — | Execution metadata |
| created_at | datetime | — | Context creation time |

### 3.2 ctx.platform (PlatformService)

Capability-oriented operations. All backed by protocol getters from the Platform Boundary. Required surface (minimal; you may add):

- **parse(file_ref, file_type, options)** — Document parsing. Use get_document_parsing().
- **parse_* (e.g. parse_pdf, parse_csv)** — Type-specific parse helpers.
- **visualize(data, viz_type, options)** — Use get_visual_generation_abstraction().
- **embed(content, model)** — Use get_deterministic_compute_abstraction() or semantic/LLM path.
- **ingest(source, source_type, tenant_id, session_id)** — Use get_ingestion_abstraction().
- **store_artifact(artifact_id, data, content_type, tenant_id)** — Use get_artifact_storage_abstraction().
- **retrieve_artifact(artifact_id, tenant_id)** — Use get_artifact_storage_abstraction().
- **store_semantic(content_id, content, embedding, tenant_id)** — Use get_semantic_data_abstraction().
- **search_semantic(query_embedding, tenant_id, limit)** — Use get_semantic_data_abstraction() or get_vector_store() / get_full_text_search().

Do **not** expose raw state or registry as “platform”; state is on ctx.state_surface, registry is on ctx.governance.registry.

### 3.3 ctx.governance (GovernanceService)

As in §2.3: data_steward, auth, registry, search, policy, sessions, events, workflows, telemetry. All backed by Smart City + Curator surfaces from the boundary.

### 3.4 ctx.reasoning (ReasoningService)

As in §2.4: llm (complete, embed), agents (get, invoke, invoke_by_type, collaborate, list, list_types). Backed by Agentic + Public Works via boundary.

### 3.5 ctx.experience

Narrow metadata surface (e.g. dict or a small typed struct). No direct Experience internals; mediated only.

---

## 4. Context Factory Contract

Your **PlatformContextFactory** (or equivalent) must:

1. **Accept** (constructor or create_context):
   - **boundary** — The foundation object providing protocol getters only (and optionally pre-built Curator/Governance/Reasoning surfaces).
   - **state_surface** — StateSurface (from Runtime).
   - **wal** — WriteAheadLog (from Runtime).
   - **artifact_registry** — ArtifactRegistry (from Runtime).

2. **Build** (internally):
   - GovernanceService from boundary (and Curator surface).
   - ReasoningService from boundary.
   - PlatformService from boundary.

3. **Return** PlatformContext with:
   - execution_id, intent, tenant_id, session_id, solution_id, metadata, created_at;
   - state_surface, wal, artifacts (injected);
   - platform, governance, reasoning, experience (built from boundary).

4. **Fail fast:** If boundary is None (or a required getter returns None when the service needs it), raise RuntimeError with "Platform contract §8A" rather than returning a partially built ctx.

Team A will call your factory with the boundary and Runtime resources they own; you never instantiate Public Works or Runtime yourself.

---

## 5. PlatformIntentService Contract

- **Base class** for all intent services that run under the Platform SDK.
- **execute(ctx: PlatformContext)** → returns a result dict (e.g. artifacts, events, status, error).
- **Must use only:** ctx.platform, ctx.governance, ctx.reasoning, ctx.experience, ctx.state_surface, ctx.wal, ctx.artifacts. No direct access to Public Works, adapters, or Civic internals.
- **Parameter access:** Via ctx.intent (and standard helpers such as get_param(ctx, name) if you provide them).
- **Validation:** validate_params(ctx, required_keys) and fail with clear error if invalid.

---

## 6. Non-Functional Requirements

| Requirement | Description |
|-------------|-------------|
| **Protocol-only** | You never call get_*_adapter() or use adapter types. You type against protocols from `symphainy_platform.foundations.public_works.protocols.*`. |
| **§8A compliance** | When a required dependency is missing (None), raise RuntimeError with message containing "Platform contract §8A". Do not silently degrade (no default None/False/[] as success). |
| **No civic internals** | You do not import or call Smart City / Agentic / Experience internals except through the boundary (e.g. pre-built GovernanceService/ReasoningService or protocol getters). |
| **Experience SDK boundary** | Experience surfaces (UIs, dashboards) use Experience SDK only (query_state, invoke_intent, trigger_journey, subscribe). They do **not** receive ctx or Platform SDK. Only **intent/capability code** (backend) receives ctx. |

---

## 7. File Structure (Your Ownership)

You own the module that provides the Platform SDK. Suggested layout:

```
symphainy_platform/civic_systems/platform_sdk/
├── __init__.py              # Exports: PlatformContext, PlatformContextFactory,
│                             #          PlatformIntentService, services
├── context.py                # PlatformContext, PlatformContextFactory
├── intent_service_base.py   # PlatformIntentService
└── services/
    ├── __init__.py
    ├── governance_service.py  # ctx.governance (wraps boundary + Curator)
    ├── reasoning_service.py   # ctx.reasoning (wraps boundary + Agentic)
    └── platform_service.py    # ctx.platform (wraps boundary protocol getters)
```

You may relocate this under a Team B–owned package; the **contract** (ctx shape, four services, boundary consumption) remains as specified.

---

## 8. References

- [INTERCEPT_ALIGNMENT_CONTRACT.md](INTERCEPT_ALIGNMENT_CONTRACT.md) — Alignment contract (we build to, you build from).
- [PLATFORM_SDK_ABSTRACTS_FOR_B_TEAM.md](PLATFORM_SDK_ABSTRACTS_FOR_B_TEAM.md) — Protocol list and provisional guidance.
- [docs/architecture/PROTOCOL_REGISTRY.md](architecture/PROTOCOL_REGISTRY.md) — Protocol stability and getter names.
- [docs/architecture/PLATFORM_SDK_ARCHITECTURE.md](architecture/PLATFORM_SDK_ARCHITECTURE.md) — High-level SDK architecture.
- [docs/architecture/PLATFORM_CONTRACT.md](architecture/PLATFORM_CONTRACT.md) — §8A, §8C.

---

**Last updated:** January 2026  
**Owner:** Team B (Landing); spec maintained jointly with Team A for intercept alignment.
