# Intent Contract: admin_get_documentation

**Intent:** admin_get_documentation  
**Intent Type:** `admin_get_documentation`  
**Journey:** Developer Documentation (`control_tower_developer`)  
**Solution:** Control Tower (Admin Dashboard)  
**View:** Developer View  
**Status:** ✅ **IMPLEMENTED**  
**Priority:** 🟡 **PRIORITY 2** - Developer tools

---

## 1. Intent Overview

### Purpose
Retrieve Platform SDK documentation including architecture overview, SDK guides, and API documentation.

### Expected Observable Artifacts
- `documentation` artifact with:
  - `sections` - Documentation sections (architecture, SDKs, etc.)

---

## 2. Intent Parameters

### Optional Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `section` | `string` | Specific section to retrieve | All sections |

---

## 3. Intent Returns

### Success Response

```json
{
  "artifacts": {
    "documentation": {
      "sections": {
        "architecture": {
          "title": "Architecture Overview",
          "content": "Platform architecture: Runtime, Civic Systems, Solutions, Foundations"
        },
        "solution_pattern": {
          "title": "Solution Pattern",
          "content": "How to build solutions using BaseSolution: compose journeys, expose SOA APIs, integrate with MCP server"
        },
        "journey_orchestrators": {
          "title": "Journey Orchestrators",
          "content": "How to implement journey orchestrators that handle specific workflows with standardized results"
        },
        "smart_city_sdk": {
          "title": "Smart City SDK",
          "content": "Smart City SDK: Security Guard, Traffic Cop, Post Office - infrastructure abstractions"
        },
        "agentic_sdk": {
          "title": "Agentic SDK",
          "content": "How to implement agents using AgentBase and collaboration patterns"
        },
        "public_works": {
          "title": "Public Works",
          "content": "Public Works pattern: Adapters, Abstractions, Protocols for infrastructure access"
        },
        "mcp_integration": {
          "title": "MCP Integration",
          "content": "How to expose solution journeys as MCP tools for AI agent consumption"
        }
      }
    }
  },
  "events": []
}
```

---

## 4. Implementation Details

### Service Location
`symphainy_platform/civic_systems/experience/admin_dashboard/services/developer_view_service.py::DeveloperViewService.get_documentation`

### API Endpoint
`GET /api/admin/developer/documentation?section=architecture`

---

## 5. Frontend Integration

### Frontend Usage
```typescript
async getDocumentation(section?: string): Promise<Documentation> {
  const artifacts = await this._submitAdminIntent('admin_get_documentation', { section });
  return artifacts.documentation;
}
```

---

**Last Updated:** January 27, 2026  
**Owner:** Control Tower Team  
**Status:** ✅ **IMPLEMENTED**
