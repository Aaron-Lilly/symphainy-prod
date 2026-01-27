# Journey Contract: Structured Extraction & Matching

**Journey:** Structured Extraction & Matching  
**Journey ID:** `journey_insights_semantic_embedding`  
**Solution:** Insights Realm Solution  
**Status:** ✅ **IMPLEMENTED**  
**Priority:** 🟡 **PRIORITY 2** - Advanced journey

---

## 1. Journey Overview

> **Note:** This journey was originally named "Semantic Embedding Creation" but the actual implementation covers structured extraction and source-to-target matching. Semantic embeddings are created in the Content Realm via `create_deterministic_embeddings`.

### Intents in Journey
1. **`extract_structured_data`** - Extract with pre-configured pattern
   - Supports: Variable Life Policy Rules, AAR, PSO, Custom
   - Available as MCP tool for agent use

2. **`discover_extraction_pattern`** - Discover pattern from data
   - Freeform analysis to discover extraction structure

3. **`create_extraction_config`** - Create config from target model
   - Generate extraction configuration from target data model

4. **`match_source_to_target`** - Three-phase source-to-target matching
   - Schema matching, semantic matching, pattern validation
   - For data migration and transformation scenarios

### Journey Flow
```
[User requests extraction/matching]
    ↓
[Choose operation]
    ├── Extract with pattern
    │   ↓
    │   [extract_structured_data intent]
    │   ↓
    │   [StructuredExtractionService.extract_structured_data()]
    │
    ├── Discover pattern
    │   ↓
    │   [discover_extraction_pattern intent]
    │   ↓
    │   [StructuredExtractionService.discover_extraction_pattern()]
    │
    ├── Create extraction config
    │   ↓
    │   [create_extraction_config intent]
    │   ↓
    │   [StructuredExtractionService.create_extraction_config_from_target_model()]
    │
    └── Match source to target
        ↓
        [match_source_to_target intent]
        ↓
        [GuidedDiscoveryService.match_source_to_target()]
        ↓
        [Phase 1: Schema matching]
        [Phase 2: Semantic matching]
        [Phase 3: Pattern validation]
    ↓
[Return result artifact]
    ↓
[Journey Complete]
```

### Expected Observable Artifacts

#### Extraction Result

| Artifact | Type | Description |
|----------|------|-------------|
| `extraction_result` | object | Extraction result |
| `extraction_result.pattern` | string | Pattern used |
| `extraction_result.extracted_data` | object | Extracted data |
| `extraction_result.validation_status` | string | Validation result |

#### Matching Result

| Artifact | Type | Description |
|----------|------|-------------|
| `matching_result` | object | Source-to-target matching result |
| `matching_result.overall_confidence` | float | Overall match confidence |
| `matching_result.mapping_table` | array | Field-level mappings |
| `matching_result.phase_results` | object | Results from each phase |
| `matching_result.unmapped_fields` | object | Fields that couldn't be mapped |
| `matching_result.transformation_suggestions` | array | Suggested transformations |

### Supported Extraction Patterns

| Pattern | Description | Config File |
|---------|-------------|-------------|
| `variable_life_policy_rules` | Variable Life insurance policy rules | `variable_life_policy_rules_config.json` |
| `aar` | After Action Review extraction | `after_action_review_config.json` |
| `pso` | Permit Semantic Object extraction | `permit_semantic_object_config.json` |
| `custom` | Custom extraction (requires config_id) | User-defined |

### Three-Phase Matching Process

| Phase | Description |
|-------|-------------|
| Schema Matching | Compare field names and data types |
| Semantic Matching | Use embeddings for meaning-based matching |
| Pattern Validation | Validate against data patterns |

---

## 2. Scenario 1: Extraction with Pattern

### Test Description
Structured extraction with pre-configured pattern succeeds.

### Steps
1. [x] User has a parsed file
2. [x] User triggers `extract_structured_data` with pattern
3. [x] StructuredExtractionService loads pattern config
4. [x] Extraction rules applied
5. [x] Extraction result returned

### Verification
- [x] `extraction_result` artifact returned
- [x] `extraction_result.pattern` matches input
- [x] `extraction_result.extracted_data` non-empty

---

## 3. Scenario 2: Source-to-Target Matching

### Test Description
Three-phase matching produces accurate mappings.

### Steps
1. [x] User has source and target deterministic embeddings
2. [x] User triggers `match_source_to_target`
3. [x] GuidedDiscoveryService performs three-phase matching
4. [x] Matching tracked in Supabase
5. [x] Matching result returned

### Verification
- [x] `matching_result` artifact returned
- [x] `overall_confidence` > 0
- [x] `mapping_table` contains field mappings
- [x] `phase_results` show all three phases

---

## 4. MCP Tool Registration

These intents are registered as MCP tools for agent use:

```python
"extract_structured_data": {
    "handler": self._handle_extract_structured_data,
    "description": "Extract structured data using pre-configured or custom pattern"
}
"discover_extraction_pattern": {
    "handler": self._handle_discover_extraction_pattern,
    "description": "Discover extraction pattern from data"
}
"create_extraction_config": {
    "handler": self._handle_create_extraction_config,
    "description": "Create extraction configuration from target data model"
}
```

---

## 5. Integration Points

### Platform Services
- **Insights Realm:** StructuredExtractionService, GuidedDiscoveryService
- **Configs:** Pre-configured extraction patterns in `configs/` directory

### Backend Handler
`symphainy_platform/realms/insights/orchestrators/insights_orchestrator.py::_handle_extract_structured_data`
`symphainy_platform/realms/insights/orchestrators/insights_orchestrator.py::_handle_discover_extraction_pattern`
`symphainy_platform/realms/insights/orchestrators/insights_orchestrator.py::_handle_create_extraction_config`
`symphainy_platform/realms/insights/orchestrators/insights_orchestrator.py::_handle_match_source_to_target`

### Frontend API
- Not currently used by frontend (available for agent/MCP use)

---

## 6. Gate Status

**Journey is "done" only when:**
- [x] ✅ Extraction with pattern works
- [x] ✅ Pattern discovery works
- [x] ✅ Config creation works
- [x] ✅ Source-to-target matching works
- [x] ✅ MCP tool registration works

**Current Status:** ✅ **IMPLEMENTED**

---

## 7. Related Documents

- **Intent Contract (Extraction):** `docs/intent_contracts/insights_extraction/intent_extract_structured_data.md`
- **Intent Contract (Matching):** `docs/intent_contracts/insights_extraction/intent_match_source_to_target.md`
- **Analysis:** `docs/intent_contracts/INSIGHTS_REALM_ANALYSIS.md`

---

**Last Updated:** January 27, 2026  
**Owner:** Insights Realm Solution Team
