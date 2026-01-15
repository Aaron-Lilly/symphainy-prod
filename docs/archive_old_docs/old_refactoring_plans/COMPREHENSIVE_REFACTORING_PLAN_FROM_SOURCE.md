# Comprehensive Refactoring Plan - From symphainy_source

**Date:** January 2026  
**Status:** 📋 **NEW PLAN FROM SCRATCH**  
**Base:** `/symphainy_source/` (real implementations)  
**Target:** New architecture with proper adapter → abstraction flows, Smart City primitives, SDK

---

## Executive Summary

**The Situation:**
- ✅ `/symphainy_source/` has **real, working implementations** with micro-modular architecture
- ❌ Current `symphainy_source_code` has **empty shells** (incomplete implementations)
- 🔴 `/symphainy_source/` has **anti-patterns** that need fixing:
  - Business logic in abstractions (auth creates tenants, extracts roles)
  - Services access adapters directly (bypassing abstractions)
  - Services have business logic (should be primitives)
  - No SDK boundary zone

**The Goal:**
- ✅ Refactor from `/symphainy_source/` to new architecture
- ✅ Proper Adapter → Abstraction flows for ALL Smart City infrastructure
- ✅ Smart City primitives (governance decisions only)
- ✅ SDK created to house business logic from old adapters and services
- ✅ Identify and document anti-patterns

---

## Part 1: Assessment of symphainy_source

### Smart City Services in symphainy_source

**Location:** `/symphainy_source/symphainy-platform/backend/smart_city/services/`

**8 Services with Real Implementations:**
1. **Security Guard** - Micro-modular with modules (authentication, orchestration, soa_mcp, utilities)
2. **City Manager** - Micro-modular with modules (bootstrapping, realm_orchestration, platform_governance)
3. **Traffic Cop** - Micro-modular with modules (session_management, websocket_session_management)
4. **Post Office** - Micro-modular with modules (event_routing, initialization, soa_mcp)
5. **Conductor** - Micro-modular implementation
6. **Librarian** - Micro-modular implementation
7. **Data Steward** - Micro-modular with modules (file_lifecycle, lineage_tracking, policy_management)
8. **Nurse** - Micro-modular implementation

**Key Characteristics:**
- ✅ Use `SmartCityRoleBase` (old base class)
- ✅ Use DI Container for infrastructure access
- ✅ Use `InfrastructureAccessMixin` to get abstractions
- ✅ Have micro-modules for organization
- ✅ Have SOA APIs and MCP tools
- 🔴 **Access adapters directly** (bypassing abstractions in some cases)
- 🔴 **Have business logic** (should be primitives)

### Infrastructure Abstractions in symphainy_source

**Location:** `/symphainy_source/symphainy-platform/foundations/public_works_foundation/infrastructure_abstractions/`

**58+ Abstractions Exist:**
- ✅ Auth Abstraction (has business logic - creates tenants, extracts roles)
- ✅ Tenant Abstraction (has business logic - validates access)
- ✅ File Management Abstraction
- ✅ Content Metadata Abstraction (has business logic - ID generation, validation)
- ✅ Semantic Data Abstraction (has business logic - validation, business rules)
- ✅ Workflow Orchestration Abstraction (has business logic - workflow definition/execution)
- ✅ Event Management Abstraction
- ✅ Messaging Abstraction
- ✅ Telemetry Abstraction
- ✅ Session Abstraction
- ✅ Policy Abstraction
- ✅ Authorization Abstraction (has business logic - permission checking)
- ✅ ... and 45+ more

**Key Characteristics:**
- ✅ Use adapters via DI Container
- ✅ Follow adapter → abstraction pattern
- 🔴 **Many have business logic** (should be pure infrastructure)
- 🔴 **Some return business objects** (should return raw data)

---

## Part 2: Anti-Patterns Identified

### Anti-Pattern 1: Business Logic in Abstractions

