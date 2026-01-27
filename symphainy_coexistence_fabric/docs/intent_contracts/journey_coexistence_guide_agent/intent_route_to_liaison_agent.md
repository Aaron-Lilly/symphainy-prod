# Intent Contract: route_to_liaison_agent

**Intent:** route_to_liaison_agent  
**Intent Type:** `route_to_liaison_agent`  
**Journey:** GuideAgent Interaction (`journey_coexistence_guide_agent`)  
**Solution:** Coexistence Solution  
**Status:** ENHANCED  
**Priority:** PRIORITY 1

---

## 1. Intent Overview

### Purpose
Routes the conversation from the GuideAgent to a specialized Liaison Agent when the user's needs require domain-specific expertise. Liaison Agents are specialists in specific pillars (Content, Insights, Journey, Outcomes) and can provide deeper assistance than the general GuideAgent.

### Intent Flow
```
[GuideAgent determines specialist needed]
    ↓
[Identify appropriate Liaison Agent]
    ↓
[Transfer conversation context to Liaison]
    ↓
[Initialize Liaison Agent session]
    ↓
[Return handoff confirmation with Liaison greeting]
```

### Expected Observable Artifacts
- `liaison_handoff` - Handoff confirmation with Liaison Agent session

---

## 2. Intent Parameters

### Required Parameters

| Parameter | Type | Description | Validation |
|-----------|------|-------------|------------|
| `agent_session_id` | `string` | Current GuideAgent session | Must be valid active session |
| `liaison_type` | `string` | Target liaison: "content", "insights", "journey", "outcomes", "operations" | Must be valid liaison type |
| `user_context` | `object` | User context with session_id | Must include session_id |

### Optional Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `handoff_reason` | `string` | Why handoff is needed | "user_request" |
| `context_summary` | `string` | Summary of conversation for Liaison | null (auto-generated) |
| `preserve_history` | `boolean` | Pass conversation history to Liaison | true |
| `auto_handoff` | `boolean` | Whether GuideAgent auto-detected need | false |

### Context Metadata (from ExecutionContext)

| Metadata Key | Type | Description | Source |
|--------------|------|-------------|--------|
| `tenant_id` | `string` | Tenant identifier | Runtime |
| `session_id` | `string` | Session identifier | Runtime |
| `guide_agent_session_id` | `string` | Original GuideAgent session | Agent state |

---

## 3. Intent Returns

### Success Response

```json
{
  "artifacts": {
    "liaison_handoff": {
      "result_type": "liaison_agent_handoff",
      "semantic_payload": {
        "from_agent": "guide_agent",
        "to_agent": "operations_liaison",
        "handoff_type": "specialist_routing"
      },
      "renderings": {
        "handoff_confirmation": {
          "success": true,
          "from_agent_id": "agent_sess_xyz789",
          "to_agent_id": "liaison_sess_ops123",
          "liaison_type": "operations",
          "handoff_reason": "User needs help with workflow coexistence analysis"
        },
        "liaison_session": {
          "liaison_session_id": "liaison_sess_ops123",
          "liaison_type": "operations",
          "liaison_name": "Operations Liaison Agent",
          "created_at": "2026-01-27T10:20:00Z"
        },
        "liaison_greeting": {
          "role": "assistant",
          "content": "Hi! I'm the Operations Liaison Agent, and I specialize in workflow management, SOP creation, and coexistence analysis. The Guide told me you're interested in understanding how your current workflows can coexist with new AI capabilities.\n\nI can help you:\n- Analyze existing SOPs and workflows\n- Identify coexistence opportunities\n- Create blueprints for boundary-crossing work\n\nWhat would you like to start with?",
          "suggestions": [
            "Upload an SOP for analysis",
            "Explain coexistence analysis",
            "Show me an example blueprint"
          ]
        },
        "context_transferred": {
          "user_goals": "Automate invoice processing workflow",
          "conversation_summary": "User asked about coexistence and wants to analyze their current workflows",
          "relevant_artifacts": []
        },
        "guide_farewell": {
          "role": "assistant",
          "content": "I'm connecting you with our Operations Liaison Agent who specializes in workflow analysis and coexistence. They'll take great care of you! I'll be here if you need general guidance again.",
          "from_agent": "guide_agent"
        }
      }
    }
  },
  "events": [
    {
      "type": "liaison_handoff_completed",
      "from_agent": "guide_agent",
      "to_agent": "operations_liaison",
      "liaison_session_id": "liaison_sess_ops123",
      "handoff_reason": "specialist_routing"
    }
  ]
}
```

