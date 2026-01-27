# Intent Contract: authenticate_user

**Intent:** authenticate_user  
**Intent Type:** `authenticate_user`  
**Journey:** Journey Security Authentication (`journey_security_authentication`)  
**Realm:** Security Solution  
**Status:** IN PROGRESS  
**Priority:** PRIORITY 1

---

## 1. Intent Overview

### Purpose
Validate user credentials (email and password). Checks if user account exists, verifies password hash, and returns user account artifact. This is a validation-only intent with no side effects (does not create session).

### Intent Flow
```
[User enters credentials (email, password)]
    ↓
[authenticate_user intent executes]
    ↓
[Validates email format]
    ↓
[Validates password]
    ↓
[Queries user database for email]
    ↓
[Checks user account exists]
    ↓
[Verifies password hash (bcrypt/argon2)]
    ↓
[Returns user account artifact (if credentials valid)]
```

### Expected Observable Artifacts
- **User Account Artifact:** User account information (if credentials valid)
  - `user_id` - User identifier
  - `email` - User's email address
  - `name` - User's full name
  - `lifecycle_state` - Account lifecycle state (must be "ACTIVE")
  - No artifacts created (validation only, returns existing user account)

---

## 2. Intent Parameters

### Required Parameters

| Parameter | Type | Description | Validation |
|-----------|------|-------------|------------|
| `email` | `string` | User's email address | Required, valid email format (RFC 5322) |
| `password` | `string` | User's password (plain text) | Required, non-empty |

### Optional Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| None | - | - | - |

### Context Metadata (from ExecutionContext)

| Metadata Key | Type | Description | Source |
|--------------|------|-------------|--------|
| `tenant_id` | `string` | Tenant identifier | Runtime (required) |
| `session_id` | `string` | Session identifier | Runtime (optional, may not have session yet) |

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
- Returns existing user account artifact (does not create new artifacts)

### Artifact Index Registration
- **No artifacts indexed** - Validation-only intent

---

## 5. Idempotency

### Idempotency Key
```
idempotency_key = hash([key components])
```

### Scope
- [Describe scope: per tenant, per session, per artifact, etc.]

### Behavior
- [Describe idempotent behavior]

---

## 6. Implementation Details

### Handler Location
- **Old Implementation:** `symphainy_platform/civic_systems/experience/api/auth.py` (login endpoint)
- **New Implementation:** `symphainy_platform/realms/security/intent_services/authenticate_user_service.py` (to be created)

### Key Implementation Steps
1. **Extract Parameters:** Get `email` and `password` from intent parameters
2. **Validate Email Format:** Ensure email is valid (RFC 5322)
3. **Query User Database:** Use AuthAbstraction to query users table by email
   - Look up user with this email in the tenant
4. **Check User Exists:** If user not found, return authentication failure
5. **Verify Password:**
   - Get stored password hash from user record
   - Use bcrypt or argon2 to verify password against hash
   - If password doesn't match, return authentication failure
6. **Check Account Status:** Verify user account `lifecycle_state: "ACTIVE"`
   - If not ACTIVE (e.g., PENDING, TERMINATED), return authentication failure with reason
7. **Return User Account Artifact:**
   - If credentials valid: Return user account artifact (user_id, email, name, lifecycle_state)
   - If credentials invalid: Return authentication failure result

### Dependencies
- **Public Works:**
  - `AuthAbstraction` - For user authentication (`authenticate()`)
  - `SecurityGuardSDK` - For authentication and user context
- **State Surface:** None (no artifacts created)
- **Runtime:** `ExecutionContext` for tenant_id (for scoping user queries)

---

## 7. Frontend Integration

### Frontend Usage
```typescript
// From login-form.tsx - uses useAuth hook
const { login } = useAuth();

// Login flow
await login(email, password);

// AuthProvider handles:
// - Validation
// - Authentication
// - Authorization
// - Session creation
// - Redirect to platform
```

### Expected Frontend Behavior
1. **Form validation** - Frontend validates email and password before submission
2. **Authentication** - Frontend submits login, waits for authentication
3. **Error display** - If authentication fails, show error message ("Invalid email or password")
4. **Success handling** - If authentication succeeds, proceed to authorization and session creation
5. **Redirect** - After successful authentication and session creation, redirect to platform

---

## 8. Error Handling

### Validation Errors
- [Error type] -> [Error response]

### Runtime Errors
- [Error type] -> [Error response]

### Error Response Format
```json
{
  "error": "Error message",
  "error_code": "ERROR_CODE",
  "execution_id": "exec_abc123",
  "intent_type": "authenticate_user"
}
```

---

## 9. Testing & Validation

### Happy Path
1. User enters valid credentials (`email: "john@example.com"`, `password: "SecurePass123!"`)
2. `authenticate_user` intent executes with email and password
3. User account found in database (`user_id: "user_abc123"`, `lifecycle_state: "ACTIVE"`)
4. Password hash verified (password matches stored hash)
5. Returns user account artifact (`user_id`, `email`, `name`, `lifecycle_state: "ACTIVE"`)
6. Frontend proceeds to authorization and session creation

### Boundary Violations
- **Invalid email format:** Email not RFC 5322 compliant -> Returns `ERROR_CODE: "INVALID_EMAIL_FORMAT"`
- **User not found:** Email does not exist -> Returns authentication failure (`authenticated: false`)
- **Invalid password:** Password doesn't match -> Returns authentication failure (`authenticated: false`)
- **Account not active:** User account `lifecycle_state` is not "ACTIVE" -> Returns authentication failure (`authenticated: false`, `reason: "Account not active"`)

### Failure Scenarios
- **Database unavailable:** Cannot query user database -> Returns `ERROR_CODE: "DATABASE_UNAVAILABLE"`, frontend shows error and allows retry
- **Password hashing failure:** Cannot verify password hash -> Returns `ERROR_CODE: "PASSWORD_VERIFICATION_FAILED"`, frontend shows error
- **Account locked:** Account is locked (too many failed attempts) -> Returns authentication failure (`authenticated: false`, `reason: "Account locked"`)

---

## 10. Contract Compliance

### Required Artifacts
- `user_account` - Required (if authentication succeeds)
- `authentication_result` - Required (if authentication fails)

### Required Events
- `authentication_succeeded` - Required (when credentials are valid)
- `authentication_failed` - Required (when credentials are invalid)

### Lifecycle State
- **No lifecycle state** - This is a validation-only intent with no artifacts created
- **User account lifecycle state** - Must be "ACTIVE" for authentication to succeed

### Contract Validation
- ✅ Intent must return user account artifact if credentials valid
- ✅ Intent must return authentication failure if credentials invalid
- ✅ No side effects (no artifacts created, no state changes)
- ✅ Idempotent (same input = same output)
- ✅ Password verification must use secure hashing (bcrypt/argon2)

---

**Last Updated:** January 27, 2026  
**Owner:** Security Solution Team  
**Status:** ✅ **ENHANCED** - Ready for implementation
