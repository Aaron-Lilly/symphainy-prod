# Intent Contract: show_solution_catalog

**Intent:** show_solution_catalog  
**Intent Type:** `show_solution_catalog`  
**Journey:** Platform Introduction (`journey_coexistence_introduction`)  
**Solution:** Coexistence Solution  
**Status:** ENHANCED  
**Priority:** PRIORITY 1

---

## 1. Intent Overview

### Purpose
Displays the catalog of available solutions on the Symphainy platform. Users can browse pre-built solutions, understand their capabilities, and select one to start their journey. The catalog includes solution templates, use cases, and recommended starting points.

### Intent Flow
```
[User requests solution catalog]
    ↓
[Fetch available solutions from Solution Registry]
    ↓
[Filter based on user context and permissions]
    ↓
[Generate catalog artifact with categorized solutions]
    ↓
[Return catalog with navigation options]
```

### Expected Observable Artifacts
- `solution_catalog` - Categorized list of available solutions

---

## 2. Intent Parameters

### Required Parameters

| Parameter | Type | Description | Validation |
|-----------|------|-------------|------------|
| `user_context` | `object` | User context information | Must include session_id |

### Optional Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `category` | `string` | Filter by category | null (show all) |
| `user_goals` | `string` | User goals for recommendations | null |
| `show_templates` | `boolean` | Include solution templates | true |
| `show_featured` | `boolean` | Highlight featured solutions | true |

### Context Metadata (from ExecutionContext)

| Metadata Key | Type | Description | Source |
|--------------|------|-------------|--------|
| `tenant_id` | `string` | Tenant identifier | Runtime |
| `session_id` | `string` | Session identifier | Runtime |

---

## 3. Intent Returns

### Success Response

```json
{
  "artifacts": {
    "catalog": {
      "result_type": "solution_catalog",
      "semantic_payload": {
        "catalog_version": "2.0",
        "total_solutions": 5,
        "categories": ["data", "analytics", "automation", "governance"]
      },
      "renderings": {
        "featured_solutions": [
          {
            "solution_id": "content_solution",
            "name": "Content Solution",
            "description": "Upload, parse, and embed content for AI-powered analysis",
            "category": "data",
            "pillars": ["content"],
            "complexity": "low",
            "is_featured": true
          }
        ],
        "solutions_by_category": {
          "data": [
            {
              "solution_id": "content_solution",
              "name": "Content Solution",
              "description": "File processing and content management",
              "journeys": ["file_upload", "parsing", "embedding"]
            }
          ],
          "analytics": [
            {
              "solution_id": "insights_solution",
              "name": "Insights Solution",
              "description": "Business analysis and data quality",
              "journeys": ["business_analysis", "data_quality"]
            }
          ],
          "automation": [
            {
              "solution_id": "journey_solution",
              "name": "Journey Solution",
              "description": "Workflow and SOP management",
              "journeys": ["workflow_sop", "coexistence_analysis"]
            }
          ],
          "governance": [
            {
              "solution_id": "control_tower",
              "name": "Control Tower",
              "description": "Platform monitoring and management",
              "journeys": ["monitoring", "solution_management"]
            }
          ]
        },
        "templates": [
          {
            "template_id": "coexistence_starter",
            "name": "Coexistence Starter",
            "description": "Begin your coexistence journey with guided analysis",
            "recommended_for": "New users exploring coexistence concepts"
          }
        ],
        "recommended_starting_point": {
          "solution_id": "content_solution",
          "reason": "Most users start by uploading content for analysis"
        }
      }
    }
  },
  "events": [
    {
      "type": "solution_catalog_displayed",
      "solution_count": 5,
      "categories_shown": 4
    }
  ]
}
```

---

## 4. Artifact Registration

### State Surface Registration
- **Artifact ID:** `catalog_{session_id}_{timestamp}`
- **Artifact Type:** `"solution_catalog"`
- **Lifecycle State:** `"READY"`
- **Produced By:** `{ intent: "show_solution_catalog", execution_id: "<execution_id>" }`
- **Materializations:** In-memory (ephemeral)

### Artifact Index Registration
- Not indexed (ephemeral catalog view)

---

## 5. Idempotency

### Idempotency Key
```
idempotency_key = hash(session_id + category + "show_solution_catalog")
```

### Scope
- Per session + category filter

### Behavior
- Returns cached catalog for same session/filter within TTL (5 minutes)

---

## 6. Implementation Details

### Handler Location
`symphainy_platform/solutions/coexistence/journeys/introduction_journey.py`

### Key Implementation Steps
1. Query Solution Registry for available solutions
2. Filter by category if specified
3. Apply user permissions/tenant restrictions
4. Generate recommendations based on user_goals
5. Structure catalog with featured solutions first

### Dependencies
- **Public Works:** registry_abstraction
- **State Surface:** solution_registry
- **Runtime:** ExecutionContext

---

## 7. Frontend Integration

### Frontend Usage
```typescript
const catalog = await platformState.submitIntent({
  intent_type: "show_solution_catalog",
  parameters: {
    user_context: { session_id },
    show_featured: true,
    user_goals: userGoals
  }
});

// Display categorized solutions
const solutions = catalog.artifacts?.catalog?.renderings;
setSolutionsByCategory(solutions.solutions_by_category);
setFeaturedSolutions(solutions.featured_solutions);
```

### Expected Frontend Behavior
1. Display featured solutions prominently
2. Show categorized solution cards
3. Enable filtering by category
4. Show "Start Journey" button for each solution

---

## 8. Error Handling

### Validation Errors
- Invalid category → Return all solutions with warning

### Runtime Errors
- Registry unavailable → Return cached/default catalog

---

## 9. Testing & Validation

### Happy Path
1. Request solution catalog
2. Verify all active solutions returned
3. Verify categorization is correct
4. Verify featured solutions highlighted

### Boundary Violations
- Unknown category → Return empty category with error message

---

## 10. Contract Compliance

### Required Artifacts
- `catalog` - Required (solution_catalog type)

### Required Events
- `solution_catalog_displayed` - Required

### Lifecycle State
- Always READY (ephemeral)

---

**Last Updated:** January 27, 2026  
**Owner:** Coexistence Solution Team  
**Status:** ENHANCED
