# Intent Contract: sop_chat_message

**Intent:** sop_chat_message  
**Intent Type:** `sop_chat_message`  
**Journey:** SOP Management (`journey_sop_management`)  
**Realm:** Journey Realm  
**Status:** ✅ **COMPREHENSIVE**  
**Priority:** 🔴 **PRIORITY 1** - Chat interaction for SOP creation

---

## 1. Intent Overview

### Purpose
Process a chat message in an active SOP generation session. Updates the SOP structure based on user input and returns agent guidance response.

### Intent Flow
```
[User sends message in SOP chat]
    ↓
[sop_chat_message intent]
    ↓
[JourneyLiaisonAgent.process_chat_message()]
    ↓
[Understand conversation intent via LLM]
[Extract title, steps, requirements]
[Update SOP structure]
[Generate guidance response]
    ↓
[Return chat response and updated structure]
```

### Expected Observable Artifacts
- `chat_response` - Agent response to user message
- `session_id` - Chat session identifier
- `sop_structure` - Updated SOP structure

---

## 2. Intent Parameters

### Required Parameters

| Parameter | Type | Description | Validation |
|-----------|------|-------------|------------|
| `session_id` | `string` | Chat session identifier | Required, non-empty |
| `message` | `string` | User message | Required, non-empty |

### Context Metadata (from ExecutionContext)

| Metadata Key | Type | Description | Source |
|--------------|------|-------------|--------|
| `tenant_id` | `string` | Tenant identifier | Runtime (required) |
| `session_id` | `string` | Session identifier | Runtime (required) |

---

## 3. Intent Returns

### Success Response

```json
{
  "artifacts": {
    "chat_response": {
      "session_id": "chat_abc123",
      "response": "Great! I've added 'Data Collection' as Step 1. What should the next step be?",
      "sop_structure": {
        "title": "Inventory Management SOP",
        "description": null,
        "steps": [
          {
            "step_number": 1,
            "name": "Data Collection",
            "description": "Collect inventory data from warehouse",
            "checkpoint": false
          }
        ],
        "checkpoints": [],
        "requirements": []
      },
      "updated": true,
      "status": "gathering_requirements"
    },
    "session_id": "chat_abc123"
  },
  "events": [
    {
      "type": "sop_chat_message_processed",
      "session_id": "chat_abc123"
    }
  ]
}
```

### Error Response

```json
{
  "error": "session_id is required for sop_chat_message intent",
  "error_code": "VALIDATION_ERROR",
  "execution_id": "exec_abc123"
}
```

---

## 4. Artifact Registration

### State Surface Updates
- Chat session state updated via `store_session_state()`
- SOP structure incrementally updated
- Conversation history appended

---

## 5. Idempotency

### Idempotency Key
Not idempotent - each message is processed sequentially

### Behavior
- Each message adds to conversation history
- Same message may produce different responses based on context
- Retry may add duplicate messages (design consideration)

---

## 6. Implementation Details

### Handler Location
`symphainy_platform/realms/journey/orchestrators/journey_orchestrator.py::JourneyOrchestrator._handle_sop_chat_message`

### Key Implementation Steps
1. Validate `session_id` and `message` provided
2. Call `JourneyLiaisonAgent.process_chat_message()`
3. Agent retrieves session state
4. Agent uses LLM to understand conversation intent
5. Agent extracts title, steps, requirements
6. Agent updates SOP structure
7. Agent generates guidance response
8. Agent stores updated session state
9. Return chat response artifact

### Agents
- **JourneyLiaisonAgent:** `symphainy_platform/realms/journey/agents/journey_liaison_agent.py`
  - `process_chat_message()` - Process message and update SOP structure
  - `_understand_conversation_intent()` - LLM-based intent understanding

### LLM Usage
- Agent uses LLM to understand user intent (not execute)
- Extracts: title, step info, guidance response
- Determines if requirements are complete

### Session State Structure
```json
{
  "sop_chat_session": {
    "session_id": "chat_abc123",
    "sop_structure": {
      "title": null,
      "description": null,
      "steps": [],
      "checkpoints": [],
      "requirements": []
    },
    "conversation_history": [
      {"role": "user", "message": "...", "timestamp": "..."},
      {"role": "assistant", "message": "...", "timestamp": "..."}
    ],
    "status": "gathering_requirements"
  }
}
```

---

## 7. Frontend Integration

### Frontend Usage (JourneyAPIManager.ts)
```typescript
// Process user message
const response = await journeyManager.processWizardConversation(
  userMessage,
  sessionId,
  {}
);

if (response.success) {
  // Display agent response
  displayMessage(response.agent_response);
  // Update SOP preview
  updateSOPPreview(response.draft_sop);
}
```

### Expected Frontend Behavior
1. User types message in chat
2. Frontend submits `sop_chat_message` intent
3. Track execution
4. Display agent response
5. Update SOP structure preview
6. Continue conversation or trigger generation

---

## 8. Error Handling

### Validation Errors
- `session_id` missing → `ValueError`
- `message` missing → `ValueError`

### Runtime Errors
- Session not found → Return error suggestion to start new session
- LLM fails → Fallback to pattern matching

---

## 9. Testing & Validation

### Happy Path
1. Active chat session exists
2. User sends message
3. Agent extracts intent and updates SOP
4. Return guidance response

### Boundary Violations
- Missing `session_id` → Validation error
- Missing `message` → Validation error

---

## 10. Contract Compliance

### Required Artifacts
- `chat_response` - Agent response and updated SOP structure

### Required Events
- `sop_chat_message_processed` - With `session_id`

---

## 11. Cross-Reference Analysis

### Journey Contract Says
- `chat_with_journey_agent` - Chat with agent

### Implementation Does
- ✅ `sop_chat_message` processes chat messages
- ✅ Uses JourneyLiaisonAgent
- ✅ Updates SOP structure incrementally

### Frontend Expects
- ✅ `process_wizard_conversation` maps to this
- ✅ Returns agent response and draft SOP

### Gaps/Discrepancies
- **NAMING:** Contract says `chat_with_journey_agent`, implementation uses `sop_chat_message`
- **Recommendation:** Use `sop_chat_message` (more specific)

---

**Last Updated:** January 27, 2026  
**Owner:** Journey Realm Solution Team  
**Status:** ✅ **COMPREHENSIVE**
