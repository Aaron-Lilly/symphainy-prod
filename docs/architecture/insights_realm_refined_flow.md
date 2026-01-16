# Insights Realm: Refined Three-Phase Flow

**Status:** Architectural Design  
**Created:** January 2026  
**Goal:** Define the refined Insights Realm flow with Data Quality, Data Interpretation, and Business Analysis phases

---

## Executive Summary

The Insights Realm operates in three distinct phases:

1. **Data Quality** - Combined analysis from parsing and deterministic embedding to identify issues
2. **Data Interpretation** - Semantic self-discovery OR guided discovery with user-provided fact patterns
3. **Business Analysis** - Structured/unstructured analysis with deep dive via Insights Liaison Agent

---

## Phase 1: Data Quality

### Purpose

**Identify issues in:**
- Parsing quality (did parsing work correctly?)
- Data quality (is the underlying data good?)
- Source issues (copybook problems, data format issues, etc.)

### Key Insight

**"Do we have a faded purchase order that's hard to read OR something that doesn't seem to be a purchase order at all?"**

**"Do we have issues with the copybook, the source data, or something else?"**

### Implementation

#### Intent: `assess_data_quality`

**Parameters:**
```json
{
    "intent_type": "assess_data_quality",
    "parameters": {
        "parsed_file_id": "...",
        "source_file_id": "...",  // Original file reference
        "parser_type": "mainframe|csv|json|pdf|...",
        "quality_dimensions": ["parsing", "data", "source"]
    }
}
```

#### Data Quality Service

**Location:** `symphainy_platform/realms/insights/enabling_services/data_quality_service.py`

**What it does:**
1. **Parsing Quality Assessment:**
   - Compare parsed results against parser expectations
   - Check for parsing errors, missing fields, unexpected formats
   - Identify parser configuration issues

2. **Data Quality Assessment:**
   - Analyze parsed data for completeness, consistency, validity
   - Check for data anomalies, outliers, missing values
   - Identify data format issues (faded documents, corrupted data)

3. **Source Quality Assessment:**
   - Analyze source file characteristics
   - Check for copybook mismatches, format issues
   - Identify source data problems

4. **Combined Analysis:**
   - Cross-reference parsing results with embeddings
   - Use embeddings to detect semantic anomalies
   - Identify root cause (parsing vs data vs source)

**Output:**
```json
{
    "quality_assessment": {
        "overall_quality": "good|fair|poor",
        "parsing_quality": {
            "status": "good|issues|failed",
            "issues": [
                {
                    "type": "missing_field",
                    "field": "policy_number",
                    "severity": "high|medium|low",
                    "suggestion": "Check copybook definition"
                }
            ]
        },
        "data_quality": {
            "status": "good|issues|poor",
            "issues": [
                {
                    "type": "data_anomaly",
                    "description": "Faded document - low OCR confidence",
                    "severity": "high",
                    "suggestion": "Rescan document or use higher quality source"
                }
            ]
        },
        "source_quality": {
            "status": "good|issues|poor",
            "issues": [
                {
                    "type": "copybook_mismatch",
                    "description": "Copybook definition doesn't match data structure",
                    "severity": "high",
                    "suggestion": "Review copybook or source data format"
                }
            ]
        },
        "root_cause_analysis": {
            "primary_issue": "parsing|data|source",
            "confidence": 0.85,
            "recommendations": [...]
        }
    }
}
```

---

## Phase 2: Data Interpretation

### Purpose

**Interpret what the data means** using two modes:

1. **Semantic Self Discovery** - AI determines what it means (unconstrained)
2. **Guided Discovery** - User-provided fact patterns/guides constrain interpretation

### Mode 1: Semantic Self Discovery

#### Intent: `interpret_data_self_discovery`

**Parameters:**
```json
{
    "intent_type": "interpret_data_self_discovery",
    "parameters": {
        "parsed_file_id": "...",
        "discovery_options": {
            "depth": "shallow|medium|deep",
            "include_relationships": true,
            "include_entities": true
        }
    }
}
```

**What it does:**
- Uses embeddings to reason about data meaning
- No constraints - AI discovers entities, relationships, meaning
- Returns discovered structure

**Output:**
```json
{
    "discovered_entities": [
        {
            "entity_type": "policy",
            "confidence": 0.92,
            "attributes": {
                "policy_number": "POL-12345",
                "status": "active"
            }
        }
    ],
    "discovered_relationships": [
        {
            "from": "policy",
            "to": "customer",
            "type": "owned_by",
            "confidence": 0.88
        }
    ],
    "semantic_summary": "This appears to be an insurance policy document..."
}
```

### Mode 2: Guided Discovery (Use Cases)

#### Intent: `interpret_data_guided`

**Parameters:**
```json
{
    "intent_type": "interpret_data_guided",
    "parameters": {
        "parsed_file_id": "...",
        "guide_id": "...",  // User-provided guide (fact pattern + output template)
        "matching_options": {
            "show_unmatched": true,
            "show_suggestions": true
        }
    }
}
```

#### Use Case Cards

