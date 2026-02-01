# CTA Top-Down Derivation: From Platform SDK to Infrastructure

**Status:** Living document — work backwards from what Team B (Platform SDK) and Team C (frontend) have built, then build back up.  
**Purpose:** One layered specification that defines everything we need: Contract at the top (what Platform SDK and frontend expect), then Protocol → Abstraction → Adapter → Infrastructure, with Genesis at the bottom. No rules uncovered as we move up; we derive the full stack from the consumer.

**Related:** [GETTING_ON_TRACK_ASSESSMENT_AND_PLAN.md](GETTING_ON_TRACK_ASSESSMENT_AND_PLAN.md), [architecture/PUBLIC_WORKS_CTA_PATTERN.md](architecture/PUBLIC_WORKS_CTA_PATTERN.md), [INTERCEPT_ALIGNMENT_CONTRACT.md](INTERCEPT_ALIGNMENT_CONTRACT.md).

---

## Response to Team B (February 2026)

Team B’s response **makes sense** and is fully aligned with this derivation. We have incorporated their requests below.

- **Awareness of Team B work:** We recognize the 18 fake-fallback removals, intent_type on all 52 services, Control Tower thin layer, execution status endpoint, and 3 new Control Tower intents. The CTA audit focuses on **adapter leaks at the boundary** (ReasoningService, GovernanceService, intent services using _public_works); capability services are architecturally aligned.
- **LLM Protocol (P0):** Treated as **critical path**. We will not change ReasoningService’s LLM access until **get_llm_abstraction() → LLMProtocol** is available. Coordination: Team B does not merge changes to ReasoningService’s LLM wiring until Team A delivers LLMAbstraction + getter.
- **Experience Service ownership:** Clarified in §2.4 — Experience Service (experience_main.py) is the HTTP/WS gateway; **Runtime (or bootstrap) injects the Platform Boundary into Experience Service at startup** so it can build SecurityGuardSDK, TrafficCopSDK, etc. for session/auth endpoints.
- **Control Tower / WAL:** Layer 1.2 and Layer 3 now include get_execution_metrics (WAL query), compose_solution, get_solution_templates, and **WALQueryProtocol** / get_wal_query_interface().
- **Curator schema status:** Documented in §1.7 — registry_entries is durable (Supabase); IntentRegistry and SolutionRegistry are currently in-memory but **must be backed by durable storage** in the target architecture (GKE = ephemeral process memory; no persistence guarantee without explicit durable backing).
- **Migration Strategy:** New section added — we are establishing the protocol-only boundary (the new operating system); breaking change for violating services is intentional. We will provide a list of violating services when we make the change; Team B can audit for compliance now to avoid breakage, or fix after.

---

## Approach

1. **Start at the top:** What has Team B created? (PlatformContext, four services, intent services that use ctx.)
2. **Derive Layer 1 — What Platform SDK expects:** What does ctx expose? What do intent services actually call on ctx.platform, ctx.governance, ctx.reasoning, ctx.experience? That is the **contract** at the boundary.
3. **Derive Layer 2 — What must enable it:** What do Experience, Agentic, Smart City, and Runtime need to do (and provide) so that Platform SDK can deliver that contract?
4. **Derive Layer 3 — Protocols:** What protocol types must exist so that Layer 2 can be consumed only via protocols (no adapter leak)?
5. **Derive Layer 4 — Abstractions:** What abstractions implement those protocols and sit above the adapters?
6. **Derive Layer 5 — Adapters:** What adapters do those abstractions need (Supabase, Redis, Arango, GCS, OpenAI, etc.)?
7. **Derive Layer 6 — Infrastructure:** What infrastructure is behind each adapter (reachable services, config, env)?
8. **Derive Layer 7 — Genesis gaps:** Given Layer 6, is anything missing in our Genesis protocol (boot order, required config, validation)?

Then **build back up:** Ensure Genesis guarantees Layer 6; ensure we have adapters for Layer 5; abstractions for Layer 4; protocols for Layer 3; Experience/Agentic/Smart City/Runtime for Layer 2; Platform SDK receives only what Layer 1 specifies. No fallbacks for required capabilities; no adapter at the boundary.

---

## Contract fulfillment rule: no silent failure / no false success

**Universal principle for all CTA work:** We are fulfilling contracts. If we cannot do what the contract is asking, we **announce it** — we do not silently fail or return false success.

