# Journey Realm: Detailed Gap Analysis & Implementation Plan

**Status:** Detailed Gap Analysis  
**Created:** January 2026  
**Goal:** Complete gap analysis for Journey Realm (Operations Pillar) with implementation details

---

## Executive Summary

The Journey Realm (Operations Pillar) requires:
1. **Visual Generation** - Create visuals from embeddings (workflows, SOPs)
2. **SOP from Chat** - Generate SOPs from interactive chat
3. **Coexistence Analysis** - Human+AI optimization opportunities
4. **Blueprint to Journey** - Convert blueprints to platform journeys
5. **Complete Lineage Tracking** - Link all artifacts to source files

---

## MVP Showcase Requirements

From `mvp_showcase_description.md`:

> "An operations pillar (showcasing the journey realm) that uses the semantic embeddings from user's uploaded workflow and/or SOP files to create visuals of both (generating one from the other) or to generate an SOP from scratch via interactive chat and analyzes those for coexistence (human+AI) optimization opportunities and creates a coexistence blueprint for the optimized process. Finally it turns that blueprint into an actual platform journey that our development teams can start bringing to life."

### Required Features

1. **Visual Generation from Embeddings**
   - Create workflow visuals from embeddings
   - Create SOP visuals from embeddings
   - Generate workflow from SOP (with visual)
   - Generate SOP from workflow (with visual)

2. **SOP from Interactive Chat**
   - Generate SOP from scratch via chat
   - Interactive conversation to build SOP
   - Visual generation for chat-generated SOP

3. **Coexistence Analysis**
   - Analyze workflows/SOPs for human+AI opportunities
   - Identify optimization opportunities
   - Create coexistence blueprint

4. **Blueprint to Journey**
   - Convert blueprint to platform journey
   - Journey stored in Supabase (solution)
   - Lineage maintained (blueprint → journey)

---

## Current Implementation Status

### Existing Capabilities

| Capability | Status | Implementation | Notes |
|------------|--------|----------------|-------|
| Generate SOP | ⚠️ Partial | `generate_sop` intent | Exists but needs validation |
| Create workflow | ⚠️ Partial | `create_workflow` intent | Exists but needs validation |
| Workflow ↔ SOP conversion | ⚠️ Partial | Both intents exist | Needs validation |
| Analyze coexistence | ⚠️ Partial | `analyze_coexistence` intent | Needs validation |
| Create blueprint | ⚠️ Partial | `create_blueprint` intent | Needs validation |
| Create solution (from blueprint) | ⚠️ Partial | `create_solution` intent | Needs validation |

### Missing Capabilities

| Capability | Status | Gap |
|------------|--------|-----|
| Visual generation | ❌ Missing | **GAP** - No visual generation service |
| SOP from chat | ❌ Missing | **GAP** - No chat integration |
| Visual generation from embeddings | ❌ Missing | **GAP** - No embedding-based visuals |
| Complete lineage tracking | ❌ Missing | **GAP** - No lineage links to source files |

---

## Detailed Gap Analysis

### Gap 1: Visual Generation Service

**Requirement:** Create visuals of workflows and SOPs (generating one from the other)

**Current State:**
- No visual generation service exists
- No diagram/flowchart generation
- No visual storage in GCS

**Required Implementation:**

#### 1.1: Visual Generation Service

**File:** `symphainy_platform/realms/journey/enabling_services/visual_generation_service.py`

**Methods:**
```python
async def generate_workflow_visual(
    self,
    workflow_id: str,
    workflow_data: Dict[str, Any],
    embeddings: Optional[List[Dict[str, Any]]] = None,
    tenant_id: str,
    context: ExecutionContext
) -> Dict[str, Any]:
    """
    Generate workflow visual from workflow data and/or embeddings.
    
    Uses embeddings to enhance visual with semantic context.
    Returns visual file path in GCS.
    """

async def generate_sop_visual(
    self,
    sop_id: str,
    sop_data: Dict[str, Any],
    embeddings: Optional[List[Dict[str, Any]]] = None,
    tenant_id: str,
    context: ExecutionContext
) -> Dict[str, Any]:
    """
    Generate SOP visual from SOP data and/or embeddings.
    
    Uses embeddings to enhance visual with semantic context.
    Returns visual file path in GCS.
    """
```

**Visual Generation Options:**
- **Mermaid diagrams** - Flowcharts, sequence diagrams
- **Graphviz** - Complex graph visualizations
- **SVG/PNG** - Raster/vector output
- **Interactive HTML** - Clickable flowcharts

