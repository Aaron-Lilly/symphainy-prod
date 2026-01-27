#!/usr/bin/env python3
"""
Batch enhancement script for remaining 8 Coexistence intent contracts.
Enhances all sections following the established pattern.
"""

import os
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
INTENTS_DIR = BASE_DIR / "docs" / "intent_contracts"

# Enhancement templates for each intent
ENHANCEMENTS = {
    "intent_process_liaison_agent_message": {
        "flow": """[User sends message to Liaison Agent]
    ↓
[process_liaison_agent_message intent executes]
    ↓
[Load Liaison Agent conversation state (from initiate_liaison_agent)]
    ↓
[Process user message with pillar-specific knowledge]
    ↓
[Optionally: Determine if pillar MCP tool call needed]
    ↓
[Optionally: Call pillar orchestrator MCP tool via call_orchestrator_mcp_tool (governed)]
    ↓
[Generate response (with MCP tool results if called)]
    ↓
[Update conversation context with message and response]
    ↓
[Returns liaison_agent_response_artifact]""",
        "artifacts": """- `liaison_agent_response_artifact` - Response artifact with message and optional MCP tool results
- `mcp_tool_call_artifact` - MCP tool call artifact (if tool was called)
- `conversation_context` - Updated conversation context (message + response added)""",
        "context_metadata": """| Metadata Key | Type | Description | Source |
|--------------|------|-------------|--------|
| `user_id` | `string` | User identifier | Runtime (required) |
| `tenant_id` | `string` | Tenant identifier | Runtime (required) |
| `chat_session` | `object` | Chat session artifact | Previous intent result (optional) |
| `liaison_agent_conversation` | `object` | Liaison Agent conversation state | Previous intent result (from initiate_liaison_agent) |""",
        "success_response": """{
  "artifacts": {
    "liaison_agent_response": {
      "result_type": "liaison_agent_response",
      "semantic_payload": {
        "message": "I can help you parse that file. Let me upload it for you.",
        "mcp_tool_called": true,
        "mcp_tool_result": {
          "tool_name": "content_parse_file",
          "execution_status": "completed",
          "results": {"file_id": "file_abc123", "artifact_id": "artifact_xyz789"}
        },
        "conversation_context": {"conversation_history": [...]}
      }
    }
  },
  "events": [{"type": "liaison_agent_message_processed", "pillar_type": "content", "mcp_tool_called": true}]
}""",
        "artifact_registration": """### State Surface Registration
- **No artifacts registered** - Response is ephemeral, stored in chat session context
- Conversation context updated in chat session (via `update_chat_context`)

### Artifact Index Registration
- **No artifacts indexed** - Response-only intent
- Conversation history stored in chat session context (chat_sessions table)""",
        "idempotency": """N/A - Stateless processing, no side effects""",
        "idempotency_scope": "N/A - Stateless processing, no side effects",
        "idempotency_behavior": "This intent processes messages statelessly (no persistent artifacts created). Context updates happen via `update_chat_context` (separate intent). MCP tool calls are idempotent (handled by `call_orchestrator_mcp_tool` intent).""",
        "implementation": """### Handler Location
- **New Implementation:** `symphainy_platform/realms/coexistence/intent_services/process_liaison_agent_message_service.py` (to be created)

### Key Implementation Steps
1. **Extract Parameters:** Get `message`, `pillar_type`, `chat_session_id`, `conversation_context` from intent parameters
2. **Load Liaison Agent State:**
   - If `conversation_context` provided: Use it
   - If not: Load from chat session (via `get_chat_session`)
   - Load available pillar MCP tools (from `initiate_liaison_agent` state)
3. **Process User Message:**
   - Use Liaison Agent LLM to process message with pillar-specific knowledge
   - Liaison Agent has access to: pillar artifacts, pillar state, pillar capabilities
   - Liaison Agent can reason about which pillar MCP tool to call (if needed)
4. **Determine Pillar MCP Tool Call (Optional):**
   - If `mcp_tool_to_call` provided: Use specified tool
   - If not: Liaison Agent determines if pillar MCP tool call is needed based on message
   - If tool needed: Validate tool exists and is pillar-specific
5. **Call Pillar MCP Tool (Optional):**
   - If pillar MCP tool call needed: Call `call_orchestrator_mcp_tool` intent (with pillar filter)
   - Tool executes pillar journey/intent
   - Results returned to Liaison Agent
6. **Generate Response:**
   - Liaison Agent generates response using:
     - Pillar-specific knowledge
     - Conversation history
     - Pillar MCP tool results (if tool was called)
7. **Update Conversation Context:**
   - Add user message and agent response to conversation history
   - Call `update_chat_context` intent to persist context
8. **Return Liaison Agent Response:**
   - Return `message`, `mcp_tool_called`, `mcp_tool_result` (if called), `conversation_context`

### Dependencies
- **Public Works:**
  - `CuratorSDK` - For MCP tool discovery (pillar-filtered, if needed)
- **State Surface:**
  - `get_artifact()` - Retrieve chat session artifact
- **Runtime:**
  - `ExecutionContext` - Tenant, user, session, execution context
- **Other Intents:**
  - `call_orchestrator_mcp_tool` - For pillar MCP tool execution
  - `update_chat_context` - For context persistence""",
        "frontend_usage": """// When user sends message to Liaison Agent
const executionId = await platformState.submitIntent(
  'process_liaison_agent_message',
  {
    message: userMessage,
    pillar_type: 'content',
    chat_session_id: sessionId
  }
);""",
        "frontend_behavior": """1. **User sends message** - Frontend calls this intent with user message and pillar_type
2. **Response received** - Frontend displays Liaison Agent response
3. **Pillar MCP tool results** - If pillar MCP tool was called, frontend shows execution results
4. **Context updated** - Conversation context automatically updated
5. **History preserved** - Conversation history available for next message""",
        "validation_errors": """- **Missing message:** `ValueError("message is required")` -> Returns error response with `ERROR_CODE: "MISSING_PARAMETER"`
- **Empty message:** Message is empty string -> Returns error response with `ERROR_CODE: "EMPTY_MESSAGE"`
- **Missing pillar_type:** `ValueError("pillar_type is required")` -> Returns error response with `ERROR_CODE: "MISSING_PARAMETER"`
- **Invalid pillar_type:** Pillar not valid -> Returns error response with `ERROR_CODE: "INVALID_PILLAR"`""",
        "runtime_errors": """- **Chat session not found:** Chat session does not exist -> Returns error response with `ERROR_CODE: "SESSION_NOT_FOUND"`
- **Liaison Agent unavailable:** Liaison Agent LLM service unavailable -> Returns error response with `ERROR_CODE: "LIAISON_AGENT_UNAVAILABLE"`
- **Pillar MCP tool call failed:** Pillar MCP tool execution failed -> Returns error response with `ERROR_CODE: "PILLAR_MCP_TOOL_CALL_FAILED"` (response may still be generated without tool results)
- **Context update failed:** Cannot update conversation context -> Returns error response with `ERROR_CODE: "CONTEXT_UPDATE_FAILED"` (response still returned)""",
        "error_response": """{
  "error": "Error message",
  "error_code": "ERROR_CODE",
  "execution_id": "exec_abc123",
  "intent_type": "process_liaison_agent_message"
}""",
        "happy_path": """1. User sends message: "Parse this file" to Content Liaison Agent
2. `process_liaison_agent_message` intent executes with message and `pillar_type: "content"`
3. Liaison Agent conversation state loaded
4. Liaison Agent processes message with Content pillar knowledge
5. Liaison Agent determines Content MCP tool needed: `content_parse_file`
6. Liaison Agent calls `call_orchestrator_mcp_tool` intent (pillar-filtered)
7. Pillar MCP tool executes file parsing journey
8. Liaison Agent generates response with tool results
9. Conversation context updated with message and response
10. Returns response: "I've parsed your file. File ID: file_abc123\"""",
        "boundary_violations": """- **Empty message:** Message is empty -> Returns `ERROR_CODE: "EMPTY_MESSAGE"`
- **Message too long:** Message exceeds length limit -> Returns `ERROR_CODE: "MESSAGE_TOO_LONG"` or truncates
- **Invalid pillar_type:** Pillar not valid -> Returns `ERROR_CODE: "INVALID_PILLAR"`""",
        "failure_scenarios": """- **Liaison Agent unavailable:** LLM service down -> Returns `ERROR_CODE: "LIAISON_AGENT_UNAVAILABLE"`, frontend shows error
- **Pillar MCP tool call failed:** Tool execution fails -> Returns `ERROR_CODE: "PILLAR_MCP_TOOL_CALL_FAILED"`, Liaison Agent may still respond without tool results
- **Context update failed:** Cannot update context -> Returns `ERROR_CODE: "CONTEXT_UPDATE_FAILED"`, response still returned but context not persisted""",
        "contract_compliance": """### Required Artifacts
- `liaison_agent_response` - Required (Liaison Agent response artifact)

### Required Events
- `liaison_agent_message_processed` - Required (emitted when message is processed)

### Lifecycle State
- **No lifecycle state** - This is a stateless processing intent with no persistent artifacts
- **Conversation context** - Updated in chat session (via `update_chat_context`)

### Contract Validation
- ✅ Intent must return Liaison Agent response with message
- ✅ Pillar MCP tool results must be included if tool was called
- ✅ Conversation context must be updated (via `update_chat_context`)
- ✅ No side effects (no artifacts created, context updated separately)
- ✅ Stateless processing (can be called multiple times with same message)"""
    }
}