- **No silent failure:** Do not hide missing capability (e.g. “registry not available”) by returning empty data, placeholder data, or success. Raise a clear error so the caller can handle it.
- **No false success:** Do not return success when the requested operation was not fully performed (e.g. “compose solution” without actually registering). Either fulfill the contract or fail with a clear message.
- **Fail fast:** When a required dependency (getter, adapter, registry) is missing or the operation cannot be completed, raise `RuntimeError` (or equivalent) with a message that states what is missing or what failed and how to fix it (e.g. “Ensure Public Works provides get_solution_registry() and initialize() has run”).
- **Applies everywhere:** Boundary getters, protocol implementations, adapters, intent services, and any code that implements a contract. If the contract says “list solutions from registry,” then no registry ⇒ error, not a fake list. If the contract says “register and activate,” then no registry or failed register ⇒ error, not success.

This rule aligns with the existing “no fallbacks for required capabilities” and “no adapter at boundary” and extends them: **contracts are explicit; failure to fulfill them must be explicit too.**

---

## Layer 1 — What Platform SDK Expects (Contract at the Top)

*Derived from: `context.py`, four services, and actual intent-service usage of ctx.*

### 1.1 ctx shape (PlatformContext)

| Field | Type | Source | Required for MVP? |
|-------|------|--------|--------------------|
| execution_id | str | Runtime | Yes |
| intent | Intent | Runtime | Yes |
| tenant_id | str | Runtime | Yes |
| session_id | str | Runtime | Yes |
| solution_id | str | Runtime | Yes |
| state_surface | StateSurface | Runtime | Yes |
| wal | WriteAheadLog | Runtime | Yes |
| artifacts | ArtifactRegistry | Runtime | Yes |
| platform | PlatformService | Public Works + Runtime | Yes |
| governance | GovernanceService | Public Works (Smart City) | Yes |
| reasoning | ReasoningService | Public Works (Agentic) | Yes |
| experience | Dict / metadata | Experience (narrow) | Optional for MVP |

### 1.2 ctx.platform (PlatformService) — What intent services call

| Operation | Used by (examples) | What it needs underneath |
|-----------|--------------------|---------------------------|
| list_files(tenant_id, ...) | list_artifacts_service, visualize_lineage_service | File listing (file_storage) |
| get_file_metadata(file_id, tenant_id) | visualize_lineage_service | File metadata |
| get_parsed_file(...) | map_relationships_service, assess_data_quality_service | Parsed content (state or file_storage + parsing) |
| parse(...) | intent_service_base, platform_sdk __init__ example | Document parsing (file_parsing protocol) |
| ingest_file(...) | platform_service doc | Ingestion |
| visualize(...) | platform_service doc | Visual generation |
| get_pending_intents(tenant_id, artifact_id, intent_type) | platform_service doc | Registry / intent_executions |
| update_intent_status(...) | (registry) | Registry |
| store_artifact / retrieve_artifact | (artifact operations) | Artifact storage |

**Current dependency (from code):** PlatformService is **built from getters only** — it uses `public_works.get_file_storage_abstraction()`, `get_artifact_storage_abstraction()`, `get_visual_generation_abstraction()`, `get_ingestion_abstraction()`, `get_semantic_data_abstraction()`, `get_deterministic_compute_abstraction()`, `get_registry_abstraction()`, and per-type getters (e.g. `get_csv_processing_abstraction()`) for parsers. No getattr on raw attributes. Contract: Public Works must provide these via getters; state_surface from Runtime.

### 1.3 ctx.governance (GovernanceService) — What intent services call

| Role | Property | Used by (examples) | What it needs underneath |
|------|----------|--------------------|---------------------------|
| Data Steward | data_steward | intent_service_base (request_data_access) | Data governance abstraction |
| Security Guard | auth | (auth flows) | Auth abstraction |
| Curator | registry | CuratorSDK (register_capability, discover_agents, promote_to_platform_dna); **Control Tower services** (list_solutions, compose_solution, solution/capability registry queries) | Curator service (Supabase-backed) |
| Librarian | search | governance_service doc (search_knowledge) | Knowledge discovery |
| City Manager | policy | (tenant/policy) | Tenant abstraction |
| Traffic Cop | sessions | session flows, terminate_session, create_session | State (sessions) |
| Post Office | events | (event publish) | Event publisher |
| Conductor | workflows | (workflow primitives) | — |
| Nurse | telemetry | intent_service_base (record_telemetry) | Telemetry abstraction |
| Materialization Policy | materialization_policy | — | — |

