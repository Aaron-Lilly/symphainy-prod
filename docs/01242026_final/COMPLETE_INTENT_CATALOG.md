# Complete Intent Catalog

**Date:** January 25, 2026  
**Status:** ✅ **COMPLETE**  
**Purpose:** Comprehensive catalog of all intents across all realms

---

## Executive Summary

This document catalogs all intents available in the Symphainy platform, organized by realm. Each intent includes:
- Intent name
- Realm
- Purpose
- Required parameters
- Optional parameters
- Return artifacts
- State updates

---

## Content Realm Intents

### 1. `ingest_file`

**Purpose:** Upload and ingest a file into the platform

**Realm:** `content`

**Required Parameters:**
- `file`: File object (from user upload)

**Optional Parameters:**
- `ingestion_type`: 'upload' (default)
- `boundary_contract_id`: Optional boundary contract ID

**Return Artifacts:**
- `file_id`: Unique identifier for the uploaded file
- `boundary_contract_id`: Boundary contract ID (if provided)

**State Updates:**
- Updates `content` realm state with file metadata
- Tracks execution status

**Flow:**
- User uploads file → `ingest_file` intent → File stored temporarily (Working Material)
- User must explicitly save via `save_materialization` to persist

**API Manager:** `ContentAPIManager.uploadFile()`

---

### 2. `save_materialization`

**Purpose:** Persist a materialized file (two-phase upload: upload → save)

**Realm:** `content`

**Required Parameters:**
- `file_id`: File identifier from `ingest_file`
- `boundary_contract_id`: Boundary contract ID

**Optional Parameters:**
- None

**Return Artifacts:**
- `materialization_id`: Persistent materialization identifier
- `file_id`: Confirmed file ID

**State Updates:**
- Updates `content` realm state with persisted file
- Registers file in Supabase

**Flow:**
- After `ingest_file` → User clicks "Save" → `save_materialization` intent → File persisted

**API Manager:** `ContentAPIManager.saveMaterialization()`

**Note:** ✅ PHASE 5.5: Migrated to intent-based API

---

### 3. `list_files`

**Purpose:** List all files for the current tenant

**Realm:** `content`

**Required Parameters:**
- `tenant_id`: Tenant identifier (from session)

**Optional Parameters:**
- None

**Return Artifacts:**
- `files`: Array of file metadata objects

**State Updates:**
- Updates `content` realm state with file list

**API Manager:** `ContentAPIManager.listFiles()`

---

### 4. `parse_content`

**Purpose:** Parse uploaded file content (extract structure, chunks, etc.)

**Realm:** `content`

**Required Parameters:**
- `file_id`: File identifier

**Optional Parameters:**
- `parser_type`: Parser type (if not auto-detected)
- `parser_options`: Parser-specific options

**Return Artifacts:**
- `parsed_file_id`: Identifier for parsed file
- `parsed_file_reference`: Reference to parsed file data
- `structure`: Extracted structure (if structured data)
- `chunks`: Extracted chunks (if unstructured data)

**State Updates:**
- Updates `content` realm state with parsed file data

**API Manager:** `ContentAPIManager.parseFile()`

---

### 5. `extract_embeddings`

**Purpose:** Extract semantic embeddings from parsed file

**Realm:** `content`

**Required Parameters:**
- `parsed_file_id`: Parsed file identifier
- `parsed_file_reference`: Reference to parsed file

**Optional Parameters:**
- `embedding_options`: Options for embedding extraction

**Return Artifacts:**
- `embeddings_id`: Identifier for extracted embeddings
- `embeddings`: Embedding vectors (or reference)
- `metadata`: Embedding metadata

**State Updates:**
- Updates `content` realm state with embeddings
- **Data Class:** Working Material → Records of Fact (when promoted)

**API Manager:** `ContentAPIManager.extractEmbeddings()`

---

### 6. `get_parsed_file`

**Purpose:** Retrieve parsed file data

**Realm:** `content`

**Required Parameters:**
- `file_id`: File identifier
- `file_reference`: File reference

**Optional Parameters:**
- None

**Return Artifacts:**
- `parsed_file`: Parsed file data
- `structure`: File structure
- `chunks`: File chunks

**State Updates:**
- Updates `content` realm state with parsed file (if not already present)

