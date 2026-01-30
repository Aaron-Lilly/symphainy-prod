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

## Phase C — Protocols

Per-protocol: name, intended contract, which abstractions implement it, who types against the protocol vs concrete. **Vision check:** "Adapter → Abstraction → Platform Contract" — is the contract the protocol? Where are callers bound to implementations?

### 1. Protocols with a single abstraction implementer (and foundation returns protocol)

| Protocol | Intended contract | Implementer(s) | Foundation get_* return type | Callers typed to protocol? | Callers typed to concrete? |
|----------|-------------------|----------------|-----------------------------|----------------------------|----------------------------|
| **StateManagementProtocol** | store_state, retrieve_state, delete_state, etc. (state_protocol.py) | StateManagementAbstraction | **StateManagementProtocol** ✓ | StateSurface, ArtifactRegistry, TrafficCopSDK, ArtifactPlane, runtime_agent_websocket (get_state_abstraction) | service_factory (public_works.state_abstraction) |
| **FileStorageProtocol** | upload_file, download_file, delete_file, etc. (file_storage_protocol.py) | FileStorageAbstraction | **FileStorageProtocol** ✓ | StateSurface, DeterministicComputeAbstraction | service_factory, runtime_api, file_parser_service, upload/edi/api adapters, export_service, report_generator, save_materialization, retrieve_artifact_metadata |
| **ServiceDiscoveryProtocol** | (service_discovery_protocol.py) | ServiceDiscoveryAbstraction | **ServiceDiscoveryProtocol** ✓ | Curator foundation_service (get_service_discovery_abstraction) | — |
| **AuthenticationProtocol** | authenticate, validate_token, etc. (auth_protocol.py) | AuthAbstraction | **AuthenticationProtocol** ✓ | — | — |
| **TenancyProtocol** | (auth_protocol.py) | TenantAbstraction | **TenancyProtocol** ✓ | — | — |
| **SemanticSearchProtocol** | (semantic_search_protocol.py) | SemanticSearchAbstraction | **SemanticSearchProtocol** ✓ | — | — |

### 2. Protocols with implementer but foundation returns concrete or Any

| Protocol | Intended contract | Implementer(s) | Foundation get_* return type | Callers typed to protocol? | Callers typed to concrete? |
|----------|-------------------|----------------|-----------------------------|----------------------------|----------------------------|
| **FileManagementProtocol** | (file_management_protocol.py) | FileManagementAbstraction | — (no get_* in list; passed internally) | — | service_factory (file_management_abstraction) |
| **ArtifactStorageProtocol** | (artifact_storage_protocol.py) | ArtifactStorageAbstraction | **ArtifactStorageAbstraction** (concrete) | — | service_factory, runtime_services |
| **IngestionProtocol** | ingest(IngestionRequest) → IngestionResult (ingestion_protocol.py) | IngestionAbstraction | **Optional[Any]** | — | — |
| **SemanticDataProtocol** | (semantic_data_protocol.py) | SemanticDataAbstraction | **Optional[Any]** | — | data_quality_service, export_service, semantic_matching_service (get_semantic_data_abstraction) |
| **VisualGenerationProtocol** | (visual_generation_protocol.py) | VisualGenerationAbstraction | **VisualGenerationAbstraction** (concrete) | — | workflow_visual_service, outcome_visual_service (get_visual_generation_abstraction) |
| **KnowledgeDiscoveryProtocol** | (knowledge_discovery_protocol.py) | KnowledgeDiscoveryAbstraction | — (internal) | — | — |
| **KnowledgeGovernanceProtocol** | (knowledge_governance_protocol.py) | KnowledgeGovernanceAbstraction | — (not wired) | — | — |
| **ContentMetadataProtocol** | (content_metadata_protocol.py) | ContentMetadataAbstraction | — (not wired) | — | — |
| **AuthorizationProtocol** | (auth_protocol.py) | AuthorizationAbstraction | — (not wired) | — | — |

### 3. Event publisher (ABC, not typing.Protocol)

| Protocol / ABC | Intended contract | Implementer(s) | Foundation get_* return type | Callers |
|----------------|-------------------|----------------|-----------------------------|---------|
| **EventPublisherProtocol** (ABC) | publish(topic, event_type, event_data, headers) (event_publisher_protocol.py) | EventPublisherAbstraction | **Optional[Any]** | — |

