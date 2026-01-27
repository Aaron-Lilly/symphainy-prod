# Intent Contract: admin_get_execution_metrics

**Intent:** admin_get_execution_metrics  
**Intent Type:** `admin_get_execution_metrics`  
**Journey:** Platform Monitoring (`control_tower_monitoring`)  
**Solution:** Control Tower (Admin Dashboard)  
**View:** Control Room  
**Status:** ⚠️ **MVP** (Structure implemented, aggregation TODO)  
**Priority:** 🔴 **PRIORITY 1** - Core observability

---

## 1. Intent Overview

### Purpose
Retrieve execution metrics for a specified time range. Shows intent counts, success rates, execution times, and error rates.

### Intent Flow
```
[Admin requests execution metrics]
    ↓
[admin_get_execution_metrics intent]
    ↓
[Access control check (control_room view)]
    ↓
[ControlRoomService.get_execution_metrics()]
    ↓
[Aggregate from WAL and execution state]  (TODO)
    ↓
[Return execution_metrics artifact]
```

### Expected Observable Artifacts
- `execution_metrics` artifact with:
  - `time_range` - Time range requested
  - `timestamp` - ISO timestamp
  - `total_intents` - Total intent count
  - `success_rate` - Success percentage
  - `average_execution_time` - Average time in ms
  - `intent_distribution` - Counts by intent type
  - `error_rate` - Error percentage

---

## 2. Intent Parameters

### Optional Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `time_range` | `string` | Time range (e.g., "1h", "24h", "7d") | `"1h"` |

---

## 3. Intent Returns

### Success Response (MVP Structure)

```json
{
  "artifacts": {
    "execution_metrics": {
      "time_range": "1h",
      "timestamp": "2026-01-27T10:30:00Z",
      "total_intents": 0,
      "success_rate": 0.0,
      "average_execution_time": 0.0,
      "intent_distribution": {},
      "error_rate": 0.0
    }
  },
  "events": []
}
```

### Expected Response (Full Implementation)

```json
{
  "artifacts": {
    "execution_metrics": {
      "time_range": "1h",
      "timestamp": "2026-01-27T10:30:00Z",
      "total_executions": 150,
      "successful_executions": 142,
      "failed_executions": 8,
      "average_execution_time": 245.5,
      "p95_execution_time": 450.0,
      "p99_execution_time": 800.0,
      "throughput": 2.5,
      "error_rate": 0.053,
      "executions_by_type": {
        "ingest_file": 45,
        "parse_content": 42,
        "analyze_content": 30,
        "interpret_data": 20,
        "optimize_process": 13
      }
    }
  },
  "events": []
}
```

---

## 4. Implementation Details

### Service Location
`symphainy_platform/civic_systems/experience/admin_dashboard/services/control_room_service.py::ControlRoomService.get_execution_metrics`

### API Endpoint
`GET /api/admin/control-room/execution-metrics?time_range=1h`

### Current Implementation (MVP)
Returns basic structure with placeholder values:
```python
metrics = {
    "time_range": time_range,
    "timestamp": datetime.utcnow().isoformat(),
    "total_intents": 0,  # TODO: Aggregate from WAL
    "success_rate": 0.0,  # TODO: Calculate from execution results
    "average_execution_time": 0.0,  # TODO: Calculate from execution times
    "intent_distribution": {},  # TODO: Group by intent type
    "error_rate": 0.0  # TODO: Calculate from errors
}
```

### Phase 2 Implementation (TODO)
- Aggregate from Runtime WAL (Write-Ahead Log)
- Query State Surface for execution results
- Calculate statistics from historical data

---

## 5. Frontend Integration

### Frontend Usage (AdminAPIManager.ts)
```typescript
// AdminAPIManager.getExecutionMetrics()
async getExecutionMetrics(timeRange: string = '1h'): Promise<ExecutionMetrics> {
  const artifacts = await this._submitAdminIntent('admin_get_execution_metrics', { time_range: timeRange });
  return artifacts.execution_metrics;
}
```

### Expected Frontend Type
```typescript
export interface ExecutionMetrics {
  time_range: string;
  total_executions: number;
  successful_executions: number;
  failed_executions: number;
  average_execution_time: number;
  p95_execution_time: number;
  p99_execution_time: number;
  throughput: number;
  error_rate: number;
  executions_by_type: Record<string, number>;
}
```

---

## 6. Time Range Options

| Value | Description |
|-------|-------------|
| `1h` | Last 1 hour |
| `6h` | Last 6 hours |
| `24h` | Last 24 hours |
| `7d` | Last 7 days |
| `30d` | Last 30 days |

---

## 7. Contract Compliance

### Required Artifacts
- `execution_metrics` - Execution metrics object

### MVP Limitations
- Currently returns placeholder values
- Full aggregation requires WAL integration

---

**Last Updated:** January 27, 2026  
**Owner:** Control Tower Team  
**Status:** ⚠️ **MVP** (Structure implemented, aggregation TODO)
