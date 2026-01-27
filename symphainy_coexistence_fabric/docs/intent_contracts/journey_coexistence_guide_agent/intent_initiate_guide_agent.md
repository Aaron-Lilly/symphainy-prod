# Intent Contract: initiate_guide_agent

**Intent:** initiate_guide_agent  
**Intent Type:** `initiate_guide_agent`  
**Journey:** Journey Coexistence Guide Agent (`journey_coexistence_guide_agent`)  
**Realm:** Coexistence Solution  
**Status:** IN PROGRESS  
**Priority:** PRIORITY 1

---

## 1. Intent Overview

### Purpose
Initialize GuideAgent conversation with platform-wide context and access to all orchestrator MCP tools. Loads conversation history, retrieves shared context from previous agent (if toggled), and queries Curator for available MCP tools from all orchestrators.

### Intent Flow
```
[User sends message to GuideAgent or toggles to GuideAgent]
    ↓
[initiate_guide_agent intent executes]
    ↓
[Retrieve chat session and context]
    ↓
[Load conversation history from context]
    ↓
[Retrieve shared context from previous agent (if toggled)]
    ↓
[Query Curator for all available MCP tools (all orchestrators)]
    ↓
[Initialize GuideAgent with platform-wide knowledge]
    ↓
[Returns guide_agent_conversation_artifact with context and MCP tools]
```

### Expected Observable Artifacts
- `guide_agent_conversation_artifact` - Conversation artifact with platform-wide context
- `available_mcp_tools` - List of all available MCP tools (from all orchestrators via Curator)
- `shared_context` - Context shared from previous agent (if toggled from Liaison Agent)
- `conversation_history` - Loaded conversation history from chat session
- `platform_context` - Platform-wide context (all pillars, all solutions)

---

## 2. Intent Parameters

### Required Parameters

| Parameter | Type | Description | Validation |
|-----------|------|-------------|------------|
| None | - | - | - |

### Optional Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `chat_session_id` | `string` | Chat session identifier | If not provided, uses active session for user |
| `include_mcp_tools` | `boolean` | Whether to query and include MCP tools | `true` |

### Context Metadata (from ExecutionContext)

| Metadata Key | Type | Description | Source |
|--------------|------|-------------|--------|
| `user_id` | `string` | User identifier | Runtime (required) |
| `tenant_id` | `string` | Tenant identifier | Runtime (required) |
| `session_id` | `string` | User session identifier | Runtime (from Security Solution) |
| `chat_session` | `object` | Chat session artifact (from get_chat_session) | Previous intent result (optional) |

---

## 3. Intent Returns

### Success Response

```json
{
  "artifacts": {
    "guide_agent_conversation": {
      "result_type": "guide_agent_conversation",
      "semantic_payload": {
        "agent_type": "guide",
        "chat_session_id": "chat_session_abc123",
        "conversation_history": [
          {
            "role": "user",
            "content": "What is SymphAIny?",
            "timestamp": "2026-01-27T10:05:00Z"
          }
        ],
        "shared_context": {
          "from_agent": "liaison_content",
          "context_data": {
            "pillar": "content",
            "intent": "file_parsing"
          }
        },
        "available_mcp_tools": [
          {
            "tool_name": "content_parse_file",
            "description": "Parse a file using Content orchestrator",
            "orchestrator": "content",
            "parameters": {
              "file_id": "string",
              "file_type": "string"
            }
          },
          {
            "tool_name": "insights_assess_quality",
            "description": "Assess data quality using Insights orchestrator",
            "orchestrator": "insights",
            "parameters": {
              "parsed_file_id": "string"
            }
          }
        ],
        "platform_context": {
          "pillars": ["content", "insights", "journey", "solution"],
          "solutions": ["content_realm", "insights_realm", "journey_realm", "solution_realm"],
          "capabilities": ["file_parsing", "data_quality", "workflow_creation", "solution_synthesis"]
        }
      },
      "renderings": {
        "message": "GuideAgent initialized. I can help you with platform-wide questions and execute actions via MCP tools."
      }
    }
  },
  "events": [
    {
      "type": "guide_agent_initialized",
      "chat_session_id": "chat_session_abc123",
      "mcp_tools_count": 25
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
  "intent_type": "initiate_guide_agent"
}
```

---

## 4. Artifact Registration

