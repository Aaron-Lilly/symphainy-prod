# User Journey Flows

**Date:** January 25, 2026  
**Status:** ✅ **COMPLETE**  
**Purpose:** Comprehensive mapping of all user journeys through the platform

---

## Executive Summary

This document maps all user journeys through the Symphainy platform, showing how users interact with Content, Insights, Journey, and Outcomes pillars to achieve business outcomes. Each journey includes:
- User actions
- Intent submissions
- State transitions
- Data flow
- Cross-pillar integration points

---

## Journey 1: File Upload & Processing (Content Pillar)

### Flow Overview
User uploads file → Parse → Extract Metadata → Save → Ready for Analysis

### Step-by-Step Flow

**1. File Upload**
- **User Action:** Select file and click "Upload"
- **Intent:** `ingest_file`
- **Parameters:** `file` (File object)
- **State Update:** 
  - File stored as **Working Material** (temporary)
  - `state.realm.content.files` updated with file metadata
  - Execution tracked in `state.execution`
- **Result:** `file_id` returned

**2. File Parsing**
- **User Action:** Click "Parse" on uploaded file
- **Intent:** `parse_content`
- **Parameters:** `file_id`
- **State Update:**
  - Parsed file data stored in `state.realm.content.parsedFiles`
  - Structure/chunks extracted
- **Result:** `parsed_file_id`, `parsed_file_reference` returned

**3. Embedding Extraction**
- **User Action:** Click "Extract Embeddings" (optional, can be automatic)
- **Intent:** `extract_embeddings`
- **Parameters:** `parsed_file_id`, `parsed_file_reference`
- **State Update:**
  - Embeddings stored as **Working Material**
  - `state.realm.content.embeddings` updated
- **Data Class:** Working Material → Records of Fact (when promoted)
- **Result:** `embeddings_id` returned

**4. Save Materialization**
- **User Action:** Click "Save" to persist file
- **Intent:** `save_materialization` ⚠️ (currently direct API call)
- **Parameters:** `file_id`, `boundary_contract_id`
- **State Update:**
  - File persisted in Supabase
  - Registered in materialization store
- **Data Class:** Working Material → Records of Fact
- **Result:** File now persistent

**5. Semantic Interpretation** (Optional)
- **User Action:** Click "Get Semantic Interpretation"
- **Intent:** `get_semantic_interpretation`
- **Parameters:** `file_id`, `file_reference`
- **State Update:**
  - Interpretation stored in `state.realm.content.interpretations`
- **Result:** Semantic interpretation data

### Completion Criteria
- File uploaded
- File parsed
- Metadata extracted
- File saved (materialized)

### Cross-Pillar Integration
- **To Insights:** Parsed file available for quality assessment, interpretation, analysis
- **To Journey:** File can be used for SOP/workflow creation
- **To Outcomes:** File data available for synthesis

---

## Journey 2: Data Quality & Interpretation (Insights Pillar)

### Flow Overview
Select File → Assess Quality → Interpret Data → Visualize Lineage → Analyze

### Step-by-Step Flow

**1. File Selection**
- **User Action:** Select file from Content pillar or Insights file selector
- **State:** File ID stored in local state
- **Source:** `state.realm.content.files` or `state.realm.insights.selectedFileId`

**2. Data Quality Assessment**
- **User Action:** Click "Assess Data Quality"
- **Intent:** `assess_data_quality`
- **Parameters:** `parsed_file_id`, `source_file_id`, `parser_type`
- **State Update:**
  - Quality assessment stored in `state.realm.insights.qualityAssessments[parsedFileId]`
- **Result:** Quality assessment with scores (completeness, accuracy, consistency, issues)

**3. Data Interpretation** (Two Options)

**Option A: Self-Discovery**
- **User Action:** Click "Interpret Data (Self-Discovery)"
- **Intent:** `interpret_data_self_discovery`
- **Parameters:** `parsed_file_id`
- **State Update:**
  - Interpretation stored in `state.realm.insights.interpretations[parsedFileId]`
