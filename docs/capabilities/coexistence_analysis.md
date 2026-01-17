# Coexistence Analysis

**Realm:** Journey  
**Status:** ✅ Complete  
**Last Updated:** January 2026

---

## Overview

The Coexistence Analysis capability understands how new processes interact with existing ones, identifying conflicts, dependencies, and integration opportunities.

---

## Intents

### 1. `analyze_coexistence`

Analyzes how a workflow coexists with existing processes.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `workflow_id` | string | Yes | Identifier for the workflow to analyze |

#### Response

```json
{
  "artifacts": {
    "coexistence_analysis": {
      "workflow_id": "workflow_123",
      "existing_processes": [
        {
          "process_id": "process_456",
          "name": "Legacy Policy Processing",
          "interaction_type": "conflict",
          "severity": "high",
          "description": "Both processes modify the same policy status field",
          "recommendations": [
            "Use transaction locks",
            "Implement process queue"
          ]
        },
        {
          "process_id": "process_789",
          "name": "Policy Validation",
          "interaction_type": "dependency",
          "severity": "medium",
          "description": "Workflow depends on validation results",
          "recommendations": [
            "Ensure validation completes before workflow starts"
          ]
        }
      ],
      "integration_points": [
        {
          "point": "policy_status_update",
          "type": "shared_resource",
          "conflicts": 1,
          "dependencies": 0
        }
      ],
      "summary": {
        "total_conflicts": 1,
        "total_dependencies": 1,
        "risk_level": "medium"
      }
    },
    "workflow_id": "workflow_123"
  },
  "events": [
    {
      "type": "coexistence_analyzed",
      "workflow_id": "workflow_123"
    }
  ]
}
```

---

### 2. `create_blueprint`

Creates a comprehensive coexistence blueprint with visual workflow charts, transition roadmap, and responsibility matrix. See [Coexistence Blueprint](coexistence_blueprint.md) for detailed documentation.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `workflow_id` | string | Yes | Identifier for the workflow |

#### Response

```json
{
  "artifacts": {
    "blueprint": {
      "blueprint_id": "blueprint_123",
      "workflow_id": "workflow_123",
      "sections": [
        {
          "section": "Process Overview",
          "content": "This workflow processes insurance policies..."
        },
        {
          "section": "Coexistence Analysis",
          "content": "Interacts with 2 existing processes..."
        },
        {
          "section": "Integration Requirements",
          "content": "Requires transaction locks for policy status..."
        }
      ],
      "metadata": {
        "created_date": "2026-01-15T10:00:00Z",
        "version": "1.0"
      }
    },
    "workflow_id": "workflow_123"
  },
  "events": [
    {
      "type": "blueprint_created",
      "workflow_id": "workflow_123"
    }
  ]
}
```

---

## Use Cases

### 1. Legacy System Integration
**Scenario:** Integrating new workflows with legacy systems.

**Use Case:** Use `analyze_coexistence` to:
- Identify conflicts with legacy processes
- Understand dependencies
- Plan integration strategy

**Business Value:** Prevents conflicts and ensures smooth integration.

---

### 2. Process Modernization
**Scenario:** Modernizing processes while maintaining legacy operations.

**Use Case:** Use coexistence analysis to:
- Understand how new processes interact with old ones
- Identify migration risks
- Plan coexistence strategy

**Business Value:** Enables safe process modernization.

---

### 3. Blueprint Creation
**Scenario:** Documenting process integration requirements.

**Use Case:** Use `create_blueprint` to:
- Document process interactions
- Specify integration requirements
- Create implementation guide

**Business Value:** Provides clear documentation for implementation teams.

---

## Technical Details

### Implementation

The `analyze_coexistence` intent uses the `CoexistenceAnalysisService` which:
1. Retrieves workflow definition
2. Queries existing processes from State Surface
3. Analyzes interactions (conflicts, dependencies)
4. Identifies integration points
5. Generates recommendations

### Interaction Types

- **Conflict:** Processes modify the same resources
- **Dependency:** One process depends on another
- **Integration Point:** Shared resources or interfaces

---

## Related Capabilities

- [Workflow Creation](workflow_creation.md) - Create workflows to analyze
- [Visual Generation](visual_generation.md) - Visualize coexistence analysis
- [SOP Generation](sop_generation.md) - Document coexistence in SOPs

---

## API Examples

### Analyze Coexistence

```python
intent = Intent(
    intent_type="analyze_coexistence",
    parameters={
        "workflow_id": "workflow_123"
    }
)

result = await runtime.execute(intent, context)
conflicts = result.artifacts["coexistence_analysis"]["existing_processes"]
```

### Create Blueprint

```python
intent = Intent(
    intent_type="create_blueprint",
    parameters={
        "workflow_id": "workflow_123"
    }
)

result = await runtime.execute(intent, context)
blueprint_id = result.artifacts["blueprint"]["blueprint_id"]
```

---

**See Also:**
- [Journey Realm Overview](../architecture/north_star.md#23-domain-services-formerly-realms)
- [API Contracts](../execution/api_contracts_frontend_integration.md)
