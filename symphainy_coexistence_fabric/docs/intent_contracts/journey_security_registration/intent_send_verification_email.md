# Intent Contract: send_verification_email

**Intent:** send_verification_email  
**Intent Type:** `send_verification_email`  
**Journey:** Journey Security Registration (`journey_security_registration`)  
**Realm:** Security Solution  
**Status:** IN PROGRESS  
**Priority:** PRIORITY 1

---

## 1. Intent Overview

### Purpose
Send email verification to a newly registered user. Generates a verification token, stores it in intent context, and sends verification email with a link. This intent is only executed if email verification is enabled for the tenant.

### Intent Flow
```
[User account created (lifecycle_state: PENDING)]
    ↓
[send_verification_email intent executes]
    ↓
[Generate verification token (UUID, time-limited)]
    ↓
[Store token in intent context (associated with user_id)]
    ↓
[Send verification email with verification link]
    ↓
[Returns confirmation (email sent, token stored)]
```

### Expected Observable Artifacts
- **Verification Token:** Generated token stored in intent context
  - `verification_token: string` - Unique token (UUID format)
  - `token_expires_at: timestamp` - Token expiration time (e.g., 24 hours)
  - `user_id: string` - Associated user ID
- **Email Sent Confirmation:** Confirmation that email was sent
  - `email_sent: boolean` - Whether email was successfully sent
  - `email_address: string` - Email address verification was sent to
  - No artifacts created (email sending only, token stored in context)

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
    "verification_email": {
      "result_type": "verification_email",
      "semantic_payload": {
        "user_id": "user_abc123",
        "email": "john@example.com",
        "email_sent": true,
        "verification_token": "token_xyz789",
        "token_expires_at": "2026-01-28T10:00:00Z",
        "verification_url": "https://platform.example.com/verify-email?token=token_xyz789"
      },
      "renderings": {
        "message": "Verification email sent to john@example.com"
      }
    }
  },
  "events": [
    {
      "type": "verification_email_sent",
      "user_id": "user_abc123",
      "email": "john@example.com",
      "token_expires_at": "2026-01-28T10:00:00Z"
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
  "intent_type": "send_verification_email",
  "details": {
    "user_id": "user_abc123",
    "reason": "Email service unavailable"
  }
}
```

---

## 4. Artifact Registration

### State Surface Registration
- **Artifact ID:** [How artifact_id is generated]
- **Artifact Type:** `"artifact_type"`
- **Lifecycle State:** `"PENDING"` or `"READY"`
- **Produced By:** `{ intent: "send_verification_email", execution_id: "<execution_id>" }`
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
idempotency_key = hash(user_id + email + timestamp_window)
```

### Scope
- Per user, per time window (e.g., per hour)
- Same user + email + time window = same verification email (prevents spam)

### Behavior
- If verification email was sent recently (within time window, e.g., 1 hour), returns existing token instead of sending new email
- Prevents email spam and token flooding
- User can request new verification email after time window expires

---

## 6. Implementation Details

### Handler Location
[Path to handler implementation]

### Key Implementation Steps
1. [Step 1]
2. [Step 2]
3. [Step 3]

### Dependencies
- **Public Works:** [Abstractions needed]
- **State Surface:** [Methods needed]
- **Runtime:** [Context requirements]

---

## 7. Frontend Integration

### Frontend Usage
```typescript
// After account creation, if email verification required
if (emailVerificationRequired) {
  const executionId = await platformState.submitIntent(
    'send_verification_email',
    {
      user_id: userId,
      email: email
    }
  );
  
  // Show "Check your email" message
  // Redirect to login page
}
```

### Expected Frontend Behavior
1. **After account creation** - If email verification required, frontend automatically calls this intent
2. **Email sent confirmation** - Frontend shows "Check your email" message
3. **Redirect to login** - User redirected to login page with message about email verification
4. **Resend option** - Frontend can provide "Resend verification email" button (calls intent again after time window)
5. **Email verification page** - Frontend has verification page that handles verification link clicks

---

## 8. Error Handling

### Validation Errors
- **Missing user_id:** `ValueError("user_id is required")` -> Returns error response with `ERROR_CODE: "MISSING_PARAMETER"`
- **Missing email:** `ValueError("email is required")` -> Returns error response with `ERROR_CODE: "MISSING_PARAMETER"`
- **User not found:** User does not exist -> Returns error response with `ERROR_CODE: "USER_NOT_FOUND"`

### Runtime Errors
- **Email service unavailable:** Cannot send email -> Returns error response with `ERROR_CODE: "EMAIL_SERVICE_UNAVAILABLE"`
- **Token storage failure:** Cannot store verification token -> Returns error response with `ERROR_CODE: "TOKEN_STORAGE_FAILED"`
- **Email verification disabled:** Email verification not enabled for tenant -> Returns success without sending email (no-op)

### Error Response Format
```json
{
  "error": "Error message",
  "error_code": "ERROR_CODE",
  "execution_id": "exec_abc123",
  "intent_type": "send_verification_email",
  "details": {
    "user_id": "user_abc123",
    "reason": "Email service unavailable"
  }
}
```

---

## 9. Testing & Validation

### Happy Path
1. [Step 1]
2. [Step 2]

### Boundary Violations
- [Violation type] -> [Expected behavior]

### Failure Scenarios
- [Failure type] -> [Expected behavior]

---

## 10. Contract Compliance

### Required Artifacts
- `verification_email` - Required (verification email confirmation artifact)

### Required Events
- `verification_email_sent` - Required (emitted when email is sent)

### Lifecycle State
- **No lifecycle state** - This intent does not create artifacts with lifecycle states
- **Token expiration** - Tokens have expiration timestamps, not lifecycle states

### Contract Validation
- ✅ Intent must return verification email confirmation (email_sent, verification_token, token_expires_at)
- ✅ Verification token must be stored (in intent context or temporary table)
- ✅ Verification email must be sent (if email service available)
- ✅ Idempotent (same user + email + time window = same token)
- ✅ Token expiration must be set (default: 24 hours)

---

**Last Updated:** January 27, 2026  
**Owner:** Security Solution Team  
**Status:** ✅ **ENHANCED** - Ready for implementation