- **Data Class:** Working Material → Records of Fact (when promoted)
- **Result:** Entities, relationships, confidence score

**Option B: Guided Discovery**
- **User Action:** Click "Interpret Data (Guided)" and select guide
- **Intent:** `interpret_data_guided`
- **Parameters:** `parsed_file_id`, `guide_id`
- **State Update:**
  - Interpretation stored in `state.realm.insights.interpretations[parsedFileId]`
- **Data Class:** Working Material → Records of Fact (when promoted)
- **Result:** Entities, relationships (matched to guide), confidence score

**4. Lineage Visualization**
- **User Action:** Click "Visualize Lineage" (in "Your Data Mash" tab)
- **Intent:** `visualize_lineage`
- **Parameters:** `file_id`
- **State Update:**
  - Lineage visualization stored in `state.realm.insights.lineageVisualizations[fileId]`
- **Result:** Lineage graph (nodes, edges), visualization image
- **UI Component:** `YourDataMash.tsx`

**5. Relationship Mapping**
- **User Action:** Click "Map Relationships" (in "Relationships" tab)
- **Intent:** `map_relationships`
- **Parameters:** `file_id`
- **State Update:**
  - Relationship mappings stored in `state.realm.insights.relationshipMappings[fileId]`
- **Result:** Entities, relationships, metadata, statistics
- **UI Components:** `RelationshipMapping.tsx`, `RelationshipGraph.tsx`

**6. Data Analysis** (Two Options)

**Option A: Structured Data Analysis**
- **User Action:** Click "Analyze Structured Data"
- **Intent:** `analyze_structured_data`
- **Parameters:** `parsed_file_id`
- **State Update:**
  - Analysis stored in `state.realm.insights.analyses[parsedFileId]`
- **Result:** Analysis summary, insights, visualizations

**Option B: Unstructured Data Analysis**
- **User Action:** Click "Analyze Unstructured Data"
- **Intent:** `analyze_unstructured_data`
- **Parameters:** `parsed_file_id`
- **State Update:**
  - Analysis stored in `state.realm.insights.analyses[parsedFileId]`
- **Result:** Analysis summary, insights, visualizations

### Completion Criteria
- At least one analysis completed (quality, interpretation, lineage, or analysis)

### Cross-Pillar Integration
- **From Content:** Uses parsed files from Content pillar
- **To Journey:** Interpretations available for workflow/SOP creation
- **To Outcomes:** Analysis data available for synthesis

---

## Journey 3: Process Optimization & Coexistence (Journey Pillar)

### Flow Overview
Select SOP/Workflow → Optimize → Analyze Coexistence → Create Blueprint

### Step-by-Step Flow

**1. File Selection**
- **User Action:** Select SOP file and/or Workflow file
- **State:** Files stored in `selected` state
- **Source:** Files from Content pillar or Journey file selector

**2. Process Optimization** (Optional)
- **User Action:** Click "Optimize Process"
- **Intent:** `optimize_process`
- **Parameters:** `workflow_id`
- **State Update:**
  - Optimized process stored in `state.realm.journey.optimizedProcesses[workflowId]`
- **Result:** Optimizations, metrics (efficiency gain, time savings, cost reduction)

**3. SOP Generation** (If workflow selected)
- **User Action:** Click "Generate SOP"
- **Intent:** `generate_sop`
- **Parameters:** `workflow_id`
- **State Update:**
  - SOP stored in `state.realm.journey.sops[workflowId]`
- **Result:** SOP with title, content, sections

**4. Workflow Creation** (If SOP selected)
- **User Action:** Click "Create Workflow"
- **Intent:** `create_workflow`
- **Parameters:** `sop_id`
- **State Update:**
  - Workflow stored in `state.realm.journey.workflows[sopId]`
- **Result:** Workflow with steps, dependencies

