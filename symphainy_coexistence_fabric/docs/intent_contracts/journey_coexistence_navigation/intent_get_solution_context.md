# Intent Contract: get_solution_context

**Intent:** get_solution_context  
**Intent Type:** `get_solution_context`  
**Journey:** Solution Navigation (`journey_coexistence_navigation`)  
**Solution:** Coexistence Solution  
**Status:** ENHANCED  
**Priority:** PRIORITY 1

---

## 1. Intent Overview

### Purpose
Retrieves the current solution context for the user's session. This includes the active solution, user goals, progress state, available journeys, and any artifacts created so far. Used to restore state after refresh or to display context-aware UI elements.

### Intent Flow
```
[User/frontend requests solution context]
    ↓
[Fetch session state from State Surface]
    ↓
[Compile context from session and solution data]
    ↓
[Include user goals, progress, and artifacts]
    ↓
[Return comprehensive context artifact]
```

### Expected Observable Artifacts
- `solution_context` - Current solution context with progress and artifacts

---

## 2. Intent Parameters

### Required Parameters

| Parameter | Type | Description | Validation |
|-----------|------|-------------|------------|
| `user_context` | `object` | User context information | Must include session_id |

### Optional Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `include_artifacts` | `boolean` | Include artifact summaries | true |
| `include_progress` | `boolean` | Include journey progress | true |
| `solution_id` | `string` | Specific solution (or current) | null (current) |

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
    "context": {
      "result_type": "solution_context",
      "semantic_payload": {
        "session_id": "sess_abc123",
        "has_active_solution": true,
        "artifact_count": 3
      },
      "renderings": {
        "current_solution": {
          "solution_id": "content_solution",
          "solution_name": "Content Solution",
          "pillar_name": "content",
          "started_at": "2026-01-27T10:00:00Z"
        },
        "user_context": {
          "user_name": "User",
          "user_goals": "Automate invoice processing workflow",
          "industry": "financial_services",
          "goals_analyzed": true
        },
        "journey_progress": {
          "current_journey": "file_upload_materialization",
          "journey_step": 2,
          "total_steps": 3,
          "completed_journeys": ["platform_introduction"],
          "pending_journeys": ["file_parsing", "deterministic_embedding"]
        },
        "artifacts_summary": [
          {
            "artifact_id": "art_001",
            "artifact_type": "uploaded_file",
            "name": "invoices.pdf",
            "lifecycle_state": "READY",
            "created_at": "2026-01-27T10:05:00Z"
          },
          {
            "artifact_id": "art_002",
            "artifact_type": "materialization",
            "name": "invoices.pdf materialization",
            "lifecycle_state": "READY",
            "created_at": "2026-01-27T10:05:30Z"
          }
        ],
        "available_actions": [
          { "action": "continue_journey", "label": "Continue Journey" },
          { "action": "view_artifacts", "label": "View Artifacts" },
          { "action": "change_solution", "label": "Change Solution" }
        ],
        "session_metadata": {
          "session_start": "2026-01-27T09:55:00Z",
          "last_activity": "2026-01-27T10:10:00Z",
          "session_duration_minutes": 15
        }
      }
    }
  },
  "events": [
    {
      "type": "solution_context_retrieved",
      "solution_id": "content_solution",
      "artifact_count": 2
    }
  ]
}
```

### Error Response (No Active Context)

```json
{
  "artifacts": {
    "context": {
      "result_type": "solution_context",
      "semantic_payload": {
        "session_id": "sess_abc123",
        "has_active_solution": false,
        "artifact_count": 0
      },
      "renderings": {
        "current_solution": null,
        "user_context": {
          "user_name": "User",
          "user_goals": null,
          "goals_analyzed": false
        },
        "journey_progress": null,
        "artifacts_summary": [],
        "available_actions": [
          { "action": "start_journey", "label": "Start Your Journey" },
          { "action": "view_catalog", "label": "Browse Solutions" }
        ]
      }
    }
  },
  "events": [
    {
      "type": "solution_context_retrieved",
      "solution_id": null,
      "artifact_count": 0
    }
  ]
}
```

---

## 4. Artifact Registration

### State Surface Registration
- **Artifact ID:** `ctx_{session_id}_{timestamp}`
- **Artifact Type:** `"solution_context"`
- **Lifecycle State:** `"READY"`
- **Produced By:** `{ intent: "get_solution_context", execution_id: "<execution_id>" }`
- **Materializations:** Ephemeral (not persisted)

---

## 5. Idempotency

### Idempotency Key
```
idempotency_key = hash(session_id + solution_id + "get_solution_context")
```

### Scope
- Per session (returns current state)

### Behavior
- Always returns current state (not cached)
- Multiple calls within same second return same result

---

## 6. Implementation Details

### Handler Location
`symphainy_platform/solutions/coexistence/journeys/navigation_journey.py`

### Key Implementation Steps
1. Fetch session state from State Surface
2. Get current solution from session
3. Compile user context (goals, industry)
4. Calculate journey progress
5. Fetch artifact summaries if requested
6. Determine available actions based on state

### Dependencies
- **Public Works:** registry_abstraction
- **State Surface:** session state, artifact registry
- **Runtime:** ExecutionContext

---

## 7. Frontend Integration

### Frontend Usage
```typescript
// On app load or refresh
const contextResult = await platformState.submitIntent({
  intent_type: "get_solution_context",
  parameters: {
    user_context: { session_id },
    include_artifacts: true,
    include_progress: true
  }
});

const ctx = contextResult.artifacts?.context?.renderings;
if (ctx.current_solution) {
  // Restore UI state
  setCurrentSolution(ctx.current_solution);
  setProgress(ctx.journey_progress);
  setArtifacts(ctx.artifacts_summary);
} else {
  // Show welcome/start journey
  router.push("/");
}
```

### Expected Frontend Behavior
1. Call on app initialization
2. Restore solution state if exists
3. Update progress indicators
4. Show available actions

---

## 8. Error Handling

### Validation Errors
- Invalid session_id → Create new session context

### Runtime Errors
- State Surface unavailable → Return empty context

---

## 9. Testing & Validation

### Happy Path
1. User has active solution
2. Request context
3. Verify solution, progress, artifacts returned
4. Verify available actions correct

### Boundary Violations
- No active solution → Return empty context with start actions

---

## 10. Contract Compliance

### Required Artifacts
- `context` - Required (solution_context type)

### Required Events
- `solution_context_retrieved` - Required

### Lifecycle State
- Always READY

---

**Last Updated:** January 27, 2026  
**Owner:** Coexistence Solution Team  
**Status:** ENHANCED
