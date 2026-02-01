# Platform SDK: Abstractions & Protocols for B-Team (Provisional)

**Purpose:** Give B-team a **reasonable perspective** of what the Platform SDK will expose so you can build with reasonable certainty. This is a **provisional** handoff: we are still completing Public Works discovery (Phases C–F). The **target shape** is described below; build against it. We will finalize the handoff after protocols, 4-layer flow, and service mapping are locked.

**Canonical intercept (January 2026):** For ownership and the formal intercept, use **[INTERCEPT_ALIGNMENT_CONTRACT.md](INTERCEPT_ALIGNMENT_CONTRACT.md)** (we build to, you build from) and **[PLATFORM_SDK_REQUIREMENT_SPEC.md](PLATFORM_SDK_REQUIREMENT_SPEC.md)** (Team B requirement spec — deep dive definition of the intercept). This doc remains the protocol/capability reference; the contract and requirement spec define the boundary and build obligations.

**Source:** Phase B of the Public Works probe. Full inventory and civic_system assignment: [PUBLIC_WORKS_REALITY_MAP.md](testing/PUBLIC_WORKS_REALITY_MAP.md) (Phase B).

---

## Correction: What ctx.platform actually exposes (to be reconciled at review)

**Earlier wording overstated what ctx.platform exposes.** Ownership will be reconciled at review; flagging now so you don't lock the wrong shape.

| Capability | Earlier (wrong) | Corrected ownership |
|------------|------------------|----------------------|
| **Storage** | ctx.platform | **Data Steward** (not Platform). |
| **State** | ctx.platform | **Runtime** (state is runtime surface, not Platform service). |
| **Registry** | ctx.platform | **Curator** (not Platform). |
| **Ingestion** | ctx.platform | **TBD** — may be Platform or Data Steward; we'll confirm. |
| **Compute** | ctx.platform | Unclear; to be defined. |

**What ctx.platform should expose (capability-oriented):** parse, analyze, visualize, synthesize, generate SOP, generate workflow, generate POC proposal, generate roadmap, metrics, and similar **capability surfaces** — not raw storage/state/registry. Build your provisional wrapper around that intent; we'll lock the exact list at review.

---

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
| **ctx.platform** | Platform — **capability surfaces**: parse, analyze, visualize, synthesize, generate SOP/workflow/POC/roadmap, metrics, etc. (Not storage/state/registry — those are Data Steward / Runtime / Curator; to be reconciled at review.) | Protocol-typed capability surfaces. This is what you use for intent implementation. |

---

## Platform service: protocols you can build against

**Note:** The final ctx.platform surface will be **capability-oriented** (parse, analyze, visualize, synthesize, generate SOP/workflow/POC/roadmap, metrics). Some items below (state, registry, storage) will be re-assigned to Runtime, Curator, or Data Steward at review. For your **provisional wrapper**, you may still wrap public_works and expose protocol-typed access to what you need; when we lock ownership, we'll document which capabilities live on ctx.platform vs other surfaces.

These are the **protocols** (or intended protocol surfaces) that may be exposed via ctx.platform or other services. Code against these contracts; implementations live in Public Works. Protocol definitions live in `symphainy_platform/foundations/public_works/protocols/` unless noted.

### State / registry / discovery (ownership TBD — likely Runtime / Curator, not ctx.platform)

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

### Compute / ingestion / events (ingestion TBD — Platform or Data Steward)

| Capability | Protocol (build against this) | Current impl | Notes |
|------------|------------------------------|---------------|-------|
| Ingestion | **IngestionProtocol** (IngestionRequest, IngestionResult) | IngestionAbstraction | `ingest` with IngestionRequest; returns IngestionResult. See `protocols/ingestion_protocol.py`. |
| Deterministic embedding storage | **DeterministicEmbeddingStorageProtocol** (to be added) | DeterministicComputeAbstraction | DuckDB for deterministic embeddings (schema fingerprints, pattern signatures). Protocol name corrected from "DeterministicCompute." |
| Event publisher | **EventPublisherProtocol** | EventPublisherAbstraction | `publish(topic, event_type, event_data, headers)`. See `protocols/event_publisher_protocol.py`. |
| Visual generation | **VisualGenerationProtocol** | VisualGenerationAbstraction | See `protocols/visual_generation_protocol.py`. |

