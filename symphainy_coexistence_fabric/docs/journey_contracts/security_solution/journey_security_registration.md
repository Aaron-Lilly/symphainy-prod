# Journey Contract: User Registration

**Journey:** User Registration  
**Journey ID:** `journey_security_registration`  
**Solution:** Security Solution  
**Status:** ⏳ **IN PROGRESS**  
**Priority:** 🔴 **PRIORITY 1** - Foundation journey for Security Solution

---

## 1. Journey Overview

### Intents in Journey
1. `validate_registration_data` - Step 1: Validate registration form data (name, email, password)
2. `check_email_availability` - Step 2: Check if email is available (not already registered)
3. `create_user_account` - Step 3: Create new user account
4. `send_verification_email` - Step 4: Send email verification (if required)
5. `verify_email` - Step 5: Verify user email address (optional, if email verification enabled)

**Note:** Email verification is optional and configurable. If disabled, journey completes after account creation.

### Journey Flow
```
[User clicks "Create Account" on login page]
    ↓
[User enters registration data (name, email, password, confirm password)]
    ↓
[validate_registration_data] → Validation result
    - Validates name format
    - Validates email format
    - Validates password complexity
    - Validates password match
    ↓
[check_email_availability] → Email availability result
    - Checks if email already exists
    - Returns available/unavailable status
    ↓
[create_user_account] → user_account_artifact (artifact_id, artifact_type: "user_account", lifecycle_state: "PENDING")
    - Registered in State Surface (ArtifactRegistry)
    - Indexed in Supabase (users table)
    - Password hashed (never stored in plain text)
    - Account created with lifecycle_state: "PENDING" (if email verification required) or "ACTIVE" (if not required)
    ↓
[If email verification required]
    ↓
[send_verification_email] → Verification email sent
    - Verification token generated
    - Email sent to user
    - Token stored in intent context
    ↓
[User clicks verification link in email]
    ↓
[verify_email] → user_account_artifact lifecycle transition (lifecycle_state: "PENDING" → "ACTIVE")
    - Verification token validated
    - Account activated
    - Artifact Registry updated (State Surface)
    - Users table updated (Supabase)
    ↓
[Journey Complete]
```

### Expected Observable Artifacts
- **Step 1 (validate_registration_data):** 
  - Validation result (valid/invalid, error messages)
  - No artifacts created (validation only)
- **Step 2 (check_email_availability):** 
  - Email availability result (available/unavailable)
  - No artifacts created (check only)
- **Step 3 (create_user_account):** 
  - `artifact_id` (artifact_type: "user_account")
  - `user_id`, `email`, `name`
  - `lifecycle_state: "PENDING"` (if email verification required) or `"ACTIVE"` (if not required)
  - Password hash (never plain text)
  - Artifact registered in State Surface (ArtifactRegistry)
  - User record created in Supabase (users table)
- **Step 4 (send_verification_email):** 
  - Verification token generated
  - Email sent
  - Token stored in intent context
- **Step 5 (verify_email):** 
  - `artifact_id` (user_account artifact)
  - `lifecycle_state: "ACTIVE"` (transitioned from PENDING)
  - Artifact Registry updated (State Surface)
  - Users table updated (Supabase)

### Artifact Lifecycle State Transitions
- **Step 3:** User account artifact created with `lifecycle_state: "PENDING"` (if email verification required) or `"ACTIVE"` (if not required)
- **Step 5:** User account artifact transitions `lifecycle_state: "PENDING"` → `"ACTIVE"` (if email verification was required)

### Idempotency Scope (Per Intent)

| Intent                      | Idempotency Key                                    | Scope                    |
| --------------------------- | -------------------------------------------------- | ------------------------ |
| `validate_registration_data` | N/A (no side effects, validation only)             | N/A                      |
| `check_email_availability`  | N/A (no side effects, check only)                  | N/A                      |
| `create_user_account`       | `account_fingerprint` (hash(email + tenant_id))    | per tenant, per email    |
| `send_verification_email`   | `verification_fingerprint` (hash(user_id + token)) | per user, per token      |
| `verify_email`              | `verification_fingerprint` (hash(user_id + token)) | per user, per token      |

**Note:** Idempotency keys prevent duplicate account creation. Same email + tenant = same user account artifact.

### Journey Completion Definition

**Journey is considered complete when:**

* User account is created and activated (`create_user_account` succeeds, and `verify_email` succeeds if email verification required) **OR**
* User account is created and email verification is not required (`create_user_account` succeeds with `lifecycle_state: "ACTIVE"`)

**Journey completion = user can authenticate.**

---

## 2. Scenario 1: Happy Path (Email Verification Disabled)

### Test Description
Complete registration journey works end-to-end without email verification. User creates account and can immediately authenticate.

### Steps
1. [ ] User clicks "Create Account" on login page
2. [ ] User enters registration data (name, email, password, confirm password)
3. [ ] `validate_registration_data` intent executes → Validation passes
4. [ ] `check_email_availability` intent executes → Email available
5. [ ] `create_user_account` intent executes → User account created (`artifact_id`, `artifact_type: "user_account"`, `lifecycle_state: "ACTIVE"`)
6. [ ] User redirected to login page
7. [ ] Journey completes successfully
8. [ ] User can authenticate with new credentials

