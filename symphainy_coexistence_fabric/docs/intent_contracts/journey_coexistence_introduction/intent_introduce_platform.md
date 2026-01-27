# Intent Contract: introduce_platform

**Intent:** introduce_platform  
**Intent Type:** `introduce_platform`  
**Journey:** Platform Introduction (`journey_coexistence_introduction`)  
**Solution:** Coexistence Solution  
**Status:** ENHANCED  
**Priority:** PRIORITY 1

---

## 1. Intent Overview

### Purpose
Introduces new users to the Symphainy platform, explaining its core value proposition: enabling boundary-crossing work coordination through the Coexistence Fabric. This intent provides a personalized welcome message and sets the context for the user's journey.

### Intent Flow
```
[User lands on platform or requests introduction]
    ↓
[Validate session and user context]
    ↓
[Generate personalized welcome message]
    ↓
[Create introduction artifact with platform overview]
    ↓
[Return welcome content and next steps]
```

### Expected Observable Artifacts
- `introduction_artifact` - Platform introduction content tailored to user context

---

## 2. Intent Parameters

### Required Parameters

| Parameter | Type | Description | Validation |
|-----------|------|-------------|------------|
| `user_context` | `object` | User context information | Must include session_id |

### Optional Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `user_name` | `string` | User's name for personalization | "User" |
| `user_goals` | `string` | Initial goals if provided | null |
| `referral_source` | `string` | How user found the platform | "direct" |
| `language` | `string` | Preferred language | "en" |

### Context Metadata (from ExecutionContext)

| Metadata Key | Type | Description | Source |
|--------------|------|-------------|--------|
| `tenant_id` | `string` | Tenant identifier | Runtime |
| `session_id` | `string` | Session identifier | Runtime |
| `execution_id` | `string` | Execution trace ID | Runtime |

---

## 3. Intent Returns

### Success Response

```json
{
  "artifacts": {
    "introduction": {
      "result_type": "platform_introduction",
      "semantic_payload": {
        "welcome_type": "new_user",
        "personalization_level": "basic",
        "user_name": "User"
      },
      "renderings": {
        "welcome_message": "Welcome to Symphainy! Let's build your coexistence future together.",
        "platform_tagline": "Coordinate boundary-crossing work across systems",
        "value_propositions": [
          "Enable legacy and modern systems to work together",
          "AI-powered guidance through your transformation journey",
          "Governed, secure coordination of cross-boundary workflows"
        ],
        "next_steps": [
          "Explore the solution catalog",
          "Tell us about your goals",
          "Start your guided journey"
        ],
        "key_concepts": {
          "coexistence": "Systems working together without replacement",
          "boundary_crossing": "Workflows spanning multiple systems and teams",
          "guided_journey": "AI-assisted path through platform capabilities"
        }
      }
    }
  },
  "events": [
    {
      "type": "platform_introduction_presented",
      "user_name": "User",
      "personalization_level": "basic"
    }
  ]
}
```

### Error Response

```json
{
  "error": "Failed to generate introduction",
  "error_code": "INTRODUCTION_FAILED",
  "execution_id": "exec_abc123"
}
```

---

## 4. Artifact Registration

### State Surface Registration
- **Artifact ID:** `intro_{session_id}_{timestamp}`
- **Artifact Type:** `"platform_introduction"`
- **Lifecycle State:** `"READY"` (ephemeral, no PENDING state)
- **Produced By:** `{ intent: "introduce_platform", execution_id: "<execution_id>" }`
- **Semantic Descriptor:** Platform introduction content
- **Parent Artifacts:** None (root artifact)
- **Materializations:** In-memory only (ephemeral)

### Artifact Index Registration
- Not indexed (ephemeral artifact)
- Session-scoped only

---

## 5. Idempotency

### Idempotency Key
```
idempotency_key = hash(session_id + user_name + "introduce_platform")
```

### Scope
- Per session (same session returns same introduction)

### Behavior
- Returns cached introduction for same session
- New session generates fresh introduction

---

## 6. Implementation Details

### Handler Location
`symphainy_platform/solutions/coexistence/journeys/introduction_journey.py`

### Key Implementation Steps
1. Extract user context from parameters
2. Generate personalized welcome message based on user_name and user_goals
3. Compile platform value propositions
4. Create structured introduction artifact
5. Log analytics event for introduction presented

### Dependencies
- **Public Works:** telemetry_abstraction (for analytics)
- **State Surface:** Optional (ephemeral artifacts)
- **Runtime:** ExecutionContext for session info

---

## 7. Frontend Integration

### Frontend Usage
```typescript
// From WelcomeJourney.tsx
const result = await platformState.submitIntent({
  intent_type: "introduce_platform",
  parameters: {
    user_context: { session_id },
    user_name: user?.name || "User",
    user_goals: userGoals || null
  }
});

// Display welcome content
const intro = result.artifacts?.introduction?.renderings;
setWelcomeMessage(intro.welcome_message);
setValueProps(intro.value_propositions);
```

### Expected Frontend Behavior
1. Display welcome message prominently
2. Show value propositions as feature cards
3. Present next steps as actionable buttons
4. Enable transition to goal analysis or solution catalog

---

## 8. Error Handling

### Validation Errors
- Missing session_id → Return "Session required" error

### Runtime Errors
- Context generation failure → Return default generic introduction

### Error Response Format
```json
{
  "error": "Session required for platform introduction",
  "error_code": "SESSION_REQUIRED",
  "execution_id": "exec_abc123",
  "intent_type": "introduce_platform"
}
```

---

## 9. Testing & Validation

### Happy Path
1. User lands on platform with valid session
2. Submit introduce_platform intent
3. Receive personalized welcome content
4. Verify all value propositions present

### Boundary Violations
- No session → Return error requiring session
- Invalid user_context → Return generic introduction

### Failure Scenarios
- Backend unavailable → Return cached/default introduction

---

## 10. Contract Compliance

### Required Artifacts
- `introduction` - Required (platform_introduction type)

### Required Events
- `platform_introduction_presented` - Required

### Lifecycle State
- Always READY (ephemeral artifact, no pending state)

---

**Last Updated:** January 27, 2026  
**Owner:** Coexistence Solution Team  
**Status:** ENHANCED
