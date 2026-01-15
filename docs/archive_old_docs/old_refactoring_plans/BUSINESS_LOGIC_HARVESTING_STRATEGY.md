# Business Logic Harvesting Strategy

**Date:** January 2026  
**Status:** 📋 **HARVESTING STRATEGY**  
**Purpose:** Preserve business logic when refactoring abstractions, even before Smart City roles exist

---

## The Problem: Chicken and Egg

**Challenge:**
- ✅ We need to refactor abstractions NOW (remove business logic)
- ❌ Smart City roles don't exist until Phase 3
- ⚠️ **Risk:** Business logic gets lost or forgotten

**Solution:** Create placeholder Smart City roles NOW, move business logic into them, then fill them out in Phase 3.

---

## Strategy: Placeholder Smart City Roles

### Approach

1. **Create Placeholder Smart City Roles** (skeleton structure)
   - Create the role files with extracted business logic
   - Mark as "PLACEHOLDER - Will be fully implemented in Phase 3"
   - Business logic is preserved and organized

2. **Move Business Logic** (from abstractions to placeholders)
   - Extract business logic from abstractions
   - Move to appropriate Smart City role placeholder
   - Abstractions become pure infrastructure

3. **Phase 3 Implementation** (fill in the skeletons)
   - Placeholder roles become real Smart City roles
   - Add protocol compliance, MCP tools, etc.
   - Business logic is already there!

---

## Implementation Plan

### Step 1: Create Placeholder Structure

**Location:** `symphainy_platform/smart_city/services/`

**Structure:**
```
smart_city/
├── services/
│   ├── security_guard/
│   │   ├── __init__.py
│   │   ├── security_guard_service.py  # PLACEHOLDER - Business logic from Auth/Tenant abstractions
│   │   └── README.md                   # Documents what business logic is here
│   ├── city_manager/
│   │   ├── __init__.py
│   │   ├── city_manager_service.py    # PLACEHOLDER - Business logic from Tenant abstraction
│   │   └── README.md
│   ├── librarian/
│   │   ├── __init__.py
│   │   ├── librarian_service.py       # PLACEHOLDER - Business logic from Semantic Search abstraction
│   │   └── README.md
│   ├── data_steward/
│   │   ├── __init__.py
│   │   ├── data_steward_service.py    # PLACEHOLDER - Business logic from Content Metadata abstraction
│   │   └── README.md
│   └── ... (other roles)
```

---

### Step 2: Extract Business Logic

**For Each Abstraction:**

1. **Identify Business Logic**
   - Tenant creation logic
   - Role/permission extraction
   - Access validation
   - ID generation
   - Validation rules
   - Status management

2. **Extract to Placeholder**
   - Move business logic to appropriate Smart City role placeholder
   - Keep as methods (not yet protocol-compliant)
   - Document what it does

3. **Update Abstraction**
   - Remove business logic
   - Return raw data
   - Call placeholder if needed (temporary bridge)

---

## Example: Auth Abstraction → Security Guard

### Before (Auth Abstraction has business logic):

```python
# symphainy_platform/foundations/public_works/abstractions/auth_abstraction.py
class AuthAbstraction:
    async def authenticate(self, credentials):
        # ... adapter call ...
        user_data = await self.supabase.sign_in_with_password(...)
        
        # ❌ BUSINESS LOGIC (should be in Security Guard)
        if not tenant_id:
            tenant_result = await self._create_tenant_for_user(...)  # BUSINESS LOGIC
        roles = tenant_info.get("roles", [])  # BUSINESS LOGIC
        permissions = tenant_info.get("permissions", [])  # BUSINESS LOGIC
        
        return SecurityContext(...)  # BUSINESS OBJECT
```

### After (Auth Abstraction is pure, Security Guard placeholder has logic):

```python
# symphainy_platform/foundations/public_works/abstractions/auth_abstraction.py
class AuthAbstraction:
    async def authenticate(self, credentials):
        # ✅ PURE INFRASTRUCTURE
        result = await self.supabase.sign_in_with_password(...)
        return result.get("user", {})  # Raw data only
```

