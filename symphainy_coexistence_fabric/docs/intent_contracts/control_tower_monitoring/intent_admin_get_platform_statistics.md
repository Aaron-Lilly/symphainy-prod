# Intent Contract: admin_get_platform_statistics

**Intent:** admin_get_platform_statistics  
**Intent Type:** `admin_get_platform_statistics`  
**Journey:** Platform Monitoring (`control_tower_monitoring`)  
**Solution:** Control Tower (Admin Dashboard)  
**View:** Control Room  
**Status:** ✅ **IMPLEMENTED**  
**Priority:** 🔴 **PRIORITY 1** - Core observability

---

## 1. Intent Overview

### Purpose
Retrieve overall platform statistics including realm count, solution count, and system health status. Provides a high-level dashboard view of platform state.

### Intent Flow
```
[Admin requests platform statistics]
    ↓
[admin_get_platform_statistics intent]
    ↓
[Access control check (control_room view)]
    ↓
[ControlRoomService.get_platform_statistics()]
    ↓
[Query Runtime client for realms]
[Query Solution registry for solutions]
[Get system health status]
    ↓
[Return platform_statistics artifact]
```

### Expected Observable Artifacts
- `platform_statistics` artifact with:
  - `timestamp` - ISO timestamp
  - `realms.total` - Total realm count
  - `realms.registered` - List of registered realm names
  - `solutions.total` - Total solution count
  - `solutions.active` - Active solution count
  - `system_health` - Overall health status

---

## 2. Intent Parameters

### Required Parameters
None - this is a read-only query intent.

### Optional Parameters
None.

### Context Metadata (from ExecutionContext)

| Metadata Key | Type | Description | Source |
|--------------|------|-------------|--------|
| `tenant_id` | `string` | Tenant identifier | Runtime (required) |
| `session_id` | `string` | Session identifier | Runtime (required) |
| `user_id` | `string` | User identifier | Auth context |

---

## 3. Intent Returns

### Success Response

```json
{
  "artifacts": {
    "platform_statistics": {
      "timestamp": "2026-01-27T10:30:00Z",
      "realms": {
        "total": 5,
        "registered": ["content", "insights", "journey", "outcomes", "operations"]
      },
      "solutions": {
        "total": 3,
        "active": 2
      },
      "system_health": "healthy"
    }
  },
  "events": []
}
```

### Error Response

```json
{
  "error": "Access denied",
  "error_code": "FORBIDDEN",
  "execution_id": "exec_abc123"
}
```

---

## 4. Access Control

### Required Access
- View: `control_room`
- Feature: None (base access)

### Check Pattern
```python
has_access = await admin_service.check_access(user_id, "control_room")
if not has_access:
    raise HTTPException(status_code=403, detail="Access denied")
```

---

## 5. Implementation Details

### Service Location
`symphainy_platform/civic_systems/experience/admin_dashboard/services/control_room_service.py::ControlRoomService.get_platform_statistics`

### API Endpoint
`GET /api/admin/control-room/statistics`

### Key Implementation Steps
1. Get realm count from Runtime client or realm registry
2. Get solution count from Solution registry
3. Get system health status
4. Return aggregated statistics

### Data Sources
- **Realms:** Runtime client (`get_realms()`) or Realm registry
- **Solutions:** Solution registry (`list_solutions()`)
- **Health:** Runtime health + Infrastructure health

---

## 6. Frontend Integration

### Frontend Usage (AdminAPIManager.ts)
```typescript
// AdminAPIManager.getPlatformStatistics()
async getPlatformStatistics(): Promise<PlatformStatistics> {
  const artifacts = await this._submitAdminIntent('admin_get_platform_statistics');
  return artifacts.platform_statistics;
}
```

### Expected Frontend Behavior
1. Admin navigates to Control Room
2. Frontend submits `admin_get_platform_statistics` intent
3. Display realm count, solution count, system health
4. Auto-refresh on interval (optional)

---

## 7. Error Handling

### Access Control Errors
- User not authorized for control_room → 403 Forbidden

### Runtime Errors
- Runtime client not available → Fallback to registry
- Registry not available → Return partial data

---

## 8. Contract Compliance

### Required Artifacts
- `platform_statistics` - Platform statistics object

### Required Events
- None (read-only query)

---

## 9. Cross-Reference Analysis

### Journey Contract Says
- `get_platform_statistics` - Step 1

### Implementation Has
- ✅ `admin_get_platform_statistics` (with `admin_` prefix)
- ✅ Returns realms, solutions, system_health

### Frontend Expects
- ✅ Intent type: `admin_get_platform_statistics`
- ✅ Returns `platform_statistics`

---

**Last Updated:** January 27, 2026  
**Owner:** Control Tower Team  
**Status:** ✅ **IMPLEMENTED**
