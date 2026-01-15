# Security Guard Refactoring Plan - Complete Analysis & Implementation

**Date:** January 2026  
**Status:** 📋 **COMPREHENSIVE PLAN**  
**Goal:** Refactor Security Guard to new architecture with better security than `/symphainy_source/`

---

## Part 1: Expert Analysis of Current Security Implementation

### 1.1 Infrastructure Layer (Supabase → Adapter → Abstraction)

#### Current Flow in `/symphainy_source/`:

```
Supabase (Technology)
  ↓
SupabaseAdapter (Layer 0 - Raw Technology)
  - sign_in_with_password()
  - sign_up_with_password()
  - validate_token_local() (JWKS)
  - get_user_tenant_info() (queries user_tenants table)
  - link_user_to_tenant()
  - create_tenant()
  ↓
AuthAbstraction (Layer 1 - HAS BUSINESS LOGIC ❌)
  - authenticate_user() → Creates SecurityContext
  - validate_token() → Creates SecurityContext
  - register_user() → Creates tenant, links user, creates SecurityContext
  - _create_tenant_for_user() → Business logic
  - Extracts roles/permissions → Business logic
  ↓
Security Guard Service (Layer 2 - HAS BUSINESS LOGIC ❌)
  - authenticate_user() → Calls AuthAbstraction, creates session
  - authorize_action() → Calls AuthorizationAbstraction
  - Direct adapter access (bypasses abstraction) ❌
```

#### Key Findings:

**✅ What Works:**
- Supabase adapter is pure (raw technology)
- JWKS local validation (fast, no network calls)
- User-tenant relationship via `user_tenants` table
- Service key for database queries

**❌ Anti-Patterns:**
1. **Auth Abstraction has business logic:**
   - Creates tenants automatically
   - Extracts roles/permissions
   - Creates SecurityContext (business object)
   - Links users to tenants

2. **Security Guard accesses adapters directly:**
   ```python
   # ❌ ANTI-PATTERN: Direct adapter access
   if hasattr(auth_abstraction, 'supabase'):
       supabase_result = await auth_abstraction.supabase.sign_in_with_password(...)
   ```

3. **Security Guard has business logic:**
   - Creates sessions
   - Orchestrates authentication flow
   - Builds user_context

4. **Authorization Abstraction has business logic:**
   - Permission checking logic
   - Tenant access validation
   - Policy enforcement decisions

---

### 1.2 Zero Trust Pattern in `/symphainy_source/`

#### Current Implementation:

**Principle:** "Secure by design, open by policy"

**Pattern:**
```python
# In realm services:
if not await self.security.check_permissions(user_context, "design_journey", "execute"):
    return {"success": False, "error": "Permission denied"}

# In orchestrators:
security = self._realm_service.get_security()
if not await security.check_permissions(user_context, "content_analysis", "execute"):
    raise PermissionError("Access denied")
```

**Security Mixin:**
```python
class SecurityMixin:
    def get_security(self):
        # Returns security provider (Security Guard API)
    
    def check_permissions(self, user_context, action, resource):
        # Delegates to Security Guard
```

**Zero Trust Characteristics:**
- ✅ Never trust, always verify
- ✅ Continuous validation
- ✅ Fail closed (deny by default)
- ❌ BUT: Business logic mixed with policy logic
- ❌ BUT: Direct adapter access bypasses abstractions

---

### 1.3 Security Guard Service Architecture

#### Current Structure:

```
SecurityGuardService
├── Micro-Modules:
│   ├── initialization.py - Security capabilities setup
│   ├── authentication.py - User authentication (HAS BUSINESS LOGIC)
│   ├── authorization_module.py - Permission checking (HAS BUSINESS LOGIC)
│   ├── orchestration.py - Policy enforcement orchestration
│   ├── soa_mcp.py - SOA API and MCP tool exposure
│   └── utilities.py - Helper functions
├── SOA APIs:
│   ├── authenticate_user()
│   ├── authorize_action()
│   ├── orchestrate_security_communication()
│   ├── orchestrate_zero_trust_policy()
│   └── orchestrate_tenant_isolation()
└── MCP Tools:
    ├── authenticate_user
    ├── authorize_action
    ├── validate_session
    └── enforce_zero_trust
```

#### Key Issues:

1. **Business Logic in Authentication Module:**
   - Creates sessions
   - Builds user_context
   - Orchestrates authentication flow

2. **Direct Adapter Access:**
   - Bypasses abstractions
   - Creates tight coupling

3. **Policy Logic Mixed with Business Logic:**
   - Authorization decisions mixed with permission extraction
   - Tenant validation mixed with tenant creation

---

## Part 2: New Architecture Design

### 2.1 Separation of Concerns

#### Three-Way Split:

