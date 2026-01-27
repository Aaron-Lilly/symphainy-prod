# Intent Contract: create_session

**Intent:** create_session  
**Intent Type:** `create_session`  
**Journey:** Journey Security Authentication (`journey_security_authentication`)  
**Realm:** Security Solution  
**Status:** IN PROGRESS  
**Priority:** PRIORITY 1

---

## 1. Intent Overview

### Purpose
Create an authenticated session for a user. Generates a session token, registers session artifact in State Surface, stores session in Supabase, and sets session cookie. This enables the user to access the platform.

### Intent Flow
```
[User authenticated and authorized]
    ↓
[create_session intent executes]
    ↓
[Generate session token (JWT, time-limited)]
    ↓
[Generate session_id (UUID)]
    ↓
[Register session artifact in State Surface (lifecycle_state: ACTIVE)]
    ↓
[Store session in Supabase (sessions table)]
    ↓
[Set session cookie (HTTP-only, secure)]
    ↓
[Returns session artifact (session_id, token, expiration)]
```

### Expected Observable Artifacts
- `artifact_id` - Session artifact identifier (session_id)
- `artifact_type: "session"`
- `lifecycle_state: "ACTIVE"`
- `session_id` - Session identifier (UUID)
- `user_id` - User identifier
- `tenant_id` - Tenant identifier
- `session_token` - JWT session token
- `expires_at` - Token expiration timestamp
- Artifact registered in State Surface (ArtifactRegistry)
- Session record created in Supabase (sessions table)

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
    "session": {
      "result_type": "session",
      "semantic_payload": {
        "session_id": "session_abc123",
        "user_id": "user_xyz789",
        "tenant_id": "tenant_def456",
        "lifecycle_state": "ACTIVE",
        "session_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "expires_at": "2026-01-28T10:00:00Z",
        "created_at": "2026-01-27T10:00:00Z"
      },
      "renderings": {
        "message": "Session created successfully"
      }
    }
  },
  "events": [
    {
      "type": "session_created",
      "session_id": "session_abc123",
      "user_id": "user_xyz789",
      "expires_at": "2026-01-28T10:00:00Z"
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
  "intent_type": "create_session",
  "details": {
    "user_id": "user_xyz789",
    "reason": "Session creation failed"
  }
}
```

---

## 4. Artifact Registration

### State Surface Registration
- **Artifact ID:** [How artifact_id is generated]
- **Artifact Type:** `"artifact_type"`
- **Lifecycle State:** `"PENDING"` or `"READY"`
- **Produced By:** `{ intent: "create_session", execution_id: "<execution_id>" }`
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
idempotency_key = hash(user_id + tenant_id + timestamp_window)
```

### Scope
- Per user, per tenant, per time window (e.g., per minute)
- Same user + tenant + time window = same session artifact (prevents duplicate sessions)

### Behavior
- If a session was created recently (within time window, e.g., 1 minute), returns existing session (idempotent)
- Prevents duplicate session creation for rapid login attempts
- Different time windows create different sessions (allows multiple sessions if needed)

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
// [Frontend code example]
```

### Expected Frontend Behavior
1. [Behavior 1]
2. [Behavior 2]

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
  "intent_type": "create_session"
}
```

---

## 9. Testing & Validation

### Happy Path
1. User authenticated and authorized (`user_id: "user_xyz789"`, `lifecycle_state: "ACTIVE"`)
2. `create_session` intent executes with `user_id`
3. Session ID generated (`session_id: "session_abc123"`)
4. Session token generated (JWT, expires in 24 hours)
5. Session artifact registered in State Surface (`lifecycle_state: "ACTIVE"`)
6. Session stored in Supabase (`sessions` table)
7. Session cookie set (HTTP-only, secure)
8. Returns `session_id`, `session_token`, `expires_at`
9. User redirected to platform

### Boundary Violations
- **User not found:** User does not exist -> Returns `ERROR_CODE: "USER_NOT_FOUND"`
- **Session expiration too short/long:** Session expiration outside valid range -> Uses default (24 hours) or returns error

### Failure Scenarios
- **Token generation failure:** Cannot generate JWT token -> Returns `ERROR_CODE: "TOKEN_GENERATION_FAILED"`, frontend shows error
- **Database unavailable:** Cannot store session -> Returns `ERROR_CODE: "DATABASE_UNAVAILABLE"`, frontend shows error and allows retry
- **Cookie setting failure:** Cannot set cookie -> Returns `ERROR_CODE: "COOKIE_SET_FAILED"`, session created but cookie not set, frontend may need to handle manually

---

## 10. Contract Compliance

### Required Artifacts
- `session` - Required (session artifact)

### Required Events
- `session_created` - Required (emitted when session is created)

### Lifecycle State
- **Initial State:** `"ACTIVE"` (session created with ACTIVE state)
- **Final State:** `"TERMINATED"` (after logout via terminate_session)
- **Transition:** `"ACTIVE"` → `"TERMINATED"` (via `terminate_session` intent)

### Contract Validation
- ✅ Artifact must have `session_id`, `user_id`, `tenant_id` in semantic_payload
- ✅ Session token must be JWT format
- ✅ Session must be stored in Supabase `sessions` table
- ✅ Artifact must be registered in State Surface
- ✅ Session cookie must be set (HTTP-only, secure)
- ✅ Idempotent (same user + tenant + time window = same session)

---

**Last Updated:** January 27, 2026  
**Owner:** Security Solution Team  
**Status:** ✅ **ENHANCED** - Ready for implementation
