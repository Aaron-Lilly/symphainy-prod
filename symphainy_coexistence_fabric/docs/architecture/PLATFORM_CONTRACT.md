# Platform Contract: Guarantee That the Platform Actually Works

**Purpose:** Single, enforceable contract that defines what infrastructure the platform **requires** and what "the platform actually works" means. No optional infra at boot—everything listed here is **required** for the platform to deliver on Public Works → Civic Systems → Solutions → Realms.

**Status:** Canonical. Code, config, and pre-boot validation must align with this contract.

**Principle:** None of our infra is optional. If it's in the contract, it must be present and validated before we build the object graph.

---

## 1. What "Platform Actually Works" Means

The platform **actually works** when:

1. **Boot to first request:** Process starts; `create_runtime_services()` completes; FastAPI app is created; uvicorn serves; `GET /health` returns 200 with a healthy body.
2. **Runtime is fully populated:** All `RuntimeServices` required fields are non-None: `public_works`, `state_surface`, `execution_lifecycle_manager`, `registry_abstraction`, `artifact_storage`, `file_storage`. No "continuing anyway" after Public Works init failure.
3. **State, WAL, and lineage work:** State Surface can store/retrieve state; WAL can append events; Artifact Registry can register and resolve artifacts; lineage is durable where the architecture requires it.
4. **Intent execution works:** Runtime can route intents to realm intent services; intent services can use Public Works abstractions (state, file storage, registry, semantic data, deterministic compute, search) without getting None or connection errors.
5. **Civic Systems can govern:** Smart City, Experience, Agentic, Platform SDK, and Artifact Plane have the infra they need (service discovery, auth, telemetry, registry) so policy and coordination work.
6. **Solutions and Realms can deliver:** Content (ingest, parse, embeddings), Insights (interpretation, analysis, lineage), Operations (SOPs, workflows), Outcomes (synthesis, roadmaps, POCs), Security (auth, sessions), Control Tower (health, stats), and Coexistence (guide agent, catalog) can fulfill their contracts because every backing service they need is present and working.

This contract defines **what must be true at the infrastructure layer** so that the above holds. **§9** adds the **functional** requirements (parsing, analytics, agentic, visualization, Artifact Plane, telemetry) that solutions, journeys, and intents require from Public Works and Civic.

---

## 2. No Optional Infra at Boot

**Rule:** Every backing service listed in §3 is **required**. There is no "optional" infra for platform boot or for the platform to deliver. If any required service is missing or unreachable at startup, the process **must not** build the object graph. It must **exit immediately** with a clear, actionable error (pre-boot validation).

- No "Public Works had issues, continuing anyway."
- No partial init where some adapters/abstractions are None and others are set.
- No silent degradation: we do not start the server and then fail on first use of a missing service.

Consul, Redis, Arango, Supabase, GCS, Meilisearch, and DuckDB are all **required** by this contract. The platform does not run without them.

---

## 3. Required Infrastructure and What Each Is For

Each backing service is used for specific platform capabilities. Using the right tool for the right job is part of the contract: we do not remove or add components without updating this section.