1. **Public Works Abstractions (Pure Infrastructure):**
   - Return raw data only (Dict[str, Any])
   - No business logic
   - No business objects (SecurityContext)
   - Swappable (Supabase → Auth0 → AWS Cognito)

2. **Platform SDK (Translation Logic):**
   - Translates raw data → SecurityContext
   - Resolves tenant from raw data
   - Extracts roles/permissions from raw data
   - Creates business objects
   - Coordinates Smart City governance decisions

3. **Security Guard Primitive (Policy Logic):**
   - Policy decisions only (allowed/denied)
   - No business logic
   - No translation logic
   - Uses Platform SDK for translation
   - Uses abstractions for infrastructure

---

### 2.2 New Flow

```
Supabase (Technology)
  ↓
SupabaseAdapter (Layer 0 - Raw Technology)
  - sign_in_with_password() → Returns raw data
  - get_user_tenant_info() → Returns raw data
  ↓
AuthAbstraction (Layer 1 - Pure Infrastructure ✅)
  - authenticate() → Returns Dict[str, Any] (raw data)
  - validate_token() → Returns Dict[str, Any] (raw data)
  - register_user() → Returns Dict[str, Any] (raw data)
  ↓
Platform SDK (Translation Layer ✅)
  - resolve_security_context() → Translates raw data to SecurityContext
  - authenticate_and_resolve_context() → Convenience method
  - validate_token_and_resolve_context() → Convenience method
  ↓
Security Guard Primitive (Policy Layer ✅)
  - evaluate_auth() → Policy decision (allowed/denied)
  - validate_tenant_access() → Policy decision
  - check_permission() → Policy decision
  ↓
Runtime / Realm Services
  - Use Security Guard for policy decisions
  - Use Platform SDK for translation
```

---

## Part 2.5: Review Board Alignment

### Key Updates Based on Review Board Feedback

1. **Libraries vs Registries:**
   - **Libraries** = Code-level interfaces (imported, versioned)
   - **Registries** = Data-backed catalogs (queried at runtime)
   - Smart City SDK = Library (imported by Realms)
   - Policy Registry = Registry (queried by SDK/primitives)

2. **Structure Changes:**
   - Smart City primitives → `civic_systems/smart_city/primitives/`
   - Smart City SDK → `civic_systems/smart_city/sdk/`
   - Policy Registry → `civic_systems/smart_city/registries/policy_registry.py`
   - Curator SDK → `civic_systems/curator/sdk/`

3. **MCP Tools Decision:**
   - MCP tools stay in Agentic SDK (never visible to Runtime)
   - Runtime only sees agent conclusions, not tools

4. **Smart City Primitives:**
   - Pure primitives (no side effects, no infra calls)
   - Only observe, validate, emit allow/deny/annotate
   - Called only by Runtime (later)

5. **Smart City SDK:**
   - Boundary zone for Realms
   - Translates Realm intent → runtime contract shape
   - Calls Public Works abstractions
   - Queries Policy Registry
   - Never executes anything

---

## Part 3: Detailed Refactoring Plan

### 3.1 Public Works Structure Changes

#### 3.1.1 Auth Abstraction (Already Done ✅)

**Current State:** Returns raw data only

**Methods:**
- `authenticate()` → Returns `Dict[str, Any]` with raw auth data
- `validate_token()` → Returns `Dict[str, Any]` with raw validation data
- `refresh_token()` → Returns `Dict[str, Any]` with raw refresh data
- `register_user()` → Returns `Dict[str, Any]` with raw registration data

**No Changes Needed** - Already refactored ✅

---

#### 3.1.2 Tenant Abstraction (Needs Refactoring)

**Current State:** Has business logic (access validation, config management)

**Changes Needed:**

1. **Add `get_user_tenant_info()` to Protocol:**
   ```python
   class TenancyProtocol(Protocol):
       async def get_user_tenant_info(self, user_id: str) -> Optional[Dict[str, Any]]:
           """Get user's tenant information from database."""
           ...
   ```

2. **Implement in Tenant Abstraction:**
   ```python
   async def get_user_tenant_info(self, user_id: str) -> Optional[Dict[str, Any]]:
       """Get user's tenant information - returns raw data only."""
       # Use Supabase adapter to query user_tenants table
       result = await self.supabase.get_user_tenant_info(user_id)
       # Return raw data - no business logic
       return result
   ```

3. **Remove Business Logic:**
   - Remove `validate_tenant_access()` (move to Security Guard)
   - Remove `get_tenant_config()` (move to City Manager or Platform SDK)
   - Keep only pure infrastructure methods

**Result:** Pure infrastructure abstraction ✅

---

#### 3.1.3 Authorization Abstraction (Needs Refactoring)

