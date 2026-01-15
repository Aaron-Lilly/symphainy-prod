# Complete Public Works Refactoring Plan

**Date:** January 2026  
**Status:** 📋 **COMPREHENSIVE REFACTORING PLAN**  
**Purpose:** Complete refactoring plan addressing abstraction business logic, Librarian role, and Supabase tenancy

---

## Executive Summary

This plan addresses three critical areas:

1. **Abstraction Refactoring** - Remove business logic from abstractions, make them pure infrastructure
2. **Librarian Role Clarification** - Define Librarian's role in data mash flow
3. **Supabase Tenancy & Fields** - Document Supabase tenancy capabilities and all available fields

**Timeline:** 3-4 weeks for complete refactoring

---

## Part 1: Librarian Role in Data Mash Flow

### Current Data Flow (As Described)

```
Content Pillar:
1. Ingest → Store file metadata in Supabase
2. Parse → With lineage stored in Supabase
3. Deterministic Embedding → Stored in Arango with lineage in Supabase

Insights Pillar:
4. Data Quality → (not sure if stored)
5. Semantic Embeddings → What data means, stored in Arango
6. Platform uses semantic embeddings instead of client data
```

### Librarian's Role (Semantic Schemas & Meaning)

**Librarian is responsible for:**
- ✅ **Semantic Schema Management** - Managing semantic schemas (what data means)
- ✅ **Semantic Meaning Resolution** - Resolving semantic meaning from embeddings
- ✅ **Semantic Search** - Enabling semantic search across embeddings
- ✅ **Knowledge Graph Operations** - Managing semantic relationships

**Librarian is NOT responsible for:**
- ❌ **Storing Embeddings** - That's Data Steward's job (lineage, provenance)
- ❌ **Creating Embeddings** - That's Content Realm's job (parsing → embeddings)
- ❌ **Data Quality** - That's Data Steward's job
- ❌ **Client Data Storage** - That's Content Realm's job

### Librarian's Role in Data Mash Flow

```
Content Pillar:
1. Ingest → Store file metadata (Content Realm)
2. Parse → With lineage stored (Content Realm + Data Steward)
3. Deterministic Embedding → Stored in Arango (Content Realm)
   ↓
   [Librarian's Role Begins]
   ↓
4. Semantic Schema Registration → Librarian registers semantic schemas
   - What semantic IDs exist
   - What semantic meanings map to which IDs
   - Semantic schema relationships
   ↓
5. Semantic Meaning Resolution → Librarian resolves meaning from embeddings
   - Takes embeddings from Arango
   - Resolves semantic meaning (what data means)
   - Maps to semantic schemas
   ↓
Insights Pillar:
6. Data Quality → Data Steward (governance, contracts)
7. Semantic Embeddings → Librarian provides semantic meaning
   - Librarian resolves "what data means" from embeddings
   - Librarian provides semantic search capabilities
   - Librarian manages semantic schemas
   ↓
8. Platform uses semantic embeddings → Librarian enables this
   - Semantic search (Librarian)
   - Semantic meaning resolution (Librarian)
   - Semantic schema management (Librarian)
```

### Librarian's Responsibilities (Detailed)

1. **Semantic Schema Management**
   - Register semantic schemas (what semantic IDs mean)
   - Manage semantic schema relationships
   - Provide semantic schema lookup

2. **Semantic Meaning Resolution**
   - Resolve semantic meaning from embeddings (stored in Arango)
   - Map embeddings to semantic schemas
   - Provide semantic interpretation

3. **Semantic Search**
   - Enable semantic search across embeddings
   - Provide semantic similarity search
   - Manage semantic search indexes

4. **Knowledge Graph Operations**
   - Manage semantic relationships (semantic graph)
   - Provide semantic graph queries
   - Enable semantic reasoning

### Librarian's Abstraction Requirements

**Required Abstractions:**
1. ✅ **Semantic Search Abstraction** - Search operations (EXISTS, needs refactoring)
2. ❌ **Semantic Data Abstraction** - Semantic data operations (MISSING, needs copy + refactor)
3. ❌ **Content Metadata Abstraction** - Content metadata (MISSING, needs copy + refactor)
4. ❌ **Knowledge Discovery Abstraction** - Knowledge graph operations (MISSING, needs copy + refactor)