| Backing Service | Purpose in the Platform | What the Platform Delivers With It | Required Env / Config |
|-----------------|--------------------------|-------------------------------------|------------------------|
| **Redis** | Hot state (StateManagementAbstraction), WAL (Write-Ahead Log via Redis Streams), event publishing (RedisStreamsPublisher), tenant/cache (TenantAbstraction). | Durable execution log, replay, audit; session/execution state; events for downstream. | `REDIS_URL` or config `redis.host`, `redis.port`, `redis.password`. Must be reachable at boot. |
| **ArangoDB** | Durable state (StateManagementAbstraction), state_data collection (_ensure_state_collections), semantic data (SemanticDataAbstraction), graph/knowledge (KnowledgeDiscoveryAbstraction). | Durable state and lineage; semantic embeddings and graph; semantic search backing. | `ARANGO_URL`, `ARANGO_USERNAME` (or ARANGO_ROOT_PASSWORD holder), `ARANGO_PASSWORD`, `ARANGO_DATABASE`. Must be reachable and authorized at boot. |
| **Consul** | Service discovery (ServiceDiscoveryAbstraction). | Registration and discovery of services; control-plane coordination. | `CONSUL_HOST`, `CONSUL_PORT` (and optional `CONSUL_TOKEN`). Must be reachable at boot. |
| **Supabase (DB + Auth)** | Registry (RegistryAbstraction), auth (AuthAbstraction), tenant (TenantAbstraction). | Artifact/index metadata, lineage metadata, auth, tenancy. | `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_KEY`; optional JWKS/issuer for JWT. Must be reachable at boot. |
| **Supabase (File)** | File metadata and storage API (SupabaseFileAdapter); used with GCS for FileStorageAbstraction and ArtifactStorageAbstraction. | File and artifact metadata; coordination with GCS blobs. | Same as above; service key required for file adapter. |
| **GCS** | Blob storage (GCSAdapter); FileStorageAbstraction and ArtifactStorageAbstraction. | Actual file and artifact bytes; durable working materials and purpose-bound outcomes. | `GCS_PROJECT_ID`, `GCS_BUCKET_NAME`, `GCS_CREDENTIALS_JSON`. Must be reachable and authorized at boot. |
| **Meilisearch** | Full-text and metadata search (SemanticSearchAbstraction); optional input to KnowledgeDiscoveryAbstraction. | Search and discovery over artifacts and metadata; "right tool" for search. | `MEILISEARCH_HOST` (or host from env), `MEILISEARCH_PORT`, `MEILI_MASTER_KEY`. Must be reachable at boot. |
| **DuckDB** | Deterministic compute (DeterministicComputeAbstraction); storage for deterministic embeddings. | Content realm deterministic embeddings; analytical workload per north star ("DuckDB for deterministic, Arango for semantic"). | Config `duckdb.database_path`, `duckdb.read_only` or equivalent from env. Must be creatable/reachable at boot. |

**Right tool for the right job (no removal without architectural change):**

- **Arango:** Durable state, graph, semantic data. We do not use it for blob storage or for deterministic analytical workloads.
- **Redis:** Hot state, WAL, events, cache. We do not use it as the only durable store for lineage or artifacts.
- **Consul:** Service discovery only. Required for control-plane coordination.
- **Supabase:** Registry, auth, tenant, file metadata. We do not use it for blob bytes (GCS does that).
- **GCS:** Blob storage only. We do not use it for structured query or graph.
- **Meilisearch:** Search and discovery. We do not use it as the system of record for state or lineage.
- **DuckDB:** Deterministic embeddings and analytical workloads. We do not use it for semantic/graph or for hot state.

**Nothing we don't need:** Each of the above backs a concrete abstraction and platform deliverable. If we remove one, we must either remove the capability or reassign it to another backing service and update this contract.

**Nothing missing:** For the north-star flows (State Surface, WAL, Intent execution, lineage, search, deterministic embeddings, service discovery, auth, file/artifact storage), the list above is sufficient. If we add a new platform capability that needs new infra, we add it here first.

---

## 4. Config: One Source of Truth

**Rule:** The platform must be driven by **one** config source. Env is acquired per [CONFIG_ACQUISITION_SPEC.md](CONFIG_ACQUISITION_SPEC.md) (Gate G2); then a single canonical config is built from that env per the [Config Contract](CONFIG_CONTRACT_SPEC.md). All adapters must be created from that canonical config. No split where some adapters read env and others read a nested dict that is never populated from env.

**Requirement:** Either:

- **A)** Public Works reads **flat** env-derived keys for every adapter (e.g. `REDIS_URL` → Redis adapter; `CONSUL_HOST`/`CONSUL_PORT` → Consul adapter; a single `DUCKDB_DATABASE_PATH` or equivalent → DuckDB adapter), and the contract defines the exact env keys required, or  
- **B)** A single **platform config builder** turns env (e.g. `get_env_contract()`) into the nested shape Public Works expects (`redis: { host, port }`, `consul: { host, port }`, `duckdb: { database_path }`, etc.), and that builder is the only path from env to config.

**Current gap:** Today Public Works expects nested `config.get("redis", {})`, `config.get("consul", {})`, `config.get("duckdb", {})`. When config is `get_env_contract().__dict__`, those are empty and Redis, Consul, and DuckDB adapters are never created. The contract therefore **requires** closing this gap (A or B above) so that all required services in §3 are actually created at boot.

---

## 5. Pre-Boot Validation (Enforcement)

**Spec:** [PRE_BOOT_SPEC.md](PRE_BOOT_SPEC.md) defines scope, order, checks, and failure semantics.

