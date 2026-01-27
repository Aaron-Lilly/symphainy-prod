# Intent Contract: admin_get_system_health

**Intent:** admin_get_system_health  
**Intent Type:** `admin_get_system_health`  
**Journey:** Platform Monitoring (`control_tower_monitoring`)  
**Solution:** Control Tower (Admin Dashboard)  
**View:** Control Room  
**Status:** ✅ **IMPLEMENTED**  
**Priority:** 🔴 **PRIORITY 1** - Core observability

---

## 1. Intent Overview

### Purpose
Retrieve comprehensive system health status including Runtime health, infrastructure health (databases, storage), and observability stack health.

### Intent Flow
```
[Admin requests system health]
    ↓
[admin_get_system_health intent]
    ↓
[Access control check (control_room view)]
    ↓
[ControlRoomService.get_system_health()]
    ↓
[Check Runtime health]
[Check Infrastructure health (ArangoDB, Redis, GCS)]
    ↓
[Return system_health artifact]
```

### Expected Observable Artifacts
- `system_health` artifact with:
  - `runtime` - Runtime health status
  - `infrastructure` - Infrastructure component health
  - `overall` - Overall health status

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
    "system_health": {
      "runtime": {
        "status": "healthy",
        "available": true
      },
      "infrastructure": {
        "adapters": {
          "arango": { "status": "healthy" },
          "redis": { "status": "healthy" },
          "gcs": { "status": "healthy" }
        },
        "status": "healthy"
      },
      "overall": "healthy"
    }
  },
  "events": []
}
```

### Frontend Expected Type
```typescript
export interface SystemHealth {
  runtime: {
    status: 'healthy' | 'degraded' | 'unhealthy';
    wal_health: 'healthy' | 'degraded' | 'unhealthy';
    state_surface_health: 'healthy' | 'degraded' | 'unhealthy';
  };
  infrastructure: {
    database: {
      arangodb: 'healthy' | 'degraded' | 'unhealthy';
      redis: 'healthy' | 'degraded' | 'unhealthy';
    };
    storage: {
      gcs: 'healthy' | 'degraded' | 'unhealthy';
      supabase: 'healthy' | 'degraded' | 'unhealthy';
    };
    telemetry: 'healthy' | 'degraded' | 'unhealthy';
  };
  observability: {
    opentelemetry: 'healthy' | 'degraded' | 'unhealthy';
    prometheus: 'healthy' | 'degraded' | 'unhealthy';
    tempo: 'healthy' | 'degraded' | 'unhealthy';
  };
}
```

---

## 4. Health Status Values

| Status | Description |
|--------|-------------|
| `healthy` | Component operating normally |
| `degraded` | Component operational but with issues |
| `unhealthy` | Component not operational or critical errors |
| `unknown` | Cannot determine health status |

---

## 5. Implementation Details

### Service Location
`symphainy_platform/civic_systems/experience/admin_dashboard/services/control_room_service.py::ControlRoomService.get_system_health`

### API Endpoint
`GET /api/admin/control-room/system-health`

### Key Implementation Steps
1. Check Runtime health (Runtime client ping)
2. Check Infrastructure health via Public Works adapters:
   - ArangoDB adapter status
   - Redis adapter status
   - GCS adapter status
3. Calculate overall health from component statuses

### Health Calculation Logic
```python
if runtime_health == "healthy" and infrastructure_health == "healthy":
    overall = "healthy"
elif runtime_health == "unhealthy" or infrastructure_health == "unhealthy":
    overall = "unhealthy"
else:
    overall = "degraded"
```

---

## 6. Frontend Integration

### Frontend Usage (AdminAPIManager.ts)
```typescript
// AdminAPIManager.getSystemHealth()
async getSystemHealth(): Promise<SystemHealth> {
  const artifacts = await this._submitAdminIntent('admin_get_system_health');
  return artifacts.system_health;
}
```

---

## 7. Contract Compliance

### Required Artifacts
- `system_health` - System health object

---

**Last Updated:** January 27, 2026  
**Owner:** Control Tower Team  
**Status:** ✅ **IMPLEMENTED**