**Storage:** GCS bucket `tenant/{tenant_id}/visuals/`

**Lineage:** Track in Supabase `visuals` table (link to source file, workflow, SOP)

#### 1.2: Integration with Workflow/SOP Generation

**When workflow/SOP generated:**
1. Generate workflow/SOP content
2. Generate embeddings (if not already generated)
3. Call visual generation service
4. Store visual in GCS
5. Track visual in Supabase with lineage

---

### Gap 2: SOP from Interactive Chat

**Requirement:** Generate an SOP from scratch via interactive chat

**Current State:**
- No chat integration
- No interactive SOP generation
- No chat session management

**Required Implementation:**

#### 2.1: Chat Integration

**File:** `symphainy_platform/realms/journey/orchestrators/journey_orchestrator.py`

**New Intent:** `generate_sop_from_chat`

**Parameters:**
```json
{
    "intent_type": "generate_sop_from_chat",
    "parameters": {
        "chat_session_id": "...",
        "chat_messages": [...],
        "sop_context": {...}
    }
}
```

**Flow:**
1. Receive chat messages
2. Use Journey Liaison Agent to interpret chat
3. Build SOP structure from chat conversation
4. Generate SOP content
5. Generate SOP visual
6. Store SOP in GCS
7. Track SOP in Supabase with lineage

#### 2.2: Journey Liaison Agent Integration

**File:** `symphainy_platform/realms/journey/agents/journey_liaison_agent.py`

**Capabilities:**
- Interpret chat messages for SOP requirements
- Ask clarifying questions
- Build SOP structure interactively
- Validate SOP completeness

---

### Gap 3: Enhanced Coexistence Analysis

**Requirement:** Analyze workflows/SOPs for coexistence (human+AI) optimization opportunities

**Current State:**
- `analyze_coexistence` intent exists but needs enhancement
- May not identify all human+AI opportunities
- May not create comprehensive blueprints

**Required Implementation:**

#### 3.1: Enhanced Coexistence Analysis Service

**File:** `symphainy_platform/realms/journey/enabling_services/coexistence_analysis_service.py`

**Enhancements:**
1. **Human Task Identification:**
   - Identify tasks best suited for humans
   - Identify tasks requiring human judgment
   - Identify tasks requiring creativity

2. **AI Task Identification:**
   - Identify tasks best suited for AI
   - Identify repetitive tasks
   - Identify data processing tasks

3. **Optimization Opportunities:**
   - Identify handoff points
   - Identify bottlenecks
   - Identify automation opportunities
   - Identify collaboration opportunities

4. **Blueprint Generation:**
   - Create coexistence blueprint
   - Define human+AI roles
   - Define handoff protocols
   - Define collaboration patterns

**Output:**
```json
{
    "coexistence_analysis": {
        "human_tasks": [...],
        "ai_tasks": [...],
        "optimization_opportunities": [...],
        "blueprint": {
            "human_roles": [...],
            "ai_roles": [...],
            "handoff_points": [...],
            "collaboration_patterns": [...]
        }
    }
}
```

---

### Gap 4: Blueprint to Journey Conversion

**Requirement:** Turn blueprint into an actual platform journey

**Current State:**
- `create_solution` intent exists but needs validation
- May not properly convert blueprints to journeys
- May not maintain proper lineage

**Required Implementation:**

#### 4.1: Blueprint to Journey Converter

**File:** `symphainy_platform/realms/journey/enabling_services/journey_converter_service.py`

**Methods:**
```python
async def convert_blueprint_to_journey(
    self,
    blueprint_id: str,
    blueprint_data: Dict[str, Any],
    tenant_id: str,
    context: ExecutionContext
) -> Dict[str, Any]:
    """
    Convert coexistence blueprint to platform journey.
    
    Creates:
    - Journey structure
    - Solution model
    - Context and bindings
    - Sync strategies
    
    Stores in Supabase (solutions table).
    Maintains lineage (blueprint → journey).
    """
```

**Journey Structure:**
- Solution model (context, bindings, sync strategies)
- Journey steps (human tasks, AI tasks, handoffs)
- Journey metadata (source blueprint, lineage)

**Storage:** Supabase `solutions` table

**Lineage:** Link journey to blueprint in Supabase

---

### Gap 5: Complete Lineage Tracking

**Requirement:** Link all Journey Realm artifacts to source files