**Example: Auth Abstraction**
```python
# ❌ ANTI-PATTERN: Auth Abstraction creates tenants
async def authenticate_user(self, credentials):
    # ... auth logic ...
    if not tenant_id:
        tenant_result = await self._create_tenant_for_user(...)  # ❌ Business logic
        # Link user to tenant
        link_result = await self.supabase.link_user_to_tenant(...)  # ❌ Business logic
    
    # Extract roles and permissions
    roles = tenant_info.get("roles", [])  # ❌ Business logic (role extraction)
    permissions = tenant_info.get("permissions", [])  # ❌ Business logic
    
    # Create SecurityContext
    context = SecurityContext(...)  # ❌ Business object creation
    return context
```

**Fix:**
- Abstraction returns raw user data only
- Policy logic → Security Guard (governance decision)
- Translation logic → Platform SDK (how to create SecurityContext)
- Business logic → Domain service (if needed)

### Anti-Pattern 2: Services Access Adapters Directly

**Example: Security Guard Authentication Module**
```python
# ❌ ANTI-PATTERN: Service accesses adapter directly
if hasattr(auth_abstraction, 'supabase'):
    supabase_result = await auth_abstraction.supabase.sign_in_with_password(...)  # ❌ Bypasses abstraction
```

**Fix:**
- Services ONLY use abstractions (never adapters directly)
- Abstractions hide adapter details
- Services don't know which adapter is used

### Anti-Pattern 3: Services Have Business Logic

**Example: Security Guard**
```python
# ❌ ANTI-PATTERN: Service has business logic
async def authenticate_user(self, credentials):
    # Resolve tenant
    tenant_id = await self._resolve_tenant(...)  # ❌ Business logic
    
    # Resolve roles/permissions
    roles, permissions = await self._resolve_roles_permissions(...)  # ❌ Business logic
    
    # Create SecurityContext
    return SecurityContext(...)  # ❌ Business object creation
```

**Fix:**
- Services provide governance decisions only (`evaluate_auth()` → PolicyValidationResult)
- Translation logic → Platform SDK (`resolve_security_context()` → SecurityContext)
- Business logic → Domain services (if needed)

### Anti-Pattern 4: No SDK Boundary Zone

**Current Flow:**
```
Runtime → Smart City Service → Abstraction → Adapter
```

**Problem:** No translation layer between Runtime and Smart City

**Fix:**
```
Runtime → Platform SDK → Smart City Role → Abstraction → Adapter
              ↓
         Translation Logic
```

### Anti-Pattern 5: Abstractions Return Business Objects

**Example: Auth Abstraction**
```python
# ❌ ANTI-PATTERN: Returns business object
async def authenticate_user(self, credentials) -> SecurityContext:  # ❌ Business object
    return SecurityContext(...)
```

**Fix:**
- Abstractions return raw data (Dict[str, Any])
- SDK creates business objects (SecurityContext)

---

## Part 3: Complete Refactoring Plan

### Phase 1: Assessment & Inventory (Week 1, Days 1-2)

**Goal:** Complete inventory of what exists and what needs refactoring

**Tasks:**

1. **Inventory Smart City Services**
   - [ ] List all 8 services in `/symphainy_source/`
   - [ ] Document micro-modules for each service
   - [ ] Document SOA APIs and MCP tools
   - [ ] Identify business logic in services
   - [ ] Identify adapter direct access

2. **Inventory Infrastructure Abstractions**
   - [ ] List all 58+ abstractions in `/symphainy_source/`
   - [ ] Document which have business logic
   - [ ] Document which return business objects
   - [ ] Document adapter → abstraction flows

3. **Create Complete Migration Map**
   - [ ] Map: Policy logic → Smart City roles
   - [ ] Map: Translation logic → SDKs
   - [ ] Map: Business logic → Domain services
   - [ ] Map: Adapter direct access → Abstraction usage

4. **Document Anti-Patterns**
   - [ ] List all anti-patterns found
   - [ ] Document fixes for each
   - [ ] Create anti-pattern checklist

