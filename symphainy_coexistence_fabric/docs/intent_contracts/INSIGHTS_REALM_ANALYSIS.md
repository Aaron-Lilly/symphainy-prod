# Insights Realm Intent Analysis

**Last Updated:** January 27, 2026  
**Purpose:** Cross-reference analysis between journey contracts, backend implementations, and frontend expectations.

---

## 1. Key Finding

**The backend is comprehensive, not shells.** The journey contracts are placeholder templates that need to be updated to reflect what's actually implemented.

### Backend Status: ✅ Comprehensive
- 16 intents implemented in orchestrator
- 12 enabling services with real implementations
- 2 agents (BusinessAnalysisAgent, InsightsLiaisonAgent)
- Artifact Plane integration
- Lineage tracking

### Journey Contracts Status: ⚠️ Templates/Placeholders
- All 5 journey contracts are placeholder templates
- Intent names don't match implementation
- Need to be enhanced to reflect reality

---

## 2. Source Documents Analyzed

### Journey Contracts (5 - all placeholders)
1. `journey_insights_data_quality` - Template with placeholder intents
2. `journey_insights_semantic_embedding` - Template with placeholder intents
3. `journey_insights_data_interpretation` - Template with placeholder intents
4. `journey_insights_relationship_mapping` - Template with placeholder intents
5. `journey_insights_business_analysis` - Template with placeholder intents

### Backend Implementation
- `symphainy_platform/realms/insights/orchestrators/insights_orchestrator.py` (1800+ lines)
- `symphainy_platform/realms/insights/enabling_services/` (12 services)
- `symphainy_platform/realms/insights/agents/` (2 agents)

### Frontend
- `symphainy-frontend/shared/managers/InsightsAPIManager.ts` (625 lines)

---

## 3. Backend Implementation Analysis

### Implemented Intents (16 total)

| Intent | Handler | Status | Used By Frontend |
|--------|---------|--------|------------------|
| `analyze_content` | `_handle_analyze_content` | ✅ Implemented | ❌ Not in manager |
| `interpret_data` | `_handle_interpret_data` | ✅ Implemented | ❌ Not in manager |
| `map_relationships` | `_handle_map_relationships` | ✅ Implemented | ✅ `mapRelationships()` |
| `query_data` | `_handle_query_data` | ✅ Implemented | ❌ Not in manager |
| `calculate_metrics` | `_handle_calculate_metrics` | ✅ Implemented | ❌ Not in manager |
| `assess_data_quality` | `_handle_assess_data_quality` | ✅ Implemented | ✅ `assessDataQuality()` |
| `interpret_data_self_discovery` | `_handle_self_discovery` | ✅ Implemented | ✅ `interpretDataSelfDiscovery()` |
| `interpret_data_guided` | `_handle_guided_discovery` | ✅ Implemented | ✅ `interpretDataGuided()` |
| `analyze_structured_data` | `_handle_analyze_structured` | ✅ Implemented | ✅ `analyzeStructuredData()` |
| `analyze_unstructured_data` | `_handle_analyze_unstructured` | ✅ Implemented | ✅ `analyzeUnstructuredData()` |
| `visualize_lineage` | `_handle_visualize_lineage` | ✅ Implemented | ✅ `visualizeLineage()` |
| `extract_structured_data` | `_handle_extract_structured_data` | ✅ Implemented | ❌ Not in manager |
| `discover_extraction_pattern` | `_handle_discover_extraction_pattern` | ✅ Implemented | ❌ Not in manager |
| `create_extraction_config` | `_handle_create_extraction_config` | ✅ Implemented | ❌ Not in manager |
| `match_source_to_target` | `_handle_match_source_to_target` | ✅ Implemented | ❌ Not in manager |

### SOA APIs (MCP Tool handlers)
- `get_parsed_data` - Get parsed file data
- `get_embeddings` - Get semantic embeddings
- `get_quality` - Get data quality metrics
- `interpret_data` - Interpret and generate business analysis

### Enabling Services (12 - all real implementations)

| Service | Purpose |
|---------|---------|
| `DataAnalyzerService` | Content analysis, relationship mapping, query |
| `DataQualityService` | Quality assessment (835 lines!) |
| `MetricsCalculatorService` | Metrics calculation |
| `SemanticSelfDiscoveryService` | Self-discovery interpretation |
| `GuidedDiscoveryService` | Guided interpretation with guides |
| `StructuredAnalysisService` | Structured data analysis |
| `UnstructuredAnalysisService` | Unstructured data analysis |
| `LineageVisualizationService` | Lineage visualization ("Your Data Mash") |
| `StructuredExtractionService` | Structured data extraction |
| `SemanticMatchingService` | Semantic matching |
| `SchemaMatchingService` | Schema matching |
| `PatternValidationService` | Pattern validation |

### Agents

| Agent | Purpose |
|-------|---------|
| `BusinessAnalysisAgent` | Agentic forward pattern for data interpretation |
| `InsightsLiaisonAgent` | Interactive insights guidance |

---

## 4. Frontend Expectations (InsightsAPIManager.ts)

