# Smart City & Abstractions Refactoring - Current State Assessment

**Date:** January 2026  
**Status:** 📋 **ASSESSMENT IN PROGRESS**  
**Purpose:** Document current state before refactoring

---

## Current Smart City Services

### Location
- **Current:** `symphainy_platform/smart_city/services/` ❌ (WRONG)
- **Target:** `civic_systems/smart_city/roles/` ✅ (CORRECT)

### Services Inventory

| Service | Location | Protocol Compliance | Current State |
|---------|----------|---------------------|---------------|
| Security Guard | `symphainy_platform/smart_city/services/security_guard/` | ❌ No (placeholder) | Has business logic (tenant creation, role extraction, SecurityContext creation) |
| City Manager | `symphainy_platform/smart_city/services/city_manager/` | ✅ Yes | Implements SmartCityServiceProtocol |
| Data Steward | `symphainy_platform/smart_city/services/data_steward/` | ✅ Yes | Implements SmartCityServiceProtocol |
| Librarian | `symphainy_platform/smart_city/services/librarian/` | ✅ Yes | Implements SmartCityServiceProtocol |
| Traffic Cop | `symphainy_platform/smart_city/services/traffic_cop/` | ✅ Yes | Implements SmartCityServiceProtocol |
| Post Office | `symphainy_platform/smart_city/services/post_office/` | ✅ Yes | Implements SmartCityServiceProtocol |
| Conductor | `symphainy_platform/smart_city/services/conductor/` | ✅ Yes | Implements SmartCityServiceProtocol |
| Nurse | `symphainy_platform/smart_city/services/nurse/` | ✅ Yes | Implements SmartCityServiceProtocol |

### Foundation Service
- **Location:** `symphainy_platform/smart_city/foundation_service.py`
- **Status:** Initializes all 8 services
- **Needs:** Move to `civic_systems/smart_city/foundation_service.py`

---

## Security Guard Current State (Detailed)

### Current Implementation
- **File:** `symphainy_platform/smart_city/services/security_guard/security_guard_service.py`
- **Status:** Placeholder with harvested business logic
- **Protocol:** Does NOT implement `SmartCityServiceProtocol`

### Business Logic Identified (Needs Separation)

**Policy Logic (→ Smart City Role):**
- `validate_tenant_access()` - Tenant isolation policy
- Auth validation decision logic

**Translation Logic (→ Platform SDK):**
- `_resolve_tenant()` - How tenant is resolved
- `_resolve_roles_permissions()` - How roles/permissions are extracted
- `SecurityContext` creation - How runtime-ready object is created

**Business Logic (→ Domain Service):**
- Tenant creation (should be in City Manager or domain service)
- Role assignment (should be in domain service)

### Methods to Refactor

1. `authenticate_user()` → Split into:
   - Auth Abstraction: `authenticate()` (raw data)
   - Security Guard: `evaluate_auth()` (policy decision)
   - Platform SDK: `resolve_security_context()` (translation)

2. `validate_token()` → Split into:
   - Auth Abstraction: `validate_token()` (raw data)
   - Security Guard: `evaluate_auth()` (policy decision)
   - Platform SDK: `resolve_security_context()` (translation)

3. `validate_tenant_access()` → Keep in Security Guard (policy logic)

4. `_resolve_tenant()` → Move to Platform SDK (translation logic)

5. `_resolve_roles_permissions()` → Move to Platform SDK (translation logic)

---

## Abstractions to Refactor

### Auth Abstraction
- **Location:** `symphainy_platform/foundations/public_works/abstractions/auth_abstraction.py`
- **Current Issues:**
  - Creates tenants (business logic)
  - Extracts roles (translation logic)
  - Creates SecurityContext (translation logic)
- **Target:** Return raw user data only

### Tenant Abstraction
- **Location:** `symphainy_platform/foundations/public_works/abstractions/tenant_abstraction.py`
- **Current Issues:**
  - Validates access (policy logic - should be in Security Guard)
  - Manages configuration (policy logic - should be in City Manager)
- **Target:** Return raw tenant data only

### Content Metadata Abstraction
- **Location:** `symphainy_platform/foundations/public_works/abstractions/content_metadata_abstraction.py`
- **Current Issues:** (Need to assess)
- **Target:** Return raw metadata only

### Semantic Search Abstraction
- **Location:** `symphainy_platform/foundations/public_works/abstractions/semantic_search_abstraction.py`
- **Current Issues:** (Need to assess)
- **Target:** Return raw search results only

### Workflow Orchestration Abstraction
- **Location:** `symphainy_platform/foundations/public_works/abstractions/workflow_orchestration_abstraction.py`
- **Current Issues:** (Need to assess)
- **Target:** Return raw workflow data only

---

## Migration Map (Initial)

### Policy Logic → Smart City Roles

| Abstraction | Policy Logic | Smart City Role | Method |
|------------|--------------|----------------|--------|
| Auth Abstraction | Auth validation | Security Guard | `evaluate_auth()` |
| Tenant Abstraction | Access validation | Security Guard | `validate_tenant_access()` |
| Tenant Abstraction | Policy enforcement | City Manager | `validate_policy()` |
| Session Abstraction | Session semantics | Traffic Cop | `get_session()` |
| Event Management Abstraction | Event routing | Post Office | `publish_event()` |
| Workflow Orchestration Abstraction | Workflow primitives | Conductor | `get_saga_primitives()` |

### Translation Logic → SDKs

| Abstraction | Translation Logic | SDK | Method |
|------------|-------------------|-----|--------|
| Auth Abstraction | Tenant resolution | Platform SDK | `resolve_security_context()` |
| Auth Abstraction | Role mapping | Platform SDK | `resolve_security_context()` |
| Auth Abstraction | Permission projection | Platform SDK | `resolve_security_context()` |
| Auth Abstraction | SecurityContext creation | Platform SDK | `resolve_security_context()` |
| Tenant Abstraction | Tenant creation logic | Platform SDK | `resolve_tenant()` |
| Content Metadata Abstraction | ID generation | Realm SDK | `translate_content_intent()` |
| Content Metadata Abstraction | Validation rules | Realm SDK | `translate_content_intent()` |

### Business Logic → Domain Services

| Abstraction | Business Logic | Domain Service |
|------------|----------------|----------------|
| Content Metadata Abstraction | Content processing | Content Realm |
| Semantic Search Abstraction | Document processing | Content Realm |
| Workflow Orchestration Abstraction | Workflow execution | Journey Realm |

---

## Next Steps

1. ✅ Complete assessment (this document)
2. ⏳ Review each abstraction in detail
3. ⏳ Create detailed migration map
4. ⏳ Start refactoring (Day 3+)

---

## Notes

- Security Guard is the most critical to refactor first (it's a placeholder)
- Other services already implement protocol but may need location change
- Need to create Platform SDK and Realm SDK foundations
- Need to ensure Runtime calls via SDK (not directly)
