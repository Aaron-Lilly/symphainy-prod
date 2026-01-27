# Control Tower (Admin Dashboard) Intent Analysis

**Last Updated:** January 27, 2026  
**Purpose:** Cross-reference analysis between journey contracts, backend implementations, and frontend expectations.

---

## 1. Key Finding

**The Control Tower is implemented as the Admin Dashboard** in `civic_systems/experience/admin_dashboard/`. It provides three views with comprehensive backend services. The frontend has migrated to intent-based API.

### Implementation Location
- **Backend:** `symphainy_platform/civic_systems/experience/admin_dashboard/`
- **Frontend:** `symphainy-frontend/shared/managers/AdminAPIManager.ts`

---

## 2. Architecture Overview

### Three Views

| View | Purpose | Backend Service |
|------|---------|-----------------|
| **Control Room** | Platform observability | `ControlRoomService` |
| **Developer View** | SDK docs, playground, patterns | `DeveloperViewService` |
| **Business User View** | Solution composition, templates | `BusinessUserViewService` |

### Backend Structure
```
civic_systems/experience/admin_dashboard/
├── admin_dashboard_service.py      # Main coordinator
├── api/
│   ├── control_room.py             # FastAPI routes
│   ├── developer_view.py           # FastAPI routes
│   └── business_user_view.py       # FastAPI routes
└── services/
    ├── control_room_service.py     # Platform observability
    ├── developer_view_service.py   # Developer tools
    ├── business_user_view_service.py # Business tools
    └── access_control_service.py   # Access control
```

---

## 3. Frontend Expectations (16 Intents)

### Control Room View (5 intents)

| Frontend Method | Intent Type | Backend Service Method |
|-----------------|-------------|------------------------|
| `getPlatformStatistics()` | `admin_get_platform_statistics` | `control_room_service.get_platform_statistics()` |
| `getExecutionMetrics()` | `admin_get_execution_metrics` | `control_room_service.get_execution_metrics()` |
| `getRealmHealth()` | `admin_get_realm_health` | `control_room_service.get_realm_health()` |
| `getSolutionRegistryStatus()` | `admin_get_solution_registry_status` | `control_room_service.get_solution_registry_status()` |
| `getSystemHealth()` | `admin_get_system_health` | `control_room_service.get_system_health()` |

### Developer View (6 intents)

| Frontend Method | Intent Type | Backend Service Method |
|-----------------|-------------|------------------------|
| `getDocumentation()` | `admin_get_documentation` | `developer_view_service.get_documentation()` |
| `getCodeExamples()` | `admin_get_code_examples` | `developer_view_service.get_code_examples()` |
| `getPatterns()` | `admin_get_patterns` | `developer_view_service.get_patterns()` |
| `validateSolution()` | `admin_validate_solution` | `developer_view_service.validate_solution()` |
| `previewSolution()` | `admin_preview_solution` | `developer_view_service.preview_solution()` |
| `submitFeatureRequest()` | `admin_submit_feature_request` | `developer_view_service.submit_feature_request()` |

### Business User View (5 intents)

| Frontend Method | Intent Type | Backend Service Method |
|-----------------|-------------|------------------------|
| `getCompositionGuide()` | `admin_get_composition_guide` | `business_user_view_service.get_composition_guide()` |
| `getSolutionTemplates()` | `admin_get_solution_templates` | `business_user_view_service.get_solution_templates()` |
| `composeSolution()` | `admin_compose_solution` | `business_user_view_service.compose_solution()` |
| `registerSolution()` | `admin_register_solution` | `business_user_view_service.register_solution()` |
| `submitBusinessFeatureRequest()` | `admin_submit_business_feature_request` | `business_user_view_service.submit_feature_request()` |

---

## 4. Journey Contract vs Implementation Gap

### Journey Contracts (Placeholder Templates)
The journey contracts in `control_tower_solution/` have placeholder intents:
- `get_platform_statistics`
- `get_execution_metrics`
- `get_realm_health`
- `get_solution_registry_status`

### Implementation Has
Intent names are prefixed with `admin_`:
- `admin_get_platform_statistics`
- `admin_get_execution_metrics`
- `admin_get_realm_health`
- `admin_get_solution_registry_status`
- `admin_get_system_health`
- Plus 11 more for Developer and Business views

### Recommended Naming Convention
Use `admin_` prefix for all Control Tower/Admin Dashboard intents to:
1. Distinguish from realm-level intents
2. Enable access control filtering
3. Maintain clear separation of concerns

