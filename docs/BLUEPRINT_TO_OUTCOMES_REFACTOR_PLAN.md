# Blueprint to Outcomes Realm Refactoring Plan

**Date:** January 2026  
**Status:** 📋 **PLANNING**  
**Purpose:** Move blueprint creation to Outcomes Realm and implement 3-artifact generation flow

---

## Executive Summary

This plan addresses the architectural correction to move blueprint creation from Journey/Operations Realm to Outcomes Realm, and implements the complete flow where:

1. **Solution Realm** shows summary visuals first
2. **User selects one of 3 artifacts** to generate:
   - Coexistence Blueprint
   - POC Proposal  
   - Roadmap
3. **Export Service** supports downloading all 3 artifacts
4. **Frontend** updated to reflect this flow

---

## Part 1: Current State Analysis

### Backend Current State

#### ✅ Outcomes Realm (Correct)
- **OutcomesOrchestrator** (`outcomes_orchestrator.py`):
  - ✅ `generate_roadmap` - Working
  - ✅ `create_poc` - Working
  - ❌ `create_blueprint` - **MISSING** (currently in Journey realm)

#### ❌ Journey Realm (Needs Refactoring)
- **JourneyOrchestrator** (`journey_orchestrator.py`):
  - ❌ `create_blueprint` - **SHOULD BE MOVED** to Outcomes realm
  - Uses `CoexistenceAnalysisService.create_blueprint()`

#### ✅ Export Service (Needs Enhancement)
- **ExportService** (`export_service.py`):
  - ✅ Currently exports solutions to migration engine format
  - ❌ **MISSING**: Export individual artifacts (Blueprint, POC, Roadmap)
  - ❌ **MISSING**: Format options for artifacts (PDF, DOCX, JSON)

### Frontend Current State

#### Business Outcomes Pillar
- **Page:** `app/(protected)/pillars/business-outcomes/page.tsx`
- **Current Flow:**
  1. Shows solution summary (if available)
  2. ❌ **MISSING**: Summary visualization
  3. ❌ **MISSING**: 3 artifact generation options
  4. ❌ **MISSING**: Export section for artifacts

---

## Part 2: Backend Refactoring Plan

### Task 2.1: Move Blueprint Creation to Outcomes Realm

**Files to Modify:**
1. `symphainy_platform/realms/outcomes/orchestrators/outcomes_orchestrator.py`
2. `symphainy_platform/realms/journey/orchestrators/journey_orchestrator.py` (remove)

**Changes:**

#### 2.1.1: Add Blueprint Handler to OutcomesOrchestrator

**File:** `outcomes_orchestrator.py`

**Add to `__init__`:**
```python
from ..enabling_services.coexistence_analysis_service import CoexistenceAnalysisService

# In __init__:
self.coexistence_analysis_service = CoexistenceAnalysisService(
    public_works=public_works,
    visual_generation_service=self.visual_generation_service
)
```

**Add to `handle_intent`:**
```python
elif intent_type == "create_blueprint":
    return await self._handle_create_blueprint(intent, context)
```

