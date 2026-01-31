# Anti-Patterns, DI Container, and Lineage — CTO/Architect Assessment

**Purpose:** (1) Assess the role of the DI container in the new platform; (2) Evaluate whether anti-patterns should use abstractions, protocols, or capability services; (3) Evaluate how components use abstractions (e.g. lineage split); (4) Recommend next steps and probing to find hidden issues.

**Status:** Assessment. Informs refactor and probe plan.

---

## 1. What Role Should the DI Container Play?

### 1.1 What Exists Today (No Formal DI Framework)

There is **no** formal DI framework (no punq, injector, lagom, or similar). The "container" is:

| Concept | What it is | Where |
|--------|-------------|--------|
| **Composition root** | `service_factory.create_runtime_services(config)` | runtime_main, experience_main |
| **Container object** | `RuntimeServices` (dataclass) | Holds public_works, state_surface, ELM, registry_abstraction, artifact_storage, file_storage, wal, intent_registry, solution_registry, solution_services |
| **FastAPI "DI"** | `request.app.state` | Experience: security_guard_sdk, traffic_cop_sdk. Runtime: **does not** attach services to app.state (RuntimeAPI is built with services passed to create_runtime_app and held in closure). |

So:

- **Runtime:** Services are built once in service_factory, passed into create_runtime_app → RuntimeAPI holds them. No app.state.service_name; routes use the RuntimeAPI instance created at startup.
- **Experience:** experience_main builds the same graph, then attaches **only** security_guard_sdk and traffic_cop_sdk to app.state. It **does not** attach public_works, admin_dashboard_service, or guide_agent_service. Code in guide_agent and runtime_agent_websocket checks `hasattr(request.app.state, "public_works")` and admin/guide check for admin_dashboard_service / guide_agent_service — **those are never set**, so those code paths either fail at runtime or are unused. This is an **incomplete DI story** for Experience.

References: `sessions.py` ("In production, this would come from DI container") — meaning today RuntimeClient is hardcoded; the "DI container" is the conceptual place (app.state or a real container) where such dependencies would live.

### 1.2 What Role the "Container" Should Play

**Recommendation:**

1. **Keep a single composition root.** service_factory (or a bootstrap module) remains the place that builds the object graph from config. No need to introduce a third-party DI framework unless we want interface-based resolution and lifecycle (e.g. scoped request).
2. **Make the container explicit and consistent.**  
   - **Runtime:** Already consistent — RuntimeServices is the container; create_fastapi_app(services) receives it and passes slices into create_runtime_app. No app.state needed for runtime API.  
   - **Experience:** Fix the gap: either (a) pass the same RuntimeServices (or a subset) into create_app(services) and attach to app.state everything Experience needs (public_works, admin_dashboard_service, guide_agent_service, etc.), or (b) document that Experience is "minimal" and only SDKs are on app.state, and remove or guard code that expects public_works / admin_dashboard_service / guide_agent_service.
3. **Optional: ctx as the container.** When we introduce the four-service context (P3 Part A), ctx can be the single object that Experience and Runtime receive — ctx.governance, ctx.reasoning, ctx.experience, ctx.platform, and optionally ctx.runtime (substrate). Then "DI" is "inject ctx" and read capabilities from it. That makes the container a **capability bundle** rather than a bag of get_*.

**Summary:** The "DI container" should be (1) one composition root (service_factory / bootstrap), (2) one container type (RuntimeServices today; ctx later), (3) explicit attachment to app.state for Experience so that every Depends(get_X) has X set at startup. No requirement for a framework; clarity and completeness are the goals.

---

## 2. Should Anti-Patterns Use Abstractions, Protocols, or a Capability Service?