**Rule:** Before `create_runtime_services()` is called (e.g. at the top of `runtime_main.main()` after loading config), the platform **must** run a **pre-boot validation** that:

1. For each required backing service in §3, performs a minimal connectivity/readiness check (e.g. connect and ping, or call a minimal API).
2. If **any** check fails, **exits immediately** with a single, clear message, e.g.  
   `"Platform contract violation: [SERVICE] failed: [reason]. Fix [ENV_KEY] and retry."`  
   No partial init. No "continuing anyway."

**Required checks (aligned with §3):**

- Redis: connect, ping.
- ArangoDB: connect, authorize (no 401), ensure state_data collection exists or can be created.
- Consul: reachable (e.g. HTTP or API check).
- Supabase: reachable (e.g. health or minimal API call with service key).
- GCS: bucket exists and credentials are valid (e.g. list or head bucket).
- Meilisearch: reachable (e.g. health endpoint).
- DuckDB: database path writable/readable and schema can be initialized (or equivalent).

**Where:** Pre-boot validation runs in `runtime_main.main()` **before** `create_runtime_services(config)`. It MUST NOT be inside Public Works as a side effect of creating adapters; it must be an explicit step that runs first and exits on failure.

---

## 6. Init Order and No Hidden Coupling

**Spec:** [INIT_ORDER_SPEC.md](INIT_ORDER_SPEC.md) defines the deterministic sequence (Public Works → StateSurface → WAL → IntentRegistry → ExecutionLifecycleManager) and Public Works contract (canonical config only).

**Rule:** No hidden coupling where failure of one service prevents creation of an unrelated abstraction. Today, Arango failure in `_ensure_state_collections()` prevents creation of `registry_abstraction` (Supabase). That violates the contract: **registry_abstraction does not depend on Arango**; it depends only on Supabase.

**Requirement:** Either:

- **A)** Pre-boot validates all services (including Arango). If Arango fails, we exit before building Public Works, so we never reach the point where Arango failure blocks registry. Init order inside Public Works can stay as-is, but boot never enters partial init.  
- **B)** Decouple init: on Arango connect failure, set `arango_adapter = None`, skip `_ensure_state_collections()`, and still create all Supabase- and GCS-backed abstractions (registry, file_storage, artifact_storage). Make semantic_data_abstraction and state_abstraction explicitly handle None Arango (degraded mode) and document that. Then pre-boot still validates Arango if we require it; if we make Arango optional for boot, document clearly.

**Contract default:** We treat **all** infra as required (§2). So the preferred enforcement is (A): pre-boot validates everything; on any failure we exit; init order inside Public Works must not leave any required abstraction as None when pre-boot has passed. If we ever introduce optional infra, we will update this contract and document degraded behavior.

---

## 7. RuntimeServices Required Fields

**Rule:** `RuntimeServices` must receive non-None for: `public_works`, `state_surface`, `execution_lifecycle_manager`, `registry_abstraction`, `artifact_storage`, `file_storage`. This is already enforced in code by `__post_init__`. The contract requires that **Public Works initialization completes successfully** when pre-boot has passed, so that every required abstraction is created and passed into RuntimeServices. No code path may call `RuntimeServices(...)` with any of these as None.

---

## 8. Summary: Contract Guarantees

When this contract is satisfied and enforced:

1. **All required infra** (Redis, Arango, Consul, Supabase, GCS, Meilisearch, DuckDB) is present and validated at boot.
2. **One config source** (env or env-derived platform config) drives all adapters; no missing adapters due to config shape mismatch.
3. **Pre-boot** runs before object-graph construction; any failure exits with a clear message.
4. **No optional infra at boot:** we do not start the server with missing or degraded backing services.
5. **Right tool for the right job:** each backing service is used only for the purposes listed in §3; the platform can deliver State Surface, WAL, lineage, search, deterministic embeddings, service discovery, auth, and file/artifact storage.
6. **Public Works → Civic → Solutions → Realms** can rely on the fact that if the process is running, the contract holds and all required abstractions are available.

**Enforcement checklist:**