**Librarian Uses Abstractions For:**
- **Semantic Search** - Search embeddings, semantic schemas
- **Semantic Data** - Read embeddings from Arango (via abstraction)
- **Content Metadata** - Read content metadata (via abstraction)
- **Knowledge Discovery** - Query semantic graph (via abstraction)

**Librarian Adds Business Logic:**
- Semantic schema management rules
- Semantic meaning resolution rules
- Semantic search query construction
- Knowledge graph relationship rules

---

## Part 2: Supabase Tenancy & Fields

### Supabase Tenancy Capabilities

**✅ Supabase DOES Handle Tenancy:**

1. **Row Level Security (RLS)**
   - ✅ RLS policies enforce tenant isolation at database level
   - ✅ Policies use `auth.uid()` to identify current user
   - ✅ Policies can check `user_tenants` table for tenant membership
   - ✅ **Database-level isolation** - Prevents cross-tenant data access

2. **Tenant Management Tables**
   - ✅ `tenants` table - Stores tenant/organization information
   - ✅ `user_tenants` table - Junction table for user-tenant relationships
   - ✅ Supports multi-tenant (users in multiple tenants)
   - ✅ Supports roles (owner, admin, member, viewer)

3. **Tenant Context in JWT**
   - ✅ JWT contains `user_id` (from `auth.users`)
   - ⚠️ JWT does NOT contain `tenant_id` by default
   - ⚠️ `tenant_id` must be fetched from `user_tenants` table
   - ✅ Can be stored in `user_metadata` as fallback

### Current Adapter Implementation

**✅ Adapter DOES Expose Tenancy:**

1. **`get_user_tenant_info(user_id)` Method**
   - ✅ Queries `user_tenants` table (requires service key)
   - ✅ Returns tenant_id, roles, permissions
   - ✅ Falls back to `user_metadata` if table query fails
   - ✅ **Properly exposes tenancy**

2. **Token Validation**
   - ✅ Validates JWT token
   - ✅ Extracts user_id from JWT
   - ✅ Fetches tenant info from database
   - ✅ Returns user + tenant context

3. **Service Key Requirement**
   - ⚠️ Requires `SUPABASE_SERVICE_KEY` to query `user_tenants` table
   - ⚠️ Falls back to `user_metadata` if service key not available
   - ✅ **Adapter properly handles this**

### Supabase User Object Fields

**Standard Supabase User Fields:**

```python
{
    # Core Identity
    "id": "uuid",                    # User ID (from auth.users)
    "email": "string",               # User email
    "phone": "string",               # User phone (optional)
    "aud": "authenticated",          # Audience (usually "authenticated")
    
    # Metadata
    "user_metadata": {               # User-defined metadata (custom fields)
        "tenant_id": "uuid",         # Custom: Tenant ID (fallback)
        "roles": ["string"],         # Custom: User roles (fallback)
        "permissions": ["string"],   # Custom: User permissions (fallback)
        "full_name": "string",       # Custom: Full name
        "tenant_type": "string",     # Custom: Tenant type
        # ... any custom fields
    },
    "app_metadata": {                # Application-defined metadata (system fields)
        "provider": "email",         # Auth provider
        "providers": ["email"],      # List of providers
        # ... system fields
    },
    
    # Timestamps
    "created_at": "datetime",         # User creation timestamp
    "updated_at": "datetime",        # User update timestamp
    "last_sign_in_at": "datetime",   # Last sign-in timestamp
    "email_confirmed_at": "datetime", # Email confirmation timestamp
    "phone_confirmed_at": "datetime", # Phone confirmation timestamp
    "confirmed_at": "datetime",      # General confirmation timestamp
    
    # Status
    "email_confirmed": "bool",       # Email confirmed status
    "phone_confirmed": "bool",       # Phone confirmed status
    "is_anonymous": "bool",          # Anonymous user flag
    "is_super_admin": "bool",        # Super admin flag
    
    # Session (if available)
    "session": {
        "access_token": "string",
        "refresh_token": "string",
        "expires_in": "int",
        "expires_at": "int",
        "token_type": "bearer"
    }
}
```

### Tenant Information (from `user_tenants` table)

**Fields from `get_user_tenant_info()`:**

```python
{
    "tenant_id": "uuid",             # Primary tenant ID
    "primary_tenant_id": "uuid",     # Primary tenant (same as tenant_id if is_primary=True)
    "tenant_type": "string",         # "individual", "organization", "enterprise"
    "roles": ["string"],             # User roles in tenant
    "permissions": ["string"],       # User permissions in tenant
    "is_primary": "bool",            # Is this the primary tenant?
    "tenant_name": "string",         # Tenant name (from tenants table)
    "tenant_status": "string"        # Tenant status (from tenants table)
}
```

