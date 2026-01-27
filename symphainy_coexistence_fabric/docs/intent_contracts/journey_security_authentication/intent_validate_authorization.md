# Intent Contract: validate_authorization

**Intent:** validate_authorization  
**Intent Type:** `validate_authorization`  
**Journey:** Journey Security Authentication (`journey_security_authentication`)  
**Realm:** Security Solution  
**Status:** IN PROGRESS  
**Priority:** PRIORITY 1

---

## 1. Intent Overview

### Purpose
Check user permissions and roles after authentication. Validates that user account is ACTIVE, retrieves user roles and permissions, and validates user access rights. This is a validation-only intent with no side effects.

### Intent Flow
```
[User authenticated (authenticate_user succeeded)]
    ↓
[validate_authorization intent executes]
    ↓
[Checks user account lifecycle_state (must be ACTIVE)]
    ↓
[Retrieves user roles and permissions]
    ↓
[Validates user access rights]
    ↓
[Returns authorization status (authorized/unauthorized, roles, permissions)]
```

### Expected Observable Artifacts
- **Authorization Result:** Object with authorization status
  - `authorized: boolean` - Whether user is authorized
  - `roles: array` - User roles (e.g., ["user", "admin"])
  - `permissions: array` - User permissions (e.g., ["read:content", "write:content"])
  - `lifecycle_state: "ACTIVE"` - User account lifecycle state
  - No artifacts created (validation only, returns authorization status)

---

## 2. Intent Parameters

### Required Parameters

| Parameter | Type | Description | Validation |
|-----------|------|-------------|------------|
| `user_id` | `string` | User account identifier (from authenticate_user) | Required, must exist in State Surface |

### Optional Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `required_permissions` | `array<string>` | Required permissions for authorization check | `[]` (check all permissions) |
| `required_roles` | `array<string>` | Required roles for authorization check | `[]` (check all roles) |

### Context Metadata (from ExecutionContext)

| Metadata Key | Type | Description | Source |
|--------------|------|-------------|--------|
| `tenant_id` | `string` | Tenant identifier | Runtime (required) |
| `session_id` | `string` | Session identifier | Runtime (optional) |
| `user_account` | `object` | User account artifact (from authenticate_user) | Previous intent result |

---

## 3. Intent Returns

### Success Response

```json
{
  "artifacts": {
    "artifact_type": {
      "result_type": "artifact",
      "semantic_payload": {
        // Artifact data
      },
      "renderings": {}
    }
  },
  "events": [
    {
      "type": "event_type",
      // Event data
    }
  ]
}
```

### Error Response

```json
{
  "error": "Error message",
  "error_code": "ERROR_CODE",
  "execution_id": "exec_abc123"
}
```

---

## 4. Artifact Registration

### State Surface Registration
- **No artifacts registered** - This is a validation-only intent with no side effects
- Authorization results are returned in the response but not persisted

### Artifact Index Registration
- **No artifacts indexed** - Validation-only intent

---

## 5. Idempotency

### Idempotency Key
```
N/A - No side effects, validation only
```

### Scope
- N/A - No side effects, validation only

### Behavior
- This intent has no side effects (no state changes, no artifacts created)
- Can be called multiple times with same user_id - always returns same authorization result
- Idempotent by nature (pure validation function)

---

## 6. Implementation Details

### Handler Location
- **New Implementation:** `symphainy_platform/realms/security/intent_services/validate_authorization_service.py` (to be created)
- **Reference:** `symphainy_platform/civic_systems/smart_city/sdk/security_guard_sdk.py` (authorization logic)

### Key Implementation Steps
1. **Extract Parameters:** Get `user_id` from intent parameters
2. **Retrieve User Account:**
   - Get user account from State Surface or Supabase
   - Verify user account exists
3. **Check Lifecycle State:**
   - Verify `lifecycle_state: "ACTIVE"`
   - If not ACTIVE, return unauthorized (`authorized: false`, `reason: "Account not active"`)
4. **Retrieve Roles and Permissions:**
   - Use SecurityGuardSDK to get user roles and permissions
   - Query role/permission assignments for user
5. **Validate Access Rights:**
   - If `required_permissions` provided, check user has all required permissions
   - If `required_roles` provided, check user has all required roles
6. **Return Authorization Result:**
   - If authorized: `authorized: true`, `roles`, `permissions`
   - If unauthorized: `authorized: false`, `reason`

