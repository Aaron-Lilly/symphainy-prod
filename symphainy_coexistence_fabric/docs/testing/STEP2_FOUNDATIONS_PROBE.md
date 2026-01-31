# Step 2 Foundations Probe (Public Works, Curator)

**Purpose:** Evidence from the foundations probe per MEET_IN_THE_MIDDLE_PLAN Step 2. This doc is a **first-pass boot-time snapshot** (what exists at boot, config keys, Curator = registries). The **full Step 2 scope** is the **Public Works review**: all adapters, 5-layer pattern, and vision alignment — a multi-day effort per [PUBLIC_WORKS_PROBE_PLAN.md](../PUBLIC_WORKS_PROBE_PLAN.md).

**References:** [STEP1_GENESIS_PROBE.md](STEP1_GENESIS_PROBE.md), [CONFIG_ACQUISITION_SPEC.md](../architecture/CONFIG_ACQUISITION_SPEC.md), [PRE_BOOT_SPEC.md](../architecture/PRE_BOOT_SPEC.md), [PLATFORM_VISION_RECONCILIATION.md](../PLATFORM_VISION_RECONCILIATION.md) §3.

---

## 1. Public Works — What Actually Exists at Boot

Evidence from Step 1 boot probe + code trace (`foundation_service.py`).

### 1.1 Config keys that drive Public Works

Canonical config comes from `load_platform_config()` (bootstrap). Public Works consumes:

| Config key / shape | Used for | Required at boot? |
|--------------------|----------|--------------------|
| `redis` (nested: host, port, db, password) | RedisAdapter | Yes (pre-boot checks Redis) |
| `consul` (nested: host, port, token) | ConsulAdapter | Yes (pre-boot checks Consul) |
| `arango_url`, `arango_username`, `arango_password`, `arango_database` | ArangoAdapter, ArangoGraphAdapter | Yes (pre-boot checks Arango) |
| `supabase_url`, `supabase_anon_key`, `supabase_service_key`, `supabase_jwks_url`, `supabase_jwt_issuer` | SupabaseAdapter, RegistryAbstraction, AuthAbstraction, TenantAbstraction | Yes (pre-boot checks Supabase) |
| `gcs_project_id`, `gcs_bucket_name`, `gcs_credentials_json` | GCSAdapter, FileStorageAbstraction, ArtifactStorageAbstraction | Yes (pre-boot checks GCS) |
| `meilisearch_host`, `meilisearch_port`, `meilisearch_key` | MeilisearchAdapter, SemanticSearchAbstraction | Yes (pre-boot checks Meilisearch) |
| `duckdb` (nested: database_path, read_only) | DuckDBAdapter, DeterministicComputeAbstraction | Yes (pre-boot checks DuckDB) |
| `kreuzberg` (nested) | KreuzbergAdapter | No — optional; not created if missing |
| `edi` (nested) | EDIAdapter | No — optional |
| `openai_api_key`, `openai_base_url` | OpenAIAdapter | No — optional |
| `huggingface_endpoint_url`, `huggingface_api_key` | HuggingFaceAdapter | No — optional |

Bootstrap `build_canonical_config()` produces nested `redis`, `consul`, `duckdb` and flat `arango_*`, `supabase_*`, `gcs_*`, `meilisearch_*`. Public Works expects these; no env reads inside Public Works (config-only).

### 1.2 Adapters created at boot (when config present)

| Adapter | Config driver | Created when | Notes |
|---------|----------------|--------------|-------|
| RedisAdapter | `config["redis"]` | Present | Pre-boot validates; adapter connects in initialize() |
| ConsulAdapter | `config["consul"]` | Present | Same |
| ArangoAdapter, ArangoGraphAdapter | `arango_url`, etc. | Present | Same; _ensure_state_collections() runs after state_abstraction |
| MeilisearchAdapter | `meilisearch_host`, `meilisearch_port`, `meilisearch_key` | Always (defaults) | connect() may fail; log warning |
| SupabaseAdapter | `supabase_url`, `supabase_anon_key` | Both set | Same |
| GCSAdapter | `gcs_project_id`, `gcs_bucket_name`, `gcs_credentials_json` | All set | Required; RuntimeError if missing |
| SupabaseFileAdapter | `supabase_url`, `supabase_service_key` | Both set | Same |
| DuckDBAdapter | `config["duckdb"]` | Present | database_path, read_only |
| CSV, Excel, PDF, Word, HTML, Image, JSON | — | Always | No config; created unconditionally |
| VisualGenerationAdapter | — | Always | No config |
| OpenAIAdapter | `openai_api_key` | Optional | Log warning if missing |
| HuggingFaceAdapter | `huggingface_endpoint_url`, `huggingface_api_key` | Both set | Optional |
| KreuzbergAdapter | `config["kreuzberg"]` | Optional | Not created if missing |
| EDIAdapter | `config["edi"]` | Optional | Not created if missing |
| UploadAdapter, APIAdapter | After file_storage_abstraction | Always | Require file_storage_abstraction |

### 1.3 Abstractions created at boot