### 4. Parsing protocols

| Protocol | Intended contract | Implementer(s) | Foundation get_* return type | Callers |
|----------|-------------------|----------------|-----------------------------|---------|
| **FileParsingProtocol** | parse_file(FileParsingRequest) → FileParsingResult (file_parsing_protocol.py) | MainframeProcessingAbstraction (doc); other parsing abstractions do not inherit it in code | — | file_parser_service uses get_*_processing_abstraction() (concrete) for each format |
| **ParsingServiceProtocol** (Structured, Unstructured, Hybrid, WorkflowSOP) | parse_structured_file, etc. (parsing_service_protocol.py) | No abstraction in public_works implements these; may be used by libraries | — | — |

### 5. Protocols with no abstraction implementer in Public Works

| Protocol | Intended contract | Implementer(s) | Notes |
|----------|-------------------|----------------|-------|
| **VectorBackendProtocol** | vector_search(...) (vector_backend_protocol.py) | Used internally by SemanticDataAbstraction (vector backend); no separate VectorBackendAbstraction | SemanticDataAbstraction uses Arango as vector backend; protocol enables swap. |

### 6. No protocol in code (abstraction only)

| Capability | Abstraction | Foundation exposes | Callers |
|------------|-------------|---------------------|---------|
| **Registry** | RegistryAbstraction | registry_abstraction (attr), no get_* return type | runtime_api, export_service, semantic_profile_registry (public_works.registry_abstraction or getattr) |
| **Deterministic compute** | DeterministicComputeAbstraction | deterministic_compute_abstraction (attr) | data_quality_service, export_service, schema_matching_service, pattern_validation_service, deterministic_embedding_service (public_works.deterministic_compute_abstraction) |

---

## Phase C — Summary (protocol as contract?)

**Where the protocol is the boundary:**  
StateManagementProtocol, FileStorageProtocol, ServiceDiscoveryProtocol, AuthenticationProtocol, TenancyProtocol, SemanticSearchProtocol — foundation's get_* returns the protocol type, and some callers (StateSurface, ArtifactRegistry, TrafficCopSDK, ArtifactPlane, Curator) accept or use the protocol type. So for these, **the contract is the protocol** where get_* is used.

**Where callers are bound to concrete or direct attr:**  
- **service_factory** passes public_works.state_abstraction, public_works.file_storage_abstraction, public_works.artifact_storage_abstraction, public_works.registry_abstraction, public_works.file_management_abstraction (direct attributes, not get_*). So runtime construction is coupled to foundation's attribute names and concrete types.
- **Libraries and realms** use get_file_storage_abstraction(), get_semantic_data_abstraction(), get_visual_generation_abstraction(), public_works.registry_abstraction, public_works.deterministic_compute_abstraction — mix of get_* (some protocol, some Any/concrete) and direct attr.
- **Parsing:** All callers use get_pdf_processing_abstraction(), get_csv_processing_abstraction(), etc. — **concrete** types. No caller uses FileParsingProtocol as the type; file_parser_service picks abstraction by format.
- **control_room_service** uses public_works.arango_adapter, public_works.redis_adapter, public_works.gcs_adapter — **direct adapter access**, bypassing abstraction/protocol.

**Gaps for platform vision (four services, protocol-typed):**  
1. **Return protocol everywhere get_* is part of the B contract:** get_artifact_storage_abstraction → ArtifactStorageProtocol; get_visual_generation_abstraction → VisualGenerationProtocol; get_ingestion_abstraction → IngestionProtocol; get_semantic_data_abstraction → SemanticDataProtocol; get_event_publisher_abstraction → EventPublisherProtocol.  
2. **Define RegistryProtocol and DeterministicComputeProtocol** so B can depend on protocol, not concrete.  
3. **Unified parsing surface:** Either have all parsing abstractions implement FileParsingProtocol and expose a single document_parsing (protocol) surface, or keep format-specific get_* but type them as FileParsingProtocol.  
4. **Stop direct adapter access:** control_room_service (and any similar) should not use public_works.arango_adapter/redis_adapter/gcs_adapter; use abstractions or a dedicated health/discovery surface.  
5. **service_factory:** Prefer passing protocol-typed capabilities (from get_* or a four-service layer) instead of public_works.state_abstraction, public_works.file_storage_abstraction, etc., so the runtime is not coupled to foundation attribute names.

---

