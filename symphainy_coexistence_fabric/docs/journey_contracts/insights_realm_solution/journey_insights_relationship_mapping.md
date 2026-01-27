# Journey Contract: Lineage & Relationship Mapping

**Journey:** Lineage & Relationship Mapping  
**Journey ID:** `journey_insights_relationship_mapping`  
**Solution:** Insights Realm Solution  
**Status:** ✅ **IMPLEMENTED**  
**Priority:** 🔴 **PRIORITY 1** - Foundation journey

---

## 1. Journey Overview

### Intents in Journey
1. **`visualize_lineage`** - "Your Data Mash" visualization
   - Shows complete lineage from upload through all transformations
   - Creates graph with nodes and edges
   - Registers as Purpose-Bound Outcome (visualization)

2. **`map_relationships`** - Entity relationship mapping
   - Discovers entities within parsed data
   - Infers relationships between entities
   - Returns structured graph data

### Journey Flow
```
[User requests lineage/relationship visualization]
    ↓
[Choose visualization type]
    ├── File lineage ("Your Data Mash")
    │   ↓
    │   [visualize_lineage intent]
    │   ↓
    │   [LineageVisualizationService.visualize_lineage()]
    │   ↓
    │   [Query all lineage nodes from Supabase]
    │   [Build graph with nodes and edges]
    │
    └── Entity relationships
        ↓
        [map_relationships intent]
        ↓
        [DataAnalyzerService.map_relationships()]
        ↓
        [Entity detection and relationship inference]
    ↓
[Return visualization/mapping artifact]
    ↓
[Journey Complete]
```

### Expected Observable Artifacts

#### Lineage Visualization

| Artifact | Type | Description |
|----------|------|-------------|
| `lineage_visualization` | object | Complete lineage graph |
| `lineage_visualization.visualization_type` | string | "lineage_graph" |
| `lineage_visualization.lineage_graph` | object | Graph structure |
| `lineage_visualization.lineage_graph.nodes` | array | Graph nodes (file, parsed_result, embedding, etc.) |
| `lineage_visualization.lineage_graph.edges` | array | Graph edges (relationships) |
| `lineage_visualization.image_base64` | string | Optional rendered image |
| `artifact_id` | string | Artifact Plane reference |

#### Relationship Mapping

| Artifact | Type | Description |
|----------|------|-------------|
| `relationships` | object | Entity relationship mapping |
| `relationships.entities` | array | Discovered entities |
| `relationships.relationships` | array | Entity relationships with confidence |

### Node Types (Lineage Graph)

| Type | Description |
|------|-------------|
| `file` | Uploaded file |
| `parsed_result` | Parsed file result |
| `embedding` | Deterministic embedding |
| `interpretation` | Data interpretation |
| `analysis` | Analysis report |
| `guide` | Guide used for interpretation |
| `agent_session` | Agent conversation session |

### Idempotency Scope (Per Intent)

| Intent | Idempotency Key | Scope |
|--------|-----------------|-------|
| `visualize_lineage` | `hash(file_id + tenant_id)` | Same file = same lineage (current state) |
| `map_relationships` | `hash(parsed_file_id + tenant_id)` | Same file = same relationships |

### Journey Completion Definition

**Journey is considered complete when:**

* Visualization/mapping artifact returned
* Graph structure valid with nodes and edges
* For lineage: Registered in Artifact Plane

---

## 2. Scenario 1: Lineage Visualization Happy Path

### Test Description
"Your Data Mash" visualization generates successfully.

### Steps
1. [x] User has uploaded a file with processing history
2. [x] User triggers `visualize_lineage` with file_id
3. [x] LineageVisualizationService queries Supabase
4. [x] Graph built with all lineage nodes
5. [x] Visualization registered in Artifact Plane
6. [x] Lineage artifact returned

### Verification
- [x] `lineage_visualization` artifact returned
- [x] `lineage_graph.nodes` contains file and derived artifacts
- [x] `lineage_graph.edges` shows transformations
- [x] `artifact_id` in Artifact Plane

---

## 3. Scenario 2: Relationship Mapping Happy Path

### Test Description
Entity relationship mapping discovers meaningful relationships.

### Steps
1. [x] User has a parsed file
2. [x] User triggers `map_relationships` with parsed_file_id
3. [x] DataAnalyzerService detects entities
4. [x] DataAnalyzerService infers relationships
5. [x] Relationships artifact returned

### Verification
- [x] `relationships` artifact returned
- [x] `relationships.entities` contains discovered entities
- [x] `relationships.relationships` has confidence scores

---

## 4. Artifact Plane Integration

Lineage visualization registered as Purpose-Bound Outcome:

```python
artifact_result = await self.artifact_plane.create_artifact(
    artifact_type="visualization",
    artifact_id=f"lineage_viz_{file_id}",
    payload=artifact_payload,
    context=context,
    lifecycle_state="draft",
    owner="client",
    purpose="delivery",  # Visualizations are deliverables
    source_artifact_ids=[file_id]
)
```

---

## 5. Integration Points

### Platform Services
- **Insights Realm:** LineageVisualizationService, DataAnalyzerService
- **Artifact Plane:** Purpose-Bound Outcome registration
- **Public Works:** RegistryAbstraction (Supabase queries)

### Backend Handler
`symphainy_platform/realms/insights/orchestrators/insights_orchestrator.py::_handle_visualize_lineage`
`symphainy_platform/realms/insights/orchestrators/insights_orchestrator.py::_handle_map_relationships`

### Frontend API
`symphainy-frontend/shared/managers/InsightsAPIManager.ts::visualizeLineage()`
`symphainy-frontend/shared/managers/InsightsAPIManager.ts::mapRelationships()`
`symphainy-frontend/shared/managers/InsightsAPIManager.ts::getDataMashVisualization()`

---

## 6. Gate Status

**Journey is "done" only when:**
- [x] ✅ Lineage visualization happy path works
- [x] ✅ Relationship mapping happy path works
- [x] ✅ Artifact Plane registration works
- [x] ✅ Frontend integration works

**Current Status:** ✅ **IMPLEMENTED**

---

## 7. Related Documents

- **Intent Contract (Lineage):** `docs/intent_contracts/insights_lineage/intent_visualize_lineage.md`
- **Intent Contract (Relationships):** `docs/intent_contracts/insights_lineage/intent_map_relationships.md`
- **Analysis:** `docs/intent_contracts/INSIGHTS_REALM_ANALYSIS.md`

---

**Last Updated:** January 27, 2026  
**Owner:** Insights Realm Solution Team
