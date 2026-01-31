# Public Works Protocol Registry

**Purpose:** Canonical list of Public Works protocols and their **stability policy**. Protocols are the boundary contract between callers and Public Works; changing them breaks consumers.

**Status:** Locked. Protocol method signatures (name, parameters, return shape) are **stable**. Changes require a deprecation path or a new protocol version; do not change in place.

**References:** [PLATFORM_CONTRACT.md](PLATFORM_CONTRACT.md), [PUBLIC_WORKS_STRATEGIC_FIX_PLAN.md](PUBLIC_WORKS_STRATEGIC_FIX_PLAN.md) §5 (one protocol per logical capability; swap unit).

---

## Stability rule

- **Do not** change a protocol’s method name, parameter list, or return type in a breaking way without:
  - Deprecating the old method and adding a new one, or
  - Introducing a new protocol version (e.g. `StateManagementProtocolV2`) and migrating callers.
- **Additive** changes (new optional parameters with defaults, new methods) are allowed if they do not break existing callers.
- When in doubt, add a new method or a new protocol rather than mutating an existing one.

---

## Registry (swap unit = what you swap when changing backing infra)

| Protocol | File | Swap unit | Foundation getter(s) |
|----------|------|-----------|----------------------|
| StateManagementProtocol | `state_protocol.py` | State backend (Redis/Arango) | get_state_abstraction() |
| FileStorageProtocol | `file_storage_protocol.py` | Blob storage (GCS/S3/FS) | get_file_storage_abstraction() |
| FileManagementProtocol | `file_management_protocol.py` | File metadata + ops | (internal) |
| ArtifactStorageProtocol | `artifact_storage_protocol.py` | Artifact storage | get_artifact_storage_abstraction() |
| ServiceDiscoveryProtocol | `service_discovery_protocol.py` | Service discovery (Consul) | get_service_discovery_abstraction() |
| AuthenticationProtocol | `auth_protocol.py` | Auth (Supabase) | get_auth_abstraction() |
| TenancyProtocol | `auth_protocol.py` | Tenancy (Supabase/Redis) | get_tenant_abstraction() |
| SemanticSearchProtocol | `semantic_search_protocol.py` | Search index (Meilisearch) | get_semantic_search_abstraction() |
| IngestionProtocol | `ingestion_protocol.py` | Ingest (upload/EDI/API) | get_ingestion_abstraction() |
| VisualGenerationProtocol | `visual_generation_protocol.py` | Visual generation | get_visual_generation_abstraction() |
| EventPublisherProtocol | `event_publisher_protocol.py` | Event publish (Redis Streams) | get_event_publisher_abstraction() |
| EventLogProtocol | `event_log_protocol.py` | Append-only log (WAL) | get_wal_backend() |
| FileParsingProtocol | `file_parsing_protocol.py` | Document parsing | get_document_parsing() |
| DeterministicEmbeddingStorageProtocol | `deterministic_embedding_storage_protocol.py` | Deterministic embeddings (DuckDB) | get_deterministic_compute_abstraction() |
| **SemanticDataProtocol** | `semantic_data_protocol.py` | **Mega** (prefer narrow below) | get_semantic_data_abstraction() |
| VectorStoreProtocol | `vector_store_protocol.py` | Vector/embedding backend (Arango→Pinecone) | get_vector_store() |
| SemanticGraphProtocol | `semantic_graph_protocol.py` | Graph backend | get_semantic_graph() |
| CorrelationMapProtocol | `correlation_map_protocol.py` | Correlation store | get_correlation_map() |
| **KnowledgeDiscoveryProtocol** | `knowledge_discovery_protocol.py` | **Mega** (prefer narrow below) | get_knowledge_discovery_abstraction() |
| FullTextSearchProtocol | `full_text_search_protocol.py` | Search engine (Meilisearch→OpenSearch) | get_full_text_search() |
| GraphQueryProtocol | `graph_query_protocol.py` | Graph backend (Arango→Neo4j) | get_graph_query() |
| BoundaryContractStoreProtocol | `boundary_contract_store_protocol.py` | Boundary contracts (Supabase) | get_boundary_contract_store() |
| LineageProvenanceProtocol | `lineage_provenance_protocol.py` | Lineage/provenance (Arango/Supabase) | get_lineage_backend() |
| ExtractionConfigRegistryProtocol | `extraction_config_registry_protocol.py` | Extraction config (Supabase) | get_extraction_config_registry() |
| GuideRegistryProtocol | `guide_registry_protocol.py` | Guide registry (Supabase) | get_guide_registry() |
| ContentMetadataProtocol | `content_metadata_protocol.py` | Content metadata (when wired) | — |
| KnowledgeGovernanceProtocol | `knowledge_governance_protocol.py` | Knowledge governance (when wired) | — |
| AuthorizationProtocol | `auth_protocol.py` | Authorization (when wired) | — |
| VectorBackendProtocol | `vector_backend_protocol.py` | Internal vector backend (SemanticData) | (internal) |
| ParsingServiceProtocol(s) | `parsing_service_protocol.py` | Structured/Unstructured/Hybrid/WorkflowSOP | (library) |

---

## Summary

- **Locked:** Method signatures are stable; no breaking changes without deprecation or new version.
- **Swap unit:** Each protocol corresponds to one logical capability; swap the implementation when changing backing infra.
- **Narrow over mega:** Prefer get_vector_store(), get_full_text_search(), get_graph_query() over get_semantic_data_abstraction() / get_knowledge_discovery_abstraction() when only one capability is needed.
