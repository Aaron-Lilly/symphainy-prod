# Intent Contract: assess_data_quality

**Intent:** assess_data_quality  
**Intent Type:** `assess_data_quality`  
**Journey:** Data Quality (`insights_data_quality`)  
**Realm:** Insights Realm  
**Status:** ✅ **COMPREHENSIVE**  
**Priority:** 🔴 **PRIORITY 1** - Core quality assessment

---

## 1. Intent Overview

### Purpose
Assess data quality across parsing, data, and source dimensions. Combines parsing results with embeddings to identify root causes of issues. Calculates confidence scores for parsing, embedding, and overall quality.

### Intent Flow
```
[User requests quality assessment]
    ↓
[assess_data_quality intent]
    ↓
[DataQualityService.assess_data_quality()]
    ↓
[Get parsed data from Content Realm]
[Get deterministic embedding (if available)]
[Get semantic embeddings from ArangoDB]
[Get source file metadata]
    ↓
[Assess parsing quality → parsing_confidence]
[Assess embedding quality → embedding_confidence]
[Assess data quality]
[Assess source quality]
    ↓
[Root cause analysis]
[Calculate overall_confidence = (parsing + embedding) / 2]
    ↓
[Return quality assessment artifact]
```

### Expected Observable Artifacts
- `quality_assessment` artifact with:
  - `overall_quality` - "good" | "fair" | "poor" | "unknown"
  - `overall_confidence` - 0.0-1.0 score
  - `parsing_confidence` - 0.0-1.0 score
  - `embedding_confidence` - 0.0-1.0 score
  - `parsing_quality` - Status and issues
  - `embedding_quality` - Status and issues
  - `data_quality` - Status and issues
  - `source_quality` - Status and issues
  - `root_cause_analysis` - Primary issue and recommendations
  - `issues` - Confidence-based issues (bad_scan, bad_schema)

---

## 2. Intent Parameters

### Required Parameters

| Parameter | Type | Description | Validation |
|-----------|------|-------------|------------|
| `parsed_file_id` | `string` | Parsed file identifier | Required, non-empty |
| `source_file_id` | `string` | Source file identifier | Required, non-empty |

### Optional Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `parser_type` | `string` | Parser type (mainframe, csv, json, pdf) | `"unknown"` |
| `deterministic_embedding_id` | `string` | Deterministic embedding ID for validation | `null` |

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
    "quality_assessment": {
      "overall_quality": "fair",
      "overall_confidence": 0.72,
      "parsing_confidence": 0.85,
      "embedding_confidence": 0.59,
      "parsing_quality": {
        "status": "good",
        "issues": [],
        "suggestions": []
      },
      "embedding_quality": {
        "status": "issues",
        "issues": [
          {
            "type": "schema_mismatch",
            "description": "Schema mismatch: Missing in parsed: customer_id",
            "severity": "high",
            "suggestion": "Review schema definition or source data format"
          }
        ],
        "schema_match": { "exact_match": false, "differences": [...] }
      },
      "data_quality": {
        "status": "good",
        "issues": [],
        "suggestions": []
      },
      "source_quality": {
        "status": "good",
        "issues": [],
        "suggestions": []
      },
      "root_cause_analysis": {
        "primary_issue": "data",
        "confidence": 0.65,
        "recommendations": [
          "Check source data quality",
          "Consider rescanning or using higher quality source"
        ]
      },
      "issues": [
        {
          "type": "bad_schema",
          "description": "Embedding confidence is low (0.59)",
          "severity": "high",
          "suggestion": "Review schema definition or create new deterministic embeddings"
        }
      ]
    },
    "parsed_file_id": "parsed_abc123",
    "source_file_id": "file_xyz789",
    "deterministic_embedding_id": "det_emb_123"
  },
  "events": [
    {
      "type": "data_quality_assessed",
      "parsed_file_id": "parsed_abc123",
      "source_file_id": "file_xyz789",
      "deterministic_embedding_id": "det_emb_123"
    }
  ]
}
```

### Error Response

```json
{
  "error": "parsed_file_id is required for assess_data_quality intent",
  "error_code": "VALIDATION_ERROR",
  "execution_id": "exec_abc123"
}
```

---

## 4. Artifact Registration

### State Surface Updates
- Quality assessment stored in execution state

### Lineage Tracking
- No separate lineage record (quality assessment is ephemeral)

---

## 5. Idempotency

### Idempotency Key
`quality_fingerprint = hash(parsed_file_id + source_file_id + deterministic_embedding_id)`

### Behavior
- Same inputs = same quality assessment
- May change if source data changes
- Safe to retry

---

## 6. Implementation Details

### Handler Location
`symphainy_platform/realms/insights/orchestrators/insights_orchestrator.py::InsightsOrchestrator._handle_assess_data_quality`

### Key Implementation Steps
1. Validate `parsed_file_id` and `source_file_id` provided
2. Call `DataQualityService.assess_data_quality()`
3. Service gets parsed data from Content Realm
4. Service gets deterministic embedding (if provided)
5. Service gets semantic embeddings from ArangoDB
6. Service assesses parsing quality → parsing_confidence
7. Service assesses embedding quality → embedding_confidence
8. Service calculates overall_confidence = (parsing + embedding) / 2
9. Service performs root cause analysis
10. Return quality assessment artifact

### Enabling Services
- **DataQualityService:** `symphainy_platform/realms/insights/enabling_services/data_quality_service.py` (835 lines!)

### Quality Dimensions
- **Parsing Quality:** Did parsing work correctly?
- **Data Quality:** Is the underlying data good?
- **Source Quality:** Copybook problems, data format issues
- **Embedding Quality:** Does schema match deterministic embedding?

### Confidence Thresholds
- Confidence < 0.7 triggers issues:
  - `bad_scan` (parsing_confidence < 0.7)
  - `bad_schema` (embedding_confidence < 0.7)

---

## 7. Frontend Integration

### Frontend Usage (InsightsAPIManager.ts)
```typescript
// InsightsAPIManager.assessDataQuality()
const result = await insightsManager.assessDataQuality(
  parsedFileId,
  sourceFileId,
  parserType
);

