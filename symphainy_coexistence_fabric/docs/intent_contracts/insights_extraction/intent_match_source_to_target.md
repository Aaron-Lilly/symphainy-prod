# Intent Contract: match_source_to_target

**Intent:** match_source_to_target  
**Intent Type:** `match_source_to_target`  
**Journey:** Source-Target Matching (`insights_matching`)  
**Realm:** Insights Realm  
**Status:** ✅ **COMPREHENSIVE**  
**Priority:** 🟡 **PRIORITY 2** - Data migration matching

---

## 1. Intent Overview

### Purpose
Perform three-phase source-to-target matching for data migration and transformation scenarios. Matches source data structure to target data model using deterministic embeddings.

### Intent Flow
```
[User requests source-to-target matching]
    ↓
[match_source_to_target intent]
    ↓
[GuidedDiscoveryService.match_source_to_target()]
    ↓
[Phase 1: Schema matching]
[Phase 2: Semantic matching]
[Phase 3: Pattern validation]
    ↓
[Track matching in Supabase for lineage]
    ↓
[Return matching_result artifact]
```

### Expected Observable Artifacts
- `matching_result` artifact with:
  - `mapping_table` - Field-level mappings
  - `overall_confidence` - Overall match confidence
  - `phase_results` - Results from each matching phase
  - `unmapped_fields` - Fields that couldn't be mapped
  - `transformation_suggestions` - Suggested transformations

---

## 2. Intent Parameters

### Required Parameters

| Parameter | Type | Description | Validation |
|-----------|------|-------------|------------|
| `source_deterministic_embedding_id` | `string` | Source embedding ID | Required |
| `target_deterministic_embedding_id` | `string` | Target embedding ID | Required |
| `source_parsed_file_id` | `string` | Source parsed file ID | Required |
| `target_parsed_file_id` | `string` | Target parsed file ID | Required |

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
    "matching_result": {
      "overall_confidence": 0.87,
      "mapping_table": [
        {
          "source_field": "POLICY_NO",
          "target_field": "policy_number",
          "match_type": "exact",
          "confidence": 0.98,
          "transformation": null
        },
        {
          "source_field": "EFF_DATE",
          "target_field": "effective_date",
          "match_type": "semantic",
          "confidence": 0.92,
          "transformation": "DATE_CONVERT"
        },
        {
          "source_field": "PREM_AMT",
          "target_field": "premium",
          "match_type": "pattern",
          "confidence": 0.85,
          "transformation": "DECIMAL_SCALE"
        }
      ],
      "phase_results": {
        "schema_matching": {
          "matched_count": 12,
          "total_fields": 15,
          "confidence": 0.80
        },
        "semantic_matching": {
          "matched_count": 14,
          "confidence": 0.93
        },
        "pattern_validation": {
          "validated_count": 14,
          "confidence": 0.88
        }
      },
      "unmapped_fields": {
        "source": ["LEGACY_CODE"],
        "target": ["audit_timestamp"]
      },
      "transformation_suggestions": [
        {
          "source_field": "EFF_DATE",
          "target_field": "effective_date",
          "transformation": "DATE_CONVERT",
          "format_from": "YYYYMMDD",
          "format_to": "ISO8601"
        }
      ]
    },
    "source_parsed_file_id": "parsed_source_123",
    "target_parsed_file_id": "parsed_target_456",
    "source_deterministic_embedding_id": "det_emb_src_123",
    "target_deterministic_embedding_id": "det_emb_tgt_456",
    "matching_uuid": "match_uuid_789"
  },
  "events": [
    {
      "type": "source_to_target_matched",
      "source_parsed_file_id": "parsed_source_123",
      "target_parsed_file_id": "parsed_target_456",
      "overall_confidence": 0.87
    }
  ]
}
```

---

## 4. Three-Phase Matching Process

### Phase 1: Schema Matching
- Compare field names (exact and fuzzy)
- Match data types
- Identify structural similarities

### Phase 2: Semantic Matching
- Use deterministic embeddings for semantic comparison
- Match fields by meaning, not just name
- Higher precision than schema-only matching

### Phase 3: Pattern Validation
- Validate matched fields against data patterns
- Ensure transformations produce valid output
- Final confidence adjustment

---

## 5. Lineage Tracking

### Supabase Tracking
Matching tracked in `source_target_matchings` table:
- `source_file_id`, `source_parsed_result_id`
- `target_file_id`, `target_parsed_result_id`
- `matching_result` - Full results
- `overall_confidence` - Confidence score
- `mapping_count` - Number of mappings

---

## 6. Idempotency

### Idempotency Key
`matching_fingerprint = hash(source_det_emb + target_det_emb + tenant_id)`

### Behavior
- Same source and target = same matching result
- Deterministic three-phase process
- Safe to retry

---

## 7. Implementation Details

### Handler Location
`symphainy_platform/realms/insights/orchestrators/insights_orchestrator.py::InsightsOrchestrator._handle_match_source_to_target`

### Key Implementation Steps
1. Validate all four required parameters
2. Call `GuidedDiscoveryService.match_source_to_target()`
3. Track matching in Supabase via `_track_matching()`
4. Return matching_result artifact

### Enabling Services
- **GuidedDiscoveryService:** `symphainy_platform/realms/insights/enabling_services/guided_discovery_service.py`

---

## 8. Error Handling

### Validation Errors
- `source_deterministic_embedding_id` missing → `ValueError`
- `target_deterministic_embedding_id` missing → `ValueError`
- `source_parsed_file_id` missing → `ValueError`
- `target_parsed_file_id` missing → `ValueError`

### Runtime Errors
- Embedding not found → RuntimeError
- Matching service error → RuntimeError

---

## 9. Use Cases

### Data Migration
- Legacy system to modern database
- Mainframe to cloud
- System consolidation

### Data Transformation
- Format conversion
- Schema evolution
- ETL pipeline setup

---

## 10. Contract Compliance

### Required Artifacts
- `matching_result` - Complete mapping with confidence

### Required Events
- `source_to_target_matched` - With file IDs and confidence

---

**Last Updated:** January 27, 2026  
**Owner:** Insights Realm Solution Team  
**Status:** ✅ **COMPREHENSIVE** (not used by frontend)