---

## 4. Artifact Registration

### State Surface Registration
- **Artifact ID:** `handoff_{guide_session_id}_{liaison_session_id}`
- **Artifact Type:** `"liaison_agent_handoff"`
- **Lifecycle State:** `"READY"`
- **Produced By:** `{ intent: "route_to_liaison_agent", execution_id: "<execution_id>" }`
- **Materializations:** Logged for analytics

### Artifact Index Registration
- Indexed: guide_session_id, liaison_session_id, liaison_type, timestamp

---

## 5. Idempotency

### Idempotency Key
```
idempotency_key = hash(agent_session_id + liaison_type + "route_to_liaison_agent")
```

### Scope
- Per guide session + liaison type

### Behavior
- Returns existing liaison session if active handoff exists
- Creates new handoff if no active liaison session

---

## 6. Implementation Details

### Handler Location
`symphainy_platform/solutions/coexistence/journeys/guide_agent_journey.py`

### Key Implementation Steps
1. Validate guide_agent_session is active
2. Determine appropriate Liaison Agent based on liaison_type
3. Generate context summary from conversation history
4. Create new Liaison Agent session
5. Transfer context (goals, artifacts, conversation summary)
6. Generate Liaison greeting based on transferred context
7. Generate Guide farewell message
8. Update session state with active liaison

### Dependencies
- **Public Works:** telemetry_abstraction
- **State Surface:** agent sessions, conversation history
- **Runtime:** ExecutionContext
- **Agent Framework:** Liaison Agent configurations

### Liaison Agent Types

| Liaison Type | Specialization | Pillar |
|-------------|----------------|--------|
| `content` | File processing, parsing, embeddings | Content |
| `insights` | Data analysis, quality, interpretation | Insights |
| `journey` / `operations` | Workflows, SOPs, coexistence | Journey |
| `outcomes` | POC generation, roadmaps | Outcomes |

---

## 7. Frontend Integration

### Frontend Usage
```typescript
// GuideAgent triggers handoff or user requests specialist
const handoff = await platformState.submitIntent({
  intent_type: "route_to_liaison_agent",
  parameters: {
    agent_session_id: guideAgentSessionId,
    liaison_type: "operations",
    user_context: { session_id },
    handoff_reason: "User needs workflow analysis help"
  }
});

const result = handoff.artifacts?.liaison_handoff?.renderings;

// Show farewell from Guide
addMessage(result.guide_farewell);

// Switch to Liaison session
setAgentSessionId(result.liaison_session.liaison_session_id);
setAgentType("liaison");

// Show Liaison greeting
addMessage(result.liaison_greeting);
setSuggestions(result.liaison_greeting.suggestions);
```

### Expected Frontend Behavior
1. Display Guide farewell message
2. Visual transition animation (optional)
3. Update agent avatar/branding for Liaison
4. Display Liaison greeting
5. Show Liaison-specific suggestions
6. Continue conversation with Liaison

---

## 8. Error Handling

### Validation Errors
- Invalid liaison_type → Return INVALID_LIAISON_TYPE error
- Inactive guide session → Return SESSION_EXPIRED error

### Runtime Errors
- Liaison unavailable → Keep conversation with Guide, offer retry

### Error Response Format
```json
{
  "error": "Operations Liaison temporarily unavailable",
  "error_code": "LIAISON_UNAVAILABLE",
  "execution_id": "exec_abc123",
  "fallback": {
    "continue_with": "guide_agent",
    "message": "Our Operations specialist is briefly unavailable. I can help you get started with the basics, or you can try again in a moment."
  }
}
```

---

## 9. Testing & Validation

### Happy Path
1. User in Guide session requests specialist
2. Submit route_to_liaison_agent
3. Verify new Liaison session created
4. Verify context transferred
5. Verify Liaison greeting contextual
6. Verify Guide farewell shown

### Boundary Violations
- Unknown liaison_type → Return error with valid types
- No conversation context → Still handoff with default greeting

### Failure Scenarios
- Liaison unavailable → Offer retry or continue with Guide

---

## 10. Contract Compliance

### Required Artifacts
- `liaison_handoff` - Required (liaison_agent_handoff type)

### Required Events
- `liaison_handoff_completed` - Required

### Lifecycle State
- Always READY

---

**Last Updated:** January 27, 2026  
**Owner:** Coexistence Solution Team  
**Status:** ENHANCED
