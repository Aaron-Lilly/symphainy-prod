# Policy Registry & Policy Library Recommendations

**Date:** January 2026  
**Status:** 📋 **RECOMMENDATIONS FOR PHASE 1**  
**Questions:** Policy Registry Schema & Policy Library timing

---

## Question 1: Policy Registry Schema

### Recommendation: **Defer Full Schema, Start with Flexible Structure**

**Rationale:**
1. **We don't know all policy types yet** - Starting with a flexible structure allows us to discover what policies we actually need
2. **Phase 1 is about moving logic, not perfecting schemas** - The goal is to get policy rules out of code and into data
3. **Supabase is flexible** - We can use JSONB columns to store policy rules without rigid schemas initially

### Phase 1 Approach: **Flexible JSONB Structure**

**Schema (Minimal, Evolvable):**
```sql
-- Supabase table: policy_rules
CREATE TABLE policy_rules (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  policy_type TEXT NOT NULL,  -- 'auth', 'tenant_isolation', 'data_access', etc.
  policy_name TEXT NOT NULL,   -- 'zero_trust', 'strict_isolation', etc.
  tenant_id TEXT,              -- NULL = global policy, TEXT = tenant-specific
  action TEXT,                  -- Optional: specific action this applies to
  resource TEXT,                -- Optional: specific resource this applies to
  policy_data JSONB NOT NULL,   -- Flexible policy configuration
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(policy_type, policy_name, tenant_id, action, resource)
);

-- Index for fast lookups
CREATE INDEX idx_policy_rules_lookup ON policy_rules(policy_type, tenant_id, action, resource);
```

**Example Policy Data (JSONB):**
```json
{
  "zero_trust_enabled": true,
  "require_mfa_for_admin": true,
  "require_mfa_for_actions": ["delete", "admin"],
  "continuous_validation": true,
  "verification_required": ["mfa", "device"]
}
```

**Benefits:**
- ✅ Flexible - can store any policy configuration
- ✅ Tenant-specific - can override global policies
- ✅ Action/resource-specific - can have fine-grained policies
- ✅ Evolvable - schema can be refined later without breaking changes

### Phase 1 Implementation:

**Policy Registry Interface:**
```python
class PolicyRegistry:
    async def get_auth_policy(
        self,
        action: str,
        resource: Optional[str] = None,
        tenant_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get authentication policy rules.
        
        Returns tenant-specific policy if available, otherwise global policy.
        """
        # Query Supabase for policy rules
        # Priority: tenant-specific > action-specific > global
        ...
    
    async def get_tenant_isolation_rules(
        self,
        tenant_id: str
    ) -> Dict[str, Any]:
        """
        Get tenant isolation rules.
        
        Returns tenant-specific rules if available, otherwise global defaults.
        """
        # Query Supabase for tenant isolation policy
        # Default: {"isolation_level": "strict", "allow_admin_override": true}
        ...
```

**Migration Strategy:**
1. Extract hardcoded policy rules from `/symphainy_source/`
2. Convert to JSONB format
3. Insert into Policy Registry (global policies)
4. Primitives query Registry instead of hardcoded values

**Example Migration:**
```python
# OLD (hardcoded in primitive):
self.zero_trust_enabled = True
self.tenant_isolation_strict = True

# NEW (from Registry):
auth_policy = await self.policy_registry.get_auth_policy(action, resource)
zero_trust_enabled = auth_policy.get("zero_trust_enabled", True)  # Default fallback
```

---

## Question 2: Policy Library

### Recommendation: **Scaffold Now, Implement Later**

**Rationale:**
1. **SDKs and Primitives need to import from it** - Even if implementation is minimal, the interface needs to exist
2. **Defines contracts early** - Helps us think about what policy evaluation looks like
3. **Prevents circular dependencies** - If we wait, we might create dependencies that are hard to untangle

### Phase 1 Approach: **Scaffold with Minimal Implementation**

**Structure:**
```
libraries/policy/
├── __init__.py
├── schemas.py          # Policy rule schemas (Pydantic models)
├── validators.py       # Policy validation helpers (stubs)
└── evaluators.py       # Policy evaluation utilities (stubs)
```

**Phase 1 Implementation (Minimal):**

**1. Schemas (`libraries/policy/schemas.py`):**
```python
from pydantic import BaseModel
from typing import Dict, Any, Optional, List

class AuthPolicyRule(BaseModel):
    """Schema for authentication policy rules."""
    zero_trust_enabled: bool = True
    require_mfa_for_admin: bool = False
    require_mfa_for_actions: List[str] = []
    continuous_validation: bool = True
    verification_required: List[str] = []

class TenantIsolationRule(BaseModel):
    """Schema for tenant isolation rules."""
    isolation_level: str = "strict"  # "strict", "relaxed", "shared"
    allow_admin_override: bool = True
    allow_cross_tenant_read: bool = False
    allow_cross_tenant_write: bool = False

class PolicyRule(BaseModel):
    """Generic policy rule schema."""
    policy_type: str
    policy_name: str
    tenant_id: Optional[str] = None
    action: Optional[str] = None
    resource: Optional[str] = None
    policy_data: Dict[str, Any]
```