**API Manager:** `ContentAPIManager.getParsedFile()`

---

### 7. `get_semantic_interpretation`

**Purpose:** Retrieve semantic interpretation of file

**Realm:** `content`

**Required Parameters:**
- `file_id`: File identifier
- `file_reference`: File reference

**Optional Parameters:**
- None

**Return Artifacts:**
- `interpretation`: Semantic interpretation data
- `entities`: Extracted entities
- `relationships`: Extracted relationships

**State Updates:**
- Updates `content` realm state with interpretation (if not already present)

**API Manager:** `ContentAPIManager.getSemanticInterpretation()`

---

## Insights Realm Intents

### 8. `assess_data_quality`

**Purpose:** Assess quality of parsed data

**Realm:** `insights`

**Required Parameters:**
- `parsed_file_id`: Parsed file identifier
- `source_file_id`: Source file identifier
- `parser_type`: Parser type used

**Optional Parameters:**
- `quality_options`: Quality assessment options

**Return Artifacts:**
- `quality_assessment`: Quality assessment object
  - `quality_score`: Overall quality score
  - `completeness`: Completeness score
  - `accuracy`: Accuracy score
  - `consistency`: Consistency score
  - `issues`: Array of quality issues

**State Updates:**
- Updates `insights` realm state with quality assessment

**API Manager:** `InsightsAPIManager.assessDataQuality()`

---

### 9. `interpret_data_self_discovery`

**Purpose:** Interpret data using self-discovery (no guide)

**Realm:** `insights`

**Required Parameters:**
- `parsed_file_id`: Parsed file identifier

**Optional Parameters:**
- `discovery_options`: Self-discovery options

**Return Artifacts:**
- `interpretation`: Interpretation result
  - `interpretation_type`: "self_discovery"
  - `entities`: Extracted entities
  - `relationships`: Extracted relationships
  - `confidence_score`: Confidence score
  - `coverage_score`: Coverage score

**State Updates:**
- Updates `insights` realm state with interpretation
- **Data Class:** Working Material → Records of Fact (when promoted)

**API Manager:** `InsightsAPIManager.interpretDataSelfDiscovery()`

---

### 10. `interpret_data_guided`

**Purpose:** Interpret data using a guide (schema, ontology, etc.)

**Realm:** `insights`

**Required Parameters:**
- `parsed_file_id`: Parsed file identifier
- `guide_id`: Guide identifier (schema, ontology, etc.)

**Optional Parameters:**
- `matching_options`: Matching options for guide

**Return Artifacts:**
- `interpretation`: Interpretation result
  - `interpretation_type`: "guided"
  - `entities`: Extracted entities (matched to guide)
  - `relationships`: Extracted relationships (matched to guide)
  - `confidence_score`: Confidence score
  - `coverage_score`: Coverage score

**State Updates:**
- Updates `insights` realm state with interpretation
- **Data Class:** Working Material → Records of Fact (when promoted)

**API Manager:** `InsightsAPIManager.interpretDataGuided()`

---

### 11. `analyze_structured_data`

**Purpose:** Analyze structured data (tables, CSV, etc.)

**Realm:** `insights`

**Required Parameters:**
- `parsed_file_id`: Parsed file identifier

**Optional Parameters:**
- `analysis_options`: Analysis options

**Return Artifacts:**
- `structured_analysis`: Analysis result
  - `analysis_type`: "structured"
  - `summary`: Analysis summary
  - `insights`: Array of insights
  - `visualizations`: Array of visualization data

**State Updates:**
- Updates `insights` realm state with analysis

**API Manager:** `InsightsAPIManager.analyzeStructuredData()`

---

### 12. `analyze_unstructured_data`

**Purpose:** Analyze unstructured data (text, documents, etc.)

**Realm:** `insights`

**Required Parameters:**
- `parsed_file_id`: Parsed file identifier

**Optional Parameters:**
- `analysis_options`: Analysis options

**Return Artifacts:**
- `unstructured_analysis`: Analysis result
  - `analysis_type`: "unstructured"
  - `summary`: Analysis summary
  - `insights`: Array of insights
  - `visualizations`: Array of visualization data

**State Updates:**
- Updates `insights` realm state with analysis

