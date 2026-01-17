# Roadmap Generation

**Realm:** Outcomes  
**Status:** ✅ Complete  
**Last Updated:** January 2026

---

## Overview

The Roadmap Generation capability creates strategic implementation roadmaps from pillar outputs, providing phased plans for solution implementation.

---

## Intent: `generate_roadmap`

Generates a strategic roadmap from Content, Insights, and Journey pillar outputs.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `additional_context` | object | No | Additional business context |
| `roadmap_options` | object | No | Options for roadmap generation (phases, timeline, etc.) |

### Response

```json
{
  "artifacts": {
    "roadmap": {
      "roadmap_id": "roadmap_123",
      "strategic_plan": {
        "overview": "Migration roadmap for 350k insurance policies",
        "phases": [
          {
            "phase": 1,
            "name": "Data Preparation",
            "duration": "4 weeks",
            "objectives": [
              "Complete data quality assessment",
              "Resolve quality issues",
              "Validate parsing accuracy"
            ],
            "dependencies": [],
            "risks": ["Data quality issues may extend timeline"],
            "success_criteria": ["95% data quality score", "All files parsed"]
          },
          {
            "phase": 2,
            "name": "Workflow Implementation",
            "duration": "6 weeks",
            "objectives": [
              "Create processing workflows",
              "Validate coexistence",
              "Generate SOPs"
            ],
            "dependencies": ["Phase 1"],
            "risks": ["Legacy system integration complexity"],
            "success_criteria": ["All workflows validated", "SOPs approved"]
          },
          {
            "phase": 3,
            "name": "Pilot Execution",
            "duration": "2 weeks",
            "objectives": [
              "Execute pilot with 1k policies",
              "Validate end-to-end process",
              "Refine workflows"
            ],
            "dependencies": ["Phase 2"],
            "risks": ["Unexpected data issues"],
            "success_criteria": ["100% pilot success", "No critical issues"]
          }
        ],
        "timeline": {
          "start_date": "2026-02-01",
          "end_date": "2026-04-15",
          "total_duration": "12 weeks"
        },
        "risk_assessment": {
          "overall_risk": "medium",
          "key_risks": [
            "Data quality issues",
            "Legacy system integration"
          ]
        }
      }
    },
    "roadmap_id": "roadmap_123",
    "roadmap_visual": {
      "image_base64": "...",
      "storage_path": "roadmaps/roadmap_123.png"
    }
  },
  "events": [
    {
      "type": "roadmap_generated",
      "roadmap_id": "roadmap_123",
      "session_id": "session_123"
    }
  ]
}
```

---

## Use Cases

### 1. Migration Planning
**Scenario:** Planning insurance policy migration.

**Use Case:** Generate roadmap to:
- Create phased implementation plan
- Identify dependencies and risks
- Provide timeline estimates

**Business Value:** Enables structured migration execution.

---

### 2. Project Planning
**Scenario:** Planning new solution implementation.

**Use Case:** Generate roadmap to:
- Break down implementation into phases
- Identify critical path
- Plan resource allocation

**Business Value:** Ensures realistic project planning.

---

### 3. Executive Reporting
**Scenario:** Presenting implementation plan to executives.

**Use Case:** Generate roadmap to:
- Provide high-level strategic plan
- Show timeline and milestones
- Identify risks and mitigation

**Business Value:** Enables executive decision-making.

---

## Technical Details

### Implementation

The `generate_roadmap` intent:
1. Reads pillar summaries from session state
2. Generates strategic plan via `RoadmapGenerationService`
3. Creates visualization via `VisualGenerationService`
4. Returns comprehensive roadmap

### Roadmap Structure

Roadmaps include:
- **Phases:** Sequential implementation phases
- **Dependencies:** Phase dependencies
- **Risks:** Identified risks and mitigation
- **Timeline:** Start/end dates and duration
- **Success Criteria:** Phase completion criteria

---

## Related Capabilities

- [Solution Synthesis](solution_synthesis.md) - Synthesize outcomes before roadmap
- [POC Creation](poc_creation.md) - Create POC from roadmap
- [Visual Generation](../journey/visual_generation.md) - Generate roadmap visualizations

---

## API Example

```python
intent = Intent(
    intent_type="generate_roadmap",
    parameters={
        "additional_context": {
            "business_goals": ["Complete migration by Q2", "Minimize downtime"],
            "constraints": ["Budget: $500k", "Team size: 10"]
        },
        "roadmap_options": {
            "max_phases": 5,
            "include_risk_assessment": True
        }
    }
)

result = await runtime.execute(intent, context)
roadmap = result.artifacts["roadmap"]["strategic_plan"]
visual = result.artifacts["roadmap_visual"]
```

---

**See Also:**
- [Outcomes Realm Overview](../architecture/north_star.md#23-domain-services-formerly-realms)
- [API Contracts](../execution/api_contracts_frontend_integration.md)
