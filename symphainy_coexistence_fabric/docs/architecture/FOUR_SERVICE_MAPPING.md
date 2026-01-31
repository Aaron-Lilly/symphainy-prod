# Four-Service Pattern Mapping (and Runtime Substrate)

**Purpose:** Map Public Works capabilities to the four-service context (ctx.governance, ctx.reasoning, ctx.experience, ctx.platform) and document where **runtime and other callers still use adapters** so we can decide if we need more than four surfaces.

**Status:** Proposal. P3 Part A (introduce ctx) is deferred to Curator/Phase F; this doc informs that implementation.

---

## 1. The Four Services (ctx)

| Service | Ownership (vision) | Capabilities (get_* today) | Notes |
|--------|---------------------|----------------------------|--------|
| **ctx.governance** | Data Steward / policy | Auth, tenant, data boundary; registry (lineage metadata). | get_auth_abstraction(), get_tenant_abstraction(), get_registry_abstraction(). Data steward primitives use Supabase (get_supabase_adapter()) for data_boundary_contracts — could stay as adapter or move behind a Governance surface. |
| **ctx.reasoning** | Semantic / analytical | Semantic data, knowledge discovery, deterministic embeddings, semantic search. | get_semantic_data_abstraction(), get_semantic_search_abstraction(), get_deterministic_compute_abstraction(); KnowledgeDiscoveryAbstraction (no get_* today; used via semantic_data / search). |
| **ctx.experience** | Experience / UX | Control room, traffic cop, security guard; admin dashboard. | Experience SDK and Control Room consume genesis status (P1 done), auth, tenant, state. No single get_experience_* today; experience_main builds TrafficCopSDK/SecurityGuardSDK from get_auth_abstraction(), get_tenant_abstraction(), get_state_abstraction(). |
| **ctx.platform** | Platform capabilities | Parse, visualize, ingest; future: analyze, synthesize, generate SOP/workflow/POC/roadmap, metrics. | get_document_parsing() (P4), get_visual_generation_abstraction(), get_ingestion_abstraction(); get_file_storage_abstraction(), get_artifact_storage_abstraction() are **runtime substrate** (see §2). |

**Boundary note:** ctx.platform in the vision is “capability-oriented only” (parse, analyze, visualize, etc.). Raw storage/state/registry are **runtime substrate** or Governance/Curator; they are needed to run the runtime but are not “platform capabilities” in the same sense. So we keep them as separate injectables (get_state_abstraction(), get_file_storage_abstraction(), get_registry_abstraction(), get_artifact_storage_abstraction()) unless we introduce an explicit **ctx.runtime** (see §2).

---

## 2. Runtime Substrate (do we need a 5th surface?)

**What runtime needs to run:** StateSurface, WAL, ArtifactRegistry, ExecutionLifecycleManager, IntentRegistry, registry_abstraction, artifact_storage, file_storage. Today service_factory builds these from:

- get_state_abstraction(), get_file_storage_abstraction() → StateSurface
- get_redis_adapter() → WAL
- get_registry_abstraction(), get_artifact_storage_abstraction(), get_file_storage_abstraction() → RuntimeServices

**Adapter usage outside abstractions:**

| Consumer | Uses | Type | Note |
|----------|------|------|------|
| **WAL** | RedisAdapter | Adapter | service_factory passes get_redis_adapter(). WAL needs streams (xadd, xrange, xgroup_create); no WAL abstraction today. |
| **TransactionalOutbox** | RedisAdapter | Adapter | Same pattern; runtime component that needs Redis streams. |
| **DataBrain** | ArangoAdapter | Adapter | Lineage/provenance; takes ArangoAdapter. Not created in service_factory in current trace; if used, would need get_arango_adapter() or a LineageAbstraction. |
| **StateSurface / ArtifactRegistry** | StateManagementProtocol, FileStorageProtocol | Abstraction | Already protocol-typed; no adapter leak. |
| **Libraries (structured_extraction_service, guided_discovery_service)** | get_supabase_adapter() | Adapter | Table access (e.g. custom tables); could stay as adapter or move behind Governance. |
| **data_steward_primitives** | supabase_adapter (injected) | Adapter | Data boundary contracts table; Governance concern. |