### What We Need to Lock In

**Before Finalizing Auth Abstraction:**

1. **Required Fields (Always Return)**
   - ✅ `user_id` - Always available
   - ✅ `email` - Always available
   - ✅ `tenant_id` - From database or metadata fallback
   - ✅ `roles` - From database or metadata fallback
   - ✅ `permissions` - From database or metadata fallback

2. **Optional Fields (Return if Available)**
   - ⚠️ `phone` - Optional
   - ⚠️ `full_name` - From user_metadata
   - ⚠️ `created_at` - Available
   - ⚠️ `last_sign_in_at` - Available
   - ⚠️ `email_confirmed_at` - Available

3. **Extra Fields (Return in Raw Data)**
   - ⚠️ `user_metadata` - All custom fields
   - ⚠️ `app_metadata` - System fields
   - ⚠️ `aud` - Audience
   - ⚠️ `confirmed_at` - General confirmation
   - ⚠️ `is_anonymous` - Anonymous flag
   - ⚠️ `is_super_admin` - Super admin flag

4. **Session Fields (If Available)**
   - ⚠️ `access_token` - If session available
   - ⚠️ `refresh_token` - If session available
   - ⚠️ `expires_in` - If session available
   - ⚠️ `expires_at` - If session available

### Recommended Auth Abstraction Return Structure

```python
@dataclass
class AuthResult:
    """Raw authentication result from auth provider."""
    # Required fields
    user_id: str
    email: Optional[str]
    
    # Tenant context (from database or metadata)
    tenant_id: Optional[str]
    roles: List[str]
    permissions: List[str]
    
    # Optional standard fields
    phone: Optional[str] = None
    full_name: Optional[str] = None
    created_at: Optional[str] = None
    last_sign_in_at: Optional[str] = None
    email_confirmed_at: Optional[str] = None
    
    # Session (if available)
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    expires_in: Optional[int] = None
    expires_at: Optional[int] = None
    
    # Raw provider data (for extensibility)
    raw_user_metadata: Dict[str, Any] = field(default_factory=dict)
    raw_app_metadata: Dict[str, Any] = field(default_factory=dict)
    raw_provider_data: Dict[str, Any] = field(default_factory=dict)  # All other fields
```

**Rationale:**
- ✅ **Required fields** - Always available, always returned
- ✅ **Optional fields** - Return if available, None if not
- ✅ **Raw data** - Preserve all provider-specific fields for extensibility
- ✅ **Swappable** - Works with Supabase, Auth0, AWS Cognito, etc.

---

## Part 3: Complete Abstraction Refactoring Plan

### Phase 1: Critical Missing Abstractions (Week 1)

**Goal:** Add 4 critical missing abstractions

1. **Event Management Abstraction** (Day 1)
   - Copy from `symphainy_source`
   - Remove `correlation_id`/`tenant_id` from parameters (move to context)
   - Test with Redis adapter

2. **Telemetry Abstraction** (Day 1)
   - Copy from `symphainy_source` (✅ good as-is)
   - Test with OpenTelemetry adapter

3. **Session Abstraction** (Day 2)
   - Copy from `symphainy_source`
   - Remove session data extraction logic (move to Traffic Cop)
   - Test with Redis adapter

4. **Policy Abstraction** (Day 2)
   - Copy from `symphainy_source` (✅ good as-is)
   - Test with policy adapter

### Phase 2: Critical Business Logic Fixes (Week 1-2)

**Goal:** Remove business logic from critical abstractions

5. **Auth Abstraction Refactoring** (Day 3-4)
   - Remove tenant creation logic
   - Remove user-tenant linking logic
   - Remove role/permission extraction logic
   - Return `AuthResult` (raw data structure)
   - Move business logic to Security Guard

6. **Tenant Abstraction Refactoring** (Day 4-5)
   - Remove access validation logic
   - Remove configuration management logic
   - Return raw tenant data
   - Move business logic to City Manager / Security Guard

### Phase 3: Important Missing Abstractions (Week 2)

**Goal:** Add important missing abstractions

7. **Messaging Abstraction** (Day 6)
   - Copy from `symphainy_source`
   - Remove `correlation_id`/`tenant_id` from parameters
   - Test with Redis adapter

