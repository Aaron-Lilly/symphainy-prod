# Intent Contract: create_solution

**Intent:** create_solution  
**Intent Type:** `create_solution`  
**Journey:** Solution Creation (`journey_solution_creation`)  
**Realm:** Solution Realm (Implementation: Outcomes Realm)  
**Status:** ✅ **IMPLEMENTED**  
**Priority:** 🔴 **PRIORITY 1**

---

## 1. Intent Overview

### Purpose
Create a platform solution from an existing artifact (roadmap, POC, or blueprint). The platform solution is registered with domain bindings and intents, enabling it to be deployed and executed within the Symphainy platform.

### Intent Flow
```
[Frontend: OutcomesAPIManager.createSolution(source, sourceId, sourceData)]
    ↓
[submitIntent("create_solution", { solution_source, source_id, source_data })]
    ↓
[Runtime: ExecutionLifecycleManager.execute()]
    ↓
[OutcomesOrchestrator._handle_create_solution()]
    ↓
[Validate solution_source and source_id]
    ↓
[Retrieve source artifact from Artifact Plane]
    ↓
[Fallback: Try execution state if Artifact Plane fails]
    ↓
[SolutionSynthesisService.create_solution_from_artifact()]
    ↓
[Generate solution_id and register solution]
    ↓
[Return solution with domain bindings]
```

### Expected Observable Artifacts
- `platform_solution` - Registered platform solution
  - `solution_id`: Unique identifier
  - `name`: Solution name
  - `description`: Solution description
  - `domain_bindings`: Array of domain/system/adapter mappings
  - `intents`: Array of supported intents
  - `metadata`: Additional solution metadata

---

## 2. Intent Parameters

### Required Parameters

| Parameter | Type | Description | Validation |
|-----------|------|-------------|------------|
| `solution_source` | `string` | Source type: "roadmap", "poc", or "blueprint" | Enum validation |
| `source_id` | `string` | ID of source artifact | Required, non-empty |

### Optional Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `source_data` | `object` | Pre-loaded source artifact data | Retrieved from Artifact Plane |
| `solution_options` | `object` | Options for solution creation | `{}` |

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
    "solution": {
      "solution_id": "solution_abc123",
      "name": "Insurance Claims Modernization",
      "description": "Platform solution for claims processing modernization",
      "domain_bindings": [
        {
          "domain": "claims",
          "system_name": "claims_processing",
          "adapter_type": "rest"
        }
      ],
      "intents": [
        "process_claim",
        "validate_claim",
        "route_claim"
      ],
      "metadata": {
        "created_from": "roadmap",
        "source_id": "roadmap_xyz789"
      }
    },
    "solution_id": "solution_abc123"
  },
  "events": [
    {
      "type": "solution_created",
      "solution_id": "solution_abc123",
      "source": "roadmap",
      "source_id": "roadmap_xyz789",
      "session_id": "session_456"
    }
  ]
}
```

### Error Response

```json
{
  "error": "Source roadmap with id roadmap_xyz789 not found in Artifact Plane or execution state",
  "error_code": "SOURCE_NOT_FOUND",
  "execution_id": "exec_abc123"
}
```

---

## 4. Artifact Registration

### Solution Registry Registration
- **Solution ID:** Generated from service
- **Solution Type:** Based on source artifact
- **Status:** Registered
- **Domain Bindings:** Derived from source artifact analysis
- **Intents:** Generated from solution requirements

### No Artifact Plane Storage
- Solution registered in Solution Registry
- Not stored in Artifact Plane (registry is authoritative)

---

## 5. Idempotency

### Idempotency Key
```
idempotency_key = hash(solution_source + source_id + session_id)
```

### Scope
- Per source artifact per session
- Not idempotent - creates new solution each time

### Behavior
- Each invocation creates a new solution with new solution_id
- Previous solutions remain in registry
- Source artifact unchanged

---

## 6. Implementation Details

### Handler Location
`symphainy_platform/realms/outcomes/orchestrators/outcomes_orchestrator.py::_handle_create_solution`

### Key Implementation Steps
1. Validate solution_source ("roadmap", "poc", "blueprint")
2. Validate source_id (required)
3. Try Artifact Plane retrieval with `include_payload=True`
4. Extract relevant data based on source type:
   - roadmap: `payload.roadmap` or `payload.strategic_plan`
   - poc: `payload.poc_proposal` or `payload.proposal`
   - blueprint: `payload.blueprint`
5. Fallback to execution state if Artifact Plane fails
6. Call SolutionSynthesisService.create_solution_from_artifact()
7. Return solution with solution_id

### Artifact Retrieval Pattern
```python
# Primary: Artifact Plane
artifact_result = await self.artifact_plane.get_artifact(
    artifact_id=source_id,
    tenant_id=context.tenant_id,
    include_payload=True,
    include_visuals=False
)

