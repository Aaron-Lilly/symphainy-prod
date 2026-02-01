# Curator / Registry Infrastructure Alignment

**Status:** Assessment (January 2026)

## 1. Contract vs Reality

- **ctx.governance.registry** (CuratorSDK): register_capability, discover_agents, get_domain_registry are **stubs** (no Supabase/Consul). promote_to_platform_dna uses CuratorService -> Supabase solution_registry, intent_registry, realm_registry.

## 2. Who Uses What

- **CuratorSDK**: stubs for capability/agent/domain; only promote writes to Supabase.
- **CuratorFoundationService** (foundations/curator): CapabilityRegistry, AgentRegistry in-memory; ServiceRegistry uses Consul. **Not wired to CuratorSDK.**
- **RegistryAbstraction**: Supabase artifact_index, intent_executions + generic RLS. Does **not** implement list_files, get_registry_entry, register_entry (callers expect these -> broken).

## 3. Supabase Tables

artifact_index, intent_executions, solution_registry, intent_registry, realm_registry, data_boundary_contracts, materialization_policies, records_of_fact, project_files, user_tenants, tenants. No schema/migrations in repo for solution/intent/realm_registry.

## 4. Bugs Fixed / Gaps

1. **CuratorService**: return created ID from response.data[0].get(id_field) not registry_id (fixed).
2. **RegistryAbstraction.list_files**: not implemented; list_artifacts_service calls it -> AttributeError. Use file_storage/file_management.
3. **RegistryAbstraction get_registry_entry/register_entry/list_registry_entries**: not implemented; semantic_profile_registry broken.
4. **CuratorSDK capability/agent**: no backing. Wire to CuratorFoundationService or Supabase.