### Dependencies
- **Public Works:**
  - `SecurityGuardSDK` - For role and permission retrieval
  - `AuthAbstraction` - For user account lookup
- **State Surface:**
  - `get_artifact()` - Retrieve user account artifact
- **Runtime:**
  - `ExecutionContext` - Tenant, session, execution context

---

## 7. Frontend Integration

### Frontend Usage
```typescript
// After authentication, before session creation
const authorizationResult = await platformState.submitIntent(
  'validate_authorization',
  { user_id: userId }
);

if (authorizationResult.artifacts.authorization_result.semantic_payload.authorized) {
  // User is authorized, proceed to session creation
} else {
  // User is not authorized, show error
}
```

### Expected Frontend Behavior
1. **After authentication** - Frontend calls this intent after successful authentication
2. **Authorization check** - Frontend waits for authorization result
3. **Success handling** - If authorized, proceed to session creation
4. **Error handling** - If unauthorized, show error message and prevent login
5. **Role-based UI** - Frontend can use roles/permissions for UI customization

---

## 8. Error Handling

### Validation Errors
- **Missing user_id:** `ValueError("user_id is required")` -> Returns error response with `ERROR_CODE: "MISSING_PARAMETER"`
- **User not found:** User does not exist -> Returns error response with `ERROR_CODE: "USER_NOT_FOUND"`

### Runtime Errors
- **Account not active:** User account `lifecycle_state` is not "ACTIVE" -> Returns unauthorized (`authorized: false`, `reason: "Account not active"`)
- **Insufficient permissions:** User doesn't have required permissions -> Returns unauthorized (`authorized: false`, `reason: "Insufficient permissions"`)
- **Insufficient roles:** User doesn't have required roles -> Returns unauthorized (`authorized: false`, `reason: "Insufficient roles"`)
- **Security service unavailable:** SecurityGuardSDK not available -> Returns error response with `ERROR_CODE: "SECURITY_SERVICE_UNAVAILABLE"`

### Error Response Format
```json
{
  "error": "Error message",
  "error_code": "ERROR_CODE",
  "execution_id": "exec_abc123",
  "intent_type": "validate_authorization",
  "details": {
    "user_id": "user_abc123",
    "reason": "Security service unavailable"
  }
}
```

---

## 9. Testing & Validation

### Happy Path
1. User authenticated (`user_id: "user_abc123"`, `lifecycle_state: "ACTIVE"`)
2. `validate_authorization` intent executes with `user_id`
3. User account retrieved (`lifecycle_state: "ACTIVE"`)
4. Roles and permissions retrieved (`roles: ["user", "content_editor"]`, `permissions: ["read:content", "write:content"]`)
5. Access rights validated (user has required permissions/roles)
6. Returns `authorized: true`, `roles`, `permissions`
7. Frontend proceeds to session creation

### Boundary Violations
- **User not found:** User does not exist -> Returns `ERROR_CODE: "USER_NOT_FOUND"`
- **Account not active:** User account `lifecycle_state` is not "ACTIVE" -> Returns unauthorized (`authorized: false`, `reason: "Account not active"`)
- **Insufficient permissions:** User doesn't have required permissions -> Returns unauthorized (`authorized: false`, `reason: "Insufficient permissions"`)

### Failure Scenarios
- **Security service unavailable:** SecurityGuardSDK not available -> Returns `ERROR_CODE: "SECURITY_SERVICE_UNAVAILABLE"`, frontend shows error
- **Role/permission lookup failure:** Cannot retrieve roles/permissions -> Returns `ERROR_CODE: "ROLE_LOOKUP_FAILED"`, frontend shows error

---

## 10. Contract Compliance

### Required Artifacts
- `authorization_result` - Required (authorization check result artifact)

### Required Events
- `authorization_succeeded` - Required (when user is authorized)
- `authorization_failed` - Required (when user is not authorized)

### Lifecycle State
- **No lifecycle state** - This is a validation-only intent with no artifacts created
- **User account lifecycle state** - Must be "ACTIVE" for authorization to succeed

### Contract Validation
- ✅ Intent must return authorization result (authorized, roles, permissions)
- ✅ No side effects (no artifacts created, no state changes)
- ✅ Idempotent (same input = same output)
- ✅ User account lifecycle state must be checked
- ✅ Roles and permissions must be retrieved and validated

---

**Last Updated:** January 27, 2026  
**Owner:** Security Solution Team  
**Status:** ✅ **ENHANCED** - Ready for implementation
