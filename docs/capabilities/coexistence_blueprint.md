# Coexistence Blueprint

**Realm:** Journey  
**Status:** ✅ Complete  
**Last Updated:** January 2026

---

## Overview

The Coexistence Blueprint capability creates comprehensive implementation blueprints that show the current state, recommended coexistence state, transition roadmap, and responsibility matrix. It synthesizes coexistence analysis into actionable implementation plans.

---

## Intent: `create_blueprint`

Creates a comprehensive coexistence blueprint with visual workflow charts and responsibility matrix.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `workflow_id` | string | Yes | Identifier for the workflow to create blueprint for |
| `current_state_workflow_id` | string | No | Identifier for existing workflow (if different from workflow_id) |

### Response

```json
{
  "artifacts": {
    "blueprint": {
      "blueprint_id": "blueprint_123",
      "workflow_id": "workflow_123",
      "current_state": {
        "description": "Existing manual process for insurance policy processing",
        "workflow_chart": {
          "image_base64": "...",
          "storage_path": "blueprints/blueprint_123_current_state.png"
        },
        "workflow_definition": {
          "steps": [
            {
              "step": 1,
              "name": "Receive Policy File",
              "actor": "human",
              "description": "Manual file upload"
            },
            {
              "step": 2,
              "name": "Validate Policy",
              "actor": "legacy_system",
              "description": "Legacy validation system"
            }
          ],
          "decision_points": 2,
          "actors": ["human", "legacy_system"]
        }
      },
      "coexistence_state": {
        "description": "Recommended process with Symphainy integration for automated processing",
        "workflow_chart": {
          "image_base64": "...",
          "storage_path": "blueprints/blueprint_123_coexistence_state.png"
        },
        "workflow_definition": {
          "steps": [
            {
              "step": 1,
              "name": "Ingest Policy File",
              "actor": "symphainy",
              "description": "Automated file ingestion and parsing"
            },
            {
              "step": 2,
              "name": "Assess Data Quality",
              "actor": "symphainy",
              "description": "Automated quality assessment"
            },
            {
              "step": 3,
              "name": "Review Exceptions",
              "actor": "human",
              "description": "Human review of flagged policies"
            }
          ],
          "decision_points": 3,
          "actors": ["human", "symphainy", "legacy_system"]
        }
      },
      "roadmap": {
        "description": "Phased transition from current to coexistence state",
        "phases": [
          {
            "phase": 1,
            "name": "Foundation Setup",
            "duration": "2 weeks",
            "objectives": [
              "Set up Symphainy integration points",
              "Configure data sync with legacy system",
              "Test file ingestion pipeline"
            ],
            "dependencies": [],
            "risks": ["Integration complexity"],
            "success_criteria": ["Integration points operational", "Data sync validated"]
          },
          {
            "phase": 2,
            "name": "Parallel Operation",
            "duration": "4 weeks",
            "objectives": [
              "Run both processes in parallel",
              "Validate coexistence",
              "Compare results"
            ],
            "dependencies": ["Phase 1"],
            "risks": ["Data inconsistency"],
            "success_criteria": ["100% parallel execution", "Results match"]
          },
          {
            "phase": 3,
            "name": "Full Migration",
            "duration": "2 weeks",
            "objectives": [
              "Switch to coexistence state",
              "Decommission old process",
              "Monitor performance"
            ],
            "dependencies": ["Phase 2"],
            "risks": ["Downtime"],
            "success_criteria": ["Zero downtime migration", "Performance maintained"]
          }
        ],
        "timeline": {
          "start_date": "2026-02-01",
          "end_date": "2026-03-15",
          "total_duration": "8 weeks"
        }
      },
      "responsibility_matrix": {
        "description": "Clear delineation of responsibilities in coexistence state",
        "note": "Platform systems (storage, state management, etc.) are a black box and not listed here",
        "responsibilities": [
          {
            "step": "Policy Data Ingestion",
            "human": ["Upload files", "Review ingestion exceptions"],
            "ai_symphainy": [
              "Parse files (PDF, Excel, binary)",
              "Extract structured data",
              "Assess data quality",
              "Flag anomalies"
            ],
            "external_systems": []
          },
          {
            "step": "Policy Validation",
            "human": [
              "Review flagged policies",
              "Approve exceptions",
              "Make complex decisions"
            ],
            "ai_symphainy": [
              "Validate data quality",
              "Check business rules",
              "Flag anomalies",
              "Generate recommendations"
            ],
            "external_systems": [
              "Legacy Policy System (validate policy numbers)",
              "Underwriting System (check coverage limits)"
            ]
          },
          {
            "step": "Dunning Letter Generation",
            "human": [
              "Review past due accounts",
              "Approve dunning letter content"
            ],
            "ai_symphainy": [
              "Identify past due accounts",
              "Generate account list",
              "Format data for CRM system"
            ],
            "external_systems": [
              "Client Billing System (retrieve account data)",
              "Client CRM System (generate and send dunning letters)"
            ]
          },
          {
            "step": "Policy Processing",
            "human": [
              "Handle complex cases",
              "Make policy decisions",
              "Approve workflows"
            ],
            "ai_symphainy": [
              "Process standard policies",
              "Generate insights",
              "Create workflows",
              "Optimize processes"
            ],
            "external_systems": [
              "Legacy Policy System (update policy status)",
              "Modern Policy System (sync policy data)"
            ]
          }
        ]
      },
      "sections": [
        {
          "section": "Executive Summary",
          "content": "This blueprint outlines the coexistence strategy for integrating Symphainy into the existing insurance policy processing workflow..."
        },
        {
          "section": "Current State Analysis",
          "content": "Current process relies on manual file uploads and legacy validation systems..."
        },
        {
          "section": "Coexistence State Design",
          "content": "Recommended process integrates Symphainy for automated ingestion, quality assessment, and processing..."
        },
        {
          "section": "Transition Roadmap",
          "content": "Phased approach ensures zero downtime and risk mitigation..."
        },
        {
          "section": "Responsibility Matrix",
          "content": "Clear delineation ensures accountability and proper handoffs..."
        },
        {
          "section": "Integration Requirements",
          "content": "Technical integration points and requirements...",
          "integration_points": [
            {
              "point": "policy_status_update",
              "type": "shared_resource",
              "conflicts": 1,
              "dependencies": 0,
              "requirements": ["Transaction locks", "Status synchronization"]
            }
          ],
          "resource_requirements": [
            "Symphainy platform access",
            "Legacy system API access",
            "Database connection pool"
          ]
        },
        {
          "section": "Risk Mitigation",
          "content": "Identified risks and mitigation strategies...",
          "risks": [
            {
              "risk": "Data inconsistency during parallel operation",
              "probability": "medium",
              "impact": "high",
              "mitigation": "Real-time sync validation, automated reconciliation"
            }
          ],
          "mitigations": [
            "Automated testing in Phase 2",
            "Rollback procedures",
            "Monitoring and alerting"
          ]
        }
      ],
      "metadata": {
        "created_date": "2026-01-15T10:00:00Z",
        "version": "1.0"
      }
    },
    "workflow_id": "workflow_123"
  },
  "events": [
    {
      "type": "blueprint_created",
      "workflow_id": "workflow_123"
    }
  ]
}
```

