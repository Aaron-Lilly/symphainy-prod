# Intent Contract: interpret_data_guided

**Intent:** interpret_data_guided  
**Intent Type:** `interpret_data_guided`  
**Journey:** Data Interpretation (`insights_data_interpretation`)  
**Realm:** Insights Realm  
**Status:** ✅ **COMPREHENSIVE**  
**Priority:** 🔴 **PRIORITY 1** - Guided interpretation capability

---

## 1. Intent Overview

### Purpose
Interpret parsed data using a pre-defined guide (schema/ontology). Matches data against guide structure to identify entities and relationships with higher precision than self-discovery.

### Intent Flow
```
[User requests guided interpretation]
    ↓
[interpret_data_guided intent]
    ↓
[Get embeddings from ArangoDB via chunk-based pattern]
[Get guide definition]
    ↓
[GuidedDiscoveryService.interpret_with_guide()]
    ↓
[Match data against guide structure]
    ↓
[Track interpretation in Supabase for lineage]
    ↓
[Promote to Record of Fact via Data Steward SDK]
    ↓
[Return interpretation artifact]
```

### Expected Observable Artifacts
- `interpretation` artifact with:
  - `interpretation_type` - "guided"
  - `entities` - Matched entities (from guide)
  - `relationships` - Matched relationships
  - `confidence_score` - Match confidence
  - `coverage_score` - Guide coverage
  - `guide_id` - Guide used
  - `match_details` - Detailed match results

---

## 2. Intent Parameters

### Required Parameters

| Parameter | Type | Description | Validation |
|-----------|------|-------------|------------|
| `parsed_file_id` | `string` | Parsed file identifier | Required (or `parsed_result_id`) |
| `guide_id` | `string` | Guide identifier | Required |

### Optional Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `parsed_result_id` | `string` | Alias for parsed_file_id | Same as parsed_file_id |
| `matching_options` | `object` | Matching configuration | `{}` |

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
    "interpretation": {
      "interpretation_type": "guided",
      "guide_id": "guide_insurance_policy",
      "entities": [
        {
          "name": "Policy",
          "type": "guide_entity",
          "matched_fields": {
            "policy_number": { "source": "POLICY_NO", "confidence": 0.95 },
            "effective_date": { "source": "EFF_DATE", "confidence": 0.92 },
            "premium": { "source": "PREMIUM_AMT", "confidence": 0.98 }
          },
          "confidence": 0.95
        }
      ],
      "relationships": [
        {
          "source": "Policy",
          "target": "Customer",
          "type": "belongs_to",
          "guide_relationship": "policy_owner",
          "confidence": 0.88
        }
      ],
      "confidence_score": 0.92,
      "coverage_score": 0.85,
      "match_details": {
        "matched_entities": 5,
        "total_guide_entities": 6,
        "unmatched_fields": ["secondary_beneficiary"]
      }
    },
    "parsed_file_id": "parsed_abc123",
    "guide_id": "guide_insurance_policy"
  },
  "events": [
    {
      "type": "data_interpreted_with_guide",
      "parsed_file_id": "parsed_abc123",
      "guide_id": "guide_insurance_policy"
    }
  ]
}
```

---

## 4. Artifact Registration

### Lineage Tracking
- Interpretation tracked in Supabase `interpretations` table
- Links: file_id, parsed_result_id, embedding_id, **guide_id**
- Includes confidence_score and coverage_score

### Record of Fact Promotion
- Interpretations are persistent meaning (Records of Fact)
- Promoted immediately via Data Steward SDK

---

## 5. Idempotency

### Idempotency Key
`guided_interpretation_fingerprint = hash(parsed_file_id + guide_id + tenant_id)`

### Behavior
- Same parsed file + guide = same interpretation
- Guided interpretation is deterministic
- Safe to retry

---

## 6. Implementation Details

### Handler Location
`symphainy_platform/realms/insights/orchestrators/insights_orchestrator.py::InsightsOrchestrator._handle_guided_discovery`

### Key Implementation Steps
1. Accept both `parsed_file_id` and `parsed_result_id` (aliases)
2. Validate `guide_id` is provided
3. Get embeddings via chunk-based pattern
4. Call `GuidedDiscoveryService.interpret_with_guide()`
5. Get guide UUID from Supabase
6. Track interpretation in Supabase
7. Promote to Record of Fact
8. Return interpretation artifact

### Enabling Services
- **GuidedDiscoveryService:** `symphainy_platform/realms/insights/enabling_services/guided_discovery_service.py`

---

## 7. Frontend Integration

### Frontend Usage (InsightsAPIManager.ts)
```typescript
// InsightsAPIManager.interpretDataGuided()
const result = await insightsManager.interpretDataGuided(
  parsedFileId,
  guideId,
  { strict_matching: true }
);

if (result.success) {
  const interpretation = result.interpretation;
  // Display matched entities and relationships
}
```

---

## 8. Error Handling

### Validation Errors
- `parsed_file_id` missing → `ValueError`
- `guide_id` missing → `ValueError("guide_id is required for interpret_data_guided intent")`

### Runtime Errors
- Guide not found → RuntimeError
- Embeddings not available → Interpretation with limited results

---

## 9. Contract Compliance

### Required Artifacts
- `interpretation` - Guided interpretation result

### Required Events
- `data_interpreted_with_guide` - With parsed_file_id and guide_id

---

## 10. Cross-Reference Analysis

### Journey Contract Says
- `initiate_guided_discovery` - Start guided discovery

### Implementation Does
- ✅ `interpret_data_guided` handles guided interpretation
- ✅ Requires guide_id parameter
- ✅ Promotes to Record of Fact

### Frontend Expects
- ✅ Intent type: `interpret_data_guided`
- ✅ Returns `interpretation` with matched entities

---

**Last Updated:** January 27, 2026  
**Owner:** Insights Realm Solution Team  
**Status:** ✅ **COMPREHENSIVE**
