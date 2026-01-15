# Security Guard Service - PLACEHOLDER

**Status:** 🟡 **PLACEHOLDER** - Will be fully implemented in Phase 3  
**Purpose:** Preserve business logic extracted from Auth and Tenant abstractions

---

## Business Logic Harvested

### From Auth Abstraction:

1. **Tenant Creation Logic**
   - Method: `_create_tenant_for_user()`
   - Location: `Auth Abstraction.authenticate()`
   - Harvested To: `SecurityGuard._resolve_tenant()`
   - **Note:** This should actually go to City Manager in Phase 3

2. **Role/Permission Extraction**
   - Method: Role extraction from `tenant_info` and `user_metadata`
   - Location: `Auth Abstraction.authenticate()`, `validate_token()`
   - Harvested To: `SecurityGuard._resolve_roles_permissions()`

3. **SecurityContext Creation**
   - Method: Creating `SecurityContext` from raw user data
   - Location: All Auth Abstraction methods
   - Harvested To: `SecurityGuard.authenticate_user()`, `validate_token()`

### From Tenant Abstraction:

1. **Access Validation Logic**
   - Method: `validate_tenant_access()`
   - Location: `Tenant Abstraction.validate_tenant_access()`
   - Harvested To: `SecurityGuard.validate_tenant_access()`

---

## Phase 3 TODO

When implementing Phase 3:

1. **Implement SmartCityServiceProtocol**
   - Make this a real Smart City role
   - Add protocol compliance

2. **Add MCP Tools**
   - Expose Security Guard capabilities as MCP tools
   - Enable agents to use Security Guard

3. **Add Telemetry**
   - Track authentication attempts
   - Track access validations

4. **Move Tenant Creation to City Manager**
   - `_resolve_tenant()` should call City Manager
   - City Manager owns tenant lifecycle

5. **Add Policy Engine Integration**
   - Integrate with Policy Abstraction
   - Add policy-based authorization

---

## Current Interface

```python
class SecurityGuardService:
    async def authenticate_user(credentials) -> SecurityContext
    async def validate_token(token) -> SecurityContext
    async def validate_tenant_access(user_tenant_id, resource_tenant_id) -> bool
    async def _resolve_tenant(user_id, raw_user_data) -> Optional[str]
    async def _resolve_roles_permissions(user_id, tenant_id) -> Tuple[List[str], List[str]]
```

---

## Usage

**Temporary (until Phase 3):**
```python
# Create placeholder
security_guard = SecurityGuardService(
    auth_abstraction=auth_abstraction,
    tenant_abstraction=tenant_abstraction
)

# Use for business logic
security_context = await security_guard.authenticate_user(credentials)
```

**Phase 3 (when real):**
```python
# Same interface, but now it's a real Smart City role
security_guard = SecurityGuardService(
    auth_abstraction=auth_abstraction,
    tenant_abstraction=tenant_abstraction
)

# Same usage
security_context = await security_guard.authenticate_user(credentials)
```
