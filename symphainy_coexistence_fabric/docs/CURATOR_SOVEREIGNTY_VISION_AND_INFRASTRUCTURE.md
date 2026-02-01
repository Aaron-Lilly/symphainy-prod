# Curator Sovereignty Vision — Confirmation, Infrastructure, and Path to Implementation

**Status:** Proposal (January 2026)  
**Purpose:** Confirm the sovereignty vision we are implementing towards; propose backend infrastructure; clarify artifact/service registry; and outline a path that keeps the demo working.

**Related:** [SOVEREIGNTY_ARCHITECTURE.md](architecture/SOVEREIGNTY_ARCHITECTURE.md), [CURATOR_INFRASTRUCTURE_ALIGNMENT.md](CURATOR_INFRASTRUCTURE_ALIGNMENT.md).

---

## 1. Vision Confirmation

**Yes — this is the vision we are implementing towards.**

It is already formalized in [SOVEREIGNTY_ARCHITECTURE.md](architecture/SOVEREIGNTY_ARCHITECTURE.md):

- **Three Sovereignty Domains:** Tenant Sovereign (client-owned), Platform Sovereign (platform-owned), Compliance Sovereign (joint stewardship).
- **Curator:** The platform’s **intelligence governance authority** — governs boundaries, flow, classification, and lifecycle of intelligence across domains. Not “just a registry.”
- **Smart City mapping:** Data Steward → tenant domain; Librarian → classification & lineage; Curator → intelligence governance; Post Office → sovereign messaging; Traffic Cop → runtime enforcement; Security Guard → identity & access.
- **Intelligence classification:** sovereignty_domain, learning_permission (none | anonymized | aggregated | reusable), retention_policy, lineage.
- **Promotion pipeline:** Tenant → Curator classification → anonymization → Platform IP (promote_to_platform_dna is the start of this).
- **Agent learning:** Agent → Curator → classification → persistence (no direct agent persistence).
- **One-liner:** *Curator governs what the platform is allowed to know, learn, remember, and reuse — across tenant, platform, and compliance sovereignty domains.*

**Gap:** Today there is **no sovereignty_domain or learning_permission in code**, no Curator classification gate, no Traffic Cop/Post Office sovereignty checks, and no agent→Curator→persistence path. We have building blocks (CuratorService promote, Smart City roles, registries) but not the full sovereignty model.

---

## 2. Backend Infrastructure Patterns (Proposal)

### 2.1 Sovereignty Schema (Data Model)

- **Artifact (and file) model extension:** Every artifact/file record that can cross boundaries or be learned from should carry:
  - `sovereignty_domain`: `tenant` | `platform` | `compliance`
  - `learning_permission`: `none` | `anonymized` | `aggregated` | `reusable`
  - `retention_policy`: optional policy id
  - `lineage`: optional { source_domain, promotion_path, created_by, created_at }
- **Where it lives:** In the same stores that already hold artifacts/files (e.g. artifact_index, project_files, solution_registry, intent_registry, realm_registry). Add columns or a companion “sovereignty_metadata” table keyed by artifact_id. Prefer columns for simplicity and queryability.

### 2.2 Infra We Need

| Need | Today | Target |
|------|--------|--------|
| **Artifact/store persistence** | Supabase (artifact_index, intent_executions, project_files, etc.) | Same; add sovereignty columns (or sovereignty_metadata). |
| **Curator “registry” (classification, promotion rules, policies)** | CuratorService writes to solution/intent/realm_registry; CuratorSDK stubs | Curator-backed registry: classification rules, promotion policies, approval hooks. Can live in Supabase (e.g. curator_policies, promotion_rules) or in-memory with optional persistence. |
| **Compliance / audit** | Ad-hoc | Immutable audit log for cross-domain operations and Curator decisions. Supabase table or append-only store (e.g. WAL or dedicated compliance_events). |
| **Service discovery** | Consul (ServiceRegistry) | Unchanged. Consul remains for *service* instances (runtime); it is not the place for *intelligence* (tenant/platform/compliance). |

