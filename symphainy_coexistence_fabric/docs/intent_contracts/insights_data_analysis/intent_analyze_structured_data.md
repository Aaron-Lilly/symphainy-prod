# Intent Contract: analyze_structured_data

**Intent:** analyze_structured_data  
**Intent Type:** `analyze_structured_data`  
**Journey:** Data Analysis (`insights_data_analysis`)  
**Realm:** Insights Realm  
**Status:** ✅ **COMPREHENSIVE**  
**Priority:** 🔴 **PRIORITY 1** - Structured data analysis

---

## 1. Intent Overview

### Purpose
Analyze structured data (CSV, JSON, mainframe records) to generate insights, identify patterns, and produce analysis reports. Registers result as Purpose-Bound Outcome in Artifact Plane.

### Intent Flow
```
[User requests structured data analysis]
    ↓
[analyze_structured_data intent]
    ↓
[StructuredAnalysisService.analyze_structured_data()]
    ↓
[Statistical analysis, pattern detection, anomaly identification]
    ↓
[Track analysis in Supabase for lineage]
    ↓
[Register as Purpose-Bound Outcome in Artifact Plane]
    ↓
[Return structured_analysis artifact]
```

### Expected Observable Artifacts
- `structured_analysis` artifact with:
  - `analysis_type` - "structured"
  - `summary` - Human-readable summary
  - `insights` - Array of insights with type, description, confidence
  - `statistics` - Column statistics, distributions
  - `patterns` - Detected patterns
  - `anomalies` - Data anomalies
  - `recommendations` - Analysis recommendations
  - `artifact_id` - Artifact Plane reference

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
| `analysis_options` | `object` | Analysis configuration | `{}` |

### Analysis Options

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `include_statistics` | `boolean` | Include column statistics | `true` |
| `detect_patterns` | `boolean` | Detect data patterns | `true` |
| `identify_anomalies` | `boolean` | Identify anomalies | `true` |

---

## 3. Intent Returns

### Success Response

```json
{
  "artifacts": {
    "structured_analysis": {
      "analysis_type": "structured",
      "summary": "Insurance policy data with 1,000 records across 15 columns",
      "insights": [
        {
          "type": "distribution",
          "description": "Premium amounts follow normal distribution centered at $500",
          "confidence": 0.92
        },
        {
          "type": "correlation",
          "description": "Strong correlation (0.85) between coverage_amount and premium",
          "confidence": 0.88
        }
      ],
      "statistics": {
        "row_count": 1000,
        "column_count": 15,
        "column_stats": {
          "premium": { "min": 100, "max": 2000, "mean": 500, "std": 150 }
        }
      },
      "patterns": [
        {
          "name": "seasonal_premium",
          "description": "Premiums trend higher in Q4",
          "confidence": 0.78
        }
      ],
      "anomalies": [
        {
          "type": "outlier",
          "column": "premium",
          "description": "5 records have premium > 3 std from mean"
        }
      ]
    },
    "parsed_file_id": "parsed_abc123",
    "artifact_id": "structured_analysis_parsed_abc123"
  },
  "events": [
    {
      "type": "structured_data_analyzed",
      "parsed_file_id": "parsed_abc123",
      "artifact_id": "structured_analysis_parsed_abc123",
      "analysis_uuid": "uuid-xyz"
    }
  ]
}
```

---

## 4. Artifact Registration

### Artifact Plane Registration
Analysis registered as Purpose-Bound Outcome:
- `artifact_type`: "analysis_report"
- `artifact_id`: `structured_analysis_{parsed_file_id}`
- `lifecycle_state`: "draft"
- `owner`: "client"
- `purpose`: "decision_support"
- `source_artifact_ids`: [parsed_file_id]

### Lineage Tracking
- Analysis tracked in Supabase `analyses` table
- Links: file_id, parsed_result_id
- Includes analysis_type, deep_dive flag

---

## 5. Idempotency

### Idempotency Key
`analysis_fingerprint = hash(parsed_file_id + analysis_options + tenant_id)`

### Behavior
- Same inputs = same analysis results
- Deterministic analysis
- Safe to retry

---

## 6. Implementation Details

### Handler Location
`symphainy_platform/realms/insights/orchestrators/insights_orchestrator.py::InsightsOrchestrator._handle_analyze_structured`

### Key Implementation Steps
1. Accept both `parsed_file_id` and `parsed_result_id`
2. Call `StructuredAnalysisService.analyze_structured_data()`
3. Track analysis in Supabase via `_track_analysis()`
4. Register as Purpose-Bound Outcome in Artifact Plane
5. Return structured_analysis artifact with artifact_id reference

### Enabling Services
- **StructuredAnalysisService:** `symphainy_platform/realms/insights/enabling_services/structured_analysis_service.py`

### Artifact Plane Integration
```python
artifact_result = await self.artifact_plane.create_artifact(
    artifact_type="analysis_report",
    artifact_id=f"structured_analysis_{parsed_file_id}",
    payload=artifact_payload,
    context=context,
    lifecycle_state="draft",
    owner="client",
    purpose="decision_support",
    source_artifact_ids=[parsed_file_id]
)
```

---

## 7. Frontend Integration

### Frontend Usage (InsightsAPIManager.ts)
```typescript
// InsightsAPIManager.analyzeStructuredData()
const result = await insightsManager.analyzeStructuredData(
  parsedFileId,
  { include_statistics: true, detect_patterns: true }
);

if (result.success) {
  const analysis = result.analysis;
  // Display insights, statistics, patterns
}
```

### Expected Frontend Behavior
1. User requests analysis of structured data
2. Frontend submits `analyze_structured_data` intent
3. Track execution
4. Extract `structured_analysis` from artifacts
5. Display insights, statistics, patterns, anomalies
6. Store in realm state

---

## 8. Error Handling

### Validation Errors
- `parsed_file_id` missing → `ValueError`

### Runtime Errors
- Parsed data not available → RuntimeError
- Analysis service error → RuntimeError with details

---

## 9. Contract Compliance

### Required Artifacts
- `structured_analysis` - Structured data analysis result

### Required Events
- `structured_data_analyzed` - With parsed_file_id and artifact_id

---

## 10. Cross-Reference Analysis

### Journey Contract Says
- `analyze_content` - Step 1: Analyze content
- `generate_business_insights` - Step 2
- `create_visualizations` - Step 3

### Implementation Does
- ✅ `analyze_structured_data` handles structured analysis
- ✅ Generates insights and statistics
- ✅ Registers in Artifact Plane

### Frontend Expects
- ✅ Intent type: `analyze_structured_data`
- ✅ Returns `analysis` with insights

---

**Last Updated:** January 27, 2026  
**Owner:** Insights Realm Solution Team  
**Status:** ✅ **COMPREHENSIVE**
