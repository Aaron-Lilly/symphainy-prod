# Public Works Abstraction Refactoring Plan

**Date:** January 2026  
**Status:** 🔴 **CRITICAL ISSUE IDENTIFIED**  
**Purpose:** Fix Public Works abstractions to be pure infrastructure interfaces

---

## Executive Summary

**The Problem:** Public Works abstractions contain **business logic** that should be in Smart City roles or domain services. This makes them:
- ❌ **Not swappable** (tightly coupled to Supabase data model)
- ❌ **Not suitable for Runtime/Smart City** (they make business decisions)
- ❌ **Violate separation of concerns** (infrastructure doing governance)

**The Fix:** Abstractions should be **pure infrastructure interfaces** - they abstract the **technology**, not the **business logic**.

---

## Core Principle

> **Public Works abstractions should abstract TECHNOLOGY, not BUSINESS LOGIC.**

**What Abstractions Should Do:**
- ✅ Provide technology-agnostic interfaces (Supabase → Auth0, GCS → S3, Redis → Kafka)
- ✅ Handle infrastructure concerns (retries, error handling, connection pooling)
- ✅ Return raw data structures (not business objects)

**What Abstractions Should NOT Do:**
- ❌ Make business decisions (create tenants, assign roles, validate access)
- ❌ Encode business rules (tenant isolation, permission models)
- ❌ Own business state (tenant relationships, user permissions)

**Where Business Logic Belongs:**
- **Smart City Roles** - Governance, policy, tenancy
- **Domain Services** - Business operations
- **Runtime** - Execution orchestration

---

## Issue Analysis

### 🔴 Critical Issue #1: Auth Abstraction

**Location:** `symphainy_platform/foundations/public_works/abstractions/auth_abstraction.py`

**Problems:**

1. **Creates Tenants Automatically** (Lines 86-116, 195-225)
   ```python
   # If still no tenant, create one automatically
   if not tenant_id:
       tenant_result = await self._create_tenant_for_user(...)
   ```
   - ❌ Business logic: "Should we create a tenant?"
   - ❌ Hardcoded: "individual" tenant type, "owner" role
   - ❌ Not swappable: Supabase-specific tenant model

2. **Manages User-Tenant Relationships** (Lines 100-105, 209-214)
   ```python
   link_result = await self.supabase.link_user_to_tenant(
       user_id=user_id,
       tenant_id=tenant_id,
       role="owner",
       is_primary=True
   )
   ```
   - ❌ Business logic: "What role should this user have?"
   - ❌ Hardcoded: "owner" role, "is_primary=True"
   - ❌ Not swappable: Supabase-specific relationship model

3. **Extracts Roles/Permissions** (Lines 118-125, 227-234)
   ```python
   roles = tenant_info.get("roles", [])
   permissions = tenant_info.get("permissions", [])
   ```
   - ❌ Business logic: "Where do roles/permissions come from?"
   - ❌ Hardcoded: Supabase-specific data model
   - ❌ Not swappable: Different auth providers have different models

4. **Registration Flow** (Lines 431-525)
   - ❌ Entire business workflow: create user → create tenant → link → update metadata
   - ❌ Should be in Smart City (City Manager) or domain service

**What Auth Abstraction SHOULD Do:**

```python
class AuthAbstraction(AuthenticationProtocol):
    """Pure infrastructure interface for authentication."""
    
    async def authenticate(
        self,
        credentials: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Authenticate user - returns RAW auth provider data.
        
        Returns:
            {
                "user_id": "...",
                "email": "...",
                "token": "...",
                "raw_data": {...}  # Provider-specific data
            }
        """
        # Just call adapter, return raw data
        result = await self.supabase.sign_in_with_password(...)
        return result.get("user", {})
    
    async def validate_token(
        self,
        token: str
    ) -> Optional[Dict[str, Any]]:
        """
        Validate token - returns RAW auth provider data.
        
        Returns:
            {
                "user_id": "...",
                "email": "...",
                "raw_data": {...}  # Provider-specific data
            }
        """
        # Just call adapter, return raw data
        result = await self.supabase.validate_token_local(token)
        return result.get("user", {})
```