**Current dependency (from code):** GovernanceService uses: get_registry_abstraction(), get_curator_service(), get_knowledge_discovery_abstraction(), get_tenant_abstraction(), get_state_abstraction(), get_event_publisher_abstraction(), get_telemetry_abstraction(), get_auth_abstraction(), get_data_governance_abstraction(), get_materialization_policy(). No getattr on raw attributes; no supabase_adapter at boundary. Contract: Public Works must provide these via getters only.

**Anti-pattern (to fix):** Some intent services use `ctx.platform._public_works` and `get_auth_abstraction()`, `getattr(..., 'traffic_cop_sdk')`. They should use only ctx.governance.auth and ctx.governance.sessions.

### 1.4 ctx.reasoning (ReasoningService) — What intent services call

| Component | Operation | Used by | What it needs underneath |
|-----------|-----------|---------|---------------------------|
| llm | complete(prompt, model, ...) | reasoning_service doc, agents | LLM completion (OpenAI/HuggingFace) |
| llm | embed(...) | (embeddings) | Embedding API |
| agents | get(id), invoke(id, params), collaborate(...) | Many intent services (generate_sop, assess_data_quality, map_relationships, etc.) | Agent registry + invocation (Agentic) |

**Current dependency (from code):** ReasoningService uses **getattr(public_works, 'openai_adapter', None)** and **getattr(public_works, 'huggingface_adapter', None)** — **adapter leak**. Contract should be: Public Works provides an **LLM protocol** (complete, embed), and an **Agentic surface** (agents.get, invoke, collaborate) built behind the boundary. No raw adapter at boundary.

### 1.5 ctx.experience

Currently a narrow surface (metadata Dict). Experience layer provides session/UX metadata; for MVP may stay minimal.

### 1.6 Runtime-provided (state_surface, wal, artifacts)

Provided by Runtime, not Public Works. Runtime must build them from Public Works getters (state_abstraction, wal_backend) and artifact_storage where applicable. So Layer 2 (Runtime) depends on Public Works providing get_state_abstraction(), get_wal_backend(), get_artifact_storage_abstraction().

**Important:** Runtime does **not** store "stuff." The **state surface** records **facts, references, and pointers** (what happened, where things are, what to call). It is not the authoritative store for registries (solutions, intent metadata, capabilities). Authoritative registry data that must survive restarts belongs in **durable storage** (e.g. Curator/Supabase), not in process memory — especially in GKE or any containerized environment where in-memory is ephemeral unless there is an explicit durable backing (e.g. Redis, WAL, or "on mount" persistence, which should be rare and explicit).

### 1.7 Curator schema status (for Team B)

**Persistence principle:** In GKE (and containerized backends generally), **in-memory is ephemeral** — there is no persistence guarantee unless there is an explicit durable backing (e.g. Supabase, Redis, WAL, or rare "on mount" persistence). So registries that must survive restarts (solutions, intent metadata, capability registry) must **not** rely on process memory as the system of record; they should be backed by durable storage (Curator/Supabase or equivalent).

| Component | Current implementation | Durable store (target) | Notes |
|-----------|-------------------------|-------------------------|-------|
| **registry_entries** | RegistryAbstraction (Public Works) | **Yes** — Supabase table `registry_entries` (entry_type, entry_key, tenant_id, data, version, created_at) | Used by Curator/RegistryAbstraction for capability/artifact metadata. If the table does not exist, add a migration; code fails gracefully if client/table missing. |
| **IntentRegistry** | Runtime process memory today | **Should be durable** | Intent handler registration and metadata must survive restarts in GKE. Target: back with Curator/registry_entries or dedicated table; in-memory only as cache/lookup, not source of truth. |
| **SolutionRegistry** | Platform SDK / Runtime process memory today | **Should be durable** | Solution registration for Control Tower (list_solutions, compose_solution) must survive restarts. Target: back with Curator/registry_abstraction or dedicated solution table; in-memory only as cache, not source of truth. |
| **RealmRegistry** | Runtime process memory today | Optional (health can be recomputed) | Realm health; can be derived at startup if needed. If it must persist, back with durable store. |

**Migration path:** CuratorService already requires Supabase and get_curator_service() at boundary. (1) Ensure registry_entries exists (migration if needed). (2) Introduce durable backing for IntentRegistry and SolutionRegistry (Curator/registry_entries or dedicated tables) so that in GKE, container restarts do not lose registry data. (3) In-memory registries become caches or thin wrappers over the durable store, not the sole copy. Timeline: Team A can provide migration script and schema when Curator schema is finalized.

---

## Layer 2 — What Experience, Agentic, Smart City, and Runtime Must Do