```python
# symphainy_platform/smart_city/services/security_guard/security_guard_service.py
# PLACEHOLDER - Will be fully implemented in Phase 3
# Business logic extracted from Auth Abstraction

class SecurityGuardService:
    """
    PLACEHOLDER Security Guard Service
    
    This is a placeholder that contains business logic extracted from
    Auth Abstraction. It will become a full Smart City role in Phase 3.
    
    Business Logic Harvested:
    - Tenant creation logic (from Auth Abstraction)
    - Role/permission extraction (from Auth Abstraction)
    - Access validation (from Tenant Abstraction)
    - SecurityContext creation (from Auth Abstraction)
    """
    
    def __init__(self, auth_abstraction, tenant_abstraction):
        self.auth_abstraction = auth_abstraction
        self.tenant_abstraction = tenant_abstraction
    
    async def authenticate_user(self, credentials):
        """
        Authenticate user with business logic.
        
        HARVESTED FROM: Auth Abstraction.authenticate()
        """
        # Use abstraction for infrastructure
        raw_user_data = await self.auth_abstraction.authenticate(credentials)
        if not raw_user_data:
            return None
        
        user_id = raw_user_data.get("id")
        email = raw_user_data.get("email")
        
        # BUSINESS LOGIC: Resolve tenant
        tenant_id = await self._resolve_tenant(user_id, raw_user_data)
        
        # BUSINESS LOGIC: Resolve roles/permissions
        roles, permissions = await self._resolve_roles_permissions(user_id, tenant_id)
        
        # BUSINESS LOGIC: Create SecurityContext
        return SecurityContext(
            user_id=user_id,
            tenant_id=tenant_id,
            email=email,
            roles=roles,
            permissions=permissions,
            origin="security_guard"
        )
    
    async def _resolve_tenant(self, user_id, raw_user_data):
        """
        BUSINESS LOGIC: Resolve tenant for user.
        
        HARVESTED FROM: Auth Abstraction._create_tenant_for_user()
        """
        # Try database first
        tenant_info = await self.tenant_abstraction.get_user_tenant_info(user_id)
        if tenant_info:
            return tenant_info.get("tenant_id")
        
        # Try metadata
        tenant_id = raw_user_data.get("user_metadata", {}).get("tenant_id")
        if tenant_id:
            return tenant_id
        
        # BUSINESS DECISION: Create tenant? (This is business logic)
        # For now, return None. In Phase 3, this will use City Manager.
        return None
    
    async def _resolve_roles_permissions(self, user_id, tenant_id):
        """
        BUSINESS LOGIC: Resolve roles and permissions.
        
        HARVESTED FROM: Auth Abstraction (role extraction logic)
        """
        # Get from database
        tenant_info = await self.tenant_abstraction.get_user_tenant_info(user_id)
        if tenant_info:
            return tenant_info.get("roles", []), tenant_info.get("permissions", [])
        
        # Fallback to metadata
        # ... (harvested logic)
        return [], []
```

---

## Harvesting Checklist

### For Each Abstraction Being Refactored:

- [ ] **Identify Business Logic**
  - [ ] List all business logic methods
  - [ ] Document what each does
  - [ ] Identify which Smart City role should own it