| Method | Intent | Backend Has |
|--------|--------|-------------|
| `assessDataQuality()` | `assess_data_quality` | ✅ |
| `interpretDataSelfDiscovery()` | `interpret_data_self_discovery` | ✅ |
| `interpretDataGuided()` | `interpret_data_guided` | ✅ |
| `analyzeStructuredData()` | `analyze_structured_data` | ✅ |
| `analyzeUnstructuredData()` | `analyze_unstructured_data` | ✅ |
| `visualizeLineage()` | `visualize_lineage` | ✅ |
| `mapRelationships()` | `map_relationships` | ✅ |
| `getDataMashVisualization()` | `visualize_lineage` | ✅ |

**All frontend methods have backend implementation.** Frontend is aligned with backend.

---

## 5. Journey Contract vs Implementation Gaps

### Data Quality Journey
| Contract Says | Implementation Has |
|---------------|-------------------|
| `assess_data_quality` | ✅ `assess_data_quality` |
| `validate_schema` | ⚠️ Part of DataQualityService (not separate intent) |
| `generate_quality_report` | ⚠️ Part of assess_data_quality return |

**Recommendation:** Single intent `assess_data_quality` covers all - update contract.

### Semantic Embedding Journey
| Contract Says | Implementation Has |
|---------------|-------------------|
| `create_semantic_embeddings` | ⚠️ In Content Realm (`create_deterministic_embeddings`) |
| `generate_interpretations` | ✅ `interpret_data_self_discovery`, `interpret_data_guided` |
| `save_interpretations` | ⚠️ Part of interpretation handlers (auto-saves) |

**Recommendation:** Move to Content Realm or rename journey to "Data Interpretation".

### Data Interpretation Journey
| Contract Says | Implementation Has |
|---------------|-------------------|
| `initiate_guided_discovery` | ✅ `interpret_data_guided` (with guide_id) |
| `explore_relationships` | ✅ `map_relationships` |
| `identify_patterns` | ⚠️ Part of analysis services |

**Recommendation:** Rename intents to match implementation.

### Relationship Mapping Journey
| Contract Says | Implementation Has |
|---------------|-------------------|
| `create_relationship_graph` | ✅ `map_relationships` |
| `visualize_relationships` | ✅ `visualize_lineage` |

**Recommendation:** Rename intents to match implementation.

### Business Analysis Journey
| Contract Says | Implementation Has |
|---------------|-------------------|
| `analyze_content` | ✅ `analyze_content` (DataAnalyzerService) |
| `generate_business_insights` | ✅ `interpret_data` (BusinessAnalysisAgent) |
| `create_visualizations` | ✅ Part of analysis handlers |

**Recommendation:** Add `analyze_structured_data`, `analyze_unstructured_data`.

---

## 6. Recommended Journey Restructure

### Data Quality Journey (1 intent)
1. **`assess_data_quality`** - Comprehensive quality assessment

### Data Interpretation Journey (2 intents)
1. **`interpret_data_self_discovery`** - Self-discovery interpretation
2. **`interpret_data_guided`** - Guided interpretation with guide

### Data Analysis Journey (2 intents)
1. **`analyze_structured_data`** - Analyze structured data
2. **`analyze_unstructured_data`** - Analyze unstructured data

### Lineage & Relationships Journey (2 intents)
1. **`visualize_lineage`** - "Your Data Mash" visualization
2. **`map_relationships`** - Entity relationship mapping

### Extraction Journey (3 intents)
1. **`extract_structured_data`** - Extract with pattern
2. **`discover_extraction_pattern`** - Discover pattern from data
3. **`create_extraction_config`** - Create config from target model

### Source-Target Matching Journey (1 intent)
1. **`match_source_to_target`** - Three-phase source-to-target matching

### Additional Intents (available but not in frontend)
- `analyze_content` - Content analysis
- `interpret_data` - Business interpretation (agentic)
- `query_data` - Semantic data query
- `calculate_metrics` - Metrics calculation

---

## 7. Key Decisions

| Decision | Rationale |
|----------|-----------|
| Keep backend as-is | Backend is comprehensive, not shells |
| Update journey contracts | Contracts are templates, need to reflect implementation |
| Create comprehensive intent contracts | Document all 16 implemented intents |
| Note frontend gaps | Some intents not used by frontend yet |

---

## 8. Implementation Architecture

### Agentic Forward Pattern
`interpret_data` uses BusinessAnalysisAgent:
- Orchestrator delegates to agent
- Agent reasons about data
- Agent uses services as MCP tools
- Agent constructs business interpretation

### Quality Assessment
`assess_data_quality` combines:
- Parsing results (from Content Realm)
- Deterministic embeddings (schema validation)
- Semantic embeddings (from ArangoDB)
- Calculates: parsing_confidence, embedding_confidence, overall_confidence

### Lineage Tracking
Interpretations and analyses are tracked in Supabase:
- `_track_interpretation()` - Tracks interpretations
- `_track_analysis()` - Tracks analyses
- `_promote_interpretation_to_record_of_fact()` - Promotes to Record of Fact

### Artifact Plane Integration
Analyses registered as Purpose-Bound Outcomes:
- `artifact_type`: "analysis_report" or "visualization"
- `lifecycle_state`: "draft"
- `purpose`: "decision_support" or "delivery"

---

**Last Updated:** January 27, 2026  
**Owner:** Insights Realm Solution Team
