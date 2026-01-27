# Intent Contract: generate_roadmap

**Intent:** generate_roadmap  
**Intent Type:** `generate_roadmap`  
**Journey:** Roadmap Generation (`journey_solution_roadmap_generation`)  
**Realm:** Solution Realm (Implementation: Outcomes Realm)  
**Status:** ✅ **IMPLEMENTED**  
**Priority:** 🔴 **PRIORITY 1**

---

## 1. Intent Overview

### Purpose
Generate a strategic roadmap from user-provided goals. The roadmap includes phases, timeline, milestones, and optional visualization. The generated roadmap is stored in the Artifact Plane for retrieval and can be used as a source for platform solution creation.

### Intent Flow
```
[Frontend: OutcomesAPIManager.generateRoadmap(goals)]
    ↓
[submitIntent("generate_roadmap", { goals, roadmap_options })]
    ↓
[Runtime: ExecutionLifecycleManager.execute()]
    ↓
[OutcomesOrchestrator._handle_generate_roadmap()]
    ↓
[Validate goals array (non-empty)]
    ↓
[RoadmapGenerationAgent.process_request() OR RoadmapGenerationService.generate_roadmap()]
    ↓
[Generate roadmap_id (UUID)]
    ↓
[VisualGenerationService.generate_roadmap_visual() - optional]
    ↓
[Store artifact in Artifact Plane]
    ↓
[Return structured artifact with roadmap_id]
```

### Expected Observable Artifacts
- `roadmap` artifact stored in Artifact Plane with:
  - `roadmap_id`: Unique identifier
  - `goals`: User-provided goals array
  - `status`: Generation status
  - `plan`: Array of phases with descriptions
  - `strategic_plan`: Detailed strategic plan
  - `metrics`: { estimated_duration_weeks, estimated_cost_usd }
  - `roadmap_visual`: Optional { image_base64, storage_path }

---

## 2. Intent Parameters

### Required Parameters

| Parameter | Type | Description | Validation |
|-----------|------|-------------|------------|
| `goals` | `string[]` | Array of business goals | Non-empty array |

### Optional Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `roadmap_options` | `object` | Options for roadmap generation | `{}` |
| `roadmap_type` | `string` | Type: "strategic", "tactical", "execution" | `"strategic"` |

### Context Metadata (from ExecutionContext)

| Metadata Key | Type | Description | Source |
|--------------|------|-------------|--------|
| `session_id` | `string` | Session identifier | Runtime (required) |
| `tenant_id` | `string` | Tenant identifier | Runtime (required) |
| `execution_id` | `string` | Execution identifier | Runtime |

---

## 3. Intent Returns

### Success Response

```json
{
  "artifacts": {
    "roadmap_id": "roadmap_abc123",
    "roadmap": {
      "result_type": "roadmap",
      "semantic_payload": {
        "roadmap_id": "roadmap_abc123",
        "execution_id": "exec_xyz789",
        "session_id": "session_456"
      },
      "renderings": {}
    }
  },
  "events": [
    {
      "type": "roadmap_generated",
      "roadmap_id": "roadmap_abc123",
      "session_id": "session_456"
    }
  ]
}
```

### Full Artifact (in Artifact Plane)

```json
{
  "roadmap": {
    "roadmap_id": "roadmap_abc123",
    "goals": ["Modernize legacy system", "Improve efficiency"],
    "status": "completed",
    "plan": [
      {
        "phase": "Discovery",
        "description": "Assess current state and define requirements",
        "duration_weeks": 4
      },
      {
        "phase": "Design",
        "description": "Design target architecture",
        "duration_weeks": 6
      },
      {
        "phase": "Implementation",
        "description": "Build and deploy solution",
        "duration_weeks": 12
      }
    ],
    "metrics": {
      "estimated_duration_weeks": 22,
      "estimated_cost_usd": 150000
    }
  },
  "strategic_plan": {
    "executive_summary": "...",
    "key_milestones": ["..."],
    "risk_assessment": ["..."]
  },
  "roadmap_visual": {
    "image_base64": "...",
    "storage_path": "gs://bucket/path/roadmap.png"
  }
}
```

### Error Response

```json
{
  "error": "Goals are required for roadmap generation",
  "error_code": "VALIDATION_ERROR",
  "execution_id": "exec_abc123"
}
```

---

## 4. Artifact Registration

### Artifact Plane Registration
- **Artifact ID:** Generated UUID (`roadmap_{uuid}`)
- **Artifact Type:** `"roadmap"`
- **Lifecycle State:** `"READY"`
- **Produced By:** `{ intent: "generate_roadmap", execution_id: "<execution_id>" }`
- **Metadata:** `{ regenerable: true, retention_policy: "session" }`
- **Payload:** Full roadmap data with strategic plan and visual

### Fallback (if Artifact Plane unavailable)
- Stored in execution state (logged as warning)
- Returns full artifact in response (not just reference)

---

## 5. Idempotency

### Idempotency Key
```
idempotency_key = hash(goals + session_id)
```