**2. Validators (`libraries/policy/validators.py`):**
```python
from typing import Dict, Any
from .schemas import AuthPolicyRule, TenantIsolationRule

def validate_auth_policy(policy_data: Dict[str, Any]) -> AuthPolicyRule:
    """Validate authentication policy data against schema."""
    # Phase 1: Basic validation (stub)
    return AuthPolicyRule(**policy_data)

def validate_tenant_isolation_rule(policy_data: Dict[str, Any]) -> TenantIsolationRule:
    """Validate tenant isolation rule data against schema."""
    # Phase 1: Basic validation (stub)
    return TenantIsolationRule(**policy_data)
```

**3. Evaluators (`libraries/policy/evaluators.py`):**
```python
from typing import Dict, Any
from symphainy_platform.foundations.public_works.protocols.auth_protocol import SecurityContext

def evaluate_auth_policy(
    policy_rule: Dict[str, Any],
    security_context: SecurityContext,
    action: str
) -> Dict[str, Any]:
    """
    Evaluate authentication policy rule.
    
    Phase 1: Basic evaluation (stub)
    Phase 2: Full policy engine integration
    """
    # Phase 1: Simple evaluation
    if policy_rule.get("zero_trust_enabled", True):
        # Zero-trust always requires verification
        return {
            "allowed": True,
            "verification_required": policy_rule.get("verification_required", [])
        }
    
    return {"allowed": True, "verification_required": []}
```

**Usage in Phase 1:**
```python
# In Security Guard Primitive:
from libraries.policy.schemas import AuthPolicyRule
from libraries.policy.validators import validate_auth_policy

# Query Registry
raw_policy = await self.policy_registry.get_auth_policy(action, resource)

# Validate using Library
auth_policy = validate_auth_policy(raw_policy)

# Use validated policy
if auth_policy.zero_trust_enabled:
    ...
```

**Benefits:**
- ✅ Defines contracts early (prevents drift)
- ✅ Provides type safety (Pydantic validation)
- ✅ Allows incremental implementation (stubs → full implementation)
- ✅ Prevents circular dependencies (Library is independent)

---

## Phase 1 Implementation Plan

### Step 1: Create Policy Registry (Data-Backed)

**File:** `civic_systems/smart_city/registries/policy_registry.py`

**Implementation:**
- Query Supabase for policy rules
- Return raw JSONB data
- Support tenant-specific overrides
- Support action/resource-specific policies

**Migration:**
- Extract hardcoded policies from `/symphainy_source/`
- Insert into Supabase `policy_rules` table
- Use flexible JSONB structure (no rigid schema)

---

### Step 2: Scaffold Policy Library (Code-Level)

**Files:**
- `libraries/policy/schemas.py` - Pydantic models
- `libraries/policy/validators.py` - Validation stubs
- `libraries/policy/evaluators.py` - Evaluation stubs

**Implementation:**
- Define schemas for known policy types (Auth, Tenant Isolation)
- Provide validation helpers (basic validation)
- Provide evaluation stubs (basic evaluation)
- Full implementation in Phase 2

---

### Step 3: Update Primitives to Use Registry + Library

**Security Guard Primitive:**
```python
# Query Registry (data-backed)
auth_policy_data = await self.policy_registry.get_auth_policy(action, resource)

# Validate using Library (code-level)
from libraries.policy.validators import validate_auth_policy
auth_policy = validate_auth_policy(auth_policy_data)

# Use validated policy
if auth_policy.zero_trust_enabled:
    ...
```

---

## Summary

### Policy Registry Schema: **Defer Full Schema**

**Phase 1:**
- Use flexible JSONB structure
- Support tenant-specific overrides
- Support action/resource-specific policies
- Migrate hardcoded policies to Registry

**Phase 2:**
- Refine schema based on actual usage
- Add more policy types as needed
- Optimize queries and indexes

---

### Policy Library: **Scaffold Now**

**Phase 1:**
- Create structure (`schemas.py`, `validators.py`, `evaluators.py`)
- Define schemas for known policy types
- Provide validation/evaluation stubs
- Primitives import and use Library

**Phase 2:**
- Full validation implementation
- Full evaluation implementation
- Policy engine integration
- Advanced policy types

---

## Benefits of This Approach

1. **Flexibility** - JSONB allows policy rules to evolve without schema changes
2. **Type Safety** - Policy Library provides Pydantic validation
3. **Incremental** - Can start simple and add complexity later
4. **Testability** - Can test Registry and Library independently
5. **Migration Path** - Clear path from hardcoded → Registry → Library

---

## Next Steps

1. **Create Policy Registry** (Phase 1)
   - Supabase table with JSONB structure
   - Query methods
   - Migration of hardcoded policies

2. **Scaffold Policy Library** (Phase 1)
   - Schemas for known policy types
   - Validation/evaluation stubs
   - Import by Primitives

3. **Implement Policy Library** (Phase 2)
   - Full validation logic
   - Full evaluation logic
   - Policy engine integration
