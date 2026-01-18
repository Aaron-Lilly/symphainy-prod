# Outcomes Realm: Detailed Gap Analysis & Implementation Plan

**Status:** Detailed Gap Analysis  
**Created:** January 2026  
**Goal:** Complete gap analysis for Outcomes Realm (Business Outcomes Pillar) with implementation details

---

## Executive Summary

The Outcomes Realm (Business Outcomes Pillar) requires:
1. **Summary Visual** - Visual summary of outputs from all realms
2. **Roadmap Generation** - Generate roadmap from realm summaries
3. **POC Proposal** - Generate POC proposal from realm summaries
4. **Solution Creation** - Convert roadmap/POC to platform solutions
5. **Complete Lineage Tracking** - Link all artifacts to source realm outputs

---

## MVP Showcase Requirements

From `mvp_showcase_description.md`:

> "A business outcomes pillar (showcasing the solution realm) that creates a summary visual of the outputs from the other realms and then uses those to generate a roadmap and a POC proposal and turns both the roadmap and the POC proposal into platform solutions that our development teams can start bringing to life."

### Required Features

1. **Summary Visual**
   - Visual summary of Content Realm outputs
   - Visual summary of Insights Realm outputs
   - Visual summary of Journey Realm outputs
   - Combined visual summary

2. **Roadmap Generation**
   - Generate roadmap from realm summaries
   - Visual roadmap generation
   - Roadmap stored in GCS

3. **POC Proposal**
   - Generate POC proposal from realm summaries
   - Visual POC proposal generation
   - POC stored in GCS

4. **Solution Creation**
   - Convert roadmap to platform solution
   - Convert POC to platform solution
   - Solution stored in Supabase

---

## Current Implementation Status

### Existing Capabilities

| Capability | Status | Implementation | Notes |
|------------|--------|----------------|-------|
| Synthesize outcome | ⚠️ Partial | `synthesize_outcome` intent | Exists but needs validation |
| Generate roadmap | ⚠️ Partial | `generate_roadmap` intent | Exists but needs validation |
| Create POC | ⚠️ Partial | `create_poc` intent | Exists but needs validation |
| Create solution (from roadmap) | ⚠️ Partial | `create_solution` intent | Needs validation |
| Create solution (from POC) | ⚠️ Partial | `create_solution` intent | Needs validation |

### Missing Capabilities

| Capability | Status | Gap |
|------------|--------|-----|
| Summary visual | ❌ Missing | **GAP** - No visual generation |
| Roadmap visual | ❌ Missing | **GAP** - No visual generation |
| POC visual | ❌ Missing | **GAP** - No visual generation |
| Complete lineage tracking | ❌ Missing | **GAP** - No lineage links to realm outputs |

---

## Detailed Gap Analysis

### Gap 1: Summary Visual Generation

**Requirement:** Create summary visual of outputs from other realms

**Current State:**
- No visual generation service
- No summary aggregation
- No visual storage

**Required Implementation:**

#### 1.1: Summary Aggregation Service

**File:** `symphainy_platform/realms/outcomes/enabling_services/summary_aggregation_service.py`

**Methods:**
```python
async def aggregate_realm_outputs(
    self,
    content_outputs: List[Dict[str, Any]],
    insights_outputs: List[Dict[str, Any]],
    journey_outputs: List[Dict[str, Any]],
    tenant_id: str,
    context: ExecutionContext
) -> Dict[str, Any]:
    """
    Aggregate outputs from all realms into summary.
    
    Returns:
    - Summary structure
    - Key insights
    - Recommendations
    - Next steps
    """
```

#### 1.2: Summary Visual Generation Service

**File:** `symphainy_platform/realms/outcomes/enabling_services/visual_generation_service.py`

**Methods:**
```python
async def generate_summary_visual(
    self,
    summary_data: Dict[str, Any],
    tenant_id: str,
    context: ExecutionContext
) -> Dict[str, Any]:
    """
    Generate visual summary from aggregated realm outputs.
    
    Visual includes:
    - Content Realm summary
    - Insights Realm summary
    - Journey Realm summary
    - Combined insights
    - Recommendations
    
    Returns visual file path in GCS.
    """
```

**Visual Types:**
- **Dashboard-style summary** - Overview of all realms
- **Timeline visualization** - Journey through realms
- **Insight cards** - Key findings from each realm
- **Recommendation matrix** - Prioritized recommendations