No new major infra: Supabase + optional compliance store; Consul unchanged.

### 2.3 Adapters

| Adapter | Role |
|---------|------|
| **SupabaseAdapter** | Already used. Extend usage for sovereignty columns and any new Curator/compliance tables. |
| **ConsulAdapter** | Unchanged. Service discovery only. |
| **Redis/Arango** | Unchanged for WAL/state. Compliance could use WAL or Supabase. |

No new adapter types; extend Supabase usage and possibly WAL for compliance.

### 2.4 Abstractions

| Abstraction | Role |
|-------------|------|
| **RegistryAbstraction** | Today: artifact_index, intent_executions, generic RLS. Extend: queries/updates that respect sovereignty_domain and learning_permission; or keep generic and push sovereignty into “Curator layer” above it. |
| **Curator “intelligence governance” abstraction** | **New.** Curator as authority: classify(artifact) → domain + learning_permission; approve_promotion(artifact, target_domain); approve_cross_domain(source, target, operation); approve_message_routing(message). Implemented by CuratorService + policy store. |
| **Compliance / audit abstraction** | **New (optional for MVP).** record_cross_domain_event(operation, source, target, actor, payload). Implemented by WAL or Supabase compliance_events. |

Curator becomes a proper abstraction (protocol) that the rest of the platform calls for classification and approval, not just “registry CRUD.”

### 2.5 Protocols

| Protocol | Role |
|----------|------|
| **SovereigntyClassificationProtocol** (or part of CuratorProtocol) | classify(artifact) → { sovereignty_domain, learning_permission }; approve_promotion(artifact, target_domain) → bool; approve_cross_domain(source, target, operation) → bool. |
| **CuratorProtocol** (expand current CuratorSDK surface) | register_capability, discover_agents, get_domain_registry, promote_to_platform_dna (existing); **add:** classify_artifact, approve_promotion, approve_cross_domain, approve_message_routing (sovereignty). |
| **Existing protocols** | StateSurface, ArtifactRegistry, FileStorage, etc. Stay; artifacts they return can carry sovereignty metadata once schema is extended. |

---

## 3. Artifact / File Management and Service Registry in This World

### 3.1 Artifact and File Management

- **StateSurface / ArtifactRegistry:** Remain the **runtime** owners of “where is this artifact/file and how do I read/write it.” They do not decide sovereignty; they **store and return** sovereignty metadata when present.
- **Sovereignty:** Applied at **write** and **read** boundaries:
  - **Write:** When an artifact is registered or a file is stored, the caller (or a Curator-backed policy) sets sovereignty_domain and learning_permission. Defaults: tenant-originated content → tenant; platform-originated (e.g. prompts, agent configs) → platform; audit events → compliance.
  - **Read / use:** Traffic Cop / Post Office (or a single “sovereignty gate”) call Curator.approve_cross_domain or approve_message_routing before allowing data to cross domains. Artifact and file management still do the actual I/O; the gate only allows or denies.
- **Librarian:** Can sit on top of RegistryAbstraction + Curator: classification, lineage, “who owns what.” Lineage can be stored in artifact lineage field or a separate lineage table.

So: **artifact/file management stay;** they get **sovereignty-aware metadata** and are **used behind sovereignty gates**, not replaced.

### 3.2 Service Registry (Consul)

- **Role unchanged:** Service registry (Consul) continues to answer “where is service X, what’s its health, how do I call it.” It is about **runtime topology**, not **intelligence ownership**.
- **Sovereignty:** Services themselves are **platform runtime**. Calls *between* services can carry tenant/platform/compliance *data*; those data flows are what Post Office / Traffic Cop govern. So:
  - **Consul:** Still the right place for service discovery.
  - **Curator:** Governs *data* and *intelligence* crossing domains, not “which process runs where.”