**Current State:** Has business logic (permission checking, policy enforcement)

**Changes Needed:**

1. **Refactor to Return Raw Data:**
   ```python
   async def check_permission(
       self,
       user_id: str,
       permission: str,
       resource: Optional[str] = None
   ) -> Dict[str, Any]:
       """Check permission - returns raw data only."""
       # Query Supabase for user permissions
       # Return raw permission data
       return {
           "has_permission": bool,
           "raw_permission_data": Dict[str, Any],
           "raw_user_data": Dict[str, Any]
       }
   ```

2. **Remove Policy Logic:**
   - Remove `enforce()` method (move to Security Guard)
   - Remove policy engine integration (move to Security Guard)
   - Keep only raw permission data retrieval

**Result:** Pure infrastructure abstraction ✅

---

### 3.2 Smart City SDK (UPDATED per Review Board)

#### 3.2.1 Location (UPDATED)

**Target:** `civic_systems/smart_city/sdk/security_sdk.py`

**Purpose:** Boundary zone for Realms - translates Realm intent → runtime contract shape

#### 3.2.2 Current State

**Already Created (Platform SDK):**
- `resolve_security_context()` - Translates raw auth data to SecurityContext
- `authenticate_and_resolve_context()` - Convenience method
- `validate_token_and_resolve_context()` - Convenience method

**Note:** Platform SDK is the translation layer. Smart City SDK is the boundary zone for Realms.

#### 3.2.3 Smart City SDK Methods Needed

**Smart City SDK Methods (Boundary Zone for Realms):**

```python
class SecuritySDK:
    """
    Security SDK - Boundary zone for Realms.
    
    Translates Realm intent → runtime contract shape.
    Queries Policy Registry.
    Calls Public Works abstractions.
    Never executes anything.
    """
    
    def __init__(
        self,
        platform_sdk: PlatformSDK,
        policy_registry: PolicyRegistry,
        auth_abstraction: AuthenticationProtocol,
        tenant_abstraction: TenancyProtocol
    ):
        self.platform_sdk = platform_sdk
        self.policy_registry = policy_registry
        self.auth_abstraction = auth_abstraction
        self.tenant_abstraction = tenant_abstraction
    
    async def ensure_user_can(
        self,
        action: str,
        tenant_id: str,
        user_id: str,
        resource: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ensure user can perform action.
        
        Boundary zone method for Realms.
        - Queries Policy Registry
        - Prepares context for Runtime
        - Does NOT call primitives directly
        """
        # Query Policy Registry for policy rules
        policy_rules = await self.policy_registry.get_policy_rules(
            action=action,
            tenant_id=tenant_id,
            resource=resource
        )
        
        # Get user context (via Platform SDK translation)
        raw_auth_data = await self.auth_abstraction.get_user_info(user_id)
        security_context = await self.platform_sdk.resolve_security_context(raw_auth_data)
        
        # Prepare runtime contract shape
        return {
            "action": action,
            "resource": resource,
            "security_context": security_context,
            "policy_rules": policy_rules,
            "ready_for_runtime": True
        }
    
    async def validate_tenant_access(
        self,
        user_tenant_id: str,
        resource_tenant_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Validate tenant access.
        
        Boundary zone method for Realms.
        """
        # Query Policy Registry for tenant isolation rules
        isolation_rules = await self.policy_registry.get_tenant_isolation_rules(
            tenant_id=user_tenant_id
        )
        
        # Get tenant info (via abstraction)
        tenant_info = await self.tenant_abstraction.get_user_tenant_info(user_id)
        
        # Prepare runtime contract shape
        return {
            "user_tenant_id": user_tenant_id,
            "resource_tenant_id": resource_tenant_id,
            "isolation_rules": isolation_rules,
            "tenant_info": tenant_info,
            "ready_for_runtime": True
        }
```

**Result:** Boundary zone for Realms ✅

---

### 3.3 Security Guard Primitive Implementation

#### 3.3.1 Location (UPDATED per Review Board)

**Target:** `civic_systems/smart_city/primitives/security_guard/`

**Structure:**
```
civic_systems/smart_city/primitives/security_guard/
├── __init__.py
├── security_guard_primitive.py
├── protocols/
│   └── security_guard_protocol.py
└── README.md
```

**Key Principle:** Primitive is pure - no side effects, no infra calls, only policy decisions.

---

#### 3.3.2 Protocol Definition

