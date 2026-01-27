# Intent Contract: create_blueprint

**Intent:** create_blueprint  
**Intent Type:** `create_blueprint`  
**Journey:** Blueprint Creation (`journey_solution_blueprint_creation`)  
**Realm:** Solution Realm (Implementation: Outcomes Realm)  
**Status:** ✅ **IMPLEMENTED**  
**Priority:** 🔴 **PRIORITY 1**

---

## 1. Intent Overview

### Purpose
Create a coexistence blueprint from workflow analysis. The blueprint defines the transformation from current state to coexistence state, including a roadmap and responsibility matrix. The generated blueprint is stored in the Artifact Plane for retrieval and can be used as a source for platform solution creation.

### Intent Flow
```
[Frontend: OutcomesAPIManager.createBlueprint(workflowId)]
    ↓
[submitIntent("create_blueprint", { workflow_id, current_state_workflow_id })]
    ↓
[Runtime: ExecutionLifecycleManager.execute()]
    ↓
[OutcomesOrchestrator._handle_create_blueprint()]
    ↓
[Validate workflow_id (required)]
    ↓
[BlueprintCreationAgent.process_request()]
    ↓
[CoexistenceAnalysisService (via MCP tools)]
    ↓
[Generate blueprint_id (UUID)]
    ↓
[Store artifact in Artifact Plane]
    ↓
[Return structured artifact with blueprint_id]
```

### Expected Observable Artifacts
- `blueprint` artifact stored in Artifact Plane with:
  - `blueprint_id`: Unique identifier
  - `current_state`: Current state workflow analysis
  - `coexistence_state`: Target coexistence state definition
  - `roadmap`: Transformation roadmap
  - `responsibility_matrix`: RACI-style matrix
  - `sections`: Blueprint sections array

---

## 2. Intent Parameters

### Required Parameters

| Parameter | Type | Description | Validation |
|-----------|------|-------------|------------|
| `workflow_id` | `string` | Workflow ID to transform | Required, non-empty |