- [x] Pre-boot validation implemented and run before `create_runtime_services()` (see [PRE_BOOT_SPEC.md](PRE_BOOT_SPEC.md)).
- [x] Canonical config built from env (acquisition + contract); Public Works receives only that config (see [CONFIG_ACQUISITION_SPEC.md](CONFIG_ACQUISITION_SPEC.md), [CONFIG_CONTRACT_SPEC.md](CONFIG_CONTRACT_SPEC.md)).
- [x] No "continuing anyway" when Public Works init fails; init raises if initialization fails (pre-boot guarantees backing services).
- [x] Pre-boot runs before init; registry_abstraction is not blocked by Arango (pre-boot fails first if Arango down).
- [x] Required keys and env mapping documented in CONFIG_CONTRACT_SPEC; repo root in CONFIG_ACQUISITION_SPEC.

---

## 9. Solution, Journey, and Intent Requirements (Functional Capabilities)

The platform contract must also capture what **solutions, journeys, and intents** require from Public Works and Civic so that the platform can actually deliver. This section maps downstream needs to abstractions, adapters, and capabilities. Nothing here is optional for the flows that use it—if an intent or journey requires a capability, that capability must be present and working when the contract holds.

### 9.1 What Solutions/Journeys/Intents Use (from code)

| Capability | Used by | Public Works / Civic | Backing / Notes |
|------------|---------|----------------------|-----------------|
| **File storage** | Content (ingest, parse, get_parsed_file, save_materialization, delete, archive), Operations (create_workflow), Outcomes (export_artifact) | file_storage_abstraction | GCS + Supabase file (§3). |
| **Artifact storage** | Content, Outcomes | artifact_storage_abstraction | GCS + Supabase file (§3). |
| **State surface** | All realms (artifact registration, execution state, session state, file metadata) | state_surface (Runtime) + state_abstraction | Redis + Arango (§3). |
| **Registry** | Content (index_artifact, register_pending_intent), Control Tower, list_artifacts | registry_abstraction | Supabase (§3). |
| **Auth** | Security (authenticate_user, create_user_account, validate_token, check_email_availability) | auth_abstraction | Supabase (§3). |
| **Ingestion** | Content (ingest_file) | See §9.2 Ingestion. | Upload, EDI, API—all required; separate from parsing. |
| **Parsing** | Content (parse_content via FileParserService) | See §9.3 Parsing. | All parsing capabilities required (no optional parsing except Cobrix noted below). |
| **Deterministic embeddings** | Content (create_deterministic_embeddings, extract_embeddings), Insights (data quality, schema matching, guided discovery) | deterministic_compute_abstraction | DuckDB (§3). |
| **Semantic data** | Content/Insights (semantic embeddings, interpretation), data quality, semantic matching | semantic_data_abstraction | Arango (§3). |
| **Semantic search** | Search/discovery over artifacts | semantic_search_abstraction | Meilisearch (§3). |
| **Knowledge discovery** | Graph/lineage (optional input Meilisearch) | knowledge_discovery_abstraction | Arango + optional Meilisearch (§3). |
| **LLM (OpenAI)** | Agents (AgentBase), SOP generation, interpretation, reasoning | get_llm_adapter() → openai_adapter | OpenAI API key; required for agentic and LLM-backed intents. |
| **Embeddings (HuggingFace)** | Semantic embedding generation | get_huggingface_adapter() | HuggingFace endpoint + key; required for semantic embeddings. |
| **Visual generation** | Outcomes (synthesize_outcome, generate_roadmap, create_poc), workflow/SOP visualization | visual_generation_abstraction | VisualGenerationAdapter (in-process). Required for outcomes visuals. |
| **Service discovery** | Control plane coordination | service_discovery_abstraction | Consul (§3). |
| **Event publishing** | Transactional outbox, downstream events | event_publisher_abstraction | Redis Streams (§3). |
| **Telemetry** | NurseSDK (bases), observability | telemetry_abstraction (Public Works) or get_telemetry_service() (app state) | NurseSDK uses telemetry_abstraction; some solutions call public_works.get_telemetry_service() which is not on Public Works—see gap below. |
| **Artifact Plane** | Security (auth/session), Operations (SOP, workflow, coexistence), Insights (data quality, interpretation, analysis), Outcomes (report, visual, synthesis) | get_artifact_plane() on public_works | **Gap:** get_artifact_plane() is called on public_works but is **not defined** on Public Works. Artifact Plane is a Civic System; must be injected or exposed via Public Works. |

### 9.2 Ingestion (Separate from Parsing)

**Ingestion** is how data enters the platform (upload, EDI, API). **Parsing** is how we extract structure from ingested files. They are distinct; both are required.