```python
from typing import Protocol, Dict, Any, Optional
from symphainy_platform.foundations.public_works.protocols.auth_protocol import SecurityContext

class SecurityGuardProtocol(Protocol):
    """
    Protocol for Security Guard primitive.
    
    Policy decisions only - no business logic, no translation logic.
    """
    
    async def evaluate_auth(
        self,
        security_context: SecurityContext,
        action: str,
        resource: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluate authentication policy.
        
        Returns:
            {
                "allowed": bool,
                "reason": str,
                "policy_decision": str  # "allowed", "denied", "requires_mfa", etc.
            }
        """
        ...
    
    async def validate_tenant_access(
        self,
        user_tenant_id: str,
        resource_tenant_id: str,
        security_context: SecurityContext
    ) -> Dict[str, Any]:
        """
        Validate tenant access policy.
        
        Returns:
            {
                "allowed": bool,
                "reason": str,
                "isolation_level": str  # "strict", "relaxed", "shared"
            }
        """
        ...
    
    async def check_permission(
        self,
        security_context: SecurityContext,
        permission: str,
        resource: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Check permission policy.
        
        Returns:
            {
                "allowed": bool,
                "reason": str,
                "permission_source": str  # "role", "explicit", "inherited"
            }
        """
        ...
    
    async def enforce_zero_trust(
        self,
        security_context: SecurityContext,
        action: str,
        resource: str
    ) -> Dict[str, Any]:
        """
        Enforce zero-trust policy.
        
        Returns:
            {
                "allowed": bool,
                "reason": str,
                "verification_required": List[str]  # ["mfa", "device", "location"]
            }
        """
        ...
```

---

#### 3.3.3 Implementation

```python
from typing import Dict, Any, Optional
from utilities import get_logger

from symphainy_platform.foundations.public_works.protocols.auth_protocol import SecurityContext
from civic_systems.platform_sdk.platform_sdk import PlatformSDK
from .protocols.security_guard_protocol import SecurityGuardProtocol


class SecurityGuardPrimitive(SecurityGuardProtocol):
    """
    Security Guard Primitive - Policy-Aware Governance Role
    
    WHAT (Smart City Role): I enforce security, zero-trust, multi-tenancy
    HOW (Primitive Implementation): I make policy decisions only (pure primitive)
    
    Key Principle: Pure primitive - no side effects, no infra calls, only policy decisions.
    Called only by Runtime (later). Realms use Smart City SDK instead.
    """
    
    def __init__(
        self,
        policy_registry: PolicyRegistry
    ):
        """
        Initialize Security Guard Primitive.
        
        Args:
            policy_registry: Policy Registry for policy rules (data-backed)
        """
        self.policy_registry = policy_registry
        self.logger = get_logger(self.__class__.__name__)
        
        # Note: Policy configuration comes from Policy Registry, not hardcoded
        self.logger.info("Security Guard Primitive initialized (pure primitive)")
    
    async def evaluate_auth(
        self,
        security_context: SecurityContext,
        action: str,
        resource: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluate authentication policy.
        
        Pure Primitive - Policy Logic Only:
        - Observes execution context
        - Validates policy (queries Policy Registry)
        - Emits allow/deny/annotate
        
        No side effects. No infra calls. Only policy decisions.
        """
        # Query Policy Registry for auth policy rules
        auth_policy = await self.policy_registry.get_auth_policy(
            action=action,
            resource=resource
        )
        
        # Policy Decision 1: Is user authenticated?
        if not security_context or not security_context.user_id:
            return {
                "allowed": False,
                "reason": "User not authenticated",
                "policy_decision": "denied",
                "policy_id": auth_policy.get("policy_id")
            }
        
        # Policy Decision 2: Zero-trust check (from Policy Registry)
        if auth_policy.get("zero_trust_enabled", True):
            # In zero-trust, we always verify
            # Token validation already happened (in SDK)
            pass
        
        # Policy Decision 3: MFA requirement (from Policy Registry)
        if auth_policy.get("require_mfa_for_admin", False) and "admin" in security_context.roles:
            # Check if MFA is verified (would come from security_context.mfa_verified)
            if not getattr(security_context, 'mfa_verified', False):
                return {
                    "allowed": False,
                    "reason": "MFA required for admin actions",
                    "policy_decision": "requires_mfa",
                    "policy_id": auth_policy.get("policy_id")
                }
        
        return {
            "allowed": True,
            "reason": "Authentication policy satisfied",
            "policy_decision": "allowed",
            "policy_id": auth_policy.get("policy_id")
        }
    
    async def validate_tenant_access(
        self,
        user_tenant_id: str,
        resource_tenant_id: str,
        security_context: SecurityContext
    ) -> Dict[str, Any]:
        """
        Validate tenant access policy.
        
        Pure Primitive - Policy Logic Only:
        - Queries Policy Registry for tenant isolation rules
        - Emits allow/deny decision
        
        No side effects. No infra calls. Only policy decisions.
        """
        # Query Policy Registry for tenant isolation rules
        isolation_rules = await self.policy_registry.get_tenant_isolation_rules(
            tenant_id=user_tenant_id
        )
        
        # Policy Decision 1: Same tenant
        if user_tenant_id == resource_tenant_id:
            return {
                "allowed": True,
                "reason": "Same tenant access",
                "isolation_level": isolation_rules.get("isolation_level", "strict"),
                "policy_id": isolation_rules.get("policy_id")
            }
        
        # Policy Decision 2: Isolation level (from Policy Registry)
        isolation_level = isolation_rules.get("isolation_level", "strict")
        
        if isolation_level == "strict":
            # Check for admin override (from Policy Registry)
            if isolation_rules.get("allow_admin_override", True) and "admin" in security_context.roles:
                return {
                    "allowed": True,
                    "reason": "Admin override for cross-tenant access",
                    "isolation_level": "strict_with_admin_override",
                    "policy_id": isolation_rules.get("policy_id")
                }
            
            return {
                "allowed": False,
                "reason": "Strict tenant isolation - cross-tenant access denied",
                "isolation_level": "strict",
                "policy_id": isolation_rules.get("policy_id")
            }
        
        # Policy Decision 3: Relaxed isolation
        return {
            "allowed": True,
            "reason": "Relaxed tenant isolation allows cross-tenant access",
            "isolation_level": "relaxed",
            "policy_id": isolation_rules.get("policy_id")
        }
    
    async def check_permission(
        self,
        security_context: SecurityContext,
        permission: str,
        resource: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Check permission policy.
        
        Policy Logic Only:
        - Does user have explicit permission?
        - Does user have role that grants permission?
        - Does admin role grant all permissions?
        """
        # Policy Decision 1: Admin override
        if "admin" in security_context.roles or "admin" in security_context.permissions:
            return {
                "allowed": True,
                "reason": "Admin role grants all permissions",
                "permission_source": "admin_role"
            }
        
        # Policy Decision 2: Explicit permission
        if permission in security_context.permissions:
            return {
                "allowed": True,
                "reason": "User has explicit permission",
                "permission_source": "explicit"
            }
        
        # Policy Decision 3: Role-based permission (would check role → permission mapping)
        # For now, deny if not explicit
        return {
            "allowed": False,
            "reason": "User does not have required permission",
            "permission_source": "none"
        }
    
    async def enforce_zero_trust(
        self,
        security_context: SecurityContext,
        action: str,
        resource: str
    ) -> Dict[str, Any]:
        """
        Enforce zero-trust policy.
        
        Policy Logic Only:
        - Never trust, always verify
        - Continuous validation
        - Adaptive access control
        """
        if not self.zero_trust_enabled:
            return {
                "allowed": True,
                "reason": "Zero-trust not enabled",
                "verification_required": []
            }
        
        # Zero-trust policy: Always verify
        verification_required = []
        
        # Check if action requires additional verification
        if action in ["admin", "delete", "modify"]:
            verification_required.append("mfa")
        
        if resource.startswith("/api/admin/"):
            verification_required.append("device")
        
        return {
            "allowed": True,  # Will be verified by Runtime
            "reason": "Zero-trust policy requires continuous verification",
            "verification_required": verification_required
        }
```

