# Interactive Analysis

**Realm:** Insights  
**Status:** ✅ Complete  
**Last Updated:** January 2026

---

## Overview

The Interactive Analysis capability provides deep analysis of structured and unstructured data, with optional "deep dive" agent sessions for complex analysis.

---

## Intents

### 1. `analyze_structured_data`

Analyzes structured data (e.g., parsed Excel, CSV, database records) to extract insights, patterns, and business meaning.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `parsed_file_id` or `parsed_result_id` | string | Yes | Identifier for the parsed file result |
| `analysis_options` | object | No | Options for analysis (fields to analyze, depth, etc.) |

#### Response

```json
{
  "artifacts": {
    "structured_analysis": {
      "summary": {
        "record_count": 1000,
        "field_count": 15,
        "data_types": {
          "numeric": 8,
          "text": 5,
          "date": 2
        }
      },
      "insights": [
        {
          "type": "pattern",
          "description": "Policy numbers follow format: XXX-XXXX-XXXX",
          "confidence": 0.95
        },
        {
          "type": "anomaly",
          "description": "5 records have negative coverage amounts",
          "severity": "high"
        }
      ],
      "statistics": {
        "coverage_amount": {
          "mean": 500000,
          "median": 450000,
          "std_dev": 150000
        }
      }
    },
    "parsed_file_id": "parsed_file_123"
  },
  "events": [
    {
      "type": "structured_data_analyzed",
      "parsed_file_id": "parsed_file_123"
    }
  ]
}
```

---

### 2. `analyze_unstructured_data`

Analyzes unstructured data (e.g., PDF text, documents) with optional deep dive agent sessions for complex analysis.

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `parsed_file_id` or `parsed_result_id` | string | Yes | Identifier for the parsed file result |
| `analysis_options` | object | No | Options including `deep_dive: true` for agent sessions |

#### Response

```json
{
  "artifacts": {
    "unstructured_analysis": {
      "summary": {
        "document_type": "insurance_policy",
        "page_count": 12,
        "word_count": 3500,
        "sections": ["terms", "coverage", "exclusions", "beneficiaries"]
      },
      "key_findings": [
        {
          "finding": "Policy includes rider for long-term care",
          "location": "page 8, section 3",
          "confidence": 0.92
        }
      ],
      "deep_dive": {
        "session_id": "agent_session_789",
        "status": "active",
        "initial_questions": [
          "What are the coverage limits?",
          "Are there any exclusions that might affect claims?"
        ]
      }
    },
    "parsed_file_id": "parsed_file_123",
    "deep_dive_initiated": true
  },
  "events": [
    {
      "type": "unstructured_data_analyzed",
      "parsed_file_id": "parsed_file_123",
      "deep_dive": true
    }
  ]
}
```

---

## Use Cases

### 1. Insurance Policy Analysis (Structured)
**Scenario:** Analyzing 350k variable life insurance policies.

**Use Case:** Use `analyze_structured_data` to:
- Identify patterns in policy data
- Detect anomalies (negative amounts, missing beneficiaries)
- Generate statistics for reporting

**Business Value:** Ensures data quality and identifies issues before migration.

---

### 2. Permit Document Analysis (Unstructured)
**Scenario:** Analyzing PDF permits for key information.

**Use Case:** Use `analyze_unstructured_data` with deep dive to:
- Extract key sections (terms, dates, restrictions)
- Answer complex questions via agent session
- Generate structured summaries

**Business Value:** Automates permit review and extraction.

---

### 3. Test Results Analysis (Structured)
**Scenario:** Analyzing test results and generating reports.

**Use Case:** Use `analyze_structured_data` to:
- Calculate test statistics
- Identify patterns in test outcomes
- Generate summary reports

**Business Value:** Accelerates test analysis and reporting.

---

## Technical Details

### Deep Dive Agent Sessions

When `deep_dive: true` is set in `analysis_options`:
- Initiates an agent session for interactive analysis
- Returns `session_id` for continued interaction
- Agent can ask clarifying questions and provide detailed insights

### Lineage Tracking

All analyses are tracked in Supabase for lineage visualization:
- Links parsed files to analysis results
- Records agent session IDs (for deep dive)
- Enables traceability from source to insights

---

## Related Capabilities

- [Data Quality Assessment](data_quality.md) - Assess quality before analysis
- [Semantic Interpretation](semantic_interpretation.md) - Understand data meaning
- [Guided Discovery](guided_discovery.md) - Systematic exploration

---

## API Examples

### Structured Analysis

```python
intent = Intent(
    intent_type="analyze_structured_data",
    parameters={
        "parsed_file_id": "parsed_file_123",
        "analysis_options": {
            "fields": ["coverage_amount", "beneficiary"],
            "include_statistics": True
        }
    }
)

result = await runtime.execute(intent, context)
insights = result.artifacts["structured_analysis"]["insights"]
```

### Unstructured Analysis with Deep Dive

```python
intent = Intent(
    intent_type="analyze_unstructured_data",
    parameters={
        "parsed_file_id": "parsed_file_123",
        "analysis_options": {
            "deep_dive": True,
            "focus_areas": ["coverage", "exclusions"]
        }
    }
)

result = await runtime.execute(intent, context)
session_id = result.artifacts["unstructured_analysis"]["deep_dive"]["session_id"]
```

---

**See Also:**
- [Insights Realm Overview](../architecture/north_star.md#23-domain-services-formerly-realms)
- [API Contracts](../execution/api_contracts_frontend_integration.md)
