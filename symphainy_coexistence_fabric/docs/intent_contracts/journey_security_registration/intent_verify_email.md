# Intent Contract: verify_email

**Intent:** verify_email  
**Intent Type:** `verify_email`  
**Journey:** Journey Security Registration (`journey_security_registration`)  
**Realm:** Security Solution  
**Status:** IN PROGRESS  
**Priority:** PRIORITY 1

---

## 1. Intent Overview

### Purpose
Verify a user's email address using a verification token. Validates the token, marks email as verified, and transitions user account lifecycle state from "PENDING" to "ACTIVE". This enables the user to authenticate.

### Intent Flow
```
[User clicks verification link in email]
    ↓
[verify_email intent executes with verification_token]
    ↓
[Validate verification token (exists, not expired, not used)]
    ↓
[Retrieve user account from token]
    ↓
[Mark email as verified in user account]
    ↓
[Transition user account lifecycle state (PENDING → ACTIVE)]
    ↓
[Mark token as used]
    ↓
[Returns user account artifact (lifecycle_state: ACTIVE)]
```

### Expected Observable Artifacts
- `artifact_id` - User account artifact identifier (user_id)
- `artifact_type: "user_account"`
- `lifecycle_state: "ACTIVE"` (transitioned from PENDING)
- `email_verified: true` - Email verification status
- `user_id` - User identifier
- `email` - User's email address
- Artifact Registry updated (State Surface)
- Users table updated (Supabase)

---

## 2. Intent Parameters

### Required Parameters

| Parameter | Type | Description | Validation |
|-----------|------|-------------|------------|
| `verification_token` | `string` | Verification token from email link | Required, must exist and be valid |

### Optional Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| None | - | - | - |

### Context Metadata (from ExecutionContext)