---

### 3.4 Policy Registry (NEW per Review Board)

#### 3.4.1 Location

**Target:** `civic_systems/smart_city/registries/policy_registry.py`

**Type:** Registry (data-backed catalog, queried at runtime)

**Backed by:** Supabase (via Public Works)

#### 3.4.2 Schema Decision (LOCKED IN)

**Decision:** Defer full schema definition, use flexible JSONB structure

**Rationale:**
- Phase 1 is about moving logic, not perfecting schemas
- Flexible structure allows evolution as requirements emerge
- JSONB supports tenant-specific, action-specific, resource-specific policies

**Implementation:**
- Supabase table: `policy_rules` with JSONB `policy_data` column
- Structure: `{policy_id, policy_type, policy_data (JSONB), tenant_id, metadata}`
- Migration: Extract hardcoded policies from `/symphainy_source/` → JSONB → insert into Registry

#### 3.4.3 Implementation

```python
from typing import Dict, Any, Optional
from symphainy_platform.foundations.public_works.abstractions.supabase_adapter import SupabaseAdapter

class PolicyRegistry:
    """
    Policy Registry - Data-backed catalog for policy rules.
    
    Type: Registry (queried at runtime, not imported)
    Stores: AuthZ rules, data access policies, execution constraints, tenant-specific overrides
    
    Schema: Flexible JSONB structure (deferred full schema definition)
    """
    
    def __init__(self, supabase_adapter: SupabaseAdapter):
        self.supabase = supabase_adapter
    
    async def get_auth_policy(
        self,
        action: str,
        resource: Optional[str] = None
    ) -> Dict[str, Any]:
        """Query Policy Registry for authentication policy rules."""
        # Query Supabase policy_rules table (JSONB policy_data column)
        # Returns policy configuration (zero_trust_enabled, require_mfa, etc.)
        ...
    
    async def get_tenant_isolation_rules(
        self,
        tenant_id: str
    ) -> Dict[str, Any]:
        """Query Policy Registry for tenant isolation rules."""
        # Query Supabase for tenant isolation configuration (JSONB)
        # Returns isolation_level, allow_admin_override, etc.
        ...
    
    async def get_policy_rules(
        self,
        action: str,
        tenant_id: str,
        resource: Optional[str] = None
    ) -> Dict[str, Any]:
        """Query Policy Registry for general policy rules."""
        # Query Supabase for policy rules matching action/tenant/resource (JSONB)
        ...
```

