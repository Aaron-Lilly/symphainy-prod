# Anti-Patterns & Questions - symphainy_source Analysis

**Date:** January 2026  
**Status:** 📋 **ANTI-PATTERN ANALYSIS**  
**Base:** `/symphainy_source/` analysis

---

## Executive Summary

**Found 8 major anti-patterns** in `/symphainy_source/` that need fixing:
- 🔴 **5 Critical** (block new architecture)
- 🟡 **3 Moderate** (should fix)

**5 Questions** need architecture team answers before proceeding.

---

## Critical Anti-Patterns (Must Fix)

### Anti-Pattern 1: Business Logic in Abstractions 🔴

**Severity:** CRITICAL  
**Impact:** Abstractions are not swappable, violate separation of concerns

**Examples:**

1. **Auth Abstraction** (`auth_abstraction.py`)
   ```python
   # ❌ Creates tenants (business logic)
   if not tenant_id:
       tenant_result = await self._create_tenant_for_user(...)
       link_result = await self.supabase.link_user_to_tenant(...)
   
   # ❌ Extracts roles (business logic)
   roles = tenant_info.get("roles", [])
   permissions = tenant_info.get("permissions", [])
   
   # ❌ Creates business object (business logic)
   context = SecurityContext(...)
   return context
   ```

2. **Tenant Abstraction** (`tenant_abstraction.py`)
   ```python
   # ❌ Validates access (business rule)
   async def validate_tenant_access(...):
       # Business logic: tenant isolation policy
   ```

3. **Content Metadata Abstraction** (`content_metadata_abstraction.py`)
   ```python
   # ❌ Generates IDs (business logic)
   content_id = self._generate_content_id(...)
   
   # ❌ Validates content (business rules)
   if not self._validate_content(...):
       raise ValidationError(...)
   ```

**Fix:**
- Abstractions return raw data only (`Dict[str, Any]`)
- Policy logic → Smart City roles
- Translation logic → SDKs
- Business logic → Domain services

---

### Anti-Pattern 2: Services Access Adapters Directly 🔴

**Severity:** CRITICAL  
**Impact:** Bypasses abstraction layer, creates tight coupling

**Example: Security Guard Authentication Module**
```python
# ❌ ANTI-PATTERN: Accesses adapter directly
if hasattr(auth_abstraction, 'supabase'):
    supabase_result = await auth_abstraction.supabase.sign_in_with_password(...)
    access_token = supabase_result.get("access_token")
```

**Problem:**
- Bypasses abstraction layer
- Creates tight coupling to Supabase
- Makes testing harder
- Violates abstraction purpose

**Fix:**
- Services ONLY use abstractions (never adapters)
- If abstraction doesn't expose what's needed, fix abstraction (don't bypass it)
- Abstractions should expose all needed functionality

---

### Anti-Pattern 3: Services Have Business Logic 🔴

**Severity:** CRITICAL  
**Impact:** Services are not primitives, violate new architecture

**Example: Security Guard**
```python
# ❌ ANTI-PATTERN: Service has business logic
async def authenticate_user(self, credentials):
    # Resolve tenant (business logic)
    tenant_id = await self._resolve_tenant(...)
    
    # Resolve roles/permissions (business logic)
    roles, permissions = await self._resolve_roles_permissions(...)
    
    # Create SecurityContext (business object)
    return SecurityContext(...)
```

**Problem:**
- Services should be primitives (governance decisions only)
- Business logic belongs in SDK or domain services
- Creates "fat services"

**Fix:**
- Services provide governance decisions only (`evaluate_auth()` → PolicyValidationResult)
- Translation logic → Platform SDK (`resolve_security_context()` → SecurityContext)
- Business logic → Domain services (if needed)

---

### Anti-Pattern 4: No SDK Boundary Zone 🔴

**Severity:** CRITICAL  
**Impact:** No translation layer, Runtime would call Smart City directly

**Current Flow:**
```
Runtime → Smart City Service → Abstraction → Adapter
```

**Problem:**
- No translation layer
- Runtime would need to know Smart City internals
- No separation of concerns

**Fix:**
```
Runtime → Platform SDK → Smart City Role → Abstraction → Adapter
              ↓
         Translation Logic
```

**Platform SDK Responsibilities:**
- Translate runtime intents into Smart City governance checks
- Translate Smart City decisions into runtime-ready objects
- Shield Runtime from infrastructure details

---

### Anti-Pattern 5: Abstractions Return Business Objects 🔴

**Severity:** CRITICAL  
**Impact:** Abstractions are not pure infrastructure

**Example: Auth Abstraction**
```python
# ❌ ANTI-PATTERN: Returns business object
async def authenticate_user(...) -> SecurityContext:  # ❌ Business object
    return SecurityContext(...)
```

**Problem:**
- Abstractions should return raw data
- Business objects belong in SDK or domain services
- Makes abstractions not swappable

**Fix:**
- Abstractions return `Dict[str, Any]` (raw data)
- SDK creates business objects (`SecurityContext`, etc.)

---

## Moderate Anti-Patterns (Should Fix)

### Anti-Pattern 6: DI Container Dependency 🟡

**Severity:** MODERATE  
**Impact:** Creates unnecessary coupling

**Current:**
```python
# Services use DI Container to get abstractions
auth_abstraction = self.di_container.get_public_works_foundation().get_auth_abstraction()
```

**Problem:**
- Creates DI Container coupling
- Harder to test
- Less explicit

**Fix:**
- Use direct dependency injection
- Roles receive abstractions via constructor
- Cleaner, more testable

---

### Anti-Pattern 7: Micro-Modules Have Business Logic 🟡

**Severity:** MODERATE  
**Impact:** Micro-modules don't use abstractions properly

**Current:**
```python
# Micro-modules implement business logic from scratch
class Authentication:
    async def authenticate_user(self, request):
        # Custom implementation instead of using abstractions
```

**Problem:**
- Micro-modules should use abstractions
- They implement everything from scratch
- Don't leverage infrastructure abstractions

**Fix:**
- Micro-modules use abstractions (not adapters)
- Micro-modules contain organization logic only (not business logic)
- Business logic in SDK or domain services

---

### Anti-Pattern 8: Base Class Dependency 🟡

**Severity:** MODERATE  
**Impact:** Creates tight coupling to old architecture

**Current:**
```python
# Services extend SmartCityRoleBase (old architecture)
class SecurityGuardService(SmartCityRoleBase, SecurityGuardServiceProtocol):
```

**Problem:**
- Creates base class coupling
- Old architecture pattern
- Less flexible

**Fix:**
- Use `SmartCityRoleProtocol` only (protocol-based)
- No base class inheritance
- Cleaner separation

---

## Questions for Architecture Team

### Question 1: Micro-Modules Pattern

**Question:** Should we keep micro-modules in new architecture?

**Current State:**
- Services use micro-modules for organization
- Dynamic loading via mixin
- Complex, but organized

**Options:**
- **A)** Keep micro-modules, simplify (no dynamic loading, direct imports)
- **B)** Remove micro-modules, use single service file
- **C)** Keep micro-modules, but refactor to use abstractions properly

