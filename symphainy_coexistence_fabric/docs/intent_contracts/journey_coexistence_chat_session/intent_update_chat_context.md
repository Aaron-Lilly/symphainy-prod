# Intent Contract: update_chat_context

**Intent:** update_chat_context  
**Intent Type:** `update_chat_context`  
**Journey:** Chat Session Management (`journey_coexistence_chat_session`)  
**Realm:** Coexistence Solution  
**Status:** ⏳ **IN PROGRESS**  
**Priority:** 🔴 **PRIORITY 1** - Foundation intent for Coexistence Solution

---

## 1. Intent Overview

### Purpose
Update shared conversation context

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
- **Produced By:** `{ intent: "update_chat_context", execution_id: "<execution_id>" }`
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
idempotency_key = hash(chat_session_id + context_hash)
```

### Scope
- Per chat session, per context state
- Same session + same context = same update result (idempotent)

### Behavior
- If context update with same data is called multiple times, returns same updated session (idempotent)
- Context merging is deterministic (same inputs = same merged output)
- Prevents duplicate context updates

---

## 6. Implementation Details

### Handler Location
- **New Implementation:** `symphainy_platform/realms/coexistence/intent_services/update_chat_context_service.py` (to be created)

### Key Implementation Steps
1. **Extract Parameters:** Get `context_updates`, `chat_session_id`, `merge_strategy` from intent parameters
2. **Retrieve Existing Session:**
   - If `chat_session_id` provided: Query session by ID
   - If not provided: Query active session by `user_id` and `tenant_id`
   - Verify session exists and `lifecycle_state: "ACTIVE"`
3. **Merge Context:**
   - Get existing `context` from session
   - If `merge_strategy: "merge"`: Deep merge `context_updates` with existing context
   - If `merge_strategy: "replace"`: Replace existing context with `context_updates`
   - Context structure:
     - `conversation_history: array` - Array of messages
     - `shared_intent: string` - Shared intent across agents
     - `pillar_context: object` - Pillar-specific context
     - `agent_metadata: object` - Agent-specific metadata
4. **Update Session Artifact in State Surface:**
   - Update chat session artifact with merged context
   - Update `updated_at` timestamp
5. **Update Session in Supabase:**
   - Update `chat_sessions` table with merged context
   - Update `updated_at` timestamp
6. **Return Updated Session Artifact:**
   - Return `chat_session_id`, `active_agent`, merged `context`, `updated_at`

### Dependencies
- **Public Works:**
  - `TenantAbstraction` - For tenant-scoped operations
- **State Surface:**
  - `get_artifact()` - Retrieve chat session artifact
  - `update_artifact()` - Update chat session artifact
- **Runtime:**
  - `ExecutionContext` - Tenant, user, session, execution context

---

## 7. Frontend Integration

### Frontend Usage
```typescript
// After user sends message or agent responds
const executionId = await platformState.submitIntent(
  'update_chat_context',
  {
    context_updates: {
      conversation_history: [
        ...existingHistory,
        {
          role: 'user',
          content: userMessage,
          timestamp: new Date().toISOString()
        },
        {
          role: 'agent',
          content: agentResponse,
          timestamp: new Date().toISOString()
        }
      ],
      shared_intent: detectedIntent
    }
  }
);
```

### Expected Frontend Behavior
1. **After message exchange** - Frontend calls this intent to update context
2. **Context merged** - New context merged with existing context
3. **Context available** - Updated context available for agent toggle
4. **Session persisted** - Context persists across page refreshes

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
  "intent_type": "update_chat_context"
}
```

---

## 9. Testing & Validation

### Happy Path
1. User has active chat session (`chat_session_id: "chat_session_abc123"`)
2. User sends message to GuideAgent
3. `update_chat_context` intent executes with `context_updates: {conversation_history: [...]}`
4. Existing context retrieved from session
5. New context merged with existing context
6. Session artifact updated in State Surface
7. Session updated in Supabase
8. Returns updated session with merged context
9. Context available for agent toggle

### Boundary Violations
- **Session not found:** Chat session does not exist -> Returns `ERROR_CODE: "SESSION_NOT_FOUND"`
- **Invalid context_updates:** Context updates not an object -> Returns `ERROR_CODE: "INVALID_PARAMETER_TYPE"`
- **Context too large:** Context exceeds size limit -> Returns `ERROR_CODE: "CONTEXT_TOO_LARGE"` or truncates

### Failure Scenarios
- **Database unavailable:** Cannot update session -> Returns `ERROR_CODE: "DATABASE_UNAVAILABLE"`, frontend shows error
- **Context merge failure:** Merge fails (circular reference, etc.) -> Returns `ERROR_CODE: "CONTEXT_MERGE_FAILED"`, frontend shows error
- **Partial update:** Context updated in database but artifact not updated -> Context in database but artifact stale (requires cleanup)

---

## 10. Contract Compliance

### Required Artifacts
- `chat_session` - Required (updated chat session artifact)

### Required Events
- `chat_context_updated` - Required (emitted when context is updated)

### Lifecycle State
- **Lifecycle state unchanged** - Session remains `"ACTIVE"` (only context is updated)

### Contract Validation
- ✅ Artifact must have updated `context` in semantic_payload
- ✅ Context must be merged correctly (no data loss)
- ✅ Session must be updated in Supabase `chat_sessions` table
- ✅ Artifact must be updated in State Surface
- ✅ Idempotent (same session + same context = same update)

---

**Last Updated:** January 27, 2026  
**Owner:** Coexistence Solution Team  
**Status:** ✅ **ENHANCED** - Ready for implementation
