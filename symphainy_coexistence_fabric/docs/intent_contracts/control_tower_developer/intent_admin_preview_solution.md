# Intent Contract: admin_preview_solution

**Intent:** admin_preview_solution  
**Intent Type:** `admin_preview_solution`  
**Journey:** Solution Playground (`control_tower_developer`)  
**Solution:** Control Tower (Admin Dashboard)  
**View:** Developer View  
**Status:** ✅ **IMPLEMENTED**  
**Priority:** 🟡 **PRIORITY 2** - Developer tools

---

## 1. Intent Overview

### Purpose
Preview a solution structure before registration. Shows what the built solution would look like.

---

## 2. Intent Parameters

### Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `solution_config` | `object` | Solution configuration to preview |

---

## 3. Intent Returns

### Success Response

```json
{
  "artifacts": {
    "solution_preview": {
      "solution_id": "generated_solution_abc123",
      "context": {
        "goals": ["Process content"],
        "constraints": [],
        "risk": "Low"
      },
      "domain_bindings": [
        {
          "domain": "content",
          "system_name": "symphainy_platform",
          "adapter_type": "internal_adapter"
        }
      ],
      "sync_strategies": [],
      "supported_intents": ["ingest_file", "parse_content"],
      "metadata": {}
    }
  },
  "events": []
}
```

---

## 4. Implementation Details

### Service Location
`symphainy_platform/civic_systems/experience/admin_dashboard/services/developer_view_service.py::DeveloperViewService.preview_solution`

---

## 5. Frontend Integration

```typescript
async previewSolution(request: SolutionValidationRequest): Promise<SolutionValidationResponse> {
  const artifacts = await this._submitAdminIntent('admin_preview_solution', request);
  return artifacts.solution_preview;
}
```

---

**Last Updated:** January 27, 2026  
**Owner:** Control Tower Team  
**Status:** ✅ **IMPLEMENTED**