**Add new method:**
```python
async def _handle_create_blueprint(
    self,
    intent: Intent,
    context: ExecutionContext
) -> Dict[str, Any]:
    """
    Handle create_blueprint intent - create coexistence blueprint.
    
    ARCHITECTURAL PRINCIPLE: Blueprints are Purpose-Bound Outcomes.
    """
    workflow_id = intent.parameters.get("workflow_id")
    if not workflow_id:
        raise ValueError("workflow_id is required for create_blueprint intent")
    
    current_state_workflow_id = intent.parameters.get("current_state_workflow_id")
    
    # Create blueprint via CoexistenceAnalysisService
    blueprint_result = await self.coexistence_analysis_service.create_blueprint(
        workflow_id=workflow_id,
        tenant_id=context.tenant_id,
        context=context,
        current_state_workflow_id=current_state_workflow_id
    )
    
    blueprint_id = blueprint_result.get("blueprint_id")
    
    # Store in Artifact Plane (same pattern as roadmap/POC)
    artifact_payload = {
        "blueprint": blueprint_result,
        "current_state": blueprint_result.get("current_state", {}),
        "coexistence_state": blueprint_result.get("coexistence_state", {}),
        "roadmap": blueprint_result.get("roadmap", {}),
        "responsibility_matrix": blueprint_result.get("responsibility_matrix", {})
    }
    
    if self.artifact_plane:
        try:
            artifact_result = await self.artifact_plane.create_artifact(
                artifact_type="blueprint",
                artifact_id=blueprint_id,
                payload=artifact_payload,
                context=context,
                metadata={
                    "regenerable": True,
                    "retention_policy": "session"
                }
            )
            
            stored_artifact_id = artifact_result.get("artifact_id", blueprint_id)
            
            return {
                "artifacts": {
                    "blueprint_id": stored_artifact_id,
                    "blueprint": {
                        "result_type": "blueprint",
                        "semantic_payload": {
                            "blueprint_id": stored_artifact_id,
                            "execution_id": context.execution_id,
                            "session_id": context.session_id
                        },
                        "renderings": {}
                    }
                },
                "events": [
                    {
                        "type": "blueprint_created",
                        "blueprint_id": stored_artifact_id,
                        "session_id": context.session_id
                    }
                ]
            }
        except Exception as e:
            self.logger.error(f"Failed to store blueprint in Artifact Plane: {e}", exc_info=True)
    
    # Fallback (should not happen in production)
    return {
        "artifacts": {
            "blueprint": blueprint_result,
            "blueprint_id": blueprint_id
        },
        "events": [
            {
                "type": "blueprint_created",
                "blueprint_id": blueprint_id,
                "session_id": context.session_id
            }
        ]
    }
```

#### 2.1.2: Remove Blueprint Handler from JourneyOrchestrator

**File:** `journey_orchestrator.py`

**Remove:**
- `_handle_create_blueprint` method
- `create_blueprint` from `handle_intent`
- `coexistence_analysis_service` initialization (if only used for blueprints)

**Note:** Keep `coexistence_analysis_service` if used for `analyze_coexistence` intent.

**Estimated Time:** 2-3 hours

---

### Task 2.2: Update Solution Synthesis Service

**File:** `solution_synthesis_service.py`

**Current State:** Only supports "roadmap" and "poc" as `solution_source`

**Required Change:**
```python
# In create_solution_from_artifact:
if solution_source not in ["roadmap", "poc", "blueprint"]:
    raise ValueError(f"Invalid solution_source: {solution_source}. Must be 'roadmap', 'poc', or 'blueprint'")

# Add blueprint handling:
elif solution_source == "blueprint":
    blueprint = source_data.get("blueprint", {}) or source_data
    
    # Extract goals from blueprint roadmap
    roadmap = blueprint.get("roadmap", {})
    phases = roadmap.get("phases", [])
    for phase in phases:
        goals.append(f"Complete {phase.get('name', 'phase')}")
    
    # Extract constraints from coexistence analysis
    coexistence_state = blueprint.get("coexistence_state", {})
    integration_points = coexistence_state.get("integration_points", [])
    for point in integration_points:
        constraints.append(f"Integration: {point.get('system_name', 'system')}")
```

**Estimated Time:** 1 hour

---

### Task 2.3: Enhance Export Service for Artifacts

**File:** `export_service.py`

**Current State:** Only exports solutions to migration engine format

**Required Changes:**

#### 2.3.1: Add Artifact Export Method

