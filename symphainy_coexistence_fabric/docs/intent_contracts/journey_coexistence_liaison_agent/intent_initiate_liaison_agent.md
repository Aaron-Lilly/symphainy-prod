# Intent Contract: initiate_liaison_agent

**Intent:** initiate_liaison_agent  
**Intent Type:** `initiate_liaison_agent`  
**Journey:** Liaison Agent Conversation (`journey_coexistence_liaison_agent`)  
**Realm:** Coexistence Solution  
**Status:** ⏳ **IN PROGRESS**  
**Priority:** 🔴 **PRIORITY 1** - Foundation intent for Coexistence Solution

---

## 1. Intent Overview

### Purpose
Initialize Liaison Agent conversation with pillar-specific context

### Intent Flow
```
[User sends message to Liaison Agent or toggles to Liaison Agent]
    ↓
[initiate_liaison_agent intent executes]
    ↓
[Retrieve chat session and context]
    ↓
[Load conversation history from context]
    ↓
[Retrieve shared context from GuideAgent (if toggled)]
    ↓
[Query Curator for pillar-specific MCP tools only]
    ↓
[Initialize Liaison Agent with pillar-specific knowledge]
    ↓
[Returns liaison_agent_conversation_artifact with context and pillar MCP tools]
```

### Expected Observable Artifacts
- `liaison_agent_conversation_artifact` - Conversation artifact with pillar-specific context
- `available_pillar_mcp_tools` - List of pillar-specific MCP tools (from pillar orchestrator only)
- `shared_context` - Context shared from GuideAgent (if toggled)
- `conversation_history` - Loaded conversation history from chat session
- `pillar_context` - Pillar-specific context (artifacts, state, capabilities)

---

## 2. Intent Parameters

### Required Parameters

| Parameter | Type | Description | Validation |
|-----------|------|-------------|------------|
| `pillar_type` | `string` | Pillar identifier | Required, one of: "content", "insights", "journey", "solution"

### Optional Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `parameter_name` | `type` | Description | Default value |

### Context Metadata (from ExecutionContext)

| Metadata Key | Type | Description | Source |
|--------------|------|-------------|--------|
| `user_id` | `string` | User identifier | Runtime (required) |
| `tenant_id` | `string` | Tenant identifier | Runtime (required) |
| `chat_session` | `object` | Chat session artifact | Previous intent result (optional) |
| `shared_context` | `object` | Shared context from GuideAgent | Previous intent result (from share_context_to_agent) |

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
- **Produced By:** `{ intent: "initiate_liaison_agent", execution_id: "<execution_id>" }`
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
N/A - No side effects, initialization only
```

### Scope
- N/A - No side effects, initialization only

### Behavior
- This intent has no side effects (no state changes, no artifacts created)
- Can be called multiple times - always returns same initialization data (idempotent)
- Idempotent by nature (pure initialization function)

---

## 6. Implementation Details

### Handler Location
- **New Implementation:** `symphainy_platform/realms/coexistence/intent_services/initiate_liaison_agent_service.py` (to be created)

### Key Implementation Steps
1. **Extract Parameters:** Get `pillar_type`, `chat_session_id` from intent parameters
2. **Validate Pillar Type:** Verify `pillar_type` is one of: "content", "insights", "journey", "solution"
3. **Retrieve Chat Session:**
   - If `chat_session_id` provided: Get session by ID
   - If not provided: Get active session for user
   - Extract `context` and `conversation_history` from session
4. **Load Shared Context:**
   - Check if context has `shared_context` from GuideAgent (if toggled)
   - Extract shared context data
5. **Query Curator for Pillar MCP Tools:**
   - Use CuratorSDK to query Tool Registry for pillar-specific MCP tools
   - Filter: Only tools from pillar orchestrator (e.g., "content" pillar = only Content orchestrator tools)
   - Get tool metadata: name, description, parameters, governance rules
6. **Get Pillar Context (Optional):**
   - Query pillar realm for artifacts, state, capabilities
   - Build pillar-specific context
7. **Initialize Liaison Agent:**
   - Load conversation history from context
   - Set pillar-specific knowledge base
   - Provide access to pillar MCP tools only
   - Load shared context (if available)
8. **Return Liaison Agent Conversation Artifact:**
   - Return `agent_type: "liaison"`, `pillar_type`, `conversation_history`, `shared_context`, `available_pillar_mcp_tools`, `pillar_context`

### Dependencies
- **Public Works:**
  - `CuratorSDK` - For querying MCP tool registry (pillar-filtered)
  - `TenantAbstraction` - For tenant-scoped operations
- **State Surface:**
  - `get_artifact()` - Retrieve chat session artifact
- **Runtime:**
  - `ExecutionContext` - Tenant, user, session, execution context
- **Curator:**
  - Tool Registry - For MCP tool discovery (pillar-filtered)

---

## 7. Frontend Integration

### Frontend Usage
```typescript
// When user toggles to Liaison Agent or sends first message
const executionId = await platformState.submitIntent(
  'initiate_liaison_agent',
  {
    pillar_type: 'content'
  }
);

