# Lineage Tracking

**Realm:** Insights  
**Status:** ✅ Complete  
**Last Updated:** January 2026

---

## Overview

The Lineage Tracking capability visualizes data origins and transformations, showing how data flows from source files through parsing, interpretation, and analysis.

---

## Intent: `visualize_lineage`

Visualizes the complete lineage of a file, showing all transformations and relationships.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file_id` | string | Yes | Identifier for the source file |

### Response

```json
{
  "artifacts": {
    "lineage_visualization": {
      "file_id": "source_file_123",
      "lineage_graph": {
        "nodes": [
          {
            "id": "source_file_123",
            "type": "source_file",
            "label": "policy_data.bin",
            "metadata": {
              "upload_date": "2026-01-15T10:00:00Z",
              "file_type": "mainframe_binary"
            }
          },
          {
            "id": "parsed_file_456",
            "type": "parsed_result",
            "label": "Parsed Policy Data",
            "metadata": {
              "parser_type": "mainframe_binary",
              "parse_date": "2026-01-15T10:05:00Z"
            }
          },
          {
            "id": "interpretation_789",
            "type": "interpretation",
            "label": "Insurance Policy Interpretation",
            "metadata": {
              "interpretation_type": "guided",
              "guide_id": "guide_insurance_vli_001",
              "interpretation_date": "2026-01-15T10:10:00Z"
            }
          }
        ],
        "edges": [
          {
            "from": "source_file_123",
            "to": "parsed_file_456",
            "type": "parsed",
            "metadata": {
              "parser_version": "1.2.0"
            }
          },
          {
            "from": "parsed_file_456",
            "to": "interpretation_789",
            "type": "interpreted",
            "metadata": {
              "method": "guided_discovery"
            }
          }
        ]
      },
      "visualization": {
        "image_base64": "...",
        "storage_path": "lineage/source_file_123.png"
      }
    },
    "file_id": "source_file_123"
  },
  "events": [
    {
      "type": "lineage_visualized",
      "file_id": "source_file_123"
    }
  ]
}
```

---

## Use Cases

### 1. Compliance & Audit
**Scenario:** Demonstrating data provenance for compliance audits.

**Use Case:** Visualize lineage to show:
- Source of all data
- All transformations applied
- Who/what performed each transformation
- When transformations occurred

**Business Value:** Provides complete audit trail for compliance.

---

### 2. Data Quality Investigation
**Scenario:** Investigating data quality issues.

**Use Case:** Visualize lineage to trace:
- Where data quality issues originated
- Which transformations may have introduced errors
- Impact of issues on downstream processes

**Business Value:** Enables root cause analysis of data quality problems.

---

### 3. Migration Planning
**Scenario:** Planning migration from legacy systems.

**Use Case:** Visualize lineage to understand:
- Data flow through existing systems
- Dependencies between data elements
- Transformation requirements

**Business Value:** Informs migration strategy and risk assessment.

---

## Technical Details

### Implementation

The `visualize_lineage` intent uses the `LineageVisualizationService` which:
1. Queries Supabase for all lineage records related to the file
2. Builds a graph structure (nodes and edges)
3. Retrieves metadata for each node
4. Generates visualization (graph diagram)
5. Stores visualization in file storage

### Lineage Data Sources

Lineage is tracked automatically when:
- Files are parsed (Content Realm)
- Data is interpreted (Insights Realm)
- Data is analyzed (Insights Realm)
- Workflows are created (Journey Realm)

All lineage records are stored in Supabase with:
- Source file reference
- Transformation type
- Timestamp
- User/agent attribution
- Metadata

---

## Related Capabilities

- [Data Quality Assessment](data_quality.md) - Assess quality with lineage context
- [Semantic Interpretation](semantic_interpretation.md) - Track interpretation lineage
- [File Parsing](file_parsing.md) - Track parsing lineage

---

## API Example

```python
intent = Intent(
    intent_type="visualize_lineage",
    parameters={
        "file_id": "source_file_123"
    }
)

result = await runtime.execute(intent, context)
lineage_graph = result.artifacts["lineage_visualization"]["lineage_graph"]
visualization = result.artifacts["lineage_visualization"]["visualization"]
```

---

**See Also:**
- [Insights Realm Overview](../architecture/north_star.md#23-domain-services-formerly-realms)
- [API Contracts](../execution/api_contracts_frontend_integration.md)
