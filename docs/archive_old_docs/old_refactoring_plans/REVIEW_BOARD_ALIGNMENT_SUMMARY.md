# Review Board Alignment Summary - Security Guard Refactoring

**Date:** January 2026  
**Status:** ✅ **ALIGNED WITH REVIEW BOARD**  
**Purpose:** Summary of updates to Security Guard refactoring plan based on Review Board feedback

---

## Key Updates Made

### 1. ✅ Libraries vs Registries Distinction

**Updated Plan:**
- **Libraries** (imported, versioned):
  - `civic_systems/smart_city/primitives/security_guard/` - Security Guard Primitive (code-level)
  - `civic_systems/smart_city/sdk/security_sdk.py` - Security SDK (code-level)
  - `libraries/policy/` - Policy Library (code-level)

- **Registries** (queried at runtime, data-backed):
  - `civic_systems/smart_city/registries/policy_registry.py` - Policy Registry (Supabase-backed)
  - Stores: AuthZ rules, data access policies, execution constraints, tenant-specific overrides

**Impact:** Policy rules come from Registry (data), not hardcoded in primitives.

---

### 2. ✅ Structure Changes

**Old Plan:**
- `civic_systems/smart_city/roles/security_guard/`

**New Plan (per Review Board):**
- `civic_systems/smart_city/primitives/security_guard/` - Primitive (policy decisions only)
- `civic_systems/smart_city/sdk/security_sdk.py` - SDK (boundary zone for Realms)
- `civic_systems/smart_city/registries/policy_registry.py` - Registry (data-backed)

**Impact:** Clear separation of concerns - primitives, SDKs, and registries are distinct.

---

### 3. ✅ MCP Tools Decision (Locked In)

**Review Board Decision:**
- MCP tools stay in Agentic SDK
- Never registered globally
- Never visible to Runtime
- Runtime only sees agent conclusions

**Impact:** Security Guard Primitive does NOT have MCP tools. Agents use Agentic SDK for MCP tools.

---

### 4. ✅ Primitive vs SDK Clarification

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
- Never call primitives directly (that's Runtime's job)

**Impact:** Realms use SDKs, Runtime uses primitives. Clear boundary.

---

### 5. ✅ Realm Access Pattern

**Rule:**
- Realms **never** call Smart City primitives directly
- Realms **only** call Smart City SDKs
- Runtime calls primitives (later)

**Example:**
```python
# ❌ OLD: Realm calls primitive directly
security_guard_primitive.evaluate_auth(...)

# ✅ NEW: Realm calls SDK
security_sdk.ensure_user_can(...)
```

**Impact:** SDK is the boundary zone, primitives are Runtime-only.

---

## Critical Updates to Implementation

### Policy Registry (NEW)

**Location:** `civic_systems/smart_city/registries/policy_registry.py`

**Type:** Registry (data-backed, queried at runtime)

**Backed by:** Supabase (via Public Works)

**Stores:**
- AuthZ rules
- Data access policies
- Execution constraints
- Tenant-specific overrides

**Queried by:**
- Smart City SDK (for Realm requests)
- Smart City Primitives (for policy decisions)

**Implementation:**
```python
class PolicyRegistry:
    async def get_auth_policy(self, action: str, resource: Optional[str] = None) -> Dict[str, Any]:
        """Query Policy Registry for authentication policy rules."""
        # Query Supabase for policy rules
        ...
    
    async def get_tenant_isolation_rules(self, tenant_id: str) -> Dict[str, Any]:
        """Query Policy Registry for tenant isolation rules."""
        # Query Supabase for tenant isolation configuration
        ...
```

---

### Security Guard Primitive (UPDATED)

**Key Changes:**
1. **Queries Policy Registry** (not hardcoded config)
2. **Pure primitive** (no side effects, no infra calls)
3. **Called only by Runtime** (not by Realms)

**Example:**
```python
async def evaluate_auth(self, security_context, action, resource):
    # Query Policy Registry for rules
    auth_policy = await self.policy_registry.get_auth_policy(action, resource)
    
    # Policy decision based on Registry rules
    if auth_policy.get("zero_trust_enabled", True):
        # Zero-trust policy from Registry
        ...
    
    return {"allowed": bool, "reason": str, "policy_id": str}
```

---

### Smart City SDK (UPDATED)

**Key Changes:**
1. **Boundary zone for Realms** (not convenience layer)
2. **Queries Policy Registry** (not primitives)
3. **Prepares runtime contract shape** (for Runtime to use with primitives)
4. **Never calls primitives directly** (that's Runtime's job)

**Example:**
```python
async def ensure_user_can(self, action, tenant_id, user_id, resource):
    # Query Policy Registry
    policy_rules = await self.policy_registry.get_policy_rules(...)
    
    # Get user context (via Platform SDK translation)
    security_context = await self.platform_sdk.resolve_security_context(...)
    
    # Prepare runtime contract shape (for Runtime)
    return {
        "action": action,
        "security_context": security_context,
        "policy_rules": policy_rules,
        "ready_for_runtime": True
    }
```