**Storage:** GCS bucket `tenant/{tenant_id}/summaries/`

**Lineage:** Track in Supabase `summaries` table (link to realm outputs)

---

### Gap 2: Roadmap Visual Generation

**Requirement:** Generate roadmap with visual representation

**Current State:**
- `generate_roadmap` intent exists but may not generate visuals
- No visual roadmap storage

**Required Implementation:**

#### 2.1: Enhanced Roadmap Generation Service

**File:** `symphainy_platform/realms/outcomes/enabling_services/roadmap_generation_service.py`

**Enhancements:**
1. **Roadmap Structure:**
   - Phases/milestones
   - Dependencies
   - Timeline
   - Resources
   - Success criteria

2. **Visual Generation:**
   - Gantt chart
   - Timeline visualization
   - Dependency graph
   - Roadmap dashboard

**Output:**
```json
{
    "roadmap": {
        "phases": [...],
        "timeline": {...},
        "dependencies": [...],
        "resources": [...],
        "success_criteria": [...]
    },
    "visual_path": "gcs://..."
}
```

**Storage:** GCS bucket `tenant/{tenant_id}/roadmaps/`

**Lineage:** Track in Supabase `roadmaps` table (link to summary)

---

### Gap 3: POC Visual Generation

**Requirement:** Generate POC proposal with visual representation

**Current State:**
- `create_poc` intent exists but may not generate visuals
- No visual POC storage

**Required Implementation:**

#### 3.1: Enhanced POC Generation Service

**File:** `symphainy_platform/realms/outcomes/enabling_services/poc_generation_service.py`

**Enhancements:**
1. **POC Structure:**
   - Objectives
   - Scope
   - Approach
   - Timeline
   - Success criteria
   - Resource requirements

2. **Visual Generation:**
   - POC proposal document
   - Visual timeline
   - Scope diagram
   - Resource allocation chart

**Output:**
```json
{
    "poc": {
        "objectives": [...],
        "scope": {...},
        "approach": {...},
        "timeline": {...},
        "success_criteria": [...],
        "resources": [...]
    },
    "visual_path": "gcs://..."
}
```

**Storage:** GCS bucket `tenant/{tenant_id}/pocs/`

**Lineage:** Track in Supabase `pocs` table (link to summary)

---

### Gap 4: Solution Creation from Roadmap/POC

**Requirement:** Turn roadmap and POC into platform solutions

**Current State:**
- `create_solution` intent exists but needs validation
- May not properly convert roadmap/POC to solutions
- May not maintain proper lineage

**Required Implementation:**

#### 4.1: Solution Creation Service

**File:** `symphainy_platform/realms/outcomes/enabling_services/solution_creation_service.py`

**Methods:**
```python
async def create_solution_from_roadmap(
    self,
    roadmap_id: str,
    roadmap_data: Dict[str, Any],
    tenant_id: str,
    context: ExecutionContext
) -> Dict[str, Any]:
    """
    Convert roadmap to platform solution.
    
    Creates:
    - Solution model (context, bindings, sync strategies)
    - Solution structure
    - Implementation plan
    
    Stores in Supabase (solutions table).
    Maintains lineage (roadmap → solution).
    """

async def create_solution_from_poc(
    self,
    poc_id: str,
    poc_data: Dict[str, Any],
    tenant_id: str,
    context: ExecutionContext
) -> Dict[str, Any]:
    """
    Convert POC to platform solution.
    
    Creates:
    - Solution model (context, bindings, sync strategies)
    - Solution structure
    - Implementation plan
    
    Stores in Supabase (solutions table).
    Maintains lineage (POC → solution).
    """
```

**Solution Structure:**
- Solution model (context, bindings, sync strategies)
- Implementation phases
- Resource requirements
- Success criteria

**Storage:** Supabase `solutions` table

**Lineage:** Link solution to roadmap/POC in Supabase

---

### Gap 5: Complete Lineage Tracking

**Requirement:** Link all Outcomes Realm artifacts to source realm outputs

**Current State:**
- No lineage tracking for summaries
- No lineage tracking for roadmaps
- No lineage tracking for POCs
- No lineage tracking for solutions

**Required Implementation:**

#### 5.1: Supabase Tables

