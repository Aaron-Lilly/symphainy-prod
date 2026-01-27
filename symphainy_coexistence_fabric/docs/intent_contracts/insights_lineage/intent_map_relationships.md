# Intent Contract: map_relationships

**Intent:** map_relationships  
**Intent Type:** `map_relationships`  
**Journey:** Lineage & Relationships (`insights_lineage`)  
**Realm:** Insights Realm  
**Status:** ✅ **COMPREHENSIVE**  
**Priority:** 🔴 **PRIORITY 1** - Entity relationship mapping

---

## 1. Intent Overview

### Purpose
Discover and map entity relationships within parsed data. Identifies entities and their relationships to create a semantic graph of the data domain.

### Intent Flow
```
[User requests relationship mapping]
    ↓
[map_relationships intent]
    ↓
[DataAnalyzerService.map_relationships()]
    ↓
[Entity detection]
[Relationship inference]
[Graph construction]
    ↓
[Return relationships artifact]
```

### Expected Observable Artifacts
- `relationships` artifact with:
  - `entities` - Discovered entities with types and attributes
  - `relationships` - Entity relationships with confidence scores

---

## 2. Intent Parameters

### Required Parameters

| Parameter | Type | Description | Validation |
|-----------|------|-------------|------------|
| `parsed_file_id` | `string` | Parsed file identifier | Required |

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
    "relationships": {
      "entities": [
        {
          "name": "Policy",
          "type": "business_entity",
          "attributes": {
            "policy_number": "string",
            "effective_date": "date",
            "premium": "currency"
          }
        },
        {
          "name": "Customer",
          "type": "business_entity",
          "attributes": {
            "customer_id": "string",
            "name": "string",
            "address": "string"
          }
        },
        {
          "name": "Agent",
          "type": "business_entity",
          "attributes": {
            "agent_id": "string",
            "name": "string",
            "territory": "string"
          }
        }
      ],
      "relationships": [
        {
          "source": "Policy",
          "target": "Customer",
          "type": "belongs_to",
          "confidence": 0.92,
          "attributes": { "cardinality": "many-to-one" }
        },
        {
          "source": "Policy",
          "target": "Agent",
          "type": "sold_by",
          "confidence": 0.85,
          "attributes": { "cardinality": "many-to-one" }
        },
        {
          "source": "Customer",
          "target": "Agent",
          "type": "assigned_to",
          "confidence": 0.78,
          "attributes": { "cardinality": "many-to-one" }
        }
      ]
    },
    "parsed_file_id": "parsed_abc123"
  },
  "events": [
    {
      "type": "relationships_mapped",
      "parsed_file_id": "parsed_abc123"
    }
  ]
}
```

---

## 4. Idempotency

### Idempotency Key
`relationship_fingerprint = hash(parsed_file_id + tenant_id)`

### Behavior
- Same parsed file = same relationship mapping
- Deterministic entity and relationship detection
- Safe to retry

---

## 5. Implementation Details

### Handler Location
`symphainy_platform/realms/insights/orchestrators/insights_orchestrator.py::InsightsOrchestrator._handle_map_relationships`

### Key Implementation Steps
1. Validate `parsed_file_id` provided
2. Call `DataAnalyzerService.map_relationships()`
3. Service performs entity detection
4. Service infers relationships between entities
5. Service calculates confidence scores
6. Return relationships artifact

### Enabling Services
- **DataAnalyzerService:** `symphainy_platform/realms/insights/enabling_services/data_analyzer_service.py`

---

## 6. Frontend Integration

### Frontend Usage (InsightsAPIManager.ts)
```typescript
// InsightsAPIManager.mapRelationships()
const result = await insightsManager.mapRelationships(fileId);

if (result.success) {
  const relationships = result.relationships;
  // Display entity-relationship diagram
  // Show entities and their connections
}
```

### Expected Frontend Behavior
1. User requests relationship mapping
2. Frontend submits `map_relationships` intent
3. Track execution
4. Extract `relationships` from artifacts
5. Render entity-relationship diagram
6. Store in realm state

---

## 7. Error Handling

### Validation Errors
- `parsed_file_id` missing → `ValueError`

### Runtime Errors
- Parsed data not available → RuntimeError
- Entity detection failed → RuntimeError

---

## 8. Contract Compliance

### Required Artifacts
- `relationships` - Entity and relationship mapping

### Required Events
- `relationships_mapped` - With parsed_file_id

---

## 9. Cross-Reference Analysis

### Journey Contract Says
- `create_relationship_graph` - Create graph
- `visualize_relationships` - Visualize

### Implementation Does
- ✅ `map_relationships` discovers entities and relationships
- ✅ Returns structured graph data

### Frontend Expects
- ✅ Intent type: `map_relationships`
- ✅ Returns `relationships` with entities and relationships

---

**Last Updated:** January 27, 2026  
**Owner:** Insights Realm Solution Team  
**Status:** ✅ **COMPREHENSIVE**
