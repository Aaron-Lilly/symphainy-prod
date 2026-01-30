# Platform SDK: Abstractions & Protocols for B-Team (Provisional)

**Purpose:** Give B-team a **reasonable perspective** of what the Platform SDK will expose so you can build with reasonable certainty. This is a **provisional** handoff: we are still completing Public Works discovery (Phases C–F). The **target shape** is described below; build against it. We will finalize the handoff after protocols, 4-layer flow, and service mapping are locked.

**Source:** Phase B of the Public Works probe. Full inventory and civic_system assignment: [PUBLIC_WORKS_REALITY_MAP.md](testing/PUBLIC_WORKS_REALITY_MAP.md) (Phase B).

**Target shape (what we're building toward):**

- **Four services on ctx:** `ctx.governance`, `ctx.reasoning`, `ctx.experience`, `ctx.platform`. Each is a **service** that exposes a curated surface; you never receive raw abstractions or call Curator/Public Works directly.
- **Protocol-typed:** Each service returns capabilities **typed to protocols** (interfaces), not concrete implementations. That gives you a stable contract and allows the platform to swap backends (BYOI) without breaking your code.
- **Platform service:** Exposes the capabilities listed below. Each row maps a **protocol** (or intended protocol surface) to how you'll get it from `ctx.platform`. Build against the **protocol** contract; the exact attribute name (e.g. `ctx.platform.storage` vs `ctx.platform.get_storage()`) may be refined when we finalize.

---

## Target: Four services on ctx

| Service | Purpose | What you get |
|---------|---------|--------------|
| **ctx.governance** | Smart City — policy, auth, tenancy | Narrow, predefined shape (e.g. check_policy, get_tenant). Mediated only; you don't get raw Auth/Tenant abstractions. |
| **ctx.reasoning** | Agentic — search, knowledge | Narrow shape (e.g. semantic search, knowledge discovery). Mediated only. |
| **ctx.experience** | Experience — user-facing metadata | Narrow shape if needed. Mediated only. |
| **ctx.platform** | Platform — storage, state, registry, parsing, compute, ingestion, etc. | Protocol-typed capabilities below. This is what you use for intent implementation. |

---

## Platform service: protocols you can build against

These are the **protocols** (or intended protocol surfaces) that the Platform service will expose. Code against these contracts; implementations live in Public Works. Protocol definitions live in `symphainy_platform/foundations/public_works/protocols/` unless noted.

### State / registry / discovery

| Capability | Protocol (build against this) | Current impl | Notes |
|------------|------------------------------|---------------|-------|
| State | **StateManagementProtocol** | StateManagementAbstraction | `store_state`, `retrieve_state`, etc. See `protocols/state_protocol.py`. |
| Service discovery | **ServiceDiscoveryProtocol** | ServiceDiscoveryAbstraction | See `protocols/service_discovery_protocol.py`. |
| Registry | (No formal protocol in code yet) | RegistryAbstraction | Registry/lineage/metadata operations. Contract TBD in Phase C; treat as "registry operations" surface. |

### Storage / file / artifact

| Capability | Protocol (build against this) | Current impl | Notes |
|------------|------------------------------|---------------|-------|
| File storage | **FileStorageProtocol** | FileStorageAbstraction | `upload_file`, `download_file`, `delete_file`, etc. See `protocols/file_storage_protocol.py`. |
| File management | **FileManagementProtocol** | FileManagementAbstraction | See `protocols/file_management_protocol.py`. |
| Artifact storage | **ArtifactStorageProtocol** | ArtifactStorageAbstraction | See `protocols/artifact_storage_protocol.py`. |

### Compute / ingestion / events

| Capability | Protocol (build against this) | Current impl | Notes |
|------------|------------------------------|---------------|-------|
| Ingestion | **IngestionProtocol** (IngestionRequest, IngestionResult) | IngestionAbstraction | `ingest` with IngestionRequest; returns IngestionResult. See `protocols/ingestion_protocol.py`. |
| Deterministic compute | (No formal protocol in code yet) | DeterministicComputeAbstraction | Embeddings/analytics. Contract TBD in Phase C; treat as "deterministic compute" surface (e.g. embeddings). |
| Event publisher | **EventPublisherProtocol** | EventPublisherAbstraction | `publish(topic, event_type, event_data, headers)`. See `protocols/event_publisher_protocol.py`. |
| Visual generation | **VisualGenerationProtocol** | VisualGenerationAbstraction | See `protocols/visual_generation_protocol.py`. |

### Semantic data (Platform slice)

| Capability | Protocol (build against this) | Current impl | Notes |
|------------|------------------------------|---------------|-------|
| Semantic data | **SemanticDataProtocol** | SemanticDataAbstraction | Store/query semantic content. See `protocols/semantic_data_protocol.py`. |

### Parsing / document (Platform slice)

| Capability | Protocol (build against this) | Current impl | Notes |
|------------|------------------------------|---------------|-------|
| Document parsing (unified) | **FileParsingProtocol** (FileParsingRequest, FileParsingResult) | All parsing abstractions | Single contract: `parse(FileParsingRequest) -> FileParsingResult`. See `protocols/file_parsing_protocol.py`. Format-specific parsers (CSV, PDF, etc.) are implementations; you call via a unified parsing surface (e.g. `ctx.platform.document_parsing.parse(...)` with file_reference + options). |
| Parsing types | — | Csv, Excel, Pdf, Word, Html, Image, Json, Text, Kreuzberg, Mainframe, DataModel, Workflow, Sop | Each maps to a parser impl; contract is FileParsingRequest/FileParsingResult. Build against FileParsingProtocol; we may expose `ctx.platform.document_parsing.by_type("pdf")` or similar. |

---

## Not exposed directly to B-team (mediated only)

- **Smart City:** Auth, Tenant, Authorization, KnowledgeGovernance — access only via **ctx.governance** (narrow, predefined shape). You never get the raw abstractions.
- **Agentic:** SemanticSearch, KnowledgeDiscovery — access only via **ctx.reasoning**.
- **Experience:** ContentMetadata (if wired) — access only via **ctx.experience**.

---

## How to build with reasonable certainty

1. **Code against protocols, not concretes.** Import and type-hint against the protocol types (e.g. `StateManagementProtocol`, `FileStorageProtocol`, `IngestionProtocol`, `FileParsingProtocol`) from `symphainy_platform/foundations/public_works/protocols/`. The runtime will inject implementations; you don't care which abstraction backs them.
2. **Assume four services on ctx.** Your intent handler receives `ctx` with `ctx.governance`, `ctx.reasoning`, `ctx.experience`, `ctx.platform`. Use **ctx.platform** for state, storage, registry, ingestion, parsing, semantic data, deterministic compute, events, visual generation. Use **ctx.governance** / **ctx.reasoning** / **ctx.experience** only for the narrow, mediated surfaces we define.
3. **Parsing:** Use **FileParsingRequest** and **FileParsingResult** from `protocols/file_parsing_protocol.py`. Pass `file_reference` (State Surface reference) and options; get back standardized parsing result. Don't depend on format-specific abstraction classes.
4. **Gaps (TBD in Phase C):** Registry and DeterministicCompute don't have a formal Protocol in code yet. Build against the **behavior** you need (registry/lineage operations; embeddings/analytics); we'll lock the protocol surface when we complete Phase C.

---

## When we finalize

After Public Works Phases C–F (protocols, 4-layer flow, service mapping, Curator boundary), we will:

- Lock the **protocol** list and any new protocols (e.g. Registry, DeterministicCompute).
- Lock the **ctx** shape (exact attribute names: `ctx.platform.get_storage()` vs `ctx.platform.storage`, etc.).
- Publish a **final** handoff; we'll communicate any small migration from this provisional shape.

Until then, this doc is the **provisional** contract. Build against the protocols and four-service shape above; we'll align the final implementation to this target.

---

## Handoff package (provisional)

- **This doc** — Provisional Platform SDK: four services, protocol-typed capabilities, how to build with reasonable certainty.
- **platform_sdk_defined.md** — Intercept model, intent contracts, Platform SDK role.
- **PUBLIC_WORKS_REALITY_MAP.md (Phase B)** — Full abstraction inventory and civic_system assignment.
- **Intent contracts** — docs/intent_contracts/ (see README there for status and ownership).
- **Protocols (code)** — `symphainy_platform/foundations/public_works/protocols/` — source of truth for protocol contracts you can import and type against.
