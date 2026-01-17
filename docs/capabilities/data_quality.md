# Data Quality Assessment

**Realm:** Insights  
**Status:** ✅ Complete  
**Last Updated:** January 2026

---

## Overview

The Data Quality Assessment capability identifies root causes of data issues by analyzing parsing quality, data quality, and source quality. It helps answer: "Do we have a faded purchase order that's hard to read OR something that doesn't seem to be a purchase order at all?"

---

## Intent: `assess_data_quality`

Assesses data quality across three dimensions: parsing quality, data quality, and source quality.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `parsed_file_id` | string | Yes | Identifier for the parsed file result |
| `source_file_id` | string | Yes | Identifier for the source file |
| `parser_type` | string | No | Type of parser used (default: "unknown") |

### Response

```json
{
  "artifacts": {
    "quality_assessment": {
      "overall_quality": "good|fair|poor",
      "parsing_quality": {
        "status": "good|issues|failed",
        "issues": [
          {
            "type": "missing_field",
            "field": "field_name",
            "severity": "high|medium|low",
            "description": "Field was expected but not found"
          }
        ],
        "suggestions": ["Fix copybook", "Update parser configuration"]
      },
      "data_quality": {
        "status": "good|issues|poor",
        "issues": [
          {
            "type": "faded_document",
            "severity": "high",
            "description": "Document appears faded or corrupted"
          }
        ],
        "suggestions": ["Rescan document", "Check source file quality"]
      },
      "source_quality": {
        "status": "good|issues|poor",
        "issues": [
          {
            "type": "copybook_mismatch",
            "severity": "high",
            "description": "Copybook does not match file structure"
          }
        ],
        "suggestions": ["Update copybook", "Verify file format"]
      },
      "root_cause_analysis": {
        "primary_issue": "parsing|data|source",
        "confidence": 0.85,
        "recommendations": ["Primary issue is in parsing", "Consider re-parsing with updated copybook"]
      }
    },
    "parsed_file_id": "parsed_file_123",
    "source_file_id": "source_file_456"
  },
  "events": [
    {
      "type": "data_quality_assessed",
      "parsed_file_id": "parsed_file_123",
      "source_file_id": "source_file_456"
    }
  ]
}
```

---

## Use Cases

### 1. Insurance Policy Migration
**Scenario:** Processing 350k insurance policies from legacy mainframe systems.

**Use Case:** Assess quality of parsed policy data to identify:
- Copybook mismatches (source issue)
- Corrupted binary data (data issue)
- Parser configuration problems (parsing issue)

**Business Value:** Prevents downstream errors by identifying root causes early.

---

### 2. Permit Data Extraction
**Scenario:** Extracting structured data from PDF permits.

**Use Case:** Assess quality of extracted permit data to identify:
- Faded or scanned documents (data issue)
- OCR errors (parsing issue)
- Missing required fields (parsing or data issue)

**Business Value:** Ensures data accuracy for permit processing workflows.

---

### 3. Testing & Evaluation
**Scenario:** Analyzing test results and generating reports.

**Use Case:** Assess quality of test data to identify:
- Incomplete test results (data issue)
- Format mismatches (parsing issue)
- Source file corruption (source issue)

**Business Value:** Ensures reliable test analysis and reporting.

---

## Technical Details

### Implementation

The `assess_data_quality` intent is handled by the `DataQualityService` in the Insights Realm, which:

1. Retrieves parsed file results from State Surface
2. Retrieves embeddings from ArangoDB
3. Retrieves source file metadata from Supabase
4. Analyzes parsing quality (compares parsed results vs parser expectations)
5. Analyzes data quality (checks for anomalies, completeness, validity)
6. Analyzes source quality (checks copybook, format, structure)
7. Cross-references parsing + embeddings to identify root cause
8. Generates suggestions for each issue type

### Dependencies

- **Content Realm:** Provides parsed file results
- **ArangoDB:** Stores embeddings for semantic analysis
- **Supabase:** Stores source file metadata
- **State Surface:** Provides execution context

---

## Related Capabilities

- [Semantic Interpretation](semantic_interpretation.md) - Understand data meaning
- [Interactive Analysis](interactive_analysis.md) - Deep dive into data issues
- [Lineage Tracking](lineage_tracking.md) - Track data origins

---

## API Example

```python
intent = Intent(
    intent_type="assess_data_quality",
    parameters={
        "parsed_file_id": "parsed_file_123",
        "source_file_id": "source_file_456",
        "parser_type": "mainframe_binary"
    }
)

result = await runtime.execute(intent, context)
quality_assessment = result.artifacts["quality_assessment"]
```

---

**See Also:**
- [Insights Realm Overview](../architecture/north_star.md#23-domain-services-formerly-realms)
- [API Contracts](../execution/api_contracts_frontend_integration.md)
