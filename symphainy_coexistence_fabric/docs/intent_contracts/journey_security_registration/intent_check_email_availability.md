# Intent Contract: check_email_availability

**Intent:** check_email_availability  
**Intent Type:** `check_email_availability`  
**Journey:** Journey Security Registration (`journey_security_registration`)  
**Realm:** Security Solution  
**Status:** IN PROGRESS  
**Priority:** PRIORITY 1

---

## 1. Intent Overview

### Purpose
Check if an email address is available for registration (not already registered). This is a check-only intent with no side effects.

### Intent Flow
```
[User enters email address]
    ↓
[check_email_availability intent executes]
    ↓
[Query user database for email]
    ↓
[Check if email exists]
    ↓
[Returns availability result (available/unavailable)]
```

### Expected Observable Artifacts
- **Availability Result:** Object with email availability status
  - `email: string` - Email address checked
  - `is_available: boolean` - Whether email is available
  - `message: string` - Human-readable message
  - No artifacts created (check only, no side effects)

---

## 2. Intent Parameters

### Required Parameters

| Parameter | Type | Description | Validation |
|-----------|------|-------------|------------|
| `email` | `string` | Email address to check | Required, valid email format (RFC 5322) |

### Optional Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| None | - | - | - |

### Context Metadata (from ExecutionContext)

| Metadata Key | Type | Description | Source |
|--------------|------|-------------|--------|
| `tenant_id` | `string` | Tenant identifier | Runtime (from session) |
| `session_id` | `string` | Session identifier | Runtime (from session) |

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
- **No artifacts registered** - This is a check-only intent with no side effects
- Availability results are returned in the response but not persisted

### Artifact Index Registration
- **No artifacts indexed** - Check-only intent

---

## 5. Idempotency

### Idempotency Key
```
N/A - No side effects, check only
```

### Scope
- N/A - No side effects, check only

### Behavior
- This intent has no side effects (no state changes, no artifacts created)
- Can be called multiple times with same email - always returns same availability result
- Idempotent by nature (pure check function)

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
// Frontend can call this intent before showing registration form
// Or call it in real-time as user types email (debounced)

const checkEmail = async (email: string) => {
  const executionId = await platformState.submitIntent(
    'check_email_availability',
    { email }
  );
  
  const status = await platformState.getExecutionStatus(executionId);
  if (status?.artifacts?.availability_result?.semantic_payload?.is_available) {
    // Email is available, proceed with registration
  } else {
    // Email is not available, show error
  }
};
```

### Expected Frontend Behavior
1. **Real-time checking (optional):** Frontend can check email availability as user types (debounced)
2. **Pre-submit checking:** Frontend checks email before allowing form submission
3. **Error display:** If email unavailable, show error message and prevent registration
4. **User guidance:** Suggest user to try logging in if email already exists

---

## 8. Error Handling

### Validation Errors
- **Missing email:** `ValueError("email is required")` -> Returns error response with `ERROR_CODE: "MISSING_PARAMETER"`
- **Invalid email format:** Email not RFC 5322 compliant -> Returns error response with `ERROR_CODE: "INVALID_EMAIL_FORMAT"`

### Runtime Errors
- **Database unavailable:** Cannot query user database -> Returns error response with `ERROR_CODE: "DATABASE_UNAVAILABLE"`
- **Auth service unavailable:** AuthAbstraction not available -> Returns error response with `ERROR_CODE: "AUTH_SERVICE_UNAVAILABLE"`

### Error Response Format
```json
{
  "error": "Error message",
  "error_code": "ERROR_CODE",
  "execution_id": "exec_abc123",
  "intent_type": "check_email_availability",
  "details": {
    "email": "invalid-email",
    "reason": "Invalid email format"
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
- `availability_result` - Required (availability check result artifact)

### Required Events
- `email_availability_checked` - Required (emitted when check completes)

### Lifecycle State
- **No lifecycle state** - This is a check-only intent with no artifacts created

### Contract Validation
- ✅ Intent must return availability result (email, is_available, message)
- ✅ No side effects (no artifacts created, no state changes)
- ✅ Idempotent (same input = same output)
- ✅ Email format validated
- ✅ Tenant-scoped query (checks email within tenant)

---

**Last Updated:** January 27, 2026  
**Owner:** Security Solution Team  
**Status:** ✅ **ENHANCED** - Ready for implementation
