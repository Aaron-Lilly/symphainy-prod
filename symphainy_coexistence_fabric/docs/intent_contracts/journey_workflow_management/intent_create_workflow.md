# Intent Contract: create_workflow

**Intent:** create_workflow  
**Intent Type:** `create_workflow`  
**Journey:** Workflow Management (`journey_workflow_management`)  
**Realm:** Journey Realm  
**Status:** ✅ **COMPREHENSIVE**  
**Priority:** 🔴 **PRIORITY 1** - Core workflow creation

---

## 1. Intent Overview

### Purpose
Create a workflow from an SOP or BPMN file. Supports two modes:
1. **From SOP:** Convert SOP structure to BPMN workflow
2. **From BPMN file:** Parse uploaded BPMN XML and create workflow structure

### Intent Flow
```
[Mode 1: From SOP]
    ↓
[create_workflow with sop_id]
    ↓
[WorkflowConversionService.create_workflow()]
    ↓
[Convert SOP steps to BPMN tasks]
[Generate BPMN XML]

[Mode 2: From BPMN file]
    ↓
[create_workflow with workflow_file_path]
    ↓
[Get file content from storage]
[WorkflowConversionService.parse_bpmn_file()]
    ↓
[Parse BPMN XML to workflow structure]

[Both modes]
    ↓
[Generate workflow visualization]
[Register artifact in Artifact Plane]
    ↓
[Return workflow artifact]
```

### Expected Observable Artifacts
- `workflow` artifact with:
  - `workflow_id` - Generated workflow identifier
  - `workflow_type` - "bpmn" or derived type
  - `status` - Creation status
  - `sop_id` - Source SOP (if from SOP)
  - `source_file` - Source file path (if from file)
  - `workflow_content` - Workflow structure
  - `bpmn_xml` - Generated/parsed BPMN XML
  - `workflow_visual` - Visualization (if generated)

---

## 2. Intent Parameters

### Required Parameters (one of)

| Parameter | Type | Description | Validation |
|-----------|------|-------------|------------|
| `sop_id` | `string` | SOP identifier (Mode 1) | Required unless `workflow_file_path` |
| `workflow_file_path` | `string` | Path to BPMN file (Mode 2) | Required unless `sop_id` |

### Optional Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `workflow_type` | `string` | Workflow type | `"bpmn"` |
| `workflow_options` | `object` | Creation options | `{}` |

### Context Metadata (from ExecutionContext)

| Metadata Key | Type | Description | Source |
|--------------|------|-------------|--------|
| `tenant_id` | `string` | Tenant identifier | Runtime (required) |
| `session_id` | `string` | Session identifier | Runtime (required) |
| `sop_{sop_id}` | `object` | SOP data (if from SOP) | From prior intent |

---

## 3. Intent Returns

### Success Response

```json
{
  "artifacts": {
    "workflow": {
      "result_type": "workflow",
      "semantic_payload": {
        "workflow_id": "workflow_abc123",
        "workflow_type": "bpmn",
        "status": "created",
        "sop_id": "sop_xyz789",
        "source_file": null
      },
      "renderings": {
        "workflow": {
          "workflow_id": "workflow_abc123",
          "workflow_name": "SOP-based Workflow",
          "sop_source": "sop_xyz789",
          "bpmn_xml": "<?xml version=\"1.0\"...>",
          "tasks": [
            {
              "id": "task_1",
              "name": "Step 1",
              "type": "bpmn:task",
              "documentation": "First step"
            }
          ],
          "sequence_flows": [
            {
              "id": "flow_1",
              "source": "task_1",
              "target": "task_2"
            }
          ],
          "total_tasks": 5
        },
        "workflow_visual": {
          "image_base64": "...",
          "storage_path": "gs://bucket/workflow_visual.png"
        }
      },
      "metadata": {
        "artifact_id": "artifact_abc123"
      }
    }
  },
  "events": [
    {
      "type": "workflow_created",
      "sop_id": "sop_xyz789",
      "workflow_id": "workflow_abc123",
      "artifact_id": "artifact_abc123"
    }
  ]
}
```

---

## 4. Artifact Registration

### Artifact Plane Registration
- **Artifact Type:** `workflow`
- **Lifecycle State:** `draft` (initial)
- **Owner:** `client`
- **Purpose:** `delivery`
- **Source Artifacts:** `[sop_id]` (if from SOP)

