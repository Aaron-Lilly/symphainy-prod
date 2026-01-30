# Step 2 Public Works Probe Run

**Purpose:** Evidence from the Public Works probe run — confirm what Public Works does at boot and how it works, mirroring the genesis probe (Step 1). Run after completing P1–P5 refactors and P3 Part B (service_factory use get_*).

**References:** [STEP1_GENESIS_PROBE.md](STEP1_GENESIS_PROBE.md), [PUBLIC_WORKS_REALITY_MAP.md](PUBLIC_WORKS_REALITY_MAP.md), [STEP2_FOUNDATIONS_PROBE.md](STEP2_FOUNDATIONS_PROBE.md).

---

## How to run

1. **Prerequisites:** Infra satisfying pre-boot (Redis, Arango, Consul, Supabase, GCS, Meilisearch, DuckDB, **OTEL_EXPORTER_OTLP_ENDPOINT** reachable). Same as genesis.
2. **Probe 04 (static trace):**  
   `python3 probes/probe_04_public_works.py`  
   Output: adapters declared, abstractions declared, 5-layer evidence, callers table (service_factory now uses get_*).
3. **Boot probe (runtime):**  
   `python3 runtime_main.py`  
   Confirm: G2 → G3 → Φ3; PublicWorks.initialize() succeeds; StateSurface, WAL, ELM, RuntimeServices built with capabilities from get_*; FastAPI starts (or fails only on bind/port).

---

## What we are confirming

- **Layer 0 (adapters):** Created in `_create_adapters()`; config-driven; TelemetryAdapter created when OTEL endpoint set.
- **Layer 1 (abstractions):** Created in `_create_abstractions()`; wrap adapters; telemetry_abstraction exposed.
- **Layer 2 (protocols):** get_* return protocol types where defined (State, FileStorage, ArtifactStorage, Ingestion, SemanticData, EventPublisher, VisualGeneration, DeterministicEmbeddingStorage); Registry/redis via get_registry_abstraction(), get_redis_adapter().
- **Layer 3/4 (service):** foundation_service orchestrates; **service_factory** uses **get_*** only (no direct public_works.state_abstraction, etc.) for StateSurface, WAL, ExecutionLifecycleManager, RuntimeServices.
- **Control Room:** Uses genesis/pre-boot status for infrastructure health (no direct adapter access).
- **Pre-boot:** OTEL required and validated; boot fails if OTEL_EXPORTER_OTLP_ENDPOINT missing or unreachable.

---

## Outcome (filled after run)

- **Probe 04 output:** Ran successfully; callers table shows service_factory uses get_state_abstraction(), get_file_storage_abstraction(), get_redis_adapter(), get_registry_abstraction(), get_artifact_storage_abstraction() for StateSurface, WAL, ELM, RuntimeServices. Adapters and abstractions lists include telemetry_adapter and telemetry_abstraction.
- **Boot sequence:** G2 (load_platform_config) → G3 (pre_boot_validate: all required services passed, including OTEL) → Φ3 (PublicWorks.initialize() → StateSurface → WAL → IntentRegistry → solutions → ExecutionLifecycleManager → RuntimeServices). Runtime object graph built successfully; FastAPI app created with all routes.
- **Failures (if any):** Port 8000 already in use (bind error). Not a Public Works or genesis bug — boot completed; only uvicorn bind failed.
- **Conclusion:** Public Works refactor (P1, P2, P5, P3 Part B) is validated. Boot uses get_* only; no direct adapter/abstraction attr access in service_factory. Genesis → pre-boot → Φ3 behavior matches STEP1.

---

## Remaining refactor (not in this run)

- **P3 Part A:** Four-service ctx (ctx.governance, ctx.reasoning, ctx.experience, ctx.platform) — depends on Curator/Phase F; deferred.
- **P4:** Unified parsing surface (FileParsingProtocol for all parsers; single document_parsing entry) — next step; see PUBLIC_WORKS_REFACTOR_PLAIN_LANGUAGE.md.

---

*Probe run date: 2026-01-30*