### Verification
- [ ] Observable artifacts at each step (artifact_id, artifact_type, lifecycle_state)
- [ ] Artifacts registered in State Surface (ArtifactRegistry)
- [ ] User record created in Supabase (users table)
- [ ] Password hashed (never stored in plain text)
- [ ] Account lifecycle state is "ACTIVE" (email verification disabled)
- [ ] User can authenticate immediately after registration

---

## 3. Scenario 2: Happy Path (Email Verification Enabled)

### Test Description
Complete registration journey works end-to-end with email verification. User creates account, verifies email, then can authenticate.

### Steps
1. [ ] User clicks "Create Account" on login page
2. [ ] User enters registration data (name, email, password, confirm password)
3. [ ] `validate_registration_data` intent executes → Validation passes
4. [ ] `check_email_availability` intent executes → Email available
5. [ ] `create_user_account` intent executes → User account created (`artifact_id`, `lifecycle_state: "PENDING"`)
6. [ ] `send_verification_email` intent executes → Verification email sent
7. [ ] User clicks verification link in email
8. [ ] `verify_email` intent executes → User account lifecycle transition (`lifecycle_state: "PENDING"` → `"ACTIVE"`)
9. [ ] User redirected to login page
10. [ ] Journey completes successfully
11. [ ] User can authenticate with new credentials

### Verification
- [ ] Observable artifacts at each step
- [ ] Account created with `lifecycle_state: "PENDING"` (email verification required)
- [ ] Verification email sent successfully
- [ ] Verification token validated correctly
- [ ] Account transitions to `lifecycle_state: "ACTIVE"` after verification
- [ ] User can authenticate after email verification

---

## 4. Scenario 3: Injected Failure

### Test Description
Journey handles failure gracefully when failure is injected at one step. User can see appropriate error and retry.

### Failure Injection Points (Test Each)
- **Option A:** Failure at `validate_registration_data` (invalid data format)
- **Option B:** Failure at `check_email_availability` (email already exists)
- **Option C:** Failure at `create_user_account` (database error, network failure)
- **Option D:** Failure at `send_verification_email` (email service unavailable)
- **Option E:** Failure at `verify_email` (invalid token, expired token)

### Steps (Example: Failure at check_email_availability)
1. [ ] User clicks "Create Account" ✅
2. [ ] User enters registration data ✅
3. [ ] `validate_registration_data` intent executes → Validation passes ✅
4. [ ] `check_email_availability` intent executes → ❌ **FAILURE INJECTED** (email already exists)
5. [ ] Journey handles failure gracefully
6. [ ] User sees appropriate error message ("Email already registered. Please use a different email or log in.")
7. [ ] State remains consistent (no account created, no corruption)
8. [ ] User can retry with different email or switch to login

### Verification
- [ ] Failure handled gracefully (no crash, no unhandled exception)
- [ ] User sees appropriate error message (clear, actionable)
- [ ] State remains consistent (no partial account creation, no corruption)
- [ ] User can retry with different email
- [ ] User can switch to login if email already exists

---

## 5. Scenario 4: Boundary Violation

### Test Description
Journey rejects invalid inputs and maintains state consistency. User sees clear validation error messages.

### Boundary Violation Points (Test Each)
- **Option A:** Invalid email format (missing @, invalid domain)
- **Option B:** Weak password (doesn't meet complexity requirements)
- **Option C:** Password mismatch (password and confirm password don't match)
- **Option D:** Missing required fields (name, email, password)
- **Option E:** Invalid name format (too short, special characters)

### Steps (Example: Invalid email format)
1. [ ] User clicks "Create Account"
2. [ ] User enters invalid email (e.g., "invalid-email")
3. [ ] `validate_registration_data` intent executes → ❌ **BOUNDARY VIOLATION** (invalid email format)
4. [ ] Journey rejects invalid input
5. [ ] User sees validation error message ("Please enter a valid email address")
6. [ ] State remains consistent (no account creation attempted)
7. [ ] User can correct email and retry

### Verification
- [ ] Invalid inputs rejected (validation fails)
- [ ] User sees clear validation error messages
- [ ] State remains consistent (no partial account creation)
- [ ] User can correct input and retry

---

## 6. Integration Points

### Platform Services
- **Security Realm:** Intent services (`validate_registration_data`, `check_email_availability`, `create_user_account`, `send_verification_email`, `verify_email`)
- **Journey Realm:** Orchestration services (compose registration journey)
- **State Surface:** Artifact registry and lifecycle management

### Civic Systems
- **Smart City Primitives:** Security Guard (authentication policies), Data Steward (password storage policies)
- **Agent Framework:** GuideAgent, Security Liaison Agent

### External Systems
- **Email Service:** (Future) For sending verification emails
- **Database:** Supabase (users table)

---

## 7. Testing & Validation

### Business Acceptance Criteria
- [ ] Users can create accounts successfully
- [ ] Email validation works correctly
- [ ] Password complexity requirements enforced
- [ ] Email verification works (if enabled)
- [ ] Duplicate email registration prevented
- [ ] Account lifecycle managed correctly (PENDING → ACTIVE)

### Contract-Based Testing
- [ ] All intent contracts validated
- [ ] Journey contract validated
- [ ] Contract violations detected and prevented

---

**Last Updated:** January 27, 2026  
**Owner:** Security Solution Team
