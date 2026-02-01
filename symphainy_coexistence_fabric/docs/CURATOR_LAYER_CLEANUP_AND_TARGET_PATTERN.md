# Curator Layer Cleanup and Target Pattern

**Status:** Plan (January 2026)  
**Purpose:** Define cleanup for the Curator layer and the target infra stack and adapter→abstraction→protocol pattern so Curator has staying power for sovereignty-aware intelligence governance.

**Related:** [CURATOR_SOVEREIGNTY_VISION_AND_INFRASTRUCTURE.md](CURATOR_SOVEREIGNTY_VISION_AND_INFRASTRUCTURE.md), [CURATOR_INFRASTRUCTURE_ALIGNMENT.md](CURATOR_INFRASTRUCTURE_ALIGNMENT.md), [SOVEREIGNTY_ARCHITECTURE.md](architecture/SOVEREIGNTY_ARCHITECTURE.md).

---

## 1. Build in Layers — This Layer

We build and clean up **in layers**. This doc defines **this layer**: Curator (intelligence governance + registry surface). Cleanup here does not yet implement full sovereignty enforcement; it establishes the **right shape** (infra, adapter→abstraction→protocol) so that adding sovereignty_domain, learning_permission, and enforcement in the next layer is straightforward.

---

## 2. Curator Layer Cleanup (Concrete)

### 2.1 Fix Broken Callers

| Issue | Fix |
|-------|-----|
| **list_artifacts_service** calls `registry.list_files()` on RegistryAbstraction | RegistryAbstraction has no list_files. Use **file_storage** or **file_management** (get_file_storage_abstraction() / get_document_parsing or file_management) for listing files. Prefer get_file_storage_abstraction().list_files(...) or equivalent. Change list_artifacts_service (and any similar caller) to use Public Works file_storage/file_management getter, not registry_abstraction. |
| **semantic_profile_registry** calls registry_abstraction.get_registry_entry, register_entry, list_registry_entries | RegistryAbstraction does not implement these. Either (a) add a minimal implementation to RegistryAbstraction (table + schema for semantic_profile entries), or (b) point semantic_profile_registry at a dedicated abstraction that does (e.g. a “registry entries” table). Prefer (a) with a single generic registry_entries table keyed by (entry_type, entry_key, tenant_id) if we want one pattern. |

### 2.2 Unify Curator Surface

| Current state | Target |
|---------------|--------|
| CuratorSDK (Smart City) = stubs for register_capability/discover_agents/get_domain_registry; promote_to_platform_dna uses CuratorService (Supabase). | **One** Curator implementation that backs ctx.governance.registry: capability/agent/domain either persisted (Supabase) or backed by CuratorFoundationService (in-memory) so that register_capability and discover_agents have a real backing. |
| CuratorFoundationService (foundations/curator) = CapabilityRegistry, AgentRegistry (in-memory), ServiceRegistry (Consul). Not wired to CuratorSDK. | **Wire** CuratorSDK to CuratorFoundationService for register_capability/discover_agents/get_domain_registry (in-memory backing for demo), OR introduce Supabase tables for capabilities/agents/domains and have CuratorSDK use RegistryAbstraction or a Curator backend that uses Supabase. For staying power, prefer **Supabase-backed** capability/agent/domain registries so data survives restarts and is queryable. |
| Two “Curator” worlds (Smart City CuratorSDK + foundation CuratorFoundationService). | **Single** Curator abstraction that implements the full contract (registry + classification + approval). CuratorService (Smart City) can become the implementation that uses Supabase + policy store; CuratorSDK is the thin wrapper that exposes the protocol to ctx.governance.registry. |

### 2.3 RegistryAbstraction Role

- **Keep** RegistryAbstraction for: artifact_index, intent_executions, generic RLS (insert_record, query_records, update_record, delete_record). Used by runtime, export, and Curator (e.g. promotion targets).
- **Do not** overload it with list_files (that belongs to file_storage/file_management). **Either** add get_registry_entry/register_entry/list_registry_entries with a clear table/schema (e.g. registry_entries(entry_type, entry_key, tenant_id, data, version)) **or** introduce a small “semantic profile store” abstraction used only by semantic_profile_registry.
- **Sovereignty:** In the next layer, artifact_index (and any artifact store) gets sovereignty_domain and learning_permission; RegistryAbstraction stays the storage layer, with sovereignty applied by Curator at write/read boundaries.

### 2.4 Deprecate or Clarify “Runtime never calls Curator”

