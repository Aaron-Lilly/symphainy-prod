# Journey Contract: User Authentication

**Journey:** User Authentication  
**Journey ID:** `journey_security_authentication`  
**Solution:** Security Solution  
**Status:** ⏳ **IN PROGRESS**  
**Priority:** 🔴 **PRIORITY 1** - Foundation journey for Security Solution

---

## 1. Journey Overview

### Intents in Journey
1. `authenticate_user` - Step 1: Validate user credentials (email, password)
2. `validate_authorization` - Step 2: Check user permissions and roles
3. `create_session` - Step 3: Create authenticated session
4. `refresh_session` - Step 4: Refresh expired session (optional, ongoing)
5. `terminate_session` - Step 5: Logout user (optional, user-initiated)

**Note:** `refresh_session` and `terminate_session` are ongoing operations that can happen at any time after session creation.

### Journey Flow
```
[User navigates to platform]
    ↓
[User redirected to login page (if not authenticated)]
    ↓
[User enters credentials (email, password)]
    ↓
[authenticate_user] → Authentication result
    - Validates email format
    - Validates password
    - Checks user account exists
    - Verifies password hash
    - Returns user account artifact
    ↓
[validate_authorization] → Authorization result
    - Checks user account lifecycle_state (must be ACTIVE)
    - Retrieves user roles and permissions
    - Validates user access rights
    - Returns authorization status
    ↓
[create_session] → session_artifact (artifact_id, artifact_type: "session", lifecycle_state: "ACTIVE")
    - Session token generated
    - Session registered in State Surface (ArtifactRegistry)
    - Session stored in Supabase (sessions table)
    - Session cookie set (HTTP-only, secure)
    - User redirected to platform
    ↓
[Ongoing: refresh_session] → Session refreshed (if needed)
    - Session token refreshed
    - Session expiration extended
    - Session artifact updated
    ↓
[Ongoing: terminate_session] → Session terminated (user logout)
    - Session artifact lifecycle transition (lifecycle_state: "ACTIVE" → "TERMINATED")
    - Session invalidated
    - Session cookie cleared
    - User redirected to login
    ↓
[Journey Complete]
```

### Expected Observable Artifacts
- **Step 1 (authenticate_user):** 
  - Authentication result (success/failure, user account artifact)
  - No artifacts created (validation only)
- **Step 2 (validate_authorization):** 
  - Authorization result (authorized/unauthorized, roles, permissions)
  - No artifacts created (validation only)
- **Step 3 (create_session):** 
  - `artifact_id` (artifact_type: "session")
  - `session_id`, `user_id`, `tenant_id`
  - `lifecycle_state: "ACTIVE"`
  - Session token, expiration time
  - Artifact registered in State Surface (ArtifactRegistry)
  - Session record created in Supabase (sessions table)
- **Step 4 (refresh_session):** 
  - Session artifact updated (new token, extended expiration)
  - Artifact Registry updated (State Surface)
  - Sessions table updated (Supabase)
- **Step 5 (terminate_session):** 
  - `artifact_id` (session artifact)
  - `lifecycle_state: "TERMINATED"` (transitioned from ACTIVE)
  - Artifact Registry updated (State Surface)
  - Sessions table updated (Supabase)

### Artifact Lifecycle State Transitions
- **Step 3:** Session artifact created with `lifecycle_state: "ACTIVE"`
- **Step 4:** Session artifact updated (token refreshed, expiration extended)
- **Step 5:** Session artifact transitions `lifecycle_state: "ACTIVE"` → `"TERMINATED"`

### Idempotency Scope (Per Intent)

| Intent                  | Idempotency Key                                    | Scope                    |
| ----------------------- | -------------------------------------------------- | ------------------------ |
| `authenticate_user`      | N/A (no side effects, validation only)             | N/A                      |
| `validate_authorization` | N/A (no side effects, validation only)            | N/A                      |
| `create_session`         | `session_fingerprint` (hash(user_id + tenant_id + timestamp)) | per user, per tenant     |
| `refresh_session`        | `session_fingerprint` (hash(session_id + timestamp)) | per session              |
| `terminate_session`      | `session_fingerprint` (hash(session_id))           | per session               |

**Note:** Idempotency keys prevent duplicate session creation. Same user + tenant + timestamp = same session artifact.

### Journey Completion Definition

**Journey is considered complete when:**

* User is authenticated and session is created (`authenticate_user` succeeds, `validate_authorization` succeeds, `create_session` succeeds)

**Journey completion = user can access platform.**

---

## 2. Scenario 1: Happy Path

