# Smart City Service Abstraction Requirements

**Date:** January 2026  
**Status:** 📋 **REQUIREMENTS DEFINED**

---

## Service → Abstraction Mapping

### 1. Librarian Service
**Needs:** `SemanticSearchAbstraction`
- **Adapter:** MeilisearchAdapter
- **Protocol:** SemanticSearchProtocol
- **Methods:** `search()`, `index_document()`, `delete_document()`

### 2. Data Steward Service
**Needs:** `FileStorageAbstraction`
- **Adapters:** GCSFileAdapter (storage) + SupabaseAdapter (metadata)
- **Protocol:** FileStorageProtocol
- **Methods:** `upload_file()`, `download_file()`, `delete_file()`, `list_files()`

### 3. Security Guard Service
**Needs:**
- `AuthenticationAbstraction` (from SupabaseAdapter)
- `AuthorizationAbstraction` (from SupabaseAdapter)
- `TenancyAbstraction` (from SupabaseAdapter)
- **Protocols:** AuthenticationProtocol, AuthorizationProtocol, TenancyProtocol
- **Methods:**
  - Auth: `authenticate()`, `validate_token()`
  - Authz: `check_permission()`, `get_user_permissions()`
  - Tenancy: `get_tenant()`, `validate_tenant_access()`

### 4. Other Services
- **Nurse:** Uses telemetry (already have OTel Collector)
- **Post Office:** Uses messaging (can use Redis pub/sub via StateManagementAbstraction)
- **Conductor:** Uses workflow state (can use StateManagementAbstraction)
- **Traffic Cop:** Uses session state (can use StateManagementAbstraction)
- **City Manager:** Uses service discovery (already have ServiceDiscoveryAbstraction)

---

## Implementation Priority

1. **HIGH:** SemanticSearchAbstraction (Librarian)
2. **HIGH:** FileStorageAbstraction (Data Steward)
3. **HIGH:** AuthAbstraction, AuthorizationAbstraction, TenancyAbstraction (Security Guard)
4. **MEDIUM:** Other abstractions as needed

---

## Next Steps

1. Adapt existing implementations to new architecture
2. Update Public Works Foundation
3. Wire into Smart City services
