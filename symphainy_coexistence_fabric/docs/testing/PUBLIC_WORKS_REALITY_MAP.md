# Public Works Reality Map

**Purpose:** Evidence from the Public Works probe (Phases A–F). Updated as we go. Links to [PUBLIC_WORKS_PROBE_PLAN.md](../PUBLIC_WORKS_PROBE_PLAN.md).

**Pattern:** 4-layer — Adapter → Abstraction → Protocol → Service (foundation service). Services were built for a prior architecture; we are reviewing how they should map to current platform vision.

**Vision (current):** Public Works = Storage adapters (GCS, S3, FS), Compute adapters, Queue adapters, Network adapters. Guarantees: Uniform interfaces, Hot-swappable backends, Deterministic behavior.

---

## Phase A — Adapter inventory

Per-adapter: purpose, config driver, wired at boot?, used by which abstraction(s), **vision category** (Storage | Compute | Queue | Network | Other). "Other" = parsing, search, auth, etc. — may align to vision under a different name or need reclassification.

### 1. Infrastructure / state / storage (vision: Storage, Queue, Network)

| Adapter | Config driver | Wired at boot? | Used by abstraction(s) | Vision category | Notes |
|---------|----------------|----------------|------------------------|------------------|-------|
| **RedisAdapter** | `config["redis"]` (host, port, db, password) | Yes (if redis present) | StateManagement, WAL, TenantAbstraction, EventPublisher | **Queue** (cache, WAL, events) | connect() in _create_adapters. Pre-boot validates Redis. |
| **ConsulAdapter** | `config["consul"]` (host, port, token) | Yes (if consul present) | ServiceDiscoveryAbstraction | **Network** (service discovery) | connect() in _create_adapters. Pre-boot validates Consul. |
| **ArangoAdapter** | `arango_url`, `arango_username`, `arango_password`, `arango_database` | Yes (if arango_url) | StateManagement, SemanticData, KnowledgeDiscovery, etc. | **Storage** (durable state, graph) | connect() async. Pre-boot validates Arango. |
| **ArangoGraphAdapter** | Wraps ArangoAdapter | Yes (if ArangoAdapter created) | KnowledgeDiscoveryAbstraction | **Storage** (graph) | Created right after ArangoAdapter. |
| **MeilisearchAdapter** | `meilisearch_host`, `meilisearch_port`, `meilisearch_key` | Always (defaults) | SemanticSearchAbstraction | **Storage** (search index) or **Compute** (search) | connect() may fail; log warning. Pre-boot validates Meilisearch. |
| **SupabaseAdapter** | `supabase_url`, `supabase_anon_key`, `supabase_service_key`, jwks, jwt_issuer | Yes (if url + anon_key) | AuthAbstraction, RegistryAbstraction, TenantAbstraction | **Storage** (DB/metadata) + **Network** (auth) | Pre-boot validates Supabase. |
| **SupabaseFileAdapter** | `supabase_url`, `supabase_service_key` | Yes (if both) | FileStorage, FileManagement, ArtifactStorage | **Storage** (file metadata) | connect() async. |
| **GCSAdapter** | `gcs_project_id`, `gcs_bucket_name`, `gcs_credentials_json` | Yes (required) | FileStorage, FileManagement, ArtifactStorage | **Storage** (blob storage) | Required; RuntimeError if missing. Pre-boot validates GCS. |
| **DuckDBAdapter** | `config["duckdb"]` (database_path, read_only) | Yes (if duckdb present) | DeterministicComputeAbstraction | **Compute** (deterministic embeddings/analytics) | connect() async. Pre-boot validates DuckDB. |

### 2. Parsing / document (vision: not explicit — "Other" or future Compute?)

| Adapter | Config driver | Wired at boot? | Used by abstraction(s) | Vision category | Notes |
|---------|----------------|----------------|------------------------|------------------|-------|
| **CsvProcessingAdapter** | — | Always | CsvProcessingAbstraction, parsing abstractions | **Other** (parsing) | No config; created unconditionally. |
| **ExcelProcessingAdapter** | — | Always | ExcelProcessingAbstraction | **Other** (parsing) | Same. |
| **PdfProcessingAdapter** | — | Always | PdfProcessingAbstraction | **Other** (parsing) | Same. |
| **WordProcessingAdapter** | — | Always | WordProcessingAbstraction | **Other** (parsing) | Same. |
| **HtmlProcessingAdapter** | — | Always | HtmlProcessingAbstraction | **Other** (parsing) | Same. |
| **ImageProcessingAdapter** | — | Always | ImageProcessingAbstraction | **Other** (parsing/OCR) | Same. |
| **JsonProcessingAdapter** | — | Always | JsonProcessingAbstraction | **Other** (parsing) | Same. |
| **KreuzbergAdapter** | `config["kreuzberg"]` | No (optional) | KreuzbergProcessingAbstraction | **Other** (mainframe/legacy?) | Not created if config missing. |
| **MainframeProcessingAdapter** | (created in _create_abstractions with state) | Later | MainframeProcessingAbstraction | **Other** (mainframe parsing) | See foundation_service. |