### State Surface Updates
- Workflow artifact registered in Artifact Plane
- Execution state stored with artifacts

---

## 5. Idempotency

### Idempotency Key
`workflow_fingerprint = hash(sop_id + tenant_id)` or `hash(workflow_file_path + tenant_id)`

### Behavior
- Same SOP/file = same workflow structure
- Regeneration produces same BPMN from same SOP
- Safe to retry

---

## 6. Implementation Details

### Handler Location
`symphainy_platform/realms/journey/orchestrators/journey_orchestrator.py::JourneyOrchestrator._handle_create_workflow`

### Key Implementation Steps

**Mode 1: From SOP**
1. Validate `sop_id` provided
2. Call `WorkflowConversionService.create_workflow()`
3. Service converts SOP steps to BPMN tasks
4. Service generates BPMN XML

**Mode 2: From BPMN file**
1. Validate `workflow_file_path` provided
2. Try to get parsed file via `FileParserService`
3. If not found, get from file storage abstraction
4. Call `WorkflowConversionService.parse_bpmn_file()`
5. Optionally create deterministic chunks and semantic signals (Phase 3)

**Both modes:**
1. Generate workflow visualization via `VisualGenerationService`
2. Register artifact in Artifact Plane (if available)
3. Create structured artifact
4. Return artifacts and events

### Enabling Services
- **WorkflowConversionService:** `symphainy_platform/realms/journey/enabling_services/workflow_conversion_service.py`
  - `create_workflow()` - Create workflow from SOP
  - `parse_bpmn_file()` - Parse BPMN XML
- **VisualGenerationService:** `symphainy_platform/realms/journey/enabling_services/visual_generation_service.py`
  - `generate_workflow_visual()` - Generate workflow visualization

### BPMN Generation
Generates valid BPMN 2.0 XML with:
- `<bpmn:startEvent>` - Start event
- `<bpmn:task>` - Tasks from SOP steps
- `<bpmn:exclusiveGateway>` - Decision points
- `<bpmn:endEvent>` - End event
- `<bpmn:sequenceFlow>` - Task connections

---

## 7. Frontend Integration

### Frontend Usage (JourneyAPIManager.ts)
```typescript
// Create workflow from SOP
const result = await journeyManager.createWorkflow(
  sopId,
  { include_visualization: true }
);

if (result.success) {
  const workflow = result.workflow;
  // Display workflow structure and visualization
}
```

### Expected Frontend Behavior
1. User has SOP or BPMN file
2. Frontend submits `create_workflow` intent
3. Track execution via `trackExecution()`
4. Wait for completion
5. Extract `workflow` from artifacts
6. Display workflow structure and visualization

---

## 8. Error Handling

### Validation Errors
- Neither `sop_id` nor `workflow_file_path` → `ValueError`

### Runtime Errors
- SOP data not found → Error response
- BPMN parsing fails → Create basic workflow structure
- Visualization fails → Continue without visual

---

## 9. Testing & Validation

### Happy Path (From SOP)
1. SOP exists with steps
2. Submit `create_workflow` with `sop_id`
3. Workflow created with BPMN XML
4. Visualization generated

### Happy Path (From BPMN)
1. BPMN file exists
2. Submit `create_workflow` with `workflow_file_path`
3. BPMN parsed to workflow structure
4. Visualization generated

### Boundary Violations
- Missing both `sop_id` and `workflow_file_path` → Validation error

---

## 10. Contract Compliance

### Required Artifacts
- `workflow` - Workflow artifact with BPMN and optional visual

### Required Events
- `workflow_created` - With `sop_id`, `workflow_id`, `artifact_id`

---

## 11. Cross-Reference Analysis

### Journey Contract Says
- `create_workflow_from_sop` - Create workflow from SOP

### Implementation Does
- ✅ `create_workflow` handles both SOP and BPMN file
- ✅ Generates BPMN XML
- ✅ Registers artifact in Artifact Plane

### Frontend Expects
- ✅ Intent type: `create_workflow`
- ✅ Returns `workflow` with structure

### Gaps/Discrepancies
- **NAMING:** Contract says `create_workflow_from_sop`, implementation uses `create_workflow`
- **Recommendation:** Use `create_workflow` (unified - handles both modes)

---

**Last Updated:** January 27, 2026  
**Owner:** Journey Realm Solution Team  
**Status:** ✅ **COMPREHENSIVE**