- Old constraint: “Runtime never calls Curator SDK methods; Runtime only consumes snapshotted registry state.”
- **New model:** Curator is the **intelligence governance authority**. Runtime, Traffic Cop, Post Office, and agents **do** call Curator for: classify_artifact, approve_promotion, approve_cross_domain, approve_message_routing. So “Runtime never calls Curator” is **deprecated** for the sovereignty model. Update comments and docs: Runtime (and agents) call Curator for classification and approval; they do not bypass Curator for cross-domain or learning decisions.

---

## 3. Target Infra Stack (Curator Layer)

| Component | Role |
|-----------|------|
| **Supabase** | Primary store for Curator: solution_registry, intent_registry, realm_registry (promotion); optional curator_policies, promotion_rules; optional capability_registry, agent_registry, domain_registry tables (if we move from in-memory to persisted). artifact_index, intent_executions remain (RegistryAbstraction). Add sovereignty_domain, learning_permission columns in next layer. |
| **Consul** | Unchanged. Service discovery only (ServiceRegistry). Not used for intelligence/capability/agent registry. |
| **Redis/Arango** | Unchanged for WAL/state. Optional: compliance_events via WAL or Supabase in next layer. |

No new infra types. Curator layer uses existing Supabase + optional new tables/columns.

---

## 4. Adapter → Abstraction → Protocol (Target Pattern)

### 4.1 Adapter (Layer 0)

- **SupabaseAdapter** — Only adapter Curator persistence needs. Used inside Public Works or inside a Curator backend to read/write: solution_registry, intent_registry, realm_registry; optional curator_policies, promotion_rules; optional capability_registry, agent_registry, domain_registry.
- **ConsulAdapter** — Used only by ServiceRegistry (service discovery). Not part of Curator intelligence governance.

**Rule:** No new adapter types. Curator backend(s) use SupabaseAdapter; they do not expose the adapter to callers.

### 4.2 Abstraction (Layer 1)

- **Curator abstraction** — Single abstraction that:
  - **Registry surface:** register_capability, discover_agents, get_domain_registry, promote_to_platform_dna. Backed by Supabase tables (or in-memory for MVP) so that capability/agent/domain are durable and queryable.
  - **Sovereignty surface (for next layer):** classify_artifact(artifact) → { sovereignty_domain, learning_permission }; approve_promotion(artifact, target_domain) → bool; approve_cross_domain(source, target, operation) → bool; approve_message_routing(message) → bool. First version can be no-op or “allow all.”
- Implemented by: **CuratorService** (Smart City) extended to use Supabase for capability/agent/domain + promotion, and to implement classification/approval methods (with a small policy store or in-memory rules). **CuratorFoundationService** can be merged into this or remain the in-memory backing that CuratorService delegates to until we add Supabase tables for capability/agent/domain.

**Rule:** Callers (GovernanceService, Runtime, Traffic Cop, Post Office, agents) depend only on the abstraction (or protocol). They never touch SupabaseAdapter.

### 4.3 Protocol (Boundary)

- **CuratorProtocol** — Formal protocol (e.g. in Public Works or Civic) that the Platform Boundary exposes. Methods:
  - register_capability(capability_definition, tenant_id) → CapabilityRegistration
  - discover_agents(agent_type, tenant_id) → AgentDiscovery
  - get_domain_registry(domain_name, tenant_id) → DomainRegistryResult
  - promote_to_platform_dna(...) → Optional[str]
  - classify_artifact(artifact) → SovereigntyClassification  (next layer)
  - approve_promotion(artifact, target_domain) → bool  (next layer)
  - approve_cross_domain(source, target, operation) → bool  (next layer)
  - approve_message_routing(message) → bool  (next layer)

- **CuratorSDK** (or a single class implementing CuratorProtocol) is what ctx.governance.registry gets. It is the thin wrapper that implements CuratorProtocol and delegates to the Curator abstraction (CuratorService + backing store).

**Rule:** Team B and Runtime code type against CuratorProtocol only. Implementation lives in Team A (Civic/Public Works).

---

## 5. Data Brain: Wire Now or YAGNI?

### 5.1 What Data Brain Is

- **DataBrain** (runtime/data_brain.py): Runtime-native data cognition — **references** (DataReference) and **provenance** (ProvenanceEntry). Stores references, not raw data; enables “data mash without ingestion,” explainable interpretation, replayable migration.
- Depends on **LineageProvenanceProtocol** (get_lineage_backend() from Public Works). Backend is Arango-backed (arango_lineage_backend) for execution provenance.
- **Current state:** DataBrain is **not wired** into the runtime graph. It is not constructed in service_factory or bootstrap; no StateSurface, ArtifactRegistry, or execution path uses it. Lineage backend exists (get_lineage_backend()); DataBrain is exported from runtime but never instantiated or passed anywhere.