**Current State:**
- No lineage tracking for workflows
- No lineage tracking for SOPs
- No lineage tracking for blueprints
- No lineage tracking for journeys

**Required Implementation:**

#### 5.1: Supabase Tables

**Tables to create:**
1. `workflows` - Track workflows, link to source files
2. `sops` - Track SOPs, link to source files/workflows
3. `blueprints` - Track blueprints, link to source workflows/SOPs
4. `journeys` - Track journeys, link to blueprints
5. `visuals` - Track visuals, link to workflows/SOPs

**Schema Examples:**

**`workflows` table:**
```sql
CREATE TABLE workflows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    workflow_id TEXT NOT NULL,
    file_id UUID REFERENCES files(id),  -- Source file
    gcs_path TEXT NOT NULL,
    visual_path TEXT,  -- Link to visual
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(tenant_id, workflow_id)
);
```

**`sops` table:**
```sql
CREATE TABLE sops (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    sop_id TEXT NOT NULL,
    file_id UUID REFERENCES files(id),  -- Source file (if from file)
    workflow_id UUID REFERENCES workflows(id),  -- Source workflow (if from workflow)
    chat_session_id TEXT,  -- If from chat
    gcs_path TEXT NOT NULL,
    visual_path TEXT,  -- Link to visual
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(tenant_id, sop_id)
);
```

**`blueprints` table:**
```sql
CREATE TABLE blueprints (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    blueprint_id TEXT NOT NULL,
    workflow_id UUID REFERENCES workflows(id),  -- Source workflow
    sop_id UUID REFERENCES sops(id),  -- Source SOP
    gcs_path TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(tenant_id, blueprint_id)
);
```

**`journeys` table:**
```sql
CREATE TABLE journeys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    journey_id TEXT NOT NULL,
    blueprint_id UUID REFERENCES blueprints(id),  -- Source blueprint
    solution_id UUID,  -- Solution in Supabase
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(tenant_id, journey_id)
);
```

**`visuals` table:**
```sql
CREATE TABLE visuals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    visual_id TEXT NOT NULL,
    visual_type TEXT NOT NULL,  -- "workflow" | "sop" | "blueprint" | "journey"
    source_id UUID,  -- Link to workflow/sop/blueprint/journey
    gcs_path TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(tenant_id, visual_id)
);
```

#### 5.2: Data Brain Integration

**Register references:**
- Workflow references
- SOP references
- Blueprint references
- Journey references
- Visual references

**Track provenance:**
- Workflow → file
- SOP → workflow/file/chat
- Blueprint → workflow/SOP
- Journey → blueprint
- Visual → workflow/SOP/blueprint/journey

---

## Implementation Plan

### Phase 1: Visual Generation (Week 1-2)
1. Visual Generation Service
2. Workflow visual generation
3. SOP visual generation
4. Visual storage in GCS
5. Visual tracking in Supabase
6. E2E tests

### Phase 2: SOP from Chat (Week 2-3)
7. Chat integration
8. Journey Liaison Agent enhancement
9. `generate_sop_from_chat` intent
10. Interactive SOP generation
11. E2E tests

### Phase 3: Enhanced Coexistence Analysis (Week 3-4)
12. Enhanced coexistence analysis service
13. Human+AI task identification
14. Optimization opportunity identification
15. Blueprint generation
16. E2E tests

### Phase 4: Blueprint to Journey (Week 4-5)
17. Journey converter service
18. Blueprint to journey conversion
19. Solution model creation
20. Journey storage in Supabase
21. E2E tests

### Phase 5: Complete Lineage Tracking (Week 5-6)
22. Supabase tables (workflows, sops, blueprints, journeys, visuals)
23. Lineage tracking in all orchestrators
24. Data Brain integration
25. E2E test: Complete lineage chain

---

## Success Criteria

✅ **Visual Generation:**
- Workflow visuals generated from embeddings
- SOP visuals generated from embeddings
- Visuals stored in GCS
- Visuals tracked in Supabase with lineage

✅ **SOP from Chat:**
- Interactive chat works
- SOP generated from chat
- SOP visual generated
- SOP tracked with lineage

✅ **Coexistence Analysis:**
- Human+AI opportunities identified
- Optimization opportunities identified
- Blueprint created
- Blueprint tracked with lineage

✅ **Blueprint to Journey:**
- Blueprint converted to journey
- Journey stored in Supabase
- Lineage maintained (blueprint → journey)

✅ **Complete Lineage:**
- All artifacts link to source files
- Full provenance chain queryable
- Data Brain integration complete