*To be filled with rigor. Summary below.*

### 2.1 Runtime

- Must build: state_surface (from state_abstraction), wal (from wal_backend), artifacts (artifact_registry from artifact_storage + registry where needed).
- **State surface** records **facts, references, and pointers** — not the authoritative store for "stuff." Durable registries (solutions, intent metadata, capabilities) live in Curator/durable storage; in GKE, in-memory is ephemeral and must not be the only copy.
- Must call Public Works only via boundary getters: get_state_abstraction(), get_wal_backend(), get_artifact_storage_abstraction(), get_registry_abstraction() (if needed for artifact index).
- Must inject state_surface, wal, artifacts into PlatformContextFactory along with public_works. IntentRegistry and SolutionRegistry, in the target architecture, should be backed by durable storage (Curator/registry) so they survive restarts.

### 2.2 Smart City (9 roles)

- Each role (Data Steward, Security Guard, Curator, Librarian, City Manager, Traffic Cop, Post Office, Nurse, Conductor) is exposed as ctx.governance.X.
- GovernanceService builds each SDK from **boundary getters only**. No getattr(public_works, 'supabase_adapter'). No getattr(public_works, 'auth_abstraction') if we have get_auth_abstraction() — use getters consistently.
- Curator: get_curator_service() → CuratorProtocol (Supabase-backed). Data Steward: get_data_governance_abstraction() or similar (no supabase_adapter). Auth: get_auth_abstraction(). Tenant: get_tenant_abstraction(). Sessions: Traffic Cop needs state or session abstraction. Events: get_event_publisher_abstraction(). Telemetry: get_telemetry_abstraction(). Search: get_knowledge_discovery_abstraction(). Policy: get_tenant_abstraction() or policy abstraction.

### 2.3 Agentic

- Must provide: agents (get, invoke, collaborate, list) and llm (complete, embed).
- LLM must be provided via a **protocol** (e.g. LLMProtocol or ReasoningProtocol) that Public Works exposes (get_llm_abstraction() or get_reasoning_abstraction()), not by passing openai_adapter / huggingface_adapter to ReasoningService.
- Agents: Agentic component builds agent registry and invocation; exposed to Platform SDK via ReasoningService.agents. May need get_agent_registry() or similar from Public Works / Agentic boundary.

### 2.4 Experience

- **Experience Service (experience_main.py)** is the HTTP/WS gateway: `/api/session/*`, `/api/intent/submit`, `/api/runtime/agent` (WebSocket), `/api/admin/*`, `/api/execution/*`. It does **not** build ctx; it submits intents to Runtime and exposes session/auth/Control Tower APIs.
- **Runtime (or bootstrap) must inject the Platform Boundary into Experience Service at startup** so Experience can build SecurityGuardSDK, TrafficCopSDK, etc. for session/auth endpoints — same boundary getters as GovernanceService (get_auth_abstraction(), get_state_abstraction(), etc.), not raw adapters. If Experience runs in the same process as Runtime, it shares the same public_works; if separate, bootstrap passes the boundary (or a client to Runtime) at startup.
- ctx.experience remains a narrow metadata Dict for now; Experience layer may provide get_experience_metadata() later. For MVP, minimal.

---

## Layer 3 — Protocols Needed

*Derived from Layer 1 and 2. Each capability at the boundary must have a protocol type. No adapter at boundary.*

