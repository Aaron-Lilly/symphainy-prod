# Corrected Consolidated Smart City & Abstractions Refactoring Plan

**Date:** January 2026  
**Status:** 📋 **CORRECTED REFACTORING PLAN**  
**Purpose:** Refactor Smart City to proper Civic Systems location AND refactor abstractions together

---

## Executive Summary

**The Problem:**
- ❌ Smart City services exist at `symphainy_platform/smart_city/` (WRONG LOCATION)
- ✅ Should be at `symphainy_source_code/civic_systems/smart_city/` (Civic System)
- ❌ Current services may not follow new primitive pattern (policy-aware primitives)
- ❌ Abstractions have business logic that needs to move to appropriate location
- ⚠️ **Risk:** If we dump abstraction business logic into Smart City roles, they become "fat services"
- ⚠️ **Missing:** SDK as the boundary zone where business logic translation happens

**The Solution:**
- ✅ **One consolidated plan** to refactor BOTH:
  1. Smart City (move to `civic_systems/smart_city/`, follow new primitive pattern)
  2. Abstractions (remove business logic, make pure)
  3. **SDK (Platform + Realm)** - where business logic translation happens
- ✅ Do this together to avoid technical debt
- ✅ Then proceed with Phase 2/3 plan

**Critical Understanding:**
- **Smart City roles** = Governance decisions (what is allowed)
- **SDKs** = Translation logic (how that decision is realized)
- **Business logic removed from abstractions** = Recreated in SDKs (not Smart City roles)

---

## Critical Understanding: The Correct Layering

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

### Smart City as Civic System

**Smart City is a Civic System:**
- One of 4 Civic Systems: Smart City, Experience, Agentic, Platform SDK
- Location: `civic_systems/smart_city/`
- Purpose: Governance (how execution is allowed to occur)
- Pattern: Policy-aware primitives consumed by Runtime **via SDK**

**Smart City Roles:**
- They are **governance decisions** (what is allowed)
- They **do NOT orchestrate services**
- They **do NOT translate logic**
- They **expose primitives** (sessions, events, workflows, etc.)
- Runtime **calls via SDK**, not directly

**Key Principle:**
> **Smart City governs *how* execution is allowed to occur.**
> It never decides *what* should happen or *why*.
> It never translates decisions into runtime objects.

---

## Current State Analysis

### Smart City Current Location (WRONG)

**Location:** `symphainy_platform/smart_city/` ❌ **WRONG LOCATION**

**What Exists:**
- Smart City services exist at `symphainy_platform/smart_city/services/`
- Foundation service exists
- Protocols exist
- **May not follow new primitive pattern** (need to assess)
- **May have business logic** (should be in domain services, not Smart City)

### Smart City Target Location (CORRECT)

**Location:** `symphainy_source_code/civic_systems/smart_city/` ✅ **CORRECT LOCATION**

**Target Structure:**
```
civic_systems/
├── smart_city/
│   ├── __init__.py
│   ├── foundation_service.py          # Smart City Foundation
│   ├── roles/                          # Smart City Roles (primitives)
│   │   ├── security_guard/
│   │   │   ├── __init__.py
│   │   │   ├── security_guard_role.py  # Policy-aware primitive
│   │   │   └── README.md
│   │   ├── city_manager/
│   │   ├── data_steward/
│   │   ├── librarian/
│   │   ├── traffic_cop/
│   │   ├── post_office/
│   │   ├── conductor/
│   │   └── nurse/
│   └── protocols/
│       └── smart_city_role_protocol.py
├── experience/
├── agentic/
└── platform_sdk/
```

---

## What Smart City Roles Actually Are (From Phase 3)

### Smart City Roles = Policy-Aware Primitives