| Metadata Key | Type | Description | Source |
|--------------|------|-------------|--------|
| `tenant_id` | `string` | Tenant identifier | Runtime (from token or session) |
| `session_id` | `string` | Session identifier | Runtime (optional, may not have session yet) |

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
        "lifecycle_state": "ACTIVE",
        "email_verified": true,
        "verified_at": "2026-01-27T10:30:00Z"
      },
      "renderings": {
        "message": "Email verified successfully. You can now log in."
      }
    }
  },
  "events": [
    {
      "type": "email_verified",
      "user_id": "user_abc123",
      "email": "john@example.com",
      "lifecycle_state": "ACTIVE",
      "verified_at": "2026-01-27T10:30:00Z"
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
  "intent_type": "verify_email",
  "details": {
    "verification_token": "token_xyz789",
    "reason": "Token expired or invalid"
  }
}
```

---

## 4. Artifact Registration

### State Surface Registration
- **Artifact ID:** [How artifact_id is generated]
- **Artifact Type:** `"artifact_type"`
- **Lifecycle State:** `"PENDING"` or `"READY"`
- **Produced By:** `{ intent: "verify_email", execution_id: "<execution_id>" }`
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
idempotency_key = hash(verification_token)
```

### Scope
- Per verification token
- Same token = same verification result (idempotent)

### Behavior
- If token is already used, returns success with existing user account (idempotent)
- If token is expired, returns error (not idempotent - expired tokens cannot be reused)
- If token is invalid, returns error (not idempotent - invalid tokens cannot be reused)
- Prevents duplicate verification for the same token

---

## 6. Implementation Details

### Handler Location
- **New Implementation:** `symphainy_platform/realms/security/intent_services/verify_email_service.py` (to be created)

### Key Implementation Steps
1. **Extract Parameters:** Get `verification_token` from intent parameters
2. **Validate Token:**
   - Look up token in `verification_tokens` table or intent context
   - Check token exists
   - Check token not expired (`token_expires_at > now`)
   - Check token not already used (`used_at is null`)
3. **Retrieve User Account:**
   - Get `user_id` from token record
   - Retrieve user account from State Surface or Supabase
   - Verify user account exists and `lifecycle_state: "PENDING"`
4. **Update User Account:**
   - Update `lifecycle_state: "PENDING"` → `"ACTIVE"`
   - Update `email_verified: false` → `true`
   - Set `verified_at: <timestamp>`
5. **Update State Surface:**
   - Update user account artifact lifecycle state
   - Update semantic descriptor (email_verified: true)
6. **Update Supabase:**
   - Update `users` table with new lifecycle_state and email_verified
7. **Mark Token as Used:**
   - Update `verification_tokens` table: `used_at: <timestamp>`
8. **Return User Account Artifact:**
   - Return updated user account with `lifecycle_state: "ACTIVE"`, `email_verified: true`

### Dependencies
- **Public Works:**
  - `AuthAbstraction` - For token validation and user account updates
  - `TenantAbstraction` - For tenant-scoped operations
- **State Surface:**
  - `update_artifact_lifecycle()` - Update user account lifecycle state
  - `get_artifact()` - Retrieve user account artifact
- **Runtime:**
  - `ExecutionContext` - Tenant, session, execution context
  - Token storage - For looking up verification tokens

---

## 7. Frontend Integration

### Frontend Usage
```typescript
// Verification page (e.g., /verify-email?token=token_xyz789)
const verifyEmail = async (token: string) => {
  const executionId = await platformState.submitIntent(
    'verify_email',
    { verification_token: token }
  );
  
  const status = await platformState.getExecutionStatus(executionId);
  if (status?.status === "completed") {
    // Email verified, redirect to login
    router.push('/login?verified=true');
  } else {
    // Verification failed, show error
    setError(status?.error || "Verification failed");
  }
};
```

### Expected Frontend Behavior
1. **User clicks verification link** - Frontend navigates to verification page with token in URL
2. **Token extracted** - Frontend extracts token from URL query parameter
3. **Verification submitted** - Frontend submits `verify_email` intent with token
4. **Success handling** - If verification succeeds:
   - Show "Email verified successfully" message
   - Redirect to login page with success message
   - User can now authenticate
5. **Error handling** - If verification fails:
   - Show error message (token expired, invalid, etc.)
   - Provide "Resend verification email" option
   - Allow user to request new verification email

---

## 8. Error Handling

### Validation Errors
- **Missing verification_token:** `ValueError("verification_token is required")` -> Returns error response with `ERROR_CODE: "MISSING_PARAMETER"`
- **Invalid token format:** Token format invalid -> Returns error response with `ERROR_CODE: "INVALID_TOKEN_FORMAT"`

### Runtime Errors
- **Token not found:** Token does not exist in database -> Returns error response with `ERROR_CODE: "TOKEN_NOT_FOUND"`
- **Token expired:** Token expiration time has passed -> Returns error response with `ERROR_CODE: "TOKEN_EXPIRED"`
- **Token already used:** Token was already used for verification -> Returns success with existing user account (idempotent) OR error with `ERROR_CODE: "TOKEN_ALREADY_USED"`
- **User not found:** User account associated with token does not exist -> Returns error response with `ERROR_CODE: "USER_NOT_FOUND"`
- **User already verified:** User account already has `email_verified: true` -> Returns success with existing user account (idempotent)
- **Database unavailable:** Cannot update user account -> Returns error response with `ERROR_CODE: "DATABASE_UNAVAILABLE"`

### Error Response Format
```json
{
  "error": "Error message",
  "error_code": "ERROR_CODE",
  "execution_id": "exec_abc123",
  "intent_type": "verify_email",
  "details": {
    "verification_token": "token_xyz789",
    "reason": "Token expired or invalid"
  }
}
```

---

## 9. Testing & Validation

### Happy Path
1. User receives verification email with token (`token: "token_xyz789"`)
2. User clicks verification link (navigates to `/verify-email?token=token_xyz789`)
3. `verify_email` intent executes with `verification_token: "token_xyz789"`
4. Token validated (exists, not expired, not used)
5. User account retrieved (`user_id: "user_abc123"`, `lifecycle_state: "PENDING"`)
6. User account updated (`lifecycle_state: "PENDING"` → `"ACTIVE"`, `email_verified: true`)
7. Token marked as used (`used_at: <timestamp>`)
8. Returns user account with `lifecycle_state: "ACTIVE"`, `email_verified: true`
9. User redirected to login page
10. User can now authenticate

### Boundary Violations
- **Token not found:** Token does not exist -> Returns `ERROR_CODE: "TOKEN_NOT_FOUND"`
- **Token expired:** Token expiration time passed -> Returns `ERROR_CODE: "TOKEN_EXPIRED"`
- **Token already used:** Token was already used -> Returns success with existing user account (idempotent)
- **User already verified:** User already has `email_verified: true` -> Returns success with existing user account (idempotent)
- **User not in PENDING state:** User account not in PENDING state -> Returns error or success depending on current state

### Failure Scenarios
- **Database unavailable:** Cannot update user account -> Returns `ERROR_CODE: "DATABASE_UNAVAILABLE"`, frontend shows error and allows retry
- **Token lookup failure:** Cannot look up token -> Returns `ERROR_CODE: "TOKEN_LOOKUP_FAILED"`, frontend shows error
- **Partial update:** User account updated but token not marked as used -> User verified but token still usable (requires cleanup)

---

## 10. Contract Compliance

### Required Artifacts
- `user_account` - Required (updated user account artifact)

### Required Events
- `email_verified` - Required (emitted when email is verified)

### Lifecycle State
- **Initial State:** `"PENDING"` (user account before verification)
- **Final State:** `"ACTIVE"` (user account after verification)
- **Transition:** `"PENDING"` → `"ACTIVE"` (automatic after successful verification)

### Contract Validation
- ✅ Artifact must have `lifecycle_state: "ACTIVE"` after verification
- ✅ Artifact must have `email_verified: true` after verification
- ✅ User record must be updated in Supabase `users` table
- ✅ Artifact must be updated in State Surface
- ✅ Token must be marked as used
- ✅ Idempotent (same token = same result, already used tokens return success)

---

**Last Updated:** January 27, 2026  
**Owner:** Security Solution Team  
**Status:** ✅ **ENHANCED** - Ready for implementation