---

## Use Cases

### 1. Legacy System Integration
**Scenario:** Integrating Symphainy into existing insurance policy processing.

**Use Case:** Create blueprint to:
- Visualize current manual process
- Design coexistence state with automation
- Plan phased transition
- Define responsibility matrix

**Business Value:** Provides clear implementation roadmap with visual guidance.

---

### 2. Process Modernization
**Scenario:** Modernizing processes while maintaining legacy operations.

**Use Case:** Create blueprint to:
- Document current state workflow
- Design coexistence state
- Create transition roadmap
- Clarify who does what

**Business Value:** Ensures smooth transition without disrupting operations.

---

### 3. Stakeholder Communication
**Scenario:** Communicating coexistence strategy to stakeholders.

**Use Case:** Use blueprint to:
- Show visual workflow comparisons
- Explain transition timeline
- Clarify responsibilities
- Demonstrate value

**Business Value:** Enables stakeholder buy-in and alignment.

---

## Technical Details

### Implementation

The `create_blueprint` intent uses the `CoexistenceAnalysisService` which:
1. Retrieves coexistence analysis results
2. Retrieves current state workflow definition
3. Generates current state workflow chart (VisualGenerationService)
4. Designs coexistence state workflow (integrates Symphainy)
5. Generates coexistence state workflow chart (VisualGenerationService)
6. Creates transition roadmap (phased approach)
7. Generates responsibility matrix (human, AI, system)
8. Synthesizes into comprehensive blueprint