**Each use case has:**
1. **Default Fact Pattern** - "Baked into" our system (pre-configured)
2. **User Guide Upload** - Users can upload their own guide
3. **Guide Creation** - Users can create guides via UI
4. **Matching Results** - Shows what matched and what didn't

**Use Case Examples:**
- **PSO (Permits)** - Default fact pattern for permits
- **AAR (After Action Reports)** - Default fact pattern for AARs
- **Purchase Orders** - Default fact pattern for POs
- **Custom Use Case** - User-created guide

#### Guide Structure

**Location:** `symphainy_platform/civic_systems/platform_sdk/guide_registry.py`

**Guide Schema:**
```json
{
    "guide_id": "uuid",
    "tenant_id": "uuid",
    "name": "PSO Permit Guide",
    "type": "default|user_uploaded|user_created",
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

#### Matching Results

**Output:**
```json
{
    "interpretation": {
        "matched_entities": [
            {
                "entity": "permit",
                "confidence": 0.95,
                "attributes": {
                    "permit_id": "PERM-123",
                    "status": "active"
                }
            }
        ],
        "unmatched_data": [
            {
                "data_snippet": "...",
                "reason": "No matching entity in guide",
                "suggestions": [
                    "Could be 'application' entity",
                    "Could be 'review' entity"
                ]
            }
        ],
        "missing_expected": [
            {
                "expected_entity": "applicant",
                "reason": "Not found in data",
                "suggestions": [
                    "Check if applicant info is in different section",
                    "May need to parse additional fields"
                ]
            }
        ],
        "confidence_score": 0.82,
        "coverage_score": 0.75  // How much of guide was matched
    }
}
```

---

## Phase 3: Business Analysis

### Purpose

**Deep analysis** with structured and unstructured data flows, plus deep dive via Insights Liaison Agent.

### Structured Analysis

#### Intent: `analyze_structured_data`

**Parameters:**
```json
{
    "intent_type": "analyze_structured_data",
    "parameters": {
        "parsed_file_id": "...",
        "analysis_type": "statistical|pattern|anomaly|trend",
        "dimensions": ["time", "category", "value"]
    }
}
```

**What it does:**
- Statistical analysis of structured data
- Pattern detection
- Anomaly detection
- Trend analysis

### Unstructured Analysis

#### Intent: `analyze_unstructured_data`

**Parameters:**
```json
{
    "intent_type": "analyze_unstructured_data",
    "parameters": {
        "parsed_file_id": "...",
        "analysis_type": "semantic|sentiment|topic|extraction",
        "deep_dive": true  // Engage Insights Liaison Agent
    }
}
```

**What it does:**
- Semantic analysis of unstructured data
- Sentiment analysis
- Topic modeling
- Entity extraction

### Deep Dive via Insights Liaison Agent

**When `deep_dive: true`:**
- Insights Liaison Agent engages
- Interactive analysis session
- User can ask questions, explore data
- Agent provides detailed insights

**Agent Capabilities:**
- Answer questions about data
- Explore relationships
- Identify patterns
- Provide recommendations

---

## Updated Insights Realm Intent Declarations

```python
def declare_intents(self) -> List[str]:
    """
    Declare which intents this realm supports.
    
    Returns:
        List of supported intent types
    """
    return [
        # Phase 1: Data Quality
        "assess_data_quality",
        
        # Phase 2: Data Interpretation
        "interpret_data_self_discovery",  # AI determines meaning
        "interpret_data_guided",  # User-provided guide
        
        # Phase 3: Business Analysis
        "analyze_structured_data",
        "analyze_unstructured_data",
        
        # Legacy (for backward compatibility)
        "analyze_content",
        "interpret_data",  # Maps to self-discovery or guided based on parameters
        "map_relationships",
        "query_data",
        "calculate_metrics"
    ]
```

---

## Implementation Architecture

### New Services

#### 1. Data Quality Service

**Location:** `symphainy_platform/realms/insights/enabling_services/data_quality_service.py`

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
    
    Combines parsing results with embeddings to identify root causes.
    """
```

#### 2. Semantic Self Discovery Service

**Location:** `symphainy_platform/realms/insights/enabling_services/semantic_self_discovery_service.py`

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
    
    AI determines entities, relationships, meaning from embeddings.
    """
```

#### 3. Guided Discovery Service

**Location:** `symphainy_platform/realms/insights/enabling_services/guided_discovery_service.py`

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
    Interpret data using user-provided guide (fact pattern + output template).
    
    Returns matched entities, unmatched data, missing expected, suggestions.
    """
```

#### 4. Guide Registry

**Location:** `symphainy_platform/civic_systems/platform_sdk/guide_registry.py`

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
    guide_type: Optional[str] = None  # "default" | "user_uploaded" | "user_created"
) -> List[Dict[str, Any]]
```

**Storage:** Supabase `guides` table

---

## Updated Insights Orchestrator

### Intent Routing

