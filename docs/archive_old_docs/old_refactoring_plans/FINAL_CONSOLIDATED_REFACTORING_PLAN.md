# Final Consolidated Smart City & Abstractions Refactoring Plan

**Date:** January 2026  
**Status:** 📋 **FINAL REFACTORING PLAN** (Incorporates Architecture Team Feedback)  
**Purpose:** Refactor Smart City to proper Civic Systems location, refactor abstractions, and establish SDK boundary zone

---

## Executive Summary

**The Problem:**
- ❌ Smart City services exist at `symphainy_platform/smart_city/` (WRONG LOCATION)
- ✅ Should be at `symphainy_source_code/civic_systems/smart_city/` (Civic System)
- ❌ Current services may not follow new primitive pattern (policy-aware primitives)
- ❌ Abstractions have business logic that needs to move to appropriate location
- ⚠️ **Missing:** SDK as the boundary zone where translation logic lives

**The Solution:**
- ✅ **One consolidated plan** to refactor BOTH:
  1. Smart City (move to `civic_systems/smart_city/`, follow new primitive pattern)
  2. Abstractions (remove business logic, make pure)
  3. **SDK (Platform + Realm)** - where translation logic happens
- ✅ Do this together to avoid technical debt
- ✅ Then proceed with Phase 2/3 plan

**Critical Understanding:**
- **Smart City roles** = Governance decisions (what is allowed)
- **SDKs** = Translation logic (how that decision is realized)
- **Business logic removed from abstractions** = Recreated in SDKs (not Smart City roles)

---

## The Correct Layering (One Slide Worth)

### Correct Responsibility Split

| Layer                      | Owns                                         | Does NOT Own          |
| -------------------------- | -------------------------------------------- | --------------------- |
| **Public Works**           | Infrastructure access (Supabase, Redis, GCS) | Business rules        |
| **Smart City Roles**       | Governance *decisions*                       | Service orchestration |
| **SDK (Platform + Realm)** | Translation & coordination                   | Infrastructure        |
| **Runtime**                | Execution & state                            | Policy interpretation |
| **Realm Services**         | Domain work                                  | Governance            |

### The SDK: The Boundary Zone

**The SDK is the formal boundary zone that translates runtime contracts into realm/service behavior.**

**Two SDKs:**
1. **Platform SDK** (Smart City ↔ Runtime)
   - Translates runtime intents into Smart City governance checks
   - Translates Smart City decisions into runtime-ready objects
   - Shields Runtime from Supabase schemas, role resolution, tenant inference

2. **Realm SDK** (Runtime ↔ Services)
   - Translates runtime intents into realm capability invocations
   - Translates realm responses into runtime-ready artifacts
   - Shields Runtime from realm internals

**Key Principle:**
> **Business logic removed from abstractions is recreated in SDKs.**
> Smart City roles decide *what is allowed*.
> SDKs decide *how that decision is realized*.

---

## Complete Auth Flow Example (Pressure-Tested)

### The Flow: Intent → SDK → Smart City → Realm → Runtime

```
Runtime Intent
  ↓
Platform SDK (resolve_security_context)
  ├─ Calls Auth Abstraction (raw_user = authenticate())
  ├─ Calls Security Guard (decision = evaluate_auth())
  ├─ Calls City Manager (policy = validate_policy())
  ├─ Calls Tenant Abstraction (tenant_data = get_tenant())
  └─ Translates → SecurityContext (runtime-ready object)
  ↓
Runtime (uses SecurityContext)
```

### 1️⃣ Auth Abstraction (Infrastructure Only)

```python
# foundations/public_works/abstractions/auth_abstraction.py
class AuthAbstraction:
    """Pure infrastructure - returns raw data only."""
    
    async def authenticate(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Returns raw user data from provider."""
        raw_user = await self.supabase_adapter.sign_in_with_password(...)
        return {
            "id": raw_user["id"],
            "email": raw_user["email"],
            "raw_provider_data": raw_user  # No decisions, no tenants, no roles
        }
```

**Returns:** Raw user data (no decisions, no tenants, no roles)

---

### 2️⃣ Security Guard Role (Smart City - Governance Decision)

```python
# civic_systems/smart_city/roles/security_guard/security_guard_role.py
class SecurityGuardRole:
    """Governance decision - what is allowed?"""
    
    async def evaluate_auth(
        self,
        raw_user: Dict[str, Any],
        execution_context: ExecutionContext
    ) -> PolicyValidationResult:
        """
        Evaluate authentication policy.
        
        Returns: PolicyValidationResult (allowed/denied + reason)
        Does NOT create SecurityContext (that's SDK's job)
        """
        # POLICY LOGIC: Is user authenticated?
        if not raw_user:
            return PolicyValidationResult(
                allowed=False,
                reason="Invalid credentials",
                policy_applied="auth_policy"
            )
        
        return PolicyValidationResult(
            allowed=True,
            reason="User authenticated",
            policy_applied="auth_policy"
        )
```