**API Manager:** `InsightsAPIManager.analyzeUnstructuredData()`

---

### 13. `visualize_lineage`

**Purpose:** Visualize data lineage for a file

**Realm:** `insights`

**Required Parameters:**
- `file_id`: File identifier

**Optional Parameters:**
- None

**Return Artifacts:**
- `lineage_visualization`: Lineage visualization object
  - `visualization_type`: "lineage_graph"
  - `lineage_graph`: Lineage graph data (nodes, edges)
  - `image_base64`: Base64-encoded visualization image (optional)
  - `storage_path`: Path to stored visualization (optional)

**State Updates:**
- Updates `insights` realm state with lineage visualization
- Key: `state.realm.insights.lineageVisualizations[fileId]`

**API Manager:** `InsightsAPIManager.visualizeLineage()`

**UI Component:** `YourDataMash.tsx`

---

### 14. `map_relationships`

**Purpose:** Map entity relationships in parsed data

**Realm:** `insights`

**Required Parameters:**
- `file_id`: File identifier

**Optional Parameters:**
- None

**Return Artifacts:**
- `relationships`: Relationship mapping object
  - `entities`: Array of entities
  - `relationships`: Array of relationships (source, target, type)
  - `metadata`: Relationship metadata
  - `statistics`: Relationship statistics

**State Updates:**
- Updates `insights` realm state with relationship mappings
- Key: `state.realm.insights.relationshipMappings[fileId]`

**API Manager:** `InsightsAPIManager.mapRelationships()`

**UI Component:** `RelationshipMapping.tsx`, `RelationshipGraph.tsx`

---

## Journey Realm Intents

### 15. `optimize_process`

**Purpose:** Optimize a workflow process

**Realm:** `journey`

**Required Parameters:**
- `workflow_id`: Workflow identifier

**Optional Parameters:**
- `optimization_options`: Process optimization options

**Return Artifacts:**
- `optimized_process`: Optimized process object
  - `process_id`: Process identifier
  - `optimizations`: Array of optimizations
    - `type`: Optimization type
    - `description`: Optimization description
    - `impact`: Impact level ("low" | "medium" | "high")
    - `recommendation`: Optimization recommendation
  - `metrics`: Optimization metrics
    - `efficiency_gain`: Efficiency gain percentage
    - `time_savings`: Time savings estimate
    - `cost_reduction`: Cost reduction estimate

**State Updates:**
- Updates `journey` realm state with optimized process
- Key: `state.realm.journey.optimizedProcesses[workflowId]`

**API Manager:** `JourneyAPIManager.optimizeProcess()`

---

### 16. `generate_sop`

**Purpose:** Generate Standard Operating Procedure from workflow

**Realm:** `journey`

**Required Parameters:**
- `workflow_id`: Workflow identifier

**Optional Parameters:**
- `sop_options`: SOP generation options

**Return Artifacts:**
- `sop`: SOP object
  - `sop_id`: SOP identifier
  - `title`: SOP title
  - `content`: SOP content
  - `sections`: Array of SOP sections
  - `metadata`: SOP metadata

**State Updates:**
- Updates `journey` realm state with SOP
- Key: `state.realm.journey.sops[workflowId]`

**API Manager:** `JourneyAPIManager.generateSOP()`

---

### 17. `create_workflow`

**Purpose:** Create workflow from SOP

**Realm:** `journey`

**Required Parameters:**
- `sop_id`: SOP identifier

**Optional Parameters:**
- `workflow_options`: Workflow creation options

**Return Artifacts:**
- `workflow`: Workflow object
  - `workflow_id`: Workflow identifier
  - `name`: Workflow name
  - `steps`: Array of workflow steps
    - `id`: Step identifier
    - `name`: Step name
    - `type`: Step type
    - `dependencies`: Array of step dependencies
  - `metadata`: Workflow metadata

**State Updates:**
- Updates `journey` realm state with workflow
- Key: `state.realm.journey.workflows[sopId]`

**API Manager:** `JourneyAPIManager.createWorkflow()`

---

### 18. `optimize_coexistence_with_content`

**Purpose:** Optimize coexistence between SOP/workflow and content

**Realm:** `journey`

