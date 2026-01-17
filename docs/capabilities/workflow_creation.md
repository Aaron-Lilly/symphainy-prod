# Workflow Creation

**Realm:** Journey  
**Status:** ✅ Complete  
**Last Updated:** January 2026

---

## Overview

The Workflow Creation capability creates executable workflows from BPMN models or existing SOPs, enabling process automation and optimization.

---

## Intent: `create_workflow`

Creates a workflow from either an existing SOP or a new BPMN file upload.

### Parameters

**Mode 1: From Existing SOP**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `sop_id` | string | Yes | Identifier for existing SOP |

**Mode 2: From BPMN File**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `workflow_file_path` | string | Yes | Path to BPMN workflow file |
| `workflow_type` | string | No | Type of workflow (default: "bpmn") |

### Response

```json
{
  "artifacts": {
    "workflow": {
      "workflow_id": "workflow_123",
      "workflow_type": "bpmn",
      "source": "sop_id_456",
      "status": "created",
      "metadata": {
        "created_date": "2026-01-15T10:00:00Z",
        "steps": 12,
        "decision_points": 3
      }
    },
    "sop_id": "sop_id_456",
    "workflow_visual": {
      "image_base64": "...",
      "storage_path": "workflows/workflow_123.png"
    }
  },
  "events": [
    {
      "type": "workflow_created",
      "sop_id": "sop_id_456"
    }
  ]
}
```

---

## Use Cases

### 1. Insurance Policy Migration Workflow
**Scenario:** Creating workflow for processing 350k insurance policies.

**Use Case:** Create workflow from BPMN model to:
- Define policy processing steps
- Include validation and error handling
- Enable automated execution

**Business Value:** Automates high-volume policy processing.

---

### 2. Permit Processing Workflow
**Scenario:** Creating workflow for permit data extraction and processing.

**Use Case:** Create workflow from SOP to:
- Convert manual SOP into executable workflow
- Include approval steps
- Track processing status

**Business Value:** Standardizes and automates permit processing.

---

### 3. Data Migration Workflow
**Scenario:** Creating workflow for legacy system data migration.

**Use Case:** Create workflow from BPMN model to:
- Define migration steps
- Include validation checkpoints
- Enable rollback capabilities

**Business Value:** Ensures reliable and auditable data migration.

---

## Technical Details

### Implementation

The `create_workflow` intent uses the `WorkflowConversionService` which:
1. **Mode 1 (SOP):** Converts SOP structure to workflow format
2. **Mode 2 (BPMN):** Parses BPMN file and creates workflow structure
3. Generates workflow visualization automatically
4. Stores workflow in State Surface

### Workflow Visualization

Automatically generates visual workflow diagrams:
- Shows all steps and decision points
- Includes metadata and annotations
- Stores as base64 image and file path

---

## Related Capabilities

- [SOP Generation](sop_generation.md) - Generate SOPs that can become workflows
- [Visual Generation](visual_generation.md) - Generate workflow diagrams
- [Coexistence Analysis](coexistence_analysis.md) - Analyze workflow interactions

---

## API Examples

### From SOP

```python
intent = Intent(
    intent_type="create_workflow",
    parameters={
        "sop_id": "sop_id_456"
    }
)

result = await runtime.execute(intent, context)
workflow_id = result.artifacts["workflow"]["workflow_id"]
```

### From BPMN File

```python
intent = Intent(
    intent_type="create_workflow",
    parameters={
        "workflow_file_path": "/path/to/workflow.bpmn",
        "workflow_type": "bpmn"
    }
)

result = await runtime.execute(intent, context)
workflow_id = result.artifacts["workflow"]["workflow_id"]
```

---

**See Also:**
- [Journey Realm Overview](../architecture/north_star.md#23-domain-services-formerly-realms)
- [API Contracts](../execution/api_contracts_frontend_integration.md)