| Abstraction | Depends on | Created when | Fails when |
|-------------|------------|--------------|------------|
| StateManagementAbstraction | redis_adapter, arango_adapter | Always | — |
| _ensure_state_collections() | arango_adapter | If Arango present | Raises if Arango collection creation fails |
| ServiceDiscoveryAbstraction | consul_adapter | Always | — |
| SemanticSearchAbstraction | meilisearch_adapter | If Meilisearch present | — |
| KnowledgeDiscoveryAbstraction | arango_adapter, arango_graph_adapter | If both present | — |
| SemanticDataAbstraction | arango_adapter | Required | RuntimeError if Arango missing |
| AuthAbstraction | supabase_adapter | If Supabase present | — |
| **RegistryAbstraction** | supabase_adapter | If Supabase present | **None if Supabase missing** — RuntimeServices requires it |
| TenantAbstraction | supabase_adapter, redis_adapter | If Supabase present | — |
| FileStorageAbstraction | gcs_adapter, supabase_file_adapter, gcs_bucket_name | Required | RuntimeError if GCS/Supabase file missing |
| FileManagementAbstraction | gcs_adapter, supabase_file_adapter | If both present | — |
| ArtifactStorageAbstraction | gcs_adapter, supabase_file_adapter, bucket_name | Required | RuntimeError if missing |
| VisualGenerationAbstraction | visual_generation_adapter, file_storage_abstraction | Always | — |
| EventPublisherAbstraction | redis_adapter + redis_streams_publisher | Optional | Log warning if module missing |
| DeterministicComputeAbstraction | duckdb_adapter | If DuckDB present | — |
| IngestionAbstraction | upload_adapter, edi_adapter, api_adapter | After file_storage | — |
| Parsing abstractions | Various adapters + temp StateSurface | After state_abstraction | — |

**Guaranteed at boot (when pre-boot passes):** All seven pre-boot services are reachable; Public Works creates Redis, Consul, Arango, Meilisearch, Supabase, GCS, DuckDB adapters and state, registry, file, artifact abstractions. registry_abstraction is created only when supabase_adapter exists; pre-boot ensures Supabase is up, so registry_abstraction is created.

**Optional / may be missing:** Kreuzberg, EDI, OpenAI, HuggingFace, EventPublisher (redis_streams_publisher). Log warnings only; boot continues.

---

## 2. Curator — Where “Curator” Lives in Code

Per PLATFORM_VISION_RECONCILIATION §3: **Curator is not a new service.** It is the **umbrella name** for existing registry and config responsibilities.

| Responsibility | Where it lives | Created when |
|-----------------|----------------|--------------|
| **registry_abstraction** | Public Works (`RegistryAbstraction`, Supabase-backed) | PublicWorks.initialize() → _create_abstractions(); requires supabase_adapter |
| **IntentRegistry** | Runtime (`service_factory.create_runtime_services`) | Created in service_factory; intent handlers registered from realm intent services |
| **SolutionRegistry** | Runtime (`civic_systems.platform_sdk.solution_registry.SolutionRegistry`) | Created in service_factory; solutions register/activate during initialize_solutions |
| **RealmRegistry** | Runtime (`runtime/realm_registry.py`) | Used by control_room_service, admin_dashboard; may be built from solution/realm discovery (not created in service_factory in same way — check call sites) |
| **Config loaders** | Bootstrap (`load_platform_config`, canonical config) | Before create_runtime_services |
| **SemanticProfileRegistry** | Foundations (`foundations/libraries/registries/semantic_profile_registry.py`) | Library; used by capabilities that need semantic profiles |

**Validation:** Registry access and registration behave as documented: IntentRegistry is populated by service_factory from intent services; RuntimeServices.registry_abstraction is required and used by runtime_api for artifact_index, pending_intents; SolutionRegistry is populated during solution init. No separate “Curator” component; the name denotes this set of registries and config.

---

## 3. Reconciliation with CONFIG_ACQUISITION_SPEC and PRE_BOOT_SPEC

- **CONFIG_ACQUISITION_SPEC:** Env files loaded in order (.env.secrets, config/development.env, .env); canonical config built from os.environ. Public Works receives that config; no env reads inside Public Works for platform infra. **Aligned.**
- **PRE_BOOT_SPEC:** Seven services checked in order (Redis, Arango, Supabase, GCS, Meilisearch, DuckDB, Consul); pre-boot uses only canonical config; exits on first failure. **Aligned.** Public Works init runs only after pre-boot passes, so required adapters/abstractions are created.

---

## 4. Known Gaps / Deferred

- **RealmRegistry creation:** RealmRegistry class exists; exact creation path for control_room (who injects realm_registry) may need a follow-up trace in Step 4 (civic systems).
- **Startup logic in adapters:** Some adapters may still perform connection or schema work that could be considered “startup”; refactor to keep “connect vs ensure schema” consistent with PRE_BOOT_SPEC (pre-boot = connect only; schema in init) is deferred to later refinement.
- **Optional adapters (Kreuzberg, EDI, OpenAI, HuggingFace):** Documented as optional; no change in this step.

---

**First-pass deliverable:** [WHY_FOUNDATIONS_WORK_AND_HOW_THEY_BEHAVE.md](../WHY_FOUNDATIONS_WORK_AND_HOW_THEY_BEHAVE.md).

**Full Step 2 scope:** See [PUBLIC_WORKS_PROBE_PLAN.md](../PUBLIC_WORKS_PROBE_PLAN.md) — review all adapters, 5-layer pattern (Layer 0→1→2→3→4), validate alignment with updated_platform_vision; produce Public Works Reality Map, vision alignment + gap map, refactor backlog; update "why foundations work and how they behave" when the review is complete.
