# Intent Contract: create_user_account

**Intent:** create_user_account  
**Intent Type:** `create_user_account`  
**Journey:** Journey Security Registration (`journey_security_registration`)  
**Realm:** Security Solution  
**Status:** IN PROGRESS  
**Priority:** PRIORITY 1

---

## 1. Intent Overview

### Purpose
Create a new user account in the platform. User account is registered in State Surface (ArtifactRegistry) and indexed in Supabase (users table). Password is hashed (never stored in plain text). Account lifecycle state is "PENDING" if email verification is required, or "ACTIVE" if email verification is disabled.

### Intent Flow
```
[User registration data validated]
    ↓
[create_user_account intent executes]
    ↓
[Hash password (bcrypt/argon2)]
    ↓
[Create user account record]
    ↓
[Register user account artifact in State Surface (lifecycle_state: PENDING or ACTIVE)]
    ↓
[Index user in Supabase (users table)]
    ↓
[Returns user_account artifact (user_id, email, name, lifecycle_state)]
```

### Expected Observable Artifacts
- `artifact_id` - User account artifact identifier (user_id)
- `artifact_type: "user_account"`
- `lifecycle_state: "PENDING"` (if email verification required) or `"ACTIVE"` (if not required)
- `user_id` - User identifier
- `email` - User's email address
- `name` - User's full name
- `password_hash` - Hashed password (never plain text)
- Artifact registered in State Surface (ArtifactRegistry)
- User record created in Supabase (users table)

---

## 2. Intent Parameters

### Required Parameters

| Parameter | Type | Description | Validation |
|-----------|------|-------------|------------|
| `parameter_name` | `type` | Description | Validation rules |

### Optional Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `parameter_name` | `type` | Description | Default value |

### Context Metadata (from ExecutionContext)

| Metadata Key | Type | Description | Source |
|--------------|------|-------------|--------|
| `metadata_key` | `type` | Description | Runtime |

---

## 3. Intent Returns

### Success Response

```json
{
  "artifacts": {
    "user_account": {
      "result_type": "user_account",
      "semantic_payload": {
        "user_id": "user_abc123",
        "email": "john@example.com",
        "name": "John Doe",
        "lifecycle_state": "PENDING",
        "email_verification_required": true,
        "created_at": "2026-01-27T10:00:00Z"
      },
      "renderings": {
        "message": "User account created successfully. Please check your email for verification."
      }
    }
  },
  "events": [
    {
      "type": "user_account_created",
      "user_id": "user_abc123",
      "email": "john@example.com",
      "lifecycle_state": "PENDING",
      "email_verification_required": true
    }
  ]
}
```

### Error Response

```json
{
  "error": "Error message",
  "error_code": "ERROR_CODE",
  "execution_id": "exec_abc123",
  "intent_type": "create_user_account",
  "details": {
    "email": "existing@example.com",
    "reason": "Email already registered"
  }
}
```

---

## 4. Artifact Registration

### State Surface Registration
- **Artifact ID:** [How artifact_id is generated]
- **Artifact Type:** `"artifact_type"`
- **Lifecycle State:** `"PENDING"` or `"READY"`
- **Produced By:** `{ intent: "create_user_account", execution_id: "<execution_id>" }`
- **Semantic Descriptor:** [Descriptor details]
- **Parent Artifacts:** [List of parent artifact IDs]
- **Materializations:** [List of materializations]

### Artifact Index Registration
- Indexed in Supabase `artifact_index` table
- Includes: [List of indexed fields]

---

## 5. Idempotency

### Idempotency Key
```
idempotency_key = hash(email + tenant_id)
```

### Scope
- Per tenant, per email
- Same email + tenant = same user account artifact

### Behavior
- If a user account already exists with the same email in the same tenant, returns existing user account (idempotent)
- Prevents duplicate account creation for the same email
- Different tenants can have users with the same email (multi-tenant isolation)

---

## 6. Implementation Details

### Handler Location
- **Old Implementation:** `symphainy_platform/civic_systems/experience/api/auth.py` (register endpoint, line ~217)
- **New Implementation:** `symphainy_platform/realms/security/intent_services/create_user_account_service.py` (to be created)

### Key Implementation Steps
1. **Validate Parameters:** Ensure `name`, `email`, `password` are provided and valid
2. **Check Email Availability:** Verify email is not already registered (idempotency check)
   - If email exists, return existing user account (idempotent)
3. **Hash Password:** Use bcrypt or argon2 to hash password
   - Never store plain text password
   - Store only password hash
4. **Determine Lifecycle State:**
   - If `email_verification_required: true`: `lifecycle_state: "PENDING"`
   - If `email_verification_required: false`: `lifecycle_state: "ACTIVE"`
5. **Create User Account:**
   - Generate `user_id` (UUID format)
   - Create user record in Supabase `users` table with:
     - `user_id`, `email`, `name`, `password_hash`, `lifecycle_state`, `tenant_id`, `email_verified`