**NOT Business Logic:**
- ❌ They do NOT create tenants (that's domain logic)
- ❌ They do NOT extract roles (that's domain logic)
- ❌ They do NOT validate business rules (that's domain logic)

**They ARE Primitives:**
- ✅ They provide **policy-aware primitives** (sessions, events, workflows)
- ✅ They **enforce policy** (can this execution proceed?)
- ✅ They **observe execution** (via observer pattern)
- ✅ Runtime **calls them** for primitives

### Example: Security Guard Role

**What Security Guard DOES:**
```python
class SecurityGuardRole:
    """Policy-aware primitive for identity/authN/Z."""
    
    async def validate_auth(
        self,
        execution_context: ExecutionContext
    ) -> PolicyValidationResult:
        """
        Validate authentication/authorization.
        
        Returns: PolicyValidationResult (allowed/denied + reason)
        """
        # Use Auth Abstraction (pure infrastructure)
        raw_user_data = await self.auth_abstraction.validate_token(...)
        
        # BUSINESS LOGIC: Resolve tenant, roles, permissions
        # This is NOT in Security Guard - this is in domain service!
        # Security Guard only validates: "Is this user authenticated?"
        
        return PolicyValidationResult(
            allowed=True,
            reason="User authenticated",
            policy_applied="auth_policy"
        )
    
    async def get_security_context(
        self,
        execution_context: ExecutionContext
    ) -> SecurityContext:
        """
        Provide security context primitive.
        
        Runtime calls this to get security context.
        """
        # Use abstractions to get raw data
        # Apply business logic to create SecurityContext
        # Return primitive
```

**What Security Guard DOES NOT DO:**
- ❌ Create tenants (that's City Manager or domain service)
- ❌ Extract roles from metadata (that's domain logic)
- ❌ Make business decisions (that's domain logic)

---

## Corrected Refactoring Strategy

### Phase 1: Inventory & Assessment (Week 1, Days 1-2)

**Goal:** Understand what exists and what needs to change

**Tasks:**

1. **Inventory Current Smart City Services**
   - [ ] List all services in `symphainy_platform/smart_city/services/`
   - [ ] Document current structure
   - [ ] Identify what follows new primitive pattern vs. what doesn't
   - [ ] Identify what business logic exists (should be in domain services)

2. **Inventory Abstractions**
   - [ ] List all abstractions with business logic
   - [ ] Map business logic to appropriate location:
     - **Policy logic** → Smart City roles (primitives)
     - **Business logic** → Domain services (Content, Insights, Journey, Solution)
   - [ ] Document what needs to move where

3. **Create Migration Map**
   - [ ] Map: Current Smart City → Target Smart City (civic_systems)
   - [ ] Map: Abstraction Business Logic → Smart City Role OR Domain Service
   - [ ] Identify dependencies

---

### Phase 2: Smart City Migration & Refactoring (Week 1, Days 3-5)

**Goal:** Move Smart City to correct location and follow new primitive pattern

**Tasks:**

1. **Create Target Structure**
   - [ ] Create `civic_systems/smart_city/` directory
   - [ ] Create `civic_systems/smart_city/roles/` directory
   - [ ] Create role directories (security_guard, city_manager, etc.)
   - [ ] Create protocol files

2. **Refactor Each Smart City Role**
   - [ ] Move from `symphainy_platform/smart_city/services/` to `civic_systems/smart_city/roles/`
   - [ ] Update to follow new primitive pattern:
     - Implement `SmartCityRoleProtocol` (policy-aware primitives)
     - Use abstractions (not adapters)
     - Provide primitives (sessions, events, workflows, etc.)
     - Enforce policy (validate, not decide)
   - [ ] Remove business logic (move to domain services)
   - [ ] Update imports

3. **Update Foundation Service**
   - [ ] Move to `civic_systems/smart_city/foundation_service.py`
   - [ ] Update to initialize roles (not services)
   - [ ] Update imports

4. **Update Dependencies**
   - [ ] Update all imports (Runtime, Experience, etc.)
   - [ ] Update foundation services
   - [ ] Update Runtime integration

---

### Phase 3: Abstraction Refactoring (Week 2, Days 1-5)

**Goal:** Remove business logic from abstractions, move to appropriate location

**Tasks:**

1. **For Each Abstraction:**
   - [ ] Identify business logic
   - [ ] Determine where it belongs:
     - **Policy logic** → Smart City role (primitive)
     - **Business logic** → Domain service
   - [ ] Move business logic to appropriate location
   - [ ] Update abstraction to return raw data
   - [ ] Test abstraction is pure

2. **Update Smart City Roles:**
   - [ ] Add policy logic (if needed)
   - [ ] Use abstractions (not adapters)
   - [ ] Provide primitives only
   - [ ] Test roles provide primitives

3. **Update Domain Services:**
   - [ ] Add business logic from abstractions
   - [ ] Use Smart City roles for primitives
   - [ ] Use abstractions for infrastructure
   - [ ] Test business logic works

---

## Corrected Business Logic Mapping

### Policy Logic → Smart City Roles (Governance Decisions)

| Abstraction | Policy Logic | Smart City Role | What Role Provides |
|------------|--------------|----------------|-------------------|
| Auth Abstraction | Auth validation | Security Guard | `evaluate_auth()` - Is user allowed? |
| Tenant Abstraction | Access validation | Security Guard | `validate_tenant_access()` - Can user access tenant? |
| Tenant Abstraction | Policy enforcement | City Manager | `validate_policy()` - Is execution allowed? |
| Session Abstraction | Session semantics | Traffic Cop | `get_session()` - Session primitive |
| Event Management Abstraction | Event routing | Post Office | `publish_event()` - Event primitive |
| Workflow Orchestration Abstraction | Workflow primitives | Conductor | `get_saga_primitives()` - Workflow primitive |

### Translation Logic → SDKs (Boundary Zone)

| Abstraction | Translation Logic | SDK | What SDK Does |
|------------|-------------------|-----|--------------|
| Auth Abstraction | Tenant resolution | Platform SDK | `resolve_security_context()` - How tenant is resolved |
| Auth Abstraction | Role mapping | Platform SDK | `resolve_security_context()` - How roles are mapped |
| Auth Abstraction | Permission projection | Platform SDK | `resolve_security_context()` - How permissions are projected |
| Auth Abstraction | SecurityContext creation | Platform SDK | `resolve_security_context()` - Creates runtime-ready SecurityContext |
| Tenant Abstraction | Tenant creation logic | Platform SDK | `resolve_tenant()` - Whether tenant is auto-created (demo vs prod) |
| Content Metadata Abstraction | ID generation | Realm SDK | `translate_content_intent()` - How content IDs are generated |
| Content Metadata Abstraction | Validation rules | Realm SDK | `translate_content_intent()` - How content is validated |

### Business Logic → Domain Services

| Abstraction | Business Logic | Domain Service | What Service Does |
|------------|----------------|----------------|------------------|
| Content Metadata Abstraction | Content processing | Content Realm | Processes content (domain logic) |
| Semantic Search Abstraction | Document processing | Content Realm | Processes documents (domain logic) |
| Workflow Orchestration Abstraction | Workflow execution | Journey Realm | Executes workflows (domain logic) |

---

## Corrected Architecture: Complete Auth Flow Example

### The Complete Flow (Intent → SDK → Smart City → Realm → Runtime)

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
    
    def _map_roles(self, raw_user: Dict, tenant_info: Dict) -> List[str]:
        """Translation: How roles are extracted from raw data."""
        # This is the "old auth logic" - now in SDK
        return tenant_info.get("roles", [])
    
    def _project_permissions(self, roles: List[str], tenant_info: Dict) -> List[str]:
        """Translation: How permissions are calculated from roles."""
        # This is the "old auth logic" - now in SDK
        permissions = []
        for role in roles:
            permissions.extend(self._get_permissions_for_role(role))
        return permissions
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

## Corrected Migration Map

### Smart City Location Migration

| Current Location | Target Location | Status |
|-----------------|----------------|--------|
| `symphainy_platform/smart_city/services/security_guard/` | `civic_systems/smart_city/roles/security_guard/` | ⏳ TODO |
| `symphainy_platform/smart_city/services/city_manager/` | `civic_systems/smart_city/roles/city_manager/` | ⏳ TODO |
| `symphainy_platform/smart_city/services/data_steward/` | `civic_systems/smart_city/roles/data_steward/` | ⏳ TODO |
| `symphainy_platform/smart_city/services/librarian/` | `civic_systems/smart_city/roles/librarian/` | ⏳ TODO |
| `symphainy_platform/smart_city/services/traffic_cop/` | `civic_systems/smart_city/roles/traffic_cop/` | ⏳ TODO |
| `symphainy_platform/smart_city/services/post_office/` | `civic_systems/smart_city/roles/post_office/` | ⏳ TODO |
| `symphainy_platform/smart_city/services/conductor/` | `civic_systems/smart_city/roles/conductor/` | ⏳ TODO |
| `symphainy_platform/smart_city/services/nurse/` | `civic_systems/smart_city/roles/nurse/` | ⏳ TODO |
| `symphainy_platform/smart_city/foundation_service.py` | `civic_systems/smart_city/foundation_service.py` | ⏳ TODO |

### Business Logic Migration

| Abstraction | Business Logic | Target Location | Type |
|------------|----------------|----------------|------|
| Auth Abstraction | Auth validation | Security Guard Role | Policy Logic (Primitive) |
| Auth Abstraction | Tenant creation | City Manager Role OR Domain Service | Business Logic |
| Auth Abstraction | Role extraction | Domain Service | Business Logic |
| Auth Abstraction | SecurityContext creation | Domain Service | Business Logic |
| Tenant Abstraction | Access validation | Security Guard Role | Policy Logic (Primitive) |
| Tenant Abstraction | Configuration management | City Manager Role | Policy Logic (Primitive) |
| Content Metadata Abstraction | ID generation | Content Realm | Business Logic |
| Content Metadata Abstraction | Validation rules | Content Realm | Business Logic |
| Semantic Search Abstraction | Document ID generation | Content Realm | Business Logic |

---

## Corrected Implementation Order

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

### Week 2: Remaining Roles + Abstractions

**Day 1: Librarian + Semantic Abstractions**
- [ ] Move Librarian to `civic_systems/smart_city/roles/librarian/`
- [ ] Refactor to provide semantic primitives
- [ ] Move business logic from Semantic Abstractions to Content Realm
- [ ] Refactor Semantic Abstractions to be pure

**Day 2: Conductor + Workflow Abstraction**
- [ ] Move Conductor to `civic_systems/smart_city/roles/conductor/`
- [ ] Refactor to provide workflow primitives
- [ ] Move business logic from Workflow Abstraction to Journey Realm
- [ ] Refactor Workflow Abstraction to be pure

**Day 3: Remaining Roles**
- [ ] Move Traffic Cop, Post Office, Nurse to `civic_systems/smart_city/roles/`
- [ ] Refactor to provide primitives
- [ ] Move any remaining business logic

**Day 4-5: Validation & Testing**
- [ ] Run all validation tests
- [ ] Fix any issues
- [ ] Update documentation

---

## Critical Distinction: Policy Logic vs. Translation Logic vs. Business Logic

### Policy Logic → Smart City Roles (Governance Decisions)

**Policy Logic Examples:**
- "Is this user authenticated?" → Security Guard (`evaluate_auth()`)
- "Can this user access this tenant?" → Security Guard (`validate_tenant_access()`)
- "Is this execution allowed by policy?" → City Manager (`validate_policy()`)
- "Can this data be accessed?" → Data Steward (`validate_data_access()`)

**Pattern:**
- Returns `PolicyValidationResult` (governance decision)
- Runtime calls via SDK for validation
- Does NOT orchestrate services
- Does NOT translate decisions

### Translation Logic → SDKs (Boundary Zone)

**Translation Logic Examples:**
- "How is tenant resolved?" → Platform SDK (`resolve_security_context()`)
- "How are roles mapped?" → Platform SDK (`resolve_security_context()`)
- "How are permissions projected?" → Platform SDK (`resolve_security_context()`)
- "How is SecurityContext created?" → Platform SDK (`resolve_security_context()`)
- "How is content intent translated?" → Realm SDK (`translate_content_intent()`)

**Pattern:**
- Returns runtime-ready objects (`SecurityContext`, `Intent`, etc.)
- Translates Smart City decisions into runtime objects
- Calls Smart City roles for governance
- Calls abstractions for infrastructure
- **This is where "old auth logic" lives - correctly reframed**

### Business Logic → Domain Services

**Business Logic Examples:**
- "How is content processed?" → Content Realm
- "How are workflows executed?" → Journey Realm
- "How are insights generated?" → Insights Realm

**Pattern:**
- Returns domain objects (`Content`, `Workflow`, etc.)
- Domain services make business decisions
- Uses Smart City primitives (via SDK) for policy validation
- Uses abstractions (via SDK) for infrastructure

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

## Conclusion

**This corrected approach:**
- ✅ Moves Smart City to correct location (`civic_systems/smart_city/`)
- ✅ Follows new primitive pattern (policy-aware primitives)
- ✅ Separates policy logic (Smart City) from business logic (Domain Services)
- ✅ Makes abstractions pure infrastructure
- ✅ Sets us up for Phase 2/3 success

**Timeline:** 2 weeks for complete refactoring

**Then:** Proceed with Phase 2/3 plan with clean foundation
