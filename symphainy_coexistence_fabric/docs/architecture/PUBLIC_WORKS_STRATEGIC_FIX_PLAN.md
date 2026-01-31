# Public Works Strategic Fix Plan

**Purpose:** Single strategic plan to align Public Works with the target architecture. All work is **strategic only** — no short-term workarounds. We break and fix toward the future state.

**Invariant:** No adapter (Redis, Arango, Supabase, GCS, etc.) may be imported, constructed, or received by any code outside the Public Works boundary. Public Works exposes only protocol-typed capabilities via the five-slice ctx.

**References:** [ARCHITECTURE_NORTH_STAR.md](../ARCHITECTURE_NORTH_STAR.md) §10, §14.4; [updated_platform_vision.md](../updated_platform_vision.md); [FOUR_SERVICE_MAPPING.md](FOUR_SERVICE_MAPPING.md); [PUBLIC_WORKS_REALITY_MAP.md](../testing/PUBLIC_WORKS_REALITY_MAP.md); [BOOT_PHASES.md](BOOT_PHASES.md); [INIT_ORDER_SPEC.md](INIT_ORDER_SPEC.md).

**Progress:** Phase A1–A3 done. A2: BoundaryContractStoreProtocol + BoundaryContractStoreBackend + get_boundary_contract_store(); DataStewardPrimitives/SDK wired in service_factory. TTL job uses boundary_contract_store + file_storage protocols. LineageProvenanceProtocol + ArangoLineageBackend + get_lineage_backend(); DataBrain takes lineage_backend (Arango-backed for execution provenance). A3: get_supabase_adapter() and get_arango_adapter() now raise RuntimeError; use protocol getters only. **Phase B (mega protocol decomposition):** SemanticData already had narrow getters (get_vector_store, get_semantic_graph, get_correlation_map); SemanticDataAbstraction now explicitly implements VectorStoreProtocol, SemanticGraphProtocol, CorrelationMapProtocol; EmbeddingAgent migrated to get_vector_store(). KnowledgeDiscovery decomposed: FullTextSearchProtocol + GraphQueryProtocol added; KnowledgeDiscoveryAbstraction implements both via delegation; foundation exposes get_full_text_search(), get_graph_query(), get_knowledge_discovery_abstraction().

---

## 1. Strategic stance

- **Only strategic fixes** aligned to realizing the future-state target architecture.
- **No** "for now" patches (e.g. attach keys to app.state to unblock routes; leave WAL with adapter; guard/remove routes).
- **Target:** Public Works only (adapters inside); one protocol per logical capability; five-slice ctx (governance, reasoning, experience, platform, runtime) MECE; single composition root; inject ctx into every process (Runtime, Experience); Genesis describes ctx and both processes as first-class outcomes of Φ3.

---

## 2. Adapter leak inventory (find all leaks)

**Rule:** No code outside `symphainy_platform/foundations/public_works/` may import an adapter class or receive an adapter instance. Foundation service must not expose `get_redis_adapter()`, `get_arango_adapter()`, `get_supabase_adapter()` to the rest of the platform.