---

### 3.5 SDK for Realm Services (UPDATED per Review Board)

#### 3.5.1 Security SDK (Updated Location)

**Location:** `civic_systems/smart_city/sdk/security_sdk.py` (UPDATED)

**Purpose:** Boundary zone for Realms - translates Realm intent → runtime contract shape

```python
from typing import Dict, Any, Optional
from symphainy_platform.foundations.public_works.protocols.auth_protocol import SecurityContext
from civic_systems.platform_sdk.platform_sdk import PlatformSDK
from civic_systems.smart_city.registries.policy_registry import PolicyRegistry
from symphainy_platform.foundations.public_works.protocols.auth_protocol import AuthenticationProtocol, TenancyProtocol


class SecuritySDK:
    """
    Security SDK - Boundary zone for Realms.
    
    Translates Realm intent → runtime contract shape.
    Queries Policy Registry.
    Calls Public Works abstractions.
    Never executes anything.
    Never calls primitives directly (that's Runtime's job).
    """
    
    def __init__(
        self,
        platform_sdk: PlatformSDK,
        policy_registry: PolicyRegistry,
        auth_abstraction: AuthenticationProtocol,
        tenant_abstraction: TenancyProtocol
    ):
        self.platform_sdk = platform_sdk
        self.policy_registry = policy_registry
        self.auth_abstraction = auth_abstraction
        self.tenant_abstraction = tenant_abstraction
    
    async def ensure_user_can(
        self,
        action: str,
        tenant_id: str,
        user_id: str,
        resource: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ensure user can perform action.
        
        Boundary zone method for Realms.
        - Queries Policy Registry
        - Prepares context for Runtime
        - Does NOT call primitives directly (that's Runtime's job)
        """
        # Query Policy Registry for policy rules
        policy_rules = await self.policy_registry.get_policy_rules(
            action=action,
            tenant_id=tenant_id,
            resource=resource
        )
        
        # Get user context (via Platform SDK translation)
        raw_auth_data = await self.auth_abstraction.get_user_info(user_id)
        security_context = await self.platform_sdk.resolve_security_context(raw_auth_data)
        
        # Prepare runtime contract shape (for Runtime to use with primitives)
        return {
            "action": action,
            "resource": resource,
            "security_context": security_context,
            "policy_rules": policy_rules,
            "ready_for_runtime": True
        }
    
    async def validate_tenant_access(
        self,
        user_tenant_id: str,
        resource_tenant_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Validate tenant access.
        
        Boundary zone method for Realms.
        - Queries Policy Registry
        - Prepares context for Runtime
        """
        # Query Policy Registry for tenant isolation rules
        isolation_rules = await self.policy_registry.get_tenant_isolation_rules(
            tenant_id=user_tenant_id
        )
        
        # Get tenant info (via abstraction)
        tenant_info = await self.tenant_abstraction.get_user_tenant_info(user_id)
        
        # Prepare runtime contract shape
        return {
            "user_tenant_id": user_tenant_id,
            "resource_tenant_id": resource_tenant_id,
            "isolation_rules": isolation_rules,
            "tenant_info": tenant_info,
            "ready_for_runtime": True
        }
```

---

## Part 4: Implementation Steps (UPDATED per Review Board)

### Phase 1: Scaffold Core Libraries & Registries

#### 1.1 Repository Structure
- ⏳ Create `civic_systems/smart_city/primitives/` directory
- ⏳ Create `civic_systems/smart_city/sdk/` directory
- ⏳ Create `civic_systems/smart_city/registries/` directory
- ⏳ Create `libraries/policy/` directory

#### 1.2 Policy Registry (NEW) - Flexible JSONB Structure
- ⏳ Create `civic_systems/smart_city/registries/policy_registry.py`
- ⏳ Implement `PolicyRegistry` class
- ⏳ Back with Supabase (via Public Works)
- ⏳ **Schema:** Flexible JSONB structure (defer full schema definition)
  - `policy_rules` table with JSONB `policy_data` column
  - Support tenant-specific, action-specific, resource-specific policies