---

## Questions & Recommendations

### Q1: Should Policy Registry be created in Phase 1?

**Recommendation:** Yes. Policy Registry is foundational and should be created early.

**Rationale:**
- Primitives need to query it
- SDKs need to query it
- It's data-backed (Supabase), so needs to be set up early

---

### Q2: How do we migrate existing policy logic to Policy Registry?

**Recommendation:** 
1. Identify all hardcoded policy rules in `/symphainy_source/`
2. Extract to Policy Registry schema
3. Populate Registry with existing rules
4. Update primitives to query Registry

**Example Migration:**
```python
# OLD: Hardcoded in primitive
if self.zero_trust_enabled:
    ...

# NEW: Query Registry
auth_policy = await self.policy_registry.get_auth_policy(action, resource)
if auth_policy.get("zero_trust_enabled", True):
    ...
```

---

### Q3: Should Policy Registry have a Library component?

**Recommendation:** Yes. Create `libraries/policy/` for:
- Policy schemas
- Validation helpers
- Evaluation utilities

**Structure:**
```
libraries/policy/
├── schemas.py          # Policy rule schemas
├── validators.py       # Policy validation helpers
└── evaluators.py       # Policy evaluation utilities
```

**Usage:**
- Policy Registry uses schemas for validation
- Primitives use evaluators for policy decisions
- SDKs use validators for input validation

---

### Q4: How does Runtime use Security Guard Primitive?

**Recommendation:** Runtime calls primitives directly (not via SDK).

**Flow:**
```
Realm → Smart City SDK → Runtime Contract Shape
Runtime → Security Guard Primitive → Policy Decision
```

**Example:**
```python
# In Runtime:
runtime_contract = await smart_city_sdk.ensure_user_can(...)
policy_result = await security_guard_primitive.evaluate_auth(
    runtime_contract["security_context"],
    runtime_contract["action"],
    runtime_contract["resource"]
)

if not policy_result.get("allowed"):
    raise PermissionError("Access denied")
```

---

## Updated Implementation Phases

### Phase 1: Scaffold Core Libraries & Registries
1. Create directory structure
2. Create Policy Registry (data-backed, flexible JSONB schema - deferred full schema)
3. Create Policy Library (scaffold structure, schemas, stubs - full implementation in Phase 2)

### Phase 2: Public Works Abstractions
1. Tenant Abstraction - Add `get_user_tenant_info()`
2. Authorization Abstraction - Refactor to return raw data

### Phase 3: Platform SDK Enhancement
1. Enhance translation logic
2. Add tenant resolution helpers

### Phase 4: Smart City SDK (Boundary Zone)
1. Create Security SDK
2. Implement `ensure_user_can()` (queries Policy Registry)
3. Implement `validate_tenant_access()` (queries Policy Registry)

### Phase 5: Security Guard Primitive (Pure Primitive)
1. Create Security Guard Primitive
2. Implement policy methods (query Policy Registry)
3. Ensure pure (no side effects, no infra calls)

### Phase 6: Realm Refactor
1. Update realm services to use Smart City SDK
2. Remove direct primitive calls

### Phase 7: Integration & Testing
1. Test Policy Registry queries
2. Test SDK boundary zone
3. Test Primitive policy decisions
4. Test Realm → SDK → Runtime contract flow

---

## Success Criteria (Updated)

Phase 1 is complete when:

- [ ] Smart City logic exists as primitives + SDK
- [ ] Policy Registry is queryable without Runtime
- [ ] Realms only talk to SDKs (never primitives directly)
- [ ] Public Works remains the only infra gateway
- [ ] No behavior regressions in the MVP

---

## Summary

The updated plan now:
- ✅ Distinguishes Libraries (imported) vs Registries (queried)
- ✅ Uses proper structure (primitives, SDKs, registries)
- ✅ Locks in MCP tools decision (Agentic SDK only)
- ✅ Clarifies Primitive vs SDK (Runtime vs Realm boundary)
- ✅ Enforces Realm access pattern (SDKs only)

**Key Improvement:** Policy rules come from Registry (data), making them configurable and tenant-specific, rather than hardcoded in primitives.

---

## Locked-In Decisions (Final)

### ✅ Policy Registry Schema
**Decision:** Defer full schema definition, use flexible JSONB structure  
**Rationale:** Phase 1 is about moving logic, not perfecting schemas  
**Implementation:** JSONB `policy_data` column, evolvable structure

### ✅ Policy Library
**Decision:** Scaffold now with minimal implementation  
**Rationale:** SDKs and Primitives need to import from it, prevents circular dependencies  
**Phase 1:** Scaffold structure, define schemas, provide stubs  
**Phase 2:** Full validation/evaluation implementation