| # | Location | What it does | Remediation |
|---|----------|--------------|-------------|
| 1 | **runtime/service_factory.py** | Calls `public_works.get_redis_adapter()`, passes to WAL | Use `get_wal_backend()` → EventLogProtocol (see §4). |
| 2 | **runtime/wal.py** | Imports `RedisAdapter`, constructor takes `redis_adapter`, uses streams | WAL depends on EventLogProtocol; Public Works implements RedisEventLogBackend. |
| 3 | **runtime/transactional_outbox.py** | Imports `RedisAdapter`, takes `redis_adapter`, uses xadd/xrange | Same: depend on EventLogProtocol; implementation inside Public Works. |
| 4 | **runtime/data_brain.py** | Imports `ArangoAdapter`, takes `arango_adapter` | Keep unwired until lineage strategy set. If wired: depend on LineageProvenanceProtocol; implement inside Public Works. |
| 5 | **foundations/libraries/extraction/structured_extraction_service.py** | `public_works.get_supabase_adapter()` → ExtractionConfigRegistry | Depend on protocol (e.g. ExtractionConfigRegistryProtocol or ctx.governance.extraction_config); Public Works implements. |
| 6 | **foundations/libraries/matching/guided_discovery_service.py** | `public_works.get_supabase_adapter()` → GuideRegistry | Depend on protocol (e.g. GuideRegistryProtocol or ctx.governance.guide_registry); Public Works implements. |
| 7 | **civic_systems/smart_city/primitives/data_steward_primitives.py** | `BoundaryContractStore(supabase_adapter=...)` | Depend on BoundaryContractStoreProtocol (or ctx.governance.boundary_contracts); Public Works implements. |
| 8 | **civic_systems/smart_city/sdk/data_steward_sdk.py** | Constructor can take `supabase_adapter`, passes to primitives | SDK receives protocol/capability from ctx.governance; no adapter. |
| 9 | **civic_systems/smart_city/jobs/ttl_enforcement_job.py** | Constructor takes `gcs_adapter`, uses for purge | Depend on protocol (e.g. BlobPurgeProtocol or extend FileStorageProtocol); Public Works implements. |
| 10 | **civic_systems/smart_city/sdk/post_office_sdk.py** | Imports `RedisAdapter`, takes `redis_adapter`, uses xrange | Depend on EventLogProtocol or EventPublisherProtocol; Public Works implements. |
| 11 | **foundation_service.py** (public API) | Exposes `get_redis_adapter()`, `get_arango_adapter()`, `get_supabase_adapter()` | Remove from public API once all consumers use protocol getters; keep internal use only inside Public Works. |

**Note:** Abstractions *inside* `public_works/abstractions/` (e.g. state_abstraction, registry_abstraction) correctly take adapters in constructors; that is inside Public Works. The leak is foundation_service exposing adapter getters and runtime/civic_systems/libraries consuming adapters.

---

## 3. Missing adapters and infrastructure (flag for discussion)

