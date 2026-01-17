# Journey Realm Blueprint Gap Analysis

**Date:** January 2026  
**Status:** Gap Identified

---

## Gap Summary

Two gaps identified in Journey Realm:

1. **Blueprint Synthesis Gap:** `create_blueprint` exists but only returns a placeholder. It doesn't actually synthesize the coexistence analysis into a detailed, actionable blueprint.

2. **Solution Conversion Gap:** Journey Realm lacks the capability to convert blueprints into implementation-ready platform solutions (similar to how Outcomes Realm converts roadmaps/POCs into solutions).

---

## Current State

### 1. Blueprint Creation (Placeholder)

**Location:** `symphainy_platform/realms/journey/enabling_services/coexistence_analysis_service.py`

**Current Implementation:**
```python
async def create_blueprint(
    self,
    workflow_id: str,
    tenant_id: str,
    context: ExecutionContext
) -> Dict[str, Any]:
    # For MVP: Return placeholder
    # In full implementation: Create coexistence blueprint from analysis
    
    return {
        "workflow_id": workflow_id,
        "blueprint_id": f"blueprint_{workflow_id}",
        "blueprint_status": "created",
        "blueprint_content": {}  # Empty!
    }
```

**Problem:** Returns empty `blueprint_content`. Doesn't synthesize:
- Integration requirements from coexistence analysis
- Implementation steps
- Resource requirements
- Risk mitigation strategies
- Dependencies and sequencing

---

### 2. Solution Conversion (Missing)

**Outcomes Realm Has:**
- `create_solution` intent that converts roadmaps/POCs into platform solutions
- Uses `SolutionSynthesisService.create_solution_from_artifact()`
- Integrates with Solution SDK to create and register solutions

**Journey Realm Lacks:**
- No equivalent capability to convert blueprints into implementation-ready solutions
- Blueprints remain as documents, not executable solutions

---

## What Should Exist

### 1. Blueprint Synthesis

The `create_blueprint` should synthesize coexistence analysis into a comprehensive blueprint with visual workflow charts and responsibility matrix:

```python
{
    "blueprint_id": "blueprint_123",
    "workflow_id": "workflow_123",
    "current_state": {
        "description": "Existing process description...",
        "workflow_chart": {
            "image_base64": "...",
            "storage_path": "blueprints/blueprint_123_current_state.png"
        },
        "workflow_definition": {
            "steps": [...],
            "decision_points": [...],
            "actors": ["human", "legacy_system"]
        }
    },
    "coexistence_state": {
        "description": "Recommended process with Symphainy integration...",
        "workflow_chart": {
            "image_base64": "...",
            "storage_path": "blueprints/blueprint_123_coexistence_state.png"
        },
        "workflow_definition": {
            "steps": [...],
            "decision_points": [...],
            "actors": ["human", "symphainy", "legacy_system", "modern_system"]
        }
    },
    "roadmap": {
        "description": "How to transition from current to coexistence state",
        "phases": [
            {
                "phase": 1,
                "name": "Foundation Setup",
                "duration": "2 weeks",
                "objectives": [
                    "Set up Symphainy integration points",
                    "Configure data sync"
                ],
                "dependencies": []
            },
            {
                "phase": 2,
                "name": "Parallel Operation",
                "duration": "4 weeks",
                "objectives": [
                    "Run both processes in parallel",
                    "Validate coexistence"
                ],
                "dependencies": ["Phase 1"]
            },
            {
                "phase": 3,
                "name": "Full Migration",
                "duration": "2 weeks",
                "objectives": [
                    "Switch to coexistence state",
                    "Decommission old process"
                ],
                "dependencies": ["Phase 2"]
            }
        ],
        "timeline": {
            "start_date": "2026-02-01",
            "end_date": "2026-03-15",
            "total_duration": "8 weeks"
        }
    },
    "responsibility_matrix": {
        "description": "Who does what in the coexistence state",
        "responsibilities": [
            {
                "step": "Policy Data Ingestion",
                "human": ["Upload files", "Review exceptions"],
                "ai_symphainy": ["Parse files", "Extract data", "Quality assessment"],
                "system_technology": ["File storage", "Database operations"]
            },
            {
                "step": "Policy Validation",
                "human": ["Review flagged policies", "Approve exceptions"],
                "ai_symphainy": ["Validate data quality", "Flag anomalies"],
                "system_technology": ["Validation rules engine", "Status updates"]
            },
            {
                "step": "Policy Processing",
                "human": ["Handle complex cases", "Make decisions"],
                "ai_symphainy": ["Process standard policies", "Generate insights"],
                "system_technology": ["Workflow execution", "State management"]
            }
        ]
    },
    "sections": [
        {
            "section": "Executive Summary",
            "content": "This blueprint outlines the coexistence strategy..."
        },
        {
            "section": "Current State Analysis",
            "content": "Current process description and workflow..."
        },
        {
            "section": "Coexistence State Design",
            "content": "Recommended process with Symphainy integration..."
        },
        {
            "section": "Transition Roadmap",
            "content": "Phased approach to migration..."
        },
        {
            "section": "Responsibility Matrix",
            "content": "Clear delineation of human, AI, and system responsibilities..."
        },
        {
            "section": "Integration Requirements",
            "content": "Technical integration points and requirements...",
            "integration_points": [...],
            "resource_requirements": [...]
        },
        {
            "section": "Risk Mitigation",
            "content": "Identified risks and mitigation strategies...",
            "risks": [...],
            "mitigations": [...]
        }
    ],
    "metadata": {
        "created_date": "2026-01-15T10:00:00Z",
        "version": "1.0"
    }
}
```