const status = await platformState.getExecutionStatus(executionId);
if (status?.artifacts?.liaison_agent_conversation) {
  const conversation = status.artifacts.liaison_agent_conversation.semantic_payload;
  const mcpTools = conversation.available_pillar_mcp_tools;
  const context = conversation.shared_context;
  // Liaison Agent ready with pillar MCP tools and context
}
```

### Expected Frontend Behavior
1. **Agent toggle** - Frontend calls this intent when user toggles to Liaison Agent
2. **Pillar MCP tools loaded** - Frontend receives list of pillar-specific MCP tools
3. **Context loaded** - Frontend receives shared context from GuideAgent (if toggled)
4. **Conversation history** - Frontend loads conversation history from context
5. **Agent ready** - Liaison Agent ready to process messages and call pillar MCP tools

---

## 8. Error Handling

### Validation Errors
- **Missing pillar_type:** `ValueError("pillar_type is required")` -> Returns error response with `ERROR_CODE: "MISSING_PARAMETER"`
- **Invalid pillar_type:** Pillar not one of valid values -> Returns error response with `ERROR_CODE: "INVALID_PILLAR"`
- **Chat session not found:** Chat session does not exist -> Returns error response with `ERROR_CODE: "SESSION_NOT_FOUND"`

### Runtime Errors
- **Curator unavailable:** Cannot query Curator for MCP tools -> Returns error response with `ERROR_CODE: "CURATOR_UNAVAILABLE"` (Liaison Agent can still initialize without tools)
- **Tool registry unavailable:** Cannot query tool registry -> Returns error response with `ERROR_CODE: "TOOL_REGISTRY_UNAVAILABLE"` (Liaison Agent can still initialize without tools)
- **Context load failure:** Cannot load conversation history -> Returns error response with `ERROR_CODE: "CONTEXT_LOAD_FAILED"` (Liaison Agent can still initialize with empty context)

### Error Response Format
```json
{
  "error": "Error message",
  "error_code": "ERROR_CODE",
  "execution_id": "exec_abc123",
  "intent_type": "initiate_liaison_agent",
  "details": {
    "pillar_type": "content",
    "reason": "Curator unavailable"
  }
}
```

---

## 9. Testing & Validation

### Happy Path
1. User has active chat session with context
2. User toggles to Content Liaison Agent
3. `initiate_liaison_agent` intent executes with `pillar_type: "content"`
4. Chat session retrieved, conversation history loaded
5. Shared context retrieved (if toggled from GuideAgent)
6. Curator queried for Content pillar MCP tools only
7. Pillar context built (artifacts, state, capabilities)
8. Returns Liaison Agent conversation artifact with pillar MCP tools and context
9. Liaison Agent ready to process messages

### Boundary Violations
- **Invalid pillar_type:** Pillar not valid -> Returns `ERROR_CODE: "INVALID_PILLAR"`
- **Session not found:** Chat session does not exist -> Returns `ERROR_CODE: "SESSION_NOT_FOUND"`
- **No MCP tools available:** Curator returns no pillar tools -> Liaison Agent initializes with empty MCP tools list (still functional)

### Failure Scenarios
- **Curator unavailable:** Cannot query Curator -> Returns `ERROR_CODE: "CURATOR_UNAVAILABLE"`, Liaison Agent initializes without MCP tools (graceful degradation)
- **Context load failure:** Cannot load context -> Returns `ERROR_CODE: "CONTEXT_LOAD_FAILED"`, Liaison Agent initializes with empty context

---

## 10. Contract Compliance

### Required Artifacts
- `liaison_agent_conversation` - Required (Liaison Agent conversation artifact)

### Required Events
- `liaison_agent_initialized` - Required (emitted when Liaison Agent is initialized)

### Lifecycle State
- **No lifecycle state** - This is an initialization-only intent with no persistent artifacts
- **Conversation state** - Stored in chat session context (ephemeral)

### Contract Validation
- ✅ Intent must return Liaison Agent conversation artifact with pillar MCP tools and context
- ✅ MCP tools must be queried from Curator (pillar-filtered, only pillar orchestrator tools)
- ✅ Shared context must be loaded (if available from GuideAgent)
- ✅ Conversation history must be loaded from chat session
- ✅ Pillar context must be built (artifacts, state, capabilities)
- ✅ No side effects (no artifacts created, no state changes)

---

**Last Updated:** January 27, 2026  
**Owner:** Coexistence Solution Team  
**Status:** ✅ **ENHANCED** - Ready for implementation
