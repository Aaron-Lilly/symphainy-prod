# Why Foundations Work and How They Behave

**Purpose:** Step 2 deliverable for MEET_IN_THE_MIDDLE_PLAN. One place that explains what is guaranteed at boot, what is optional, and what fails and how — so the next layer (runtime probe) and Team B can rely on it.

**Full Step 2 scope:** The **Public Works probe** is a multi-day review: **all adapters**, the **5-layer pattern** (Layer 0→1→2→3→4), and **vision alignment** with updated_platform_vision. See [PUBLIC_WORKS_PROBE_PLAN.md](PUBLIC_WORKS_PROBE_PLAN.md) for Phases A–F (adapter inventory, abstraction inventory, protocol audit, 5-layer flow, vision alignment + gap map, Curator boundary). This doc is a first-pass snapshot; it should be updated when that review is complete.

**References:** [STEP2_FOUNDATIONS_PROBE.md](testing/STEP2_FOUNDATIONS_PROBE.md), [CONFIG_ACQUISITION_SPEC.md](architecture/CONFIG_ACQUISITION_SPEC.md), [PRE_BOOT_SPEC.md](architecture/PRE_BOOT_SPEC.md), [PLATFORM_VISION_RECONCILIATION.md](PLATFORM_VISION_RECONCILIATION.md) §3, [WHY_GENESIS_WORKS_AND_HOW_BOOT_BEHAVES.md](WHY_GENESIS_WORKS_AND_HOW_BOOT_BEHAVES.md).

---

## What is guaranteed at boot (when pre-boot passes)

1. **Canonical config** — One config dict from `load_platform_config()`; nested keys for redis, consul, duckdb; flat keys for arango_*, supabase_*, gcs_*, meilisearch_*. No env reads inside Public Works for platform infra.

2. **Seven backing services** — Redis, Arango, Consul, Supabase, GCS, Meilisearch, DuckDB are reachable and authorized (pre-boot checked). Public Works then creates adapters and abstractions for all of them.

3. **Public Works adapters (required)** — RedisAdapter, ConsulAdapter, ArangoAdapter, ArangoGraphAdapter, MeilisearchAdapter, SupabaseAdapter, GCSAdapter, SupabaseFileAdapter, DuckDBAdapter. Parsing adapters (CSV, Excel, PDF, Word, HTML, Image, JSON), UploadAdapter, APIAdapter, VisualGenerationAdapter. All created when config is present and pre-boot passed.

4. **Public Works abstractions (required)** — StateManagementAbstraction (with Arango collections ensured via _ensure_state_collections), ServiceDiscoveryAbstraction, SemanticSearchAbstraction (if Meilisearch), SemanticDataAbstraction, AuthAbstraction (if Supabase), **RegistryAbstraction** (if Supabase — and Supabase is required by pre-boot), TenantAbstraction (if Supabase), FileStorageAbstraction, FileManagementAbstraction (if GCS + Supabase file), ArtifactStorageAbstraction, DeterministicComputeAbstraction (if DuckDB), IngestionAbstraction, parsing abstractions. registry_abstraction is required by RuntimeServices; it is created when supabase_adapter exists, which is guaranteed after pre-boot.

5. **Curator (registries)** — **registry_abstraction** (Public Works, Supabase-backed) exists. **IntentRegistry** and **SolutionRegistry** are created and populated in the runtime layer (service_factory) after Public Works; they are not “foundations” but depend on foundations. Config loaders (bootstrap) ran before Public Works. So at “foundations complete,” we have: config loaded, Public Works initialized, registry_abstraction available for RuntimeServices.

---

## What is optional (boot continues)

- **Kreuzberg** — Adapter not created if config["kreuzberg"] missing; log only.
- **EDI** — Adapter not created if config["edi"] missing; log only.
- **OpenAI** — Adapter not created if openai_api_key missing; log only.
- **HuggingFace** — Adapter not created if endpoint/key missing; log only.
- **EventPublisherAbstraction** — Not created if redis_streams_publisher module missing or Redis missing; log only. Other abstractions and boot proceed.

---

## What fails and how

- **Pre-boot (G3):** If any of the seven services (Redis, Arango, Supabase, GCS, Meilisearch, DuckDB, Consul) fails the check, the process **exits immediately** with a clear message. We never enter create_runtime_services(). See WHY_GENESIS_WORKS_AND_HOW_BOOT_BEHAVES.md.

- **Public Works — GCS / Supabase file / Arango:** If required config is missing (e.g. GCS_PROJECT_ID, GCS_BUCKET_NAME), Public Works raises **RuntimeError** during _create_adapters or _create_abstractions. If _ensure_state_collections() fails (e.g. Arango collection creation fails), Public Works.initialize() catches, logs, and returns False; service_factory then raises RuntimeError and the process exits. So we do not build a partial graph.

- **Public Works — registry_abstraction:** registry_abstraction is created only when supabase_adapter exists. Pre-boot ensures Supabase is up; so in normal boot after pre-boot, supabase_adapter is created and registry_abstraction is created. If Supabase were missing, pre-boot would have already exited. So at “foundations complete,” registry_abstraction is non-None.

- **RuntimeServices validation:** If registry_abstraction (or any other required field) were None, RuntimeServices.__post_init__ raises ValueError. That would indicate a bug (e.g. Supabase passed pre-boot but adapter creation failed) or a code path that skipped creating registry_abstraction; in current code path, registry_abstraction is set when Supabase adapter exists.

---

## Curator: one sentence

**Curator** is the umbrella name for platform registry and metadata authority. It is **not** a new service. It is implemented today by: **registry_abstraction** (Public Works, Supabase-backed), **IntentRegistry** (runtime, in-memory, populated by service_factory), **SolutionRegistry** (runtime, platform_sdk), **RealmRegistry** (runtime, used by control room / admin), config loaders (bootstrap), and (where applicable) **SemanticProfileRegistry** (foundations/libraries/registries). No separate “Curator” component is required; the name denotes this set of responsibilities (PLATFORM_VISION_RECONCILIATION §3).

---

## Summary

- **Why foundations work:** Config is single-source (bootstrap); pre-boot fails at the door for the seven services; Public Works uses only that config and creates adapters/abstractions in a fixed order; registry_abstraction is created when Supabase is present (guaranteed after pre-boot); RuntimeServices validation ensures no None for required fields.
- **How they behave:** When pre-boot passes, Public Works creates all required adapters and abstractions; optional ones (Kreuzberg, EDI, OpenAI, HuggingFace, EventPublisher) may be missing with only a log. Failures in required steps (GCS, Supabase file, Arango state collections, registry_abstraction) raise or return False and abort boot. Curator = existing registries and config loaders; no separate service.
