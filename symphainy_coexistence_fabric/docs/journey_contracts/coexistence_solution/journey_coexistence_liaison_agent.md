# Journey Contract: Liaison Agent Conversation

**Journey:** Liaison Agent Conversation  
**Journey ID:** `journey_coexistence_liaison_agent`  
**Solution:** Coexistence Solution  
**Status:** ⏳ **IN PROGRESS**  
**Priority:** 🔴 **PRIORITY 1** - Foundation journey for Coexistence Solution

---

## 1. Journey Overview

### Intents in Journey
1. `initiate_liaison_agent` - Step 1: Initialize Liaison Agent conversation with pillar-specific context
2. `get_pillar_context` - Step 2: Retrieve pillar-specific context for Liaison Agent
3. `process_liaison_agent_message` - Step 3: Process user message, generate response, optionally call pillar MCP tools
4. `execute_pillar_action` - Step 4: Execute pillar-specific action via pillar orchestrator MCP tool

### Journey Flow
```
[User sends message to Liaison Agent or toggles to Liaison Agent]
    ↓
[initiate_liaison_agent] → liaison_agent_conversation_artifact
    - Liaison Agent initialized with pillar-specific context
    - Pillar identified (content, insights, journey, or solution)
    - Access to pillar orchestrator MCP tools only (via Curator)
    - Context shared from GuideAgent (if toggled)
    ↓
[get_pillar_context] → pillar_context_artifact
    - Retrieve pillar-specific context (artifacts, state, etc.)
    - Context available for Liaison Agent responses
    ↓
[process_liaison_agent_message] → liaison_agent_response_artifact
    - User message processed
    - Liaison Agent generates response (with pillar-specific knowledge)
    - Optionally: Liaison Agent calls pillar orchestrator MCP tool (governed)
    - MCP tool executes pillar journey/intent
    - Response includes MCP tool results (if called)
    - Conversation context updated
    ↓
[Optionally: execute_pillar_action] → pillar_action_result_artifact
    - Liaison Agent calls pillar orchestrator MCP tool
    - MCP tool validates and executes pillar action
    - Results returned to Liaison Agent
    ↓
[Journey Complete]
```

### Expected Observable Artifacts
- **Step 1 (initiate_liaison_agent):**
  - `liaison_agent_conversation_artifact` - Conversation artifact with pillar-specific context
  - `pillar_type` - Pillar identifier (content, insights, journey, or solution)
  - `available_pillar_mcp_tools` - List of pillar-specific MCP tools
  - `shared_context` - Context shared from GuideAgent (if toggled)

- **Step 2 (get_pillar_context):**
  - `pillar_context_artifact` - Pillar-specific context (artifacts, state, etc.)

- **Step 3 (process_liaison_agent_message):**
  - `liaison_agent_response_artifact` - Response artifact with message and optional MCP tool results
  - `mcp_tool_call_artifact` - MCP tool call artifact (if tool was called)
  - `conversation_context` - Updated conversation context

- **Step 4 (execute_pillar_action):**
  - `pillar_action_result_artifact` - Result artifact from pillar orchestrator MCP tool

### Artifact Lifecycle State Transitions
- **Step 1:** Liaison Agent conversation artifact created with `lifecycle_state: "ACTIVE"`
- **Step 3:** Conversation context updated (lifecycle state remains ACTIVE)

### Idempotency Scope (Per Intent)

| Intent | Idempotency Key | Scope |
|--------|-----------------|-------|
| `initiate_liaison_agent` | `hash(user_id + pillar_type + timestamp_window)` | Per user, per pillar, per time window |
| `get_pillar_context` | `hash(pillar_type + context_query)` | Per pillar, per context query |
| `process_liaison_agent_message` | N/A (stateless processing) | N/A |
| `execute_pillar_action` | `hash(pillar_type + action_type + action_params)` | Per pillar, per action |

### Journey Completion Definition

**Journey is considered complete when:**

* Liaison Agent processes user message and returns response **OR**
* Liaison Agent successfully calls pillar orchestrator MCP tool and returns results **OR**
* Liaison Agent executes pillar-specific action via MCP tool

**Journey completion = user receives helpful response from Liaison Agent (with optional pillar MCP tool execution).**

---

**Last Updated:** January 27, 2026  
**Owner:** Coexistence Solution Team  
**Status:** ⏳ **IN PROGRESS**