**5. Coexistence Optimization** (Key Feature)
- **User Action:** Enter SOP content and Workflow content, click "Optimize Coexistence"
- **Intent:** `optimize_coexistence_with_content`
- **Parameters:** `sop_content`, `workflow_content`
- **State Update:**
  - Optimized coexistence stored in `state.realm.journey.operations`
    - `optimizedSop`
    - `optimizedWorkflow`
    - `blueprint`
    - `analysisComplete: true`
- **Result:** Optimized SOP, optimized workflow, blueprint, metrics
- **UI Component:** `CoexistenceBlueprint` (Journey pillar)

**6. Coexistence Analysis** (Alternative)
- **User Action:** Click "Analyze Coexistence"
- **Intent:** `analyze_coexistence`
- **Parameters:** `sop_id`, `workflow_id`
- **State Update:**
  - Analysis stored in `state.realm.journey.coexistenceAnalyses[analysisId]`
- **Result:** Coexistence opportunities, recommendations, blueprint

**7. Blueprint Creation** (Journey Realm)
- **User Action:** Click "Create Blueprint" (from optimized coexistence)
- **Intent:** `create_blueprint` (Journey realm)
- **Parameters:** `blueprint_data` (name, description, components)
- **State Update:**
  - Blueprint stored in `state.realm.journey.blueprints[blueprintId]`
- **Result:** Blueprint with visualization, components

### Completion Criteria
- SOP and/or Workflow created or optimized
- Coexistence analysis completed
- Blueprint created (optional)

### Cross-Pillar Integration
- **From Content:** Uses file content for SOP/workflow creation
- **From Insights:** Uses interpretations for process optimization
- **To Outcomes:** Blueprints available for solution creation

---

## Journey 4: Business Outcomes Synthesis (Outcomes Pillar)

### Flow Overview
Synthesize → Generate Roadmap/POC → Create Blueprint → Export Artifacts

### Step-by-Step Flow

**1. Outcome Synthesis**
- **User Action:** Click "Synthesize Outcome"
- **Intent:** `synthesize_outcome`
- **Parameters:** `synthesis_options` (optional)
- **State Update:**
  - Synthesis stored in `state.realm.outcomes.syntheses[synthesisId]`
- **Result:** Synthesis summary (content, insights, journey, overall), report
- **Data Source:** Aggregates data from Content, Insights, Journey realms

**2. Artifact Generation** (Three Options)

**Option A: Generate Roadmap**
- **User Action:** Enter goals, click "Generate Roadmap"
- **Intent:** `generate_roadmap`
- **Parameters:** `goals` (array of strings)
- **State Update:**
  - Roadmap stored in `state.realm.outcomes.roadmaps[roadmapId]`
  - **Lifecycle:** Purpose-Bound Outcome (draft → active → archived)
  - Lifecycle fields: `lifecycle_state`, `purpose`, `scope`, `owner`
- **Result:** Roadmap with phases, metrics (duration, cost)

**Option B: Create POC**
- **User Action:** Enter description, click "Create POC"
- **Intent:** `create_poc`
- **Parameters:** `description`
- **State Update:**
  - POC stored in `state.realm.outcomes.pocProposals[pocId]`
  - **Lifecycle:** Purpose-Bound Outcome (draft → active → archived)
  - Lifecycle fields: `lifecycle_state`, `purpose`, `scope`, `owner`
- **Result:** POC with objectives, scope, deliverables, duration

**Option C: Create Blueprint** (Outcomes Realm)
- **User Action:** Select workflow, click "Create Blueprint"
- **Intent:** `create_blueprint` (Outcomes realm)
- **Parameters:** `workflow_id`, `current_state_workflow_id` (optional)
- **State Update:**
  - Blueprint stored in `state.realm.outcomes.blueprints[blueprintId]`
  - **Lifecycle:** Purpose-Bound Outcome (draft → active → archived)
  - Lifecycle fields: `lifecycle_state`, `purpose`, `scope`, `owner`
- **Result:** Blueprint for coexistence planning