if (result.success) {
  const assessment = result.quality_assessment;
  // Display quality scores and issues
}
```

### Expected Frontend Behavior
1. User requests quality assessment for parsed file
2. Frontend submits `assess_data_quality` intent
3. Track execution via `trackExecution()`
4. Wait for completion
5. Extract `quality_assessment` from artifacts
6. Display quality scores, issues, and recommendations
7. Store in realm state for subsequent operations

---

## 8. Error Handling

### Validation Errors
- `parsed_file_id` missing → `ValueError`
- `source_file_id` missing → `ValueError`

### Runtime Errors
- Parsed data not available → Return quality = "unknown"
- Embeddings not available → Skip embedding quality
- Service error → RuntimeError with details

---

## 9. Testing & Validation

### Happy Path
1. Parsed file and source file exist
2. Submit `assess_data_quality` intent
3. Quality assessment returns with confidence scores
4. Issues identified if confidence < threshold

### Boundary Violations
- Missing `parsed_file_id` → Validation error
- Missing `source_file_id` → Validation error

### Failure Scenarios
- No parsed data → overall_quality = "unknown", confidence = 0.0
- No embeddings → Skip embedding quality assessment

---

## 10. Contract Compliance

### Required Artifacts
- `quality_assessment` - Comprehensive quality assessment

### Required Events
- `data_quality_assessed` - With file IDs

---

## 11. Cross-Reference Analysis

### Journey Contract Says
- `assess_data_quality` - Step 1
- `validate_schema` - Step 2 (separate intent)
- `generate_quality_report` - Step 3 (separate intent)

### Implementation Does
- ✅ `assess_data_quality` combines all into single comprehensive intent
- ✅ Schema validation is part of embedding quality assessment
- ✅ Quality report is the returned artifact

### Frontend Expects
- ✅ Intent type: `assess_data_quality`
- ✅ Returns `quality_assessment` with confidence scores

### Gaps/Discrepancies
- **NAMING:** Contract has 3 intents, implementation has 1 comprehensive intent
- **Recommendation:** Update contract to single `assess_data_quality` intent

---

**Last Updated:** January 27, 2026  
**Owner:** Insights Realm Solution Team  
**Status:** ✅ **COMPREHENSIVE**