```python
async def export_artifact(
    self,
    artifact_type: str,  # "blueprint", "poc", or "roadmap"
    artifact_id: str,
    export_format: str = "json",  # "json", "pdf", "docx", "yaml"
    context: ExecutionContext = None
) -> Dict[str, Any]:
    """
    Export artifact (Blueprint, POC, or Roadmap) to specified format.
    
    ARCHITECTURAL PRINCIPLE: Uses Artifact Plane to retrieve artifacts.
    
    Args:
        artifact_type: Type of artifact ("blueprint", "poc", "roadmap")
        artifact_id: Artifact identifier
        export_format: Export format ("json", "pdf", "docx", "yaml")
        context: Execution context
    
    Returns:
        Dict with export data and download URL
    """
    self.logger.info(f"Exporting {artifact_type} {artifact_id} as {export_format}")
    
    try:
        # Retrieve artifact from Artifact Plane
        if not self.public_works:
            raise ValueError("Public Works required for artifact export")
        
        artifact_storage = self.public_works.artifact_storage_abstraction
        if not artifact_storage:
            raise ValueError("Artifact Plane storage not available")
        
        # Get artifact
        artifact = await artifact_storage.get_artifact(
            artifact_id=artifact_id,
            tenant_id=context.tenant_id,
            include_payload=True
        )
        
        if not artifact:
            raise ValueError(f"Artifact {artifact_id} not found")
        
        artifact_data = artifact.get("payload", {})
        
        # Format based on export_format
        if export_format == "json":
            export_data = artifact_data
            export_content = json.dumps(export_data, indent=2)
            mime_type = "application/json"
            file_extension = "json"
        
        elif export_format == "yaml":
            import yaml
            export_data = artifact_data
            export_content = yaml.dump(export_data, default_flow_style=False)
            mime_type = "text/yaml"
            file_extension = "yaml"
        
        elif export_format == "pdf":
            # Generate PDF from artifact (requires PDF generation library)
            export_content = await self._generate_pdf(artifact_type, artifact_data, context)
            mime_type = "application/pdf"
            file_extension = "pdf"
        
        elif export_format == "docx":
            # Generate DOCX from artifact (requires DOCX generation library)
            export_content = await self._generate_docx(artifact_type, artifact_data, context)
            mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            file_extension = "docx"
        
        else:
            raise ValueError(f"Unsupported export format: {export_format}")
        
        # Store export file
        file_storage = self.public_works.get_file_storage_abstraction()
        if not file_storage:
            raise ValueError("File storage not available")
        
        export_filename = f"{artifact_type}_{artifact_id}.{file_extension}"
        storage_path = f"exports/{context.tenant_id}/{export_filename}"
        
        await file_storage.upload_file(
            storage_path=storage_path,
            file_content=export_content.encode('utf-8') if isinstance(export_content, str) else export_content,
            metadata={
                "artifact_type": artifact_type,
                "artifact_id": artifact_id,
                "export_format": export_format,
                "mime_type": mime_type
            }
        )
        
        # Generate download URL (or return storage path)
        download_url = f"/api/download/{storage_path}"  # Frontend will handle actual download
        
        return {
            "artifact_type": artifact_type,
            "artifact_id": artifact_id,
            "export_format": export_format,
            "download_url": download_url,
            "storage_path": storage_path,
            "file_size": len(export_content) if isinstance(export_content, str) else len(export_content),
            "mime_type": mime_type
        }
        
    except Exception as e:
        self.logger.error(f"Failed to export artifact: {e}", exc_info=True)
        return {
            "artifact_type": artifact_type,
            "artifact_id": artifact_id,
            "export_format": export_format,
            "error": str(e)
        }

async def _generate_pdf(
    self,
    artifact_type: str,
    artifact_data: Dict[str, Any],
    context: ExecutionContext
) -> bytes:
    """Generate PDF from artifact data (optional - DOCX is primary format)."""
    # For MVP: DOCX is primary format, PDF can be added later if needed
    # Could use: reportlab, weasyprint, or convert DOCX to PDF
    self.logger.info("PDF generation deferred - using DOCX as primary format")
    raise NotImplementedError("PDF generation not yet implemented - use DOCX format")

async def _generate_docx(
    self,
    artifact_type: str,
    artifact_data: Dict[str, Any],
    context: ExecutionContext
) -> bytes:
    """Generate DOCX from artifact data using python-docx."""
    try:
        from docx import Document
        from docx.shared import Inches, Pt
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        
        doc = Document()
        
        # Title
        title = doc.add_heading(f"{artifact_type.title()} Export", 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Metadata
        doc.add_paragraph(f"Generated: {datetime.utcnow().isoformat()}")
        doc.add_paragraph(f"Artifact ID: {artifact_data.get('blueprint_id') or artifact_data.get('proposal_id') or artifact_data.get('roadmap_id', 'N/A')}")
        doc.add_paragraph("")
        
        # Content based on artifact type
        if artifact_type == "blueprint":
            self._add_blueprint_content(doc, artifact_data)
        elif artifact_type == "poc":
            self._add_poc_content(doc, artifact_data)
        elif artifact_type == "roadmap":
            self._add_roadmap_content(doc, artifact_data)
        
        # Save to bytes
        import io
        doc_io = io.BytesIO()
        doc.save(doc_io)
        doc_io.seek(0)
        return doc_io.read()
        
    except ImportError:
        self.logger.error("python-docx not installed. Install with: pip install python-docx")
        raise
    except Exception as e:
        self.logger.error(f"Failed to generate DOCX: {e}", exc_info=True)
        raise

def _add_blueprint_content(self, doc, blueprint_data: Dict[str, Any]):
    """Add blueprint content to DOCX document."""
    # Current State
    doc.add_heading("Current State", 1)
    current_state = blueprint_data.get("current_state", {})
    doc.add_paragraph(current_state.get("description", "N/A"))
    
    # Coexistence State
    doc.add_heading("Coexistence State", 1)
    coexistence_state = blueprint_data.get("coexistence_state", {})
    doc.add_paragraph(coexistence_state.get("description", "N/A"))
    
    # Roadmap
    doc.add_heading("Transition Roadmap", 1)
    roadmap = blueprint_data.get("roadmap", {})
    phases = roadmap.get("phases", [])
    for phase in phases:
        doc.add_heading(f"Phase {phase.get('phase')}: {phase.get('name')}", 2)
        doc.add_paragraph(f"Duration: {phase.get('duration')}")
        for objective in phase.get("objectives", []):
            doc.add_paragraph(f"• {objective}", style='List Bullet')
    
    # Responsibility Matrix
    doc.add_heading("Responsibility Matrix", 1)
    matrix = blueprint_data.get("responsibility_matrix", {})
    responsibilities = matrix.get("responsibilities", [])
    for resp in responsibilities:
        doc.add_heading(resp.get("step", "Step"), 3)
        if resp.get("human"):
            doc.add_paragraph(f"Human: {', '.join(resp['human'])}")
        if resp.get("ai_symphainy"):
            doc.add_paragraph(f"AI/Symphainy: {', '.join(resp['ai_symphainy'])}")

def _add_poc_content(self, doc, poc_data: Dict[str, Any]):
    """Add POC proposal content to DOCX document."""
    proposal = poc_data.get("proposal", {}) or poc_data
    
    # Objectives
    doc.add_heading("Objectives", 1)
    for obj in proposal.get("objectives", []):
        doc.add_paragraph(f"• {obj}", style='List Bullet')
    
    # Scope
    doc.add_heading("Scope", 1)
    doc.add_paragraph(proposal.get("scope", "N/A"))
    
    # Timeline
    doc.add_heading("Timeline", 1)
    timeline = proposal.get("timeline", {})
    doc.add_paragraph(f"Start: {timeline.get('start_date', 'N/A')}")
    doc.add_paragraph(f"End: {timeline.get('end_date', 'N/A')}")
    doc.add_paragraph(f"Duration: {timeline.get('duration', 'N/A')}")
    
    # Resources
    doc.add_heading("Resources", 1)
    resources = proposal.get("resources", [])
    for resource in resources:
        doc.add_paragraph(f"• {resource}", style='List Bullet')

def _add_roadmap_content(self, doc, roadmap_data: Dict[str, Any]):
    """Add roadmap content to DOCX document."""
    roadmap = roadmap_data.get("roadmap", {}) or roadmap_data
    
    # Strategic Plan
    doc.add_heading("Strategic Plan", 1)
    strategic_plan = roadmap_data.get("strategic_plan", {})
    doc.add_paragraph(strategic_plan.get("overview", "N/A"))
    
    # Phases
    doc.add_heading("Phases", 1)
    phases = roadmap.get("phases", [])
    for phase in phases:
        doc.add_heading(f"Phase {phase.get('phase')}: {phase.get('name')}", 2)
        doc.add_paragraph(f"Duration: {phase.get('duration')}")
        for milestone in phase.get("milestones", []):
            doc.add_paragraph(f"• {milestone}", style='List Bullet')
    
    # Timeline
    doc.add_heading("Timeline", 1)
    timeline = roadmap.get("timeline", {})
    doc.add_paragraph(f"Start: {timeline.get('start_date', 'N/A')}")
    doc.add_paragraph(f"End: {timeline.get('end_date', 'N/A')}")
```