**Business Logic Moves To:**
- **Security Guard (Smart City)** - Uses Auth Abstraction + adds policy validation
- **City Manager (Smart City)** - Uses Auth Abstraction + Tenant Abstraction + adds tenant management

---

### 🔴 Critical Issue #2: Tenant Abstraction

**Location:** `symphainy_platform/foundations/public_works/abstractions/tenant_abstraction.py`

**Problems:**

1. **Tenant Access Validation** (Lines 91-123)
   ```python
   async def validate_tenant_access(
       self,
       user_tenant_id: str,
       resource_tenant_id: str
   ) -> bool:
       # Same tenant = always allowed
       if user_tenant_id == resource_tenant_id:
           return True
       # For now, strict isolation: only same tenant allowed
       return False
   ```
   - ❌ Business logic: "What is the tenant access policy?"
   - ❌ Hardcoded: "strict isolation" policy
   - ❌ Should be in Smart City (City Manager or Security Guard)

2. **Tenant Configuration** (Lines 125-150)
   - ❌ Business logic: "What is the tenant configuration model?"
   - ❌ Hardcoded: Supabase-specific configuration structure

**What Tenant Abstraction SHOULD Do:**

```python
class TenantAbstraction(TenancyProtocol):
    """Pure infrastructure interface for tenant data storage."""
    
    async def get_tenant(
        self,
        tenant_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get tenant data - returns RAW tenant data.
        
        Returns:
            Raw tenant data from storage (provider-specific)
        """
        # Just call adapter, return raw data
        result = await self.supabase.get_tenant_by_id(tenant_id)
        return result.get("tenant", {})
    
    async def store_tenant(
        self,
        tenant_data: Dict[str, Any]
    ) -> bool:
        """
        Store tenant data - accepts RAW tenant data.
        
        Args:
            tenant_data: Raw tenant data (provider-specific)
        """
        # Just call adapter, store raw data
        return await self.supabase.create_tenant(tenant_data)
```

**Business Logic Moves To:**
- **City Manager (Smart City)** - Uses Tenant Abstraction + adds tenant management logic
- **Security Guard (Smart City)** - Uses Tenant Abstraction + adds access validation

---

### 🟡 Moderate Issue #3: File Storage Abstraction

**Location:** `symphainy_platform/foundations/public_works/abstractions/file_storage_abstraction.py`

**Problems:**

1. **Content Type Inference** (Lines 72-86)
   ```python
   if file_path.endswith('.parquet'):
       content_type = 'application/parquet'
   ```
   - ⚠️ Minor: This is infrastructure logic (file type detection), but could be in a separate utility

2. **File ID Generation** (Line 105)
   ```python
   file_id = generate_session_id()  # Generate unique file ID
   ```
   - ⚠️ Minor: ID generation is infrastructure, but the choice of generator is business logic

3. **Metadata Creation** (Lines 108-123)
   ```python
   file_metadata = {
       "uuid": file_id,
       "user_id": metadata.get("user_id"),
       "tenant_id": metadata.get("tenant_id"),
       ...
   }
   ```
   - ⚠️ Minor: Metadata structure is business logic, but creating it is infrastructure

**Assessment:** File Storage Abstraction is mostly OK. The issues are minor and could be addressed by:
- Making content type inference optional/configurable
- Accepting file_id as parameter (caller generates)
- Accepting metadata as-is (caller structures it)

---

### ✅ Good Examples

1. **State Abstraction** - ✅ Pure infrastructure (Redis/ArangoDB coordination)
2. **Service Discovery Abstraction** - ✅ Mostly pure (minor validation is OK)

---

## Refactoring Plan

### Phase 1: Auth Abstraction Refactoring (Priority: HIGH)

**Goal:** Make Auth Abstraction a pure infrastructure interface

**Steps:**

1. **Remove Business Logic from Auth Abstraction**
   - Remove `_create_tenant_for_user()` method
   - Remove tenant creation logic from `authenticate()` and `validate_token()`
   - Remove user-tenant linking logic
   - Remove role/permission extraction logic
   - Remove `register_user()` method (move to Smart City)

