# Journey Contract: Data Quality Assessment

**Journey:** Data Quality Assessment  
**Journey ID:** `journey_insights_data_quality`  
**Solution:** Insights Realm Solution  
**Status:** ✅ **IMPLEMENTED**  
**Priority:** 🔴 **PRIORITY 1** - Foundation journey

---

## 1. Journey Overview

### Intents in Journey
1. **`assess_data_quality`** - Comprehensive data quality assessment
   - Combines parsing, data, and source quality dimensions
   - Calculates parsing_confidence and embedding_confidence
   - Returns overall_confidence = (parsing + embedding) / 2
   - Identifies root causes (bad_scan, bad_schema)

### Journey Flow
```
[User requests quality assessment]
    ↓
[assess_data_quality intent]
    ↓
[DataQualityService.assess_data_quality()]
    ↓
  ├── Get parsed data from Content Realm
  ├── Get deterministic embedding (optional)
  ├── Get semantic embeddings from ArangoDB
  ├── Get source file metadata
    ↓
  ├── Assess parsing quality → parsing_confidence
  ├── Assess embedding quality → embedding_confidence
  ├── Assess data quality
  ├── Assess source quality
    ↓
[Root cause analysis]
[Calculate overall_confidence]
    ↓
[Return quality_assessment artifact]
    ↓
[Journey Complete]
```

### Expected Observable Artifacts

| Artifact | Type | Description |
|----------|------|-------------|
| `quality_assessment` | object | Comprehensive quality assessment |
| `quality_assessment.overall_quality` | string | "good" \| "fair" \| "poor" \| "unknown" |
| `quality_assessment.overall_confidence` | float | 0.0-1.0 overall confidence score |
| `quality_assessment.parsing_confidence` | float | 0.0-1.0 parsing confidence |
| `quality_assessment.embedding_confidence` | float | 0.0-1.0 embedding confidence |
| `quality_assessment.parsing_quality` | object | Parsing quality assessment |
| `quality_assessment.embedding_quality` | object | Embedding quality assessment |
| `quality_assessment.data_quality` | object | Data quality assessment |
| `quality_assessment.source_quality` | object | Source quality assessment |
| `quality_assessment.root_cause_analysis` | object | Primary issue and recommendations |
| `quality_assessment.issues` | array | Confidence-based issues |

### Artifact Lifecycle State Transitions

| State | Description |
|-------|-------------|
| N/A | Quality assessment is ephemeral (not persisted) |

### Idempotency Scope (Per Intent)

| Intent | Idempotency Key | Scope |
|--------|-----------------|-------|
| `assess_data_quality` | `hash(parsed_file_id + source_file_id + deterministic_embedding_id)` | Same inputs = same assessment |

### Journey Completion Definition

**Journey is considered complete when:**

* Quality assessment artifact returned with confidence scores
* Root cause analysis completed
* Issues identified based on confidence thresholds

---

## 2. Scenario 1: Happy Path

### Test Description
Complete quality assessment works end-to-end without failures.

### Steps
1. [x] User has a parsed file and source file
2. [x] User triggers `assess_data_quality` with file IDs
3. [x] DataQualityService performs assessment
4. [x] Confidence scores calculated
5. [x] Quality assessment returned

### Verification
- [x] `quality_assessment` artifact returned
- [x] `overall_confidence` between 0.0 and 1.0
- [x] `parsing_confidence` and `embedding_confidence` calculated
- [x] `root_cause_analysis` provided

### Status
✅ Implemented

---

## 3. Scenario 2: Low Confidence Detection

### Test Description
Journey correctly identifies low confidence and reports issues.

### Steps
1. [x] User triggers assessment for file with parsing issues
2. [x] Assessment detects low parsing_confidence (< 0.7)
3. [x] Issue `bad_scan` added to issues array
4. [x] Root cause analysis identifies "parsing" as primary issue

### Verification
- [x] `issues` array contains `bad_scan` issue
- [x] `root_cause_analysis.primary_issue` is "parsing"
- [x] Recommendations provided

---

## 4. Scenario 3: Missing Deterministic Embedding

### Test Description
Journey handles missing deterministic embedding gracefully.

### Steps
1. [x] User triggers assessment without `deterministic_embedding_id`
2. [x] Embedding quality assessment returns "unknown" status
3. [x] Overall confidence still calculated
4. [x] No crash or unhandled exception

### Verification
- [x] Assessment completes
- [x] `embedding_quality.status` is "unknown"
- [x] Assessment includes note about missing embedding

---

## 5. Integration Points

### Platform Services
- **Content Realm:** File Parser Service (get parsed data)
- **Insights Realm:** DataQualityService
- **Public Works:** SemanticDataAbstraction, DeterministicComputeAbstraction

### Backend Handler
`symphainy_platform/realms/insights/orchestrators/insights_orchestrator.py::_handle_assess_data_quality`

### Frontend API
`symphainy-frontend/shared/managers/InsightsAPIManager.ts::assessDataQuality()`

---

## 6. Architectural Verification

### Intent Flow
- [x] Intent uses intent-based API (submitIntent)
- [x] Intent flows through Runtime (ExecutionLifecycleManager)
- [x] Intent has execution_id tracking
- [x] Intent has parameter validation

### State Authority
- [x] Runtime is authoritative
- [x] Quality assessment is ephemeral (not persisted)

### Enforcement
- [x] Required parameters validated (parsed_file_id, source_file_id)
- [x] Invalid parameters rejected

---

## 7. Gate Status

**Journey is "done" only when:**
- [x] ✅ Happy path works
- [x] ✅ Low confidence detection works
- [x] ✅ Missing embedding handled gracefully
- [x] ✅ Architectural verification passes

**Current Status:** ✅ **IMPLEMENTED**

---

## 8. Related Documents

- **Intent Contract:** `docs/intent_contracts/insights_data_quality/intent_assess_data_quality.md`
- **Analysis:** `docs/intent_contracts/INSIGHTS_REALM_ANALYSIS.md`

---

**Last Updated:** January 27, 2026  
**Owner:** Insights Realm Solution Team