### 3. Ingestion / upload (vision: Storage or Network?)

| Adapter | Config driver | Wired at boot? | Used by abstraction(s) | Vision category | Notes |
|---------|----------------|----------------|------------------------|------------------|-------|
| **UploadAdapter** | — (needs file_storage_abstraction) | After file_storage | IngestionAbstraction | **Storage** (ingest) | Created in _create_abstractions. |
| **APIAdapter** | — | After file_storage | IngestionAbstraction | **Network** (API ingest) | Same. |
| **EDIAdapter** | `config["edi"]` | No (optional) | IngestionAbstraction | **Other** (EDI) | Not created if edi missing. |

### 4. LLM / compute (vision: Compute)

| Adapter | Config driver | Wired at boot? | Used by abstraction(s) | Vision category | Notes |
|---------|----------------|----------------|------------------------|------------------|-------|
| **OpenAIAdapter** | `openai_api_key`, `openai_base_url` | No (optional) | (Realms/capabilities use via public_works) | **Compute** (LLM) | Log warning if missing. |
| **HuggingFaceAdapter** | `huggingface_endpoint_url`, `huggingface_api_key` | No (optional) | (Embeddings/capabilities) | **Compute** (embeddings) | Log warning if missing. |

### 5. Other (visual, telemetry, JWKS)

| Adapter | Config driver | Wired at boot? | Used by abstraction(s) | Vision category | Notes |
|---------|----------------|----------------|------------------------|------------------|-------|
| **VisualGenerationAdapter** | — | Always | VisualGenerationAbstraction | **Other** (visual gen) or **Compute** | No config. |
| **SupabaseJWKSAdapter** | (inside SupabaseAdapter) | If Supabase | Auth/JWT validation | **Network** (auth) | Internal to Supabase adapter. |
| **TelemetryAdapter** | — | (Not in _create_adapters list in foundation_service) | — | **Other** | Present in adapters/; need to check if wired. |

### 6. Not wired in foundation_service._create_adapters (present in adapters/ only)