| Consumer | Current | Recommendation | Rationale |
|----------|---------|-----------------|-----------|
| **WAL** | RedisAdapter (get_redis_adapter()) | **Option A (acceptable):** Keep adapter. **Option B (cleaner):** Introduce **EventLogProtocol** (append, read_range, consumer_group) and RedisStreamsEventLog implementation. WAL and TransactionalOutbox depend on protocol. | Adapter is fine for "runtime substrate" that rarely swaps. Protocol is better if we want to test or swap (e.g. in-memory event log). Low priority. |
| **TransactionalOutbox** | RedisAdapter | Same as WAL — protocol optional. **Not wired** in service_factory today (ELM gets transactional_outbox=None). | If we wire it, pass get_redis_adapter() or a shared EventLogProtocol impl. |
| **DataBrain** | ArangoAdapter | **Do not wire** until lineage is reconciled (see §3). If we wire: use **LineageProvenanceProtocol** (track_provenance, get_provenance, get_lineage) backed by Registry (Supabase) for artifact lineage, or by a dedicated store. Prefer **one source of truth for artifact lineage** (Registry/Supabase). | DataBrain today is Arango-only and never instantiated; it duplicates the "provenance" concern that Supabase/Registry already own for client-facing lineage. |
| **structured_extraction_service** | get_supabase_adapter() → ExtractionConfigRegistry | **Option A:** Keep adapter for "governance/config tables" (extraction_configs). **Option B:** ctx.governance exposes "extraction_config_registry" as a capability (thin wrapper over Supabase table). | Governance surface can own config tables; adapter is acceptable until we have ctx.governance. |
| **guided_discovery_service** | get_supabase_adapter() | Same as above — table access for discovery config; governance or adapter. | Same. |
| **data_steward_primitives (BoundaryContractStore)** | supabase_adapter (injected) | **Governance capability.** data_boundary_contracts is a governance concern. Prefer get_boundary_contract_store() or ctx.governance.boundary_contracts (protocol over the table). | Keeps Data Steward behind a named capability; adapter behind it is an implementation detail. |

**Summary:**  
- **WAL / TransactionalOutbox:** Keep adapter for now; optional EventLogProtocol later.  
- **DataBrain:** Don’t wire; reconcile lineage first (§3).  
- **Libraries (Supabase table access):** Keep adapter near-term; move behind ctx.governance or a capability when we introduce the four-service ctx.  
- **Data steward (boundary contracts):** Treat as governance capability; protocol or get_* over the store.

---

## 3. How Are They Using Abstractions? (Lineage Split)

### 3.1 Two Notions of Lineage/Provenance

| Notion | Where it lives | Who uses it | Purpose |
|--------|----------------|-------------|---------|
| **Artifact / file lineage** | **Supabase** (Registry + file metadata). RegistryAbstraction; Supabase file adapter (get_file_lineage, get_lineage_tree). | file_parser_service (lineage_query), parse_content_service, VisualizeLineageService, artifact index, runtime_api (artifact with materializations). | Client-facing: "this file → parsed → embedded"; UI lineage views; artifact resolution. |
| **Runtime reference/provenance** | **DataBrain** (Arango: data_references, data_provenance). Not wired. | Nobody (DataBrain never instantiated). | Would be runtime-internal: "this reference was produced by this execution." |

So from a **client/file perspective, lineage lives in Supabase**. DataBrain’s use of Arango for "provenance" is a **second, runtime-internal** store. That is only appropriate if we explicitly want two stores (e.g. "artifact lineage" in Supabase for governance/UI and "execution provenance" in Arango for replay/audit). Today we have not made that design decision; DataBrain is dead code.

### 3.2 Is DataBrain’s Arango Use Wrong?

It’s **not wrong per se** if we define: (a) Supabase = artifact/file lineage (what users see), (b) Arango = runtime execution provenance (references, execution_id, operation). But then we should:

- Name and document the split (e.g. "artifact lineage" vs "execution provenance").
- Avoid duplicating the same facts in both stores.
- If we only need one, prefer **Registry (Supabase)** as the source of truth for lineage and have any "provenance" API (e.g. track_provenance) go through RegistryAbstraction or a LineageAbstraction backed by Supabase.

