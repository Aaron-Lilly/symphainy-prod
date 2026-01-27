# Intent Contract: admin_validate_solution

**Intent:** admin_validate_solution  
**Intent Type:** `admin_validate_solution`  
**Journey:** Solution Playground (`control_tower_developer`)  
**Solution:** Control Tower (Admin Dashboard)  
**View:** Developer View  
**Status:** ✅ **IMPLEMENTED**  
**Priority:** 🟡 **PRIORITY 2** - Developer tools

---

## 1. Intent Overview

### Purpose
Validate a solution configuration using the Solution Builder Playground. Checks if the configuration is valid and can be built.

---

## 2. Intent Parameters

### Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `solution_config` | `object` | Solution configuration to validate |

### Solution Config Structure
```json
{
  "context": {
    "goals": ["Goal 1", "Goal 2"],
    "constraints": [],
    "risk": "Low"
  },
  "domain_service_bindings": [
    {
      "domain": "content",
      "system_name": "symphainy_platform",
      "adapter_type": "internal_adapter"
    }
  ],
  "supported_intents": ["ingest_file", "parse_content"]
}
```

---

## 3. Intent Returns

### Success Response (Valid)

```json
{
  "artifacts": {
    "solution_validation": {
      "valid": true,
      "solution": { ... },
      "message": "Solution is valid"
    }
  },
  "events": []
}
```

### Error Response (Invalid)

```json
{
  "artifacts": {
    "solution_validation": {
      "valid": false,
      "error": "Missing required field: context.goals",
      "message": "Solution validation failed"
    }
  },
  "events": []
}
```

---

## 4. Implementation Details

### Service Location
`symphainy_platform/civic_systems/experience/admin_dashboard/services/developer_view_service.py::DeveloperViewService.validate_solution`

### Key Implementation
Uses `SolutionBuilder.from_config()` to validate configuration:
```python
try:
    builder = SolutionBuilder.from_config(solution_config)
    solution = builder.build()
    return {"valid": True, "solution": solution.to_dict()}
except ValueError as e:
    return {"valid": False, "error": str(e)}
```

---

## 5. Frontend Integration

### Frontend Usage
```typescript
async validateSolution(request: SolutionValidationRequest): Promise<SolutionValidationResponse> {
  const artifacts = await this._submitAdminIntent('admin_validate_solution', request);
  return artifacts.solution_validation;
}
```

---

**Last Updated:** January 27, 2026  
**Owner:** Control Tower Team  
**Status:** ✅ **IMPLEMENTED**
