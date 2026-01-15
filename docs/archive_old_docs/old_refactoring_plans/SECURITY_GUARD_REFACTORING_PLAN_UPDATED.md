# Security Guard Refactoring Plan - UPDATED per Review Board

**Date:** January 2026  
**Status:** 📋 **UPDATED - ALIGNED WITH REVIEW BOARD**  
**Goal:** Refactor Security Guard to new architecture with better security, aligned with Review Board structure

---

## Executive Summary

This plan has been **updated to align with Review Board feedback** on:
- **Libraries vs Registries** distinction
- **Structure** (primitives, SDKs, registries)
- **MCP Tools** decision (stay in Agentic SDK)
- **Realm access pattern** (SDKs only, never primitives directly)

---

## Key Updates from Review Board

### 1. Libraries vs Registries

**Libraries** (imported, versioned):
- `civic_systems/smart_city/primitives/` - Smart City Primitives (code-level)
- `civic_systems/smart_city/sdk/` - Smart City SDK (code-level)
- `libraries/policy/` - Policy Library (code-level)

**Registries** (queried at runtime, data-backed):
- `civic_systems/smart_city/registries/policy_registry.py` - Policy Registry (Supabase-backed)
- `civic_systems/curator/registries/service_registry.py` - Service Registry (Consul-backed)

### 2. Structure Changes

**Old Plan:**
- `civic_systems/smart_city/roles/security_guard/`

**New Plan (per Review Board):**
- `civic_systems/smart_city/primitives/security_guard/` - Primitive (policy decisions only)
- `civic_systems/smart_city/sdk/security_sdk.py` - SDK (boundary zone for Realms)
- `civic_systems/smart_city/registries/policy_registry.py` - Registry (data-backed)

### 3. MCP Tools Decision

**Locked In:**
- MCP tools stay in Agentic SDK
- Never registered globally
- Never visible to Runtime
- Runtime only sees agent conclusions

### 4. Primitive vs SDK

**Primitives:**
- Pure policy decisions only
- No side effects, no infra calls
- Called only by Runtime (later)
- Query Policy Registry for rules

**SDKs:**
- Boundary zone for Realms
- Translate Realm intent → runtime contract shape
- Query Policy Registry
- Call Public Works abstractions
- Never execute anything

### 5. Realm Access Pattern

**Rule:**
- Realms **never** call Smart City primitives directly
- Realms **only** call Smart City SDKs
- Runtime calls primitives (later)

---

## Updated Implementation Plan

### Phase 1: Scaffold Core Libraries & Registries

1. **Create Structure:**
   ```
   civic_systems/smart_city/
   ├── primitives/
   │   └── security_guard/
   ├── sdk/
   │   └── security_sdk.py
   └── registries/
       └── policy_registry.py
   ```

2. **Create Policy Registry:**
   - Type: Registry (data-backed)
   - Backed by: Supabase (via Public Works)
   - Stores: AuthZ rules, data access policies, execution constraints, tenant-specific overrides
   - Queried by: Smart City SDK, Smart City Primitives

### Phase 2: Public Works Abstractions

1. **Tenant Abstraction:**
   - Add `get_user_tenant_info()` to protocol
   - Implement in abstraction
   - Return raw data only

2. **Authorization Abstraction:**
   - Refactor to return raw data only
   - Remove policy logic (move to primitives)

### Phase 3: Platform SDK Enhancement

1. **Enhance translation logic:**
   - Tenant resolution
   - Role/permission extraction
   - SecurityContext creation

### Phase 4: Smart City SDK (Boundary Zone)

1. **Create Security SDK:**
   - Location: `civic_systems/smart_city/sdk/security_sdk.py`
   - Methods: `ensure_user_can()`, `validate_tenant_access()`
   - Queries Policy Registry
   - Prepares runtime contract shape
   - Never calls primitives directly

### Phase 5: Security Guard Primitive

1. **Create Primitive:**
   - Location: `civic_systems/smart_city/primitives/security_guard/`
   - Pure policy decisions only
   - Queries Policy Registry
   - No side effects, no infra calls
   - Called only by Runtime (later)

### Phase 6: Realm Refactor

1. **Update realm services:**
   - Use Smart City SDK (not primitives)
   - Change: `auth_service.validate_user(...)` → `smart_city_sdk.ensure_user_can(...)`
   - All functional logic stays where it is

### Phase 7: Integration & Testing

1. **Update Runtime** (later) to use Security Guard Primitive
2. **Update realm services** to use Smart City SDK
3. **Run all tests**
4. **Update documentation**

---

## Success Criteria

Phase 1 is complete when:

- [ ] Smart City logic exists as primitives + SDK
- [ ] Policy Registry is queryable without Runtime
- [ ] Realms only talk to SDKs (never primitives directly)
- [ ] Public Works remains the only infra gateway
- [ ] No behavior regressions in the MVP

---

## Summary

This updated plan aligns with Review Board feedback and provides:
- ✅ Clear Libraries vs Registries distinction
- ✅ Proper structure (primitives, SDKs, registries)
- ✅ MCP tools decision locked in
- ✅ Realm access pattern (SDKs only)
- ✅ Better separation of concerns
- ✅ Better testability
- ✅ Better security