**Returns:** Policy decision (allowed/denied) - NOT business objects

---

### 3️⃣ Platform SDK (Boundary Zone - Translation Logic)

```python
# civic_systems/platform_sdk/platform_sdk.py
class PlatformSDK:
    """
    Boundary zone - translates runtime contracts into realm/service behavior.
    
    This is where the "old auth logic" lives - correctly reframed as translation.
    """
    
    async def resolve_security_context(
        self,
        raw_user: Dict[str, Any],
        policy_decision: PolicyValidationResult,
        tenant_hint: Optional[str],
        solution_context: Optional[Dict[str, Any]]
    ) -> SecurityContext:
        """
        Resolve security context - TRANSLATION LOGIC.
        
        This is where:
        - Tenant is resolved (how tenant is determined)
        - Roles are mapped (how roles are extracted)
        - Permissions are projected (how permissions are calculated)
        - SecurityContext is created (runtime-ready object)
        """
        # Call City Manager if tenant creation needed
        if not tenant_hint and solution_context.get("auto_create_tenant"):
            tenant_data = await self.city_manager.create_tenant(...)
        else:
            tenant_data = await self.tenant_abstraction.get_tenant(...)
        
        # Call Tenant Abstraction for tenant data
        tenant_info = await self.tenant_abstraction.get_user_tenant_info(
            raw_user["id"]
        )
        
        # TRANSLATION LOGIC: How roles are mapped
        roles = self._map_roles(raw_user, tenant_info)
        
        # TRANSLATION LOGIC: How permissions are projected
        permissions = self._project_permissions(roles, tenant_info)
        
        # Create runtime-ready SecurityContext
        return SecurityContext(
            user_id=raw_user["id"],
            tenant_id=tenant_info["tenant_id"],
            email=raw_user["email"],
            roles=roles,
            permissions=permissions,
            access_token=raw_user.get("access_token"),
            # ... other fields
        )
```

**Returns:** Runtime-ready `SecurityContext` (translation, not governance)

---

### 4️⃣ Runtime (Uses the Result)

```python
# runtime/runtime_service.py
class RuntimeService:
    """Runtime uses the result, not the process."""
    
    async def execute_intent(self, intent: Intent):
        # Platform SDK translates intent into runtime-ready objects
        security_context = await self.platform_sdk.resolve_security_context(
            raw_user=raw_user,
            policy_decision=policy_decision,
            tenant_hint=intent.tenant_id,
            solution_context=intent.solution_context
        )
        
        # Runtime just uses it
        execution_context.security = security_context
        # Runtime does NOT care:
        # - how tenant was resolved
        # - where roles came from
        # - which auth provider was used
```

**Key Point:** Runtime does NOT care about the translation process

---

## Curator-Specific Clarification

### Curator is a Smart City Role

**Curator:**
- Owns **registries as libraries** (Supabase)
- Observes **infrastructure liveness** (Consul)
- Produces a **runtime registry view**
- Is accessed **only via SDK**, not SOA APIs

**Critical Rule:**
> **Runtime never talks to Consul or registries directly.**
> Runtime always goes through **Curator SDK calls**.

**Example:**
```python
# ❌ WRONG: Runtime talks to Consul directly
consul_client = ConsulClient()
services = consul_client.get_services()

# ✅ CORRECT: Runtime uses Curator via SDK
curator_sdk = platform_sdk.get_curator_sdk()
capabilities = await curator_sdk.discover_capabilities(intent_type)
```

---

## Implementation Plan

### Week 1: Smart City Migration + Critical Abstractions + SDK Foundation

**Day 1-2: Assessment**
- [ ] Assess current Smart City services
- [ ] Inventory abstraction business logic
- [ ] Create detailed migration map:
  - Policy logic → Smart City roles
  - Translation logic → SDKs
  - Business logic → Domain services

**Day 3: Security Guard + Auth Abstraction + Platform SDK**
- [ ] Create `civic_systems/smart_city/roles/security_guard/`
- [ ] Move Security Guard to new location
- [ ] Refactor to provide governance decisions (`evaluate_auth()`)
- [ ] Move policy logic from Auth Abstraction to Security Guard
- [ ] **Create Platform SDK foundation** (`civic_systems/platform_sdk/`)
- [ ] **Move translation logic to Platform SDK** (`resolve_security_context()`)
- [ ] Refactor Auth Abstraction to be pure (returns raw data only)

