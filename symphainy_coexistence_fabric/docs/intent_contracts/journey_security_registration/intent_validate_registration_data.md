# Intent Contract: validate_registration_data

**Intent:** validate_registration_data  
**Intent Type:** `validate_registration_data`  
**Journey:** Journey Security Registration (`journey_security_registration`)  
**Realm:** Security Solution  
**Status:** IN PROGRESS  
**Priority:** PRIORITY 1

---

## 1. Intent Overview

### Purpose
Validate registration form data (name, email, password, confirm password) before proceeding with account creation. This is a validation-only intent with no side effects.

### Intent Flow
```
[User enters registration data]
    ↓
[validate_registration_data intent executes]
    ↓
[Validates name format]
    ↓
[Validates email format]
    ↓
[Validates password complexity]
    ↓
[Validates password match]
    ↓
[Returns validation result (valid/invalid, error messages)]
```

### Expected Observable Artifacts
- **Validation Result:** Object with validation status and error messages
  - `is_valid: boolean` - Overall validation status
  - `errors: object` - Field-specific error messages
  - No artifacts created (validation only, no side effects)

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

### Success Response (Validation Passed)

```json
{
  "artifacts": {
    "validation_result": {
      "result_type": "validation",
      "semantic_payload": {
        "is_valid": true,
        "errors": {}
      },
      "renderings": {
        "message": "All fields are valid"
      }
    }
  },
  "events": [
    {
      "type": "validation_passed",
      "fields_validated": ["name", "email", "password", "confirm_password"]
    }
  ]
}
```

### Success Response (Validation Failed)

```json
{
  "artifacts": {
    "validation_result": {
      "result_type": "validation",
      "semantic_payload": {
        "is_valid": false,
        "errors": {
          "name": "Name must be between 2 and 100 characters",
          "email": "Invalid email format",
          "password": "Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character",
          "confirm_password": "Passwords do not match"
        }
      },
      "renderings": {
        "message": "Validation failed"
      }
    }
  },
  "events": [
    {
      "type": "validation_failed",
      "errors": {
        "name": "Name must be between 2 and 100 characters",
        "email": "Invalid email format"
      }
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
  "intent_type": "validate_registration_data"
}
```

---

## 4. Artifact Registration

### State Surface Registration
- **Artifact ID:** [How artifact_id is generated]
- **Artifact Type:** `"artifact_type"`
- **Lifecycle State:** `"PENDING"` or `"READY"`
- **Produced By:** `{ intent: "validate_registration_data", execution_id: "<execution_id>" }`
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
N/A - No side effects, validation only
```

### Scope
- N/A - No side effects, validation only

### Behavior
- This intent has no side effects (no state changes, no artifacts created)
- Can be called multiple times with same parameters - always returns same validation result
- Idempotent by nature (pure validation function)

---

## 6. Implementation Details

### Handler Location
- **New Implementation:** `symphainy_platform/realms/security/intent_services/validate_registration_data_service.py` (to be created)
- **Frontend Reference:** `symphainy-frontend/components/auth/register-form.tsx` (uses `useServiceLayerAPI` for validation)

### Key Implementation Steps
1. **Extract Parameters:** Get `name`, `email`, `password`, `confirm_password` from intent parameters
2. **Validate Name:**
   - Check non-empty
   - Check length (2-100 characters)
   - Check format (alphanumeric and spaces only)
3. **Validate Email:**
   - Check non-empty
   - Validate email format (RFC 5322 compliant)
4. **Validate Password:**
   - Check non-empty
   - Check minimum length (8 characters)
   - Check complexity (at least one uppercase, one lowercase, one number, one special character)
5. **Validate Password Match:**
   - Check `password` matches `confirm_password`
6. **Return Validation Result:**
   - If all valid: `is_valid: true`, `errors: {}`
   - If any invalid: `is_valid: false`, `errors: {field: "error_message"}`

### Dependencies
- **Public Works:** None (pure validation, no infrastructure access)
- **State Surface:** None (no artifacts created)
- **Runtime:** `ExecutionContext` for tenant_id and session_id (for logging/telemetry only)

---

## 7. Frontend Integration

### Frontend Usage
```typescript
// From register-form.tsx - uses useServiceLayerAPI hook
const { validateName, validateEmail, validatePassword } = useServiceLayerAPI();

// Validation happens client-side before submit
const nameValidation = validateName(name);
const emailValidation = validateEmail(email);
const passwordValidation = validatePassword(password);

if (!nameValidation.isValid) {
  setErrors({ name: nameValidation.message });
}
if (!emailValidation.isValid) {
  setErrors({ email: emailValidation.message });
}
if (!passwordValidation.isValid) {
  setErrors({ password: passwordValidation.message });
}
if (password !== confirmPassword) {
  setErrors({ confirmPassword: "Passwords do not match" });
}
```

### Expected Frontend Behavior
1. **Client-side validation** - Frontend validates fields before submitting registration
2. **Real-time feedback** - Validation errors shown as user types (optional enhancement)
3. **Form submission blocked** - If validation fails, form submission is prevented
4. **Error display** - Field-specific error messages displayed below each input field
5. **Server-side validation** - Intent can be called server-side for additional validation if needed

---

## 8. Error Handling

### Validation Errors
- **Missing required parameter:** `ValueError("name is required")` -> Returns error response with `ERROR_CODE: "MISSING_PARAMETER"`
- **Invalid parameter type:** Parameter not a string -> Returns error response with `ERROR_CODE: "INVALID_PARAMETER_TYPE"`

### Runtime Errors
- **Validation service unavailable:** Validation logic fails -> Returns error response with `ERROR_CODE: "VALIDATION_SERVICE_UNAVAILABLE"`

### Error Response Format
```json
{
  "error": "Error message",
  "error_code": "ERROR_CODE",
  "execution_id": "exec_abc123",
  "intent_type": "validate_registration_data",
  "details": {
    "parameter": "name",
    "reason": "Missing required parameter"
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
- `validation_result` - Required (validation result artifact)

### Required Events
- `validation_passed` - Required (when validation succeeds)
- `validation_failed` - Required (when validation fails)

### Lifecycle State
- **No lifecycle state** - This is a validation-only intent with no artifacts created

### Contract Validation
- ✅ Intent must return validation result (is_valid, errors)
- ✅ No side effects (no artifacts created, no state changes)
- ✅ Idempotent (same input = same output)
- ✅ All required parameters validated
- ✅ Error messages are clear and actionable

---

**Last Updated:** January 27, 2026  
**Owner:** Security Solution Team  
**Status:** ✅ **ENHANCED** - Ready for implementation