## Phase D — 4-layer flow (evidence)

Trace: Layer 0 (Adapter) → Layer 1 (Abstraction) → Layer 2 (Protocol, when used) → Layer 4 (Foundation Service) → caller. **Layer 3:** No named Layer 3 in code; the foundation service (Layer 4) holds abstractions and exposes them; callers get them via direct attributes or get_* methods. So the flow is: caller → Foundation Service (L4) → Abstraction (L1) → Adapter (L0). Protocol (L2) is the type contract where get_* returns protocol; some callers still receive concrete or direct attr.

### Flow 1: Ingest file (intent → storage)

| Step | Layer | Component | Evidence |
|------|-------|-----------|----------|
| 1 | Caller | IngestFileService.execute() | realms/content/intent_services/ingest_file_service.py |
| 2 | L4 | public_works.get_ingestion_abstraction() | Returns IngestionAbstraction (L1). Line 134: `ingestion_abstraction = self.public_works.get_ingestion_abstraction()` |
| 3 | L1 | IngestionAbstraction.ingest_data(IngestionRequest) | ingestion_abstraction.py — implements IngestionProtocol (L2) |
| 4 | L1→L0 | Routes to UploadAdapter.ingest(request) | IngestionAbstraction holds upload_adapter (L0); line 73: `return await self.upload_adapter.ingest(request)` |
| 5 | L0 | UploadAdapter | upload_adapter.py — uses file_storage_abstraction (L1) |
| 6 | L1 | FileStorageAbstraction.upload_file() | UploadAdapter calls self.file_storage.upload_file(); FileStorageAbstraction implements FileStorageProtocol (L2) |
| 7 | L0 | GCSAdapter, SupabaseFileAdapter | file_storage_abstraction.py uses gcs_adapter, supabase_file_adapter |

**Chain:** Caller (intent) → Foundation get_ingestion_abstraction() → IngestionAbstraction (L1) → UploadAdapter (L0) → FileStorageAbstraction (L1) → GCS/Supabase (L0). **Protocol in use:** IngestionProtocol, FileStorageProtocol. No bypass.

### Flow 2: State (session state read/write)

| Step | Layer | Component | Evidence |
|------|-------|-----------|----------|
| 1 | Caller | StateSurface.get_session_state() / set_session_state() | runtime/state_surface.py — used by API, intent handlers, ArtifactRegistry |
| 2 | L4 → L1 | StateSurface holds state_abstraction | service_factory.py lines 79–80: `state_surface = StateSurface(state_abstraction=public_works.state_abstraction, file_storage=public_works.file_storage_abstraction)` — **direct attr**, not get_* |
| 3 | L1 | StateManagementAbstraction.retrieve_state() / store_state() | state_surface.py lines 87, 124, etc.: `await self.state_abstraction.retrieve_state(state_id)` |
| 4 | L0 | RedisAdapter, ArangoAdapter | state_abstraction.py (StateManagementAbstraction) uses redis_adapter, arango_adapter |

**Chain:** Caller (StateSurface) → state_abstraction (L1) → Redis/Arango (L0). **Entry:** service_factory passes public_works.state_abstraction (direct attr) to StateSurface. StateSurface is typed to StateManagementProtocol in its constructor; foundation stores concrete StateManagementAbstraction. No bypass for state.

### Flow 3: Bypass — direct adapter access

| Step | Caller | What it does | Evidence |
|------|--------|---------------|----------|
| 1 | control_room_service | Uses public_works.arango_adapter, public_works.redis_adapter, public_works.gcs_adapter directly | civic_systems/experience/admin_dashboard/services/control_room_service.py lines 256–264: `hasattr(self.public_works, 'arango_adapter')`, etc. |

**Bypass:** Caller skips Layer 1 (abstraction) and Layer 2 (protocol); goes straight to Layer 0 (adapters). Should use abstractions or a dedicated health/discovery surface.

### Flow 4: Registry (runtime API → registry)

| Step | Layer | Component | Evidence |
|------|-------|-----------|----------|
| 1 | Caller | runtime_api (list_artifacts, get_pending_intents, create_pending_intent) | runtime/runtime_api.py — receives registry_abstraction in create_runtime_app() |
| 2 | L4 | public_works.registry_abstraction (direct attr) | service_factory.py line 359: `registry_abstraction = public_works.registry_abstraction`; passed to RuntimeServices and create_runtime_app() |
| 3 | L1 | RegistryAbstraction (no protocol in code) | registry_abstraction.py — uses supabase_adapter (L0) |
| 4 | L0 | SupabaseAdapter | RegistryAbstraction uses Supabase |