| Ingestion type | What we have | Infrastructure to support it | Contract |
|----------------|--------------|------------------------------|----------|
| **Upload** | UploadAdapter; uses file_storage_abstraction. | File storage (GCS + Supabase file) (§3). Adapter created when file_storage exists. | **Required.** Always created. |
| **API** | APIAdapter; converts API payloads to files and stores via file_storage. | File storage (§3). Adapter is **always** created (no config gate). | **Required.** We have the infrastructure: adapter + file_storage. Client sends payload to our ingest endpoint; we store. |
| **EDI** | EDIAdapter; AS2/SFTP, decrypt/verify, store via file_storage. | File storage (§3) + **EDI config** (partners, AS2 keys/certs, organization). Adapter created only when `config.get("edi", {})` is non-empty. Optional lib: pyas2lib for AS2. | **Required.** We have the adapter and code. To support EDI (top client ask): (1) Platform config must provide EDI config (partners, decrypt_key, verify_cert, etc.) so EDI adapter is created at boot. (2) Config bridge (§4) must include EDI from env or from a dedicated EDI config source. (3) If AS2/SFTP is used, pyas2lib (or equivalent) must be available. Contract: EDI ingestion is required; EDI config is required so the EDI adapter is created. |

**Summary:** Upload and API are supported with current infra (file_storage). API adapter is always created. EDI adapter is created only when EDI config is provided; contract requires EDI config so that EDI ingestion is available for clients.

### 9.3 Parsing (All Required; Cobrix Likely Required Soon)

**Parsing** is how we extract structured/unstructured content from ingested files. None of the parsing capabilities are optional (with the possible exception of Cobrix, which is likely to be required soon).

Public Works must create and expose **all** of the following parsing abstractions (and their adapters) so that parse_content and downstream flows work:

| Parsing capability | Adapter / abstraction | Backing / config | Notes |
|--------------------|------------------------|------------------|--------|
| **PDF** | PdfProcessingAbstraction, PdfProcessingAdapter | In-process. | Required. |
| **Word** | WordProcessingAbstraction, WordAdapter | In-process. | Required. |
| **Excel** | ExcelProcessingAbstraction, ExcelAdapter | In-process; **pandas** and **openpyxl** required for Excel. | Required. |
| **CSV** | CsvProcessingAbstraction, CsvProcessingAdapter | In-process. | Required. |
| **JSON** | JsonProcessingAbstraction, JsonProcessingAdapter | In-process. | Required. |
| **Image** | ImageProcessingAbstraction, ImageAdapter (OCR) | In-process. | Required. |
| **HTML** | HtmlProcessingAbstraction, HtmlAdapter | In-process. | Required. |
| **Text** | TextProcessingAbstraction (no adapter) | In-process. | Required. |
| **Mainframe** | MainframeProcessingAbstraction, MainframeProcessingAdapter | Copybook + binary; **Cobrix** (config: cobrix.service_url, prefer_cobrix) — likely required soon. | Required. Cobrix currently config-driven; treat as required for mainframe parsing. |
| **Kreuzberg** | KreuzbergProcessingAbstraction, KreuzbergAdapter | Config: kreuzberg.api_key, kreuzberg.base_url. | Required (PDF/hybrid). Config must be provided. |
| **Data model** | DataModelProcessingAbstraction | JSON/YAML adapters; PyYAML. | Required. |
| **SOP** | SopProcessingAbstraction | Markdown/text. | Required. |
| **Workflow** | WorkflowProcessingAbstraction | BPMN/DrawIO XML. | Required. |

**Contract:** All parsing capabilities above are **required**. Config (Kreuzberg, Cobrix, EDI) must be provided via the single config source (§4) so that the corresponding adapters/abstractions are created at boot. Cobrix is not optional for long; treat as required for mainframe flows.

### 9.4 EDA and Data Analysis: Pandas (and openpyxl)

**How we actually do EDA / data analysis in the platform:**

- **EDA Analysis Agent** (`eda_analysis_agent.py`): Uses **pandas** (DataFrame, shape, columns, dtypes, etc.) in `perform_eda()`. Loads data into a pandas DataFrame and runs EDA; generates insights from eda_results. This is the primary EDA path.
- **Excel parsing:** ExcelAdapter prefers **pandas** with **openpyxl** engine for reading XLSX/XLS. Without pandas/openpyxl, Excel parsing is limited or fails.
- **Mainframe custom strategy:** Optional pandas for DataFrame output; not the primary path.

