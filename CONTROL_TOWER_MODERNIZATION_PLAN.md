# Control Tower Modernization Plan

**Date:** January 29, 2026  
**Goal:** Transform Admin Dashboard into thin persona-aware layer over Control Tower intents

---

## Executive Summary

The Admin Dashboard currently implements Control Tower functionality using direct service calls. We will modernize it to submit intents to the Control Tower capability, aligning with our platform architecture where **everything flows through intents**.

```
BEFORE: Frontend → Admin Dashboard Service → Direct Registry Queries
AFTER:  Frontend → Admin Dashboard API → Intent Submit → Control Tower Capability
```

---

## Part 1: Team A Requirements (Infrastructure)

### 1.1 No Blocking Dependencies

Good news: **Team A has no blocking work for this modernization**. The infrastructure we need already exists:

| Requirement | Status | Notes |
|-------------|--------|-------|
| Intent submission endpoint | ✅ Exists | `/api/intent/submit` |
| Control Tower capability | ✅ Exists | 9 intent services ready |
| State Surface | ✅ Exists | For metrics aggregation |
| Public Works | ✅ Exists | For infrastructure access |

### 1.2 Future Enhancements (Non-Blocking)

These would enhance Control Tower but are **not required for MVP**:

| Enhancement | Priority | Description |
|-------------|----------|-------------|
| **Metrics Abstraction** | P2 | OpenTelemetry integration for real execution metrics |
| **WAL Query Interface** | P2 | Query WAL for intent history, execution stats |
| **Real-time Streaming** | P3 | WebSocket subscription for live metrics |
| **Alerting Protocol** | P3 | Protocol for health alerts and notifications |

### 1.3 Team A Coordination Points

- **Inform Team A** that Control Tower will be the primary observability interface
- **Request** that future telemetry work expose metrics via Control Tower intents
- **Align** on WAL query patterns when Team A implements execution history

---

## Part 2: Team B Work (Our Implementation)

### Phase 1: Thin Layer Conversion (Core Work)

**Goal:** Convert Admin Dashboard API to submit intents instead of direct service calls.

#### 1.1 Control Room API Conversion

| Endpoint | Current | New Intent |
|----------|---------|------------|
| `GET /api/admin/control-room/statistics` | `control_room_service.get_platform_statistics()` | `get_platform_statistics` |
| `GET /api/admin/control-room/execution-metrics` | `control_room_service.get_execution_metrics()` | `get_execution_metrics` |
| `GET /api/admin/control-room/realm-health` | `control_room_service.get_realm_health()` | `get_realm_health` |
| `GET /api/admin/control-room/solution-registry` | `control_room_service.get_solution_registry_status()` | `list_solutions` |
| `GET /api/admin/control-room/system-health` | `control_room_service.get_system_health()` | `get_system_health` |

**Implementation:**
```python
# BEFORE
@router.get("/statistics")
async def get_platform_statistics(admin_service: AdminDashboardService = Depends(...)):
    return await admin_service.control_room_service.get_platform_statistics()

# AFTER
@router.get("/statistics")
async def get_platform_statistics(
    request: Request,
    session_id: str = Query(...),
    tenant_id: str = Query(...)
):
    result = await submit_control_tower_intent(
        request=request,
        intent_type="get_platform_statistics",
        session_id=session_id,
        tenant_id=tenant_id,
        parameters={}
    )
    return result
```

#### 1.2 Developer View API Conversion

| Endpoint | Current | New Intent |
|----------|---------|------------|
| `GET /api/admin/developer/documentation` | `developer_view_service.get_documentation()` | `get_documentation` |
| `GET /api/admin/developer/code-examples` | `developer_view_service.get_code_examples()` | `get_code_examples` |
| `GET /api/admin/developer/patterns` | `developer_view_service.get_patterns()` | `get_patterns` |
| `POST /api/admin/developer/validate-solution` | `developer_view_service.validate_solution()` | `validate_solution` |

#### 1.3 Business User View API Conversion

| Endpoint | Current | New Intent |
|----------|---------|------------|
| `GET /api/admin/business/templates` | `business_user_view_service.get_solution_templates()` | `list_solutions` (with filter) |
| `POST /api/admin/business/compose` | `business_user_view_service.compose_solution()` | `compose_solution` (new) |
| `GET /api/admin/business/solutions` | `business_user_view_service.list_solutions()` | `list_solutions` |

