# Journey Contract: Agent-Orchestrator Interaction

**Journey:** Agent-Orchestrator Interaction  
**Journey ID:** `journey_coexistence_orchestrator_interaction`  
**Solution:** Coexistence Solution  
**Status:** ⏳ **IN PROGRESS**  
**Priority:** 🔴 **PRIORITY 1** - Foundation journey for Coexistence Solution

---

## 1. Journey Overview

### Intents in Journey
1. `list_available_mcp_tools` - Step 1: List available orchestrator MCP tools for agent
2. `validate_mcp_tool_call` - Step 2: Validate MCP tool call against governance (before execution)
3. `call_orchestrator_mcp_tool` - Step 3: Call orchestrator MCP tool with parameters

### Journey Flow
```
[Agent needs to execute platform action]
    ↓
[list_available_mcp_tools] → available_mcp_tools_artifact
    - Agent queries Curator for available MCP tools
    - Tools filtered by agent type (GuideAgent: all, Liaison: pillar-specific)
    - Tool metadata returned (name, description, parameters, governance rules)
    ↓
[validate_mcp_tool_call] → validation_result_artifact
    - MCP tool call validated against governance policies
    - Smart City Primitives check permissions, rate limits, etc.
    - Validation result returned (approved/rejected, reason)
    ↓
[call_orchestrator_mcp_tool] → mcp_tool_result_artifact
    - MCP tool called with parameters
    - Tool executes orchestrator journey/intent
    - Execution results returned
    - Results formatted for agent response
    ↓
[Journey Complete]
```

### Expected Observable Artifacts
- **Step 1 (list_available_mcp_tools):**
  - `available_mcp_tools_artifact` - List of available MCP tools
  - `tools` - Array of tool metadata (name, description, parameters, governance)
  - `filtered_by_agent` - Tools filtered by agent type

- **Step 2 (validate_mcp_tool_call):**
  - `validation_result_artifact` - Validation result
  - `approved` - Whether call is approved
  - `rejection_reason` - Reason if rejected
  - `governance_checks` - List of governance checks performed

- **Step 3 (call_orchestrator_mcp_tool):**
  - `mcp_tool_result_artifact` - MCP tool execution result
  - `tool_name` - Name of tool called
  - `execution_status` - Success/failure status
  - `results` - Execution results (if successful)
  - `error` - Error message (if failed)

### Artifact Lifecycle State Transitions
- **Step 3:** MCP tool result artifact created with `lifecycle_state: "COMPLETED"` (if successful) or `"FAILED"` (if failed)

### Idempotency Scope (Per Intent)

| Intent | Idempotency Key | Scope |
|--------|-----------------|-------|
| `list_available_mcp_tools` | N/A (no side effects, retrieval only) | N/A |
| `validate_mcp_tool_call` | N/A (no side effects, validation only) | N/A |
| `call_orchestrator_mcp_tool` | `hash(tool_name + tool_params + agent_id)` | Per tool, per parameters, per agent |

### Journey Completion Definition

**Journey is considered complete when:**

* Available MCP tools are listed for agent **OR**
* MCP tool call is validated (approved or rejected) **OR**
* Orchestrator MCP tool is called and execution results are returned

**Journey completion = agent successfully interacts with orchestrator via MCP tool (or receives validation result).**

---

**Last Updated:** January 27, 2026  
**Owner:** Coexistence Solution Team  
**Status:** ⏳ **IN PROGRESS**