**Contract:** **pandas** and **openpyxl** are **required** runtime/library dependencies for:
1. EDA and data analysis (EDA Analysis Agent, Insights).
2. Excel parsing (Content).

They must be in the platform environment (e.g. requirements.txt or equivalent). Pre-boot or first-use validation can check that pandas and openpyxl are importable if we want to fail fast.

**Other analytics/plotting already in use:** plotly, numpy (in requirements); used by visual generation and charts. PyYAML for data model/YAML. These remain required as today.

### 9.5 Agentic and Analytics

- **Agents:** Require get_llm_adapter() (OpenAI). No LLM → agents cannot reason.
- **Semantic embeddings:** Require HuggingFace adapter (or equivalent) and semantic_data_abstraction (Arango). No HF → extract_embeddings / semantic flows fail.
- **Deterministic embeddings:** Require deterministic_compute_abstraction (DuckDB). Already in §3.
- **Data quality, schema matching, guided discovery:** Use deterministic_compute, semantic_data, and optionally artifact_plane. Require DuckDB + Arango + (if used) Artifact Plane.

### 9.6 Visualization

- **Outcomes (roadmap, POC, synthesis, report, blueprint):** Use get_visual_generation_abstraction(). Visual generation adapter is in-process; uses plotly/numpy. Required for outcomes flows that produce charts/diagrams.

### 9.7 Gaps and Contract Additions

| Gap | Current state | Contract requirement |
|-----|----------------|----------------------|
| **get_artifact_plane()** | Called on public_works in Security, Operations, Insights, Outcomes; **not defined** on Public Works. | Either (a) Public Works exposes get_artifact_plane() (delegating to Civic/Artifact Plane), or (b) Artifact Plane is injected into intent services/solutions by Runtime, and call sites are updated. Contract: platform must provide Artifact Plane to intents/solutions that need it. |
| **get_telemetry_service()** | Some solutions/journeys call public_works.get_telemetry_service(); that method is not on Public Works. get_telemetry_service() lives in runtime (app state). | Either (a) Public Works exposes get_telemetry_service() or telemetry_abstraction so solutions can get telemetry, or (b) solutions get telemetry from Runtime/app state (e.g. via dependency injection). Contract: platform must provide telemetry to solutions/journeys that need it. |
| **LLM / HuggingFace** | Not in §3 (infra). Required for agents and semantic embeddings. | Contract: OpenAI and/or HuggingFace (or equivalent) must be configured and reachable for agentic and embedding flows. Pre-boot or first-use check should fail clearly if an intent that needs LLM/HF is invoked and adapter is None. |

### 9.8 Summary: What the Platform Must Have to Deliver

- **Infra (§3):** Redis, Arango, Consul, Supabase, GCS, Meilisearch, DuckDB—all required, pre-boot validated.
- **Ingestion (§9.2):** Upload, EDI, API—all required. EDI config required so EDI adapter is created. API and Upload use file_storage.
- **Parsing (§9.3):** All parsing capabilities required (PDF, Word, Excel, CSV, JSON, Image, HTML, Text, Mainframe, Kreuzberg, Data model, SOP, Workflow). Cobrix likely required soon for mainframe.
- **EDA / analytics (§9.4):** pandas and openpyxl required for EDA agent and Excel parsing. plotly, numpy, PyYAML already in use.
- **Storage/state/registry/auth:** Covered by §3.
- **Semantic/deterministic/search:** semantic_data, deterministic_compute, semantic_search, knowledge_discovery—backed by §3.
- **Agentic:** LLM adapter (OpenAI) and HuggingFace adapter (or equivalent) required for agents and semantic embeddings.
- **Visualization:** Visual generation abstraction (plotly/numpy) required for outcomes.
- **Civic:** Artifact Plane and Telemetry must be available to intents/solutions that call get_artifact_plane() or need telemetry; current code assumes public_works provides them—either add to Public Works or inject via Runtime.

When this section is satisfied **in addition to §1–§8**, the platform can deliver on solutions, journeys, and intents as implemented. Any new intent or journey that requires a new capability (e.g. a new parsing type or a new Civic surface) must be reflected here and in §3 if it needs new infra.

