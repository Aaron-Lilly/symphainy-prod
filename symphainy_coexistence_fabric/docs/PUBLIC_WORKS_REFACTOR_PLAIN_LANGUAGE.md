# Public Works Refactor — Plain-Language Guide

**Purpose:** Explain what’s actually broken and what we’re doing in P1–P6 so it’s easy to visualize and decide. This doc answers your specific questions and scopes what’s in vs out.

---

## P1: Control Room — use genesis protocol status for infrastructure health

### What’s broken

The **Control Room** (admin dashboard) has a method `_get_infrastructure_health()` that builds a small health map for the UI. Right now it does this by reaching **directly onto Public Works adapters** (`public_works.arango_adapter`, `redis_adapter`, `gcs_adapter`) — “do we have an adapter instance?” with a TODO for a real check. That’s a **control room design flaw**: Control Room was built before we had the genesis protocol, so it never had a proper source of truth for infrastructure health.

### What we’re doing

Control Room should **check genesis protocol status** for infrastructure health instead of touching adapters or abstractions. Genesis (and pre-boot) already define what “backing services are reachable” means; the platform should expose that status so the Control Room can consume it. So:

- **Remove** direct adapter access from Control Room.
- **Add or use** a surface that exposes genesis/pre-boot status (e.g. “which services passed pre-boot; last validation result”). Control Room calls that surface for infrastructure health, not Public Works adapters or abstraction health_check().

No new abstraction health_check() on State/FileStorage for this use case — the source of truth is genesis protocol status.

---

## P2: Return protocol from all relevant get_*; DeterministicEmbeddingStorageProtocol (Registry deferred to Curator)

### What “return protocol from all relevant get_*” means

Today the foundation service has methods like:

- `get_state_abstraction()` → return type is **StateManagementProtocol** ✅  
- `get_file_storage_abstraction()` → **FileStorageProtocol** ✅  
- `get_artifact_storage_abstraction()` → **ArtifactStorageAbstraction** (concrete class) ❌  
- `get_ingestion_abstraction()` → **Optional[Any]** ❌  
- `get_semantic_data_abstraction()` → **Optional[Any]** ❌  
- `get_event_publisher_abstraction()` → **Optional[Any]** ❌  
- `get_visual_generation_abstraction()` → **VisualGenerationAbstraction** (concrete) ❌  

“Return protocol” means: **change the method’s return type (and docstring) to the protocol interface**, and keep returning the same underlying object. Callers then depend on the **interface**, not the concrete class. So: `get_artifact_storage_abstraction()` → `Optional[ArtifactStorageProtocol]`, `get_ingestion_abstraction()` → `Optional[IngestionProtocol]`, and similarly for semantic_data, event_publisher, visual_generation.

### Registry: defer to Curator flow

**RegistryAbstraction** is too generic if Supabase is what it exposes — services need to register in **Consul** (service discovery), and the split between “registry” (lineage/metadata) and “service registration” (Consul) is a Curator-boundary question. So we **defer** defining a RegistryProtocol and wiring it in P2. Add it to the Curator flow (or Phase F) and decide what to do with Registry/Curator/Consul together before locking a protocol.

### DeterministicEmbeddingStorageProtocol (not DeterministicComputeProtocol)

We use **DuckDB** in Public Works specifically for **deterministic embeddings** (schema fingerprints, pattern signatures) — store and retrieve, repeatable. So the protocol should be named **DeterministicEmbeddingStorageProtocol**, not DeterministicComputeProtocol. It describes the embedding-storage surface (e.g. `get_deterministic_embedding`, `store_deterministic_embedding`, etc.).

**Where it’s used:** data_quality_service, export_service, schema_matching_service, pattern_validation_service, deterministic_embedding_service — all via `public_works.deterministic_compute_abstraction`.

**P2 in practice (current scope):** (1) Add **DeterministicEmbeddingStorageProtocol** in `protocols/`; (2) have DeterministicComputeAbstraction implement it; (3) change every other relevant `get_*` (artifact_storage, ingestion, semantic_data, event_publisher, visual_generation) to return the protocol type. **Registry:** come back after Curator/Phase F.

---

## P3: Introduce four-service ctx; have service_factory use get_* or ctx

You said you get this one — it’s the four services on `ctx` (governance, reasoning, experience, platform) and service_factory receiving capabilities via `get_*` or `ctx` instead of direct `public_works.state_abstraction` etc. No extra explanation here.

---

## P4: Unified parsing surface (FileParsingProtocol)

### What we’re doing (and what’s reasonably achievable)

Today callers ask for **format-specific** abstractions: `get_pdf_processing_abstraction()`, `get_csv_processing_abstraction()`, etc. There is a **FileParsingProtocol** (parse_file(FileParsingRequest) → FileParsingResult) but only **MainframeProcessingAbstraction** implements it in code; other parsers don’t formally implement that protocol yet.

**Reasonable scope:**