### Phase 2: New Control Tower Intent Services

**Goal:** Add missing intent services to Control Tower capability.

| New Intent Service | Purpose |
|-------------------|---------|
| `GetExecutionMetricsService` | Aggregate execution metrics from WAL/State |
| `ComposeSolutionService` | Create solution from configuration |
| `GetSolutionTemplatesService` | Return available solution templates |

### Phase 3: Cleanup

**Goal:** Remove deprecated code after conversion.

| Action | Files |
|--------|-------|
| Delete | `admin_dashboard/services/control_room_service.py` |
| Delete | `admin_dashboard/services/developer_view_service.py` |
| Delete | `admin_dashboard/services/business_user_view_service.py` |
| Simplify | `admin_dashboard/admin_dashboard_service.py` |
| Keep | `admin_dashboard/services/access_control_service.py` (still needed) |

---

## Part 3: Team C Requirements (Frontend)

### 3.1 No Blocking Changes Required

The frontend API calls don't need to change initially. The Admin Dashboard API endpoints remain the same:
- `GET /api/admin/control-room/statistics`
- `GET /api/admin/developer/documentation`
- etc.

The change is **internal** - how the backend handles these requests.

### 3.2 Recommended Frontend Enhancements (Non-Blocking)

| Enhancement | Priority | Description |
|-------------|----------|-------------|
| **Add session/tenant params** | P1 | Pass `session_id` and `tenant_id` to admin endpoints |
| **Handle async results** | P2 | Support polling for long-running operations |
| **Real-time updates** | P3 | WebSocket subscription for live metrics |

### 3.3 Future Frontend Opportunities

Once Control Tower is intent-based, the frontend could:
- Use the same `ExperiencePlaneClient.submitIntent()` for admin operations
- Get audit trail of admin actions
- Support multi-tenant admin views

---

## Implementation Order

### Sprint 1: Core Conversion (Today)

```
1. Create helper function for Control Tower intent submission
2. Convert Control Room API endpoints (5 endpoints)
3. Convert Developer View API endpoints (4 endpoints)  
4. Convert Business User View API endpoints (3 endpoints)
5. Test E2E with existing frontend
```

### Sprint 2: New Intents + Cleanup (Tomorrow)

```
1. Add GetExecutionMetricsService to Control Tower
2. Add ComposeSolutionService to Control Tower
3. Add GetSolutionTemplatesService to Control Tower
4. Delete deprecated service files
5. Update tests
```

### Sprint 3: Enhancement (Future)

```
1. Add real metrics aggregation (with Team A)
2. Add WebSocket streaming for live updates
3. Frontend updates for enhanced experience
```

---

## Success Criteria

| Criteria | Measure |
|----------|---------|
| **All admin endpoints work** | Existing frontend functions unchanged |
| **Intents logged** | Admin actions visible in WAL |
| **No direct registry access** | Admin Dashboard API has no imports from registries |
| **Tests pass** | Existing tests continue to pass |

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| **Breaking frontend** | Keep same API contract, change only implementation |
| **Missing intent services** | Create any missing services before removing old code |
| **Performance regression** | Intent submission adds latency; acceptable for admin ops |

---

## File Changes Summary

### Modified Files
- `admin_dashboard/api/control_room.py` - Convert to intent submission
- `admin_dashboard/api/developer_view.py` - Convert to intent submission
- `admin_dashboard/api/business_user_view.py` - Convert to intent submission
- `admin_dashboard/admin_dashboard_service.py` - Simplify to just access control

### New Files
- `capabilities/control_tower/intent_services/get_execution_metrics_service.py`
- `capabilities/control_tower/intent_services/compose_solution_service.py`
- `capabilities/control_tower/intent_services/get_solution_templates_service.py`

### Deleted Files (After Conversion)
- `admin_dashboard/services/control_room_service.py`
- `admin_dashboard/services/developer_view_service.py`
- `admin_dashboard/services/business_user_view_service.py`

---

## Conclusion

This modernization aligns the Admin Dashboard with our platform architecture where everything flows through intents. The work is primarily **Team B** (our implementation), with **no blocking dependencies** on Team A or Team C.

The frontend continues to work unchanged while we improve the backend architecture.
