# Guided Discovery

**Realm:** Insights  
**Status:** ✅ Complete  
**Last Updated:** January 2026

---

## Overview

The Guided Discovery capability helps users systematically explore their data using guides (use case cards) to match data against known patterns and discover relationships.

---

## Intent: `interpret_data_guided`

Interprets data using a guide to match data against known patterns and discover relationships.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `parsed_file_id` or `parsed_result_id` | string | Yes | Identifier for the parsed file result |
| `guide_id` | string | Yes | Identifier for the guide/use case card |
| `matching_options` | object | No | Options for matching process (strict matching, partial match, etc.) |

### Response

```json
{
  "artifacts": {
    "interpretation": {
      "matched_guide": "insurance_policy_vli",
      "confidence": 0.94,
      "mappings": {
        "policy_number": "field_1",
        "beneficiary": "field_5",
        "coverage_amount": "field_12"
      },
      "unmapped_fields": ["field_8", "field_15"],
      "suggestions": [
        "Field 8 may be a rider",
        "Field 15 appears to be metadata"
      ],
      "relationships": [
        {
          "from": "policy_number",
          "to": "beneficiary",
          "type": "has",
          "confidence": 0.88
        }
      ]
    },
    "parsed_file_id": "parsed_file_123",
    "guide_id": "guide_insurance_vli_001"
  },
  "events": [
    {
      "type": "data_interpreted_with_guide",
      "parsed_file_id": "parsed_file_123",
      "guide_id": "guide_insurance_vli_001"
    }
  ]
}
```

---

## Use Cases

### 1. Insurance Policy Migration
**Scenario:** Processing variable life insurance policies with known structure.

**Use Case:** Use guided discovery with an insurance policy guide to:
- Map fields to known policy structure
- Identify riders and optional fields
- Validate data completeness against guide
- Discover relationships between policy elements

**Business Value:** Ensures accurate field mapping for 350k+ policies.

---

### 2. Permit Data Extraction
**Scenario:** Extracting data from permits using a permit template guide.

**Use Case:** Use guided discovery with a permit guide to:
- Match permit fields to template
- Identify missing required fields
- Validate permit structure
- Extract key information systematically

**Business Value:** Standardizes permit data extraction across diverse formats.

---

### 3. Legacy System Analysis
**Scenario:** Understanding data from legacy systems using known patterns.

**Use Case:** Use guided discovery with system-specific guides to:
- Match data to known system patterns
- Identify deviations from expected structure
- Map legacy fields to modern equivalents
- Document system structure

**Business Value:** Accelerates legacy system understanding and migration.

---

## Technical Details

### Implementation

The `interpret_data_guided` intent uses the `GuidedDiscoveryService` which:
1. Retrieves guide/use case card from Supabase
2. Gets embeddings from ArangoDB for semantic matching
3. Matches data fields against guide patterns
4. Validates field mappings
5. Identifies unmapped fields
6. Discovers relationships based on guide structure
7. Tracks interpretation in Supabase for lineage

### Guide Structure

Guides (use case cards) define:
- Expected fields and types
- Field relationships
- Validation rules
- Business context

---

## Related Capabilities

- [Semantic Interpretation](semantic_interpretation.md) - Self-discovery mode
- [Data Quality Assessment](data_quality.md) - Assess quality before discovery
- [Interactive Analysis](interactive_analysis.md) - Deep dive into discovered data
- [Lineage Tracking](lineage_tracking.md) - Track discovery lineage

---

## API Example

```python
intent = Intent(
    intent_type="interpret_data_guided",
    parameters={
        "parsed_file_id": "parsed_file_123",
        "guide_id": "guide_insurance_vli_001",
        "matching_options": {
            "strict_matching": False,
            "allow_partial_match": True,
            "min_confidence": 0.8
        }
    }
)

result = await runtime.execute(intent, context)
mappings = result.artifacts["interpretation"]["mappings"]
```

---

**See Also:**
- [Insights Realm Overview](../architecture/north_star.md#23-domain-services-formerly-realms)
- [API Contracts](../execution/api_contracts_frontend_integration.md)
