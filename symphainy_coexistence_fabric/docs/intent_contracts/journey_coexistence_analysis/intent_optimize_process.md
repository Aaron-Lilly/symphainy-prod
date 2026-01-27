# Intent Contract: optimize_process

**Intent:** optimize_process  
**Intent Type:** `optimize_process`  
**Journey:** Coexistence Analysis (`journey_coexistence_analysis`)  
**Realm:** Journey Realm  
**Status:** ✅ **COMPREHENSIVE**  
**Priority:** 🟡 **PRIORITY 2** - Workflow optimization

---

## 1. Intent Overview

### Purpose
Optimize a workflow for human+AI coexistence. Analyzes workflow tasks and recommends automation opportunities, human retention areas, and overall optimization potential.

### Intent Flow
```
[User selects workflow to optimize]
    ↓
[optimize_process intent]
    ↓
[WorkflowConversionService.optimize_workflow()]
    ↓
[Analyze tasks for AI suitability]
[Identify human-required tasks]
[Generate optimization recommendations]
    ↓
[Return optimization artifact]
```

### Expected Observable Artifacts
- `optimization` artifact with:
  - `workflow_id` - Source workflow identifier
  - `optimization_id` - Optimization result identifier
  - `status` - Optimization status
  - `recommendations` - Array of recommendations
  - `automation_potential` - Percentage of automatable tasks
  - `ai_suitable_tasks_count` - Tasks suitable for AI
  - `human_required_tasks_count` - Tasks requiring human judgment

---

## 2. Intent Parameters

### Required Parameters

| Parameter | Type | Description | Validation |
|-----------|------|-------------|------------|
| `workflow_id` | `string` | Workflow identifier to optimize | Required, non-empty |

### Optional Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `optimization_options` | `object` | Optimization configuration | `{}` |
| `optimization_goals` | `array` | Specific optimization goals | `[]` |

### Context Metadata (from ExecutionContext)

| Metadata Key | Type | Description | Source |
|--------------|------|-------------|--------|
| `tenant_id` | `string` | Tenant identifier | Runtime (required) |
| `session_id` | `string` | Session identifier | Runtime (required) |
| `workflow_{workflow_id}` | `object` | Workflow data in context metadata | From prior intent |

---

## 3. Intent Returns

### Success Response

```json
{
  "artifacts": {
    "optimization": {
      "result_type": "optimization",
      "semantic_payload": {
        "workflow_id": "workflow_abc123",
        "optimization_id": "opt_xyz789",
        "status": "completed"
      },
      "renderings": {
        "optimization": {
          "workflow_id": "workflow_abc123",
          "optimization_status": "completed",
          "recommendations": [
            {
              "type": "ai_automation",
              "description": "Consider automating 5 data processing tasks with AI",
              "tasks": [
                {
                  "task_id": "task_1",
                  "task_name": "Data Extraction",
                  "reason": "Data processing task suitable for AI automation"
                }
              ],
              "impact": "high",
              "effort": "medium"
            },
            {
              "type": "human_retention",
              "description": "Maintain human oversight for 3 decision-making tasks",
              "tasks": [
                {
                  "task_id": "task_6",
                  "task_name": "Final Approval",
                  "reason": "Requires human judgment and decision-making"
                }
              ],
              "impact": "high",
              "effort": "low"
            }
          ],
          "automation_potential": 0.6,
          "ai_suitable_tasks_count": 5,
          "human_required_tasks_count": 3,
          "total_tasks": 8
        }
      }
    }
  },
  "events": [
    {
      "type": "process_optimized",
      "workflow_id": "workflow_abc123"
    }
  ]
}
```

### Error Response

```json
{
  "error": "workflow_id is required for optimize_process intent",
  "error_code": "VALIDATION_ERROR",
  "execution_id": "exec_abc123"
}
```

---

## 4. Artifact Registration

### State Surface Updates
- Optimization artifact stored in execution state
- No Artifact Plane registration (optimization is a proposal, not a deliverable)

---

## 5. Idempotency

### Idempotency Key
`optimization_fingerprint = hash(workflow_id + tenant_id)`

### Behavior
- Same workflow = same optimization recommendations
- May change if workflow data changes
- Safe to retry

---

## 6. Implementation Details

### Handler Location
`symphainy_platform/realms/journey/orchestrators/journey_orchestrator.py::JourneyOrchestrator._handle_optimize_process`

### Key Implementation Steps
1. Validate `workflow_id` is provided
2. Call `WorkflowConversionService.optimize_workflow()`
3. Create structured artifact with semantic payload and renderings
4. Return artifacts and events

### Enabling Services
- **WorkflowConversionService:** `symphainy_platform/realms/journey/enabling_services/workflow_conversion_service.py`
  - `optimize_workflow()` - Analyze workflow for optimization

### Optimization Logic
Tasks categorized by keywords:
- **AI suitable:** "data", "extract", "parse", "validate", "transform", "analyze"
- **Human required:** "approve", "review", "decide", "judge", "evaluate"

---

## 7. Frontend Integration

### Frontend Usage (JourneyAPIManager.ts)
```typescript
// JourneyAPIManager.optimizeProcess()
const result = await journeyManager.optimizeProcess(
  workflowId,
  { detailed_analysis: true }
);

if (result.success) {
  const optimization = result.optimized_process;
  // Display recommendations, automation potential
}
```

### Expected Frontend Behavior
1. User selects workflow
2. Frontend submits `optimize_process` intent
3. Track execution via `trackExecution()`
4. Wait for completion
5. Extract `optimized_process` from artifacts
6. Display recommendations to user

---

## 8. Error Handling

### Validation Errors
- `workflow_id` missing → `ValueError`

### Runtime Errors
- Workflow data not found → Empty recommendations
- Service error → RuntimeError

---

## 9. Testing & Validation

### Happy Path
1. Workflow exists in context
2. Submit `optimize_process` intent
3. Service analyzes workflow
4. Return optimization recommendations

### Boundary Violations
- Missing `workflow_id` → Validation error

---

## 10. Contract Compliance

### Required Artifacts
- `optimization` - Optimization recommendations

### Required Events
- `process_optimized` - With `workflow_id`

---

## 11. Cross-Reference Analysis

### Journey Contract Says
- Not explicitly in journey contracts
- Implied by coexistence analysis journey

### Implementation Does
- ✅ Handles `optimize_process` intent
- ✅ Returns recommendations

### Frontend Expects
- ✅ Intent type: `optimize_process`
- ✅ Returns `optimized_process`

### Gaps/Discrepancies
- **NAMING:** Not in journey contracts, but implemented and used by frontend
- **Recommendation:** Add to coexistence analysis journey contract

---

**Last Updated:** January 27, 2026  
**Owner:** Journey Realm Solution Team  
**Status:** ✅ **COMPREHENSIVE**