### State Surface Registration
- **Artifact ID:** [How artifact_id is generated]
- **Artifact Type:** `"artifact_type"`
- **Lifecycle State:** `"PENDING"` or `"READY"`
- **Produced By:** `{ intent: "initiate_guide_agent", execution_id: "<execution_id>" }`
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
// When user toggles to GuideAgent or sends first message
const executionId = await platformState.submitIntent(
  'initiate_guide_agent',
  {}
);

const status = await platformState.getExecutionStatus(executionId);
if (status?.artifacts?.guide_agent_conversation) {
  const conversation = status.artifacts.guide_agent_conversation.semantic_payload;
  const mcpTools = conversation.available_mcp_tools;
  const context = conversation.shared_context;
  // GuideAgent ready with MCP tools and context
}
```

### Expected Frontend Behavior
1. **Agent toggle** - Frontend calls this intent when user toggles to GuideAgent
2. **MCP tools loaded** - Frontend receives list of available MCP tools
3. **Context loaded** - Frontend receives shared context from previous agent (if toggled)
4. **Conversation history** - Frontend loads conversation history from context
5. **Agent ready** - GuideAgent ready to process messages and call MCP tools

---

## 8. Error Handling

### Validation Errors
- **User not authenticated:** User not logged in -> Returns error response with `ERROR_CODE: "UNAUTHENTICATED"`
- **Chat session not found:** Chat session does not exist -> Returns error response with `ERROR_CODE: "SESSION_NOT_FOUND"`

### Runtime Errors
- **Curator unavailable:** Cannot query Curator for MCP tools -> Returns error response with `ERROR_CODE: "CURATOR_UNAVAILABLE"` (GuideAgent can still initialize without tools)
- **Tool registry unavailable:** Cannot query tool registry -> Returns error response with `ERROR_CODE: "TOOL_REGISTRY_UNAVAILABLE"` (GuideAgent can still initialize without tools)
- **Context load failure:** Cannot load conversation history -> Returns error response with `ERROR_CODE: "CONTEXT_LOAD_FAILED"` (GuideAgent can still initialize with empty context)

### Error Response Format
```json
{
  "error": "Error message",
  "error_code": "ERROR_CODE",
  "execution_id": "exec_abc123",
  "intent_type": "initiate_guide_agent",
  "details": {
    "reason": "Curator unavailable"
  }
}
```

---

## 9. Testing & Validation

### Happy Path
1. User has active chat session with context
2. User toggles to GuideAgent
3. `initiate_guide_agent` intent executes
4. Chat session retrieved, conversation history loaded
5. Shared context retrieved (if toggled from Liaison Agent)
6. Curator queried for all MCP tools (all orchestrators)
7. Platform context built (solutions, pillars, capabilities)
8. Returns GuideAgent conversation artifact with MCP tools and context
9. GuideAgent ready to process messages

### Boundary Violations
- **Session not found:** Chat session does not exist -> Returns `ERROR_CODE: "SESSION_NOT_FOUND"`
- **No MCP tools available:** Curator returns no tools -> GuideAgent initializes with empty MCP tools list (still functional)

### Failure Scenarios
- **Curator unavailable:** Cannot query Curator -> Returns `ERROR_CODE: "CURATOR_UNAVAILABLE"`, GuideAgent initializes without MCP tools (graceful degradation)
- **Context load failure:** Cannot load context -> Returns `ERROR_CODE: "CONTEXT_LOAD_FAILED"`, GuideAgent initializes with empty context

---

## 10. Contract Compliance

### Required Artifacts
- `guide_agent_conversation` - Required (GuideAgent conversation artifact)

### Required Events
- `guide_agent_initialized` - Required (emitted when GuideAgent is initialized)

### Lifecycle State
- **No lifecycle state** - This is an initialization-only intent with no persistent artifacts
- **Conversation state** - Stored in chat session context (ephemeral)

### Contract Validation
- ✅ Intent must return GuideAgent conversation artifact with MCP tools and context
- ✅ MCP tools must be queried from Curator (all orchestrators)
- ✅ Shared context must be loaded (if available from previous agent)
- ✅ Conversation history must be loaded from chat session
- ✅ Platform context must be built (solutions, pillars, capabilities)
- ✅ No side effects (no artifacts created, no state changes)

---

**Last Updated:** January 27, 2026  
**Owner:** Coexistence Solution Team  
**Status:** ✅ **ENHANCED** - Ready for implementation