---

### Phase 2: Refactor Abstractions (Week 1, Days 3-5)

**Goal:** Make all abstractions pure infrastructure

**Tasks:**

1. **Refactor Auth Abstraction**
   - [ ] Remove tenant creation logic
   - [ ] Remove role extraction logic
   - [ ] Remove SecurityContext creation
   - [ ] Return raw user data only
   - [ ] Test is pure infrastructure

2. **Refactor Tenant Abstraction**
   - [ ] Remove access validation logic
   - [ ] Remove configuration management
   - [ ] Return raw tenant data only
   - [ ] Test is pure infrastructure

3. **Refactor Content Metadata Abstraction**
   - [ ] Remove ID generation
   - [ ] Remove validation rules
   - [ ] Remove status management
   - [ ] Return raw metadata only
   - [ ] Test is pure infrastructure

4. **Refactor Semantic Data Abstraction**
   - [ ] Remove validation logic
   - [ ] Remove business rules
   - [ ] Return raw semantic data only
   - [ ] Test is pure infrastructure

5. **Refactor Workflow Orchestration Abstraction**
   - [ ] Remove workflow definition logic
   - [ ] Remove workflow execution logic
   - [ ] Return raw workflow data only
   - [ ] Test is pure infrastructure

6. **Refactor Authorization Abstraction**
   - [ ] Remove permission checking logic
   - [ ] Remove access validation logic
   - [ ] Return raw authorization data only
   - [ ] Test is pure infrastructure

7. **Review Remaining Abstractions**
   - [ ] Check all other abstractions for business logic
   - [ ] Fix any found
   - [ ] Test all are pure infrastructure

---

### Phase 3: Create Platform SDK (Week 2, Days 1-2)

**Goal:** Create SDK boundary zone for translation logic

**Tasks:**

1. **Create Platform SDK Foundation**
   - [ ] Create `civic_systems/platform_sdk/` structure
   - [ ] Create `platform_sdk.py` with translation methods
   - [ ] Wire to Smart City roles and abstractions

2. **Move Translation Logic to Platform SDK**
   - [ ] `resolve_security_context()` - From Auth Abstraction + Security Guard
   - [ ] `resolve_tenant()` - From Tenant Abstraction
   - [ ] `resolve_roles_permissions()` - From Auth Abstraction
   - [ ] Test translation logic works

3. **Create Realm SDK Foundation**
   - [ ] Create `civic_systems/platform_sdk/realm_sdk.py`
   - [ ] Add realm-specific translation methods
   - [ ] Wire to realm services

---

### Phase 4: Refactor Smart City Services to Primitives (Week 2, Days 3-5)

**Goal:** Convert Smart City services to policy-aware primitives

**Tasks:**

1. **Refactor Security Guard**
   - [ ] Move to `civic_systems/smart_city/roles/security_guard/`
   - [ ] Implement `SmartCityRoleProtocol`
   - [ ] Remove business logic (move to Platform SDK)
   - [ ] Add policy logic (`evaluate_auth()`, `validate_tenant_access()`)
   - [ ] Remove adapter direct access (use abstractions only)
   - [ ] Test provides primitives only

2. **Refactor City Manager**
   - [ ] Move to `civic_systems/smart_city/roles/city_manager/`
   - [ ] Ensure implements `SmartCityRoleProtocol`
   - [ ] Remove business logic (move to Platform SDK)
   - [ ] Add policy logic (`validate_policy()`)
   - [ ] Remove adapter direct access
   - [ ] Test provides primitives only

3. **Refactor Data Steward**
   - [ ] Move to `civic_systems/smart_city/roles/data_steward/`
   - [ ] Ensure implements `SmartCityRoleProtocol`
   - [ ] Remove business logic (move to Realm SDK)
   - [ ] Add policy logic (`validate_data_access()`)
   - [ ] Remove adapter direct access
   - [ ] Test provides primitives only

