# Insights Realm Implementation Plan: Three-Phase Flow

**Status:** Implementation Plan  
**Created:** January 2026  
**Goal:** Implement refined Insights Realm with Data Quality, Data Interpretation, and Business Analysis phases

---

## Overview

The Insights Realm operates in three distinct phases:

1. **Data Quality** - Combined parsing + embedding analysis to identify issues
2. **Data Interpretation** - Self-discovery OR guided discovery with use case cards
3. **Business Analysis** - Structured/unstructured analysis with deep dive agent

---

## Phase 1: Data Quality

### Goal

**Identify root causes of issues:**
- Parsing quality (did parsing work correctly?)
- Data quality (is the underlying data good?)
- Source issues (copybook problems, data format issues)

**Key Question:** "Do we have a faded purchase order that's hard to read OR something that doesn't seem to be a purchase order at all?"

### Implementation

#### 1.1: Data Quality Service

**File:** `symphainy_platform/realms/insights/enabling_services/data_quality_service.py`

**Methods:**
```python
async def assess_data_quality(
    self,
    parsed_file_id: str,
    source_file_id: str,
    parser_type: str,
    tenant_id: str,
    context: ExecutionContext
) -> Dict[str, Any]:
    """
    Assess data quality across parsing, data, and source dimensions.
    
    Combines:
    - Parsing results (from Content Realm)
    - Embeddings (from ArangoDB)
    - Source file metadata (from Supabase)
    
    Identifies:
    - Parsing issues (missing fields, format mismatches)
    - Data issues (faded documents, corrupted data)
    - Source issues (copybook mismatches, format problems)
    - Root cause (parsing vs data vs source)
    """
```

**Implementation Steps:**
1. Get parsed file from State Surface
2. Get embeddings from ArangoDB
3. Get source file metadata from Supabase
4. Analyze parsing quality (compare parsed results vs parser expectations)
5. Analyze data quality (check for anomalies, completeness, validity)
6. Analyze source quality (check copybook, format, structure)
7. Cross-reference parsing + embeddings to identify root cause
8. Generate suggestions for each issue type

**Output Structure:**
```json
{
    "quality_assessment": {
        "overall_quality": "good|fair|poor",
        "parsing_quality": {
            "status": "good|issues|failed",
            "issues": [...],
            "suggestions": [...]
        },
        "data_quality": {
            "status": "good|issues|poor",
            "issues": [...],
            "suggestions": [...]
        },
        "source_quality": {
            "status": "good|issues|poor",
            "issues": [...],
            "suggestions": [...]
        },
        "root_cause_analysis": {
            "primary_issue": "parsing|data|source",
            "confidence": 0.85,
            "recommendations": [...]
        }
    }
}
```

#### 1.2: Update Insights Orchestrator

**File:** `symphainy_platform/realms/insights/orchestrators/insights_orchestrator.py`

**Add:**
```python
async def _handle_assess_data_quality(
    self,
    intent: Intent,
    context: ExecutionContext
) -> Dict[str, Any]:
    """Handle assess_data_quality intent."""
    parsed_file_id = intent.parameters.get("parsed_file_id")
    source_file_id = intent.parameters.get("source_file_id")
    parser_type = intent.parameters.get("parser_type")
    
    # Assess quality via DataQualityService
    quality_result = await self.data_quality_service.assess_data_quality(
        parsed_file_id=parsed_file_id,
        source_file_id=source_file_id,
        parser_type=parser_type,
        tenant_id=context.tenant_id,
        context=context
    )
    
    return {
        "artifacts": {
            "quality_assessment": quality_result,
            "parsed_file_id": parsed_file_id
        },
        "events": [
            {
                "type": "data_quality_assessed",
                "parsed_file_id": parsed_file_id
            }
        ]
    }
```

#### 1.3: Update Insights Realm

**File:** `symphainy_platform/realms/insights/insights_realm.py`

**Add to `declare_intents()`:**
```python
return [
    # Phase 1: Data Quality
    "assess_data_quality",
    
    # ... existing intents
]
```

---

## Phase 2: Data Interpretation

### Goal

**Interpret what data means** using two modes:

1. **Semantic Self Discovery** - AI determines meaning (unconstrained)
2. **Guided Discovery** - User-provided guides constrain interpretation

### Implementation

#### 2.1: Guide Registry

**File:** `symphainy_platform/civic_systems/platform_sdk/guide_registry.py`

**Purpose:** Store and manage guides (fact patterns + output templates)