**Tables to create:**
1. `summaries` - Track summaries, link to realm outputs
2. `roadmaps` - Track roadmaps, link to summaries
3. `pocs` - Track POCs, link to summaries
4. `solutions` - Track solutions, link to roadmaps/POCs
5. `outcome_visuals` - Track visuals, link to summaries/roadmaps/POCs

**Schema Examples:**

**`summaries` table:**
```sql
CREATE TABLE summaries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    summary_id TEXT NOT NULL,
    content_output_ids UUID[],  -- Array of content output IDs
    insights_output_ids UUID[],  -- Array of insights output IDs
    journey_output_ids UUID[],  -- Array of journey output IDs
    gcs_path TEXT NOT NULL,
    visual_path TEXT,  -- Link to visual
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(tenant_id, summary_id)
);
```

**`roadmaps` table:**
```sql
CREATE TABLE roadmaps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    roadmap_id TEXT NOT NULL,
    summary_id UUID REFERENCES summaries(id),  -- Source summary
    gcs_path TEXT NOT NULL,
    visual_path TEXT,  -- Link to visual
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(tenant_id, roadmap_id)
);
```

**`pocs` table:**
```sql
CREATE TABLE pocs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    poc_id TEXT NOT NULL,
    summary_id UUID REFERENCES summaries(id),  -- Source summary
    gcs_path TEXT NOT NULL,
    visual_path TEXT,  -- Link to visual
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(tenant_id, poc_id)
);
```

**`solutions` table:**
```sql
CREATE TABLE solutions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    solution_id TEXT NOT NULL,
    roadmap_id UUID REFERENCES roadmaps(id),  -- Source roadmap (if from roadmap)
    poc_id UUID REFERENCES pocs(id),  -- Source POC (if from POC)
    solution_model JSONB NOT NULL,  -- Solution model (context, bindings, sync strategies)
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(tenant_id, solution_id)
);
```

**`outcome_visuals` table:**
```sql
CREATE TABLE outcome_visuals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    visual_id TEXT NOT NULL,
    visual_type TEXT NOT NULL,  -- "summary" | "roadmap" | "poc" | "solution"
    source_id UUID,  -- Link to summary/roadmap/poc/solution
    gcs_path TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(tenant_id, visual_id)
);
```

#### 5.2: Data Brain Integration

**Register references:**
- Summary references
- Roadmap references
- POC references
- Solution references
- Visual references

**Track provenance:**
- Summary → content/insights/journey outputs
- Roadmap → summary
- POC → summary
- Solution → roadmap/POC
- Visual → summary/roadmap/POC/solution

---

## Implementation Plan

### Phase 1: Summary Visual (Week 1-2)
1. Summary aggregation service
2. Summary visual generation service
3. Visual storage in GCS
4. Summary tracking in Supabase
5. E2E tests

### Phase 2: Roadmap Visual (Week 2-3)
6. Enhanced roadmap generation service
7. Roadmap visual generation
8. Roadmap storage in GCS
9. Roadmap tracking in Supabase
10. E2E tests

### Phase 3: POC Visual (Week 3-4)
11. Enhanced POC generation service
12. POC visual generation
13. POC storage in GCS
14. POC tracking in Supabase
15. E2E tests

### Phase 4: Solution Creation (Week 4-5)
16. Solution creation service
17. Roadmap to solution conversion
18. POC to solution conversion
19. Solution storage in Supabase
20. E2E tests

### Phase 5: Complete Lineage Tracking (Week 5-6)
21. Supabase tables (summaries, roadmaps, pocs, solutions, outcome_visuals)
22. Lineage tracking in all orchestrators
23. Data Brain integration
24. E2E test: Complete lineage chain

---

## Success Criteria

✅ **Summary Visual:**
- Summary aggregated from all realms
- Visual summary generated
- Visual stored in GCS
- Summary tracked with lineage

✅ **Roadmap Visual:**
- Roadmap generated from summary
- Visual roadmap generated
- Roadmap stored in GCS
- Roadmap tracked with lineage

✅ **POC Visual:**
- POC generated from summary
- Visual POC generated
- POC stored in GCS
- POC tracked with lineage

✅ **Solution Creation:**
- Roadmap converted to solution
- POC converted to solution
- Solution stored in Supabase
- Lineage maintained (roadmap/POC → solution)

✅ **Complete Lineage:**
- All artifacts link to source realm outputs
- Full provenance chain queryable
- Data Brain integration complete