### Test Description
Complete authentication journey works end-to-end. User logs in and can access platform.

### Steps
1. [ ] User navigates to platform
2. [ ] User redirected to login page (not authenticated)
3. [ ] User enters credentials (email, password)
4. [ ] `authenticate_user` intent executes → Authentication succeeds (user account found, password verified)
5. [ ] `validate_authorization` intent executes → Authorization succeeds (user account ACTIVE, permissions valid)
6. [ ] `create_session` intent executes → Session created (`artifact_id`, `artifact_type: "session"`, `lifecycle_state: "ACTIVE"`)
7. [ ] User redirected to platform
8. [ ] Journey completes successfully
9. [ ] User can access platform features

### Verification
- [ ] Observable artifacts at each step (artifact_id, artifact_type, lifecycle_state)
- [ ] Artifacts registered in State Surface (ArtifactRegistry)
- [ ] Session record created in Supabase (sessions table)
- [ ] Session cookie set (HTTP-only, secure)
- [ ] User can access platform after authentication
- [ ] Session validated on subsequent requests

---

## 3. Scenario 2: Injected Failure

### Test Description
Journey handles failure gracefully when failure is injected at one step. User can see appropriate error and retry.

### Failure Injection Points (Test Each)
- **Option A:** Failure at `authenticate_user` (invalid credentials, user not found)
- **Option B:** Failure at `validate_authorization` (account not ACTIVE, insufficient permissions)
- **Option C:** Failure at `create_session` (database error, session creation failure)

### Steps (Example: Failure at authenticate_user)
1. [ ] User navigates to platform ✅
2. [ ] User redirected to login page ✅
3. [ ] User enters invalid credentials (wrong password)
4. [ ] `authenticate_user` intent executes → ❌ **FAILURE INJECTED** (invalid credentials)
5. [ ] Journey handles failure gracefully
6. [ ] User sees appropriate error message ("Invalid email or password. Please try again.")
7. [ ] State remains consistent (no session created, no corruption)
8. [ ] User can retry with correct credentials

### Verification
- [ ] Failure handled gracefully (no crash, no unhandled exception)
- [ ] User sees appropriate error message (clear, actionable, doesn't reveal if email exists)
- [ ] State remains consistent (no partial session creation, no corruption)
- [ ] User can retry authentication
- [ ] Failed login attempts logged for security

---

## 4. Scenario 3: Boundary Violation

### Test Description
Journey rejects invalid inputs and maintains state consistency. User sees clear validation error messages.

### Boundary Violation Points (Test Each)
- **Option A:** Invalid email format (missing @, invalid domain)
- **Option B:** Missing credentials (empty email or password)
- **Option C:** Account locked (too many failed attempts)
- **Option D:** Account not ACTIVE (PENDING, SUSPENDED)

### Steps (Example: Account not ACTIVE)
1. [ ] User navigates to platform
2. [ ] User enters credentials
3. [ ] `authenticate_user` intent executes → Authentication succeeds ✅
4. [ ] `validate_authorization` intent executes → ❌ **BOUNDARY VIOLATION** (account lifecycle_state: "PENDING", not ACTIVE)
5. [ ] Journey rejects invalid state
6. [ ] User sees appropriate error message ("Account not activated. Please verify your email.")
7. [ ] State remains consistent (no session created)
8. [ ] User can verify email and retry

### Verification
- [ ] Invalid states rejected (authorization fails)
- [ ] User sees clear error messages
- [ ] State remains consistent (no partial session creation)
- [ ] User can resolve issue and retry

---

## 5. Integration Points

### Platform Services
- **Security Realm:** Intent services (`authenticate_user`, `validate_authorization`, `create_session`, `refresh_session`, `terminate_session`)
- **Journey Realm:** Orchestration services (compose authentication journey)
- **State Surface:** Artifact registry and lifecycle management

### Civic Systems
- **Smart City Primitives:** Security Guard (authentication policies, session policies), Traffic Cop (session management)
- **Agent Framework:** GuideAgent, Security Liaison Agent

### External Systems
- **Database:** Supabase (users table, sessions table)

---

## 6. Testing & Validation

### Business Acceptance Criteria
- [ ] Users can authenticate successfully
- [ ] Invalid credentials rejected correctly
- [ ] Session created and managed correctly
- [ ] Session refresh works correctly
- [ ] Session termination works correctly
- [ ] Account lifecycle states validated correctly

### Contract-Based Testing
- [ ] All intent contracts validated
- [ ] Journey contract validated
- [ ] Contract violations detected and prevented

---

**Last Updated:** January 27, 2026  
**Owner:** Security Solution Team