---

## 5. Backend Service Capabilities

### ControlRoomService

| Method | Status | Notes |
|--------|--------|-------|
| `get_platform_statistics()` | ✅ Implemented | Returns realm count, solution count, system health |
| `get_execution_metrics()` | ⚠️ MVP | Returns structure, TODO: aggregate from WAL |
| `get_realm_health()` | ✅ Implemented | Returns realm status from Runtime/Registry |
| `get_solution_registry_status()` | ✅ Implemented | Returns solution status from registry |
| `get_system_health()` | ✅ Implemented | Returns runtime and infrastructure health |

### DeveloperViewService

| Method | Status | Notes |
|--------|--------|-------|
| `get_documentation()` | ✅ Implemented | Returns SDK documentation structure |
| `get_code_examples()` | ✅ Implemented | Returns code examples by category |
| `get_patterns()` | ✅ Implemented | Returns patterns and best practices |
| `validate_solution()` | ✅ Implemented | Uses SolutionBuilder to validate config |
| `preview_solution()` | ✅ Implemented | Returns solution preview structure |
| `submit_feature_request()` | ⚠️ Gated | Returns "Coming Soon" for MVP |

### BusinessUserViewService

| Method | Status | Notes |
|--------|--------|-------|
| `get_composition_guide()` | ✅ Implemented | Returns step-by-step guide |
| `get_solution_templates()` | ✅ Implemented | Returns pre-built templates |
| `compose_solution()` | ✅ Implemented | Uses SolutionBuilder |
| `register_solution()` | ✅ Implemented | Registers via SolutionRegistry |
| `submit_feature_request()` | ✅ Implemented | Stores feature request |

---

## 6. Access Control

All admin endpoints require access control check:
```python
has_access = await admin_service.check_access(user_id, view, feature)
```

### Access Levels
- `control_room` - Platform operators
- `developer` - Developers (gated features)
- `business` - Business users (gated features)

---

## 7. Data Sources

| Data | Source | Notes |
|------|--------|-------|
| Realm health | Runtime client / Realm registry | Real-time |
| Solution status | Solution registry | Real-time |
| Execution metrics | WAL (TODO) | MVP: placeholder |
| Infrastructure health | Public Works adapters | Health checks |

---

## 8. Intent Contract Organization

### Recommended Structure
```
control_tower_monitoring/
├── intent_admin_get_platform_statistics.md
├── intent_admin_get_execution_metrics.md
├── intent_admin_get_realm_health.md
├── intent_admin_get_solution_registry_status.md
└── intent_admin_get_system_health.md

control_tower_developer/
├── intent_admin_get_documentation.md
├── intent_admin_get_code_examples.md
├── intent_admin_get_patterns.md
├── intent_admin_validate_solution.md
├── intent_admin_preview_solution.md
└── intent_admin_submit_feature_request.md

control_tower_business/
├── intent_admin_get_composition_guide.md
├── intent_admin_get_solution_templates.md
├── intent_admin_compose_solution.md
├── intent_admin_register_solution.md
└── intent_admin_submit_business_feature_request.md
```

---

## 9. Key Decisions

| Decision | Rationale |
|----------|-----------|
| Keep `admin_` prefix | Distinguishes from realm intents, enables filtering |
| Update journey contracts | Reflect actual implementation |
| Create comprehensive intent contracts | Document all 16 intents |
| Note MVP limitations | Execution metrics has TODO items |

---

## 10. Implementation Notes

### Frontend Intent Submission
Frontend uses intent-based API pattern:
```typescript
private async _submitAdminIntent(
  intentType: string,
  parameters: Record<string, any> = {}
): Promise<any> {
  const platformState = this.getPlatformState();
  validateSession(platformState, `admin operation: ${intentType}`);
  const execution = await platformState.submitIntent(intentType, parameters);
  // Wait for execution and return artifacts
}
```

### Backend API Routes (Current)
Backend currently has FastAPI routes:
```
GET /api/admin/control-room/statistics
GET /api/admin/control-room/execution-metrics
GET /api/admin/control-room/realm-health
GET /api/admin/control-room/solution-registry
GET /api/admin/control-room/system-health
```

### Integration Pattern
The Experience Plane needs to route admin intents to the appropriate service methods. This could be:
1. An Admin orchestrator that handles `admin_*` intents
2. Direct service calls from Experience Plane intent handler

---

**Last Updated:** January 27, 2026  
**Owner:** Control Tower / Admin Dashboard Team
