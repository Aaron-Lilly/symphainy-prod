# Curator Layer: What’s Real, What’s Stub, What’s Fallback

**Purpose:** Clarify what is a real working implementation vs a stub or fallback so we can make the system actually work.

---

## 0. Platform policy: Curator is required and Supabase-only

- **Curator is required for the platform to run.** The platform does not start without Curator. If Curator cannot be built (e.g. Supabase or required abstractions missing), Public Works `initialize()` or GovernanceService construction fails with a clear `RuntimeError`.
- **Curator is only valid with proper Supabase.** Local or in-memory storage is not a final answer for a database of that criticality. The promotion path (CuratorService) is Supabase-backed; Public Works builds CuratorService only when Supabase and artifact/state abstractions are present, and fails fast otherwise.
- **Capability/agent registries** (CuratorFoundationService) are still in-memory for now; for production they should move to Supabase-backed tables (see §5). The *critical* path (promotion to platform DNA) is already Supabase-only and required.

---

## 1. Summary Table

| Component | Status | What’s real | What’s stub/fallback |
|-----------|--------|-------------|----------------------|
| **RegistryAbstraction** (get_registry_entry, register_entry, list_registry_entries) | Real implementation with graceful degradation | Real Supabase calls to table `registry_entries` when table and client exist | If table missing or no client: return None/False/[] and log at debug (no crash) |
| **CuratorFoundationService** (register_capability, list_agents) | Real in-memory implementation | CapabilityRegistry and AgentRegistry actually store and return data | Data is in-memory only; lost on restart until we add Supabase-backed capability/agent tables |
| **CuratorSDK** → CuratorFoundationService | Real wiring | GovernanceService creates CuratorFoundationService and passes it to CuratorSDK; register_capability and discover_agents call the foundation and persist in memory | None |
| **CuratorSDK** → CuratorService (promote_to_platform_dna) | Wired when Public Works initialized first | CuratorService is built inside Public Works (after _create_abstractions); GovernanceService passes it to CuratorSDK via get_curator_service() | If GovernanceService is created before public_works.initialize(), get_curator_service() returns None and promote_to_platform_dna is no-op until next time SDK is built with an initialized Public Works |
| **CuratorSDK** sovereignty methods (classify_artifact, approve_*) | Deliberate stubs | Protocol and method signatures are real; callers can depend on them | Always return “allow all” / default classification; no policy store or rules yet |
| **SemanticProfileRegistry** | Real when table exists | Uses RegistryAbstraction.get_registry_entry/register_entry/list_registry_entries | If `registry_entries` table doesn’t exist or adapter unavailable: uses built-in default profiles only |

---

## 2. What “stub” and “fallback” mean here

- **Stub:** A method that exists for the contract (e.g. CuratorProtocol) but does not implement real business logic yet; it returns a safe default (e.g. “allow all”) so callers don’t break. Replacing stubs = adding real policy/classification later.
- **Fallback:** When the real backend is missing (no table, no client, no service wired), we don’t crash; we return an empty/safe result and optionally log. Fallbacks are intentional defensive behavior, not the main path.

We want the **main path** to be real: when dependencies exist, the system should do real work. Stubs and fallbacks should be clearly documented and eventually replaced or narrowed.

---

## 3. What’s actually missing for a “real working” system

1. **Curator required and Supabase-only**  
   **Done.** Curator is required for platform boot; Public Works fails if Supabase or artifact/state abstractions are missing. GovernanceService fails if get_curator_service() is None. Promotion path is Supabase-backed only.

2. **Sovereignty methods are “allow all”**  
   classify_artifact, approve_promotion, approve_cross_domain, approve_message_routing always return permissive defaults.  
   **Fix:** Introduce a minimal real policy (e.g. config or DB table) and have these methods call it; keep “allow all” only as fallback when policy is missing.

3. **registry_entries table**  
   SemanticProfileRegistry and RegistryAbstraction entry methods are real only if the `registry_entries` table exists in Supabase.  
   **Fix:** Add migration/schema for `registry_entries` so the real path is used in deployed environments.

4. **CuratorFoundationService persistence**  
   Capabilities and agents are stored only in memory; they’re lost on restart.  
   **Fix (later):** Add Supabase tables (e.g. capability_registry, agent_registry) and have CuratorFoundationService (or a backend) use them; or accept in-memory for demo and document it.

---

## 4. Recommended next steps for a real implementation

1. **Curator required and Supabase-only**  
   **Done.** Curator is required for platform run; Public Works fails if Supabase/artifact/state missing; GovernanceService fails if Curator service missing.

2. **Create registry_entries in Supabase**  
   - Run the schema (see CURATOR_LAYER_CLEANUP_AND_TARGET_PATTERN.md) so get_registry_entry/register_entry/list_registry_entries and SemanticProfileRegistry use the real table.

3. **Sovereignty: minimal real policy**  
   - Add a small policy layer (e.g. config or table: “allow promotion from X to Y”, “allow cross-domain from A to B”) and have classify_artifact / approve_* call it; return “allow all” only when policy is absent or not configured.

4. **Document “real vs stub” in code**  
   - In CuratorSDK (and related docs): state clearly which methods are fully implemented vs stub/fallback, and under what conditions (e.g. “promote_to_platform_dna is real when CuratorService is wired”).

After (1)–(3), the system has a real working path: registry entries, capability/agent registration and discovery, promotion to platform DNA when wired, and optional real sovereignty policy, with stubs/fallbacks only where we explicitly choose them (e.g. “allow all” when policy not configured).
