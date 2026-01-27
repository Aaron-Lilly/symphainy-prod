# Intent Contract: generate_sop

**Intent:** generate_sop  
**Intent Type:** `generate_sop`  
**Journey:** SOP Management (`journey_sop_management`)  
**Realm:** Journey Realm  
**Status:** ✅ **COMPREHENSIVE**  
**Priority:** 🔴 **PRIORITY 1** - Core SOP generation

---

## 1. Intent Overview

### Purpose
Generate a Standard Operating Procedure (SOP) from a workflow. Converts BPMN workflow structure to SOP document format. Supports both direct generation from workflow_id or chat-based generation via chat_mode.

### Intent Flow
```
[User has workflow to convert]
    ↓
[generate_sop intent]
    ↓
[If chat_mode: Redirect to generate_sop_from_chat]
[Else: WorkflowConversionService.generate_sop()]
    ↓
[Parse BPMN XML (if available)]
[Convert tasks to SOP steps]
[Generate SOP visualization (optional)]
    ↓
[Return SOP artifact]
```

### Expected Observable Artifacts
- `sop` artifact with:
  - `sop_id` - Generated SOP identifier
  - `workflow_id` - Source workflow identifier
  - `title` - SOP title
  - `status` - Generation status
  - `sop_content` - SOP structure with steps
  - `sop_visual` - Visualization (if available)

---

## 2. Intent Parameters

### Required Parameters (unless chat_mode)

| Parameter | Type | Description | Validation |
|-----------|------|-------------|------------|
| `workflow_id` | `string` | Workflow identifier to convert | Required unless `chat_mode=true` |

### Optional Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `chat_mode` | `boolean` | Use chat-based generation | `false` |
| `sop_options` | `object` | SOP generation options | `{}` |

### Context Metadata (from ExecutionContext)

| Metadata Key | Type | Description | Source |
|--------------|------|-------------|--------|
| `tenant_id` | `string` | Tenant identifier | Runtime (required) |
| `session_id` | `string` | Session identifier | Runtime (required) |
| `workflow_{workflow_id}` | `object` | Workflow data including BPMN | From prior intent |

---

## 3. Intent Returns

### Success Response

```json
{
  "artifacts": {
    "sop": {
      "result_type": "sop",
      "semantic_payload": {
        "sop_id": "sop_abc123",
        "workflow_id": "workflow_xyz789",
        "title": "SOP from workflow_xyz789",
        "status": "generated"
      },
      "renderings": {
        "sop": {
          "workflow_id": "workflow_xyz789",
          "sop_id": "sop_abc123",
          "sop_status": "generated",
          "sop_content": {
            "sop_id": "sop_abc123",
            "sop_title": "SOP from workflow_xyz789",
            "workflow_source": "workflow_xyz789",
            "steps": [
              {
                "step_number": 1,
                "step_name": "Data Collection",
                "step_id": "task_1",
                "description": "Collect data from sources",
                "actor": "user",
                "type": "task"
              }
            ],
            "total_steps": 5,
            "version": "1.0"
          },
          "steps_count": 5
        },
        "sop_visual": {
          "image_base64": "...",
          "storage_path": "gs://bucket/sop_visual.png"
        }
      }
    }
  },
  "events": [
    {
      "type": "sop_generated",
      "workflow_id": "workflow_xyz789"
    }
  ]
}
```

### Error Response

```json
{
  "error": "workflow_id is required for generate_sop intent (or use chat_mode=True)",
  "error_code": "VALIDATION_ERROR",
  "execution_id": "exec_abc123"
}
```

---

## 4. Artifact Registration

### State Surface Updates
- SOP artifact stored in execution state
- SOP visualization stored (if generated)

---

## 5. Idempotency

### Idempotency Key
`sop_fingerprint = hash(workflow_id + tenant_id)`

### Behavior
- Same workflow = same SOP structure
- Regeneration produces same steps from same BPMN
- Safe to retry

---

## 6. Implementation Details

### Handler Location
`symphainy_platform/realms/journey/orchestrators/journey_orchestrator.py::JourneyOrchestrator._handle_generate_sop`

### Key Implementation Steps
1. Check if `chat_mode=true` → Redirect to `_handle_generate_sop_from_chat`
2. Validate `workflow_id` is provided
3. Call `WorkflowConversionService.generate_sop()`
4. Optionally generate SOP visualization via `VisualGenerationService`
5. Create structured artifact
6. Return artifacts and events

### Enabling Services
- **WorkflowConversionService:** `symphainy_platform/realms/journey/enabling_services/workflow_conversion_service.py`
  - `generate_sop()` - Convert workflow to SOP format
- **VisualGenerationService:** `symphainy_platform/realms/journey/enabling_services/visual_generation_service.py`
  - `generate_sop_visual()` - Generate SOP visualization

### BPMN Parsing
- Parses `<bpmn:task>` elements → SOP steps
- Parses `<bpmn:exclusiveGateway>` elements → Decision points
- Falls back to workflow task structure if BPMN not available

---

## 7. Frontend Integration

### Frontend Usage (JourneyAPIManager.ts)
```typescript
// JourneyAPIManager.generateSOP()
const result = await journeyManager.generateSOP(
  workflowId,
  { include_visualization: true }
);

if (result.success) {
  const sop = result.sop;
  // Display SOP content and visualization
}
```

### Expected Frontend Behavior
1. User has workflow loaded
2. Frontend submits `generate_sop` intent
3. Track execution via `trackExecution()`
4. Wait for completion
5. Extract `sop` from artifacts
6. Display SOP content and visualization

---

## 8. Error Handling

### Validation Errors
- `workflow_id` missing (and not chat_mode) → `ValueError`

### Runtime Errors
- BPMN parsing fails → Use task structure fallback
- Visualization fails → Continue without visual (warning logged)
- Service error → RuntimeError

---

## 9. Testing & Validation

### Happy Path
1. Workflow with BPMN exists
2. Submit `generate_sop` intent
3. BPMN parsed to SOP steps
4. Visualization generated
5. SOP artifact returned

### Boundary Violations
- Missing `workflow_id` → Validation error (unless chat_mode)

---

## 10. Contract Compliance

### Required Artifacts
- `sop` - SOP artifact with content and optional visual

### Required Events
- `sop_generated` - With `workflow_id`

---

## 11. Cross-Reference Analysis

### Journey Contract Says
- `generate_sop_from_workflow` - Convert workflow to SOP

### Implementation Does
- ✅ Uses `generate_sop` intent type
- ✅ Converts workflow to SOP
- ✅ Supports chat_mode redirection

### Frontend Expects
- ✅ Intent type: `generate_sop`
- ✅ Returns `sop` with content

### Gaps/Discrepancies
- **NAMING:** Contract says `generate_sop_from_workflow`, implementation uses `generate_sop`
- **Recommendation:** Use `generate_sop` (simpler, unified)

---

**Last Updated:** January 27, 2026  
**Owner:** Journey Realm Solution Team  
**Status:** ✅ **COMPREHENSIVE**