**Required Parameters:**
- `sop_content`: SOP content (string)
- `workflow_content`: Workflow content (string or object)

**Optional Parameters:**
- None

**Return Artifacts:**
- `optimized_coexistence`: Optimized coexistence object
  - `optimized_sop`: Optimized SOP
  - `optimized_workflow`: Optimized workflow
  - `blueprint`: Coexistence blueprint
  - `metrics`: Optimization metrics

**State Updates:**
- Updates `journey` realm state with optimized coexistence
- Key: `state.realm.journey.operations`
  - `optimizedSop`
  - `optimizedWorkflow`
  - `blueprint`
  - `analysisComplete`

**API Manager:** `JourneyAPIManager.optimizeCoexistenceWithContent()`

**UI Component:** `CoexistenceBlueprint` (Journey pillar)

**Note:** ✅ Migrated from legacy `OperationsService` to intent-based API

---

### 19. `analyze_coexistence`

**Purpose:** Analyze coexistence between SOP and workflow

**Realm:** `journey`

**Required Parameters:**
- `sop_id`: SOP identifier
- `workflow_id`: Workflow identifier

**Optional Parameters:**
- `analysis_options`: Coexistence analysis options

**Return Artifacts:**
- `coexistence_analysis`: Coexistence analysis object
  - `analysis_id`: Analysis identifier
  - `sop_id`: SOP identifier
  - `workflow_id`: Workflow identifier
  - `opportunities`: Array of coexistence opportunities
    - `type`: Opportunity type
    - `description`: Opportunity description
    - `potential_impact`: Potential impact
    - `recommendation`: Recommendation
  - `blueprint`: Coexistence blueprint (optional)

**State Updates:**
- Updates `journey` realm state with coexistence analysis
- Key: `state.realm.journey.coexistenceAnalyses[analysisId]`

**API Manager:** `JourneyAPIManager.analyzeCoexistence()`

---

### 20. `create_blueprint` (Journey Realm)

**Purpose:** Create coexistence blueprint

**Realm:** `journey`

**Required Parameters:**
- `blueprint_data`: Blueprint data object
  - `name`: Blueprint name (required)
  - `description`: Blueprint description (required)
  - `components`: Array of blueprint components (optional)

**Optional Parameters:**
- `blueprint_options`: Blueprint creation options

**Return Artifacts:**
- `blueprint`: Blueprint object
  - `blueprint_id`: Blueprint identifier
  - `name`: Blueprint name
  - `description`: Blueprint description
  - `visualization`: Blueprint visualization (optional)
  - `components`: Array of blueprint components

**State Updates:**
- Updates `journey` realm state with blueprint
- Key: `state.realm.journey.blueprints[blueprintId]`

**API Manager:** `JourneyAPIManager.createBlueprint()`

**Note:** Different from Outcomes realm `create_blueprint` (different purpose)

---

## Outcomes Realm Intents

### 21. `synthesize_outcome`

**Purpose:** Synthesize outcome from Content, Insights, and Journey data

**Realm:** `outcomes`

**Required Parameters:**
- None (uses synthesis_options)

**Optional Parameters:**
- `synthesis_options`: Synthesis options (defaults to empty object)

**Return Artifacts:**
- `synthesis_summary`: Synthesis summary object
  - `synthesis_id`: Synthesis identifier
  - `content_summary`: Content summary
  - `insights_summary`: Insights summary
  - `journey_summary`: Journey summary
  - `overall_synthesis`: Overall synthesis
  - `report`: Synthesis report (optional)
    - `report_id`: Report identifier
    - `report_type`: Report type
    - `content`: Report content
    - `format`: Report format

**State Updates:**
- Updates `outcomes` realm state with synthesis
- Key: `state.realm.outcomes.syntheses[synthesisId]`

**API Manager:** `OutcomesAPIManager.synthesizeOutcome()`

---

### 22. `generate_roadmap`

**Purpose:** Generate strategic roadmap

**Realm:** `outcomes`

**Required Parameters:**
- `goals`: Array of goal strings

**Optional Parameters:**
- `roadmap_options`: Roadmap generation options