8. **Workflow Orchestration Abstraction** (Day 7)
   - Copy from `symphainy_source`
   - Remove workflow definition/execution logic (move to Conductor)
   - Test with Redis Graph adapter

9. **Authorization Abstraction** (Day 8)
   - Copy from `symphainy_source`
   - Remove ALL business logic (tenant access, permissions, policies)
   - Return raw authorization data
   - Move business logic to Security Guard

10. **Content Metadata Abstraction** (Day 9)
    - Copy from `symphainy_source`
    - Remove ID generation, validation, status management
    - Accept IDs as parameters
    - Return raw metadata data
    - Move business logic to Data Steward

11. **Semantic Data Abstraction** (Day 10)
    - Copy from `symphainy_source`
    - Remove validation logic, business rules
    - Return raw semantic data
    - Move business logic to Librarian

### Phase 4: Moderate Fixes (Week 3)

**Goal:** Fix minor business logic issues

12. **Semantic Search Abstraction** (Day 11)
    - Don't generate document IDs
    - Require document ID as parameter
    - Move ID generation to Librarian

13. **File Storage Abstraction** (Day 11)
    - Make content type inference optional
    - Accept file_id as parameter (don't generate)
    - Accept metadata as-is (don't structure)

### Phase 5: Remaining Abstractions (Week 3-4)

**Goal:** Review and copy remaining abstractions

14. **Routing Abstraction** (Day 12)
    - Copy from `symphainy_source` (✅ good as-is)

15. **Task Management Abstraction** (Day 13)
    - Copy from `symphainy_source`
    - Review for business logic
    - Remove if found

16. **Observability Abstraction** (Day 14)
    - Copy from `symphainy_source`
    - Review for business logic
    - Remove if found

17. **Health Abstraction** (Day 15)
    - Copy from `symphainy_source` (✅ good as-is)

18. **Alert Management Abstraction** (Day 16)
    - Copy from `symphainy_source`
    - Review for business logic
    - Remove if found

19. **Log Aggregation Abstraction** (Day 17)
    - Copy from `symphainy_source`
    - Review for business logic
    - Remove if found

20. **Knowledge Discovery Abstraction** (Day 18)
    - Copy from `symphainy_source`
    - Review for business logic
    - Remove if found

21. **Metadata Management Abstraction** (Day 19)
    - Copy from `symphainy_source`
    - Review for business logic
    - Remove if found

22. **Knowledge Governance Abstraction** (Day 20)
    - Copy from `symphainy_source`
    - Review for business logic
    - Remove if found

23. **Session Management Abstraction** (Day 21)
    - Copy from `symphainy_source`
    - Review for business logic
    - Remove if found

---

## Part 4: Supabase Setup Requirements

### Required Supabase Setup

**1. Database Schema (Already Exists)**
- ✅ `tenants` table
- ✅ `user_tenants` table
- ✅ RLS policies enabled

**2. Environment Variables (Required)**
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key  # REQUIRED for tenant queries
SUPABASE_JWKS_URL=https://your-project.supabase.co/.well-known/jwks.json  # Optional
SUPABASE_JWT_ISSUER=https://your-project.supabase.co  # Optional
```

**3. Service Key Requirement**
- ⚠️ **CRITICAL:** `SUPABASE_SERVICE_KEY` is required to query `user_tenants` table
- ⚠️ Without service key, adapter falls back to `user_metadata` (less reliable)
- ✅ **Adapter properly handles this** - Logs warning if service key missing

**4. RLS Policies (Already Configured)**
- ✅ RLS enabled on `tenants` table
- ✅ RLS enabled on `user_tenants` table
- ✅ RLS enabled on tenant-scoped tables (files, audit_logs, sessions)
- ✅ Policies enforce tenant isolation

### Adapter Tenancy Exposure

**✅ Adapter DOES Properly Expose Tenancy:**

1. **`get_user_tenant_info(user_id)` Method**
   - ✅ Queries `user_tenants` table (requires service key)
   - ✅ Returns: `tenant_id`, `roles`, `permissions`, `tenant_type`, `tenant_name`, `tenant_status`
   - ✅ Falls back to `user_metadata` if service key not available
   - ✅ **Properly exposes tenancy**

2. **Token Validation**
   - ✅ Validates JWT token
   - ✅ Extracts user_id from JWT
   - ✅ Calls `get_user_tenant_info()` to get tenant context
   - ✅ Returns user + tenant context

3. **Service Key Handling**
   - ✅ Logs warning if service key not available
   - ✅ Falls back to `user_metadata` gracefully
   - ✅ **Properly handles missing service key**

### What We Need to Lock In

**Before Finalizing Auth Abstraction:**

1. **Required Return Fields**
   ```python
   {
       "user_id": "uuid",           # Always available
       "email": "string",           # Always available
       "tenant_id": "uuid",         # From database or metadata
       "roles": ["string"],         # From database or metadata
       "permissions": ["string"]    # From database or metadata
   }
   ```

2. **Optional Return Fields**
   ```python
   {
       "phone": "string",           # Optional
       "full_name": "string",      # From user_metadata
       "created_at": "datetime",    # Available
       "last_sign_in_at": "datetime", # Available
       "email_confirmed_at": "datetime" # Available
   }
   ```

3. **Raw Provider Data (For Extensibility)**
   ```python
   {
       "raw_user_metadata": {},    # All custom fields
       "raw_app_metadata": {},     # System fields
       "raw_provider_data": {}     # All other fields (aud, confirmed_at, etc.)
   }
   ```

4. **Session Data (If Available)**
   ```python
   {
       "access_token": "string",   # If session available
       "refresh_token": "string",  # If session available
       "expires_in": "int",        # If session available
       "expires_at": "int"         # If session available
   }
   ```

---

## Part 5: Implementation Strategy

### Strategy: Copy + Refactor in Phases

**Phase 1 (Week 1): Critical Missing + Critical Fixes**
- Add 4 critical missing abstractions
- Fix 2 critical business logic issues (Auth, Tenant)
- **Result:** Runtime and Smart City can start using abstractions

**Phase 2 (Week 2): Important Missing**
- Add 5 important missing abstractions
- **Result:** All Smart City roles have required abstractions

**Phase 3 (Week 3): Moderate Fixes + Remaining**
- Fix minor business logic issues
- Add remaining abstractions
- **Result:** Complete abstraction layer

**Phase 4 (Week 4): Integration + Testing**
- Integrate with Runtime
- Integrate with Smart City roles
- Test swappability
- **Result:** Production-ready abstraction layer

### Copy Strategy for Each Abstraction

1. **Copy File** - Copy abstraction from `symphainy_source`
2. **Review for Business Logic** - Identify business logic
3. **Remove Business Logic** - Move to Smart City role or domain service
4. **Update Protocol** - Ensure protocol matches pure infrastructure pattern
5. **Test Swappability** - Verify can swap adapters
6. **Update Foundation Service** - Wire into Public Works Foundation

---

## Part 6: Success Criteria

### ✅ Abstractions Are Swappable

- ✅ Can swap Supabase → Auth0 without changing business logic
- ✅ Can swap GCS → S3 without changing business logic
- ✅ Can swap Redis → Kafka without changing business logic
- ✅ Can swap Meilisearch → Elasticsearch without changing business logic

### ✅ Business Logic in Right Place

- ✅ Tenant creation logic in City Manager
- ✅ Access validation logic in Security Guard
- ✅ Role/permission resolution in Security Guard
- ✅ Semantic schema management in Librarian
- ✅ Workflow definition/execution in Conductor

### ✅ Runtime/Smart City Can Use Abstractions

- ✅ Runtime uses abstractions via Smart City roles
- ✅ Smart City roles use abstractions for infrastructure
- ✅ No business logic in abstractions

### ✅ Librarian Role Clarified

- ✅ Librarian's role in data mash flow defined
- ✅ Librarian's responsibilities clear
- ✅ Librarian's abstraction requirements identified

### ✅ Supabase Tenancy Documented

- ✅ Supabase tenancy capabilities documented
- ✅ Adapter tenancy exposure verified
- ✅ Required fields locked in
- ✅ Extra fields documented

---

## Conclusion

**This is a comprehensive refactoring plan that addresses:**
1. ✅ **Abstraction Refactoring** - Remove business logic, make swappable
2. ✅ **Librarian Role** - Clarify role in data mash flow
3. ✅ **Supabase Tenancy** - Document capabilities and fields

**Timeline:** 3-4 weeks for complete refactoring

**Priority:** Start with Phase 1 (critical missing + critical fixes) to unblock Phase 2/3 implementation