2. **Simplify Auth Abstraction Interface**
   ```python
   class AuthAbstraction(AuthenticationProtocol):
       """Pure infrastructure interface for authentication."""
       
       async def authenticate(
           self,
           credentials: Dict[str, Any]
       ) -> Optional[Dict[str, Any]]:
           """Authenticate - returns raw auth provider data."""
           result = await self.supabase.sign_in_with_password(...)
           return result.get("user", {})  # Raw data only
       
       async def validate_token(
           self,
           token: str
       ) -> Optional[Dict[str, Any]]:
           """Validate token - returns raw auth provider data."""
           result = await self.supabase.validate_token_local(token)
           return result.get("user", {})  # Raw data only
       
       async def refresh_token(
           self,
           refresh_token: str
       ) -> Optional[Dict[str, Any]]:
           """Refresh token - returns raw auth provider data."""
           result = await self.supabase.refresh_session(refresh_token)
           return result.get("session", {})  # Raw data only
   ```

3. **Move Business Logic to Smart City**
   - **Security Guard** - Uses Auth Abstraction + Tenant Abstraction + adds:
     - Policy validation
     - Role/permission resolution
     - SecurityContext creation
   - **City Manager** - Uses Auth Abstraction + Tenant Abstraction + adds:
     - Tenant creation logic
     - User-tenant relationship management
     - Registration workflow

**Example: Security Guard Using Auth Abstraction**

```python
class SecurityGuard:
    """Smart City role - uses Auth Abstraction for infrastructure."""
    
    def __init__(
        self,
        auth_abstraction: AuthAbstraction,
        tenant_abstraction: TenantAbstraction
    ):
        self.auth = auth_abstraction
        self.tenant = tenant_abstraction
    
    async def authenticate_user(
        self,
        credentials: Dict[str, Any]
    ) -> Optional[SecurityContext]:
        """
        Authenticate user with policy validation.
        
        Business logic: How do we resolve tenant, roles, permissions?
        """
        # 1. Use Auth Abstraction (infrastructure)
        raw_user_data = await self.auth.authenticate(credentials)
        if not raw_user_data:
            return None
        
        user_id = raw_user_data.get("id")
        email = raw_user_data.get("email")
        
        # 2. Business logic: Resolve tenant (via City Manager or Tenant Abstraction)
        tenant_id = await self._resolve_tenant(user_id, raw_user_data)
        
        # 3. Business logic: Resolve roles/permissions (via City Manager)
        roles, permissions = await self._resolve_roles_permissions(
            user_id,
            tenant_id
        )
        
        # 4. Create SecurityContext (business object)
        return SecurityContext(
            user_id=user_id,
            tenant_id=tenant_id,
            email=email,
            roles=roles,
            permissions=permissions,
            origin="security_guard"
        )
    
    async def _resolve_tenant(
        self,
        user_id: str,
        raw_user_data: Dict[str, Any]
    ) -> Optional[str]:
        """Business logic: How do we resolve tenant?"""
        # Try database first
        tenant_info = await self.tenant.get_user_tenant_info(user_id)
        if tenant_info:
            return tenant_info.get("tenant_id")
        
        # Try metadata
        tenant_id = raw_user_data.get("user_metadata", {}).get("tenant_id")
        if tenant_id:
            return tenant_id
        
        # Business decision: Create tenant? (via City Manager)
        # This is where tenant creation logic belongs
        return None
```

---

### Phase 2: Tenant Abstraction Refactoring (Priority: HIGH)

**Goal:** Make Tenant Abstraction a pure infrastructure interface

**Steps:**

1. **Remove Business Logic from Tenant Abstraction**
   - Remove `validate_tenant_access()` method (move to Security Guard)
   - Remove `get_tenant_config()` method (move to City Manager)
   - Simplify to pure data operations