### 9.9 Phase Boundaries: Foundation vs Capability

**Purpose:** Clarify what must exist by Φ3 (G3) vs Φ4/Φ5 vs "when an intent runs," so we don't conflate backing services with libraries or Civic surfaces.

| Group | Examples | When validated | Phase / gate |
|-------|----------|----------------|--------------|
| **Backing services (G3)** | Redis, Arango, Consul, Supabase, GCS, Meilisearch, DuckDB | Pre-boot (connectivity) before Φ3 | Must exist by Φ3; pre-boot checks them. |
| **Backing services (when intent runs)** | LLM endpoints (OpenAI, HuggingFace), Cobrix container, EDI partners | First use or intent routing | Not blocking Φ3; fail clearly when an intent that needs them is invoked. |
| **Libraries** | pandas, openpyxl, PyYAML, redis, arango, httpx | Importable at G2 or first use | No connectivity check; require in environment/requirements. |
| **Civic surfaces** | Artifact Plane, Telemetry | Injected or exposed via Public Works / Runtime | Document who provides them (§9.7); must be available to intents that need them. |

- **By Φ3:** All seven backing services (§3) are present and validated (pre-boot passed). Runtime graph is built; Public Works, StateSurface, WAL, IntentRegistry, ExecutionLifecycleManager exist.
- **By Φ4:** Background workers, event loops, agents, websockets, schedulers. Out of scope for foundation gates.
- **By Φ5:** Health green, invariants. Out of scope for foundation gates.
- **When an intent runs:** LLM/HuggingFace, Cobrix, EDI config—required for that intent; adapter may be None if config absent; intent fails with clear message.

### 9.10 Holistic Audit: What Else Might Be Missing

This subsection captures additional capabilities or dependencies that could be missing from the contract. Review periodically.

| Area | Status | Notes |
|------|--------|--------|
| **pandas / openpyxl** | Added §9.4 | Required for EDA and Excel; must be in requirements/environment. |
| **EDI config** | Added §9.2 | EDI adapter exists; config (partners, AS2) must be provided. pyas2lib optional for AS2. |
| **API ingestion** | Added §9.2 | We have it: APIAdapter + file_storage. No extra infra. |
| **Cobrix** | §9.3 | Likely required soon; config-driven for mainframe. |
| **YAML** | In use | PyYAML in requirements; data model processing uses built-in yaml. No separate YAML adapter. |
| **Telemetry abstraction** | Gap §9.7 | Public Works may not expose telemetry_abstraction; NurseSDK and solutions need it. |
| **Artifact Plane** | Gap §9.7 | get_artifact_plane() not on Public Works; must be provided. |
| **Structured extraction / LLM** | In table §9.1 | OpenAI/HF required for agents and embeddings. |
| **OCR / image** | §9.3 | Image processing abstraction required; adapter in-process. |
| **BPMN / Workflow** | §9.3 | Workflow processing (BPMN XML) required; in-process. |

**Possible future additions (not yet contract):** External AS2/SFTP server connectivity for EDI receive; webhook endpoint configuration for API ingestion; additional export formats (e.g. Parquet); real-time streaming ingestion. When a client ask or new journey requires them, add to this section and to §3 or §9 as appropriate.

---

## 10. References

- [HYBRID_CLOUD_VISION](../HYBRID_CLOUD_VISION.md) — deployment north star (Option C, three planes, phased evolution). Contract defines *what* we need; that doc defines *where* it runs.
- [PLATFORM_INVENTORY](../testing/PLATFORM_INVENTORY.md) — what's in the platform vs what we need; superseded by this contract for "required."
- [PATH_TO_WORKING_PLATFORM](../testing/PATH_TO_WORKING_PLATFORM.md) — roadmap (pre-boot → boot → first request → critical path); pre-boot must enforce this contract.
- [ARANGO_REGISTRY_ABSTRACTION_SEAM](../testing/ARANGO_REGISTRY_ABSTRACTION_SEAM.md) — why Arango currently blocks registry; contract §6 addresses this.
- [ARCHITECTURE_NORTH_STAR](../ARCHITECTURE_NORTH_STAR.md) — storage strategy (DuckDB deterministic, Arango semantic); contract §3 aligns.
- Code: `runtime_services.py` (required list), `foundation_service.py` (_create_adapters, _create_abstractions), `env_contract.py`, `runtime_main.py`.