**3. Artifact Lifecycle Management**
- **User Action:** Transition artifact lifecycle state (draft → active → archived)
- **Intent:** `transition_artifact_lifecycle`
- **Parameters:** `artifact_id`, `artifact_type`, `current_state`, `target_state`, `reason` (optional)
- **State Update:**
  - Artifact lifecycle state updated in realm state
  - Transition history updated
- **Valid Transitions:**
  - `draft` → `active`
  - `draft` → `archived`
  - `active` → `archived`
- **Result:** Updated artifact with new lifecycle state

**4. Artifact Export**
- **User Action:** Select artifact, select format, click "Export"
- **Intent:** `export_artifact`
- **Parameters:** `artifact_type`, `artifact_id`, `format` ("json" | "docx" | "yaml")
- **State Update:** None (read-only)
- **Result:** Download URL, filename

**5. Solution Creation** (Optional)
- **User Action:** Create solution from roadmap, POC, or blueprint
- **Intent:** `create_solution`
- **Parameters:** `solution_source`, `source_id`, `source_data`, `solution_options` (optional)
- **State Update:**
  - Solution stored in `state.realm.outcomes.solutions[solutionId]`
- **Result:** Platform solution with domain bindings, intents, metadata

### Completion Criteria
- Synthesis completed
- At least one artifact generated (roadmap, POC, or blueprint)
- Artifact lifecycle managed (optional)

### Cross-Pillar Integration
- **From Content:** Uses file data for synthesis
- **From Insights:** Uses analysis data for synthesis
- **From Journey:** Uses blueprints, workflows, SOPs for synthesis
- **To Journey:** Solutions can inform workflow creation

---

## Journey 5: Complete End-to-End Flow

### Flow Overview
Upload File → Parse → Analyze → Optimize Process → Synthesize → Generate Artifact

### Complete Flow

**Phase 1: Content Ingestion**
1. Upload file → `ingest_file`
2. Parse file → `parse_content`
3. Extract embeddings → `extract_embeddings`
4. Save materialization → `save_materialization`

**Phase 2: Insights Analysis**
5. Assess quality → `assess_data_quality`
6. Interpret data → `interpret_data_self_discovery` or `interpret_data_guided`
7. Visualize lineage → `visualize_lineage`
8. Map relationships → `map_relationships`
9. Analyze data → `analyze_structured_data` or `analyze_unstructured_data`

**Phase 3: Journey Optimization**
10. Create/select workflow → `create_workflow` or select existing
11. Optimize coexistence → `optimize_coexistence_with_content`
12. Create blueprint → `create_blueprint` (Journey realm)

**Phase 4: Outcomes Synthesis**
13. Synthesize outcome → `synthesize_outcome`
14. Generate roadmap → `generate_roadmap` OR
15. Create POC → `create_poc` OR
16. Create blueprint → `create_blueprint` (Outcomes realm)
17. Export artifact → `export_artifact`

### Data Flow Through Journey

```
File Upload (Working Material)
  ↓
Parse → Embeddings (Working Material → Records of Fact)
  ↓
Interpretation (Working Material → Records of Fact)
  ↓
Analysis (Working Material)
  ↓
Process Optimization (Working Material)
  ↓
Coexistence Blueprint (Working Material)
  ↓
Synthesis (Working Material)
  ↓
Artifact (Purpose-Bound Outcome)
  ↓
Lifecycle Management (draft → active → archived)
```

---

## Journey 6: Cross-Pillar Integration Points

### Content → Insights
- **Trigger:** File parsed in Content pillar
- **Action:** File available for quality assessment, interpretation, analysis in Insights pillar
- **State:** `state.realm.content.parsedFiles` → `state.realm.insights.*`

### Insights → Journey
- **Trigger:** Data interpreted/analyzed in Insights pillar
- **Action:** Interpretations available for workflow/SOP creation in Journey pillar
- **State:** `state.realm.insights.interpretations` → `state.realm.journey.*`