**Chain:** Caller (runtime_api) → registry_abstraction (L1) → Supabase (L0). No protocol type for Registry; callers get concrete. No bypass.

---

## Phase D — Summary

- **4-layer flow holds** for ingestion and state: Caller → Foundation (L4) → Abstraction (L1) → Adapter (L0). Protocol (L2) exists where get_* returns protocol type or callers are typed to protocol (e.g. StateSurface, ArtifactRegistry).
- **Layer 3** is not present as a named layer; the foundation service is the single aggregation point. A future "four services" (Governance, Reasoning, Experience, Platform) could sit as a Layer 3 between callers and foundation.
- **Bypass:** control_room_service uses public_works.arango_adapter, redis_adapter, gcs_adapter directly — should be removed or replaced with abstraction/health surface.
- **Vision check:** "Public Works → Adapter → Abstraction → Platform Contract" holds for the flows traced; the "contract" is the protocol where used. Gaps: service_factory uses direct attrs (public_works.state_abstraction, file_storage_abstraction, etc.) instead of get_* or a single context; one caller bypasses to adapters.

---

## Phase E — Vision alignment + service mapping + gap map

**Vision (current):** Public Works = Storage adapters (GCS, S3, FS), Compute adapters, Queue adapters, Network adapters. Guarantees: **Uniform interfaces**, **Hot-swappable backends**, **Deterministic behavior.** "Public Works → Adapter → Abstraction → Platform Contract."

### Alignments (what matches the vision)

| Vision element | Current state | Evidence |
|----------------|---------------|----------|
| **Storage adapters** | GCS, Supabase (file + DB), Arango (state/graph), Meilisearch (search). No S3 or generic FS in code. | Phase A: GCS, SupabaseFile, Arango wired; file storage abstraction backs ingest and artifacts. |
| **Compute adapters** | DuckDB (deterministic), OpenAI, HuggingFace. Parsing adapters (CSV, PDF, etc.) as "Other" / capability. | Phase A: DuckDB, OpenAI, HuggingFace; parsing as document processing. |
| **Queue adapters** | Redis (WAL, cache, events). EventPublisher (Redis Streams) optional. | Phase A: RedisAdapter; EventPublisherAbstraction when Redis present. |
| **Network adapters** | Consul (service discovery), Supabase (auth/API), API/EDI for ingestion. | Phase A: ConsulAdapter, SupabaseAdapter; APIAdapter, EDIAdapter. |
| **Adapter → Abstraction → Protocol** | 4-layer flow holds for ingestion, state, registry; abstractions implement protocols where defined. | Phase B, C, D: abstractions use adapters; many implement protocols; get_* returns protocol for State, FileStorage, ServiceDiscovery, Auth, Tenant, SemanticSearch. |
| **Deterministic behavior** | Pre-boot validates backing services; config-only (canonical config); no env reads inside Public Works for platform infra. | Genesis / STEP2: pre-boot G3; foundation receives config dict. |
| **Uniform interfaces (partial)** | StateManagementProtocol, FileStorageProtocol, IngestionProtocol, etc. exist; some callers use them. | Phase C: StateSurface, ArtifactRegistry, TrafficCopSDK, ArtifactPlane, Curator use protocol-typed get_* where available. |

### Gap map (what does not align)

