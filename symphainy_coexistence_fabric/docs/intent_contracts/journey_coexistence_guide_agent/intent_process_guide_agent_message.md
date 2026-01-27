# Intent Contract: process_guide_agent_message

**Intent:** process_guide_agent_message  
**Intent Type:** `process_guide_agent_message`  
**Journey:** Journey Coexistence Guide Agent (`journey_coexistence_guide_agent`)  
**Realm:** Coexistence Solution  
**Status:** IN PROGRESS  
**Priority:** PRIORITY 1

---

## 1. Intent Overview

### Purpose
Process user message to GuideAgent, generate response using platform-wide knowledge, and optionally call orchestrator MCP tools. Updates conversation context with message and response.

### Intent Flow
```
[User sends message to GuideAgent]
    ↓
[process_guide_agent_message intent executes]
    ↓
[Load GuideAgent conversation state (from initiate_guide_agent)]
    ↓
[Process user message with platform-wide knowledge]
    ↓
[Optionally: Determine if MCP tool call needed]
    ↓
[Optionally: Call orchestrator MCP tool via call_orchestrator_mcp_tool (governed)]
    ↓
[Generate response (with MCP tool results if called)]
    ↓
[Update conversation context with message and response]
    ↓
[Returns guide_agent_response_artifact]
```

### Expected Observable Artifacts
- `guide_agent_response_artifact` - Response artifact with message and optional MCP tool results
- `mcp_tool_call_artifact` - MCP tool call artifact (if tool was called)
- `conversation_context` - Updated conversation context (message + response added)

---

## 2. Intent Parameters

### Required Parameters

| Parameter | Type | Description | Validation |
|-----------|------|-------------|------------|
| `message` | `string` | User message to GuideAgent | Required, non-empty |

### Optional Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `chat_session_id` | `string` | Chat session identifier | If not provided, uses active session for user |
| `conversation_context` | `object` | Existing conversation context | If not provided, loads from chat session |
| `mcp_tool_to_call` | `string` | Specific MCP tool to call (if known) | If not provided, GuideAgent determines tool |
| `mcp_tool_params` | `object` | Parameters for MCP tool call | `{}` |

### Context Metadata (from ExecutionContext)

| Metadata Key | Type | Description | Source |
|--------------|------|-------------|--------|
| `user_id` | `string` | User identifier | Runtime (required) |
| `tenant_id` | `string` | Tenant identifier | Runtime (required) |
| `chat_session` | `object` | Chat session artifact | Previous intent result (optional) |
| `guide_agent_conversation` | `object` | GuideAgent conversation state | Previous intent result (from initiate_guide_agent) |

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
- **No artifacts registered** - Response is ephemeral, stored in chat session context
- Conversation context updated in chat session (via `update_chat_context`)

### Artifact Index Registration
- **No artifacts indexed** - Response-only intent
- Conversation history stored in chat session context (chat_sessions table)

---

## 5. Idempotency

### Idempotency Key
```
N/A - Stateless processing, no side effects
```

### Scope
- N/A - Stateless processing, no side effects

### Behavior
- This intent processes messages statelessly (no persistent artifacts created)
- Context updates happen via `update_chat_context` (separate intent)
- MCP tool calls are idempotent (handled by `call_orchestrator_mcp_tool` intent)

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
// When user sends message to GuideAgent
const executionId = await platformState.submitIntent(
  'process_guide_agent_message',
  {
    message: userMessage,
    chat_session_id: sessionId
  }
);

const status = await platformState.getExecutionStatus(executionId);
if (status?.artifacts?.guide_agent_response) {
  const response = status.artifacts.guide_agent_response.semantic_payload;
  // Display response message
  // If mcp_tool_called: Show tool execution results
  // Update conversation history in UI
}
```

### Expected Frontend Behavior
1. **User sends message** - Frontend calls this intent with user message
2. **Response received** - Frontend displays GuideAgent response
3. **MCP tool results** - If MCP tool was called, frontend shows execution results
4. **Context updated** - Conversation context automatically updated
5. **History preserved** - Conversation history available for next message

---

## 8. Error Handling

### Validation Errors
- **Missing message:** `ValueError("message is required")` -> Returns error response with `ERROR_CODE: "MISSING_PARAMETER"`
- **Empty message:** Message is empty string -> Returns error response with `ERROR_CODE: "EMPTY_MESSAGE"`

### Runtime Errors
- **Chat session not found:** Chat session does not exist -> Returns error response with `ERROR_CODE: "SESSION_NOT_FOUND"`
- **GuideAgent unavailable:** GuideAgent LLM service unavailable -> Returns error response with `ERROR_CODE: "GUIDE_AGENT_UNAVAILABLE"`
- **MCP tool call failed:** MCP tool execution failed -> Returns error response with `ERROR_CODE: "MCP_TOOL_CALL_FAILED"` (response may still be generated without tool results)
- **Context update failed:** Cannot update conversation context -> Returns error response with `ERROR_CODE: "CONTEXT_UPDATE_FAILED"` (response still returned)

### Error Response Format
```json
{
  "error": "Error message",
  "error_code": "ERROR_CODE",
  "execution_id": "exec_abc123",
  "intent_type": "process_guide_agent_message",
  "details": {
    "reason": "GuideAgent unavailable"
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
- `guide_agent_response` - Required (GuideAgent response artifact)

### Required Events
- `guide_agent_message_processed` - Required (emitted when message is processed)

### Lifecycle State
- **No lifecycle state** - This is a stateless processing intent with no persistent artifacts
- **Conversation context** - Updated in chat session (via `update_chat_context`)

### Contract Validation
- ✅ Intent must return GuideAgent response with message
- ✅ MCP tool results must be included if tool was called
- ✅ Conversation context must be updated (via `update_chat_context`)
- ✅ No side effects (no artifacts created, context updated separately)
- ✅ Stateless processing (can be called multiple times with same message)

---

**Last Updated:** January 27, 2026  
**Owner:** Coexistence Solution Team  
**Status:** ✅ **ENHANCED** - Ready for implementation