**Return Artifacts:**
- `roadmap`: Roadmap object
  - `roadmap_id`: Roadmap identifier
  - `goals`: Array of goals
  - `status`: Roadmap status
  - `plan`: Array of roadmap phases
    - `phase`: Phase name
    - `description`: Phase description
  - `metrics`: Roadmap metrics
    - `estimated_duration_weeks`: Estimated duration
    - `estimated_cost_usd`: Estimated cost
  - `generated_at`: Generation timestamp
  - **Lifecycle:** `lifecycle_state`, `purpose`, `scope`, `owner` (via `ensureArtifactLifecycle`)

**State Updates:**
- Updates `outcomes` realm state with roadmap
- Key: `state.realm.outcomes.roadmaps[roadmapId]`

**API Manager:** `OutcomesAPIManager.generateRoadmap()`

**Lifecycle:** ✅ Purpose-Bound Outcome (draft → active → archived)

---

### 23. `create_poc`

**Purpose:** Create Proof of Concept proposal

**Realm:** `outcomes`

**Required Parameters:**
- `description`: POC description

**Optional Parameters:**
- `poc_options`: POC creation options

**Return Artifacts:**
- `poc_proposal`: POC proposal object
  - `poc_id`: POC identifier
  - `description`: POC description
  - `status`: POC status
  - `objectives`: Array of objectives
  - `scope`: POC scope
  - `deliverables`: Array of deliverables
  - `estimated_duration_weeks`: Estimated duration
  - `generated_at`: Generation timestamp
  - **Lifecycle:** `lifecycle_state`, `purpose`, `scope`, `owner` (via `ensureArtifactLifecycle`)

**State Updates:**
- Updates `outcomes` realm state with POC
- Key: `state.realm.outcomes.pocProposals[pocId]`

**API Manager:** `OutcomesAPIManager.createPOC()`

**Lifecycle:** ✅ Purpose-Bound Outcome (draft → active → archived)

---

### 24. `create_blueprint` (Outcomes Realm)

**Purpose:** Create blueprint from workflow (for coexistence planning)

**Realm:** `outcomes`

**Required Parameters:**
- `workflow_id`: Workflow identifier

**Optional Parameters:**
- `current_state_workflow_id`: Current state workflow ID (optional)

**Return Artifacts:**
- `blueprint`: Blueprint object
  - `blueprint_id`: Blueprint identifier
  - **Lifecycle:** `lifecycle_state`, `purpose`, `scope`, `owner` (via `ensureArtifactLifecycle`)

**State Updates:**
- Updates `outcomes` realm state with blueprint
- Key: `state.realm.outcomes.blueprints[blueprintId]`

**API Manager:** `OutcomesAPIManager.createBlueprint()`

**Lifecycle:** ✅ Purpose-Bound Outcome (draft → active → archived)

**Note:** Different from Journey realm `create_blueprint` (different purpose)

---

### 25. `export_artifact`

**Purpose:** Export artifact (roadmap, POC, blueprint) in various formats

**Realm:** `outcomes`

**Required Parameters:**
- `artifact_type`: Artifact type ("blueprint" | "poc" | "roadmap")
- `artifact_id`: Artifact identifier
- `format`: Export format ("json" | "docx" | "yaml")

**Optional Parameters:**
- None

**Return Artifacts:**
- `export`: Export object
  - `download_url`: Download URL for exported artifact
  - `filename`: Export filename

**State Updates:**
- None (export is read-only)

**API Manager:** `OutcomesAPIManager.exportArtifact()`

---

### 26. `create_solution`

**Purpose:** Create platform solution from roadmap, POC, or blueprint

**Realm:** `outcomes`

**Required Parameters:**
- `solution_source`: Source type ("roadmap" | "poc" | "blueprint")
- `source_id`: Source identifier
- `source_data`: Source data object

**Optional Parameters:**
- `solution_options`: Solution creation options

**Return Artifacts:**
- `platform_solution`: Platform solution object
  - `solution_id`: Solution identifier
  - `name`: Solution name (optional)
  - `description`: Solution description (optional)
  - `domain_bindings`: Array of domain bindings
    - `domain`: Domain name
    - `system_name`: System name
    - `adapter_type`: Adapter type
  - `intents`: Array of intent names
  - `metadata`: Solution metadata

**State Updates:**
- Updates `outcomes` realm state with solution
- Key: `state.realm.outcomes.solutions[solutionId]`

