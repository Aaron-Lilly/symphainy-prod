# Intent Contract: interpret_data_self_discovery

**Intent:** interpret_data_self_discovery  
**Intent Type:** `interpret_data_self_discovery`  
**Journey:** Data Interpretation (`insights_data_interpretation`)  
**Realm:** Insights Realm  
**Status:** ✅ **COMPREHENSIVE**  
**Priority:** 🔴 **PRIORITY 1** - Core interpretation capability

---

## 1. Intent Overview

### Purpose
Discover semantic meaning in parsed data without a guide. Uses self-discovery algorithms to identify entities, relationships, and patterns. Promotes interpretation to Record of Fact for persistent meaning.

### Intent Flow
```
[User requests self-discovery interpretation]
    ↓
[interpret_data_self_discovery intent]
    ↓
[Get embeddings from ArangoDB via chunk-based pattern]
    ↓
[SemanticSelfDiscoveryService.discover_semantics()]
    ↓
[Track interpretation in Supabase for lineage]
    ↓
[Promote to Record of Fact via Data Steward SDK]
    ↓
[Return discovery artifact]
```

### Expected Observable Artifacts
- `discovery` artifact with:
  - `interpretation_type` - "self_discovery"
  - `entities` - Discovered entities
  - `relationships` - Discovered relationships
  - `confidence_score` - Discovery confidence
  - `coverage_score` - Data coverage
  - `patterns` - Identified patterns
  - `semantic_summary` - Human-readable summary

---

## 2. Intent Parameters

### Required Parameters

| Parameter | Type | Description | Validation |
|-----------|------|-------------|------------|
| `parsed_file_id` | `string` | Parsed file identifier | Required (or `parsed_result_id`) |

### Optional Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `parsed_result_id` | `string` | Alias for parsed_file_id | Same as parsed_file_id |
| `discovery_options` | `object` | Discovery configuration | `{}` |

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
    "discovery": {
      "interpretation_type": "self_discovery",
      "entities": [
        {
          "name": "Policy",
          "type": "business_entity",
          "attributes": {
            "policy_number": "string",
            "effective_date": "date",
            "premium": "currency"
          },
          "confidence": 0.92
        }
      ],
      "relationships": [
        {
          "source": "Policy",
          "target": "Customer",
          "type": "belongs_to",
          "confidence": 0.85
        }
      ],
      "patterns": [
        {
          "name": "policy_lifecycle",
          "description": "Policy state transitions",
          "confidence": 0.78
        }
      ],
      "confidence_score": 0.85,
      "coverage_score": 0.92,
      "semantic_summary": "Insurance policy data with customer relationships"
    },
    "parsed_file_id": "parsed_abc123"
  },
  "events": [
    {
      "type": "semantics_discovered",
      "parsed_file_id": "parsed_abc123"
    }
  ]
}
```

---

## 4. Artifact Registration

### State Surface Updates
- Discovery artifact stored in execution state

### Lineage Tracking
- Interpretation tracked in Supabase `interpretations` table
- Links: file_id, parsed_result_id, embedding_id
- Includes confidence_score and coverage_score

### Record of Fact Promotion
- Interpretations are persistent meaning (Records of Fact)
- Promoted immediately via Data Steward SDK
- `record_type`: "interpretation"
- `promotion_reason`: "Interpretation created - persistent meaning"

---

## 5. Idempotency

### Idempotency Key
`discovery_fingerprint = hash(parsed_file_id + tenant_id)`

### Behavior
- Same parsed file = same discovery result
- Self-discovery is deterministic given same embeddings
- Safe to retry

---

## 6. Implementation Details

### Handler Location
`symphainy_platform/realms/insights/orchestrators/insights_orchestrator.py::InsightsOrchestrator._handle_self_discovery`

### Key Implementation Steps
1. Accept both `parsed_file_id` and `parsed_result_id` (aliases)
2. Get embeddings from ArangoDB via chunk-based pattern:
   - Get parsed file
   - Create deterministic chunks
   - Query embeddings by chunk_id
3. Call `SemanticSelfDiscoveryService.discover_semantics()`
4. Track interpretation in Supabase via `_track_interpretation()`
5. Promote to Record of Fact via Data Steward SDK
6. Return discovery artifact

### Enabling Services
- **SemanticSelfDiscoveryService:** `symphainy_platform/realms/insights/enabling_services/semantic_self_discovery_service.py`

### Chunk-Based Pattern (Phase 3)
```python
# 1. Get parsed file
parsed_file = await file_parser_service.get_parsed_file(...)

# 2. Create deterministic chunks
chunks = await deterministic_chunking_service.create_chunks(...)

# 3. Query embeddings by chunk_id (not parsed_file_id)
chunk_ids = [chunk.chunk_id for chunk in chunks]
embeddings = await semantic_data.get_semantic_embeddings(
    filter_conditions={"chunk_id": {"$in": chunk_ids}}
)
```

---

## 7. Frontend Integration

### Frontend Usage (InsightsAPIManager.ts)
```typescript
// InsightsAPIManager.interpretDataSelfDiscovery()
const result = await insightsManager.interpretDataSelfDiscovery(
  parsedFileId,
  { include_patterns: true }
);

if (result.success) {
  const interpretation = result.interpretation;
  // Display entities, relationships, patterns
}
```

### Expected Frontend Behavior
1. User requests interpretation of parsed data
2. Frontend submits `interpret_data_self_discovery` intent
3. Track execution via `trackExecution()`
4. Wait for completion
5. Extract `discovery` from artifacts
6. Display entities, relationships, patterns
7. Store in realm state

---

## 8. Error Handling

### Validation Errors
- Neither `parsed_file_id` nor `parsed_result_id` provided → `ValueError`

### Runtime Errors
- Embeddings not available → Discovery with limited results
- Self-discovery service error → RuntimeError

---

## 9. Testing & Validation

### Happy Path
1. Parsed file with embeddings exists
2. Submit `interpret_data_self_discovery` intent
3. Self-discovery identifies entities and relationships
4. Interpretation tracked and promoted to Record of Fact
5. Return discovery artifact

---

## 10. Contract Compliance

### Required Artifacts
- `discovery` - Self-discovery interpretation result

### Required Events
- `semantics_discovered` - With parsed_file_id

---

## 11. Cross-Reference Analysis

### Journey Contract Says
- `initiate_guided_discovery` - Start guided discovery
- `explore_relationships` - Explore relationships
- `identify_patterns` - Identify patterns

### Implementation Does
- ✅ `interpret_data_self_discovery` handles ungided discovery
- ✅ Identifies entities, relationships, and patterns in one intent
- ✅ Promotes to Record of Fact

### Frontend Expects
- ✅ Intent type: `interpret_data_self_discovery`
- ✅ Returns `interpretation` with entities and relationships

---

**Last Updated:** January 27, 2026  
**Owner:** Insights Realm Solution Team  
**Status:** ✅ **COMPREHENSIVE**
