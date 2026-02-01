# Public Works Contract — Single Source of Truth for the Foundation Boundary

**Status:** To be filled and then audited against.  
**Purpose:** One document that lists every boundary getter, its protocol type, and whether it’s required or optional. No fallbacks for required capabilities.

**Related:** [GETTING_ON_TRACK_ASSESSMENT_AND_PLAN.md](GETTING_ON_TRACK_ASSESSMENT_AND_PLAN.md), [architecture/PUBLIC_WORKS_CTA_PATTERN.md](architecture/PUBLIC_WORKS_CTA_PATTERN.md), [INTERCEPT_ALIGNMENT_CONTRACT.md](INTERCEPT_ALIGNMENT_CONTRACT.md), [architecture/PLATFORM_CONTRACT.md](architecture/PLATFORM_CONTRACT.md).

---

## 1. Scope

- **Public Works** = the foundation service that owns adapters and abstractions and exposes **only** protocol-typed getters (CTA pattern).
- **Boundary** = the set of getters that Runtime, Civic, and Platform SDK use. Nothing else is the official way to get capability from Public Works.
- **Required** = boot fails (Public Works `initialize()` raises) if the backing adapter or dependency is missing.
- **Optional** = getter may return None; callers must check and fail fast if they need it and it’s missing.

---

## 2. Required Getters (Boot Fails If Missing)

To be filled from INTERCEPT_ALIGNMENT_CONTRACT + PLATFORM_CONTRACT. For each row: getter name, protocol type, backing (adapter), and notes.

| Getter | Protocol Type | Backing | Notes |
|--------|----------------|---------|--------|
| `get_state_abstraction()` | StateManagementProtocol | Redis + Arango | Required for state, WAL-related flows. |
| `get_file_storage_abstraction()` | FileStorageProtocol | GCS + Supabase file | Required for content/artifact. |
| `get_artifact_storage_abstraction()` | ArtifactStorageProtocol | GCS + Supabase | Required for artifact plane. |
| `get_registry_abstraction()` | Registry contract | Supabase | Required for lineage, intent_executions, artifact_index. |
| `get_auth_abstraction()` | AuthenticationProtocol | Supabase | Required for Smart City auth. |
| `get_tenant_abstraction()` | TenancyProtocol | Supabase | Required for tenancy. |
| `get_wal_backend()` | EventLogProtocol | Redis | Required for WAL, Outbox. |
| `get_curator_service()` | CuratorProtocol | Supabase + ArtifactPlane | Required; Curator only valid with Supabase. |

*Above is a starter list; align with PLATFORM_CONTRACT §3 and INTERCEPT_ALIGNMENT_CONTRACT §3.1. Add/remove rows so this table is the single source of truth.*

**Rule:** For every required getter, if the backing adapter or dependency is missing, Public Works `initialize()` must **raise**. No partial init, no “return None and log.”

---

## 3. Optional Getters (May Return None; Callers Must Check)

Only list getters that are **explicitly** not required for MVP. Everything else is required.

| Getter | Protocol Type | When None |
|--------|----------------|-----------|
| (List only if truly optional) | | |

---

## 4. What Must NOT Exist

- No boundary getter that returns an **adapter** (e.g. get_supabase_adapter). Those raise or are not part of the boundary.
- No **fallback** for a required capability (no “if adapter missing return None”, no “if table missing return []”).
- No caller (GovernanceService, Runtime, Civic) that receives an adapter from Public Works. They use only boundary getters and protocol types.

---

## 5. Audit Checklist

After this contract is filled and agreed:

1. [ ] Every required getter in §2 exists in code and fails boot when its dependency is missing.
2. [ ] No boundary getter returns an adapter.
3. [ ] No fallback (return None / return [] / log and continue) for any required capability.
4. [ ] Optional getters (if any) are explicitly listed in §3; all others are required.
5. [ ] Probes: boot with full required config succeeds; boot without required config fails with clear error.
6. [ ] Document “Public Works contract satisfied as of &lt;date&gt;” and “how Public Works fails and when.”

---

## 6. Next Step

1. **Reconcile** this table with INTERCEPT_ALIGNMENT_CONTRACT §3.1 and PLATFORM_CONTRACT §3 (required infra).
2. **Audit** Public Works code against this contract (and PUBLIC_WORKS_CTA_PATTERN).
3. **Fix** all gaps in one pass.
4. **Probe** and document; then lock. Then start Curator with schema and migrations.