### Scope
- Per goals input per session
- Not idempotent - generates new roadmap each time

### Behavior
- Each invocation generates a new roadmap with new roadmap_id
- Previous roadmaps remain in Artifact Plane
- Useful for iterating on goals

---

## 6. Implementation Details

### Handler Location
`symphainy_platform/realms/outcomes/orchestrators/outcomes_orchestrator.py::_handle_generate_roadmap`

### Key Implementation Steps
1. Validate goals array (non-empty)
2. Try RoadmapGenerationAgent (if available)
3. Fallback to RoadmapGenerationService if agent unavailable
4. Generate roadmap_id (UUID)
5. Call VisualGenerationService.generate_roadmap_visual() (optional)
6. Store artifact in Artifact Plane
7. Return artifact reference (not full artifact)

### Dependencies
- **Public Works:** None directly
- **Artifact Plane:** `create_artifact()` for storage
- **Runtime:** `ExecutionContext`
- **Agents:** `RoadmapGenerationAgent` (optional)
- **Services:** `RoadmapGenerationService`, `VisualGenerationService`

---

## 7. Frontend Integration

### Frontend Usage
```typescript
// OutcomesAPIManager.generateRoadmap()
async generateRoadmap(
  goals: string[],
  roadmapOptions?: Record<string, any>
): Promise<RoadmapGenerationResponse> {
  const platformState = this.getPlatformState();
  
  // Session validation
  if (!platformState.state.session.sessionId || !platformState.state.session.tenantId) {
    throw new Error("Session required to generate roadmap");
  }

  // Parameter validation
  if (!goals || goals.length === 0) {
    throw new Error("goals array is required for generate_roadmap");
  }

  // Submit intent
  const execution = await platformState.submitIntent(
    "generate_roadmap",
    {
      goals,
      roadmap_options: roadmapOptions || {}
    }
  );

  // Wait for execution
  const result = await this._waitForExecution(execution, platformState);

  if (result.status === "completed" && result.artifacts?.roadmap) {
    const roadmapId = result.artifacts.roadmap.roadmap_id;
    
    // Ensure lifecycle state
    const roadmapWithLifecycle = ensureArtifactLifecycle(
      result.artifacts.roadmap,
      'strategic_planning',
      'business_transformation',
      platformState.state.session.userId || 'system'
    );
    
    // Update realm state
    platformState.setRealmState("outcomes", "roadmaps", {
      ...platformState.getRealmState("outcomes", "roadmaps") || {},
      [roadmapId]: roadmapWithLifecycle
    });

    return { success: true, roadmap: roadmapWithLifecycle };
  }
  
  throw new Error(result.error || "Failed to generate roadmap");
}
```

### Expected Frontend Behavior
1. Collect goals from user input
2. Call `generateRoadmap(goals)` when user clicks "Generate Roadmap"
3. Show loading state during generation
4. Display roadmap with phases and timeline
5. Store roadmap reference in realm state
6. Enable "Create Solution" flow with roadmap as source

---

## 8. Error Handling

### Validation Errors
- Empty goals → `"Goals are required for roadmap generation"`
- No session → `"Session required to generate roadmap"`

### Runtime Errors
- Agent failure → Fallback to service
- Service failure → Error returned
- Artifact Plane failure → Fallback to execution state (warning logged)
- Visual generation failure → Non-blocking (warning logged)

### Error Response Format
```json
{
  "error": "Error message",
  "error_code": "ERROR_CODE",
  "execution_id": "exec_abc123",
  "intent_type": "generate_roadmap"
}
```

---

## 9. Testing & Validation

### Happy Path
1. User provides goals array (e.g., ["Modernize system", "Reduce costs"])
2. User clicks "Generate Roadmap"
3. Roadmap generated with phases and timeline
4. Artifact stored in Artifact Plane
5. roadmap_id returned and displayed

### Boundary Violations
- Empty goals → Validation error
- No session → Session validation error

### Failure Scenarios
- Agent unavailable → Service fallback (success)
- Service failure → Error returned
- Artifact Plane failure → Execution state fallback (warning)

---

## 10. Contract Compliance

### Required Artifacts
- `roadmap` reference - Required
- `roadmap_id` - Required

### Required Events
- `roadmap_generated` - Required

### Lifecycle State
- Artifact created with `READY` state
- Stored in Artifact Plane (not execution state)
- Retrievable via `roadmap_id`

### Cross-Reference Analysis

| Source | Expectation | Implementation | Notes |
|--------|-------------|----------------|-------|
| **Journey Contract** | Generate roadmap from goals | ✅ Implemented | Via agent/service |
| **Solution Contract** | Store in Artifact Plane | ✅ Implemented | With fallback |
| **Frontend** | Return roadmap_id for retrieval | ✅ Implemented | Reference pattern |

---

**Last Updated:** January 27, 2026  
**Owner:** Solution Realm Solution Team  
**Status:** ✅ **IMPLEMENTED**