| Adapter | Wired? | Notes |
|---------|--------|-------|
| **as2_decryption** | No (utility?) | File in adapters/; not instantiated in _create_adapters. |
| **file_parsing/** (copybook, metadata_extractor) | Via mainframe? | Subpackage; used by mainframe parsing. |
| **redis_streams_publisher** | No (optional EventPublisher) | Import in _create_abstractions for EventPublisher; module may be missing. |

---

## Phase A — Summary (what we find vs what vision needs)

**Vision says:** Public Works = Storage (GCS, S3, FS), Compute, Queue, Network. Uniform interfaces, hot-swappable backends, deterministic behavior.

**What we have:**

- **Storage:** GCS, Supabase (DB + file metadata), Arango (state, graph), Meilisearch (search index). No S3 or generic FS adapter in this list — GCS and Supabase file are the storage backends. **Aligns** if we treat "FS" as "file storage abstraction" backed by GCS + Supabase file.
- **Compute:** DuckDB (deterministic compute), OpenAI, HuggingFace. **Aligns.** Parsing (CSV, PDF, etc.) could be considered "compute" for document processing — currently "Other."
- **Queue:** Redis (WAL, cache, events). **Aligns.** EventPublisher (Redis Streams) optional.
- **Network:** Consul (service discovery), Supabase (auth/API). **Aligns.** API adapter for ingestion is network-side.

**Gaps / questions for later phases:**

1. **Parsing adapters:** Vision doesn't list "parsing" explicitly. Are they Compute? Or do they belong under a different foundation (e.g. "content pipeline")? Document as "Other" until vision or reconciliation clarifies.
2. **Service exposure:** Foundation service exposes many attributes (state_abstraction, file_storage_abstraction, registry_abstraction, etc.). Who actually receives them? Runtime gets public_works; realms get public_works. Do we expose the right surface for current vision (Experience SDK, runtime contracts, Curator)? **Phase E — service mapping.**
3. **Startup behavior:** Several adapters call `connect()` or `await .connect()` inside _create_adapters. Pre-boot already validated connectivity; is adapter connect() redundant or doing more (e.g. schema)? **Phase E — refactor backlog.**
4. **TelemetryAdapter:** In adapters/ but not in _create_adapters — confirm if used elsewhere or legacy.

---

## Phase B — Abstractions

Per-abstraction: name, adapters used, protocol(s) implemented, foundation service attr, **civic_system** (Smart City | Agentic | Experience | Platform). Civic system is part of the abstraction's **shape** when registered with Curator; only the context factory (Platform) or the owning civic system may read that slice.

**Agreed pattern:** Smart City = governance/policy/security; Agentic = reasoning/knowledge; Experience = user-facing interaction; Platform = "other" — what intent services need (storage, parsing, registry, state, etc.). Platform SDK exposes only **Platform**-category abstractions on `ctx`; civic abstractions are mediated via wrappers.

### 1. Infrastructure / state / registry (wired at boot)

| Abstraction | Adapters used | Protocol(s) | Foundation attr | Civic system | Notes |
|-------------|----------------|-------------|-----------------|--------------|-------|
| **StateManagementAbstraction** | Redis, Arango | StateManagementProtocol | state_abstraction | **Platform** | State surface backing; intents use via ctx. |
| **ServiceDiscoveryAbstraction** | Consul | ServiceDiscoveryProtocol | service_discovery_abstraction | **Platform** | Service discovery for runtime/services. |
| **RegistryAbstraction** | Supabase | — | registry_abstraction | **Platform** | Lineage, metadata, registry; intents use via ctx. |
| **AuthAbstraction** | Supabase | AuthenticationProtocol | auth_abstraction | **Smart City** | Governance/security; mediated only. |
| **TenantAbstraction** | Supabase, Redis | TenancyProtocol | tenant_abstraction | **Smart City** | Governance/tenancy; mediated only. |
| **AuthorizationAbstraction** | (not wired in foundation_service) | AuthorizationProtocol | — | **Smart City** | Present in abstractions/; assign when wired. |

### 2. Storage / file / artifact (wired at boot)

| Abstraction | Adapters used | Protocol(s) | Foundation attr | Civic system | Notes |
|-------------|----------------|-------------|-----------------|--------------|-------|
| **FileStorageAbstraction** | GCS, SupabaseFile | FileStorageProtocol | file_storage_abstraction | **Platform** | Blob + metadata; intents use via ctx. |
| **FileManagementAbstraction** | GCS, SupabaseFile | FileManagementProtocol | file_management_abstraction | **Platform** | File ops (get_parsed_file, etc.). |
| **ArtifactStorageAbstraction** | GCS, SupabaseFile | ArtifactStorageProtocol | artifact_storage_abstraction | **Platform** | Artifact storage for intents. |

### 3. Reasoning / knowledge (wired at boot)

| Abstraction | Adapters used | Protocol(s) | Foundation attr | Civic system | Notes |
|-------------|----------------|-------------|-----------------|--------------|-------|
| **SemanticSearchAbstraction** | Meilisearch | SemanticSearchProtocol | semantic_search_abstraction | **Agentic** | Search for agents; mediated via ctx.reasoning. |
| **KnowledgeDiscoveryAbstraction** | Meilisearch, ArangoGraph, Arango | KnowledgeDiscoveryProtocol | knowledge_discovery_abstraction | **Agentic** | Graph/knowledge for agents. |
| **SemanticDataAbstraction** | Arango | SemanticDataProtocol | semantic_data_abstraction | **Platform** | Store/query semantic content; intents (content/insights) use via ctx. |
| **KnowledgeGovernanceAbstraction** | (not wired in foundation_service) | KnowledgeGovernanceProtocol | — | **Smart City** | Present in abstractions/; assign when wired. |

### 4. Compute / ingestion / events (wired at boot)

| Abstraction | Adapters used | Protocol(s) | Foundation attr | Civic system | Notes |
|-------------|----------------|-------------|-----------------|--------------|-------|
| **DeterministicComputeAbstraction** | DuckDB, FileStorage | — (uses FileStorageProtocol) | deterministic_compute_abstraction | **Platform** | Embeddings/analytics; intents use via ctx. |
| **IngestionAbstraction** | Upload, EDI, API | IngestionProtocol | ingestion_abstraction | **Platform** | Ingest file/EDI/API; intents use via ctx. |
| **EventPublisherAbstraction** | Redis (Streams) | — | event_publisher_abstraction | **Platform** | Events for intents/outbox. |
| **VisualGenerationAbstraction** | VisualGenerationAdapter, FileStorage | VisualGenerationProtocol | visual_generation_abstraction | **Platform** | Visual gen for intents. |

### 5. Parsing / document (wired at boot)

| Abstraction | Adapters used | Protocol(s) | Foundation attr | Civic system | Notes |
|-------------|----------------|-------------|-----------------|--------------|-------|
| **CsvProcessingAbstraction** | CsvProcessingAdapter, StateSurface | — | csv_processing_abstraction | **Platform** | Document parsing; intents use via ctx. |
| **ExcelProcessingAbstraction** | ExcelProcessingAdapter, StateSurface | — | excel_processing_abstraction | **Platform** | Same. |
| **PdfProcessingAbstraction** | PdfProcessingAdapter, StateSurface | — | pdf_processing_abstraction | **Platform** | Same. |
| **WordProcessingAbstraction** | WordProcessingAdapter, StateSurface | — | word_processing_abstraction | **Platform** | Same. |
| **HtmlProcessingAbstraction** | HtmlProcessingAdapter, StateSurface | — | html_processing_abstraction | **Platform** | Same. |
| **ImageProcessingAbstraction** | ImageProcessingAdapter, StateSurface | — | image_processing_abstraction | **Platform** | Same. |
| **JsonProcessingAbstraction** | JsonProcessingAdapter, StateSurface | — | json_processing_abstraction | **Platform** | Same. |
| **TextProcessingAbstraction** | (built-in), StateSurface | — | text_processing_abstraction | **Platform** | Same. |
| **KreuzbergProcessingAbstraction** | KreuzbergAdapter, StateSurface | — | kreuzberg_processing_abstraction | **Platform** | Optional; mainframe/legacy. |
| **MainframeProcessingAbstraction** | MainframeProcessingAdapter, StateSurface | FileParsingProtocol | mainframe_processing_abstraction | **Platform** | Mainframe parsing. |
| **DataModelProcessingAbstraction** | JsonAdapter, StateSurface | — | data_model_processing_abstraction | **Platform** | JSON/YAML schemas. |
| **WorkflowProcessingAbstraction** | (built-in BPMN), StateSurface | — | workflow_processing_abstraction | **Platform** | BPMN/DrawIO. |
| **SopProcessingAbstraction** | (built-in Markdown), StateSurface | — | sop_processing_abstraction | **Platform** | Markdown SOP. |

### 6. Not wired in foundation_service (present in abstractions/ only)

| Abstraction | Protocol(s) | Civic system (when wired) | Notes |
|-------------|-------------|---------------------------|-------|
| **ContentMetadataAbstraction** | ContentMetadataProtocol | **Experience** | Metadata for UI/experience; assign when wired. |
| **AuthorizationAbstraction** | AuthorizationProtocol | **Smart City** | See §1. |
| **KnowledgeGovernanceAbstraction** | KnowledgeGovernanceProtocol | **Smart City** | See §3. |

---

## Phase B — Summary (civic_system assignment)

**Civic system assignment rationale:**

- **Smart City:** Auth, Tenant, Authorization, KnowledgeGovernance — governance, policy, security. Intent code never touches these directly; only via Platform SDK context (e.g. `ctx.governance`).
- **Agentic:** SemanticSearch, KnowledgeDiscovery — reasoning/knowledge for agents. Intent code gets these only via `ctx.reasoning` (mediated).
- **Experience:** ContentMetadata (if wired) — user-facing metadata. Intent code gets only via `ctx.experience` (mediated).
- **Platform:** State, ServiceDiscovery, Registry, FileStorage, FileManagement, ArtifactStorage, DeterministicCompute, Ingestion, EventPublisher, VisualGeneration, SemanticData, and all parsing abstractions. These are the only abstractions intent services **directly** use via `ctx` (e.g. `ctx.public_works.storage`, `ctx.document_parsing`, `ctx.state_surface`).

**Platform-category abstractions (expose via Platform SDK):**  
StateManagement, ServiceDiscovery, Registry, FileStorage, FileManagement, ArtifactStorage, DeterministicCompute, Ingestion, EventPublisher, VisualGeneration, SemanticData, and all parsing abstractions (Csv, Excel, Pdf, Word, Html, Image, Json, Text, Kreuzberg, Mainframe, DataModel, Workflow, Sop). These form the starter set for `IntentExecutionContext` (ctx) so B-team intent services get them via Platform SDK only.

**Abstraction registration shape:** When registering an abstraction with Curator, include **civic_system** (Smart City | Agentic | Experience | Platform) as part of the abstraction's shape. Curator returns only the slice for the requesting reader (Smart City → governance, Agentic → reasoning, Experience → experience, Platform context factory → platform).

---

## Phase C — Protocols (placeholder)

*To be filled after Phase C. List: protocol name, implementers, callers typed to protocol vs concrete.*

---

## Phase D — 4-layer flow (placeholder)

*To be filled after Phase D. Trace: Adapter → Abstraction → Protocol → Service → caller.*

---

## Phase E — Vision alignment + service mapping + gap map (placeholder)

*To be filled after Phase E. Alignments, **service mapping recommendations** (what foundation service should expose for current vision), gap map, refactor backlog.*

---

## Phase F — Curator boundary (placeholder)

*To be filled after Phase F. What gets registered and where; Curator vs Public Works boundary.*
