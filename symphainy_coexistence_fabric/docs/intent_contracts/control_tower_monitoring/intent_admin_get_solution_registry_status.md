# Intent Contract: admin_get_solution_registry_status

**Intent:** admin_get_solution_registry_status  
**Intent Type:** `admin_get_solution_registry_status`  
**Journey:** Platform Monitoring (`control_tower_monitoring`)  
**Solution:** Control Tower (Admin Dashboard)  
**View:** Control Room  
**Status:** ✅ **IMPLEMENTED**  
**Priority:** 🔴 **PRIORITY 1** - Core observability

---

## 1. Intent Overview

### Purpose
Retrieve status of all registered solutions in the platform. Shows total solutions, active vs inactive, domain bindings, and supported intents per solution.

### Intent Flow
```
[Admin requests solution registry status]
    ↓
[admin_get_solution_registry_status intent]
    ↓
[Access control check (control_room view)]
    ↓
[ControlRoomService.get_solution_registry_status()]
    ↓
[Query Solution registry]
    ↓
[Return solution_registry_status artifact]
```

### Expected Observable Artifacts
- `solution_registry_status` artifact with:
  - `solutions` - Array of solution details
  - `total` - Total solution count
  - `active` - Active solution count
  - `timestamp` - ISO timestamp

---

## 2. Intent Parameters

### Required Parameters
None - this is a read-only query intent.

---

## 3. Intent Returns

### Success Response

```json
{
  "artifacts": {
    "solution_registry_status": {
      "solutions": [
        {
          "solution_id": "coexistence_solution_v1",
          "status": "active",
          "domains": ["content", "insights", "journey", "outcomes"],
          "intents": ["ingest_file", "parse_content", "analyze_content", "optimize_process", "synthesize_outcome"],
          "created_at": "2026-01-15T08:00:00Z"
        },
        {
          "solution_id": "content_only_solution",
          "status": "inactive",
          "domains": ["content"],
          "intents": ["ingest_file", "parse_content"],
          "created_at": "2026-01-10T12:00:00Z"
        }
      ],
      "total": 2,
      "active": 1,
      "timestamp": "2026-01-27T10:30:00Z"
    }
  },
  "events": []
}
```

---

## 4. Implementation Details

### Service Location
`symphainy_platform/civic_systems/experience/admin_dashboard/services/control_room_service.py::ControlRoomService.get_solution_registry_status`

### API Endpoint
`GET /api/admin/control-room/solution-registry`

### Key Implementation Steps
1. Get all solutions from Solution registry
2. Get active solutions
3. For each solution, extract:
   - solution_id
   - status (active/inactive)
   - domains (from domain_service_bindings)
   - intents (supported_intents)
   - created_at
4. Return aggregated status

---

## 5. Frontend Integration

### Frontend Usage (AdminAPIManager.ts)
```typescript
// AdminAPIManager.getSolutionRegistryStatus()
async getSolutionRegistryStatus(): Promise<SolutionRegistryStatus> {
  const artifacts = await this._submitAdminIntent('admin_get_solution_registry_status');
  return artifacts.solution_registry_status;
}
```

### Expected Frontend Type
```typescript
export interface SolutionRegistryStatus {
  total_solutions: number;
  active_solutions: number;
  inactive_solutions: number;
  solutions_by_domain: Record<string, number>;
  solution_health: Record<string, {
    status: 'active' | 'inactive' | 'error';
    execution_count: number;
    success_rate: number;
  }>;
}
```

---

## 6. Contract Compliance

### Required Artifacts
- `solution_registry_status` - Solution registry status object

---

**Last Updated:** January 27, 2026  
**Owner:** Control Tower Team  
**Status:** ✅ **IMPLEMENTED**
