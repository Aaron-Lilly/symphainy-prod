# Intent Contract: initiate_guide_agent

**Intent:** initiate_guide_agent  
**Intent Type:** `initiate_guide_agent`  
**Journey:** GuideAgent Interaction (`journey_coexistence_guide_agent`)  
**Solution:** Coexistence Solution  
**Status:** ENHANCED  
**Priority:** PRIORITY 1

---

## 1. Intent Overview

### Purpose
Initiates a conversation with the GuideAgent - the platform's AI assistant that helps users navigate the platform, understand coexistence concepts, and find the right solutions for their needs. This intent creates a new agent session and returns an initial greeting.

### Intent Flow
```
[User opens chat or requests guide]
    ↓
[Create GuideAgent session]
    ↓
[Load user context and history (if available)]
    ↓
[Generate contextual greeting]
    ↓
[Return agent session with initial message]
```

### Expected Observable Artifacts
- `agent_session` - GuideAgent session with initial greeting

---

## 2. Intent Parameters

### Required Parameters

| Parameter | Type | Description | Validation |
|-----------|------|-------------|------------|
| `user_context` | `object` | User context with session_id | Must include session_id |

### Optional Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `trigger_source` | `string` | What triggered the agent: "chat_open", "help_button", "proactive" | "chat_open" |
| `current_pillar` | `string` | User's current location in platform | null |
| `initial_context` | `string` | Any initial context to seed conversation | null |
| `conversation_mode` | `string` | Mode: "guided", "freeform", "diagnostic" | "guided" |

### Context Metadata (from ExecutionContext)

| Metadata Key | Type | Description | Source |
|--------------|------|-------------|--------|
| `tenant_id` | `string` | Tenant identifier | Runtime |
| `session_id` | `string` | Session identifier | Runtime |
| `solution_context` | `object` | Current solution context | State Surface |

---

## 3. Intent Returns

### Success Response

```json
{
  "artifacts": {
    "agent_session": {
      "result_type": "guide_agent_session",
      "semantic_payload": {
        "agent_session_id": "agent_sess_xyz789",
        "agent_type": "guide_agent",
        "conversation_mode": "guided"
      },
      "renderings": {
        "session_info": {
          "agent_session_id": "agent_sess_xyz789",
          "created_at": "2026-01-27T10:15:00Z",
          "expires_at": "2026-01-27T11:15:00Z"
        },
        "initial_message": {
          "role": "assistant",
          "content": "Hello! I'm your Guide through the Symphainy platform. I can help you understand coexistence concepts, navigate to the right solutions, or answer questions about your current journey. What would you like to explore today?",
          "suggestions": [
            "What is coexistence?",
            "Help me find a solution for my needs",
            "Show me what I can do here",
            "Explain the current pillar"
          ]
        },
        "agent_capabilities": [
          "Platform navigation assistance",
          "Coexistence concept explanation",
          "Solution recommendations",
          "Journey guidance",
          "Artifact explanation"
        ],
        "context_awareness": {
          "knows_current_pillar": true,
          "knows_user_goals": true,
          "knows_artifacts": true,
          "current_pillar": "content",
          "user_has_goals": true
        }
      }
    }
  },
  "events": [
    {
      "type": "guide_agent_initiated",
      "agent_session_id": "agent_sess_xyz789",
      "trigger_source": "chat_open",
      "conversation_mode": "guided"
    }
  ]
}
```

---

## 4. Artifact Registration

### State Surface Registration
- **Artifact ID:** `agent_{session_id}_{agent_session_id}`
- **Artifact Type:** `"guide_agent_session"`
- **Lifecycle State:** `"READY"`
- **Produced By:** `{ intent: "initiate_guide_agent", execution_id: "<execution_id>" }`
- **Materializations:** In-memory with TTL (1 hour)

### Artifact Index Registration
- Indexed for analytics: session_id, agent_session_id, created_at

---

## 5. Idempotency

### Idempotency Key
```
idempotency_key = hash(session_id + trigger_source + "initiate_guide_agent")
```

### Scope
- Per session + trigger (reuse active session)

### Behavior
- Returns existing active session if one exists
- Creates new session if no active session

---

## 6. Implementation Details

### Handler Location
`symphainy_platform/solutions/coexistence/journeys/guide_agent_journey.py`

### Key Implementation Steps
1. Check for existing active agent session
2. If active, return existing session
3. Create new agent session with unique ID
4. Load user context (goals, pillar, artifacts)
5. Generate contextual greeting based on state
6. Return agent session artifact

### Dependencies
- **Public Works:** telemetry_abstraction (agent analytics)
- **State Surface:** session state, agent sessions
- **Runtime:** ExecutionContext
- **Agent Framework:** GuideAgent configuration

---

## 7. Frontend Integration

### Frontend Usage
```typescript
// From ExperienceLayerProvider - useGuideAgent hook
const initResult = await platformState.submitIntent({
  intent_type: "initiate_guide_agent",
  parameters: {
    user_context: { session_id },
    trigger_source: "chat_open",
    current_pillar: currentPillar,
    conversation_mode: "guided"
  }
});

const session = initResult.artifacts?.agent_session?.renderings;
setAgentSessionId(session.session_info.agent_session_id);
addMessage({
  role: "assistant",
  content: session.initial_message.content
});
setSuggestions(session.initial_message.suggestions);
```

### Expected Frontend Behavior
1. Call when user opens chat interface
2. Display initial message from agent
3. Show suggested questions as quick actions
4. Enable message input for conversation

---

## 8. Error Handling

### Validation Errors
- Invalid session_id → Create temporary session

### Runtime Errors
- Agent framework unavailable → Return fallback greeting

### Error Response Format
```json
{
  "error": "Guide Agent temporarily unavailable",
  "error_code": "AGENT_UNAVAILABLE",
  "execution_id": "exec_abc123",
  "fallback_message": "I'm having trouble connecting. Please try again in a moment."
}
```

---

## 9. Testing & Validation

### Happy Path
1. User opens chat
2. Submit initiate_guide_agent
3. Verify agent session created
4. Verify greeting contextual to user state
5. Verify suggestions relevant

### Boundary Violations
- No session → Create ephemeral session
- Invalid conversation_mode → Default to "guided"

---

## 10. Contract Compliance

### Required Artifacts
- `agent_session` - Required (guide_agent_session type)

### Required Events
- `guide_agent_initiated` - Required

### Lifecycle State
- Always READY

---

**Last Updated:** January 27, 2026  
**Owner:** Coexistence Solution Team  
**Status:** ENHANCED
