# Solution Synthesis

**Realm:** Outcomes  
**Status:** ✅ Complete  
**Last Updated:** January 2026

---

## Overview

The Solution Synthesis capability synthesizes outputs from Content, Insights, and Journey realms into comprehensive business outcomes, generating summary reports and visualizations.

---

## Intent: `synthesize_outcome`

Synthesizes pillar outputs (Content, Insights, Journey) into a comprehensive summary with visualization.

### Parameters

No parameters required - reads pillar summaries from session state.

### Response

```json
{
  "artifacts": {
    "synthesis": {
      "summary_report": {
        "content_summary": {
          "files_processed": 1000,
          "parsing_success_rate": 0.98,
          "key_findings": ["All files parsed successfully", "5 files had quality issues"]
        },
        "insights_summary": {
          "interpretations_completed": 950,
          "quality_assessments": 1000,
          "key_findings": ["95% of data is high quality", "5% requires manual review"]
        },
        "journey_summary": {
          "workflows_created": 3,
          "sops_generated": 2,
          "key_findings": ["All workflows validated", "Coexistence analysis completed"]
        },
        "overall_assessment": {
          "status": "success",
          "readiness_score": 0.95,
          "recommendations": [
            "Proceed with migration",
            "Review 5% of data requiring manual attention"
          ]
        }
      }
    },
    "content_summary": {...},
    "insights_summary": {...},
    "journey_summary": {...},
    "summary_visual": {
      "image_base64": "...",
      "storage_path": "synthesis/session_123.png"
    }
  },
  "events": [
    {
      "type": "outcome_synthesized",
      "session_id": "session_123"
    }
  ]
}
```

---

## Use Cases

### 1. Migration Readiness Assessment
**Scenario:** Assessing readiness for insurance policy migration.

**Use Case:** Synthesize outcomes to:
- Combine file processing, data quality, and workflow readiness
- Generate overall migration readiness score
- Provide actionable recommendations

**Business Value:** Enables data-driven migration decisions.

---

### 2. Project Status Reporting
**Scenario:** Generating executive status reports.

**Use Case:** Synthesize outcomes to:
- Combine all pillar outputs into single report
- Generate visual summary
- Provide high-level assessment

**Business Value:** Enables executive decision-making.

---

### 3. Solution Validation
**Scenario:** Validating solution completeness.

**Use Case:** Synthesize outcomes to:
- Verify all pillars completed successfully
- Identify gaps or issues
- Generate validation report

**Business Value:** Ensures solution completeness.

---

## Technical Details

### Implementation

The `synthesize_outcome` intent:
1. Reads pillar summaries from session state (State Surface)
2. Generates summary report via `ReportGeneratorService`
3. Creates visualization via `VisualGenerationService`
4. Returns comprehensive synthesis

### Session State

Pillar summaries are stored in session state by each realm:
- `content_pillar_summary`
- `insights_pillar_summary`
- `journey_pillar_summary`

---

## Related Capabilities

- [Roadmap Generation](roadmap_generation.md) - Generate strategic roadmap from synthesis
- [POC Creation](poc_creation.md) - Create POC from synthesis
- [Visual Generation](../journey/visual_generation.md) - Generate synthesis visualizations

---

## API Example

```python
intent = Intent(
    intent_type="synthesize_outcome",
    parameters={}
)

result = await runtime.execute(intent, context)
summary = result.artifacts["synthesis"]["summary_report"]
visual = result.artifacts["summary_visual"]
```

---

**See Also:**
- [Outcomes Realm Overview](../architecture/north_star.md#23-domain-services-formerly-realms)
- [API Contracts](../execution/api_contracts_frontend_integration.md)