### Optional Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `current_state_workflow_id` | `string` | Current state workflow for comparison | `null` |

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
    "blueprint_id": "blueprint_workflow123_abc456",
    "blueprint": {
      "result_type": "blueprint",
      "semantic_payload": {
        "blueprint_id": "blueprint_workflow123_abc456",
        "execution_id": "exec_xyz789",
        "session_id": "session_456"
      },
      "renderings": {}
    }
  },
  "events": [
    {
      "type": "blueprint_created",
      "blueprint_id": "blueprint_workflow123_abc456",
      "session_id": "session_456"
    }
  ]
}
```

### Full Artifact (in Artifact Plane)

```json
{
  "blueprint": {
    "blueprint_id": "blueprint_workflow123_abc456",
    "current_state": {
      "workflow_name": "Claims Processing",
      "steps": ["..."],
      "systems": ["Legacy CRM", "Manual spreadsheets"],
      "pain_points": ["Slow processing", "Error prone"]
    },
    "coexistence_state": {
      "workflow_name": "Claims Processing (Coexistence)",
      "steps": ["..."],
      "systems": ["Legacy CRM", "AI Processing Engine", "Data Lake"],
      "improvements": ["Automated validation", "Real-time updates"]
    },
    "roadmap": {
      "phases": [
        {
          "phase": "Foundation",
          "activities": ["Set up Data Lake", "Deploy AI Engine"],
          "duration_weeks": 4
        },
        {
          "phase": "Integration",
          "activities": ["Connect to Legacy CRM", "Build pipelines"],
          "duration_weeks": 6
        }
      ]
    },
    "responsibility_matrix": {
      "roles": ["IT Team", "Business", "Vendor"],
      "tasks": [
        {
          "task": "Data migration",
          "responsible": "IT Team",
          "accountable": "Business",
          "consulted": "Vendor",
          "informed": "All"
        }
      ]
    },
    "sections": [
      {
        "title": "Executive Summary",
        "content": "..."
      },
      {
        "title": "Technical Architecture",
        "content": "..."
      }
    ]
  }
}
```

### Error Response

```json
{
  "error": "workflow_id is required for create_blueprint intent",
  "error_code": "VALIDATION_ERROR",
  "execution_id": "exec_abc123"
}
```

---

## 4. Artifact Registration

### Artifact Plane Registration
- **Artifact ID:** Generated (`blueprint_{workflow_id}_{uuid}`)
- **Artifact Type:** `"blueprint"`
- **Lifecycle State:** `"READY"`
- **Produced By:** `{ intent: "create_blueprint", execution_id: "<execution_id>" }`
- **Metadata:** `{ regenerable: true, retention_policy: "session" }`
- **Payload:** Full blueprint with sections

### Fallback (if Artifact Plane unavailable)
- Stored in execution state (logged as warning)
- Returns full artifact in response (not just reference)

---

## 5. Idempotency

### Idempotency Key
```
idempotency_key = hash(workflow_id + current_state_workflow_id + session_id)
```

### Scope
- Per workflow input per session
- Not idempotent - generates new blueprint each time

### Behavior
- Each invocation generates a new blueprint with new blueprint_id
- Previous blueprints remain in Artifact Plane
- Useful for iterating on workflow transformation

---

## 6. Implementation Details

### Handler Location
`symphainy_platform/realms/outcomes/orchestrators/outcomes_orchestrator.py::_handle_create_blueprint`

### Key Implementation Steps
1. Validate workflow_id (required)
2. Check BlueprintCreationAgent availability
3. If agent not available → Raise NotImplementedError
4. Call BlueprintCreationAgent.process_request()
5. Agent uses CoexistenceAnalysisService as MCP tool
6. Generate blueprint_id (UUID)
7. Store artifact in Artifact Plane
8. Return artifact reference (not full artifact)

### Agent Requirement
**BlueprintCreationAgent is required** - no service fallback available.
If agent is not implemented, intent raises `NotImplementedError`.

### Dependencies
- **Public Works:** None directly
- **Artifact Plane:** `create_artifact()` for storage
- **Runtime:** `ExecutionContext`
- **Agents:** `BlueprintCreationAgent` (required)
- **Services:** `CoexistenceAnalysisService` (used as MCP tool by agent)

---

## 7. Frontend Integration

### Frontend Usage
```typescript
// OutcomesAPIManager.createBlueprint()
async createBlueprint(
  workflowId: string,
  currentStateWorkflowId?: string
): Promise<{ success: boolean; blueprint?: any; blueprint_id?: string; error?: string }> {
  const platformState = this.getPlatformState();
  
  // Session validation
  validateSession(platformState, "create blueprint");

  // Parameter validation
  if (!workflowId) {
    throw new Error("workflow_id is required for blueprint creation");
  }

  // Submit intent
  const execution = await platformState.submitIntent(
    "create_blueprint",
    {
      workflow_id: workflowId,
      current_state_workflow_id: currentStateWorkflowId
    }
  );

  // Wait for execution
  const result = await this._waitForExecution(execution, platformState);

  if (result.status === "completed" && result.artifacts?.blueprint) {
    const blueprintId = result.artifacts.blueprint.blueprint_id || result.artifacts.blueprint_id;
    
    // Ensure lifecycle state
    const blueprintWithLifecycle = ensureArtifactLifecycle(
      result.artifacts.blueprint,
      'coexistence_planning',
      'workflow_optimization',
      platformState.state.session.userId || 'system'
    );
    
    // Update realm state
    platformState.setRealmState("outcomes", "blueprints", {
      ...platformState.getRealmState("outcomes", "blueprints") || {},
      [blueprintId]: blueprintWithLifecycle
    });

    return { success: true, blueprint: blueprintWithLifecycle, blueprint_id: blueprintId };
  }
  
  throw new Error(result.error || "Failed to create blueprint");
}
```

### Expected Frontend Behavior
1. User selects workflow to transform
2. Optionally provides current state workflow for comparison
3. Call `createBlueprint(workflowId)` when user clicks "Create Blueprint"
4. Show loading state during generation
5. Display blueprint with current state, coexistence state, roadmap
6. Store blueprint reference in realm state
7. Enable "Create Solution" flow with blueprint as source

---

## 8. Error Handling

### Validation Errors
- Missing workflow_id → `"workflow_id is required for create_blueprint intent"`
- No session → `"Session required to create blueprint"`

### Runtime Errors
- Agent not available → `NotImplementedError: "BlueprintCreationAgent not available"`
- Agent failure → Error returned
- Artifact Plane failure → Fallback to execution state (warning logged)

### Error Response Format
```json
{
  "error": "Error message",
  "error_code": "ERROR_CODE",
  "execution_id": "exec_abc123",
  "intent_type": "create_blueprint"
}
```

---

## 9. Testing & Validation

### Happy Path
1. User selects workflow
2. User clicks "Create Blueprint"
3. Blueprint generated with transformation analysis
4. Artifact stored in Artifact Plane
5. blueprint_id returned and displayed

### Boundary Violations
- Missing workflow_id → Validation error
- No session → Session validation error

### Failure Scenarios
- Agent not available → NotImplementedError
- Agent failure → Error returned
- Artifact Plane failure → Execution state fallback (warning)

---

## 10. Contract Compliance

### Required Artifacts
- `blueprint` reference - Required
- `blueprint_id` - Required

### Required Events
- `blueprint_created` - Required

### Lifecycle State
- Artifact created with `READY` state
- Stored in Artifact Plane (not execution state)
- Retrievable via `blueprint_id`

### Agent Pattern
- Uses agentic forward pattern
- Agent uses MCP tools for service access
- No service fallback (agent required)

### Cross-Reference Analysis

| Source | Expectation | Implementation | Notes |
|--------|-------------|----------------|-------|
| **Journey Contract** | Create blueprint from workflow | ✅ Implemented | Via agent |
| **Solution Contract** | Store in Artifact Plane | ✅ Implemented | With fallback |
| **Frontend** | Return blueprint_id for retrieval | ✅ Implemented | Reference pattern |

---

**Last Updated:** January 27, 2026  
**Owner:** Solution Realm Solution Team  
**Status:** ✅ **IMPLEMENTED** (requires BlueprintCreationAgent)