### 2. Solution Conversion

Journey Realm should have an intent to convert blueprints into platform solutions:

**Proposed Intent:** `create_solution_from_blueprint`

**Parameters:**
- `blueprint_id` - Blueprint identifier
- `solution_options` - Options for solution creation

**Implementation:**
- Read blueprint from State Surface
- Extract integration requirements
- Use Solution SDK to create solution
- Register solution in Solution Registry
- Return solution ID

---

## Recommended Implementation

### Phase 1: Blueprint Synthesis

**Update:** `CoexistenceAnalysisService.create_blueprint()`

**Steps:**
1. Retrieve coexistence analysis results
2. **Retrieve current state workflow** (from existing process/workflow)
3. **Generate current state workflow chart** (using VisualGenerationService)
4. **Design coexistence state workflow** (integrate Symphainy into current process)
5. **Generate coexistence state workflow chart** (using VisualGenerationService)
6. **Create transition roadmap** (phased approach from current to coexistence)
7. **Generate responsibility matrix** (human, AI/Symphainy, system/technology for each step)
8. Synthesize into structured blueprint sections
9. Identify resource requirements
10. Create risk mitigation strategies
11. Return comprehensive blueprint with visual charts

**Key Components:**
- **Current State Workflow Chart:** Visual representation of existing process
- **Coexistence State Workflow Chart:** Visual representation of recommended process
- **Roadmap:** Phased transition plan with timeline
- **Responsibility Matrix:** Clear delineation of who does what

**Dependencies:**
- Coexistence analysis must be completed first
- Need access to current state workflow definition
- VisualGenerationService for workflow charts
- May need LLM for synthesis (or structured templates)

---

### Phase 2: Solution Conversion

**Add:** New intent `create_solution_from_blueprint` to Journey Orchestrator

**Implementation:**
1. Read blueprint from State Surface
2. Extract integration requirements from blueprint
3. Use `SolutionSynthesisService` (or create Journey-specific service)
4. Use Solution SDK to build solution
5. Register solution in Solution Registry
6. Return solution ID

**Service:** Could reuse `SolutionSynthesisService` from Outcomes Realm or create `JourneySolutionService`

---

## Alignment with Outcomes Realm

Outcomes Realm pattern:
1. `generate_roadmap` → Creates roadmap document
2. `create_poc` → Creates POC document
3. `create_solution` → Converts roadmap/POC into platform solution

Journey Realm should follow same pattern:
1. `analyze_coexistence` → Creates coexistence analysis
2. `create_blueprint` → Creates blueprint document (needs synthesis)
3. `create_solution_from_blueprint` → Converts blueprint into platform solution (missing)

---

## Recommendation

**Priority:** High

**Rationale:**
1. Blueprint synthesis is critical for making coexistence analysis actionable
2. Solution conversion completes the Journey Realm workflow
3. Aligns Journey Realm with Outcomes Realm pattern
4. Makes blueprints "implementation ready"

**Implementation Order:**
1. First: Implement blueprint synthesis in `create_blueprint`
2. Second: Add `create_solution_from_blueprint` intent
3. Third: Update documentation to reflect capabilities

---

## Blueprint Structure Details

### Current State Workflow Chart
- Visual representation of existing process
- Shows all steps, decision points, and actors
- Generated from existing workflow definition or process documentation
- Uses VisualGenerationService to create diagram

### Coexistence State Workflow Chart
- Visual representation of recommended process with Symphainy integration
- Shows how Symphainy enhances/automates steps
- Identifies integration points with existing systems
- Generated from coexistence analysis + current state
- Uses VisualGenerationService to create diagram

### Transition Roadmap
- Phased approach to move from current to coexistence state
- Includes:
  - Phase descriptions and objectives
  - Duration estimates
  - Dependencies between phases
  - Timeline with start/end dates
- Similar structure to Outcomes Realm roadmap but focused on process transition

### Responsibility Matrix
- Clear delineation of responsibilities for each step in coexistence state
- Three categories:
  - **Human:** Manual tasks, decisions, reviews, approvals
  - **AI/Symphainy:** Automated processing, analysis, insights, recommendations
  - **External Systems:** Client's external systems (Billing, CRM, Legacy systems, etc.) that we integrate with
- **Note:** Platform systems (storage, state management, databases) are a "black box" and not listed - they just work
- Helps stakeholders understand who/what is responsible for each step

## Questions for User

1. Should blueprint synthesis use LLM (like SOP generation) or structured templates?
2. Should `create_solution_from_blueprint` reuse `SolutionSynthesisService` or have its own service?
3. Should this be documented as a separate capability or part of coexistence analysis?
4. How should we retrieve the "current state" workflow? From existing workflow definition, process documentation, or user input?

---

**Status:** Ready for Implementation