So: **service registry stays as-is;** sovereignty applies to **data and intelligence**, not to service registration.

---

## 4. Phased Plan: Vision in Focus, Demo Still Works

### Phase 1 — Schema and contract (no behavior change)

- Add **sovereignty_domain** and **learning_permission** to artifact/file models and Supabase schema (artifact_index, and any tables used for “promotable” content). Default existing rows to `tenant` or `platform` as appropriate.
- Define **CuratorProtocol** (or extend Curator SDK contract) with: classify_artifact, approve_promotion, approve_cross_domain, approve_message_routing.
- Document in SOVEREIGNTY_ARCHITECTURE that Step 1 is “schema + contract”; implementation of enforcement is Phase 2–3.

**Demo:** No change. New columns can default; new methods can be no-op or “allow all” for now.

### Phase 2 — Curator as classification and promotion gate

- Implement **CuratorService** (or CuratorFoundationService) to:
  - **classify_artifact:** Return sovereignty_domain and learning_permission (from artifact metadata or policy).
  - **approve_promotion:** Check learning_permission and policy; return yes/no. Wire **promote_to_platform_dna** to call this before writing to solution/intent/realm_registry.
- Persist promotion decisions (and optionally lineage) in artifact or in a small “promotion_log” table.

**Demo:** promote_to_platform_dna becomes sovereignty-aware; existing flows still work with “allow” policies.

### Phase 3 — Enforcement hooks (log-only or soft enforcement)

- Add **Traffic Cop** and **Post Office** hooks: before cross-domain read or message route, call Curator.approve_cross_domain / approve_message_routing. First version: **log and allow** (or allow if no Curator configured). Later: **deny** when policy says no.
- Optionally: **Compliance** record for each cross-domain decision (log to WAL or compliance_events).

**Demo:** No hard blocks; optional logging. Demo keeps working; we gain observability and a place to turn on strict enforcement later.

### Phase 4 — Agent learning through Curator

- Introduce path: **agent learning event → Curator.classify_artifact (or classify_learning) → Curator decides tenant_only vs platform vs compliance → persistence**. Existing direct persistence remains for backward compatibility; new agent flows use the Curator path.
- Document “agents must not persist learnings directly” as the target; achieve it incrementally.

**Demo:** Existing agents unchanged; new or refactored agents use Curator path where needed.

### Phase 5 — Strict enforcement and productization

- Turn Traffic Cop / Post Office to **deny** when policy says no. Add compliance reporting and retention. Harden promotion pipeline and productized intelligence.

---

## 5. Summary

| Question | Answer |
|----------|--------|
| **Is this the vision we’re implementing towards?** | Yes. It is in SOVEREIGNTY_ARCHITECTURE.md; we have not yet implemented it in code. |
| **Backend infra?** | Same Supabase + Consul; add sovereignty columns and optional compliance store; Curator protocol with classification and approval methods. |
| **Adapters?** | No new kinds; extend Supabase (and optionally WAL) for sovereignty and compliance. |
| **Abstractions?** | Curator as intelligence governance abstraction; optional compliance/audit abstraction. |
| **Protocols?** | Extend Curator surface with classify_artifact, approve_promotion, approve_cross_domain, approve_message_routing. |
| **Artifact/file management?** | Unchanged ownership (StateSurface, ArtifactRegistry, file storage); add sovereignty metadata; use behind sovereignty gates. |
| **Service registry?** | Unchanged; Consul for service discovery; sovereignty governs data/intelligence, not service registration. |
| **Path without losing demo?** | Phase 1: schema + contract. Phase 2: Curator classification + promotion gate. Phase 3: enforcement hooks (log-only). Phase 4: agent→Curator path. Phase 5: strict enforcement. |

This brings the sovereignty vision into focus and aligns Curator, Smart City roles, tenancy, compliance, product IP, and platform evolution into one coherent system, while keeping the working demo intact at each step.