2. **Simplify Tenant Abstraction Interface**
   ```python
   class TenantAbstraction(TenancyProtocol):
       """Pure infrastructure interface for tenant data storage."""
       
       async def get_tenant(
           self,
           tenant_id: str
       ) -> Optional[Dict[str, Any]]:
           """Get tenant - returns raw tenant data."""
           result = await self.supabase.get_tenant_by_id(tenant_id)
           return result.get("tenant", {})
       
       async def store_tenant(
           self,
           tenant_data: Dict[str, Any]
       ) -> bool:
           """Store tenant - accepts raw tenant data."""
           return await self.supabase.create_tenant(tenant_data)
       
       async def get_user_tenant_info(
           self,
           user_id: str
       ) -> Optional[Dict[str, Any]]:
           """Get user-tenant relationship - returns raw data."""
           result = await self.supabase.get_user_tenant_info(user_id)
           return result.get("tenant_info", {})
   ```

3. **Move Business Logic to Smart City**
   - **Security Guard** - Uses Tenant Abstraction + adds:
     - Tenant access validation (policy-based)
   - **City Manager** - Uses Tenant Abstraction + adds:
     - Tenant configuration management
     - Tenant lifecycle management

---

### Phase 3: File Storage Abstraction Refactoring (Priority: LOW)

**Goal:** Make File Storage Abstraction more flexible

**Steps:**

1. **Make Content Type Inference Optional**
   - Accept `content_type` as parameter
   - Make inference optional/configurable

2. **Accept File ID as Parameter**
   - Don't generate file_id in abstraction
   - Caller generates (Runtime or domain service)

3. **Accept Metadata as-Is**
   - Don't structure metadata in abstraction
   - Caller structures it

---

## Impact Assessment

### What Breaks?

1. **Experience Plane** - Currently uses `AuthAbstraction.authenticate()` which returns `SecurityContext`
   - **Fix:** Experience calls Security Guard instead

2. **Runtime** - Currently uses `AuthAbstraction.validate_token()` which returns `SecurityContext`
   - **Fix:** Runtime calls Security Guard instead

3. **Domain Services** - May use `AuthAbstraction` directly
   - **Fix:** Domain services should use Smart City roles (Security Guard, City Manager)

### Migration Path

1. **Build Smart City Roles First** (Phase 3.1)
   - Security Guard uses refactored Auth Abstraction
   - City Manager uses refactored Tenant Abstraction

2. **Update Callers**
   - Experience → Security Guard
   - Runtime → Security Guard
   - Domain Services → Smart City roles

3. **Remove Old Methods**
   - Remove business logic methods from abstractions
   - Update tests

---

## Success Criteria

### ✅ Abstractions Are Swappable

- ✅ Can swap Supabase → Auth0 without changing business logic
- ✅ Can swap GCS → S3 without changing business logic
- ✅ Can swap Redis → Kafka without changing business logic

### ✅ Business Logic in Right Place

- ✅ Tenant creation logic in City Manager
- ✅ Access validation logic in Security Guard
- ✅ Role/permission resolution in Security Guard

### ✅ Runtime/Smart City Can Use Abstractions

- ✅ Runtime uses abstractions via Smart City roles
- ✅ Smart City roles use abstractions for infrastructure
- ✅ No business logic in abstractions

---

## Recommendation

**Priority:** 🔴 **HIGH** - This is blocking Phase 2/3 implementation

**Timeline:**
- **Phase 1 (Auth Abstraction):** 1-2 days
- **Phase 2 (Tenant Abstraction):** 1 day
- **Phase 3 (File Storage Abstraction):** 0.5 days (optional)

**Order:**
1. Refactor Auth Abstraction (Phase 1)
2. Build Security Guard using refactored Auth Abstraction (Phase 3.1)
3. Refactor Tenant Abstraction (Phase 2)
4. Build City Manager using refactored Tenant Abstraction (Phase 3.1)
5. Update callers (Experience, Runtime, Domain Services)

**This refactoring is critical for:**
- ✅ Making abstractions truly swappable
- ✅ Enabling Runtime/Smart City to use abstractions correctly
- ✅ Maintaining architectural boundaries

---

## Conclusion

**You are NOT over-reacting.** This is a **critical architectural issue** that will block Phase 2/3 implementation.

The abstractions are doing too much business logic, making them:
- Not swappable
- Not suitable for Runtime/Smart City
- Violating separation of concerns

**The fix is clear:** Abstractions should be pure infrastructure interfaces. Business logic belongs in Smart City roles.