- [ ] **Create Placeholder Role** (if doesn't exist)
  - [ ] Create role directory
  - [ ] Create placeholder service file
  - [ ] Add README documenting harvested logic

- [ ] **Extract Business Logic**
  - [ ] Copy business logic to placeholder
  - [ ] Update to use abstractions (not adapters)
  - [ ] Document where it came from

- [ ] **Update Abstraction**
  - [ ] Remove business logic
  - [ ] Return raw data only
  - [ ] Add comment: "Business logic moved to <Role> placeholder"

- [ ] **Create Bridge** (temporary, until Phase 3)
  - [ ] Abstraction can call placeholder if needed
  - [ ] Or Experience/Runtime can call placeholder directly
  - [ ] Document this is temporary

---

## Placeholder Structure Template

### Security Guard Placeholder

```python
# symphainy_platform/smart_city/services/security_guard/security_guard_service.py
"""
PLACEHOLDER Security Guard Service

This is a placeholder that contains business logic extracted from
Auth and Tenant abstractions. It will become a full Smart City role in Phase 3.

Business Logic Harvested:
- From Auth Abstraction:
  - Tenant creation logic (authenticate method)
  - Role/permission extraction (validate_token method)
  - SecurityContext creation (all methods)
- From Tenant Abstraction:
  - Access validation logic (validate_tenant_access method)
  - Tenant configuration management (get_tenant_config method)

Phase 3 TODO:
- Implement SmartCityServiceProtocol
- Add MCP tools
- Add protocol compliance
- Add telemetry
- Add proper error handling
"""

from typing import Dict, Any, Optional, List
from symphainy_platform.foundations.public_works.abstractions.auth_abstraction import AuthAbstraction
from symphainy_platform.foundations.public_works.abstractions.tenant_abstraction import TenantAbstraction
from symphainy_platform.foundations.public_works.protocols.auth_protocol import SecurityContext


class SecurityGuardService:
    """PLACEHOLDER - Security Guard Service with harvested business logic."""
    
    def __init__(
        self,
        auth_abstraction: AuthAbstraction,
        tenant_abstraction: TenantAbstraction
    ):
        self.auth_abstraction = auth_abstraction
        self.tenant_abstraction = tenant_abstraction
    
    # ============================================================================
    # HARVESTED BUSINESS LOGIC (from Auth Abstraction)
    # ============================================================================
    
    async def authenticate_user(
        self,
        credentials: Dict[str, Any]
    ) -> Optional[SecurityContext]:
        """
        Authenticate user with business logic.
        
        HARVESTED FROM: Auth Abstraction.authenticate()
        """
        # ... (harvested logic)
        pass
    
    async def validate_token(
        self,
        token: str
    ) -> Optional[SecurityContext]:
        """
        Validate token with business logic.
        
        HARVESTED FROM: Auth Abstraction.validate_token()
        """
        # ... (harvested logic)
        pass
    
    # ============================================================================
    # HARVESTED BUSINESS LOGIC (from Tenant Abstraction)
    # ============================================================================
    
    async def validate_tenant_access(
        self,
        user_tenant_id: str,
        resource_tenant_id: str
    ) -> bool:
        """
        Validate tenant access with business logic.
        
        HARVESTED FROM: Tenant Abstraction.validate_tenant_access()
        """
        # ... (harvested logic)
        pass
```

---

## Harvesting Workflow

### Step-by-Step Process

**1. Before Refactoring Abstraction:**
```bash
# Create placeholder if doesn't exist
mkdir -p symphainy_platform/smart_city/services/security_guard
touch symphainy_platform/smart_city/services/security_guard/security_guard_service.py
```

**2. Extract Business Logic:**
```python
# In abstraction, identify business logic
# Copy it to placeholder
# Update placeholder to use abstraction (not adapter)
```

**3. Update Abstraction:**
```python
# Remove business logic
# Return raw data
# Add comment: "Business logic moved to SecurityGuard placeholder"
```

**4. Test:**
```bash
# Test abstraction returns raw data
pytest tests/foundations/public_works/test_auth_abstraction_validation.py

# Test placeholder has business logic
pytest tests/smart_city/test_security_guard_placeholder.py
```

**5. Document:**
```markdown
# In placeholder README.md
## Business Logic Harvested

### From Auth Abstraction:
- `authenticate()` → `SecurityGuard.authenticate_user()`
- `validate_token()` → `SecurityGuard.validate_token()`
- `_create_tenant_for_user()` → `SecurityGuard._resolve_tenant()`

### From Tenant Abstraction:
- `validate_tenant_access()` → `SecurityGuard.validate_tenant_access()`
```

---

## Temporary Bridge Pattern

### Option 1: Abstraction Calls Placeholder (Temporary)

```python
# symphainy_platform/foundations/public_works/abstractions/auth_abstraction.py
class AuthAbstraction:
    def __init__(self, supabase_adapter, security_guard_placeholder=None):
        self.supabase = supabase_adapter
        self.security_guard = security_guard_placeholder  # Optional bridge
    
    async def authenticate(self, credentials):
        # Pure infrastructure
        raw_data = await self.supabase.sign_in_with_password(...)
        
        # TEMPORARY BRIDGE: If placeholder exists, use it
        # This will be removed in Phase 3 when Security Guard is real
        if self.security_guard:
            return await self.security_guard.authenticate_user(credentials)
        
        # Otherwise, return raw data (abstraction is pure)
        return raw_data.get("user", {})
```

**Pros:**
- Existing code continues to work
- Gradual migration

**Cons:**
- Abstraction still has dependency on placeholder
- Not fully pure

---

### Option 2: Experience/Runtime Calls Placeholder Directly

```python
# symphainy_platform/experience/api/auth_handler.py
class AuthHandler:
    def __init__(self, auth_abstraction, security_guard_placeholder):
        self.auth_abstraction = auth_abstraction
        self.security_guard = security_guard_placeholder
    
    async def login(self, credentials):
        # Use placeholder for business logic
        security_context = await self.security_guard.authenticate_user(credentials)
        return security_context
```

**Pros:**
- Abstraction is fully pure
- Clear separation

**Cons:**
- Requires updating callers
- More changes needed

---

### Recommendation: Option 2 (Direct Calls)

**Why:**
- Keeps abstractions fully pure
- Makes it clear where business logic lives
- Easier to migrate to Phase 3 (just make placeholder real)

---

## Harvesting Map

### Business Logic → Smart City Role Mapping

| Abstraction | Business Logic | Smart City Role | Placeholder Location |
|------------|----------------|----------------|---------------------|
| Auth Abstraction | Tenant creation | City Manager | `smart_city/services/city_manager/` |
| Auth Abstraction | Role extraction | Security Guard | `smart_city/services/security_guard/` |
| Auth Abstraction | SecurityContext creation | Security Guard | `smart_city/services/security_guard/` |
| Tenant Abstraction | Access validation | Security Guard | `smart_city/services/security_guard/` |
| Tenant Abstraction | Configuration management | City Manager | `smart_city/services/city_manager/` |
| Content Metadata Abstraction | ID generation | Data Steward | `smart_city/services/data_steward/` |
| Content Metadata Abstraction | Validation rules | Data Steward | `smart_city/services/data_steward/` |
| Semantic Search Abstraction | Document ID generation | Librarian | `smart_city/services/librarian/` |
| Semantic Data Abstraction | Validation logic | Librarian | `smart_city/services/librarian/` |
| Workflow Orchestration Abstraction | Workflow definition | Conductor | `smart_city/services/conductor/` |
| Workflow Orchestration Abstraction | Workflow execution | Conductor | `smart_city/services/conductor/` |

---

## Phase 3 Migration Path

### When Phase 3 Arrives:

**1. Placeholder → Real Role:**
```python
# Before (Placeholder)
class SecurityGuardService:
    """PLACEHOLDER - Security Guard Service"""
    # ... harvested business logic ...

# After (Real Smart City Role)
class SecurityGuardService(SmartCityServiceProtocol):
    """Security Guard - Smart City Role"""
    # ... same business logic ...
    # ... add protocol compliance ...
    # ... add MCP tools ...
    # ... add telemetry ...
```

**2. Update Callers:**
```python
# Before (calling placeholder)
security_guard = SecurityGuardService(auth_abstraction, tenant_abstraction)

# After (calling real role - same interface!)
security_guard = SecurityGuardService(auth_abstraction, tenant_abstraction)
# No changes needed - interface is the same!
```

**3. Remove Temporary Bridges:**
```python
# Remove any temporary bridges from abstractions
# Abstractions are now fully pure
```

---

## Validation Strategy

### Test Placeholders Too

```python
# tests/smart_city/test_security_guard_placeholder.py
class TestSecurityGuardPlaceholder:
    """Test that placeholder has harvested business logic."""
    
    async def test_has_authenticate_user_method(self, security_guard_placeholder):
        """Test that placeholder has authenticate_user method."""
        assert hasattr(security_guard_placeholder, 'authenticate_user')
    
    async def test_authenticate_user_creates_security_context(self, security_guard_placeholder):
        """Test that authenticate_user creates SecurityContext (business logic)."""
        result = await security_guard_placeholder.authenticate_user({...})
        assert isinstance(result, SecurityContext)  # Business logic preserved!
```

---

## Summary

**Strategy:**
1. ✅ Create placeholder Smart City roles NOW
2. ✅ Move business logic from abstractions to placeholders
3. ✅ Abstractions become pure infrastructure
4. ✅ Business logic is preserved and organized
5. ✅ Phase 3: Fill in placeholders (add protocol, MCP tools, etc.)

**Benefits:**
- ✅ No business logic lost
- ✅ Organized by Smart City role
- ✅ Easy Phase 3 migration (just fill in skeletons)
- ✅ Abstractions are pure from day 1

**This solves the chicken-and-egg problem!**