**Storage:** Supabase `guides` table

**Schema:**
```json
{
    "guide_id": "uuid",
    "tenant_id": "uuid",
    "name": "PSO Permit Guide",
    "type": "default|user_uploaded|user_created",
    "description": "...",
    "fact_pattern": {
        "entities": [...],
        "relationships": [...],
        "attributes": {...}
    },
    "output_template": {...},
    "created_at": "timestamp",
    "updated_at": "timestamp"
}
```

**Methods:**
```python
async def register_guide(
    self,
    guide_id: str,
    guide: Dict[str, Any],
    tenant_id: str
) -> bool

async def get_guide(
    self,
    guide_id: str,
    tenant_id: str
) -> Optional[Dict[str, Any]]

async def list_guides(
    self,
    tenant_id: str,
    guide_type: Optional[str] = None
) -> List[Dict[str, Any]]
```

#### 2.2: Semantic Self Discovery Service

**File:** `symphainy_platform/realms/insights/enabling_services/semantic_self_discovery_service.py`

**Methods:**
```python
async def discover_semantics(
    self,
    parsed_file_id: str,
    embeddings: List[Dict[str, Any]],
    discovery_options: Dict[str, Any],
    tenant_id: str,
    context: ExecutionContext
) -> Dict[str, Any]:
    """
    Discover semantic meaning without constraints.
    
    Uses embeddings to reason about:
    - Entities (what things are)
    - Relationships (how things connect)
    - Attributes (properties of things)
    - Semantic summary (what it all means)
    """
```

**Implementation:**
1. Get embeddings from ArangoDB
2. Use semantic reasoning to discover entities
3. Use semantic reasoning to discover relationships
4. Generate semantic summary
5. Store results in GCS with lineage in Supabase

#### 2.3: Guided Discovery Service

**File:** `symphainy_platform/realms/insights/enabling_services/guided_discovery_service.py`

**Methods:**
```python
async def interpret_with_guide(
    self,
    parsed_file_id: str,
    guide_id: str,
    embeddings: List[Dict[str, Any]],
    matching_options: Dict[str, Any],
    tenant_id: str,
    context: ExecutionContext
) -> Dict[str, Any]:
    """
    Interpret data using user-provided guide.
    
    Returns:
    - Matched entities (found in data, match guide)
    - Unmatched data (found in data, no guide match)
    - Missing expected (expected in guide, not found in data)
    - Suggestions for unmatched/missing
    """
```

**Implementation:**
1. Get guide from Guide Registry
2. Get embeddings from ArangoDB
3. Use guide fact pattern to constrain reasoning
4. Match data against guide entities/relationships
5. Identify unmatched data
6. Identify missing expected entities
7. Generate suggestions
8. Format output using guide template
9. Store results in GCS with lineage

#### 2.4: Default Guides

**Pre-configured guides "baked into" system:**

**PSO Guide:**
- Entities: permit, applicant, property, regulation
- Relationships: permit → applicant, permit → property, permit → regulation
- Output template: PSO-specific format

**AAR Guide:**
- Entities: event, action, outcome, lesson_learned
- Relationships: event → action, action → outcome, outcome → lesson_learned
- Output template: AAR-specific format

**Purchase Order Guide:**
- Entities: purchase_order, vendor, line_item, approval
- Relationships: purchase_order → vendor, purchase_order → line_item, purchase_order → approval
- Output template: PO-specific format

**Storage:** Supabase `guides` table with `type: "default"`

#### 2.5: Update Insights Orchestrator

**Add:**
```python
async def _handle_self_discovery(
    self,
    intent: Intent,
    context: ExecutionContext
) -> Dict[str, Any]:
    """Handle interpret_data_self_discovery intent."""
    # ... implementation

async def _handle_guided_discovery(
    self,
    intent: Intent,
    context: ExecutionContext
) -> Dict[str, Any]:
    """Handle interpret_data_guided intent."""
    # ... implementation
```

#### 2.6: Update Insights Realm

**Add to `declare_intents()`:**
```python
return [
    # Phase 2: Data Interpretation
    "interpret_data_self_discovery",
    "interpret_data_guided",
    
    # ... existing intents
]
```

---

## Phase 3: Business Analysis

### Goal

**Deep analysis** with structured/unstructured data flows, plus deep dive via Insights Liaison Agent.

### Implementation

#### 3.1: Enhanced Structured Analysis

**File:** `symphainy_platform/realms/insights/enabling_services/structured_analysis_service.py`

