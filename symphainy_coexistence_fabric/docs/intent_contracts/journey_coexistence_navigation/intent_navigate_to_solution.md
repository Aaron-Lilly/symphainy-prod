# Intent Contract: navigate_to_solution

**Intent:** navigate_to_solution  
**Intent Type:** `navigate_to_solution`  
**Journey:** Solution Navigation (`journey_coexistence_navigation`)  
**Solution:** Coexistence Solution  
**Status:** ENHANCED  
**Priority:** PRIORITY 1

---

## 1. Intent Overview

### Purpose
Handles user navigation to a specific solution or pillar within the platform. This intent validates the navigation target, prepares the solution context, and returns navigation metadata including the appropriate route and any required pre-conditions.

### Intent Flow
```
[User requests navigation to solution]
    ↓
[Validate solution_id exists and is accessible]
    ↓
[Check user permissions for solution]
    ↓
[Prepare navigation context and initial state]
    ↓
[Return navigation artifact with route and context]
```

### Expected Observable Artifacts
- `navigation` - Navigation metadata including route and pre-conditions

---

## 2. Intent Parameters

### Required Parameters

| Parameter | Type | Description | Validation |
|-----------|------|-------------|------------|
| `solution_id` | `string` | Target solution identifier | Must exist in registry |
| `user_context` | `object` | User context information | Must include session_id |

### Optional Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `pillar_name` | `string` | Specific pillar within solution | null (landing) |
| `preserve_context` | `boolean` | Preserve current solution context | true |
| `navigation_source` | `string` | Where navigation originated | "user_action" |

### Context Metadata (from ExecutionContext)

| Metadata Key | Type | Description | Source |
|--------------|------|-------------|--------|
| `tenant_id` | `string` | Tenant identifier | Runtime |
| `session_id` | `string` | Session identifier | Runtime |
| `current_solution_id` | `string` | Current solution (if any) | Session state |

---

## 3. Intent Returns

### Success Response

```json
{
  "artifacts": {
    "navigation": {
      "result_type": "navigation_result",
      "semantic_payload": {
        "target_solution": "content_solution",
        "navigation_type": "solution_switch",
        "requires_context_transfer": true
      },
      "renderings": {
        "route": "/pillars/content",
        "solution_id": "content_solution",
        "solution_name": "Content Solution",
        "pillar_name": "content",
        "navigation_metadata": {
          "from_solution": "coexistence",
          "to_solution": "content_solution",
          "context_preserved": true
        },
        "pre_conditions": [],
        "initial_state": {
          "welcome_message": "Welcome to Content Solution! Upload a file to begin.",
          "suggested_actions": ["upload_file", "view_artifacts"]
        },
        "breadcrumbs": [
          { "label": "Home", "route": "/" },
          { "label": "Content", "route": "/pillars/content" }
        ]
      }
    }
  },
  "events": [
    {
      "type": "navigation_initiated",
      "from_solution": "coexistence",
      "to_solution": "content_solution",
      "pillar_name": "content"
    }
  ]
}
```

### Error Response

```json
{
  "error": "Solution not found",
  "error_code": "SOLUTION_NOT_FOUND",
  "execution_id": "exec_abc123",
  "solution_id": "invalid_solution"
}
```

---

## 4. Artifact Registration

### State Surface Registration
- **Artifact ID:** `nav_{session_id}_{solution_id}_{timestamp}`
- **Artifact Type:** `"navigation_result"`
- **Lifecycle State:** `"READY"`
- **Produced By:** `{ intent: "navigate_to_solution", execution_id: "<execution_id>" }`
- **Materializations:** Logged for analytics

### Artifact Index Registration
- Indexed for analytics: session_id, from_solution, to_solution, timestamp

---

## 5. Idempotency

### Idempotency Key
```
idempotency_key = hash(session_id + solution_id + pillar_name + "navigate_to_solution")
```

### Scope
- Per session + target

### Behavior
- Same navigation request returns same route (deterministic)
- Context is re-prepared each time

---

## 6. Implementation Details

### Handler Location
`symphainy_platform/solutions/coexistence/journeys/navigation_journey.py`

### Key Implementation Steps
1. Validate solution_id exists in Solution Registry
2. Check user has permission to access solution
3. Determine route based on solution_id and pillar_name
4. Prepare initial state for target solution
5. Log navigation event for analytics
6. Return navigation artifact

### Dependencies
- **Public Works:** registry_abstraction (Solution Registry)
- **State Surface:** session state for context transfer
- **Runtime:** ExecutionContext, Security validation

---

## 7. Frontend Integration

### Frontend Usage
```typescript
// From WelcomeJourney.tsx - handleStartCustomizedJourney
const navResult = await platformState.submitIntent({
  intent_type: "navigate_to_solution",
  parameters: {
    solution_id: "content_solution",
    pillar_name: "content",
    user_context: { session_id }
  }
});

const nav = navResult.artifacts?.navigation?.renderings;
router.push(nav.route);
dispatch({ 
  type: "SET_CHAT_STATE", 
  payload: { initialMessage: nav.initial_state.welcome_message }
});
```

### Expected Frontend Behavior
1. Submit navigation intent
2. Receive route and context
3. Update breadcrumbs
4. Navigate to new route
5. Set initial chat message

---

## 8. Error Handling

### Validation Errors
- Unknown solution_id → Return SOLUTION_NOT_FOUND
- Permission denied → Return ACCESS_DENIED

### Runtime Errors
- Registry unavailable → Return cached routes

### Error Response Format
```json
{
  "error": "You don't have access to this solution",
  "error_code": "ACCESS_DENIED",
  "execution_id": "exec_abc123",
  "intent_type": "navigate_to_solution"
}
```

---

## 9. Testing & Validation

### Happy Path
1. Request navigation to valid solution
2. Verify route is correct
3. Verify context is prepared
4. Verify analytics event logged

### Boundary Violations
- Invalid solution_id → Return error
- No permission → Return access denied

### Failure Scenarios
- Registry down → Use fallback routes

---

## 10. Contract Compliance

### Required Artifacts
- `navigation` - Required (navigation_result type)

### Required Events
- `navigation_initiated` - Required

### Lifecycle State
- Always READY

---

**Last Updated:** January 27, 2026  
**Owner:** Coexistence Solution Team  
**Status:** ENHANCED