def enhance_file(file_path, enhancement):
    """Enhance a single intent contract file"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Replace sections
    replacements = [
        (r'### Intent Flow\n```\n\[Describe the flow for this intent\]\n```', 
         f'### Intent Flow\n```\n{enhancement["flow"]}\n```'),
        (r'### Expected Observable Artifacts\n- \[List expected artifacts\]', 
         f'### Expected Observable Artifacts\n{enhancement["artifacts"]}'),
        (r'### Context Metadata.*?\n\| `metadata_key` \| `type` \| Description \| Runtime \|', 
         f'### Context Metadata (from ExecutionContext)\n\n{enhancement["context_metadata"]}', flags=re.DOTALL),
        (r'### Success Response.*?```json\n\{.*?\n\}.*?```', 
         f'### Success Response\n\n```json\n{enhancement["success_response"]}\n```', flags=re.DOTALL),
        (r'## 4\. Artifact Registration.*?## 5\. Idempotency', 
         f'## 4. Artifact Registration\n\n{enhancement["artifact_registration"]}\n\n---\n\n## 5. Idempotency', flags=re.DOTALL),
        (r'### Idempotency Key.*?### Behavior.*?- \[Describe idempotent behavior\]', 
         f'### Idempotency Key\n```\n{enhancement["idempotency"]}\n```\n\n### Scope\n- {enhancement["idempotency_scope"]}\n\n### Behavior\n- {enhancement["idempotency_behavior"]}', flags=re.DOTALL),
        (r'## 6\. Implementation Details.*?## 7\. Frontend Integration', 
         f'## 6. Implementation Details\n\n{enhancement["implementation"]}\n\n---\n\n## 7. Frontend Integration', flags=re.DOTALL),
        (r'### Frontend Usage.*?### Expected Frontend Behavior.*?2\. \[Behavior 2\]', 
         f'### Frontend Usage\n```typescript\n{enhancement["frontend_usage"]}\n```\n\n### Expected Frontend Behavior\n{enhancement["frontend_behavior"]}', flags=re.DOTALL),
        (r'### Validation Errors.*?### Error Response Format.*?```', 
         f'### Validation Errors\n{enhancement["validation_errors"]}\n\n### Runtime Errors\n{enhancement["runtime_errors"]}\n\n### Error Response Format\n```json\n{enhancement["error_response"]}\n```', flags=re.DOTALL),
        (r'### Happy Path.*?### Failure Scenarios.*?- \[Failure type\] -> \[Expected behavior\]', 
         f'### Happy Path\n{enhancement["happy_path"]}\n\n### Boundary Violations\n{enhancement["boundary_violations"]}\n\n### Failure Scenarios\n{enhancement["failure_scenarios"]}', flags=re.DOTALL),
        (r'## 10\. Contract Compliance.*?\*\*Status:\*\* ⏳ \*\*IN PROGRESS\*\*', 
         f'## 10. Contract Compliance\n\n{enhancement["contract_compliance"]}\n\n---\n\n**Last Updated:** January 27, 2026\n**Owner:** Coexistence Solution Team\n**Status:** ✅ **ENHANCED** - Ready for implementation', flags=re.DOTALL),
    ]
    
    for pattern, replacement in replacements:
        if isinstance(pattern, tuple):
            pattern, flags = pattern
        else:
            flags = 0
        content = re.sub(pattern, replacement, content, flags=flags)
    
    # Update status
    content = re.sub(r'\*\*Status:\*\* ⏳ \*\*IN PROGRESS\*\*', '**Status:** ✅ **ENHANCED** - Ready for implementation', content)
    content = re.sub(r'\*\*Status:\*\* IN PROGRESS', '**Status:** ✅ **ENHANCED** - Ready for implementation', content)
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    return True

if __name__ == "__main__":
    # Enhance process_liaison_agent_message
    file_path = INTENTS_DIR / "journey_coexistence_liaison_agent" / "intent_process_liaison_agent_message.md"
    if file_path.exists() and "intent_process_liaison_agent_message" in ENHANCEMENTS:
        enhance_file(file_path, ENHANCEMENTS["intent_process_liaison_agent_message"])
        print(f"✅ Enhanced {file_path.name}")
    else:
        print(f"❌ File not found or no enhancement data: {file_path}")
