# Intent Contract: visualize_lineage

**Intent:** visualize_lineage  
**Intent Type:** `visualize_lineage`  
**Journey:** Lineage & Relationships (`insights_lineage`)  
**Realm:** Insights Realm  
**Status:** ✅ **COMPREHENSIVE**  
**Priority:** 🔴 **PRIORITY 1** - "Your Data Mash" visualization

---

## 1. Intent Overview

### Purpose
Generate "Your Data Mash" visualization showing the complete lineage of a file - from upload through parsing, embedding, interpretation, and analysis. Creates a visual graph of all transformations and relationships.

### Intent Flow
```
[User requests lineage visualization]
    ↓
[visualize_lineage intent]
    ↓
[LineageVisualizationService.visualize_lineage()]
    ↓
[Query Supabase for lineage nodes:
 - Files, Parsed Results, Embeddings
 - Interpretations, Analyses, Guides, Agent Sessions]
    ↓
[Build lineage graph with nodes and edges]
    ↓
[Register as Purpose-Bound Outcome (visualization)]
    ↓
[Return lineage_visualization artifact]
```

### Expected Observable Artifacts
- `lineage_visualization` artifact with:
  - `visualization_type` - "lineage_graph"
  - `lineage_graph` - Graph with nodes and edges
  - `image_base64` - Optional base64 image
  - `storage_path` - Optional GCS path
  - `artifact_id` - Artifact Plane reference

---

## 2. Intent Parameters

### Required Parameters

| Parameter | Type | Description | Validation |
|-----------|------|-------------|------------|
| `file_id` | `string` | File identifier (source file) | Required |

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
    "lineage_visualization": {
      "visualization_type": "lineage_graph",
      "lineage_graph": {
        "nodes": [
          {
            "id": "file_abc123",
            "label": "policy_data.csv",
            "type": "file",
            "metadata": { "file_size": "1.2MB", "upload_date": "2026-01-27" }
          },
          {
            "id": "parsed_xyz789",
            "label": "Parsed Result",
            "type": "parsed_result",
            "metadata": { "record_count": 1000 }
          },
          {
            "id": "emb_def456",
            "label": "Deterministic Embedding",
            "type": "embedding",
            "metadata": { "dimension": 768 }
          },
          {
            "id": "interp_ghi012",
            "label": "Self-Discovery Interpretation",
            "type": "interpretation",
            "metadata": { "confidence": 0.85 }
          },
          {
            "id": "analysis_jkl345",
            "label": "Structured Analysis",
            "type": "analysis",
            "metadata": { "analysis_type": "structured" }
          }
        ],
        "edges": [
          { "source": "file_abc123", "target": "parsed_xyz789", "type": "parsed_from" },
          { "source": "parsed_xyz789", "target": "emb_def456", "type": "embedded_from" },
          { "source": "parsed_xyz789", "target": "interp_ghi012", "type": "interpreted_from" },
          { "source": "parsed_xyz789", "target": "analysis_jkl345", "type": "analyzed_from" }
        ],
        "file_id": "file_abc123",
        "tenant_id": "tenant_001"
      },
      "image_base64": "data:image/png;base64,...",
      "storage_path": "gs://bucket/lineage/file_abc123.png"
    },
    "file_id": "file_abc123",
    "artifact_id": "lineage_viz_file_abc123"
  },
  "events": [
    {
      "type": "lineage_visualized",
      "file_id": "file_abc123",
      "artifact_id": "lineage_viz_file_abc123"
    }
  ]
}
```

---

## 4. Artifact Registration

### Artifact Plane Registration
Visualization registered as Purpose-Bound Outcome:
- `artifact_type`: "visualization"
- `artifact_id`: `lineage_viz_{file_id}`
- `lifecycle_state`: "draft"
- `owner`: "client"
- `purpose`: "delivery" (visualizations are deliverables)
- `source_artifact_ids`: [file_id]

---

## 5. Idempotency

### Idempotency Key
`lineage_fingerprint = hash(file_id + tenant_id)`

### Behavior
- Same file = same lineage graph (based on current state)
- Lineage grows as operations are performed
- Safe to retry, returns current state

---

## 6. Implementation Details

### Handler Location
`symphainy_platform/realms/insights/orchestrators/insights_orchestrator.py::InsightsOrchestrator._handle_visualize_lineage`

### Key Implementation Steps
1. Validate `file_id` provided
2. Call `LineageVisualizationService.visualize_lineage()`
3. Service queries Supabase for all lineage nodes:
   - Files table
   - Parsed results table
   - Embeddings table
   - Interpretations table
   - Analyses table
   - Guides table (if used)
   - Agent sessions table (if deep dive)
4. Build graph structure with nodes and edges
5. Generate visualization image (optional)
6. Register as Purpose-Bound Outcome in Artifact Plane
7. Return lineage_visualization artifact

### Enabling Services
- **LineageVisualizationService:** `symphainy_platform/realms/insights/enabling_services/lineage_visualization_service.py`

### Node Types
| Type | Description |
|------|-------------|
| `file` | Uploaded file |
| `parsed_result` | Parsed file result |
| `embedding` | Deterministic embedding |
| `interpretation` | Data interpretation |
| `analysis` | Analysis report |
| `guide` | Guide used for interpretation |
| `agent_session` | Agent conversation session |

---

## 7. Frontend Integration

### Frontend Usage (InsightsAPIManager.ts)
```typescript
// InsightsAPIManager.visualizeLineage()
const result = await insightsManager.visualizeLineage(fileId);

if (result.success) {
  const viz = result.visualization;
  // Render lineage graph
  // Display nodes and edges
}

// Alternative: Get cached visualization
const cached = await insightsManager.getDataMashVisualization(fileId);
```

### Expected Frontend Behavior
1. User requests "Your Data Mash" visualization
2. Frontend submits `visualize_lineage` intent
3. Track execution
4. Extract `lineage_visualization` from artifacts
5. Render interactive graph with nodes and edges
6. Allow user to explore lineage
7. Store in realm state for caching

---

## 8. Error Handling

### Validation Errors
- `file_id` missing → `ValueError("file_id is required for visualize_lineage intent")`

### Runtime Errors
- File not found → Empty lineage graph
- Visualization service error → RuntimeError

---

## 9. Contract Compliance

### Required Artifacts
- `lineage_visualization` - Lineage graph with nodes and edges

### Required Events
- `lineage_visualized` - With file_id and artifact_id

---

## 10. Cross-Reference Analysis

### Journey Contract Says
- `create_relationship_graph` - Step 1
- `visualize_relationships` - Step 2

### Implementation Does
- ✅ `visualize_lineage` creates complete lineage graph
- ✅ Shows all transformations (file → parsed → embedding → interpretation → analysis)
- ✅ Registers as deliverable in Artifact Plane

### Frontend Expects
- ✅ Intent type: `visualize_lineage`
- ✅ Returns `visualization` with lineage_graph

---

**Last Updated:** January 27, 2026  
**Owner:** Insights Realm Solution Team  
**Status:** ✅ **COMPREHENSIVE**