**Methods:**
```python
async def analyze_structured_data(
    self,
    parsed_file_id: str,
    analysis_type: str,
    dimensions: List[str],
    tenant_id: str,
    context: ExecutionContext
) -> Dict[str, Any]:
    """
    Analyze structured data.
    
    Analysis types:
    - statistical: Statistical analysis
    - pattern: Pattern detection
    - anomaly: Anomaly detection
    - trend: Trend analysis
    """
```

#### 3.2: Enhanced Unstructured Analysis

**File:** `symphainy_platform/realms/insights/enabling_services/unstructured_analysis_service.py`

**Methods:**
```python
async def analyze_unstructured_data(
    self,
    parsed_file_id: str,
    analysis_type: str,
    deep_dive: bool,
    tenant_id: str,
    context: ExecutionContext
) -> Dict[str, Any]:
    """
    Analyze unstructured data.
    
    Analysis types:
    - semantic: Semantic analysis
    - sentiment: Sentiment analysis
    - topic: Topic modeling
    - extraction: Entity extraction
    
    If deep_dive=true, engage Insights Liaison Agent.
    """
```

#### 3.3: Insights Liaison Agent Integration

**File:** `symphainy_platform/realms/insights/agents/insights_liaison_agent.py`

**Purpose:** Interactive analysis agent for deep dive

**Capabilities:**
- Answer questions about data
- Explore relationships
- Identify patterns
- Provide recommendations
- Interactive chat interface

**Integration:**
- Called when `deep_dive: true` in unstructured analysis
- Uses embeddings and analysis results
- Provides interactive analysis session

#### 3.4: Update Insights Orchestrator

**Add:**
```python
async def _handle_analyze_structured(
    self,
    intent: Intent,
    context: ExecutionContext
) -> Dict[str, Any]:
    """Handle analyze_structured_data intent."""
    # ... implementation

async def _handle_analyze_unstructured(
    self,
    intent: Intent,
    context: ExecutionContext
) -> Dict[str, Any]:
    """Handle analyze_unstructured_data intent."""
    # ... implementation
    # If deep_dive=true, engage Insights Liaison Agent
```

#### 3.5: Update Insights Realm

**Add to `declare_intents()`:**
```python
return [
    # Phase 3: Business Analysis
    "analyze_structured_data",
    "analyze_unstructured_data",
    
    # ... existing intents
]
```

---

## Implementation Timeline

### Week 1-2: Data Quality Phase
- ✅ Data Quality Service
- ✅ `assess_data_quality` intent
- ✅ E2E tests

### Week 3-4: Data Interpretation Phase (Part 1)
- ✅ Guide Registry
- ✅ Semantic Self Discovery Service
- ✅ `interpret_data_self_discovery` intent
- ✅ E2E tests

### Week 4-5: Data Interpretation Phase (Part 2)
- ✅ Guided Discovery Service
- ✅ Default guides (PSO, AAR, PO)
- ✅ `interpret_data_guided` intent
- ✅ Matching results with suggestions
- ✅ E2E tests

### Week 5-6: Business Analysis Phase
- ✅ Enhanced structured analysis
- ✅ Enhanced unstructured analysis
- ✅ Insights Liaison Agent integration
- ✅ E2E tests

### Week 6-7: Complete Lineage Tracking
- ✅ Supabase tables for lineage (parsed_results, embeddings, interpretations, analyses, guides)
- ✅ Content Realm: Track parsed results + embeddings in Supabase
- ✅ Insights Realm: Track interpretations + analyses in Supabase
- ✅ Link embeddings to files
- ✅ Link interpretations to guides
- ✅ Link analyses to guides
- ✅ Data Brain integration (register references, track provenance)
- ✅ E2E test: Complete lineage chain verification

---

## Success Criteria

✅ **Data Quality:**
- Identifies parsing vs data vs source issues
- Provides actionable suggestions
- Uses combined parsing + embedding analysis

✅ **Data Interpretation:**
- Self-discovery works without constraints
- Guided discovery works with user-provided guides
- Default guides "baked in" for common use cases
- Shows matched/unmatched/missing with suggestions

✅ **Business Analysis:**
- Structured analysis works
- Unstructured analysis works
- Deep dive with agent works
- All results stored with proper lineage

✅ **Complete Lineage Tracking:**
- Every embedding traceable to original file
- Every interpretation traceable to guide used
- Every analysis traceable to guide used
- Full provenance chain queryable
- Data Brain integration complete