**Conclusion:**

- **Four services are enough for capability grouping** (governance, reasoning, experience, platform). Runtime does not need a 5th “service” for capabilities; it needs **injectables** for state, WAL, registry, artifact, file_storage.
- **Runtime substrate options:**  
  - **A)** Keep current pattern: service_factory gets get_state_abstraction(), get_file_storage_abstraction(), get_redis_adapter(), get_registry_abstraction(), get_artifact_storage_abstraction() and passes them into StateSurface, WAL, ELM, RuntimeServices. No ctx.runtime.  
  - **B)** Introduce **ctx.runtime** (or a RuntimeSubstrate): one object that holds state_surface, wal, registry_abstraction, artifact_storage, file_storage (and optionally transactional_outbox, data_brain). service_factory builds it from get_* and attaches to ctx. Then runtime code takes ctx.runtime instead of separate args.  
- **Adapter usage:** WAL and TransactionalOutbox (and DataBrain if wired) **use adapters directly** (Redis, Arango). That is acceptable as long as they are created by service_factory via get_redis_adapter() / get_arango_adapter() (no direct public_works.redis_adapter). If we want to hide adapters entirely, we could introduce a thin WALProtocol / LineageProtocol and implementations that wrap the adapter; not required for the four-service pattern.

**Recommendation:** Implement the four services (ctx.governance, ctx.reasoning, ctx.experience, ctx.platform) first. Keep runtime substrate as today (get_* passed into StateSurface, WAL, ELM, RuntimeServices). Optionally add ctx.runtime later as a single bundle for clarity. Do not add more than four **capability** services; adapter-backed runtime components (WAL, Outbox, DataBrain) stay as injectables.

---

## 3. Suggested get_* → ctx Mapping (when we implement ctx)

| ctx slice | get_* / capability | Protocol / type |
|-----------|---------------------|------------------|
| ctx.governance | auth | get_auth_abstraction() → AuthenticationProtocol |
| ctx.governance | tenant | get_tenant_abstraction() → TenancyProtocol |
| ctx.governance | registry | get_registry_abstraction() (Registry deferred to Curator) |
| ctx.reasoning | semantic_data | get_semantic_data_abstraction() → SemanticDataProtocol |
| ctx.reasoning | semantic_search | get_semantic_search_abstraction() → SemanticSearchProtocol |
| ctx.reasoning | deterministic_embeddings | get_deterministic_compute_abstraction() → DeterministicEmbeddingStorageProtocol |
| ctx.experience | (no single getter) | Built from auth, tenant, state; Control Room uses get_pre_boot_status() |
| ctx.platform | document_parsing | get_document_parsing() → FileParsingProtocol |
| ctx.platform | visual_generation | get_visual_generation_abstraction() → VisualGenerationProtocol |
| ctx.platform | ingestion | get_ingestion_abstraction() → IngestionProtocol |
| (runtime substrate) | state | get_state_abstraction() → StateManagementProtocol |
| (runtime substrate) | file_storage | get_file_storage_abstraction() → FileStorageProtocol |
| (runtime substrate) | artifact_storage | get_artifact_storage_abstraction() → ArtifactStorageProtocol |
| (runtime substrate) | registry | get_registry_abstraction() |
| (runtime substrate) | wal / redis | get_redis_adapter() (adapter; no protocol today) |

---

## 4. Summary

- **Four services:** governance, reasoning, experience, platform. Map get_* as in §3; implement ctx when doing P3 Part A (after Curator/Phase F).
- **Runtime substrate:** state, file_storage, artifact_storage, registry, redis (WAL). Keep as get_* injectables unless we add ctx.runtime as a bundle.
- **Adapter usage:** WAL, TransactionalOutbox, DataBrain use adapters (Redis, Arango); acceptable if obtained via get_redis_adapter() / get_arango_adapter(). No need for more than four **capability** services; runtime does not require a 5th “service” for capabilities, only clear injectables for execution infrastructure.

**See also:** [ANTI_PATTERNS_AND_DI_ASSESSMENT.md](ANTI_PATTERNS_AND_DI_ASSESSMENT.md) — DI container role, anti-patterns (abstractions vs protocols vs capability service), lineage split (Supabase vs Arango), and recommended probes.