#### 2.3.2: Add Export Handler to OutcomesOrchestrator

**File:** `outcomes_orchestrator.py`

**Add to `handle_intent`:**
```python
elif intent_type == "export_artifact":
    return await self._handle_export_artifact(intent, context)
```

**Add new method:**
```python
async def _handle_export_artifact(
    self,
    intent: Intent,
    context: ExecutionContext
) -> Dict[str, Any]:
    """Handle export_artifact intent."""
    from ..enabling_services.export_service import ExportService
    
    export_service = ExportService(public_works=self.public_works)
    
    artifact_type = intent.parameters.get("artifact_type")
    artifact_id = intent.parameters.get("artifact_id")
    export_format = intent.parameters.get("export_format", "json")
    
    if not artifact_type or not artifact_id:
        raise ValueError("artifact_type and artifact_id are required")
    
    export_result = await export_service.export_artifact(
        artifact_type=artifact_type,
        artifact_id=artifact_id,
        export_format=export_format,
        context=context
    )
    
    return {
        "artifacts": {
            "export": export_result
        },
        "events": [
            {
                "type": "artifact_exported",
                "artifact_type": artifact_type,
                "artifact_id": artifact_id,
                "export_format": export_format
            }
        ]
    }
```

**Estimated Time:** 4-6 hours (including PDF/DOCX generation placeholders)