- ⏳ **Migration:** Extract hardcoded policies from `/symphainy_source/` → JSONB → insert into Registry
- ⏳ Store: AuthZ rules, data access policies, execution constraints, tenant-specific overrides

#### 1.3 Policy Library (NEW) - Scaffold with Minimal Implementation
- ⏳ Create `libraries/policy/schemas.py` - Pydantic models (AuthPolicyRule, TenantIsolationRule)
- ⏳ Create `libraries/policy/validators.py` - Validation stubs (basic validation)
- ⏳ Create `libraries/policy/evaluators.py` - Evaluation stubs (basic evaluation)
- ⏳ **Phase 1:** Scaffold structure, define schemas, provide stubs
- ⏳ **Phase 2:** Full validation/evaluation implementation

---

### Phase 2: Public Works Abstractions ✅ (Already Done)
- ✅ Auth Abstraction refactored
- ⏳ Tenant Abstraction - Add `get_user_tenant_info()` to protocol and implementation
- ⏳ Authorization Abstraction - Refactor to return raw data only

---

### Phase 3: Platform SDK Enhancement
- ⏳ Enhance `resolve_security_context()` with tenant resolution
- ⏳ Add tenant resolution helpers
- ⏳ Ensure all translation logic is in Platform SDK

---

### Phase 4: Smart City SDK (Boundary Zone)
- ⏳ Create `civic_systems/smart_city/sdk/security_sdk.py`
- ⏳ Implement `ensure_user_can()` method
- ⏳ Implement `validate_tenant_access()` method
- ⏳ Ensure SDK queries Policy Registry (not primitives)
- ⏳ Ensure SDK prepares runtime contract shape

---

### Phase 5: Security Guard Primitive (Pure Primitive)
- ⏳ Create `civic_systems/smart_city/primitives/security_guard/` structure
- ⏳ Implement `SecurityGuardPrimitive` class
- ⏳ Implement policy methods (`evaluate_auth`, `validate_tenant_access`, `check_permission`, `enforce_zero_trust`)
- ⏳ Ensure primitive queries Policy Registry (not hardcoded config)
- ⏳ Ensure primitive is pure (no side effects, no infra calls)
- ⏳ Note: Primitives are called only by Runtime (later), not by Realms

---

### Phase 6: Realm Refactor (Minimal, Surgical)
- ⏳ Update realm services to use Smart City SDK (not primitives directly)
- ⏳ Change: `auth_service.validate_user(...)` → `smart_city_sdk.ensure_user_can(...)`
- ⏳ All functional logic stays where it is

---

### Phase 7: Integration & Testing
- ⏳ Update Runtime (later) to use Security Guard Primitive
- ⏳ Update realm services to use Smart City SDK
- ⏳ Run all tests
- ⏳ Update documentation

---

## Part 5: Improvements Over Old Implementation

### 5.1 Better Separation of Concerns

**Old:** Business logic, translation logic, and policy logic all mixed together

**New:** 
- ✅ Abstractions = Pure infrastructure
- ✅ Platform SDK = Translation logic
- ✅ Security Guard = Policy logic only

### 5.2 Better Testability

**Old:** Hard to test because everything is coupled

**New:**
- ✅ Abstractions can be swapped (Supabase → Auth0)
- ✅ Platform SDK can be tested independently
- ✅ Security Guard can be tested with mock SDK

### 5.3 Better Security

**Old:** Direct adapter access bypasses abstractions

**New:**
- ✅ All access through abstractions
- ✅ Policy decisions centralized in Security Guard
- ✅ Translation logic centralized in Platform SDK

### 5.4 Better Maintainability

**Old:** Micro-modules with mixed concerns

**New:**
- ✅ Clear separation of concerns
- ✅ Single responsibility per component
- ✅ Easy to extend (add new policy rules)

---

## Part 6: Questions & Answers

### Q1: Should Security Guard Primitive have SOA APIs?

**A:** No. Primitives are called only by Runtime (later). Realms use Smart City SDK instead.

**If SOA APIs are needed for backward compatibility:**
- They should be in Smart City SDK (boundary zone)
- They prepare runtime contract shape
- Runtime calls primitives, not Realms

### Q2: Should Security Guard have MCP Tools?

**A:** No. MCP tools stay in Agentic SDK (per Review Board decision).

**Key Principle:**
- MCP tools are never registered globally
- MCP tools are never visible to Runtime
- Runtime only sees agent conclusions, not tools
- This avoids Runtime pollution and Agent/Execution coupling

### Q3: How do realm services use Security Guard?