### Journey → Outcomes
- **Trigger:** Blueprint/workflow created in Journey pillar
- **Action:** Blueprints available for solution creation in Outcomes pillar
- **State:** `state.realm.journey.blueprints` → `state.realm.outcomes.*`

### All Pillars → Outcomes
- **Trigger:** Data available in Content, Insights, Journey realms
- **Action:** Synthesis aggregates data from all realms
- **State:** `state.realm.content.*`, `state.realm.insights.*`, `state.realm.journey.*` → `state.realm.outcomes.syntheses`

---

## Journey 7: Artifact Lifecycle Management

### Flow Overview
Create Artifact → Transition Lifecycle → Archive

### Step-by-Step Flow

**1. Artifact Creation**
- **User Action:** Generate roadmap, create POC, or create blueprint
- **Intents:** `generate_roadmap`, `create_poc`, `create_blueprint`
- **State:** Artifact created with `lifecycle_state: 'draft'`
- **Lifecycle Fields:** `purpose`, `scope`, `owner`, `createdAt`

**2. Lifecycle Transition**
- **User Action:** Transition artifact state (e.g., draft → active)
- **Intent:** `transition_artifact_lifecycle`
- **Parameters:** `artifact_id`, `artifact_type`, `current_state`, `target_state`, `reason` (optional)
- **State Update:**
  - Artifact lifecycle state updated
  - Transition history updated
- **Valid Transitions:**
  - `draft` → `active`
  - `draft` → `archived`
  - `active` → `archived`

**3. Artifact Archival**
- **User Action:** Archive artifact (active → archived)
- **Intent:** `transition_artifact_lifecycle`
- **State:** Artifact marked as `archived` (terminal state)
- **Result:** Artifact no longer active, but preserved

### Lifecycle States
- **`draft`:** Initial state, can transition to `active` or `archived`
- **`active`:** Active state, can transition to `archived`
- **`archived`:** Terminal state, no transitions allowed

---

## Journey Summary

### Primary Journeys
1. **File Upload & Processing** (Content) - 5 steps
2. **Data Quality & Interpretation** (Insights) - 6 steps
3. **Process Optimization & Coexistence** (Journey) - 7 steps
4. **Business Outcomes Synthesis** (Outcomes) - 5 steps
5. **Complete End-to-End Flow** - 17 steps across all pillars
6. **Cross-Pillar Integration** - 4 integration points
7. **Artifact Lifecycle Management** - 3 steps

### Intent Usage by Journey
- **Content Journey:** 7 intents
- **Insights Journey:** 7 intents
- **Journey Journey:** 6 intents
- **Outcomes Journey:** 6 intents
- **Lifecycle Journey:** 1 intent

**Total Unique Intents:** 27 intents

---

## State Authority Model

### Runtime Authority
- All state updates go through Runtime
- Runtime is authoritative for committed execution and durable state
- Frontend state is ephemeral/speculative until Runtime confirms

### Realm State Structure
```
state.realm.content.*
  - files
  - parsedFiles
  - embeddings
  - interpretations

state.realm.insights.*
  - qualityAssessments
  - interpretations
  - lineageVisualizations
  - relationshipMappings
  - analyses

state.realm.journey.*
  - optimizedProcesses
  - sops
  - workflows
  - coexistenceAnalyses
  - blueprints
  - operations

state.realm.outcomes.*
  - syntheses
  - roadmaps
  - pocProposals
  - blueprints
  - solutions
```

---

## Notes

1. **Intent-Based Architecture:** All operations (except `save_materialization`) use intent-based API
2. **State Authority:** All state updates go through Runtime
3. **Data Classes:** Working Materials → Records of Fact → Purpose-Bound Outcomes
4. **Lifecycle Management:** Artifacts have explicit lifecycle states
5. **Cross-Pillar Integration:** Data flows seamlessly between pillars via realm state

---

**Prepared By:** Development Team  
**Date:** January 25, 2026  
**Status:** ✅ **COMPLETE**
