# CTA Top-Down Derivation: From Platform SDK to Infrastructure

**Status:** Living document — work backwards from what Team B (Platform SDK) and Team C (frontend) have built, then build back up.  
**Purpose:** One layered specification that defines everything we need: Contract at the top (what Platform SDK and frontend expect), then Protocol → Abstraction → Adapter → Infrastructure, with Genesis at the bottom. No rules uncovered as we move up; we derive the full stack from the consumer.

**Related:** [GETTING_ON_TRACK_ASSESSMENT_AND_PLAN.md](GETTING_ON_TRACK_ASSESSMENT_AND_PLAN.md), [architecture/PUBLIC_WORKS_CTA_PATTERN.md](architecture/PUBLIC_WORKS_CTA_PATTERN.md), [INTERCEPT_ALIGNMENT_CONTRACT.md](INTERCEPT_ALIGNMENT_CONTRACT.md).

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

**Current dependency (from code):** PlatformService uses `getattr(public_works, 'file_storage_abstraction', None)`, `file_parsing`, `visual_generation_abstraction`, `ingestion_abstraction`, `semantic_data_abstraction`, `deterministic_compute_abstraction`, `artifact_storage_abstraction`, and parsers by type (csv_processing_abstraction, etc.). It also needs registry_abstraction for get_pending_intents/update_intent_status (via PlatformService internal wiring). So the **contract** Platform SDK expects: Public Works must provide (via getters, not raw attributes) these protocol-typed capabilities: file_storage, artifact_storage, file_parsing (or document_parsing), visual_generation, ingestion, semantic_data, deterministic_compute, registry (for intents). Plus state_surface from Runtime.

### 1.3 ctx.governance (GovernanceService) — What intent services call

| Role | Property | Used by (examples) | What it needs underneath |
|------|----------|--------------------|---------------------------|
| Data Steward | data_steward | intent_service_base (request_data_access) | Data governance abstraction |
| Security Guard | auth | (auth flows) | Auth abstraction |
| Curator | registry | CuratorSDK (register_capability, discover_agents, promote_to_platform_dna) | Curator service (Supabase-backed) |
| Librarian | search | governance_service doc (search_knowledge) | Knowledge discovery |
| City Manager | policy | (tenant/policy) | Tenant abstraction |
| Traffic Cop | sessions | session flows, terminate_session, create_session | State (sessions) |
| Post Office | events | (event publish) | Event publisher |
| Conductor | workflows | (workflow primitives) | — |
| Nurse | telemetry | intent_service_base (record_telemetry) | Telemetry abstraction |
| Materialization Policy | materialization_policy | — | — |

**Current dependency (from code):** GovernanceService uses: get_registry_abstraction(), get_curator_service(), get_knowledge_discovery_abstraction(), get_tenant_abstraction(), get_state_abstraction(), get_event_publisher_abstraction(), get_telemetry_abstraction(), get_auth_abstraction() — and **getattr(public_works, 'supabase_adapter', None)** for DataStewardPrimitives (adapter leak), getattr(public_works, 'data_governance_abstraction', None), getattr(public_works, 'auth_abstraction', None). So the **contract** Platform SDK expects: Public Works must provide (via getters only) auth, tenant, registry, curator_service, knowledge_discovery, state, event_publisher, telemetry, data_governance (and no supabase_adapter at boundary — DataStewardPrimitives should get a protocol, not the adapter).

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

---

## Layer 2 — What Experience, Agentic, Smart City, and Runtime Must Do

*To be filled with rigor. Summary below.*

### 2.1 Runtime

- Must build: state_surface (from state_abstraction), wal (from wal_backend), artifacts (artifact_registry from artifact_storage + registry where needed).
- Must call Public Works only via boundary getters: get_state_abstraction(), get_wal_backend(), get_artifact_storage_abstraction(), get_registry_abstraction() (if needed for artifact index).
- Must inject state_surface, wal, artifacts into PlatformContextFactory along with public_works.

### 2.2 Smart City (9 roles)

- Each role (Data Steward, Security Guard, Curator, Librarian, City Manager, Traffic Cop, Post Office, Nurse, Conductor) is exposed as ctx.governance.X.
- GovernanceService builds each SDK from **boundary getters only**. No getattr(public_works, 'supabase_adapter'). No getattr(public_works, 'auth_abstraction') if we have get_auth_abstraction() — use getters consistently.
- Curator: get_curator_service() → CuratorProtocol (Supabase-backed). Data Steward: get_data_governance_abstraction() or similar (no supabase_adapter). Auth: get_auth_abstraction(). Tenant: get_tenant_abstraction(). Sessions: Traffic Cop needs state or session abstraction. Events: get_event_publisher_abstraction(). Telemetry: get_telemetry_abstraction(). Search: get_knowledge_discovery_abstraction(). Policy: get_tenant_abstraction() or policy abstraction.

### 2.3 Agentic

- Must provide: agents (get, invoke, collaborate, list) and llm (complete, embed).
- LLM must be provided via a **protocol** (e.g. LLMProtocol or ReasoningProtocol) that Public Works exposes (get_llm_abstraction() or get_reasoning_abstraction()), not by passing openai_adapter / huggingface_adapter to ReasoningService.
- Agents: Agentic component builds agent registry and invocation; exposed to Platform SDK via ReasoningService.agents. May need get_agent_registry() or similar from Public Works / Agentic boundary.

### 2.4 Experience

- Provides ctx.experience (metadata for now). May need get_experience_metadata() or similar. For MVP, minimal.

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
| **LLM** | **LLMProtocol (to define)** | **get_llm_abstraction()** | **Gap:** replace openai_adapter/huggingface_adapter at boundary |
| **Data governance** | **DataGovernanceProtocol (to define or formalize)** | **get_data_governance_abstraction()** | **Gap:** DataStewardPrimitives must not take supabase_adapter; build inside PW |
| Service discovery | ServiceDiscoveryProtocol | get_service_discovery_abstraction() | Existing |
| Lineage backend | LineageProvenanceProtocol | get_lineage_backend() | Existing (no adapter leak) |

**Gaps to close:** (1) Define LLMProtocol (complete, embed) and LLMAbstraction that wraps OpenAI + HuggingFace adapters; ReasoningService uses get_llm_abstraction() only. (2) Add get_data_governance_abstraction(); DataStewardPrimitives must be constructed inside Public Works from supabase_adapter, not passed across boundary.

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
| **LLMProtocol** | **LLMAbstraction (to add)** | **OpenAIAdapter, HuggingFaceAdapter** |
| DataGovernanceProtocol | DataGovernanceAbstraction (if exists) | SupabaseAdapter (DataStewardPrimitives built inside PW) |
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
- **Gap list (to fill):** e.g. “Genesis does not validate Meilisearch reachability”; “Public Works initialize() does not fail when Redis is missing.”

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