| Capability | Protocol (existing or to define) | Returned by (boundary getter) | Notes |
|------------|----------------------------------|-------------------------------|-------|
| State | StateManagementProtocol | get_state_abstraction() | Existing |
| File storage | FileStorageProtocol | get_file_storage_abstraction() | Existing |
| Artifact storage | ArtifactStorageProtocol | get_artifact_storage_abstraction() | Existing |
| Registry | Registry protocol (Curator/lineage) | get_registry_abstraction() | Existing |
| Auth | AuthenticationProtocol | get_auth_abstraction() | Existing |
| Tenant | TenancyProtocol | get_tenant_abstraction() | Existing |
| Curator | CuratorProtocol | get_curator_service() | Existing |
| Knowledge discovery | KnowledgeDiscoveryProtocol | get_knowledge_discovery_abstraction() | Existing |
| Event publisher | EventPublisherProtocol | get_event_publisher_abstraction() | Existing |
| Telemetry | TelemetryProtocol (or abstraction interface) | get_telemetry_abstraction() | Existing |
| WAL / event log | EventLogProtocol | get_wal_backend() | Existing |
| Document parsing | FileParsingProtocol | get_document_parsing() | Existing (router) |
| Visual generation | VisualGenerationProtocol | get_visual_generation_abstraction() | Existing |
| Ingestion | IngestionProtocol | get_ingestion_abstraction() | Existing |
| Semantic data | SemanticDataProtocol | get_semantic_data_abstraction() | Existing |
| Deterministic compute | DeterministicEmbeddingStorageProtocol | get_deterministic_compute_abstraction() | Existing |
| **LLM** | **LLMProtocol** | **get_llm_abstraction()** | **Done:** ReasoningService uses getter only; no adapter at boundary |
| **Data governance** | **DataGovernanceProtocol** | **get_data_governance_abstraction()** | **Done:** DataStewardPrimitives built inside PW; GovernanceService uses getter only |
| **WAL Query** | **WALQueryProtocol** | **get_wal_query_interface()** | **Done:** GetExecutionMetricsService uses ctx.platform.get_wal_query_interface(); WalQueryBackend aggregates from EventLogProtocol |
| **Solution registry** | **SolutionRegistryProtocol** | **get_solution_registry()** | **Done:** list_solutions, compose_solution use ctx.platform.get_solution_registry(); in-memory MVP, durable later |
| Service discovery | ServiceDiscoveryProtocol | get_service_discovery_abstraction() | Existing |
| Lineage backend | LineageProvenanceProtocol | get_lineage_backend() | Existing (no adapter leak) |

**Gaps closed:** (1) **P0 LLM:** LLMProtocol + get_llm_abstraction(); ReasoningService uses getter only. (2) **Data governance:** DataGovernanceProtocol + get_data_governance_abstraction(); GovernanceService uses getter only. (3) **P2 WAL Query:** WALQueryProtocol + get_wal_query_interface(); GetExecutionMetricsService uses ctx.platform.get_wal_query_interface(). (4) **Solution registry:** SolutionRegistryProtocol + get_solution_registry(); ListSolutionsService and ComposeSolutionService use ctx.platform.get_solution_registry(); in-memory MVP, durable backing later. (5) **Civic systems — Agentic:** EmbeddingService (embedding_agent) and SemanticSignalExtractor use get_llm_abstraction() only; no openai_adapter/llm_adapter_registry at boundary. (6) **Civic systems — Governance:** GovernanceService uses get_materialization_policy() (Public Works getter); no getattr(public_works, "materialization_policy").

---

## Layer 4 — Abstractions

*Each protocol is implemented by an abstraction that uses adapters internally. Adapters never cross the boundary.*

| Protocol | Abstraction (existing or to add) | Adapter(s) used |
|----------|-----------------------------------|------------------|
| StateManagementProtocol | StateManagementAbstraction | RedisAdapter, ArangoAdapter |
| FileStorageProtocol | FileStorageAbstraction | GCSAdapter, SupabaseFileAdapter |
| ArtifactStorageProtocol | ArtifactStorageAbstraction | GCSAdapter, Supabase (metadata) |
| Registry (lineage/artifact metadata) | RegistryAbstraction | SupabaseAdapter |
| AuthenticationProtocol | AuthAbstraction | SupabaseAdapter (auth) |
| TenancyProtocol | TenantAbstraction | SupabaseAdapter, RedisAdapter (cache) |
| CuratorProtocol | CuratorService (implementation) | SupabaseAdapter, artifact storage |
| KnowledgeDiscoveryProtocol | KnowledgeDiscoveryAbstraction | MeilisearchAdapter, ArangoAdapter |
| EventPublisherProtocol | (RedisStreamsPublisher / Outbox) | RedisAdapter |
| TelemetryProtocol | TelemetryAbstraction (or adapter as abstraction) | TelemetryAdapter (OTLP) |
| EventLogProtocol | WAL backend implementation | RedisAdapter |
| FileParsingProtocol | DocumentParsingRouter + type-specific abstractions | PdfProcessingAbstraction, CsvProcessingAbstraction, … (each uses adapters) |
| VisualGenerationProtocol | VisualGenerationAbstraction | VisualGenerationAdapter |
| IngestionProtocol | IngestionAbstraction | UploadAdapter, GCS, Supabase |
| SemanticDataProtocol | SemanticDataAbstraction | ArangoAdapter |
| DeterministicEmbeddingStorageProtocol | DeterministicComputeAbstraction | DuckDBAdapter |
| **LLMProtocol** | **LLMAbstraction** | **OpenAIAdapter, HuggingFaceAdapter** |
| DataGovernanceProtocol | DataStewardPrimitives (built inside PW) | BoundaryContractStoreBackend (SupabaseAdapter inside PW) |
| WALQueryProtocol | WalQueryBackend | EventLogProtocol (Redis Streams via get_wal_backend()) |
| SolutionRegistryProtocol | SolutionRegistry (in-memory MVP) | Durable later: Curator/registry_entries |
| ServiceDiscoveryProtocol | ServiceDiscoveryAbstraction | ConsulAdapter |
| LineageProvenanceProtocol | Lineage backend implementation | ArangoAdapter |