6. **Register Artifact in State Surface:**
   - Register user account artifact with:
     - `artifact_id: user_id`
     - `artifact_type: "user_account"`
     - `lifecycle_state: "PENDING"` or `"ACTIVE"`
     - `semantic_descriptor` (schema, email, name, email_verified)
7. **Return User Account Artifact:**
   - Return `user_id`, `email`, `name`, `lifecycle_state`, `email_verification_required`

### Dependencies
- **Public Works:**
  - `AuthAbstraction` - For user registration (`register_user()`)
  - `SecurityGuardSDK` - For user registration and role/permission assignment
- **State Surface:**
  - `register_artifact()` - Register user account artifact
- **Runtime:**
  - `ExecutionContext` - Tenant, session, execution context
  - Tenant config - For email verification settings

---

## 7. Frontend Integration

### Frontend Usage
```typescript
// [Frontend code example]
```

### Expected Frontend Behavior
1. [Behavior 1]
2. [Behavior 2]

---

## 8. Error Handling

### Validation Errors
- **Missing required parameter:** `ValueError("name/email/password is required")` -> Returns error response with `ERROR_CODE: "MISSING_PARAMETER"`
- **Invalid email format:** Email not RFC 5322 compliant -> Returns error response with `ERROR_CODE: "INVALID_EMAIL_FORMAT"`
- **Password too weak:** Password doesn't meet complexity requirements -> Returns error response with `ERROR_CODE: "WEAK_PASSWORD"`

### Runtime Errors
- **Email already registered:** Email exists in database -> Returns existing user account (idempotent) OR error with `ERROR_CODE: "EMAIL_ALREADY_REGISTERED"`
- **Database unavailable:** Cannot create user record -> Returns error response with `ERROR_CODE: "DATABASE_UNAVAILABLE"`
- **Password hashing failure:** Password hashing fails -> Returns error response with `ERROR_CODE: "PASSWORD_HASHING_FAILED"`
- **Auth service unavailable:** AuthAbstraction not available -> Returns error response with `ERROR_CODE: "AUTH_SERVICE_UNAVAILABLE"`

### Error Response Format
```json
{
  "error": "Error message",
  "error_code": "ERROR_CODE",
  "execution_id": "exec_abc123",
  "intent_type": "create_user_account",
  "details": {
    "email": "existing@example.com",
    "reason": "Email already registered"
  }
}
```

---

## 9. Testing & Validation

### Happy Path (Email Verification Disabled)
1. User enters valid registration data (name, email, password)
2. `create_user_account` intent executes
3. Email availability checked (email not found)
4. Password hashed (bcrypt/argon2)
5. User account created in Supabase (users table)
6. User account artifact registered in State Surface (`lifecycle_state: "ACTIVE"`)
7. Returns `user_id`, `email`, `name`, `lifecycle_state: "ACTIVE"`
8. User can immediately authenticate

### Happy Path (Email Verification Enabled)
1. User enters valid registration data
2. `create_user_account` intent executes
3. Email availability checked
4. Password hashed
5. User account created (`lifecycle_state: "PENDING"`)
6. User account artifact registered (`lifecycle_state: "PENDING"`)
7. Returns `user_id`, `email`, `name`, `lifecycle_state: "PENDING"`, `email_verification_required: true`
8. User must verify email before authenticating

### Boundary Violations
- **Email already registered:** Email exists -> Returns existing user account (idempotent) OR `ERROR_CODE: "EMAIL_ALREADY_REGISTERED"`
- **Invalid email format:** Email not RFC 5322 compliant -> Returns `ERROR_CODE: "INVALID_EMAIL_FORMAT"`
- **Weak password:** Password doesn't meet complexity -> Returns `ERROR_CODE: "WEAK_PASSWORD"`

### Failure Scenarios
- **Database unavailable:** Cannot create user record -> Returns `ERROR_CODE: "DATABASE_UNAVAILABLE"`, frontend shows error and allows retry
- **Password hashing failure:** Hashing algorithm fails -> Returns `ERROR_CODE: "PASSWORD_HASHING_FAILED"`, frontend shows error and allows retry
- **Partial creation:** User created in database but artifact registration fails -> User exists but artifact not registered, requires manual cleanup

---

## 10. Contract Compliance

### Required Artifacts
- `user_account` - Required (user account artifact)

### Required Events
- `user_account_created` - Required (emitted when account is created)

### Lifecycle State
- **Initial State:** `"PENDING"` (if email verification required) or `"ACTIVE"` (if not required)
- **Final State:** `"ACTIVE"` (after email verification, if required)
- **Transition:** `"PENDING"` → `"ACTIVE"` (via `verify_email` intent, if email verification was required)

### Contract Validation
- ✅ Artifact must have `user_id`, `email`, `name` in semantic_payload
- ✅ Password must be hashed (never plain text)
- ✅ User record must be created in Supabase `users` table
- ✅ Artifact must be registered in State Surface
- ✅ Lifecycle state must match email verification requirement
- ✅ Idempotent (same email + tenant = same user account)

---

**Last Updated:** January 27, 2026  
**Owner:** Security Solution Team  
**Status:** ✅ **ENHANCED** - Ready for implementation
