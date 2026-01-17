# Visual Generation

**Realm:** Journey  
**Status:** ✅ Complete  
**Last Updated:** January 2026

---

## Overview

The Visual Generation capability automatically creates visual diagrams for workflows, SOPs, and process documentation, making complex processes easy to understand.

---

## Automatic Visual Generation

Visual generation happens automatically when:
- Workflows are created (`create_workflow`)
- SOPs are generated (`generate_sop`, `generate_sop_from_chat`)
- Coexistence analysis is performed (`analyze_coexistence`)

### Visual Output

All visualizations include:
- **Base64 Image:** For immediate display in UI
- **Storage Path:** For persistent storage and retrieval
- **Metadata:** Diagram type, creation date, version

---

## Visual Types

### 1. Workflow Visualizations

Generated when workflows are created from BPMN files or SOPs.

**Features:**
- Process flow diagrams
- Decision points and branches
- Step annotations
- Metadata display

**Example:**
```json
{
  "workflow_visual": {
    "image_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
    "storage_path": "workflows/workflow_123.png"
  }
}
```

---

### 2. SOP Visualizations

Generated when SOPs are created from workflows or chat.

**Features:**
- Process flow diagrams
- Section breakdowns
- Step-by-step visualizations
- Annotations and notes

**Example:**
```json
{
  "sop_visual": {
    "image_base64": "iVBORw0KGgoAAAANSUhEUgAA...",
    "storage_path": "sops/sop_123.png"
  }
}
```

---

### 3. Coexistence Analysis Visualizations

Generated when coexistence analysis is performed.

**Features:**
- Process interaction diagrams
- Conflict visualization
- Integration points
- Dependency mapping

---

## Use Cases

### 1. Process Documentation
**Scenario:** Documenting complex business processes.

**Use Case:** Automatically generate visual diagrams to:
- Show process flow clearly
- Highlight decision points
- Document step sequences

**Business Value:** Makes complex processes understandable.

---

### 2. Training & Onboarding
**Scenario:** Training new team members on processes.

**Use Case:** Use visual diagrams to:
- Explain process steps visually
- Show process relationships
- Provide visual reference materials

**Business Value:** Accelerates onboarding and reduces errors.

---

### 3. Process Review
**Scenario:** Reviewing and optimizing processes.

**Use Case:** Use visual diagrams to:
- Identify bottlenecks visually
- See process interactions
- Plan optimizations

**Business Value:** Enables data-driven process improvement.

---

## Technical Details

### Implementation

Visual generation uses the `VisualGenerationService` which:
1. Receives workflow/SOP data
2. Generates diagram using graph visualization libraries
3. Converts to base64 image format
4. Stores in file storage
5. Returns both base64 and storage path

### Storage

Visualizations are stored:
- In GCS (via FileStorageAbstraction)
- With metadata in Supabase
- Accessible via storage path

---

## Related Capabilities

- [Workflow Creation](workflow_creation.md) - Creates workflows with visuals
- [SOP Generation](sop_generation.md) - Creates SOPs with visuals
- [Coexistence Analysis](coexistence_analysis.md) - Creates analysis visuals

---

## API Access

Visuals are automatically included in workflow and SOP creation responses:

```python
# Workflow creation includes visual
intent = Intent(
    intent_type="create_workflow",
    parameters={"sop_id": "sop_123"}
)

result = await runtime.execute(intent, context)
visual_base64 = result.artifacts["workflow_visual"]["image_base64"]
visual_path = result.artifacts["workflow_visual"]["storage_path"]
```

---

**See Also:**
- [Journey Realm Overview](../architecture/north_star.md#23-domain-services-formerly-realms)
- [API Contracts](../execution/api_contracts_frontend_integration.md)