4. **Refactor Remaining Services**
   - [ ] Traffic Cop, Post Office, Conductor, Librarian, Nurse
   - [ ] Move to `civic_systems/smart_city/roles/`
   - [ ] Ensure implement `SmartCityRoleProtocol`
   - [ ] Remove business logic
   - [ ] Remove adapter direct access
   - [ ] Test provide primitives only

---

### Phase 5: Create Proper Adapter → Abstraction Flows (Week 3)

**Goal:** Ensure ALL Smart City infrastructure uses proper flows

**Tasks:**

1. **Map All Smart City Infrastructure Needs**
   - [ ] Security Guard: Auth, Tenant, Authorization abstractions
   - [ ] City Manager: Policy, Tenant abstractions
   - [ ] Data Steward: File Storage, Content Metadata abstractions
   - [ ] Librarian: Semantic Search, Semantic Data abstractions
   - [ ] Traffic Cop: Session, State abstractions
   - [ ] Post Office: Event Management, Messaging abstractions
   - [ ] Conductor: Workflow Orchestration, State abstractions
   - [ ] Nurse: Telemetry, Health abstractions

2. **Ensure All Abstractions Exist**
   - [ ] Copy missing abstractions from `/symphainy_source/`
   - [ ] Refactor to remove business logic
   - [ ] Test are pure infrastructure

3. **Ensure All Services Use Abstractions**
   - [ ] Remove all adapter direct access
   - [ ] Use abstractions only
   - [ ] Test proper flows

---

### Phase 6: Integration & Testing (Week 3-4)

**Goal:** Ensure everything works together

**Tasks:**

1. **Update Foundation Services**
   - [ ] Update Smart City Foundation Service
   - [ ] Update Public Works Foundation Service
   - [ ] Wire all abstractions
   - [ ] Wire all Smart City roles

2. **Update Runtime Integration**
   - [ ] Ensure Runtime calls Smart City via SDK (not directly)
   - [ ] Ensure Runtime calls Curator via SDK (not Consul directly)
   - [ ] Test integration works

3. **Run All Tests**
   - [ ] Unit tests for abstractions
   - [ ] Unit tests for Smart City roles
   - [ ] Unit tests for SDKs
   - [ ] Integration tests
   - [ ] E2E tests

4. **Update Documentation**
   - [ ] Document new architecture
   - [ ] Document anti-patterns fixed
   - [ ] Document migration guide

---

## Part 4: Anti-Patterns & Questions

### Anti-Patterns Found

1. **Business Logic in Abstractions** 🔴 **CRITICAL**
   - **Auth Abstraction:**
     - Creates tenants automatically (`_create_tenant_for_user()`)
     - Links users to tenants (`link_user_to_tenant()`)
     - Extracts roles and permissions from tenant info
     - Creates SecurityContext (business object)
   - **Tenant Abstraction:**
     - Validates tenant access (business rule)
     - Manages tenant configuration (business logic)
   - **Content Metadata Abstraction:**
     - Generates content IDs (business logic)
     - Validates content (business rules)
     - Manages status/version (business logic)
   - **Semantic Data Abstraction:**
     - Validates embeddings (business rules)
     - Applies semantic graph business rules
   - **Workflow Orchestration Abstraction:**
     - Defines workflows (business logic)
     - Executes workflows (business logic)
   - **Authorization Abstraction:**
     - Checks permissions (business logic)
     - Validates access (business rules)
     - Hardcodes "MVP open policy" (business rule)

2. **Services Access Adapters Directly** 🔴 **CRITICAL**
   - **Security Guard Authentication Module:**
     ```python
     # ❌ ANTI-PATTERN: Accesses adapter directly
     if hasattr(auth_abstraction, 'supabase'):
         supabase_result = await auth_abstraction.supabase.sign_in_with_password(...)
     ```
   - **Problem:** Bypasses abstraction layer, creates tight coupling
   - **Fix:** Services ONLY use abstractions (never adapters)