| Gap | Current state | Vision / target | Phase source |
|-----|---------------|-----------------|--------------|
| **No S3 or generic FS** | GCS and Supabase file only. | Vision lists S3, FS; BYOI implies swappable backends. | A |
| **Callers bound to concrete / direct attr** | service_factory uses public_works.state_abstraction, file_storage_abstraction, registry_abstraction, artifact_storage_abstraction (direct attr). Libraries/realms use direct attr or get_* returning Any/concrete. | All callers should receive protocol-typed capabilities (or four-service ctx). | C, D |
| **get_* returns concrete or Any** | get_artifact_storage_abstraction → ArtifactStorageAbstraction; get_ingestion_abstraction → Any; get_semantic_data_abstraction → Any; get_event_publisher_abstraction → Any; get_visual_generation_abstraction → VisualGenerationAbstraction; all get_*_processing_abstraction() → concrete. | get_* (or four-service surface) should return protocol type for every capability exposed to B/runtime. | C |
| **No RegistryProtocol / DeterministicComputeProtocol** | RegistryAbstraction, DeterministicComputeAbstraction have no formal Protocol in code. | B and runtime should depend on protocol, not concrete. | C |
| **Parsing: no unified protocol surface** | Callers use get_pdf_processing_abstraction(), get_csv_processing_abstraction(), etc. (concrete). Only MainframeProcessingAbstraction implements FileParsingProtocol in code. | ctx.platform exposes parse (capability); all parsers should implement FileParsingProtocol and be exposed as single document_parsing surface. | B, C |
| **Direct adapter access (bypass)** | control_room_service uses public_works.arango_adapter, redis_adapter, gcs_adapter. | No caller should touch adapters directly; use abstractions or dedicated health/discovery surface. | D |
| **Layer 3 missing** | Foundation service is single aggregation; no "four services" (Governance, Reasoning, Experience, Platform) in code. | Target: four services on ctx; ctx.platform capability-oriented (parse, analyze, visualize, synthesize, generate SOP/workflow/POC/roadmap, metrics). | D, handoff |
| **Service exposure vs ownership** | Foundation exposes state, storage, registry, ingestion, parsing, etc. to runtime/realms. | Ownership to be reconciled: storage → Data Steward; state → Runtime; registry → Curator; ctx.platform → parse, analyze, visualize, synthesize, generate, metrics. | Handoff correction |
| **Startup: adapter connect()** | Several adapters call connect() inside _create_adapters. | **Removed from backlog.** Redundancy was expected given startup mess; can safely remove this as a refactor item. | A |
| **OpenTelemetry / TelemetryAdapter** | In adapters/ but not in _create_adapters or pre-boot; telemetry_abstraction never wired. | Add OpenTelemetry to pre-boot checklist; wire TelemetryAdapter in foundation_service and expose telemetry_abstraction. Foundational; should have been essential pre-boot. Prior implementations: symphainy_source, symphainy_platform_old. | A |

### Service mapping recommendations (what foundation should expose for current vision)

1. **Expose via four services (Layer 3), not a bag of attrs.** Introduce ctx.governance, ctx.reasoning, ctx.experience, ctx.platform. Foundation service (or a context factory) builds these; callers (runtime, intent handlers) receive ctx only, not public_works directly.
2. **ctx.platform:** Capability-oriented surface only: parse, analyze, visualize, synthesize, generate SOP/workflow/POC/roadmap, metrics. Not raw storage/state/registry (those belong to Data Steward, Runtime, Curator per handoff correction).
3. **Every get_* that is part of the B/runtime contract returns protocol type.** Today: get_artifact_storage_abstraction → ArtifactStorageProtocol; get_visual_generation_abstraction → VisualGenerationProtocol; get_ingestion_abstraction → IngestionProtocol; get_semantic_data_abstraction → SemanticDataProtocol; get_event_publisher_abstraction → EventPublisherProtocol. Add RegistryProtocol and DeterministicComputeProtocol and return them from get_* (or from the appropriate service slice).
4. **Unified parsing:** Expose document_parsing as a single protocol-typed surface (FileParsingProtocol); all parsing abstractions implement it; callers use ctx.platform.document_parsing (or equivalent), not format-specific get_*.
5. **Remove direct adapter access.** control_room_service (and any similar) must not use public_works.arango_adapter, redis_adapter, gcs_adapter. Provide health/discovery via abstractions or a dedicated surface.
6. **service_factory:** Stop passing public_works.state_abstraction, file_storage_abstraction, etc. (direct attr). Pass protocol-typed capabilities from get_* or from the four-service context so runtime is not coupled to foundation attribute names.

### Refactor backlog (prioritized by layer)