- **S3 / generic FS:** Vision lists S3, FS; current code has GCS + Supabase file only. **Deferred** per PUBLIC_WORKS_REALITY_MAP P6; no implementation until concrete requirement. **Flag:** If BYOI or multi-cloud file storage is required, add S3/generic FS adapter and wire behind FileStorageProtocol.
- **TelemetryAdapter:** Present in adapters/ but not in foundation_service `_create_adapters`. Pre-boot now requires OTEL; telemetry is foundational. **Action:** Wire TelemetryAdapter in Public Works and expose via get_telemetry_abstraction() (or ctx.platform.telemetry). Confirm if already wired elsewhere.
- **redis_streams_publisher:** Optional EventPublisher; may be used by EventPublisherAbstraction. Confirm wiring and that no caller receives RedisAdapter.
- **as2_decryption, file_parsing/** (copybook, metadata_extractor): Utility/subpackage; document as internal to Public Works or clarify ownership.

---

## 4. Missing abstractions and protocols — order of work

**Strategic order:** Fix leaks first (so no adapter crosses the boundary), then decompose megas (so swaps are local), then finalize ctx and DI.

### 4.1 Protocols to add (to eliminate adapter leaks)

| Protocol | Purpose | Consumers | Implemented by (inside Public Works) |
|----------|---------|-----------|--------------------------------------|
| **EventLogProtocol** | Append-only log: append, read_range, consumer_group create, readgroup, ack (Redis Streams–shaped surface). | WAL, TransactionalOutbox, PostOfficeSDK | RedisStreamsEventLogBackend (wraps RedisAdapter). |
| **BoundaryContractStoreProtocol** (or GovernanceTableProtocol) | CRUD for data_boundary_contracts (governance table). | data_steward_primitives, DataStewardSDK | Implementation over SupabaseAdapter inside Public Works. |
| **ExtractionConfigRegistryProtocol** | Read/write extraction config table. | structured_extraction_service | Implementation over SupabaseAdapter inside Public Works. |
| **GuideRegistryProtocol** | Read/write discovery/guide config table. | guided_discovery_service | Implementation over SupabaseAdapter inside Public Works. |
| **BlobPurgeProtocol** or extend **FileStorageProtocol** | Purge/delete expired blobs by policy (e.g. TTL). | ttl_enforcement_job | FileStorageAbstraction or dedicated implementation over GCSAdapter. |
| **LineageProvenanceProtocol** (DataBrain) | Track/query execution provenance (references, provenance entries). | DataBrain | **Lineage data lives in Supabase** (artifact lineage: Registry, get_file_lineage). This protocol is backend-agnostic: implement with Supabase (single source of truth) or Arango (execution provenance / analysis). First implementation can be Arango-backed for DataBrain; Supabase-backed impl can be added when we add data_references/data_provenance tables. |

**Implementation rule:** All of the above are implemented **inside** Public Works (new or existing modules under foundations/public_works/). Foundation service exposes them via get_* returning the protocol type. No adapter escapes.

### 4.2 Remove adapter getters from public API

- Remove or restrict to private/internal: `get_redis_adapter()`, `get_arango_adapter()`, `get_supabase_adapter()`.
- Add getters that return protocol types only: e.g. `get_wal_backend() -> EventLogProtocol`, `get_boundary_contract_store() -> BoundaryContractStoreProtocol`, etc.

---

## 5. Decompose mega protocols (and abstractions)

**Standard rule:** One protocol per logical capability; avoid mega protocols. A "logical capability" is a cohesive set of operations that would be swapped as a **unit** when changing infrastructure.

### 5.1 SemanticDataProtocol (mega)

**Current:** Embeds embeddings (store/get/query/vector_search), semantic graph (store/get), correlation map (store/get), health_check.

**Split:**

| New protocol | Swap unit | Methods (conceptual) |
|--------------|-----------|----------------------|
| **VectorStoreProtocol** | Vector backend (e.g. Arango → Pinecone) | store_semantic_embeddings, get_semantic_embeddings, query_by_semantic_id, vector_search |
| **SemanticGraphProtocol** | Graph backend | store_semantic_graph, get_semantic_graph |
| **CorrelationMapProtocol** | Correlation store | store_correlation_map, get_correlation_map |

**Abstraction:** SemanticDataAbstraction can implement all three protocols (or we introduce VectorStoreAbstraction, SemanticGraphAbstraction, CorrelationMapAbstraction and compose). Callers depend on the narrowest protocol they need.

### 5.2 KnowledgeDiscoveryProtocol (mega)

**Current:** Meilisearch (search, facets, analytics, event tracking) + Arango graph (search, neighbors, path, stats) in one protocol.

**Split:**

| New protocol | Swap unit | Methods (conceptual) |
|--------------|-----------|----------------------|
| **FullTextSearchProtocol** (or SearchIndexProtocol) | Search engine (Meilisearch → OpenSearch, etc.) | search, search_with_facets, get_analytics, track_event |
| **GraphQueryProtocol** | Graph backend | search_graph, get_neighbors, find_path, get_stats |

**Abstraction:** KnowledgeDiscoveryAbstraction implements both protocols (or we split into FullTextSearchAbstraction and GraphQueryAbstraction and compose).

### 5.3 Mega abstractions / adapters

- **Abstractions:** If an abstraction implements multiple narrow protocols, that is acceptable (one abstraction, multiple protocols). Alternatively, split into smaller abstractions and compose. Prefer "implement multiple protocols" where it avoids unnecessary indirection.
- **Adapters:** Adapters stay as-is (RedisAdapter, ArangoAdapter, etc.) but are **only** used inside Public Works. We do not split adapters; we split **protocols** so that new backends can implement one narrow protocol at a time.

---

## 6. Five ctx capability services (MECE)

**Model:** One ctx object with five slices. Every capability has exactly one home. No floating injectables.

| Slice | Purpose | Capabilities (get_* or attr) |
|-------|---------|------------------------------|
| **ctx.governance** | Auth, tenant, policy, lineage metadata, data boundary | auth (AuthenticationProtocol), tenant (TenancyProtocol), registry (RegistryAbstraction/Protocol), boundary_contracts (BoundaryContractStoreProtocol), extraction_config (ExtractionConfigRegistryProtocol), guide_registry (GuideRegistryProtocol) |
| **ctx.reasoning** | Semantic, search, analytical | semantic_data (SemanticDataProtocol or split VectorStore/SemanticGraph/CorrelationMap), semantic_search (SemanticSearchProtocol), deterministic_embeddings (DeterministicEmbeddingStorageProtocol), knowledge_discovery (FullTextSearchProtocol + GraphQueryProtocol or composed) |
| **ctx.experience** | UX, Control Room, admin, guide agent | Built from auth, tenant, state; Control Room (genesis status); TrafficCopSDK, SecurityGuardSDK, AdminDashboardService, GuideAgentService — all fed from ctx.governance, ctx.runtime as needed. |
| **ctx.platform** | Capability-oriented: parse, visualize, ingest, metrics | document_parsing (FileParsingProtocol), visual_generation (VisualGenerationProtocol), ingestion (IngestionProtocol), telemetry (when wired) |
| **ctx.runtime** | Execution infrastructure | state (StateManagementProtocol), file_storage (FileStorageProtocol), artifact_storage (ArtifactStorageProtocol), registry (RegistryAbstraction), wal_backend (EventLogProtocol), service_discovery (ServiceDiscoveryProtocol) |

**MECE:** Every get_* or capability maps to exactly one slice. Runtime process uses ctx.runtime (and passes ctx to intent execution for ctx.platform, ctx.reasoning, ctx.governance). Experience process uses ctx.experience and ctx.governance. No "substrate" floating outside ctx; ctx.runtime is the fifth slice.

---

## 7. New DI container / injection pattern

- **Composition root:** One place (bootstrap or service_factory extended) that: (1) builds Public Works from config, (2) builds **ctx** (all five slices) from Public Works, (3) builds runtime graph (StateSurface, WAL, ELM, IntentRegistry, etc.) from ctx.runtime and protocol getters.
- **Container:** **ctx** is the container. No separate "RuntimeServices" bag; Runtime process receives **ctx**. Experience process receives **ctx**. Optional: RuntimeServices or a small struct holds runtime-specific construction (state_surface, wal, elm) but is built from ctx and not passed as a substitute for ctx.
- **Injection:**
  - **Runtime process:** Build ctx → create Runtime app with ctx (e.g. `create_runtime_app(ctx)`). Attach `app.state.ctx = ctx` if FastAPI routes need it. Runtime API and ELM use ctx.runtime (and ctx.platform, ctx.reasoning, ctx.governance for intent execution).
  - **Experience process:** Build ctx → create Experience app with ctx (e.g. `create_app(ctx)` or `create_app()` and then `app.state.ctx = ctx`). All Depends(get_ctx) or get_experience_ctx resolve. Routes use `ctx.experience`, `ctx.governance` as needed. No per-service keys (security_guard_sdk, guide_agent_service, etc.) on app.state; only **ctx**.
- **Request-scoped:** Current user, tenant, session remain resolved per-request via Depends() from request (e.g. token → SecurityContext). They are not part of ctx; they are derived from ctx.governance (auth, tenant) at request time.

**Deliverable:** Bootstrap (or experience_main / runtime_main) builds ctx; both processes receive the same ctx shape; attach app.state.ctx = ctx; migrate all route dependencies to Depends(get_ctx) and read from the appropriate slice.

---

## 8. Genesis protocol alignment (all five slices; Runtime and Experience first-class)

**Problem:** Current boot narrative emphasizes "Experience SDK surface available" as the Φ3 outcome and "Experience attachment" as Φ4. That can read as if Experience is the only consumer of the runtime graph. In the target architecture, **ctx** is the outcome of Φ3, and **both** Runtime and Experience (and any other process) receive ctx and use the slice(s) they need.

**Changes to apply:**

1. **BOOT_PHASES.md**
   - **Φ3 outcome:** Replace "Experience SDK surface is available" with: "**ctx is built and available.** Runtime app and Experience app each receive ctx; Runtime uses ctx.runtime (and other slices for intent execution); Experience uses ctx.experience and ctx.governance. Experience SDK surface is available via ctx.experience."
   - **Φ4:** Keep "Experience surfaces attach to the SDK" but clarify that the SDK is fed by ctx.experience (and that ctx is already injected in Φ3).

2. **INIT_ORDER_SPEC.md**
   - **Φ3 outcome:** State that the outcome of Φ3 is "ctx built; Runtime and Experience apps created with ctx attached; all five capability slices (governance, reasoning, experience, platform, runtime) available."
   - **Sequence:** Add step (or sub-step): "Build ctx from Public Works (five slices); create Runtime app with ctx; create Experience app with ctx; attach app.state.ctx = ctx in each app."
   - **WAL:** When EventLogProtocol is introduced, document that Step 3 (WAL) uses get_wal_backend() → EventLogProtocol, not get_redis_adapter().

3. **genesis_protocol.md**
   - **Φ3 — Operational Reality:** Add that "ctx (five-slice capability context) is constructed and injected into Runtime and Experience processes." So "universe assembles" includes: Public Works, ctx, runtime graph, and both apps receiving ctx.
   - Avoid language that suggests only "Experience SDK" or "Experience service" is the consumer of the runtime; both Runtime and Experience are first-class consumers of ctx.

4. **PRE_BOOT_SPEC / PLATFORM_CONTRACT**
   - No change to gates; ensure that when we document "what is built after G3," we list ctx and both apps (Runtime, Experience) as outcomes.

**Principle:** Genesis describes **what must be true** at each phase. After Φ3, what must be true is: ctx exists, Runtime app has ctx, Experience app has ctx, and all five slices are populated. Neither "Runtime" nor "Experience" is the only destination; both are first-class; ctx is the single capability container they share.

---

## 9. Execution order (recommended)

| Phase | Work | Outcome |
|-------|------|---------|
| **A** | Document and fix adapter leaks | EventLogProtocol, BoundaryContractStoreProtocol, ExtractionConfigRegistryProtocol, GuideRegistryProtocol, BlobPurge/FileStorage extension; remove adapter getters from public API; WAL, Outbox, PostOffice, TTL job, libraries, data_steward use protocols only. |
| **B** | Decompose mega protocols | SemanticDataProtocol → VectorStore, SemanticGraph, CorrelationMap. KnowledgeDiscoveryProtocol → FullTextSearch, GraphQuery. Abstractions implement narrow protocols; foundation get_* return protocol types. |
| **C** | Implement five-slice ctx | Define ctx type (e.g. PlatformContext) with governance, reasoning, experience, platform, runtime. Build ctx in composition root from Public Works. Map every get_* to a slice. |
| **D** | DI: inject ctx into Runtime and Experience | Bootstrap builds ctx; runtime_main and experience_main receive ctx; attach app.state.ctx = ctx; migrate routes to Depends(get_ctx) and slice access. Remove per-service app.state keys from Experience. |
| **E** | Genesis alignment | Update BOOT_PHASES, INIT_ORDER_SPEC, genesis_protocol (and related) so Φ3 outcome is ctx built and both Runtime and Experience receive ctx; all five slices first-class. |
| **F** | Enforcement and cleanup | CI or grep: no file outside foundations/public_works/ imports adapter classes. Add "swap unit" comment to each protocol per strategic protocol rule. **Protocols locked:** [PROTOCOL_REGISTRY.md](PROTOCOL_REGISTRY.md) + PLATFORM_CONTRACT §8C; no breaking signature changes without deprecation or new version. |

**Dependencies:** A and B can be parallelized (leaks vs megas). C depends on A (ctx exposes protocol getters, no adapters). D depends on C (we need ctx to inject). E can be done alongside C–D (docs). F after A–D.

---

## 10. Summary

| Item | Strategic choice |
|------|------------------|
| **Leaks** | All removed via new protocols (EventLog, BoundaryContract, ExtractionConfig, GuideRegistry, BlobPurge/FileStorage); no adapter outside Public Works. |
| **Adapters** | No new adapters required for current scope; TelemetryAdapter wired; S3/FS deferred. Flag missing infra for product discussion. |
| **Protocols** | One per logical capability; add missing protocols for leaks; decompose SemanticData and KnowledgeDiscovery into narrow protocols. |
| **Abstractions** | Implement one or more narrow protocols; compose where needed. No mega abstraction that bundles multiple swap units. |
| **ctx** | Five slices: governance, reasoning, experience, platform, runtime. MECE; every capability has one home. |
| **DI** | Single composition root builds ctx; Runtime and Experience receive ctx; app.state.ctx = ctx; routes use Depends(get_ctx) and slice. |
| **Genesis** | Φ3 outcome = ctx built and both Runtime and Experience receive ctx; all five capability surfaces available. Experience is one of two first-class process consumers, not the only one. |

This plan is the single reference for the strategic Public Works fix. All implementation work should align to it; no short-term workarounds.
