# Intent Contract: admin_get_realm_health

**Intent:** admin_get_realm_health  
**Intent Type:** `admin_get_realm_health`  
**Journey:** Platform Monitoring (`control_tower_monitoring`)  
**Solution:** Control Tower (Admin Dashboard)  
**View:** Control Room  
**Status:** ✅ **IMPLEMENTED**  
**Priority:** 🔴 **PRIORITY 1** - Core observability

---

## 1. Intent Overview

### Purpose
Retrieve health status for all registered realms. Shows which realms are healthy, degraded, or unhealthy, along with supported intents and activity metrics.

### Intent Flow
```
[Admin requests realm health]
    ↓
[admin_get_realm_health intent]
    ↓
[Access control check (control_room view)]
    ↓
[ControlRoomService.get_realm_health()]
    ↓
[Query Runtime client for realm list]
[Check health status for each realm]
    ↓
[Return realm_health artifact]
```

### Expected Observable Artifacts
- `realm_health` artifact with:
  - `realms` - Array of realm health objects
  - `total` - Total realm count
  - `timestamp` - ISO timestamp
  - Per realm: `name`, `status`, `intents_supported`, `intents`

---

## 2. Intent Parameters

### Required Parameters
None - this is a read-only query intent.

### Context Metadata (from ExecutionContext)

| Metadata Key | Type | Description | Source |
|--------------|------|-------------|--------|
| `tenant_id` | `string` | Tenant identifier | Runtime (required) |
| `session_id` | `string` | Session identifier | Runtime (required) |

---

## 3. Intent Returns

### Success Response

```json
{
  "artifacts": {
    "realm_health": {
      "realms": [
        {
          "name": "content",
          "status": "healthy",
          "intents_supported": 12,
          "intents": ["ingest_file", "parse_content", "save_materialization", ...]
        },
        {
          "name": "insights",
          "status": "healthy",
          "intents_supported": 16,
          "intents": ["analyze_content", "interpret_data", "assess_data_quality", ...]
        },
        {
          "name": "journey",
          "status": "healthy",
          "intents_supported": 8,
          "intents": ["optimize_process", "generate_sop", "create_workflow", ...]
        },
        {
          "name": "outcomes",
          "status": "healthy",
          "intents_supported": 7,
          "intents": ["synthesize_outcome", "generate_roadmap", "create_poc", ...]
        }
      ],
      "total": 4,
      "timestamp": "2026-01-27T10:30:00Z"
    }
  },
  "events": []
}
```

### Realm Status Values

| Status | Description |
|--------|-------------|
| `healthy` | Realm responding normally |
| `degraded` | Realm responding with delays or partial errors |
| `unhealthy` | Realm not responding or critical errors |

---

## 4. Implementation Details

### Service Location
`symphainy_platform/civic_systems/experience/admin_dashboard/services/control_room_service.py::ControlRoomService.get_realm_health`

### API Endpoint
`GET /api/admin/control-room/realm-health`

### Key Implementation Steps
1. Try to get realms from Runtime client
2. If unavailable, fallback to Realm registry
3. For each realm, check health status and get supported intents
4. Return aggregated realm health

### Data Sources
- **Primary:** Runtime client (`get_realms()`)
- **Fallback:** Realm registry (`list_realms()`)
- **Intents:** Realm's `declare_intents()` method

---

## 5. Frontend Integration

### Frontend Usage (AdminAPIManager.ts)
```typescript
// AdminAPIManager.getRealmHealth()
async getRealmHealth(): Promise<RealmHealth> {
  const artifacts = await this._submitAdminIntent('admin_get_realm_health');
  return artifacts.realm_health;
}
```

### Expected Frontend Type
```typescript
export interface RealmHealth {
  realms: Record<string, {
    status: 'healthy' | 'degraded' | 'unhealthy';
    intent_count: number;
    response_time_ms: number;
    error_rate: number;
    last_activity: string;
  }>;
  overall_health: 'healthy' | 'degraded' | 'unhealthy';
}
```

---

## 6. Error Handling

### Runtime Errors
- Runtime client not available → Fallback to registry
- Realm registry not available → Return empty list with message

---

## 7. Contract Compliance

### Required Artifacts
- `realm_health` - Realm health object

### Required Events
- None (read-only query)

---

**Last Updated:** January 27, 2026  
**Owner:** Control Tower Team  
**Status:** ✅ **IMPLEMENTED**
