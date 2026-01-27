# Intent Contract: analyze_unstructured_data

**Intent:** analyze_unstructured_data  
**Intent Type:** `analyze_unstructured_data`  
**Journey:** Data Analysis (`insights_data_analysis`)  
**Realm:** Insights Realm  
**Status:** ✅ **COMPREHENSIVE**  
**Priority:** 🔴 **PRIORITY 1** - Unstructured data analysis

---

## 1. Intent Overview

### Purpose
Analyze unstructured data (documents, PDFs, text) to generate insights, extract key information, and produce analysis reports. Optionally triggers deep dive with Insights Liaison Agent.

### Intent Flow
```
[User requests unstructured data analysis]
    ↓
[analyze_unstructured_data intent]
    ↓
[UnstructuredAnalysisService.analyze_unstructured_data()]
    ↓
[NLP analysis, entity extraction, topic modeling]
    ↓
[Optional: Deep dive with Insights Liaison Agent]
    ↓
[Track analysis in Supabase for lineage]
    ↓
[Register as Purpose-Bound Outcome in Artifact Plane]
    ↓
[Return unstructured_analysis artifact]
```

### Expected Observable Artifacts
- `unstructured_analysis` artifact with:
  - `analysis_type` - "unstructured"
  - `summary` - Human-readable summary
  - `insights` - Array of insights
  - `entities` - Extracted named entities
  - `topics` - Identified topics
  - `key_phrases` - Important phrases
  - `deep_dive` - Agent session info (if initiated)
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
| `deep_dive` | `boolean` | Trigger Insights Liaison Agent | `false` |
| `extract_entities` | `boolean` | Extract named entities | `true` |
| `topic_modeling` | `boolean` | Perform topic modeling | `true` |

---

## 3. Intent Returns

### Success Response

```json
{
  "artifacts": {
    "unstructured_analysis": {
      "analysis_type": "unstructured",
      "summary": "Insurance policy document with coverage details and terms",
      "insights": [
        {
          "type": "document_type",
          "description": "Life insurance policy contract",
          "confidence": 0.95
        },
        {
          "type": "key_finding",
          "description": "Policy excludes pre-existing conditions",
          "confidence": 0.88
        }
      ],
      "entities": [
        { "text": "John Smith", "type": "PERSON", "confidence": 0.92 },
        { "text": "Acme Insurance Co.", "type": "ORGANIZATION", "confidence": 0.95 }
      ],
      "topics": [
        { "name": "coverage_terms", "weight": 0.35 },
        { "name": "premium_payments", "weight": 0.25 },
        { "name": "beneficiary_details", "weight": 0.20 }
      ],
      "key_phrases": [
        "policy effective date",
        "coverage amount",
        "premium payment schedule"
      ],
      "deep_dive": {
        "session_id": "agent_session_xyz",
        "initiated": true
      }
    },
    "parsed_file_id": "parsed_abc123",
    "deep_dive_initiated": true,
    "artifact_id": "unstructured_analysis_parsed_abc123"
  },
  "events": [
    {
      "type": "unstructured_data_analyzed",
      "parsed_file_id": "parsed_abc123",
      "deep_dive": true,
      "artifact_id": "unstructured_analysis_parsed_abc123",
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
- `artifact_id`: `unstructured_analysis_{parsed_file_id}`
- `lifecycle_state`: "draft"
- `owner`: "client"
- `purpose`: "decision_support"
- `source_artifact_ids`: [parsed_file_id]

### Lineage Tracking
- Analysis tracked in Supabase `analyses` table
- Links: file_id, parsed_result_id
- Includes: analysis_type, deep_dive flag, agent_session_id

---

## 5. Idempotency

### Idempotency Key
`analysis_fingerprint = hash(parsed_file_id + analysis_options + tenant_id)`

### Behavior
- Same inputs = same analysis results (excluding agent session)
- Deep dive creates new agent session each time
- Safe to retry

---

## 6. Implementation Details

### Handler Location
`symphainy_platform/realms/insights/orchestrators/insights_orchestrator.py::InsightsOrchestrator._handle_analyze_unstructured`

### Key Implementation Steps
1. Accept both `parsed_file_id` and `parsed_result_id`
2. Extract `deep_dive` option
3. Call `UnstructuredAnalysisService.analyze_unstructured_data()`
4. If deep_dive, get agent session ID from result
5. Track analysis in Supabase with agent_session_id
6. Register as Purpose-Bound Outcome in Artifact Plane
7. Return unstructured_analysis artifact

### Enabling Services
- **UnstructuredAnalysisService:** `symphainy_platform/realms/insights/enabling_services/unstructured_analysis_service.py`

### Deep Dive Pattern
When `deep_dive: true`:
- Insights Liaison Agent is triggered
- Creates interactive session for deeper analysis
- Agent session ID returned in `deep_dive.session_id`
- User can continue conversation with agent

---

## 7. Frontend Integration

### Frontend Usage (InsightsAPIManager.ts)
```typescript
// InsightsAPIManager.analyzeUnstructuredData()
const result = await insightsManager.analyzeUnstructuredData(
  parsedFileId,
  { deep_dive: true, extract_entities: true }
);

if (result.success) {
  const analysis = result.analysis;
  if (analysis.deep_dive?.initiated) {
    // Open agent conversation with session_id
  }
  // Display insights, entities, topics
}
```

### Expected Frontend Behavior
1. User requests analysis of unstructured data
2. Frontend submits `analyze_unstructured_data` intent
3. Track execution
4. Extract `unstructured_analysis` from artifacts
5. If deep_dive initiated, open agent conversation
6. Display insights, entities, topics, key phrases
7. Store in realm state

---

## 8. Error Handling

### Validation Errors
- `parsed_file_id` missing → `ValueError`

### Runtime Errors
- Parsed data not available → RuntimeError
- Agent session creation failed → Analysis returns without deep_dive

---

## 9. Contract Compliance

### Required Artifacts
- `unstructured_analysis` - Unstructured data analysis result

### Required Events
- `unstructured_data_analyzed` - With parsed_file_id, deep_dive, artifact_id

---

## 10. Cross-Reference Analysis

### Implementation Does
- ✅ `analyze_unstructured_data` handles document/text analysis
- ✅ Optional deep dive with Insights Liaison Agent
- ✅ Registers in Artifact Plane

### Frontend Expects
- ✅ Intent type: `analyze_unstructured_data`
- ✅ Returns `analysis` with entities and deep_dive info

---

**Last Updated:** January 27, 2026  
**Owner:** Insights Realm Solution Team  
**Status:** ✅ **COMPREHENSIVE**