---

## Part 3: Frontend Refactoring Plan

### Task 3.1: Update Business Outcomes Page Structure

**File:** `app/(protected)/pillars/business-outcomes/page.tsx`

**Current Structure:**
```tsx
// Current: Shows solution summary (if available)
```

**Required Structure:**
```tsx
// New: Two-phase flow
// Phase 1: Summary Visualization
<SummaryVisualization solutionId={solutionId} />

// Phase 2: Artifact Generation Options
<ArtifactGenerationOptions 
  solutionId={solutionId}
  onArtifactGenerated={(type, id) => handleArtifactGenerated(type, id)}
/>

// Phase 3: Generated Artifacts Display
<GeneratedArtifactsDisplay 
  artifacts={artifacts}
  onExport={(type, id, format) => handleExport(type, id, format)}
/>
```

**Estimated Time:** 3-4 hours

---

### Task 3.2: Create Summary Visualization Component

**File:** `app/(protected)/pillars/business-outcomes/components/SummaryVisualization.tsx`

**Props:**
```typescript
interface SummaryVisualizationProps {
  solutionId?: string;
  onVisualizationReady?: (visualUrl: string) => void;
}
```

**Features:**
- Calls `synthesize_outcome` intent
- Displays three-column summary visualization:
  - **Content Pillar Column:**
    - File inventory (uploaded, parsed, embedded)
    - Embedding coverage chart
    - Target model status
  - **Insights Pillar Column:**
    - Data quality scorecard
    - Mapping completeness
    - Key insights summary
  - **Journey Pillar Column:**
    - Workflow/SOP inventory
    - Coexistence opportunities
    - Process optimization metrics
- Visual representation of solution overview

**Estimated Time:** 2-3 hours

---

### Task 3.3: Create Artifact Generation Options Component

**File:** `app/(protected)/pillars/business-outcomes/components/ArtifactGenerationOptions.tsx`

**Props:**
```typescript
interface ArtifactGenerationOptionsProps {
  solutionId?: string;
  onArtifactGenerated: (artifactType: 'blueprint' | 'poc' | 'roadmap', artifactId: string) => void;
}
```

