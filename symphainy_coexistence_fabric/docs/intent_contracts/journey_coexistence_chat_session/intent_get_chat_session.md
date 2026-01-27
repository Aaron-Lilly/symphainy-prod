# Intent Contract: get_chat_session

**Intent:** get_chat_session  
**Intent Type:** `get_chat_session`  
**Journey:** Chat Session Management (`journey_coexistence_chat_session`)  
**Realm:** Coexistence Solution  
**Status:** ⏳ **IN PROGRESS**  
**Priority:** 🔴 **PRIORITY 1** - Foundation intent for Coexistence Solution

---

## 1. Intent Overview

### Purpose
Retrieve active chat session (if exists)

### Intent Flow
```
[Describe the flow for this intent]
```

### Expected Observable Artifacts
- [List expected artifacts]

---

## 2. Intent Parameters

### Required Parameters

| Parameter | Type | Description | Validation |
|-----------|------|-------------|------------|
| None | - | - | - |

### Optional Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `chat_session_id` | `string` | Specific session ID to retrieve | If not provided, retrieves active session for user |

### Context Metadata (from ExecutionContext)

| Metadata Key | Type | Description | Source |
|--------------|------|-------------|--------|
| `user_id` | `string` | User identifier | Runtime (required) |
| `tenant_id` | `string` | Tenant identifier | Runtime (required) |
| `session_id` | `string` | User session identifier | Runtime (from Security Solution) |

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
- **Artifact ID:** [How artifact_id is generated]
- **Artifact Type:** `"artifact_type"`
- **Lifecycle State:** `"PENDING"` or `"READY"`
- **Produced By:** `{ intent: "get_chat_session", execution_id: "<execution_id>" }`
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
idempotency_key = hash([key components])
```

### Scope
- [Describe scope: per tenant, per session, per artifact, etc.]

### Behavior
- [Describe idempotent behavior]

---

## 6. Implementation Details

### Handler Location
- **New Implementation:** `symphainy_platform/realms/coexistence/intent_services/get_chat_session_service.py` (to be created)

### Key Implementation Steps
1. **Extract Context:** Get `user_id`, `tenant_id` from ExecutionContext
2. **Query Chat Session:**
   - If `chat_session_id` provided: Query `chat_sessions` table by `chat_session_id`
   - If not provided: Query `chat_sessions` table by `user_id` and `tenant_id` where `lifecycle_state: "ACTIVE"`
3. **Check Session Exists:**
   - If session found: Retrieve session artifact from State Surface
   - If not found: Return session not found response
4. **Return Chat Session Artifact:**
   - Return `chat_session_id`, `active_agent`, `context`, `created_at`, `updated_at`

### Dependencies
- **Public Works:**
  - `TenantAbstraction` - For tenant-scoped queries
- **State Surface:**
  - `get_artifact()` - Retrieve chat session artifact
- **Runtime:**
  - `ExecutionContext` - Tenant, user, session, execution context

---

## 7. Frontend Integration

### Frontend Usage
```typescript
// When chat interface opens or user toggles agent
const executionId = await platformState.submitIntent(
  'get_chat_session',
  {}
);

const status = await platformState.getExecutionStatus(executionId);
if (status?.artifacts?.chat_session?.semantic_payload?.exists) {
  const session = status.artifacts.chat_session.semantic_payload;
  const activeAgent = session.active_agent;
  const context = session.context;
  // Load chat interface with existing session
} else {
  // No session found, initialize new one
  await platformState.submitIntent('initialize_chat_session', {});
}
```

### Expected Frontend Behavior
1. **Chat interface opens** - Frontend calls this intent to check for existing session
2. **Session found** - Frontend loads chat with existing context and active agent
3. **Session not found** - Frontend initializes new session
4. **Agent toggle** - Frontend calls this intent to get current session before toggling

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
  "intent_type": "get_chat_session"
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
- `chat_session` - Required (if session exists) or session not found response

### Required Events
- `chat_session_retrieved` - Required (when session is found)
- `chat_session_not_found` - Required (when session is not found)

### Lifecycle State
- **No lifecycle state** - This is a retrieval-only intent with no artifacts created
- **Returned session lifecycle state** - Must be "ACTIVE" (only active sessions are returned)

### Contract Validation
- ✅ Intent must return chat session artifact if session exists
- ✅ Intent must return session not found response if session doesn't exist
- ✅ No side effects (no artifacts created, no state changes)
- ✅ Idempotent (same input = same output)
- ✅ Session must be active (lifecycle_state: "ACTIVE")

---

**Last Updated:** January 27, 2026  
**Owner:** Coexistence Solution Team  
**Status:** ✅ **ENHANCED** - Ready for implementation
