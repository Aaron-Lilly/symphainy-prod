# Intent Contract: admin_get_composition_guide

**Intent:** admin_get_composition_guide  
**Intent Type:** `admin_get_composition_guide`  
**Journey:** Solution Composition (`control_tower_business`)  
**Solution:** Control Tower (Admin Dashboard)  
**View:** Business User View  
**Status:** ✅ **IMPLEMENTED**  
**Priority:** 🟡 **PRIORITY 2** - Business tools

---

## 1. Intent Overview

### Purpose
Retrieve the solution composition guide showing step-by-step instructions for creating solutions, available domains, and available intents.

---

## 2. Intent Returns

### Success Response

```json
{
  "artifacts": {
    "composition_guide": {
      "steps": [
        { "step": 1, "title": "Define Goals", "description": "Define what you want to achieve with this solution" },
        { "step": 2, "title": "Select Domains", "description": "Choose which domains (Content, Insights, Journey, Outcomes) to include" },
        { "step": 3, "title": "Configure Intents", "description": "Select which intents your solution will support" },
        { "step": 4, "title": "Set Context", "description": "Define constraints and risk level" },
        { "step": 5, "title": "Review & Register", "description": "Review your solution and register it with the platform" }
      ],
      "available_domains": ["content", "insights", "journey", "outcomes"],
      "available_intents": {
        "content": ["ingest_file", "parse_content", "extract_embeddings"],
        "insights": ["analyze_content", "interpret_data", "map_relationships"],
        "journey": ["optimize_process", "generate_sop", "create_blueprint"],
        "outcomes": ["synthesize_outcome", "generate_roadmap", "create_poc"]
      }
    }
  },
  "events": []
}
```

---

## 3. Implementation Details

### Service Location
`symphainy_platform/civic_systems/experience/admin_dashboard/services/business_user_view_service.py::BusinessUserViewService.get_composition_guide`

---

## 4. Frontend Integration

```typescript
async getCompositionGuide(): Promise<CompositionGuide> {
  const artifacts = await this._submitAdminIntent('admin_get_composition_guide');
  return artifacts.composition_guide;
}
```

---

**Last Updated:** January 27, 2026  
**Owner:** Control Tower Team  
**Status:** ✅ **IMPLEMENTED**
