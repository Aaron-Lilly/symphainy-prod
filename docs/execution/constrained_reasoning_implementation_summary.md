# Constrained Semantic Reasoning: Implementation Summary

**Status:** Architectural Solution  
**Created:** January 2026  
**Goal:** Summary of how constrained semantic reasoning solves PSO, AAR, and data mapping elegantly

---

## The Problem

**Old Approach:**
- PSO Parser → specialized code for permits
- AAR Parser → specialized code for after action reports
- Data Mapping → specialized code for each mapping scenario
- ❌ Not composable, requires code changes for each use case

**The Insight:**
These aren't really "specialized parsers" - they're **user-provided fact patterns/data models** that constrain how we reason about what data means and format the output structure.

---

## The Solution: Constrained Semantic Reasoning

### Universal Engine + User Constraints

**Universal Components (No Specialization):**
1. **Content Realm:** Universal parsing (structure extraction) - works for all file types
2. **Insights Realm:** Universal semantic interpretation engine - works for all data types
3. **ArangoDB:** Universal embedding storage - works for all embeddings

**User-Provided Constraints (Extensibility):**
1. **Fact Patterns:** User defines entities, relationships, attributes (what to look for)
2. **Output Templates:** User defines output structure (how to format results)
3. **Mapping Schemas:** User defines source→target mappings (how to transform)

---

## How It Works

### PSO (Permits) Use Case

**User Provides:**
- **Fact Pattern:** "Look for permit entities with these attributes: id, type, status, issue_date"
- **Output Template:** "Format results as: {permit_id, permit_type, status, applicant: {...}}"

**System Behavior:**
1. Content Realm parses PSO file (universal parser)
2. Content Realm generates embeddings (universal embedding)
3. Insights Realm interprets with PSO fact pattern constraints
4. Insights Realm formats output using PSO output template
5. ✅ No specialized parser needed!

### AAR (After Action Reports) Use Case

**User Provides:**
- **Fact Pattern:** "Look for event, action, outcome, lesson_learned entities"
- **Output Template:** "Format results as: {event_summary, actions_taken: [...], lessons_learned: [...]}"

**System Behavior:**
1. Content Realm parses AAR file (universal parser)
2. Content Realm generates embeddings (universal embedding)
3. Insights Realm interprets with AAR fact pattern constraints
4. Insights Realm formats output using AAR output template
5. ✅ Same engine, different constraints!

### Data Mapping (Data Mash) Use Case

**User Provides:**
- **Mapping Schema:** "Map policy.policy_number → policy_new.external_id with transformation prefix_with_legacy_"
- **Virtual Pipeline Config:** "No ingestion, relationships only"

**System Behavior:**
1. Content Realm parses source files (universal parser)
2. Content Realm generates embeddings (universal embedding)
3. Insights Realm interprets with mapping schema constraints
4. Virtual Data Mapper creates relationships in ArangoDB graph (no data ingestion)
5. Lineage tracked in Supabase
6. ✅ Virtual pipeline, no ingestion!

---

## Architectural Components

### 1. Fact Pattern Registry
- **Location:** `symphainy_platform/civic_systems/platform_sdk/fact_pattern_registry.py`
- **Storage:** Supabase `fact_patterns` table
- **Purpose:** Store user-provided fact patterns (entities, relationships, attributes)

### 2. Output Template Registry
- **Location:** `symphainy_platform/civic_systems/platform_sdk/output_template_registry.py`
- **Storage:** Supabase `output_templates` table
- **Purpose:** Store user-provided output structure templates

### 3. Mapping Schema Registry
- **Location:** `symphainy_platform/civic_systems/platform_sdk/mapping_schema_registry.py`
- **Storage:** Supabase `mapping_schemas` table
- **Purpose:** Store user-provided mapping schemas (source→target, transformations)

### 4. Constrained Semantic Interpreter
- **Location:** `symphainy_platform/realms/insights/enabling_services/constrained_semantic_interpreter.py`
- **Purpose:** Perform semantic interpretation with user-provided constraints
- **Input:** Embeddings + Fact Pattern + Output Template
- **Output:** Interpreted data structured according to template