3. **Services Have Business Logic** 🔴 **CRITICAL**
   - **Security Guard:**
     - Resolves tenants (`_resolve_tenant()`)
     - Resolves roles/permissions (`_resolve_roles_permissions()`)
     - Creates SecurityContext (business object)
   - **Data Steward:**
     - Manages file lifecycle (business logic)
     - Enforces data policies (business rules)
   - **Problem:** Services should be primitives (governance decisions only)
   - **Fix:** Move business logic to SDK, keep only policy logic in services

4. **No SDK Boundary Zone** 🔴 **CRITICAL**
   - **Current Flow:**
     ```
     Runtime → Smart City Service → Abstraction → Adapter
     ```
   - **Problem:** No translation layer, Runtime would call Smart City directly
   - **Fix:**
     ```
     Runtime → Platform SDK → Smart City Role → Abstraction → Adapter
              ↓
         Translation Logic
     ```

5. **Abstractions Return Business Objects** 🔴 **CRITICAL**
   - **Auth Abstraction:**
     ```python
     async def authenticate_user(...) -> SecurityContext:  # ❌ Business object
     ```
   - **Problem:** Abstractions should return raw data
   - **Fix:** Return `Dict[str, Any]`, SDK creates business objects

6. **DI Container Dependency** 🟡 **MODERATE**
   - Services use DI Container to get abstractions
   - Creates unnecessary coupling
   - **Fix:** Use direct dependency injection (cleaner)

7. **Micro-Modules Have Business Logic** 🟡 **MODERATE**
   - Micro-modules implement business logic from scratch
   - Don't use abstractions properly
   - **Fix:** Micro-modules use abstractions, contain only organization logic

8. **Base Class Dependency** 🟡 **MODERATE**
   - Services extend `SmartCityRoleBase` (old architecture)
   - Creates tight coupling
   - **Fix:** Use `SmartCityRoleProtocol` only (protocol-based)

### Questions to Address

1. **Micro-Modules Pattern**
   - **Question:** Should we keep micro-modules in new architecture?
   - **Current:** Dynamic loading via mixin, complex
   - **Recommendation:** Yes, but simplified:
     - No dynamic loading (just organized code)
     - Direct imports (not mixin-based)
     - Micro-modules use abstractions (not adapters)
     - Micro-modules contain organization logic only (not business logic)

2. **SOA APIs and MCP Tools**
   - **Question:** Should Smart City roles expose SOA APIs and MCP tools?
   - **Current:** Services expose SOA APIs and MCP tools directly
   - **Recommendation:** Yes, but via SDK:
     - SDK exposes SOA APIs (not roles directly)
     - SDK exposes MCP tools (not roles directly)
     - Roles provide primitives (SDK wraps them)

3. **DI Container Dependency**
   - **Question:** Should Smart City roles use DI Container?
   - **Current:** Services use DI Container to get abstractions
   - **Recommendation:** No, use direct dependency injection:
     - Roles receive abstractions via constructor
     - Cleaner, more testable
     - No DI Container coupling

4. **Base Classes**
   - **Question:** Should we keep `SmartCityRoleBase`?
   - **Current:** Services extend `SmartCityRoleBase` (old architecture)
   - **Recommendation:** No, use `SmartCityRoleProtocol` only:
     - Protocol-based (not inheritance-based)
     - Cleaner separation
     - No base class coupling

5. **State Management**
   - **Question:** Should Smart City roles manage state?
   - **Current:** Some services manage internal state
   - **Recommendation:** No, Runtime owns state:
     - Roles are stateless primitives
     - Runtime manages all state
     - Roles observe Runtime (via observer pattern)

6. **Infrastructure Access Pattern**
   - **Question:** How should Smart City roles access abstractions?
   - **Current:** Via `InfrastructureAccessMixin.get_infrastructure_abstraction()`
   - **Recommendation:** Direct dependency injection:
     - Roles receive abstractions via constructor
     - No mixin needed
     - Cleaner, more explicit