Processing abstractions (PDF, CSV, Excel, Word, etc.) are per-type; they may use PDF adapter, CSV adapter, etc. PlatformService gets them via get_document_parsing() (router) or get_*_processing_abstraction(); all sit above adapters.

---

## Layer 5 — Adapters

*Each abstraction uses one or more adapters. Adapters never cross the boundary; only protocol-typed abstractions are returned by Public Works getters.*

| Adapter | Used by (abstractions) | Purpose |
|---------|------------------------|---------|
| SupabaseAdapter | RegistryAbstraction, AuthAbstraction, TenantAbstraction, CuratorService, DataStewardPrimitives (internal) | DB, auth, tenancy, Curator tables, data governance |
| RedisAdapter | StateManagementAbstraction, WAL backend, EventPublisher, TenantAbstraction (cache) | Hot state, event log, cache |
| ArangoAdapter | StateManagementAbstraction, SemanticDataAbstraction, KnowledgeDiscoveryAbstraction, Lineage backend | Durable state, graph, semantic, lineage |
| GCSAdapter | FileStorageAbstraction, ArtifactStorageAbstraction | Blob storage |
| SupabaseFileAdapter | FileStorageAbstraction (metadata) | File metadata, coordination |
| OpenAIAdapter | LLMAbstraction (to add) | Completion, embeddings |
| HuggingFaceAdapter | LLMAbstraction (to add) | Alternative models |
| MeilisearchAdapter | KnowledgeDiscoveryAbstraction, SemanticSearchAbstraction | Full-text search |
| ConsulAdapter | ServiceDiscoveryAbstraction | Service discovery |
| DuckDBAdapter | DeterministicComputeAbstraction | Deterministic embeddings, analytics |
| TelemetryAdapter | TelemetryAbstraction | OTLP tracing/metrics |
| PdfAdapter, CsvAdapter, ExcelAdapter, WordAdapter, etc. | Per-type processing abstractions | Document parsing |
| VisualGenerationAdapter | VisualGenerationAbstraction | Visual generation |
| UploadAdapter | IngestionAbstraction | Upload handling |

---

## Layer 6 — Infrastructure

*What infrastructure is behind each adapter. Aligned with PLATFORM_CONTRACT §3 and PRE_BOOT_SPEC.*

| Adapter | Infrastructure | Required env / config | Genesis / pre-boot check? |
|---------|-----------------|------------------------|---------------------------|
| SupabaseAdapter | Supabase (DB + Auth + File API) | SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_KEY | Yes (G3) |
| RedisAdapter | Redis | config["redis"] (host, port, db, password) or REDIS_URL | Yes (G3) |
| ArangoAdapter | ArangoDB | arango_url, arango_username, arango_password, arango_database | Yes (G3) |
| GCSAdapter | Google Cloud Storage | gcs_project_id, gcs_bucket_name, gcs_credentials_json | Yes (G3) |
| SupabaseFileAdapter | Same as Supabase | Same | Yes (G3) |
| MeilisearchAdapter | Meilisearch | meilisearch_host, meilisearch_port, meilisearch_key | Yes (G3) |
| DuckDBAdapter | DuckDB | config["duckdb"] (database_path, read_only) | Yes (G3) |
| ConsulAdapter | Consul | config["consul"] (host, port, token) | Yes (G3) |
| TelemetryAdapter | OpenTelemetry OTLP | otel_exporter_otlp_endpoint | Yes when configured (G3) |
| OpenAIAdapter | OpenAI API | (required when LLM intents run; not blocking Φ3 per PRE_BOOT_SPEC) | No at boot |
| HuggingFaceAdapter | HuggingFace API | (same) | No at boot |

**Order (PRE_BOOT_SPEC):** Data plane first — Redis → ArangoDB → Supabase → GCS → Meilisearch → DuckDB; then Control plane — Consul; then Telemetry — OTLP when configured. On first failure: exit immediately; no partial init.

---

