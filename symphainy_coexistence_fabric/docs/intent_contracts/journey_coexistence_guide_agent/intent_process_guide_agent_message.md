# Intent Contract: process_guide_agent_message

**Intent:** process_guide_agent_message  
**Intent Type:** `process_guide_agent_message`  
**Journey:** GuideAgent Interaction (`journey_coexistence_guide_agent`)  
**Solution:** Coexistence Solution  
**Status:** ENHANCED  
**Priority:** PRIORITY 1

---

## 1. Intent Overview

### Purpose
Processes a user message sent to the GuideAgent and returns the agent's response. The GuideAgent can answer questions about the platform, explain coexistence concepts, provide navigation guidance, and help users understand their artifacts and journey progress.

### Intent Flow
```
[User sends message to GuideAgent]
    ↓
[Validate agent session is active]
    ↓
[Analyze message intent and context]
    ↓
[Generate response with GuideAgent LLM]
    ↓
[Determine if action needed (navigation, liaison handoff)]
    ↓
[Return response with suggestions and actions]
```

### Expected Observable Artifacts
- `conversation_turn` - Agent response with suggestions and potential actions

---

## 2. Intent Parameters

### Required Parameters

| Parameter | Type | Description | Validation |
|-----------|------|-------------|------------|
| `agent_session_id` | `string` | Active GuideAgent session | Must be valid active session |
| `message` | `string` | User's message content | Non-empty string |
| `user_context` | `object` | User context with session_id | Must include session_id |

### Optional Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `message_context` | `object` | Additional context (selected artifact, etc.) | {} |
| `response_format` | `string` | Format: "conversational", "structured" | "conversational" |
| `include_actions` | `boolean` | Include actionable suggestions | true |

### Context Metadata (from ExecutionContext)

| Metadata Key | Type | Description | Source |
|--------------|------|-------------|--------|
| `tenant_id` | `string` | Tenant identifier | Runtime |
| `session_id` | `string` | Session identifier | Runtime |
| `conversation_history` | `array` | Previous messages in session | Agent state |

---

## 3. Intent Returns

### Success Response

```json
{
  "artifacts": {
    "conversation_turn": {
      "result_type": "guide_agent_response",
      "semantic_payload": {
        "message_id": "msg_abc123",
        "response_type": "explanation",
        "requires_action": false
      },
      "renderings": {
        "response": {
          "role": "assistant",
          "content": "Great question! **Coexistence** in the Symphainy platform means enabling your existing systems to work together with modern AI capabilities without replacing them.\n\nThink of it like this: instead of ripping out your legacy SAP system, we help you build bridges between SAP, your modern tools, and AI agents. The platform coordinates work that crosses these boundaries.\n\nWould you like me to show you an example of how this works in practice?",
          "timestamp": "2026-01-27T10:16:30Z"
        },
        "suggestions": [
          "Show me an example",
          "How does it work with my data?",
          "Take me to coexistence analysis"
        ],
        "detected_intent": {
          "intent_type": "concept_explanation",
          "confidence": 0.92,
          "entities": ["coexistence"]
        },
        "actions": [],
        "follow_up_prompt": "Would you like to see this in action with your own data?"
      }
    }
  },
  "events": [
    {
      "type": "guide_agent_message_processed",
      "agent_session_id": "agent_sess_xyz789",
      "message_intent": "concept_explanation",
      "response_type": "explanation"
    }
  ]
}
```

### Response with Action

```json
{
  "artifacts": {
    "conversation_turn": {
      "result_type": "guide_agent_response",
      "semantic_payload": {
        "message_id": "msg_def456",
        "response_type": "navigation",
        "requires_action": true
      },
      "renderings": {
        "response": {
          "role": "assistant",
          "content": "I'll help you get to the Content pillar where you can upload your files. Click the button below to navigate there, or I can explain what you'll be able to do once you're there.",
          "timestamp": "2026-01-27T10:17:00Z"
        },
        "suggestions": [
          "What can I do in Content?",
          "What file types are supported?"
        ],
        "detected_intent": {
          "intent_type": "navigation_request",
          "confidence": 0.95,
          "entities": ["content_pillar"]
        },
        "actions": [
          {
            "action_type": "navigate",
            "label": "Go to Content",
            "intent": "navigate_to_solution",
            "parameters": {
              "solution_id": "content_solution",
              "pillar_name": "content"
            }
          }
        ],
        "follow_up_prompt": null
      }
    }
  },
  "events": [
    {
      "type": "guide_agent_message_processed",
      "agent_session_id": "agent_sess_xyz789",
      "message_intent": "navigation_request",
      "response_type": "navigation"
    }
  ]
}
```

