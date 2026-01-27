# Intent Contract: admin_get_solution_templates

**Intent:** admin_get_solution_templates  
**Intent Type:** `admin_get_solution_templates`  
**Journey:** Solution Composition (`control_tower_business`)  
**Solution:** Control Tower (Admin Dashboard)  
**View:** Business User View  
**Status:** ✅ **IMPLEMENTED**  
**Priority:** 🟡 **PRIORITY 2** - Business tools

---

## 1. Intent Overview

### Purpose
Retrieve available solution templates for business users to create solutions from pre-built configurations.

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
    "solution_templates": {
      "templates": {
        "content_insights": {
          "title": "Content + Insights Solution",
          "description": "Solution combining content processing with insights generation",
          "config": {
            "context": {
              "goals": ["Process content", "Generate insights"],
              "constraints": [],
              "risk": "Low"
            },
            "domain_service_bindings": [
              { "domain": "content", "system_name": "symphainy_platform", "adapter_type": "internal_adapter" },
              { "domain": "insights", "system_name": "symphainy_platform", "adapter_type": "internal_adapter" }
            ],
            "supported_intents": ["ingest_file", "parse_content", "analyze_content", "interpret_data"]
          }
        },
        "full_pillar": {
          "title": "Full Pillar Solution",
          "description": "Solution using all pillars: Content, Insights, Journey, Outcomes",
          "config": { ... }
        }
      },
      "count": 2
    }
  },
  "events": []
}
```

---

## 4. Available Templates

| Template ID | Title | Domains | Complexity |
|-------------|-------|---------|------------|
| `content_insights` | Content + Insights Solution | content, insights | Low |
| `full_pillar` | Full Pillar Solution | content, insights, journey, outcomes | Medium |

---

## 5. Implementation Details

### Service Location
`symphainy_platform/civic_systems/experience/admin_dashboard/services/business_user_view_service.py::BusinessUserViewService.get_solution_templates`

---

## 6. Frontend Integration

### Frontend Usage
```typescript
async getSolutionTemplates(): Promise<SolutionTemplates> {
  const artifacts = await this._submitAdminIntent('admin_get_solution_templates');
  return artifacts.solution_templates;
}
```

---

**Last Updated:** January 27, 2026  
**Owner:** Control Tower Team  
**Status:** ✅ **IMPLEMENTED**