**Recommendation:** **Option A** - Keep micro-modules for organization, but:
- No dynamic loading (just organized code)
- Direct imports (not mixin-based)
- Micro-modules use abstractions (not adapters)
- Micro-modules contain organization logic only (not business logic)

**Rationale:** Micro-modules provide good organization, but need simplification.

---

### Question 2: SOA APIs and MCP Tools

**Question:** Should Smart City roles expose SOA APIs and MCP tools?

**Current State:**
- Services expose SOA APIs directly
- Services expose MCP tools directly
- Used by agents and other services

**Options:**
- **A)** Roles expose SOA APIs/MCP tools directly
- **B)** SDK exposes SOA APIs/MCP tools (wraps roles)
- **C)** Both (roles provide primitives, SDK wraps them)

**Recommendation:** **Option C** - Both:
- Roles provide primitives (governance decisions)
- SDK wraps primitives into SOA APIs and MCP tools
- Agents use SDK (not roles directly)

**Rationale:** Maintains separation (roles = primitives, SDK = exposure).

---

### Question 3: DI Container Dependency

**Question:** Should Smart City roles use DI Container?

**Current State:**
- Services use DI Container to get abstractions
- Creates coupling

**Options:**
- **A)** Keep DI Container (current pattern)
- **B)** Use direct dependency injection (cleaner)

**Recommendation:** **Option B** - Direct dependency injection:
- Roles receive abstractions via constructor
- Cleaner, more testable
- No DI Container coupling

**Rationale:** Direct injection is cleaner and more testable.

---

### Question 4: Base Classes

**Question:** Should we keep `SmartCityRoleBase`?

**Current State:**
- Services extend `SmartCityRoleBase` (old architecture)
- Provides utilities, logging, etc.

**Options:**
- **A)** Keep base class (utilities, logging)
- **B)** Use protocol only (no base class)

**Recommendation:** **Option B** - Protocol only:
- Use `SmartCityRoleProtocol` only
- No base class inheritance
- Utilities via direct imports (not base class)

**Rationale:** Protocol-based is cleaner and more flexible.

---

### Question 5: State Management

**Question:** Should Smart City roles manage state?

**Current State:**
- Some services manage internal state (sessions, policies, etc.)

**Options:**
- **A)** Roles manage state (current pattern)
- **B)** Runtime owns all state (roles are stateless)

**Recommendation:** **Option B** - Runtime owns state:
- Roles are stateless primitives
- Runtime manages all state
- Roles observe Runtime (via observer pattern)

**Rationale:** Aligns with new architecture (Runtime owns state).

---

### Question 6: Infrastructure Access Pattern

**Question:** How should Smart City roles access abstractions?

**Current State:**
- Via `InfrastructureAccessMixin.get_infrastructure_abstraction()`
- DI Container-based

**Options:**
- **A)** Keep mixin pattern (current)
- **B)** Direct dependency injection (cleaner)

**Recommendation:** **Option B** - Direct dependency injection:
- Roles receive abstractions via constructor
- No mixin needed
- Cleaner, more explicit

**Rationale:** Direct injection is cleaner and more explicit.

---

### Question 7: Adapter → Abstraction Flow

**Question:** Should services ever access adapters directly?

**Current State:**
- Some services access `abstraction.adapter` directly
- Bypasses abstraction layer

**Options:**
- **A)** Services can access adapters (if needed)
- **B)** Services NEVER access adapters (always use abstractions)

**Recommendation:** **Option B** - Never access adapters:
- Services ONLY use abstractions
- Abstractions hide adapter details
- If abstraction doesn't expose what's needed, fix abstraction (don't bypass it)

**Rationale:** Maintains abstraction layer integrity.

---

## Summary

**Anti-Patterns to Fix:**
- 🔴 **5 Critical** (must fix before proceeding)
- 🟡 **3 Moderate** (should fix)

**Questions to Answer:**
- **7 Questions** need architecture team answers
- **Recommendations provided** for each

**Next Steps:**
1. Review anti-patterns with architecture team
2. Get answers to questions
3. Update refactoring plan based on answers
4. Proceed with refactoring