| Priority | Layer | Item | Rationale |
|----------|-------|------|------------|
| P1 | Caller | **Control Room: use genesis protocol status for infrastructure health.** Remove direct adapter access; Control Room was built before genesis — it should check genesis/pre-boot status, not adapters or abstraction health_check(). | Design flaw; single source of truth for infra health is genesis. |
| P2 | L4 / Service | **Return protocol from every get_* used by B/runtime.** get_artifact_storage_abstraction → ArtifactStorageProtocol; get_visual_generation_abstraction → VisualGenerationProtocol; get_ingestion_abstraction → IngestionProtocol; get_semantic_data_abstraction → SemanticDataProtocol; get_event_publisher_abstraction → EventPublisherProtocol. | Aligns with "uniform interfaces" and B-team provisional wrapper. |
| P2 | L2 | **Define DeterministicEmbeddingStorageProtocol** (not DeterministicComputeProtocol — DuckDB is for embedding storage). Have DeterministicComputeAbstraction implement it; foundation returns protocol. **Registry:** defer to Curator flow (RegistryAbstraction too generic vs Consul; add to Phase F / Curator). | Correct naming; Registry decided with Curator. |
| P3 | L4 / Service | **Introduce four-service context (ctx).** Build ctx.governance, ctx.reasoning, ctx.experience, ctx.platform; context factory reads Curator (abstraction registry by civic_system) and injects protocol-typed capabilities. service_factory (or bootstrap) creates ctx and passes it to runtime/intent handlers instead of public_works. | Matches platform vision and handoff; enables clear ownership (Data Steward, Runtime, Curator, Platform). |
| P3 | L4 / Service | **service_factory: use get_* or ctx instead of direct attrs.** StateSurface, ExecutionLifecycleManager, runtime_api receive protocol-typed capabilities from get_* or from ctx, not public_works.state_abstraction, etc. | Decouples runtime from foundation attribute names; supports swap. **Done:** service_factory now uses get_state_abstraction(), get_file_storage_abstraction(), get_redis_adapter(), get_registry_abstraction(), get_artifact_storage_abstraction(). |
| P4 | L1 / L2 | **Unified parsing surface.** Have all parsing abstractions implement FileParsingProtocol; expose single document_parsing (protocol) on ctx.platform; deprecate or wrap format-specific get_* as implementation detail. | Aligns with ctx.platform = parse (capability); single contract for B. |
| P5 | L0 / Pre-boot | **Add OpenTelemetry to pre-boot checklist.** Telemetry is foundational; it should have been an essential part of pre-boot. Extend pre_boot (and PRE_BOOT_SPEC) to validate telemetry/OTLP where applicable. | Foundational; gate entry to Φ3. |
| P5 | L4 / Service | **Wire TelemetryAdapter and expose telemetry_abstraction.** Create TelemetryAdapter in _create_adapters (or equivalent); expose via get_telemetry_abstraction() so NurseSDK and intent services get a real implementation. Prior implementations: symphainy_source and symphainy_platform_old (see plain-language P5). | Close OpenTelemetry gap; expose as intended. |
| P6 | L0 | **S3 / generic FS adapter.** Deferred / out of scope. Stick to current tech stack (GCS, Supabase file); no theoretical future adapters for now. | Vision lists S3, FS; not needed until concrete requirement. |

---

## Phase E — Summary

- **Alignments:** Storage/Compute/Queue/Network adapters and 4-layer flow (Adapter → Abstraction → Protocol → Service) match the vision where protocols exist and get_* returns protocol type. Deterministic behavior and partial uniform interfaces (State, FileStorage, ServiceDiscovery, Auth, Tenant, SemanticSearch) are in place.
- **Gaps:** Callers bound to concrete/direct attr; several get_* return concrete or Any; no RegistryProtocol/DeterministicComputeProtocol; parsing not a unified protocol surface; control_room_service bypass (direct adapter access); no four-service ctx in code; ownership of storage/state/registry vs ctx.platform to be reconciled.
- **Refactor backlog:** P1 = done; P2 = done; P3 Part B = done; P3 Part A = four-service ctx deferred (Curator/Phase F); P4 = done (DocumentParsingRouter + get_document_parsing()); P5 = done; P6 = deferred. **Four-service mapping:** [FOUR_SERVICE_MAPPING.md](../architecture/FOUR_SERVICE_MAPPING.md) — suggested ctx.governance, ctx.reasoning, ctx.experience, ctx.platform + runtime substrate; adapter usage elsewhere noted. **Plain-language guide:** [PUBLIC_WORKS_REFACTOR_PLAIN_LANGUAGE.md](../PUBLIC_WORKS_REFACTOR_PLAIN_LANGUAGE.md) — what's broken and what we're doing for each item.

---

## Phase F — Curator boundary (placeholder)

*To be filled after Phase F. What gets registered and where; Curator vs Public Works boundary.*