### Visual Components

**Current State Workflow Chart:**
- Visual representation of existing process
- Shows steps, decision points, actors
- Generated from workflow definition or process documentation

**Coexistence State Workflow Chart:**
- Visual representation of recommended process
- Shows Symphainy integration points
- Generated from coexistence analysis + current state

### Responsibility Matrix

Three responsibility categories:
- **Human:** Manual tasks, decisions, reviews, approvals
- **AI/Symphainy:** Automated processing, analysis, insights, recommendations
- **External Systems:** Client's external systems (Billing, CRM, Legacy systems, etc.) that we integrate with

**Note:** Platform systems (storage, state management, databases) are a "black box" and not listed in the responsibility matrix - they just work.

---

## Intent: `create_solution_from_blueprint`

Converts a blueprint into an implementation-ready platform solution using the Solution SDK.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `blueprint_id` | string | Yes | Identifier for the blueprint to convert |

### Response

```json
{
  "artifacts": {
    "solution": {
      "solution_id": "solution_123",
      "solution": {
        "solution_id": "solution_123",
        "context": {
          "goals": ["Foundation Setup: Set up Symphainy integration points", "..."],
          "constraints": ["Symphainy platform access", "..."],
          "risk": "Medium"
        },
        "domain_service_bindings": [
          {
            "domain": "content",
            "system_name": "symphainy_platform",
            "adapter_type": "internal_adapter"
          },
          {
            "domain": "insights",
            "system_name": "symphainy_platform",
            "adapter_type": "internal_adapter"
          },
          {
            "domain": "journey",
            "system_name": "symphainy_platform",
            "adapter_type": "internal_adapter"
          }
        ],
        "supported_intents": [
          "analyze_coexistence",
          "create_blueprint",
          "create_workflow",
          "create_solution_from_blueprint"
        ]
      },
      "source": "blueprint",
      "source_id": "blueprint_123"
    },
    "solution_id": "solution_123",
    "blueprint_id": "blueprint_123"
  },
  "events": [
    {
      "type": "solution_created_from_blueprint",
      "solution_id": "solution_123",
      "blueprint_id": "blueprint_123",
      "session_id": "session_123"
    }
  ]
}
```

---

## Related Capabilities

- [Coexistence Analysis](coexistence_analysis.md) - Analyze coexistence (prerequisite)
- [Workflow Creation](workflow_creation.md) - Create workflows from blueprints
- [Visual Generation](visual_generation.md) - Generate workflow charts
- [Solution Synthesis](../outcomes/solution_synthesis.md) - Similar capability in Outcomes Realm

---

## API Examples

### Create Blueprint

```python
intent = Intent(
    intent_type="create_blueprint",
    parameters={
        "workflow_id": "workflow_123",
        "current_state_workflow_id": "legacy_workflow_456"  # Optional
    }
)

result = await runtime.execute(intent, context)
blueprint = result.artifacts["blueprint"]
current_chart = blueprint["current_state"]["workflow_chart"]
coexistence_chart = blueprint["coexistence_state"]["workflow_chart"]
roadmap = blueprint["roadmap"]
responsibility_matrix = blueprint["responsibility_matrix"]
```

### Create Solution from Blueprint

```python
# First create blueprint
blueprint_intent = Intent(
    intent_type="create_blueprint",
    parameters={"workflow_id": "workflow_123"}
)
blueprint_result = await runtime.execute(blueprint_intent, context)
blueprint_id = blueprint_result.artifacts["blueprint"]["blueprint_id"]

# Then create solution from blueprint
solution_intent = Intent(
    intent_type="create_solution_from_blueprint",
    parameters={"blueprint_id": blueprint_id}
)
solution_result = await runtime.execute(solution_intent, context)
solution_id = solution_result.artifacts["solution"]["solution_id"]
```

---

**See Also:**
- [Journey Realm Overview](../architecture/north_star.md#23-domain-services-formerly-realms)
- [API Contracts](../execution/api_contracts_frontend_integration.md)
- [Gap Analysis](../execution/journey_realm_blueprint_gap_analysis.md)