**Features:**
- Three cards/buttons:
  1. **Coexistence Blueprint** - Calls `create_blueprint` intent
  2. **POC Proposal** - Calls `create_poc` intent
  3. **Roadmap** - Calls `generate_roadmap` intent
- Each card shows:
  - Icon
  - Title
  - Description
  - "Generate" button
- Loading states during generation
- Error handling

**Estimated Time:** 3-4 hours

---

### Task 3.4: Create Generated Artifacts Display Component

**File:** `app/(protected)/pillars/business-outcomes/components/GeneratedArtifactsDisplay.tsx`

**Props:**
```typescript
interface GeneratedArtifactsDisplayProps {
  artifacts: {
    blueprint?: { id: string; data: any };
    poc?: { id: string; data: any };
    roadmap?: { id: string; data: any };
  };
  onExport: (artifactType: string, artifactId: string, format: string) => void;
}
```

**Features:**
- **Modal Dialog** with tabs for each artifact type
- **Tab 1: Blueprint**
  - Current state workflow chart
  - Coexistence state workflow chart
  - Transition roadmap
  - Responsibility matrix
  - Export button (JSON, DOCX, YAML)
- **Tab 2: POC Proposal**
  - Objectives and scope
  - Timeline visualization
  - Resource requirements
  - Success criteria
  - Export button (JSON, DOCX, YAML)
- **Tab 3: Roadmap**
  - Strategic plan overview
  - Phase timeline
  - Milestones and dependencies
  - Export button (JSON, DOCX, YAML)
- Export handler calls `export_artifact` intent
- Reuses existing visualization components where possible

**Estimated Time:** 4-5 hours

---

### Task 3.5: Update OutcomesAPIManager

**File:** `shared/managers/OutcomesAPIManager.ts`

**Add Methods:**
```typescript
// Existing: synthesizeOutcome, generateRoadmap, createPoc

// NEW:
async createBlueprint(workflowId: string, currentStateWorkflowId?: string): Promise<BlueprintResponse> {
  // Call create_blueprint intent
}

async exportArtifact(
  artifactType: 'blueprint' | 'poc' | 'roadmap',
  artifactId: string,
  format: 'json' | 'pdf' | 'docx' | 'yaml' = 'json'
): Promise<ExportResponse> {
  // Call export_artifact intent
}
```

**Estimated Time:** 1-2 hours

---

### Task 3.6: Update State Management

**File:** `shared/state/PlatformStateProvider.tsx`

**Add to Outcomes State:**
```typescript
outcomes: {
  solution: Solution | null;
  summaryVisual: string | null;
  artifacts: {
    blueprint: Artifact | null;
    poc: Artifact | null;
    roadmap: Artifact | null;
  };
  exports: Export[];
}
```

**Estimated Time:** 1 hour

---

## Part 4: Integration Points

### Backend Intent Flow

```
Frontend → OutcomesOrchestrator
  ├─ synthesize_outcome → Summary visualization
  ├─ create_blueprint → Blueprint artifact
  ├─ create_poc → POC artifact
  ├─ generate_roadmap → Roadmap artifact
  └─ export_artifact → Export file (JSON/PDF/DOCX/YAML)
```

### Frontend Component Flow

```
Business Outcomes Page
  ├─ SummaryVisualization (Phase 1)
  ├─ ArtifactGenerationOptions (Phase 2)
  │   ├─ Generate Blueprint
  │   ├─ Generate POC
  │   └─ Generate Roadmap
  └─ GeneratedArtifactsDisplay (Phase 3)
      ├─ Blueprint Tab/Card
      ├─ POC Tab/Card
      ├─ Roadmap Tab/Card
      └─ Export Options (per artifact)
```

---

## Part 5: Implementation Timeline

### Phase 1: Backend Refactoring (8-10 hours) ✅ **COMPLETE**
- ✅ Task 2.1: Move blueprint to Outcomes realm (2-3h) - **DONE**
- ✅ Task 2.2: Update Solution Synthesis (1h) - **DONE**
- ✅ Task 2.3: Enhance Export Service (4-6h) - **DONE**
- ✅ Task 2.4: Update Summary Visualization (1h) - **DONE**

