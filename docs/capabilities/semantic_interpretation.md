# Semantic Interpretation

**Realm:** Insights  
**Status:** ✅ Complete  
**Last Updated:** January 2026

---

## Overview

The Semantic Interpretation capability understands data meaning and relationships through two discovery modes: **self-discovery** (automatic semantic discovery) and **guided discovery** (using use case cards/guides).

---

## Intents

### 1. `interpret_data_self_discovery`

Automatically discovers semantics from parsed data using embeddings and semantic analysis.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `parsed_file_id` or `parsed_result_id` | string | Yes | Identifier for the parsed file result |
| `discovery_options` | object | No | Options for discovery process |

#### Response

```json
{
  "artifacts": {
    "discovery": {
      "semantic_map": {
        "entities": [
          {
            "name": "policy_number",
            "type": "identifier",
            "confidence": 0.95,
            "location": "field_1"
          }
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
      "interpretation": {
        "data_type": "insurance_policy",
        "confidence": 0.92,
        "key_fields": ["policy_number", "beneficiary", "coverage_amount"]
      }
    },
    "parsed_file_id": "parsed_file_123"
  },
  "events": [
    {
      "type": "semantics_discovered",
      "parsed_file_id": "parsed_file_123"
    }
  ]
}
```

---

### 2. `interpret_data_guided`

Interprets data using a guide (use case card) to match data against known patterns.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `parsed_file_id` or `parsed_result_id` | string | Yes | Identifier for the parsed file result |
| `guide_id` | string | Yes | Identifier for the guide/use case card |
| `matching_options` | object | No | Options for matching process |

#### Response

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
      "suggestions": ["Field 8 may be a rider", "Field 15 appears to be metadata"]
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

### 1. Insurance Policy Migration (Guided Discovery)
**Scenario:** Processing variable life insurance policies with known structure.

**Use Case:** Use `interpret_data_guided` with an insurance policy guide to:
- Map fields to known policy structure
- Identify riders and optional fields
- Validate data completeness against guide

**Business Value:** Ensures accurate field mapping for 350k+ policies.

---

### 2. Permit Data Extraction (Self-Discovery)
**Scenario:** Extracting data from diverse permit formats.

**Use Case:** Use `interpret_data_self_discovery` to:
- Automatically identify permit type
- Discover key fields (permit number, issue date, expiration)
- Map relationships between fields

**Business Value:** Handles diverse permit formats without manual configuration.

---

### 3. Legacy System Analysis (Self-Discovery)
**Scenario:** Understanding data from unknown legacy systems.

**Use Case:** Use `interpret_data_self_discovery` to:
- Discover data structure automatically
- Identify entities and relationships
- Generate semantic map for documentation

**Business Value:** Accelerates understanding of legacy systems before migration.

---

## Technical Details

### Implementation

**Self-Discovery:**
- Uses `SemanticSelfDiscoveryService`
- Analyzes embeddings from ArangoDB
- Performs semantic clustering and entity extraction
- Generates semantic maps automatically

**Guided Discovery:**
- Uses `GuidedDiscoveryService`
- Matches data against guide patterns
- Validates field mappings
- Identifies unmapped fields

### Lineage Tracking

Both discovery modes track interpretations in Supabase for lineage visualization:
- Links parsed files to interpretations
- Records guide usage (for guided discovery)
- Enables traceability from source to interpretation

---

## Related Capabilities

- [Data Quality Assessment](data_quality.md) - Assess data quality before interpretation
- [Interactive Analysis](interactive_analysis.md) - Deep dive into interpreted data
- [Lineage Tracking](lineage_tracking.md) - Visualize interpretation lineage

---

## API Examples

### Self-Discovery

```python
intent = Intent(
    intent_type="interpret_data_self_discovery",
    parameters={
        "parsed_file_id": "parsed_file_123",
        "discovery_options": {
            "min_confidence": 0.8,
            "include_relationships": True
        }
    }
)

result = await runtime.execute(intent, context)
semantic_map = result.artifacts["discovery"]["semantic_map"]
```

### Guided Discovery

```python
intent = Intent(
    intent_type="interpret_data_guided",
    parameters={
        "parsed_file_id": "parsed_file_123",
        "guide_id": "guide_insurance_vli_001",
        "matching_options": {
            "strict_matching": False,
            "allow_partial_match": True
        }
    }
)

result = await runtime.execute(intent, context)
interpretation = result.artifacts["interpretation"]
```

---

**See Also:**
- [Insights Realm Overview](../architecture/north_star.md#23-domain-services-formerly-realms)
- [API Contracts](../execution/api_contracts_frontend_integration.md)