**API Manager:** `OutcomesAPIManager.createSolution()`

---

## Artifact Lifecycle Intent

### 27. `transition_artifact_lifecycle`

**Purpose:** Transition artifact lifecycle state (draft → active → archived)

**Realm:** `outcomes` or `journey`

**Required Parameters:**
- `artifact_id`: Artifact identifier
- `artifact_type`: Artifact type ("blueprint" | "poc" | "roadmap" | "sop" | "workflow")
- `current_state`: Current lifecycle state
- `target_state`: Target lifecycle state

**Optional Parameters:**
- `reason`: Reason for transition (optional)

**Return Artifacts:**
- `artifact`: Updated artifact with new lifecycle state
- `transition_history`: Updated transition history

**State Updates:**
- Updates artifact lifecycle state in realm state
- Updates transition history

**API Manager:** `useArtifactLifecycle.transitionLifecycle()`

**Lifecycle States:**
- `draft`: Initial state, can transition to `active` or `archived`
- `active`: Active state, can transition to `archived`
- `archived`: Terminal state, no transitions allowed

**Valid Transitions:**
- `draft` → `active`
- `draft` → `archived`
- `active` → `archived`

---

## Intent Summary by Realm

### Content Realm (7 intents)
1. `ingest_file`
2. `save_materialization` ⚠️ (direct API call, should be intent-based)
3. `list_files`
4. `parse_content`
5. `extract_embeddings`
6. `get_parsed_file`
7. `get_semantic_interpretation`

### Insights Realm (7 intents)
8. `assess_data_quality`
9. `interpret_data_self_discovery`
10. `interpret_data_guided`
11. `analyze_structured_data`
12. `analyze_unstructured_data`
13. `visualize_lineage`
14. `map_relationships`

### Journey Realm (6 intents)
15. `optimize_process`
16. `generate_sop`
17. `create_workflow`
18. `optimize_coexistence_with_content`
19. `analyze_coexistence`
20. `create_blueprint` (Journey)

### Outcomes Realm (6 intents)
21. `synthesize_outcome`
22. `generate_roadmap`
23. `create_poc`
24. `create_blueprint` (Outcomes)
25. `export_artifact`
26. `create_solution`

### Artifact Lifecycle (1 intent)
27. `transition_artifact_lifecycle`

**Total: 27 intents**

---

## Intent Execution Flow

All intents follow this flow:

```
User Action (UI)
  ↓
API Manager Method
  ↓
Parameter Validation (✅ Issue 3 Fix)
  ↓
Session Validation (✅ Issue 4 Fix)
  ↓
submitIntent(intent_type, parameters)
  ↓
Experience Plane Client
  ↓
Runtime (ExecutionLifecycleManager)
  ↓
Realm Orchestrator
  ↓
Realm Services
  ↓
Public Works Abstractions
  ↓
Infrastructure (Supabase, GCS, etc.)
  ↓
Execution Result
  ↓
Realm State Update
  ↓
UI Update (via PlatformStateProvider)
```

---

## Data Class Transitions

### Working Materials → Records of Fact
- **Embeddings:** Created via `extract_embeddings` → Promoted to Records of Fact
- **Interpretations:** Created via `interpret_data_*` → Promoted to Records of Fact

### Records of Fact → Purpose-Bound Outcomes
- **Artifacts:** Created via `generate_roadmap`, `create_poc`, `create_blueprint` → Purpose-Bound Outcomes with lifecycle

### Ephemeral → Working Materials
- **File Upload:** `ingest_file` → Working Material (temporary)
- **File Save:** `save_materialization` → Persisted (Records of Fact)

---

## Notes

1. **Intent-Based Architecture:** All operations (except `save_materialization`) use intent-based API
2. **Parameter Validation:** All intents have parameter validation (✅ Issue 3 Fix)
3. **Session Validation:** All intents have session validation (✅ Issue 4 Fix)
4. **State Authority:** All state updates go through Runtime (✅ Issue 1 Fix)
5. **Visualization Data:** All visualizations read from Runtime state (✅ Issue 2 Fix)

---

**Prepared By:** Development Team  
**Date:** January 25, 2026  
**Status:** ✅ **COMPLETE**
