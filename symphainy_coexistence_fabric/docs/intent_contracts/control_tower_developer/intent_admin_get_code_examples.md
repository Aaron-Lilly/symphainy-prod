# Intent Contract: admin_get_code_examples

**Intent:** admin_get_code_examples  
**Intent Type:** `admin_get_code_examples`  
**Journey:** Developer Documentation (`control_tower_developer`)  
**Solution:** Control Tower (Admin Dashboard)  
**View:** Developer View  
**Status:** ✅ **IMPLEMENTED**  
**Priority:** 🟡 **PRIORITY 2** - Developer tools

---

## 1. Intent Overview

### Purpose
Retrieve code examples for Platform SDK patterns including solution implementation, journey orchestration, and MCP integration patterns.

---

## 2. Intent Parameters

### Optional Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `category` | `string` | Specific category to retrieve | All examples |

---

## 3. Intent Returns

### Success Response

```json
{
  "artifacts": {
    "code_examples": {
      "examples": {
        "creating_solution": {
          "title": "Creating a Solution",
          "language": "python",
          "code": "from symphainy_platform.bases.solution_base import BaseSolution..."
        },
        "building_solution": {
          "title": "Building a Solution with SolutionBuilder",
          "language": "python",
          "code": "from symphainy_platform.civic_systems.platform_sdk.solution_builder import SolutionBuilder..."
        },
        "creating_journey": {
          "title": "Creating a Journey Orchestrator",
          "language": "python",
          "code": "from symphainy_platform.bases.orchestrator_base import OrchestratorBase..."
        }
      }
    }
  },
  "events": []
}
```

---

## 4. Implementation Details

### Service Location
`symphainy_platform/civic_systems/experience/admin_dashboard/services/developer_view_service.py::DeveloperViewService.get_code_examples`

---

## 5. Frontend Integration

```typescript
async getCodeExamples(category?: string): Promise<CodeExamples> {
  const artifacts = await this._submitAdminIntent('admin_get_code_examples', { category });
  return artifacts.code_examples;
}
```

---

**Last Updated:** January 27, 2026  
**Owner:** Control Tower Team  
**Status:** ✅ **IMPLEMENTED**
