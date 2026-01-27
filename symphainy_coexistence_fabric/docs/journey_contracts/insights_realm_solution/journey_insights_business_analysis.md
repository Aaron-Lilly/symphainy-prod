# Journey Contract: Business Analysis

**Journey:** Business Analysis  
**Journey ID:** `journey_insights_business_analysis`  
**Solution:** Insights Realm Solution  
**Status:** ✅ **IMPLEMENTED**  
**Priority:** 🔴 **PRIORITY 1** - Foundation journey

---

## 1. Journey Overview

### Intents in Journey
1. **`analyze_structured_data`** - Analyze structured data (CSV, JSON, mainframe)
   - Statistical analysis, pattern detection, anomaly identification
   - Registers as Purpose-Bound Outcome in Artifact Plane

2. **`analyze_unstructured_data`** - Analyze unstructured data (documents, text)
   - NLP analysis, entity extraction, topic modeling
   - Optional deep dive with Insights Liaison Agent

### Journey Flow
```
[User requests business analysis]
    ↓
[Determine data type]
    ├── Structured data
    │   ↓
    │   [analyze_structured_data intent]
    │   ↓
    │   [StructuredAnalysisService.analyze_structured_data()]
    │
    └── Unstructured data
        ↓
        [analyze_unstructured_data intent]
        ↓
        [UnstructuredAnalysisService.analyze_unstructured_data()]
        ↓
        [Optional: Deep dive with Insights Liaison Agent]
    ↓
[Track analysis in Supabase for lineage]
    ↓
[Register as Purpose-Bound Outcome in Artifact Plane]
    ↓
[Return analysis artifact]
    ↓
[Journey Complete]
```

### Expected Observable Artifacts

#### Structured Analysis

| Artifact | Type | Description |
|----------|------|-------------|
| `structured_analysis` | object | Structured data analysis |
| `structured_analysis.analysis_type` | string | "structured" |
| `structured_analysis.summary` | string | Human-readable summary |
| `structured_analysis.insights` | array | Generated insights |
| `structured_analysis.statistics` | object | Column statistics |
| `structured_analysis.patterns` | array | Detected patterns |
| `structured_analysis.anomalies` | array | Data anomalies |
| `artifact_id` | string | Artifact Plane reference |

#### Unstructured Analysis

| Artifact | Type | Description |
|----------|------|-------------|
| `unstructured_analysis` | object | Unstructured data analysis |
| `unstructured_analysis.analysis_type` | string | "unstructured" |
| `unstructured_analysis.summary` | string | Human-readable summary |
| `unstructured_analysis.insights` | array | Generated insights |
| `unstructured_analysis.entities` | array | Extracted entities |
| `unstructured_analysis.topics` | array | Identified topics |
| `unstructured_analysis.deep_dive` | object | Agent session info |
| `artifact_id` | string | Artifact Plane reference |

### Artifact Lifecycle State Transitions

| State | Transition | Description |
|-------|------------|-------------|
| draft | Initial | Analysis created |
| published | Optional | Analysis approved |

### Idempotency Scope (Per Intent)

| Intent | Idempotency Key | Scope |
|--------|-----------------|-------|
| `analyze_structured_data` | `hash(parsed_file_id + analysis_options + tenant_id)` | Same inputs = same analysis |
| `analyze_unstructured_data` | `hash(parsed_file_id + analysis_options + tenant_id)` | Same inputs = same analysis (excluding agent session) |

### Journey Completion Definition

**Journey is considered complete when:**

* Analysis artifact returned
* Analysis tracked in Supabase
* Analysis registered in Artifact Plane

---

## 2. Scenario 1: Structured Analysis Happy Path

### Test Description
Structured data analysis completes successfully.

### Steps
1. [x] User has a parsed structured file (CSV, JSON, mainframe)
2. [x] User triggers `analyze_structured_data`
3. [x] StructuredAnalysisService performs analysis
4. [x] Analysis tracked in Supabase
5. [x] Analysis registered in Artifact Plane
6. [x] Analysis artifact returned

### Verification
- [x] `structured_analysis` artifact returned
- [x] `structured_analysis.insights` non-empty
- [x] `structured_analysis.statistics` contains column stats
- [x] `artifact_id` in Artifact Plane

---

## 3. Scenario 2: Unstructured Analysis with Deep Dive

### Test Description
Unstructured analysis with deep dive creates agent session.

### Steps
1. [x] User has a parsed document
2. [x] User triggers `analyze_unstructured_data` with `deep_dive: true`
3. [x] UnstructuredAnalysisService performs analysis
4. [x] Insights Liaison Agent session created
5. [x] Analysis tracked with agent_session_id
6. [x] Analysis artifact returned with deep_dive info

### Verification
- [x] `unstructured_analysis` artifact returned
- [x] `unstructured_analysis.deep_dive.initiated` is true
- [x] `unstructured_analysis.deep_dive.session_id` present
- [x] Agent session accessible

---

## 4. Artifact Plane Integration

Analysis registered as Purpose-Bound Outcome:

```python
artifact_result = await self.artifact_plane.create_artifact(
    artifact_type="analysis_report",
    artifact_id=f"structured_analysis_{parsed_file_id}",
    payload=artifact_payload,
    context=context,
    lifecycle_state="draft",
    owner="client",
    purpose="decision_support",  # Analysis reports support decisions
    source_artifact_ids=[parsed_file_id]
)
```

---

## 5. Integration Points

### Platform Services
- **Insights Realm:** StructuredAnalysisService, UnstructuredAnalysisService
- **Artifact Plane:** Purpose-Bound Outcome registration
- **Insights Liaison Agent:** Deep dive agent

### Backend Handler
`symphainy_platform/realms/insights/orchestrators/insights_orchestrator.py::_handle_analyze_structured`
`symphainy_platform/realms/insights/orchestrators/insights_orchestrator.py::_handle_analyze_unstructured`

### Frontend API
`symphainy-frontend/shared/managers/InsightsAPIManager.ts::analyzeStructuredData()`
`symphainy-frontend/shared/managers/InsightsAPIManager.ts::analyzeUnstructuredData()`

---

## 6. Gate Status

**Journey is "done" only when:**
- [x] ✅ Structured analysis happy path works
- [x] ✅ Unstructured analysis happy path works
- [x] ✅ Deep dive with agent works
- [x] ✅ Artifact Plane registration works
- [x] ✅ Lineage tracking works

**Current Status:** ✅ **IMPLEMENTED**

---

## 7. Related Documents

- **Intent Contract (Structured):** `docs/intent_contracts/insights_data_analysis/intent_analyze_structured_data.md`
- **Intent Contract (Unstructured):** `docs/intent_contracts/insights_data_analysis/intent_analyze_unstructured_data.md`
- **Analysis:** `docs/intent_contracts/INSIGHTS_REALM_ANALYSIS.md`

---

**Last Updated:** January 27, 2026  
**Owner:** Insights Realm Solution Team
