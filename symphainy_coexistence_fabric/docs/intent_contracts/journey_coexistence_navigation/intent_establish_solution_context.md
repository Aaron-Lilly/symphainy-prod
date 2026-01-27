# Intent Contract: establish_solution_context

**Intent:** establish_solution_context  
**Intent Type:** `establish_solution_context`  
**Journey:** Solution Navigation (`journey_coexistence_navigation`)  
**Solution:** Coexistence Solution  
**Status:** ENHANCED  
**Priority:** PRIORITY 1

---

## 1. Intent Overview

### Purpose
Establishes or updates the solution context for a user's session. This includes setting user goals, selecting a solution structure, configuring pillar preferences, and initializing the journey state. Called after goal analysis or when user customizes their journey.

### Intent Flow
```
[User completes goal analysis or customization]
    ↓
[Validate solution structure and preferences]
    ↓
[Create/update session context in State Surface]
    ↓
[Initialize journey state for selected solution]
    ↓
[Return established context with first journey step]
```

### Expected Observable Artifacts
- `established_context` - Confirmed solution context with initial state

---

## 2. Intent Parameters

### Required Parameters

| Parameter | Type | Description | Validation |
|-----------|------|-------------|------------|
| `user_context` | `object` | User context with session_id | Must include session_id |
| `solution_structure` | `object` | Solution structure from goal analysis | Must have solution_id |

### Optional Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `user_goals` | `string` | User's stated goals | null |
| `pillar_preferences` | `array` | Enabled/disabled pillars | All enabled |
| `reasoning` | `object` | Agent reasoning from analysis | null |
| `customizations` | `object` | User customization choices | {} |

### Context Metadata (from ExecutionContext)

| Metadata Key | Type | Description | Source |
|--------------|------|-------------|--------|
| `tenant_id` | `string` | Tenant identifier | Runtime |
| `session_id` | `string` | Session identifier | Runtime |

---

## 3. Intent Returns

### Success Response

```json
{
  "artifacts": {
    "established_context": {
      "result_type": "solution_context_established",
      "semantic_payload": {
        "session_id": "sess_abc123",
        "solution_id": "content_solution",
        "context_version": 1
      },
      "renderings": {
        "solution": {
          "solution_id": "content_solution",
          "solution_name": "Content Solution",
          "strategic_focus": "data_processing"
        },
        "user_profile": {
          "user_name": "User",
          "user_goals": "Automate invoice processing workflow",
          "industry": null,
          "goals_analyzed": true
        },
        "pillar_configuration": [
          {
            "pillar_name": "content",
            "enabled": true,
            "navigation_order": 1,
            "focus_areas": ["file_upload", "parsing"]
          },
          {
            "pillar_name": "insights",
            "enabled": true,
            "navigation_order": 2,
            "focus_areas": ["data_quality"]
          },
          {
            "pillar_name": "journey",
            "enabled": false,
            "navigation_order": 3,
            "focus_areas": []
          },
          {
            "pillar_name": "outcomes",
            "enabled": true,
            "navigation_order": 4,
            "focus_areas": ["poc_generation"]
          }
        ],
        "initial_journey": {
          "journey_id": "file_upload_materialization",
          "journey_name": "File Upload & Materialization",
          "first_intent": "ingest_file"
        },
        "agent_guidance": {
          "initial_message": "Welcome! Based on your goal to automate invoice processing, I recommend starting by uploading some sample invoices.",
          "recommended_file_types": ["pdf", "xlsx", "csv"],
          "confidence": 0.85
        },
        "navigation": {
          "start_route": "/pillars/content",
          "breadcrumbs": [
            { "label": "Home", "route": "/" },
            { "label": "Content", "route": "/pillars/content" }
          ]
        }
      }
    }
  },
  "events": [
    {
      "type": "solution_context_established",
      "solution_id": "content_solution",
      "pillars_enabled": ["content", "insights", "outcomes"],
      "has_customizations": true
    }
  ]
}
```

---

## 4. Artifact Registration

### State Surface Registration
- **Artifact ID:** `ctx_est_{session_id}_{solution_id}`
- **Artifact Type:** `"solution_context_established"`
- **Lifecycle State:** `"READY"`
- **Produced By:** `{ intent: "establish_solution_context", execution_id: "<execution_id>" }`
- **Materializations:** Persisted in session state

### Artifact Index Registration
- Indexed: session_id, solution_id, tenant_id, timestamp

---

## 5. Idempotency

### Idempotency Key
```
idempotency_key = hash(session_id + solution_id + hash(solution_structure) + "establish_solution_context")
```

### Scope
- Per session + solution structure

### Behavior
- Same structure returns same context
- Updated structure increments context_version

---

## 6. Implementation Details

### Handler Location
`symphainy_platform/solutions/coexistence/journeys/navigation_journey.py`

### Key Implementation Steps
1. Validate solution_structure has valid solution_id
2. Apply pillar_preferences to solution configuration
3. Store user_goals and reasoning in session state
4. Initialize journey state for first enabled pillar
5. Generate agent guidance message
6. Persist context to State Surface
7. Return established context with navigation info

### Dependencies
- **Public Works:** registry_abstraction (Solution Registry)
- **State Surface:** session state persistence
- **Runtime:** ExecutionContext

---

## 7. Frontend Integration

### Frontend Usage
```typescript
// After goal analysis completes (WelcomeJourney.tsx)
const sessionResult = await platformState.submitIntent({
  intent_type: "establish_solution_context",
  parameters: {
    user_context: { session_id },
    solution_structure: solutionStructure.solution_structure,
    user_goals: userGoals,
    pillar_preferences: customizedPillars,
    reasoning: solutionStructure.reasoning
  }
});

const ctx = sessionResult.artifacts?.established_context?.renderings;
// Navigate to first pillar
router.push(ctx.navigation.start_route);
// Set agent message
dispatch({
  type: "SET_CHAT_STATE",
  payload: { initialMessage: ctx.agent_guidance.initial_message }
});
```

### Expected Frontend Behavior
1. Call after goal analysis or customization
2. Receive established context
3. Navigate to start route
4. Display agent guidance message
5. Update pillar navigation based on configuration

---

## 8. Error Handling

### Validation Errors
- Invalid solution_structure → Return INVALID_STRUCTURE error
- Unknown solution_id → Return SOLUTION_NOT_FOUND

### Runtime Errors
- State Surface unavailable → Return error (cannot establish context)

---

## 9. Testing & Validation

### Happy Path
1. Complete goal analysis
2. Submit establish_solution_context with structure
3. Verify context persisted
4. Verify navigation info correct
5. Verify agent guidance generated

### Boundary Violations
- No pillars enabled → Return error requiring at least one
- Invalid pillar names → Ignore invalid, use valid ones

---

## 10. Contract Compliance

### Required Artifacts
- `established_context` - Required (solution_context_established type)

### Required Events
- `solution_context_established` - Required

### Lifecycle State
- Always READY (establishes new state)

---

**Last Updated:** January 27, 2026  
**Owner:** Coexistence Solution Team  
**Status:** ENHANCED