# Fallback: Execution state
execution_state = await context.state_surface.get_execution_state(
    source_id,
    context.tenant_id
)
```

### Dependencies
- **Artifact Plane:** `get_artifact()` for source retrieval
- **State Surface:** `get_execution_state()` for fallback
- **Services:** `SolutionSynthesisService.create_solution_from_artifact()`
- **Solution Registry:** Solution registration

---

## 7. Frontend Integration

### Frontend Usage
```typescript
// OutcomesAPIManager.createSolution()
async createSolution(
  solutionSource: "roadmap" | "poc" | "blueprint",
  sourceId: string,
  sourceData: any,
  solutionOptions?: Record<string, any>
): Promise<SolutionCreationResponse> {
  const platformState = this.getPlatformState();
  
  // Session validation
  validateSession(platformState, "create solution");

  // Parameter validation
  if (!solutionSource || !sourceId || !sourceData) {
    throw new Error("solution_source, source_id, and source_data are required");
  }

  // Submit intent
  const execution = await platformState.submitIntent(
    "create_solution",
    {
      solution_source: solutionSource,
      source_id: sourceId,
      source_data: sourceData,
      solution_options: solutionOptions || {}
    }
  );

  // Wait for execution
  const result = await this._waitForExecution(execution, platformState);

  if (result.status === "completed" && result.artifacts?.platform_solution) {
    const solutionId = result.artifacts.platform_solution.solution_id;
    
    // Update realm state
    platformState.setRealmState("outcomes", "solutions", {
      ...platformState.getRealmState("outcomes", "solutions") || {},
      [solutionId]: result.artifacts.platform_solution
    });

    return { success: true, platform_solution: result.artifacts.platform_solution };
  }
  
  throw new Error(result.error || "Failed to create solution");
}
```

### Expected Frontend Behavior
1. User selects source type (roadmap, POC, or blueprint)
2. User selects existing artifact
3. Call `createSolution(source, sourceId, sourceData)` when user clicks "Create Solution"
4. Show loading state during creation
5. Display solution with domain bindings and intents
6. Store solution reference in realm state

---

## 8. Error Handling

### Validation Errors
- Missing solution_source → `"solution_source and source_id are required"`
- Invalid solution_source → `"Invalid solution_source: X. Must be 'roadmap', 'poc', or 'blueprint'"`
- No session → `"Session required to create solution"`

### Runtime Errors
- Source not found → `"Source {type} with id {id} not found in Artifact Plane or execution state"`
- Service failure → Error returned

### Error Response Format
```json
{
  "error": "Error message",
  "error_code": "ERROR_CODE",
  "execution_id": "exec_abc123",
  "intent_type": "create_solution"
}
```

---

## 9. Testing & Validation

### Happy Path
1. User creates roadmap/POC/blueprint first
2. User selects source artifact
3. User clicks "Create Solution"
4. Solution created with domain bindings
5. solution_id returned and displayed

### Boundary Violations
- Invalid solution_source → Validation error
- Missing source_id → Validation error
- Source not found → Detailed error with lookup attempts

### Failure Scenarios
- Artifact Plane unavailable → Execution state fallback
- Both lookups fail → Clear error message
- Service failure → Error returned

---

## 10. Contract Compliance

### Required Artifacts
- `solution` - Required
- `solution_id` - Required

### Required Events
- `solution_created` - Required (includes source, source_id)

### Retrieval Pattern
- Primary: Artifact Plane with `include_payload=True`
- Fallback: Execution state
- Clear error if both fail

### Cross-Reference Analysis

| Source | Expectation | Implementation | Notes |
|--------|-------------|----------------|-------|
| **Journey Contract** | Create solution from artifact | ✅ Implemented | Via service |
| **Solution Contract** | Register in Solution Registry | ✅ Implemented | Via service |
| **Frontend** | Return solution_id | ✅ Implemented | Reference pattern |

---

**Last Updated:** January 27, 2026  
**Owner:** Solution Realm Solution Team  
**Status:** ✅ **IMPLEMENTED**