1. **Single contract:** One parsing surface (e.g. `document_parsing` or `parse`) that takes a file reference + options and returns **FileParsingResult**. Callers don’t need to know “PDF vs CSV”; they go through one entry point. Under the hood we can still route by format (e.g. by extension or content type).
2. **All parsers implement FileParsingProtocol:** Each existing processing abstraction (PDF, CSV, Excel, Word, HTML, Image, JSON, Text, Kreuzberg, Mainframe, DataModel, Workflow, SOP) implements the same `parse_file(FileParsingRequest) -> FileParsingResult` so the platform can treat them uniformly.
3. **Declared capabilities (what we can parse):** A small, honest **list we can document and maintain** — not a black box. For example:
   - **Images:** e.g. “PNG, JPEG, TIFF; we run OCR where supported (Tesseract).” List what we actually support and any limits.
   - **PDFs:** e.g. “Text-based PDFs; extraction of text and basic structure (pages, sections). No full layout reconstruction.” Be explicit about what we don’t do.
   - **Mainframe:** e.g. “Copybook-based fixed-width; we support copybook reference + file reference. Complexity: single record type per file; multi-record or complex hierarchy = future.”
   - **Other formats:** Same idea — one short line per format (CSV, Excel, Word, HTML, JSON, etc.) with “what we do” and “what we don’t.”

We **don’t** need to over-engineer: no heavy capability registry in code for MVP. A **doc** (e.g. in `docs/` or next to the parsing entry point) that says “Supported formats and limits” plus the single protocol surface is enough to stop it being a black box and keep scope under control.

---

## P5: OpenTelemetry — add to pre-boot and expose

### Adapter connect() vs pre-boot (removed from P5)

The connect() redundancy was expected given the startup mess we saw. We can **safely remove** that item from P5 — no need to document or refactor adapter connect() vs pre-boot as part of this backlog.

### OpenTelemetry: foundational, add to pre-boot and expose

OpenTelemetry is a **foundational** part of the architecture and **should have been** an essential part of the pre-boot checklist. We need to **add it** and **expose it**:

1. **Add OpenTelemetry to pre-boot.** Extend the pre-boot checklist (see `symphainy_platform/bootstrap/pre_boot.py` and `docs/architecture/PRE_BOOT_SPEC.md`) so that telemetry/OTLP reachability (or SDK init) is validated before we consider the platform up — same contract as the other seven backing services where applicable.
2. **Wire and expose TelemetryAdapter.** In foundation_service: create TelemetryAdapter in `_create_adapters()` (or equivalent), expose it via a telemetry abstraction and/or `get_telemetry_abstraction()` so that `public_works.telemetry_abstraction` exists. Intent services and NurseSDK already do `getattr(public_works, 'telemetry_abstraction', None)`; they should get a real implementation.

### Prior working implementations

There are prior working Public Works implementations of telemetry that can be used as reference:

- **symphainy_source** (older codebase):  
  - `symphainy_source/symphainy-platform/foundations/public_works_foundation/infrastructure_adapters/telemetry_adapter.py` — OpenTelemetry adapter (trace, metrics, OTLP).  
  - `symphainy_source/symphainy-platform/foundations/public_works_foundation/infrastructure_abstractions/telemetry_abstraction.py` — TelemetryAbstraction (collect_metric, collect_trace, etc.).  
  - `symphainy_source/symphainy-platform/foundations/public_works_foundation/abstraction_contracts/telemetry_protocol.py` — TelemetryProtocol, TelemetryData, TraceSpan, etc.
- **symphainy_platform_old** (inside coexistence fabric):  
  - `symphainy_platform_old/foundations/public_works/adapters/telemetry_adapter.py` — OpenTelemetry SDK (trace, metrics, logs, OTLP), `initialize()`, `instrument_logging()`, `instrument_fastapi()`, `get_tracer()`, `get_meter()`, `is_initialized()`.

The current coexistence_fabric adapter at `symphainy_platform/foundations/public_works/adapters/telemetry_adapter.py` is already close to platform_old; it just isn’t wired in foundation_service or pre-boot. Use the prior implementations above to align wiring and pre-boot.

---

## P6: Optional S3 / generic FS adapter

**What it meant:** The written vision mentions “GCS, S3, FS”; the codebase today has GCS and Supabase file, not S3 or a generic filesystem adapter. P6 was “if we need BYOI / swappable backends for other object stores or local FS, add those adapters behind FileStorageProtocol.”

**Decision:** Stick to what’s actually in the tech stack. No new theoretical adapters now. We **drop P6** from the active refactor list (or mark it “deferred / out of scope until we have a concrete need”). The reality map and backlog should reflect that.

---

## Summary: What we’re actually doing

| Priority | What’s broken | What we’re doing |
|----------|---------------|------------------|
| **P1** | Control Room touches adapters for “health” (design flaw; built before genesis) | Control Room checks **genesis protocol status** for infrastructure health; remove direct adapter access. |
| **P2** | Many get_* return concrete or Any; no protocol for embedding storage | Return protocol from all relevant get_*; add **DeterministicEmbeddingStorageProtocol** (DuckDB embeddings). **Registry:** defer to Curator flow. |
| **P3** | No four-service ctx; service_factory uses direct attrs | Introduce ctx (governance, reasoning, experience, platform); service_factory uses get_* or ctx. |
| **P4** | Parsing is format-specific and opaque | Single parsing surface (FileParsingProtocol); all parsers implement it; document “what we can parse” (formats + limits). |
| **P5** | OpenTelemetry not in pre-boot; TelemetryAdapter never wired or exposed | Add OpenTelemetry to pre-boot checklist; wire TelemetryAdapter in foundation_service and expose telemetry_abstraction. (Adapter connect() item removed.) |
| **P6** | — | **Out of scope.** Stick to current tech stack; no S3/FS adapter for now. |

This keeps the refactor list to what’s real and achievable and answers exactly what’s broken and what we’re doing for each item.
