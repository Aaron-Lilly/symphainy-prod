# Intent Contract: admin_compose_solution

**Intent:** admin_compose_solution  
**Intent Type:** `admin_compose_solution`  
**Journey:** Solution Composition (`control_tower_business`)  
**Solution:** Control Tower (Admin Dashboard)  
**View:** Business User View  
**Status:** ✅ **IMPLEMENTED**  
**Priority:** 🟡 **PRIORITY 2** - Business tools (Gated)

---

## 1. Intent Overview

### Purpose
Compose a new solution from a configuration. Uses the advanced Solution Builder for business users.

---

## 2. Intent Parameters

### Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `solution_config` | `object` | Solution configuration |

---

## 3. Intent Returns

### Success Response

```json
{
  "artifacts": {
    "solution_composition": {
      "solution": { ... },
      "valid": true,
      "message": "Solution composed successfully"
    }
  },
  "events": []
}
```

---

## 4. Implementation Details

### Service Location
`symphainy_platform/civic_systems/experience/admin_dashboard/services/business_user_view_service.py::BusinessUserViewService.compose_solution`

### Access Control
This is a **gated feature** - requires `business` view access with `compose_solution` feature permission.

---

## 5. Frontend Integration

### Frontend Usage
```typescript
async composeSolution(request: SolutionCompositionRequest): Promise<SolutionCompositionResponse> {
  const artifacts = await this._submitAdminIntent('admin_compose_solution', request);
  return artifacts.solution_composition;
}
```

---

**Last Updated:** January 27, 2026  
**Owner:** Control Tower Team  
**Status:** ✅ **IMPLEMENTED** (Gated)