```python
async def handle_intent(
    self,
    intent: Intent,
    context: ExecutionContext
) -> Dict[str, Any]:
    intent_type = intent.intent_type
    
    # Phase 1: Data Quality
    if intent_type == "assess_data_quality":
        return await self._handle_assess_data_quality(intent, context)
    
    # Phase 2: Data Interpretation
    elif intent_type == "interpret_data_self_discovery":
        return await self._handle_self_discovery(intent, context)
    elif intent_type == "interpret_data_guided":
        return await self._handle_guided_discovery(intent, context)
    
    # Phase 3: Business Analysis
    elif intent_type == "analyze_structured_data":
        return await self._handle_analyze_structured(intent, context)
    elif intent_type == "analyze_unstructured_data":
        return await self._handle_analyze_unstructured(intent, context)
    
    # Legacy support
    elif intent_type == "interpret_data":
        # Route to self-discovery or guided based on parameters
        if intent.parameters.get("guide_id"):
            return await self._handle_guided_discovery(intent, context)
        else:
            return await self._handle_self_discovery(intent, context)
    
    # ... other intents
```

---

## Use Case Cards UI Flow

### Default Guides

**Pre-configured guides "baked into" system:**
- PSO (Permits)
- AAR (After Action Reports)
- Purchase Orders
- Insurance Policies
- etc.

**Each card shows:**
- Guide name and description
- Default fact pattern (entities, relationships)
- Default output template
- "Use this guide" button
- "Customize" button (create copy for editing)

### User Guides

**Users can:**
1. **Upload Guide** - Upload JSON/YAML guide file
2. **Create Guide** - Use UI to create guide (easier, lower risk)
3. **Edit Guide** - Modify existing guide
4. **View Matching Results** - See what matched, what didn't, suggestions

### Guide Creation UI

**Simplified guide creation:**
1. **Define Entities** - Add entity types (permit, applicant, etc.)
2. **Define Attributes** - Add attributes for each entity
3. **Define Relationships** - Add relationships between entities
4. **Define Output Template** - Define how results should be formatted
5. **Test Guide** - Test guide against sample data
6. **Save Guide** - Save to registry

---

## E2E Test Coverage

### Phase 1: Data Quality Tests

**Test:** `test_assess_data_quality_parsing_issues`
- Upload file with parsing issues
- Verify parsing quality assessment identifies issues
- Verify suggestions provided

**Test:** `test_assess_data_quality_data_issues`
- Upload faded/corrupted document
- Verify data quality assessment identifies issues
- Verify root cause analysis (data vs parsing)

**Test:** `test_assess_data_quality_source_issues`
- Upload file with copybook mismatch
- Verify source quality assessment identifies issues
- Verify suggestions for copybook review

### Phase 2: Data Interpretation Tests

**Test:** `test_self_discovery`
- Upload file
- Call self-discovery intent
- Verify entities and relationships discovered
- Verify semantic summary generated

**Test:** `test_guided_discovery_default_guide`
- Upload PSO document
- Use default PSO guide
- Verify matched entities
- Verify unmatched data identified
- Verify suggestions provided

**Test:** `test_guided_discovery_user_guide`
- Upload custom document
- Use user-created guide
- Verify interpretation uses guide constraints
- Verify output matches template

**Test:** `test_guide_creation`
- Create guide via UI/API
- Test guide against sample data
- Verify guide works correctly

### Phase 3: Business Analysis Tests

**Test:** `test_structured_analysis`
- Upload structured data (CSV, JSON)
- Call structured analysis intent
- Verify statistical analysis performed
- Verify patterns detected

**Test:** `test_unstructured_analysis`
- Upload unstructured data (PDF, text)
- Call unstructured analysis intent
- Verify semantic analysis performed
- Verify topics extracted

**Test:** `test_deep_dive_with_agent`
- Upload data
- Call unstructured analysis with deep_dive=true
- Verify Insights Liaison Agent engages
- Verify interactive analysis works

---

## Implementation Priority

### Phase 1: Data Quality (Week 1-2)
1. Data Quality Service
2. `assess_data_quality` intent
3. E2E tests for data quality assessment

### Phase 2: Data Interpretation (Week 2-4)
4. Guide Registry
5. Semantic Self Discovery Service
6. Guided Discovery Service
7. Default guides (PSO, AAR, etc.)
8. `interpret_data_self_discovery` intent
9. `interpret_data_guided` intent
10. E2E tests for both modes

### Phase 3: Business Analysis (Week 4-5)
11. Enhanced structured analysis
12. Enhanced unstructured analysis
13. Insights Liaison Agent integration
14. E2E tests for business analysis

---

## Success Criteria

✅ **Data Quality:**
- Identifies parsing issues vs data issues vs source issues
- Provides actionable suggestions
- Uses combined parsing + embedding analysis

✅ **Data Interpretation:**
- Self-discovery works without constraints
- Guided discovery works with user-provided guides
- Shows matched/unmatched/missing with suggestions
- Default guides "baked in" for common use cases

✅ **Business Analysis:**
- Structured analysis works
- Unstructured analysis works
- Deep dive with agent works
- All results stored with proper lineage
