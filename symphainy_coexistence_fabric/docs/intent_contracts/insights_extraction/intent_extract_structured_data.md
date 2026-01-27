# Intent Contract: extract_structured_data

**Intent:** extract_structured_data  
**Intent Type:** `extract_structured_data`  
**Journey:** Extraction (`insights_extraction`)  
**Realm:** Insights Realm  
**Status:** ✅ **COMPREHENSIVE**  
**Priority:** 🟡 **PRIORITY 2** - Structured data extraction

---

## 1. Intent Overview

### Purpose
Extract structured data from parsed content using pre-configured or custom extraction patterns. Supports patterns like Variable Life Policy Rules, After Action Review, and Permit Semantic Object.

### Intent Flow
```
[User requests structured data extraction]
    ↓
[extract_structured_data intent]
    ↓
[StructuredExtractionService.extract_structured_data()]
    ↓
[Load extraction config (pattern or custom)]
[Apply extraction rules]
[Validate extracted data]
    ↓
[Return extraction_result artifact]
```

### Expected Observable Artifacts
- `extraction_result` artifact with:
  - `pattern` - Pattern used
  - `extracted_data` - Extracted structured data
  - `validation_status` - Validation result
  - `field_mappings` - Field mappings applied

---

## 2. Intent Parameters

### Required Parameters

| Parameter | Type | Description | Validation |
|-----------|------|-------------|------------|
| `pattern` | `string` | Extraction pattern name | One of: "variable_life_policy_rules", "aar", "pso", "custom" |
| `data_source` | `object` | Data source configuration | Must include `parsed_file_id` or `session_id` |

### Optional Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `extraction_config_id` | `string` | Custom extraction config ID | `null` |

### Data Source Object

| Field | Type | Description |
|-------|------|-------------|
| `parsed_file_id` | `string` | Parsed file to extract from |
| `session_id` | `string` | Session context |

---

## 3. Intent Returns

### Success Response

```json
{
  "artifacts": [
    {
      "artifact_type": "extraction_result",
      "data": {
        "pattern": "variable_life_policy_rules",
        "extracted_data": {
          "policy_rules": [
            {
              "rule_id": "VL001",
              "rule_name": "Premium Calculation",
              "condition": "coverage_type == 'variable_life'",
              "action": "apply_variable_premium_rate()"
            }
          ],
          "metadata": {
            "total_rules": 15,
            "extraction_confidence": 0.92
          }
        },
        "validation_status": "valid",
        "field_mappings": {
          "RULE_ID": "rule_id",
          "RULE_NAME": "rule_name"
        }
      },
      "metadata": {
        "pattern": "variable_life_policy_rules",
        "extraction_config_id": null,
        "tenant_id": "tenant_001"
      }
    }
  ],
  "events": []
}
```

---

## 4. Supported Patterns

### Pre-configured Patterns

| Pattern | Description | Config File |
|---------|-------------|-------------|
| `variable_life_policy_rules` | Variable Life insurance policy rules | `variable_life_policy_rules_config.json` |
| `aar` | After Action Review extraction | `after_action_review_config.json` |
| `pso` | Permit Semantic Object extraction | `permit_semantic_object_config.json` |

### Custom Pattern
- Set `pattern: "custom"`
- Provide `extraction_config_id` for custom config

---

## 5. Implementation Details

### Handler Location
`symphainy_platform/realms/insights/orchestrators/insights_orchestrator.py::InsightsOrchestrator._handle_extract_structured_data`

### Key Implementation Steps
1. Extract pattern and data_source from parameters
2. If called from intent handler, use intent.parameters
3. If called from MCP tool, use kwargs
4. Call `StructuredExtractionService.extract_structured_data()`
5. Create structured artifact
6. Return artifacts format

### Enabling Services
- **StructuredExtractionService:** `symphainy_platform/realms/insights/enabling_services/structured_extraction_service.py`

### Dual Call Pattern (SOA API)
Handler supports both:
- Intent-based call (from Runtime)
- Direct call (from MCP tool)

---

## 6. MCP Tool Registration

### SOA API Definition
```python
"extract_structured_data": {
    "handler": self._handle_extract_structured_data,
    "input_schema": {
        "type": "object",
        "properties": {
            "pattern": {
                "type": "string",
                "enum": ["variable_life_policy_rules", "aar", "pso", "custom"]
            },
            "data_source": { "type": "object" },
            "extraction_config_id": { "type": ["string", "null"] }
        },
        "required": ["pattern", "data_source"]
    }
}
```

---

## 7. Error Handling

### Validation Errors
- `pattern` missing → `ValueError("pattern parameter required")`
- `data_source` missing → `ValueError`
- Invalid pattern value → `ValueError`

### Runtime Errors
- Config not found → RuntimeError
- Extraction failed → RuntimeError with details

---

## 8. Contract Compliance

### Required Artifacts
- `extraction_result` - Extracted structured data

### MCP Tool Integration
- Registered as MCP tool for agent use
- Available via SOA API pattern

---

**Last Updated:** January 27, 2026  
**Owner:** Insights Realm Solution Team  
**Status:** ✅ **COMPREHENSIVE** (not used by frontend)