**Recommendation:**  
- Treat **Registry (Supabase)** as the single source of truth for **artifact lineage** (file → parsed → embedded, materializations, parent_artifacts).  
- **Do not wire DataBrain** until we decide we need a separate execution-provenance store. If we do, introduce a **LineageProvenanceProtocol** and either (1) implement it with Registry for artifact lineage and a separate impl for execution provenance, or (2) implement DataBrain as an execution-provenance backend and keep Registry for artifact lineage only. Document the split.

---

## 4. Recommended Next Steps and Probing

### 4.1 Immediate (Fix and Document)

1. **Experience DI gap:** In experience_main, after building services, attach to app.state everything Experience routes expect: e.g. `app.state.public_works = services.public_works`, and build and attach `admin_dashboard_service` and `guide_agent_service` (both take public_works and possibly state_surface) so that Depends(get_admin_dashboard_service) and Depends(get_guide_agent_service) succeed. Alternatively, remove or guard routes that depend on them until they are wired.
2. **Document the "container":** Add a short doc (or section in BOOT_PHASES or a new CONTAINER_AND_INJECTION.md) that states: composition root = service_factory; container = RuntimeServices; Experience must attach the same services it needs to app.state at startup. No formal DI framework; inject by constructor and app.state.

### 4.2 Short-Term (Anti-Patterns)

3. **WAL / TransactionalOutbox:** Leave as adapter (get_redis_adapter()). Optionally add EventLogProtocol and RedisStreamsEventLog in a later sprint; low priority.
4. **DataBrain:** Do not wire. Add a brief note in code or FOUR_SERVICE_MAPPING: "DataBrain not instantiated; lineage lives in Registry (Supabase). If execution provenance is needed, introduce LineageProvenanceProtocol and decide Supabase vs Arango."
5. **Libraries (Supabase table access):** Leave as get_supabase_adapter() until ctx.governance exists; then consider moving extraction_config and discovery config behind a governance capability.

### 4.3 Probing to Find More Hidden Issues

6. **Probe: "Who depends on app.state?"**  
   Grep for `app.state` and `request.app.state`; list every attribute read (e.g. public_works, security_guard_sdk, admin_dashboard_service, guide_agent_service, telemetry_service). For each, verify it is set in the appropriate main (runtime_main vs experience_main) or in create_app/startup. **Deliverable:** List of app.state keys and where they are set; fix any missing.

7. **Probe: "Who is never instantiated?"**  
   Search for `DataBrain(`, `TransactionalOutbox(`, and any other runtime/foundation class that takes adapters or abstractions. If never called, document as "not wired" and either wire or remove from "required" narratives. **Deliverable:** List of dead/unwired components; decision to wire or drop.

8. **Probe: "Adapter vs abstraction by layer."**  
   For each component that currently uses an adapter (WAL, TransactionalOutbox, DataBrain, structured_extraction, guided_discovery, data_steward_primitives), confirm whether it should instead use an abstraction/protocol and under which ctx slice it would fall. **Deliverable:** Table (component, current, recommended, ctx slice) and backlog items.

9. **Probe: "Lineage read/write paths."**  
   Trace all reads and writes to "lineage" or "provenance" (Supabase vs Arango). Confirm: artifact lineage = Registry/Supabase only; any Arango provenance = future/optional and documented. **Deliverable:** Lineage/provenance map (store, API, consumer) and one-line policy ("artifact lineage in Registry only").

### 4.4 Summary Table

| Item | Action |
|------|--------|
| DI container role | One composition root (service_factory); one container (RuntimeServices → ctx later); Experience must set all app.state keys it uses. |
| WAL / TransactionalOutbox | Keep adapter; optional EventLogProtocol later. Wire TransactionalOutbox only if needed. |
| DataBrain | Do not wire; reconcile lineage first; prefer Registry for artifact lineage. |
| Libraries (Supabase) | Keep adapter; move behind ctx.governance when ctx exists. |
| data_steward (boundary contracts) | Treat as governance capability; protocol or get_* when formalizing. |
| Probing | app.state audit; unwired components; adapter vs abstraction by layer; lineage read/write paths. |

---

*Assessment date: 2026-01-30. To be updated after probe runs and Experience DI fix.*