---

## 4. Artifact Registration

### State Surface Registration
- **Artifact ID:** `conv_{agent_session_id}_{message_id}`
- **Artifact Type:** `"guide_agent_response"`
- **Lifecycle State:** `"READY"`
- **Produced By:** `{ intent: "process_guide_agent_message", execution_id: "<execution_id>" }`
- **Materializations:** Conversation history (persisted if enabled)

### Artifact Index Registration
- Indexed for analytics: agent_session_id, message_intent, timestamp

---

## 5. Idempotency

### Idempotency Key
```
idempotency_key = hash(agent_session_id + message + timestamp_bucket + "process_guide_agent_message")
```

### Scope
- Per agent session + message + time bucket (1 second)

### Behavior
- Same message within 1 second returns cached response
- Prevents duplicate processing on retry

---

## 6. Implementation Details

### Handler Location
`symphainy_platform/solutions/coexistence/journeys/guide_agent_journey.py`

### Key Implementation Steps
1. Validate agent_session_id is active
2. Load conversation history from session
3. Analyze message to determine intent (LLM or rules)
4. Load relevant context (current pillar, artifacts, goals)
5. Generate response using GuideAgent LLM
6. Determine if action is needed
7. Store conversation turn in history
8. Return response artifact

### Dependencies
- **Public Works:** llm_abstraction (for GuideAgent responses)
- **State Surface:** conversation history
- **Runtime:** ExecutionContext
- **Agent Framework:** GuideAgent prompts and configuration

---

## 7. Frontend Integration

### Frontend Usage
```typescript
// Send message to GuideAgent
const response = await platformState.submitIntent({
  intent_type: "process_guide_agent_message",
  parameters: {
    agent_session_id: agentSessionId,
    message: userMessage,
    user_context: { session_id },
    include_actions: true
  }
});

const turn = response.artifacts?.conversation_turn?.renderings;
addMessage(turn.response);
setSuggestions(turn.suggestions);

// Handle actions if present
if (turn.actions?.length > 0) {
  setActionButtons(turn.actions);
}
```

### Expected Frontend Behavior
1. Display user message immediately
2. Show typing indicator
3. Display agent response when received
4. Show suggestions as quick actions
5. Render action buttons if present
6. Handle action button clicks (navigation, etc.)

---

## 8. Error Handling

### Validation Errors
- Invalid agent_session_id → Return SESSION_EXPIRED error
- Empty message → Return EMPTY_MESSAGE error

### Runtime Errors
- LLM unavailable → Return fallback response
- Timeout → Return partial response with retry option

### Error Response Format
```json
{
  "error": "Agent session expired",
  "error_code": "SESSION_EXPIRED",
  "execution_id": "exec_abc123",
  "recovery_action": {
    "intent": "initiate_guide_agent",
    "message": "Your session expired. Starting a new conversation."
  }
}
```

---

## 9. Testing & Validation

### Happy Path
1. User sends message
2. Agent processes and responds
3. Verify response contextual
4. Verify suggestions relevant
5. Verify actions work if present

### Boundary Violations
- Very long message → Truncate and process
- Profanity/abuse → Return polite redirect

### Failure Scenarios
- LLM timeout → Return "thinking" message with retry
- Session expired → Auto-initiate new session

---

## 10. Contract Compliance

### Required Artifacts
- `conversation_turn` - Required (guide_agent_response type)

### Required Events
- `guide_agent_message_processed` - Required

### Lifecycle State
- Always READY

---

**Last Updated:** January 27, 2026  
**Owner:** Coexistence Solution Team  
**Status:** ENHANCED
