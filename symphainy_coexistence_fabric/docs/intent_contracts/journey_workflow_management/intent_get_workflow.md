# Intent Contract: get_workflow

**Intent:** get_workflow  
**Intent Type:** `get_workflow`  
**Journey:** Workflow Management (`journey_workflow_management`)  
**Realm:** Journey Realm  
**Status:** ✅ **COMPREHENSIVE**  
**Priority:** 🟡 **PRIORITY 2** - Workflow retrieval

---

## 1. Intent Overview

### Purpose
Retrieve workflow data by workflow_id. Attempts to get workflow from execution state or Artifact Plane. Returns workflow structure including BPMN, tasks, and sequence flows.

### Intent Flow
```
[User requests workflow data]
    ↓
[get_workflow intent]
    ↓
[Try execution state]
    ↓
[If not found: Try Artifact Plane]
    ↓
[If not found: Return basic structure with status "not_found"]
    ↓
[Return workflow data]
```

### Expected Observable Artifacts
- `workflow` - Workflow data object

---

## 2. Intent Parameters

### Required Parameters

| Parameter | Type | Description | Validation |
|-----------|------|-------------|------------|
| `workflow_id` | `string` | Workflow identifier | Required, non-empty |

### Optional Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `user_context` | `object` | User context (tenant_id, session_id) | `{}` |

### Context Metadata (from ExecutionContext)

| Metadata Key | Type | Description | Source |
|--------------|------|-------------|--------|
| `tenant_id` | `string` | Tenant identifier | Runtime or user_context |
| `session_id` | `string` | Session identifier | Runtime or user_context |

---

## 3. Intent Returns

### Success Response (Found)

```json
{
  "success": true,
  "workflow": {
    "workflow_id": "workflow_abc123",
    "workflow_name": "Order Processing Workflow",
    "bpmn_xml": "<?xml version=\"1.0\"...>",
    "tasks": [
      {
        "id": "task_1",
        "name": "Receive Order",
        "type": "task",
        "description": "Receive customer order",
        "actor": "user",
        "position": 1
      }
    ],
    "sequence_flows": [
      {
        "id": "flow_1",
        "source": "task_1",
        "target": "task_2"
      }
    ],
    "total_tasks": 5,
    "decision_points": 2
  }
}
```

### Response (Not Found)

```json
{
  "success": true,
  "workflow": {
    "workflow_id": "workflow_abc123",
    "description": "Workflow process",
    "steps": [],
    "status": "not_found"
  }
}
```

---

## 4. Artifact Registration

### State Surface Access
- **Read-Only:** This intent retrieves, does not create artifacts
- **Sources:** Execution state, Artifact Plane

---

## 5. Idempotency

### Idempotency Key
N/A - Read-only operation

### Behavior
- Safe to call multiple times
- Returns current state of workflow
- May return different results if workflow updated

---

## 6. Implementation Details

### Handler Location
`symphainy_platform/realms/journey/orchestrators/journey_orchestrator.py::JourneyOrchestrator._handle_get_workflow_soa`

### Key Implementation Steps
1. Validate `workflow_id` provided
2. Create execution context
3. Try to get workflow from execution state
4. If not found, try Artifact Plane
5. If still not found, return basic structure with "not_found" status

### Data Sources (in order)
1. **Execution State:** `state_surface.get_execution_state(f"workflow_{workflow_id}")`
2. **Artifact Plane:** `artifact_plane.get_artifact(artifact_id=workflow_id)`

---

## 7. Frontend Integration

### Frontend Usage
```typescript
// Get workflow data (via SOA API or intent)
const workflow = await journeyOrchestrator.get_workflow({
  workflow_id: "workflow_abc123",
  user_context: {
    tenant_id: "tenant_123",
    session_id: "session_456"
  }
});

if (workflow.success) {
  // Use workflow.workflow data
  displayWorkflow(workflow.workflow);
}
```

### Expected Frontend Behavior
1. Frontend needs workflow data
2. Call `get_workflow` with `workflow_id`
3. Receive workflow structure
4. Display or process workflow

---

## 8. Error Handling

### Validation Errors
- `workflow_id` missing → `ValueError("workflow_id is required")`

### Runtime Errors
- Execution state unavailable → Try Artifact Plane
- Artifact Plane unavailable → Return basic structure
- All sources fail → Return "not_found" status

---

## 9. Testing & Validation

### Happy Path
1. Workflow exists in execution state
2. Call `get_workflow`
3. Return workflow data

### Not Found Path
1. Workflow doesn't exist
2. Call `get_workflow`
3. Return basic structure with "not_found" status

---

## 10. Contract Compliance

### Required Response
- `success` - Boolean
- `workflow` - Workflow data object

### SOA API
- Defined in `_define_soa_api_handlers()`
- Can be called via MCP tool

---

## 11. Cross-Reference Analysis

### Journey Contract Says
- Not explicitly in journey contracts

### Implementation Does
- ✅ `get_workflow` SOA API handler
- ✅ Retrieves from execution state or Artifact Plane
- ✅ Graceful fallback for not found

### Frontend Expects
- ✅ Workflow retrieval capability
- ✅ Returns workflow structure

### Gaps/Discrepancies
- **NAMING:** Not in journey contracts, but implemented as SOA API
- **Recommendation:** Add to workflow management journey contract

---

**Last Updated:** January 27, 2026  
**Owner:** Journey Realm Solution Team  
**Status:** ✅ **COMPREHENSIVE**
