# Intent Contract: route_to_liaison_agent

**Intent:** route_to_liaison_agent  
**Intent Type:** `route_to_liaison_agent`  
**Journey:** Journey Coexistence Guide Agent (`journey_coexistence_guide_agent`)  
**Realm:** Coexistence Solution  
**Status:** IN PROGRESS  
**Priority:** PRIORITY 1

---

## 1. Intent Overview

### Purpose
Route conversation from GuideAgent to appropriate Liaison Agent with context sharing. GuideAgent determines which Liaison Agent based on user intent and pillar context. Context is shared to enable seamless conversation continuity.

### Intent Flow
```
[GuideAgent determines user needs pillar-specific assistance]
    ↓
[route_to_liaison_agent intent executes]
    ↓
[Extract conversation context from GuideAgent]
    ↓
[Determine appropriate Liaison Agent (content, insights, journey, or solution)]
    ↓
[Share context to Liaison Agent via share_context_to_agent]
    ↓
[Update chat session active_agent to Liaison Agent]
    ↓
[Returns liaison_agent_activation_artifact]
```

### Expected Observable Artifacts
- `liaison_agent_activation_artifact` - Activation artifact with shared context
- `routing_decision` - GuideAgent's routing decision (which Liaison Agent)
- `shared_context` - Context shared to Liaison Agent (via `share_context_to_agent` intent)
- `chat_session` - Updated chat session with `active_agent` changed to Liaison Agent

---

## 2. Intent Parameters

### Required Parameters

| Parameter | Type | Description | Validation |
|-----------|------|-------------|------------|
| `target_pillar` | `string` | Target pillar for Liaison Agent | Required, one of: "content", "insights", "journey", "solution" |

### Optional Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `chat_session_id` | `string` | Chat session identifier | If not provided, uses active session for user |
| `routing_reason` | `string` | Reason for routing decision | Optional explanation |
| `context_to_share` | `object` | Specific context to share (if not provided, shares all context) | If not provided, shares all conversation context |

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
- **No artifacts registered** - Activation is ephemeral, context shared via `share_context_to_agent`
- Chat session artifact updated (active_agent changed to Liaison Agent)

### Artifact Index Registration
- **No artifacts indexed** - Activation-only intent
- Chat session updated in Supabase (chat_sessions table, active_agent field)

---

## 5. Idempotency

### Idempotency Key
```
idempotency_key = hash(chat_session_id + target_pillar + context_hash)
```

### Scope
- Per chat session, per target pillar, per context state
- Same session + same pillar + same context = same routing result (idempotent)

### Behavior
- If routing to same pillar with same context is called multiple times, returns same activation (idempotent)
- Context sharing is idempotent (handled by `share_context_to_agent` intent)

---

## 6. Implementation Details

### Handler Location
- **New Implementation:** `symphainy_platform/realms/coexistence/intent_services/route_to_liaison_agent_service.py` (to be created)

### Key Implementation Steps
1. **Extract Parameters:** Get `target_pillar`, `chat_session_id`, `routing_reason`, `context_to_share` from intent parameters
2. **Retrieve Chat Session:**
   - If `chat_session_id` provided: Get session by ID
   - If not provided: Get active session for user
   - Verify session exists and `active_agent: "guide"`
3. **Extract Conversation Context:**
   - Get `context` from chat session
   - If `context_to_share` provided: Use it
   - If not: Extract all conversation context (conversation_history, shared_intent, etc.)
4. **Share Context to Liaison Agent:**
   - Call `share_context_to_agent` intent with:
     - `source_agent: "guide"`
     - `target_agent: "liaison_{target_pillar}"`
     - `shared_context: context_to_share or all context`
5. **Update Chat Session:**
   - Update `active_agent` to `"liaison_{target_pillar}"`
   - Update session in Supabase (chat_sessions table)
6. **Return Liaison Agent Activation:**
   - Return `target_pillar`, `liaison_agent_id`, `shared_context`, `routing_reason`, `active_agent_updated`

### Dependencies
- **Public Works:**
  - `TenantAbstraction` - For tenant-scoped operations
- **State Surface:**
  - `get_artifact()` - Retrieve chat session artifact
  - `update_artifact()` - Update chat session artifact
- **Runtime:**
  - `ExecutionContext` - Tenant, user, session, execution context
- **Other Intents:**
  - `share_context_to_agent` - For context sharing

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
- **Missing target_pillar:** `ValueError("target_pillar is required")` -> Returns error response with `ERROR_CODE: "MISSING_PARAMETER"`
- **Invalid target_pillar:** Pillar not one of valid values -> Returns error response with `ERROR_CODE: "INVALID_PILLAR"`
- **Chat session not found:** Chat session does not exist -> Returns error response with `ERROR_CODE: "SESSION_NOT_FOUND"`

### Runtime Errors
- **Context sharing failed:** Cannot share context to Liaison Agent -> Returns error response with `ERROR_CODE: "CONTEXT_SHARING_FAILED"`
- **Session update failed:** Cannot update chat session -> Returns error response with `ERROR_CODE: "SESSION_UPDATE_FAILED"`
- **Liaison Agent unavailable:** Target Liaison Agent not available -> Returns error response with `ERROR_CODE: "LIAISON_AGENT_UNAVAILABLE"`

### Error Response Format
```json
{
  "error": "Error message",
  "error_code": "ERROR_CODE",
  "execution_id": "exec_abc123",
  "intent_type": "route_to_liaison_agent",
  "details": {
    "target_pillar": "content",
    "reason": "Context sharing failed"
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
- `liaison_agent_activation` - Required (Liaison Agent activation artifact)

### Required Events
- `liaison_agent_activated` - Required (emitted when Liaison Agent is activated)

### Lifecycle State
- **No lifecycle state** - This is an activation-only intent with no persistent artifacts
- **Chat session active_agent** - Updated to Liaison Agent identifier

### Contract Validation
- ✅ Intent must return Liaison Agent activation with shared context
- ✅ Context must be shared via `share_context_to_agent` intent
- ✅ Chat session must be updated with new active_agent
- ✅ Routing decision must be included
- ✅ Idempotent (same session + same pillar + same context = same activation)

---

**Last Updated:** January 27, 2026  
**Owner:** Coexistence Solution Team  
**Status:** ✅ **ENHANCED** - Ready for implementation
