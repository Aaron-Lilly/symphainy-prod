# Intent Contract: admin_submit_business_feature_request

**Intent:** admin_submit_business_feature_request  
**Intent Type:** `admin_submit_business_feature_request`  
**Journey:** Feature Requests (`control_tower_business`)  
**Solution:** Control Tower (Admin Dashboard)  
**View:** Business User View  
**Status:** ✅ **IMPLEMENTED**  
**Priority:** 🟢 **PRIORITY 3** - Business tools

---

## 1. Intent Overview

### Purpose
Submit a business feature request for platform capabilities. Unlike developer feature requests, these focus on business needs.

---

## 2. Intent Parameters

### Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `title` | `string` | Feature request title |
| `description` | `string` | Feature description |
| `business_need` | `string` | Business justification |

### Optional Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `priority` | `string` | Priority level (low, medium, high) |
| `metadata` | `object` | Additional metadata |

---

## 3. Intent Returns

### Success Response

```json
{
  "artifacts": {
    "business_feature_request": {
      "success": true,
      "feature_request_id": "feature_new_integration",
      "message": "Feature request submitted successfully",
      "feature_request": {
        "title": "Integration with SAP",
        "description": "Add ability to connect to SAP systems",
        "business_need": "Enable enterprise ERP integration"
      }
    }
  },
  "events": []
}
```

---

## 4. Implementation Details

### Service Location
`symphainy_platform/civic_systems/experience/admin_dashboard/services/business_user_view_service.py::BusinessUserViewService.submit_feature_request`

### Current Behavior
- Generates feature ID from title
- Stores request (in-memory for MVP)
- Phase 2: Full workflow integration

---

## 5. Frontend Integration

```typescript
async submitBusinessFeatureRequest(request: BusinessFeatureRequest): Promise<BusinessFeatureRequestResponse> {
  const artifacts = await this._submitAdminIntent('admin_submit_business_feature_request', request);
  return artifacts.business_feature_request;
}
```

---

**Last Updated:** January 27, 2026  
**Owner:** Control Tower Team  
**Status:** ✅ **IMPLEMENTED**