**A:** Via Smart City SDK (boundary zone):
```python
# In realm service:
from civic_systems.smart_city.sdk.security_sdk import SecuritySDK

class MyRealmService:
    def __init__(self, security_sdk: SecuritySDK):
        self.security_sdk = security_sdk
    
    async def my_method(self, user_id: str, tenant_id: str):
        # Use Smart City SDK (boundary zone)
        runtime_contract = await self.security_sdk.ensure_user_can(
            action="my_action",
            tenant_id=tenant_id,
            user_id=user_id,
            resource="my_resource"
        )
        
        # Runtime contract is ready for Runtime to use with primitives
        # For now, Realms can check if ready_for_runtime is True
        if not runtime_contract.get("ready_for_runtime"):
            raise PermissionError("Access denied")
        
        # Continue with business logic
        ...
```

**Note:** Realms never call primitives directly. They use SDKs. Runtime calls primitives.

---

## Part 7: Success Criteria (UPDATED per Review Board)

### ✅ Phase 1 Exit Criteria

Phase 1 is complete when:

- [ ] Smart City logic exists as primitives + SDK
- [ ] Policy Registry is queryable without Runtime
- [ ] Realms only talk to SDKs (never primitives directly)
- [ ] Public Works remains the only infra gateway
- [ ] No behavior regressions in the MVP

### ✅ Functional Requirements

1. **Authentication:**
   - ✅ Users can authenticate via Supabase
   - ✅ Tokens are validated (JWKS)
   - ✅ SecurityContext is created (via Platform SDK)

2. **Authorization:**
   - ✅ Permissions are checked (via Security Guard Primitive, called by Runtime)
   - ✅ Tenant access is validated (via Security Guard Primitive)
   - ✅ Zero-trust policy is enforced (via Security Guard Primitive)

3. **Integration:**
   - ✅ Realm services can use Smart City SDK (boundary zone)
   - ✅ Runtime can use Security Guard Primitive (later)
   - ✅ Policy Registry is queryable (data-backed)

### ✅ Non-Functional Requirements

1. **Performance:**
   - ✅ JWKS validation (fast, no network calls)
   - ✅ Policy Registry queries (cached where appropriate)
   - ✅ No unnecessary abstraction layers

2. **Maintainability:**
   - ✅ Clear separation: Libraries (imported) vs Registries (queried)
   - ✅ Clear separation: Primitives (policy) vs SDK (boundary zone)
   - ✅ Easy to test (each layer independently)
   - ✅ Easy to extend (add new policy rules to Registry)

3. **Security:**
   - ✅ Zero-trust pattern enforced
   - ✅ Fail closed (deny by default)
   - ✅ All access through abstractions
   - ✅ Policy decisions centralized in primitives

---

## Part 8: Next Steps (UPDATED per Review Board)

1. **✅ Review this plan** - Aligned with Review Board feedback
2. **Implement Phase 1** - Scaffold core libraries & registries (Policy Registry)
3. **Implement Phase 2** - Public Works abstractions (Tenant & Authorization)
4. **Implement Phase 3** - Platform SDK enhancement
5. **Implement Phase 4** - Smart City SDK (boundary zone)
6. **Implement Phase 5** - Security Guard Primitive (pure primitive)
7. **Implement Phase 6** - Realm refactor (use SDK, not primitives)
8. **Implement Phase 7** - Integration & Testing

---

## Part 9: Key Architectural Decisions (Locked In)

### 9.1 Libraries vs Registries

**Libraries** (imported, versioned):
- `civic_systems/smart_city/sdk/` - Smart City SDK
- `civic_systems/smart_city/primitives/` - Smart City Primitives
- `libraries/policy/` - Policy Library

**Registries** (queried at runtime, data-backed):
- `civic_systems/smart_city/registries/policy_registry.py` - Policy Registry
- `civic_systems/curator/registries/service_registry.py` - Service Registry

### 9.2 MCP Tools Decision

**Locked In:**
- MCP tools stay in Agentic SDK
- Never registered globally
- Never visible to Runtime
- Runtime only sees agent conclusions

### 9.3 Primitive vs SDK

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

### 9.4 Realm Access Pattern

**Rule:**
- Realms **never** call Smart City primitives directly
- Realms **only** call Smart City SDKs
- Runtime calls primitives (later)

---

## Summary

This plan provides:
- ✅ **Better separation of concerns** (infrastructure, translation, policy)
- ✅ **Better testability** (each layer can be tested independently)
- ✅ **Better security** (all access through abstractions, policy centralized)
- ✅ **Better maintainability** (clear responsibilities, easy to extend)

The new implementation will be **better than the old** because:
1. No direct adapter access (all through abstractions)
2. Clear policy logic (in Security Guard only)
3. Centralized translation (in Platform SDK)
4. Pure infrastructure (abstractions are swappable)
