# Admin Dashboard

**Civic System:** Experience  
**Status:** ✅ Complete  
**Last Updated:** January 2026

---

## Overview

The Admin Dashboard provides three specialized views for platform management, development, and business users, with role-based access control and gated features.

---

## Views

### 1. Control Room View

**Purpose:** Platform observability and monitoring

**Access:** Admin, Demo User

**Capabilities:**
- **Platform Statistics** - Overall platform health and metrics
- **Execution Metrics** - Intent execution statistics and performance
- **Realm Health** - Health status of all registered realms
- **Solution Registry Status** - Status of registered solutions
- **System Health** - Infrastructure health monitoring
- **Real-time Monitoring** (gated) - Live execution monitoring

**API Endpoints:**
- `GET /api/admin/control-room/statistics` - Platform statistics
- `GET /api/admin/control-room/execution-metrics` - Execution metrics
- `GET /api/admin/control-room/realm-health` - Realm health
- `GET /api/admin/control-room/solution-registry` - Solution registry status
- `GET /api/admin/control-room/system-health` - System health

---

### 2. Developer View

**Purpose:** Platform SDK documentation and developer tools

**Access:** Admin, Demo User, Developer

**Capabilities:**
- **Platform SDK Documentation** - Complete SDK documentation
- **Code Examples** - Working code examples for common tasks
- **Patterns & Best Practices** - Architectural patterns and guidelines
- **Solution Builder Playground** (gated) - Interactive solution builder
- **Feature Submission** (gated - Coming Soon) - Submit feature requests

**API Endpoints:**
- `GET /api/admin/developer/docs` - Platform SDK documentation
- `GET /api/admin/developer/examples` - Code examples
- `GET /api/admin/developer/patterns` - Patterns and best practices
- `POST /api/admin/developer/playground/validate` (gated) - Validate solution
- `POST /api/admin/developer/features/submit` (gated) - Submit feature request

---

### 3. Business User View

**Purpose:** Solution composition and business tools

**Access:** Admin, Demo User, Business User

**Capabilities:**
- **Solution Composition Guide** - Step-by-step composition guide
- **Solution Builder** (gated) - Advanced solution builder
- **Solution Templates** (gated) - Pre-built solution templates
- **Feature Request System** - Submit business feature requests

**API Endpoints:**
- `GET /api/admin/business/composition-guide` - Composition guide
- `GET /api/admin/business/solution-templates` (gated) - Solution templates
- `POST /api/admin/business/solutions/from-template` (gated) - Create from template
- `POST /api/admin/business/features/submit` - Submit feature request

---

## Access Control

### Role-Based Access

| Role | Control Room | Developer View | Business View |
|------|--------------|----------------|---------------|
| Admin | ✅ Full Access | ✅ Full Access | ✅ Full Access |
| Demo User | ✅ Full Access | ✅ Full Access | ✅ Full Access |
| Developer | ❌ No Access | ✅ Full Access | ❌ No Access |
| Business User | ❌ No Access | ❌ No Access | ✅ Full Access |

### Gated Features

Some features require additional permissions:

- **Developer Playground** - Admin, Demo User only
- **Solution Templates** - Admin, Demo User only
- **Real-time Monitoring** - Admin, Demo User only
- **Advanced Metrics** - Admin, Demo User only
- **Alerting** - Admin only

---

## Use Cases

### 1. Platform Monitoring (Control Room)
**Scenario:** Monitoring platform health and performance.

**Use Case:** Use Control Room to:
- Monitor realm health
- Track execution metrics
- Identify performance issues
- View solution registry status

**Business Value:** Ensures platform reliability and performance.

---

### 2. Developer Onboarding (Developer View)
**Scenario:** Onboarding new developers to the platform.

**Use Case:** Use Developer View to:
- Access SDK documentation
- Review code examples
- Learn patterns and best practices
- Experiment in playground

**Business Value:** Accelerates developer productivity.

---

### 3. Solution Composition (Business View)
**Scenario:** Composing solutions for business needs.

**Use Case:** Use Business View to:
- Follow composition guide
- Use solution templates
- Create custom solutions
- Submit feature requests

**Business Value:** Enables business users to create solutions.

---

## Technical Details

### Implementation

The Admin Dashboard is implemented as part of the Experience Civic System:
- **AdminDashboardService** - Core service coordinating all views
- **ControlRoomService** - Platform observability
- **DeveloperViewService** - Developer tools and documentation
- **BusinessUserViewService** - Solution composition tools
- **AccessControlService** - Role-based access control

### Access Control

Access control uses:
- Feature flags for gated features
- Role-based permissions
- Security Guard SDK integration (for production)

---

## Related Capabilities

- [Solution Builder](../architecture/north_star.md#44-platform-sdk-civic-front-door) - Platform SDK for solution building
- [Realm SDK](../architecture/north_star.md#44-platform-sdk-civic-front-door) - SDK for realm development
- [Runtime API](../execution/api_contracts_frontend_integration.md) - Runtime execution API

---

## API Examples

### Get Platform Statistics

```python
GET /api/admin/control-room/statistics
Headers: Authorization: Bearer <token>

Response:
{
  "timestamp": "2026-01-15T10:00:00Z",
  "realms": {
    "total": 4,
    "registered": ["content", "insights", "journey", "outcomes"]
  },
  "solutions": {
    "total": 5,
    "active": 3
  },
  "system_health": "healthy"
}
```

### Get Documentation

```python
GET /api/admin/developer/docs?section=realm_sdk
Headers: Authorization: Bearer <token>

Response:
{
  "sections": {
    "realm_sdk": {
      "title": "Realm SDK",
      "content": "How to implement realms using RealmBase..."
    }
  }
}
```

---

**See Also:**
- [Experience Plane](../architecture/north_star.md#42-experience-exposure--interaction)
- [Platform SDK](../architecture/north_star.md#44-platform-sdk-civic-front-door)
- [API Contracts](../execution/api_contracts_frontend_integration.md)