### Semantic data / visualize (ctx.platform — capability surfaces: analyze, visualize)

| Capability | Protocol (build against this) | Current impl | Notes |
|------------|------------------------------|---------------|-------|
| Semantic data | **SemanticDataProtocol** | SemanticDataAbstraction | Store/query semantic content. See `protocols/semantic_data_protocol.py`. |

### Parsing / document (ctx.platform — capability surface)

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

## Team B guidance: provisional SDK and your questions

**Disconnect:** Platform SDK doesn't exist yet — ctx.platform is only in docs. You're told to "build with reasonable certainty"; protocols do exist in public_works/protocols/.

**Option B (provisional Platform SDK wrapper) — endorsed.**  
Build a thin PlatformSDKContext that wraps public_works into ctx.platform, type against protocols. Team A can later replace the implementation. Your capability code stays clean and forward-compatible. This matches our expectations; no correction needed before you create your implementation plan.

**Answers to your questions:**

| Question | Answer |
|----------|--------|
| **Should I build a provisional Platform SDK wrapper (Option B)?** | **Yes.** Option B is the right approach. Don't wait for Team A; build the provisional wrapper so you're unblocked and forward-compatible. |
| **How much of the four services on ctx do I implement?** | **Just ctx.platform for now.** Stub ctx.governance, ctx.reasoning, ctx.experience only if your code paths need a placeholder to call (e.g. you're wiring a path that will eventually call governance). Otherwise implement only ctx.platform. |
| **Timeline for Team A's Platform SDK?** | No firm timeline; that's why we gave a provisional handoff. Option B means you're not blocked; when we deliver the real Platform SDK, we'll align with the same protocols and you swap the implementation. |
| **Experience surfaces: Experience SDK only, or also Platform SDK?** | **Experience surfaces (UIs, dashboards) use Experience SDK only** — query_state, invoke_intent, trigger_journey, subscribe. They do **not** get direct access to Platform SDK. **Intent/capability code (backend)** gets ctx and thus ctx.platform — that's where your provisional wrapper is used. So: frontend/experience surfaces → Experience SDK only; backend intent handlers → ctx (and your provisional ctx.platform). |

**Summary:** Build the provisional ctx.platform wrapper; type against protocols; implement only ctx.platform unless you need stubs for the other three. Experience surfaces stay on Experience SDK; capability code uses ctx.platform. We'll reconcile ctx.platform's exact surface (parse, analyze, visualize, synthesize, generate SOP/workflow/POC/roadmap, metrics, etc.) at review.

---

## How to build with reasonable certainty

1. **Code against protocols, not concretes.** Import and type-hint against the protocol types (e.g. `StateManagementProtocol`, `FileStorageProtocol`, `IngestionProtocol`, `FileParsingProtocol`) from `symphainy_platform/foundations/public_works/protocols/`. The runtime will inject implementations; you don't care which abstraction backs them.
2. **Assume four services on ctx.** Your intent handler receives `ctx` with `ctx.governance`, `ctx.reasoning`, `ctx.experience`, `ctx.platform`. Use **ctx.platform** for state, storage, registry, ingestion, parsing, semantic data, deterministic compute, events, visual generation. Use **ctx.governance** / **ctx.reasoning** / **ctx.experience** only for the narrow, mediated surfaces we define.
3. **Parsing:** Use **FileParsingRequest** and **FileParsingResult** from `protocols/file_parsing_protocol.py`. Pass `file_reference` (State Surface reference) and options; get back standardized parsing result. Don't depend on format-specific abstraction classes.
4. **Gaps (TBD in Phase C):** Registry and DeterministicCompute don't have a formal Protocol in code yet. Build against the **behavior** you need (registry/lineage operations; embeddings/analytics); we'll lock the protocol surface when we complete Phase C.

---

## When we finalize

After Public Works Phases C–F (protocols, 4-layer flow, service mapping, Curator boundary), we will:

- Lock the **protocol** list and any new protocols (e.g. DeterministicEmbeddingStorageProtocol; Registry when Curator flow is decided).
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