### 5.2 Recommendation: **Defer (YAGNI)**

- **Curator layer** and **sovereignty** need: artifact/store sovereignty_domain and learning_permission; lineage for **classification and promotion** (where did this artifact come from, promotion path). That lineage can live in **artifact metadata** or **RegistryAbstraction** (e.g. artifact_index lineage columns or a small lineage table in Supabase). We do **not** need DataBrain for that.
- **DataBrain** is for **execution-level** provenance: data references and provenance chains across executions (references, derived_from, operation). That is valuable for “explainable interpretation” and “replayable migration” but is **not** required for the current demo or for Curator-layer cleanup.
- **Wiring DataBrain** would require: (1) service_factory or bootstrap to create DataBrain(lineage_backend=public_works.get_lineage_backend()), (2) StateSurface or artifact registration to call DataBrain.register_reference / track_provenance when artifacts are created or updated. That is a non-trivial integration and would add a second lineage system (DataBrain/Arango) alongside artifact lineage (Supabase). Until we have a concrete need (e.g. “we need execution provenance for compliance” or “we need reference-based data mash”), we should not wire it.

**Conclusion:** **YAGNI.** Continue to defer DataBrain. Focus on Curator layer cleanup and target pattern; add sovereignty schema and Curator classification/approval in the next layer. When we need execution-level provenance (references + provenance chain), we can wire DataBrain and document the integration path (e.g. StateSurface or ArtifactRegistry calling DataBrain on register/update).

---

## 6. Implementation Order (This Layer)

1. **Fix list_artifacts:** ✅ Done. Point list_artifacts_service (and callers) at file_storage; remove use of registry_abstraction for list_files.
2. **Fix semantic_profile_registry:** ✅ Done. Added get_registry_entry/register_entry/list_registry_entries to RegistryAbstraction. Table: **registry_entries** (entry_type, entry_key, tenant_id, data jsonb, version, created_at). If the table does not exist, methods fail gracefully (return None/False/[]). Schema for deploy: create table registry_entries (id uuid primary key default gen_random_uuid(), entry_type text not null, entry_key text not null, tenant_id text, data jsonb, version text, created_at timestamptz default now()); create index on registry_entries(entry_type, entry_key, tenant_id);
3. **Define CuratorProtocol:** ✅ Done. foundations/public_works/protocols/curator_protocol.py with register_capability, discover_agents, get_domain_registry, promote_to_platform_dna; stubs for classify_artifact, approve_promotion, approve_cross_domain, approve_message_routing.
4. **Unify Curator backing:** ✅ Done. CuratorSDK accepts curator_foundation (CuratorFoundationService) and curator_service (CuratorService). GovernanceService creates CuratorFoundationService(public_works) and passes it to CuratorSDK; register_capability/discover_agents/get_domain_registry delegate to foundation (in-memory); promote_to_platform_dna delegates to curator_service when wired.
5. **Document:** Update CURATOR_INFRASTRUCTURE_ALIGNMENT and CURATOR_SOVEREIGNTY_VISION_AND_INFRASTRUCTURE to reference this target pattern; deprecate “Runtime never calls Curator” where it conflicts with sovereignty model.

---

## 7. Summary

| Item | Decision |
|------|----------|
| **Build in layers** | Yes. This layer = Curator cleanup + target infra and adapter→abstraction→protocol. |
| **Target infra** | Supabase (existing + optional new tables); Consul unchanged (service discovery only). |
| **Adapter** | SupabaseAdapter only for Curator persistence; no new adapter type. |
| **Abstraction** | Single Curator abstraction: registry surface + sovereignty surface (classification/approval); implemented by CuratorService + backing store. |
| **Protocol** | CuratorProtocol: register_capability, discover_agents, get_domain_registry, promote_to_platform_dna, classify_artifact, approve_promotion, approve_cross_domain, approve_message_routing. ctx.governance.registry = implementation of CuratorProtocol. |
| **Data Brain** | **Defer (YAGNI).** Not required for demo or Curator layer. Wire when we need execution-level provenance. |

This gives Curator the staying power we need for sovereignty-aware intelligence governance while keeping the demo working and avoiding unnecessary complexity.