### Phase 2: Frontend Implementation (14-18 hours)
- ✅ Task 3.1: Update Business Outcomes Page (3-4h)
- ✅ Task 3.2: Summary Visualization Component (2-3h)
- ✅ Task 3.3: Artifact Generation Options (3-4h)
- ✅ Task 3.4: Generated Artifacts Display (4-5h)
- ✅ Task 3.5: Update OutcomesAPIManager (1-2h)
- ✅ Task 3.6: Update State Management (1h)

### Total Estimated Time: **22-28 hours** (3-4 days)

---

## Part 6: Acceptance Criteria

### Backend
- [ ] Blueprint creation moved to Outcomes realm
- [ ] Journey realm no longer handles blueprints
- [ ] Export service supports all 3 artifact types
- [ ] Export service supports JSON, PDF, DOCX, YAML formats
- [ ] Solution synthesis supports blueprints as source

### Frontend
- [ ] Business Outcomes page shows summary visualization first
- [ ] Three artifact generation options displayed
- [ ] Each artifact can be generated independently
- [ ] Generated artifacts displayed with previews
- [ ] Export functionality works for all 3 artifacts
- [ ] Export supports multiple formats

### Integration
- [ ] End-to-end flow: Summary → Generate → Preview → Export
- [ ] All artifacts stored in Artifact Plane
- [ ] Export files stored in File Storage
- [ ] Download URLs work correctly

---

## Part 7: Architecture Alignment

### ✅ Principles Maintained
- **Only Realms touch data** - Outcomes realm handles all artifact creation
- **Public Works abstractions** - All data access via abstractions
- **Artifact Plane** - All artifacts stored in Artifact Plane
- **Purpose-Bound Outcomes** - Blueprints, POCs, Roadmaps are Purpose-Bound Outcomes

### ✅ Benefits
- **Clear separation** - Journey realm for workflows, Outcomes realm for artifacts
- **Consistent pattern** - All 3 artifacts follow same generation/export pattern
- **Better UX** - Summary first, then user chooses what to generate
- **Export flexibility** - Multiple formats for different use cases

---

## Part 8: Decisions Made ✅

1. **PDF/DOCX Generation:**
   - ✅ **Decision:** Use DOCX format (python-docx library)
   - ✅ **Rationale:** More common than ODF, good library support
   - ✅ **Implementation:** Template-based DOCX generation for all 3 artifacts

2. **Summary Visualization:**
   - ✅ **Decision:** Reimagine with realm-specific visuals
   - ✅ **Content Pillar Visual:**
     - File inventory dashboard (uploaded files, parsing status)
     - Embedding coverage chart (deterministic + semantic)
     - Target model status
   - ✅ **Insights Pillar Visual:**
     - Data quality scorecard (overall quality, completeness, accuracy)
     - Mapping completeness chart (source-to-target matches)
     - Key insights summary (top patterns, relationships)
   - ✅ **Journey Pillar Visual:**
     - Workflow/SOP inventory
     - Coexistence opportunities chart
     - Process optimization metrics
   - ✅ **Combined Summary:** Three-column layout showing all pillar visuals

3. **Artifact Display:**
   - ✅ **Decision:** Tabs in modal dialog
   - ✅ **Rationale:** Lots of content to display, modal keeps focus
   - ✅ **Implementation:** Reuse existing display components where possible
   - ✅ **Tab Structure:**
     - Tab 1: Blueprint (workflow charts, responsibility matrix, roadmap)
     - Tab 2: POC Proposal (objectives, scope, timeline, resources)
     - Tab 3: Roadmap (phases, timeline, milestones, dependencies)

---

## Part 9: Next Steps

1. **Review and approve plan**
2. **Decide on PDF/DOCX approach** (MVP vs full implementation)
3. **Start with backend refactoring** (Phase 1)
4. **Then frontend implementation** (Phase 2)
5. **Integration testing** (end-to-end flow)

---

**Status:** Ready for review and approval