7. **Adapter → Abstraction Flow**
   - **Question:** Should services ever access adapters directly?
   - **Current:** Some services access `abstraction.adapter` directly
   - **Recommendation:** Never:
     - Services ONLY use abstractions
     - Abstractions hide adapter details
     - If abstraction doesn't expose what's needed, fix abstraction (don't bypass it)

---

## Part 5: Detailed Migration Map

### Security Guard Migration

**From:** `/symphainy_source/symphainy-platform/backend/smart_city/services/security_guard/`

**To:** `civic_systems/smart_city/roles/security_guard/`

**What to Keep:**
- ✅ Micro-module structure (simplified)
- ✅ Infrastructure abstraction usage pattern
- ✅ Policy enforcement logic

**What to Remove:**
- ❌ Business logic (tenant resolution, role extraction, SecurityContext creation)
- ❌ Adapter direct access
- ❌ DI Container dependency
- ❌ `SmartCityRoleBase` (use protocol only)

**What to Add:**
- ✅ `SmartCityRoleProtocol` implementation
- ✅ Policy methods (`evaluate_auth()`, `validate_tenant_access()`)
- ✅ SDK integration

**Translation Logic → Platform SDK:**
- `resolve_security_context()` - From authentication module
- `resolve_tenant()` - From authentication module
- `resolve_roles_permissions()` - From authentication module

### Auth Abstraction Migration

**From:** `/symphainy_source/symphainy-platform/foundations/public_works_foundation/infrastructure_abstractions/auth_abstraction.py`

**To:** `symphainy_platform/foundations/public_works/abstractions/auth_abstraction.py`

**What to Keep:**
- ✅ Adapter usage pattern
- ✅ Error handling
- ✅ Infrastructure logic

**What to Remove:**
- ❌ Tenant creation logic (`_create_tenant_for_user()`)
- ❌ Role extraction logic
- ❌ SecurityContext creation
- ❌ Business object returns

**What to Add:**
- ✅ Raw data return (Dict[str, Any])
- ✅ Pure infrastructure interface

---

## Part 6: Success Criteria

### ✅ Abstractions

- [ ] All abstractions return raw data (not business objects)
- [ ] All abstractions are pure infrastructure (no business logic)
- [ ] All abstractions are swappable (technology-agnostic)
- [ ] All abstractions have proper adapter → abstraction flows

### ✅ Smart City Roles

- [ ] All roles moved to `civic_systems/smart_city/roles/`
- [ ] All roles implement `SmartCityRoleProtocol`
- [ ] All roles provide governance decisions only (not business logic)
- [ ] All roles use abstractions (not adapters directly)
- [ ] All roles are stateless primitives

### ✅ SDKs

- [ ] Platform SDK created with translation logic
- [ ] Realm SDK created with translation logic
- [ ] SDKs translate Smart City decisions into runtime objects
- [ ] SDKs shield Runtime from infrastructure details

### ✅ Integration

- [ ] Runtime calls Smart City via SDK (not directly)
- [ ] Runtime calls Curator via SDK (not Consul directly)
- [ ] All adapter → abstraction flows work
- [ ] End-to-end flows work
- [ ] All tests pass

---

## Timeline

**Week 1:** Assessment + Abstraction Refactoring  
**Week 2:** Platform SDK + Smart City Refactoring  
**Week 3:** Adapter → Abstraction Flows + Integration  
**Week 4:** Testing + Documentation

**Total: 4 weeks for complete refactoring**

---

## Next Steps

1. **Complete Assessment** (Day 1-2)
   - Inventory all services and abstractions
   - Document all anti-patterns
   - Create complete migration map

2. **Start Refactoring** (Day 3+)
   - Begin with Auth Abstraction (most critical)
   - Then Security Guard
   - Then Platform SDK
   - Continue with remaining components