### 5. Virtual Data Mapper
- **Location:** `symphainy_platform/realms/insights/enabling_services/virtual_data_mapper.py`
- **Purpose:** Create virtual data mappings without ingestion
- **Input:** Source files + Mapping Schema
- **Output:** Virtual relationships in ArangoDB graph, lineage in Supabase

---

## New Intent Types

### `interpret_data_with_constraints`
```json
{
    "intent_type": "interpret_data_with_constraints",
    "parameters": {
        "parsed_file_id": "...",
        "fact_pattern_id": "...",  // User-provided fact pattern
        "output_template_id": "...",  // User-provided output template
        "reasoning_constraints": {...}  // Optional reasoning rules
    }
}
```

### `create_virtual_mapping`
```json
{
    "intent_type": "create_virtual_mapping",
    "parameters": {
        "source_files": ["file1", "file2", ...],
        "mapping_schema_id": "...",  // User-provided mapping schema
        "virtual": true
    }
}
```

---

## Benefits

✅ **Composability:**
- Same semantic interpretation engine for PSO, AAR, and any future use case
- No code changes needed for new use cases
- Users define their own fact patterns/templates

✅ **Extensibility:**
- Users can create new fact patterns without code changes
- Users can create new output templates without code changes
- Users can create new mapping schemas without code changes

✅ **Architectural Compliance:**
- Follows 5-layer architecture
- Uses Public Works pattern
- Follows Runtime Participation Contract

✅ **Real Functionality:**
- All operations use real infrastructure (GCS, Supabase, ArangoDB)
- All results stored with proper lineage
- Virtual pipeline truly virtual (no ingestion)

---

## Implementation Priority

### Phase 1: Core Infrastructure (Week 1-2)
1. Fact Pattern Registry
2. Output Template Registry
3. Mapping Schema Registry

### Phase 2: Constrained Semantic Interpreter (Week 2-3)
4. Constrained Semantic Interpreter implementation
5. Update Insights Realm with `interpret_data_with_constraints` intent
6. PSO fact pattern + template (user-provided, not hardcoded)
7. AAR fact pattern + template (user-provided, not hardcoded)

### Phase 3: Virtual Data Mapper (Week 3-4)
8. Virtual Data Mapper implementation
9. Update Insights Realm with `create_virtual_mapping` intent
10. Verify virtual pipeline (no ingestion)

### Phase 4: E2E Testing (Week 4-5)
11. E2E tests for PSO use case
12. E2E tests for AAR use case
13. E2E tests for data mapping (virtual pipeline)

---

## Migration from Old Approach

### For PSO Use Case:
1. Extract fact pattern from old PSO parser → register in Fact Pattern Registry
2. Extract output template from old PSO parser → register in Output Template Registry
3. Use `interpret_data_with_constraints` instead of specialized parser
4. ✅ No specialized parser needed!

### For AAR Use Case:
1. Extract fact pattern from old AAR parser → register in Fact Pattern Registry
2. Extract output template from old AAR parser → register in Output Template Registry
3. Use `interpret_data_with_constraints` instead of specialized parser
4. ✅ No specialized parser needed!

### For Data Mapping:
1. Extract mapping schema from old data mash → register in Mapping Schema Registry
2. Use `create_virtual_mapping` instead of specialized data mash
3. ✅ Virtual pipeline, no ingestion!

---

## Success Criteria

✅ **Universal Engine:**
- Same semantic interpretation engine for all use cases
- No specialized parsers needed

✅ **User-Provided Constraints:**
- Users can define fact patterns
- Users can define output templates
- Users can define mapping schemas

✅ **Composability:**
- Same engine works for PSO, AAR, and any future use case
- No code changes needed for new use cases

✅ **Real Functionality:**
- All operations use real infrastructure
- All results stored with proper lineage
- Virtual pipeline truly virtual

---

## References

- [Constrained Semantic Reasoning Architecture](../architecture/constrained_semantic_reasoning.md) - Full architectural details
- [Realm Gap Analysis](./realm_gap_analysis.md) - Updated gap analysis
- [Comprehensive Realm Testing Strategy](./comprehensive_realm_testing_strategy.md) - Testing strategy