**Day 4: City Manager + Tenant Abstraction + Platform SDK**
- [ ] Create `civic_systems/smart_city/roles/city_manager/`
- [ ] Move City Manager to new location
- [ ] Refactor to provide policy primitives
- [ ] Move policy logic from Tenant Abstraction to City Manager/Security Guard
- [ ] **Move translation logic to Platform SDK** (`resolve_tenant()`)
- [ ] Refactor Tenant Abstraction to be pure

**Day 5: Data Steward + Content Metadata Abstraction + Realm SDK**
- [ ] Create `civic_systems/smart_city/roles/data_steward/`
- [ ] Move Data Steward to new location
- [ ] Refactor to provide policy primitives (data boundaries, contracts)
- [ ] **Create Realm SDK foundation** (`civic_systems/platform_sdk/realm_sdk.py`)
- [ ] **Move translation logic to Realm SDK** (`translate_content_intent()`)
- [ ] Move business logic from Content Metadata Abstraction to Content Realm
- [ ] Refactor Content Metadata Abstraction to be pure

### Week 2: Remaining Roles + Abstractions + SDK Completion

**Day 1: Librarian + Semantic Abstractions + Realm SDK**
- [ ] Move Librarian to `civic_systems/smart_city/roles/librarian/`
- [ ] Refactor to provide semantic primitives
- [ ] Move translation logic from Semantic Abstractions to Realm SDK
- [ ] Move business logic from Semantic Abstractions to Content Realm
- [ ] Refactor Semantic Abstractions to be pure

**Day 2: Conductor + Workflow Abstraction + Realm SDK**
- [ ] Move Conductor to `civic_systems/smart_city/roles/conductor/`
- [ ] Refactor to provide workflow primitives
- [ ] Move translation logic from Workflow Abstraction to Realm SDK
- [ ] Move business logic from Workflow Abstraction to Journey Realm
- [ ] Refactor Workflow Abstraction to be pure

**Day 3: Remaining Roles + Curator**
- [ ] Move Traffic Cop, Post Office, Nurse to `civic_systems/smart_city/roles/`
- [ ] Refactor to provide primitives
- [ ] **Ensure Curator is a Smart City role** (accessed via SDK)
- [ ] Move any remaining translation logic to SDKs

**Day 4-5: Validation & Testing**
- [ ] Run all validation tests
- [ ] Ensure Runtime calls Smart City via SDK (not directly)
- [ ] Ensure Runtime calls Curator via SDK (not Consul directly)
- [ ] Fix any issues
- [ ] Update documentation

---

## Success Criteria

### ✅ Smart City Refactoring

- [ ] All roles moved to `civic_systems/smart_city/roles/`
- [ ] All roles implement `SmartCityRoleProtocol`
- [ ] All roles provide governance decisions (not translation logic)
- [ ] All roles use abstractions (not adapters)
- [ ] Curator is a Smart City role (accessed via SDK)
- [ ] All imports updated

### ✅ SDK Refactoring

- [ ] Platform SDK created (`civic_systems/platform_sdk/`)
- [ ] Realm SDK created (`civic_systems/platform_sdk/realm_sdk.py`)
- [ ] Translation logic moved to SDKs (from abstractions)
- [ ] SDKs translate Smart City decisions into runtime objects
- [ ] SDKs shield Runtime from infrastructure details

### ✅ Abstraction Refactoring

- [ ] All abstractions return raw data (not business objects)
- [ ] Policy logic moved to Smart City roles
- [ ] Translation logic moved to SDKs
- [ ] Business logic moved to domain services
- [ ] All abstractions are swappable
- [ ] All abstractions comply with protocols

### ✅ Integration

- [ ] Runtime calls Smart City roles via SDK (not directly)
- [ ] Runtime calls Curator via SDK (not Consul directly)
- [ ] Domain services use Smart City primitives via SDK
- [ ] Domain services use abstractions via SDK
- [ ] End-to-end flows work (Intent → SDK → Smart City → Realm → Runtime)
- [ ] All tests pass

---

## Why This Matters

If the SDK is not explicitly named as the translation layer:

* Smart City roles grow orchestration logic
* Runtime becomes policy-aware (bad)
* Abstractions get polluted again (inevitable)

By explicitly placing logic in the SDK:

* Public Works stays swappable
* Smart City stays declarative
* Runtime stays deterministic
* Realm services stay ignorant (in a good way)

---

## Conclusion

**This final approach:**
- ✅ Moves Smart City to correct location (`civic_systems/smart_city/`)
- ✅ Follows new primitive pattern (policy-aware primitives)
- ✅ Separates policy logic (Smart City) from translation logic (SDK)
- ✅ Makes abstractions pure infrastructure
- ✅ Establishes SDK as boundary zone
- ✅ Sets us up for Phase 2/3 success

**Timeline:** 2 weeks for complete refactoring

**Then:** Proceed with Phase 2/3 plan with clean foundation
