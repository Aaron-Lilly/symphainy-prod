# Smart City Abstractions Implementation Plan

**Date:** January 2026  
**Status:** 📋 **PLAN DEFINED - READY FOR IMPLEMENTATION**

---

## Summary

We have comprehensive existing implementations in `/symphainy_source` that need to be adapted to the new architecture. The key changes are:

1. **Use new utilities:** `get_logger()`, `get_clock()`, `generate_*_id()`
2. **Remove DI container:** Use direct utilities instead
3. **Use env_contract:** Replace `config_adapter` with `get_env_contract()`
4. **Use StateManagementAbstraction:** For caching/state (not direct Redis)
5. **Keep all business logic:** Preserve existing functionality

---

## Implementation Steps

### Step 1: Adapt Adapters (Layer 0)
- ✅ MeilisearchAdapter - DONE
- ⏳ SupabaseAdapter - Need to adapt (large file, ~885 lines)
- ⏳ GCSFileAdapter - Need to adapt (large file, ~495 lines)

### Step 2: Create/Adapt Protocols (Layer 1)
- ⏳ SemanticSearchProtocol - Create simplified version
- ✅ FileStorageProtocol - Already created
- ✅ AuthProtocol - Already created (Authentication, Authorization, Tenancy)

### Step 3: Adapt Abstractions (Layer 2)
- ⏳ SemanticSearchAbstraction - Adapt from KnowledgeDiscoveryAbstraction
- ⏳ AuthAbstraction - Adapt (~577 lines)
- ⏳ TenantAbstraction - Adapt (~456 lines)
- ⏳ FileStorageAbstraction - Adapt from FileManagementAbstraction (~529 lines)

### Step 4: Update Public Works Foundation
- ⏳ Initialize all adapters
- ⏳ Create all abstractions
- ⏳ Expose getter methods

### Step 5: Update Smart City Services
- ⏳ Librarian - Use SemanticSearchAbstraction
- ⏳ Security Guard - Use AuthAbstraction, TenantAbstraction
- ⏳ Data Steward - Use FileStorageAbstraction

---

## Key Files to Adapt

### From `/symphainy_source`:
1. `infrastructure_adapters/supabase_adapter.py` → Adapt to new architecture
2. `infrastructure_adapters/gcs_file_adapter.py` → Adapt to new architecture
3. `infrastructure_abstractions/auth_abstraction.py` → Adapt to new architecture
4. `infrastructure_abstractions/tenant_abstraction_supabase.py` → Adapt to new architecture
5. `infrastructure_abstractions/file_management_abstraction_gcs.py` → Adapt to new architecture
6. `infrastructure_abstractions/knowledge_discovery_abstraction.py` → Adapt to SemanticSearchAbstraction

### To `/symphainy_source_code`:
1. `symphainy_platform/foundations/public_works/adapters/supabase_adapter.py`
2. `symphainy_platform/foundations/public_works/adapters/gcs_adapter.py`
3. `symphainy_platform/foundations/public_works/abstractions/auth_abstraction.py`
4. `symphainy_platform/foundations/public_works/abstractions/tenant_abstraction.py`
5. `symphainy_platform/foundations/public_works/abstractions/file_storage_abstraction.py`
6. `symphainy_platform/foundations/public_works/abstractions/semantic_search_abstraction.py`

---

## Migration Checklist Per File

For each adapter/abstraction:
- [ ] Replace `logging.getLogger(__name__)` with `from utilities import get_logger` → `get_logger(self.__class__.__name__)`
- [ ] Replace `datetime.utcnow()` with `from utilities import get_clock` → `get_clock().now()` or `get_clock().now_iso()`
- [ ] Replace `uuid.uuid4()` with `from utilities import generate_*_id`
- [ ] Remove `di_container` parameter and usage
- [ ] Replace `config_adapter.get("KEY")` with `from config.env_contract import get_env_contract` → `env.KEY`
- [ ] Replace direct Redis calls with `StateManagementAbstraction` (for abstractions)
- [ ] Update imports to match new structure
- [ ] Test that business logic is preserved

---

## Next Action

Given the size of these files, I recommend:
1. Start with the most critical ones (Auth, Tenant, FileStorage for Security Guard and Data Steward)
2. Adapt them systematically
3. Update Public Works Foundation
4. Wire into Smart City services
5. Test integration

Would you like me to proceed with adapting these files now, or would you prefer to review the plan first?