## Layer 7 — Genesis Gaps

*Given Layer 6 (required infrastructure), is anything missing in Genesis?*

- Genesis must: load config (G2), validate pre-boot / Public Works reachable (G3), create adapters and abstractions in correct order, fail fast if required infra is missing.
- If a capability is **required** for MVP and it depends on an adapter, that adapter’s infra must be **required** at boot and checked in Genesis (or in Public Works initialize() and treated as Genesis failure).
- Curator requires Supabase → Genesis (or Public Works) must fail if Supabase is missing when Curator is required.
- **Gap list (filled):** (1) Pre-boot (Gate G3): `pre_boot_validate(config)` in `bootstrap/pre_boot.py` validates Redis, Arango, Supabase, GCS, Meilisearch, DuckDB, Consul, Telemetry; exits on first failure. (2) Public Works `initialize()` assumes pre-boot passed; returns False on exception (caller must abort). (3) Order aligned with PRE_BOOT_SPEC. (4) Pre-boot ensures required infra is reachable before initialize() is called. (Previously: e.g. “Genesis does not validate Meilisearch reachability”; “Public Works initialize() does not fail when Redis is missing.”

---

## Migration Strategy (for Team B coordination)

**Goal:** Establish the **protocol-only boundary** — the new operating system. Services that **natively conform** (use only ctx.governance.*, ctx.platform.*, no _public_works, no adapter access at boundary) will continue to work. Services that **use improper patterns** (e.g. ctx.platform._public_works, getattr for security_guard_sdk / traffic_cop_sdk / get_auth_abstraction) **will break** when we enforce the boundary. That breakage is **intentional**: we are birthing the new contract; the purpose is for services to conform to it, not to preserve every existing anti-pattern.

**Principles:**
- **Incremental:** One boundary change at a time (e.g. LLM first, then Data Steward, then removal of adapter leaks).
- **Explicit coordination:** Team B does not merge changes to ReasoningService LLM wiring (or GovernanceService Data Steward / auth wiring) until Team A delivers the corresponding protocol + getter. After that, we enforce the boundary; conforming services stay green, violating ones break until fixed.
- **We do not guarantee zero breaking changes** for services that violate the boundary. We *do* provide a path to avoid breakage: compliance before we flip the switch.

**Violating services and compliance:**

- When we make the change (remove _public_works, enforce getters-only at boundary), we **will provide Team B with a list of violating services** (those that touch _public_works, getattr for adapters/SDKs, etc.) so they know exactly what will break and what to fix.
- **Suggestion for Team B:** Audit intent services **now** for compliance — refactor to use only **ctx.governance.auth**, **ctx.governance.sessions**, **ctx.platform.*** (no ctx.platform._public_works, no getattr(..., 'security_guard_sdk'|'traffic_cop_sdk'|'get_auth_abstraction')). Services that already conform will not break when we enforce the boundary. Services that are updated to conform before we make the change avoid breakage; those that are not will break and will need to be updated to conform after.

**List of violating services (as of audit):**

| Location | Service | Violation | Fix | Status |
|----------|---------|-----------|-----|--------|
| capabilities/security | TerminateSessionService | ctx.platform._public_works, getattr traffic_cop_sdk | Use ctx.governance.sessions | **Done** |
| capabilities/security | CreateSessionService | Same | Use ctx.governance.sessions | **Done** |
| capabilities/security | CheckEmailAvailabilityService | _public_works, security_guard_sdk, get_auth_abstraction() | Use ctx.governance.auth | **Done** |
| capabilities/security | CreateUserAccountService | Same | Use ctx.governance.auth | **Done** |
| capabilities/security | ValidateAuthorizationService | Same | Use ctx.governance.auth | **Done** |
| capabilities/security | ValidateTokenService | Same | Use ctx.governance.auth | **Done** |
| realms/security | create_user_account, authenticate_user, validate_authorization, validate_token, create_session | getattr(self.public_works, 'security_guard_sdk'\|'traffic_cop_sdk') | Use get_security_guard_sdk() / get_traffic_cop_sdk() (Public Works getters) | **Done** |
| civic_systems/agentic | EmbeddingService (embedding_agent), SemanticSignalExtractor | getattr(public_works, 'openai_adapter'\|'llm_adapter_registry') | Use get_llm_abstraction() only | **Done** |

**Suggested order:**

| Step | Team A delivers | Team B (and Experience) | Coordination |
|------|------------------|--------------------------|--------------|
| 1 | **LLMProtocol** + **LLMAbstraction** + **get_llm_abstraction()** | No change to ReasoningService LLM wiring until Step 1 is on main | Team B freezes ReasoningService LLM wiring; Team A merges getter + ReasoningService update so 18 services use protocol only |
| 2 | **get_data_governance_abstraction()**; DataStewardPrimitives built inside Public Works (no supabase_adapter at boundary) | — | Team A removes getattr(public_works, 'supabase_adapter') from GovernanceService |
| 3 | Enforce boundary: no _public_works / adapter at boundary | **Done (capabilities + realms):** Capability and realm security services use boundary getters (ctx.governance.auth/sessions or get_security_guard_sdk/get_traffic_cop_sdk) | Realms/security remediated; list in CTA updated |
| 4 | PlatformService built from getters only (or get_platform_capabilities()) | — | Optional; reduces getattr surface |
| 5 | **WALQueryProtocol** + **get_wal_query_interface()** | **Done:** WalQueryBackend + GetExecutionMetricsService uses ctx.platform.get_wal_query_interface() | P2 done |

**Coordination rule:** Getters first, then enforce boundary. Conforming services stay green; violating services break until they conform. Team B can audit now for compliance to avoid breakage, or fix after we provide the list of violating services.

---

## How to Use This Document

1. **Layer 1:** Audit all intent services and four services to complete “what Platform SDK expects” and “what it currently uses (including violations).” Remove any use of _public_works or adapters at boundary; document as “must use only ctx.governance.X / ctx.platform.X.”
2. **Layer 2:** For each capability in Layer 1, write what Experience/Agentic/Smart City/Runtime must do and provide. Expand Smart City into 9 roles with required getters per role.
3. **Layer 3:** List every protocol type; add missing ones (e.g. LLMProtocol, DataGovernanceProtocol).
4. **Layer 4:** List abstraction per protocol; add missing abstractions (e.g. LLMAbstraction that wraps OpenAI + HuggingFace).
5. **Layer 5:** List adapter per abstraction.
6. **Layer 6:** List infrastructure per adapter; align with PLATFORM_CONTRACT.
7. **Layer 7:** Compare with genesis_protocol and PRE_BOOT_SPEC; list Genesis gaps.
8. **Build back up:** Fix Genesis (Layer 7); ensure infra and adapters (5–6); implement or fix abstractions and protocols (3–4); ensure Experience/Agentic/Smart City/Runtime provide only via protocols (2); ensure Platform SDK uses only ctx and boundary getters (1). No fallbacks for required; no adapter at boundary.

---

## Summary

This document is the **single layered specification** for the platform. We start with what Team B has created (Platform SDK / ctx), derive what it expects and what it currently uses (including violations), then work down: what enables it → protocols → abstractions → adapters → infrastructure → Genesis gaps. Then we build back up with proper rigor.

**Layers 1–7 are now populated:** Layer 1 includes the full audit of ctx usage and violations; Layer 2 defines Runtime, Smart City (9 roles with getters), Agentic, and Experience; Layers 3–5 list protocols, abstractions, and adapters; Layer 6 aligns infrastructure with PLATFORM_CONTRACT and PRE_BOOT_SPEC; Layer 7 lists Genesis gaps and fixes. Smart City (9 roles, SDKs, primitives), LLM boundary (get_llm_abstraction), and Data Steward boundary (get_data_governance_abstraction, no supabase_adapter leak) are the main implementation targets.

---

## Addendum (inline edits not applying — apply manually if desired)

**Note:** The following updates were intended as inline edits; they are recorded here because inline editing in the doc was not working.

1. **Layer 7 — Gap list (filled):** Replace the placeholder “Gap list (to fill): e.g. …” with: **(1)** Pre-boot (Gate G3): `pre_boot_validate(config)` in `bootstrap/pre_boot.py` validates Redis, Arango, Supabase, GCS, Meilisearch, DuckDB, Consul, Telemetry; exits on first failure. **(2)** Public Works `initialize()` assumes pre-boot has passed; returns False on exception (caller must abort). **(3)** Order aligned with PRE_BOOT_SPEC. **(4)** Pre-boot ensures required infra is reachable before initialize() is called.

2. **Suggested order — Step 3:** Update the “Team B (and Experience)” cell from “**Done (capabilities):** … realms/security still pending” to “**Done (capabilities + realms):** Capability and realm security services use boundary getters (ctx.governance.auth/sessions or get_security_guard_sdk/get_traffic_cop_sdk).” Update the Coordination cell to “Realms/security remediated; list in CTA updated.”
