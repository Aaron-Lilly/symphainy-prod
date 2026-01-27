# Intent Contract: analyze_coexistence

**Intent:** analyze_coexistence  
**Intent Type:** `analyze_coexistence`  
**Journey:** Coexistence Analysis (`journey_coexistence_analysis`)  
**Realm:** Journey Realm  
**Status:** ✅ **COMPREHENSIVE**  
**Priority:** 🔴 **PRIORITY 1** - Core coexistence analysis

---

## 1. Intent Overview

### Purpose
Analyze a workflow for coexistence opportunities (human+AI optimization). Identifies friction points that can be automated, high-value human focus areas, and hybrid opportunities where AI can assist while humans provide oversight.

### Intent Flow
```
[User selects workflow to analyze]
    ↓
[analyze_coexistence intent]
    ↓
[CoexistenceAnalysisService.analyze_coexistence()]
    - OR CoexistenceAnalysisAgent (agentic forward pattern)
    ↓
[Identify friction points (automatable tasks)]
[Identify human focus areas (decision-making, judgment)]
[Identify hybrid opportunities (AI + human oversight)]
    ↓
[Return coexistence analysis artifact]
```

### Expected Observable Artifacts
- `coexistence_analysis` artifact with:
  - `analysis_id` - Unique analysis identifier
  - `workflow_id` - Source workflow identifier
  - `coexistence_opportunities` - Array of opportunities
  - `friction_points` - Tasks suitable for AI automation
  - `human_focus_areas` - High-value human tasks
  - `recommendations` - Optimization recommendations
  - `integration_points` - System integration points
  - `conflicts` - Potential conflicts identified
  - `dependencies` - Task dependencies

---

## 2. Intent Parameters

### Required Parameters

| Parameter | Type | Description | Validation |
|-----------|------|-------------|------------|
| `workflow_id` | `string` | Workflow identifier to analyze | Required, non-empty |

### Optional Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `analysis_options` | `object` | Analysis configuration | `{}` |
| `chunks` | `array` | Deterministic chunks (for semantic understanding) | `null` |
| `semantic_signals` | `object` | Semantic signals (Phase 3) | `null` |

### Context Metadata (from ExecutionContext)

| Metadata Key | Type | Description | Source |
|--------------|------|-------------|--------|
| `tenant_id` | `string` | Tenant identifier | Runtime (required) |
| `session_id` | `string` | Session identifier | Runtime (required) |
| `workflow_{workflow_id}` | `object` | Workflow data in context metadata | From prior intent |

---

## 3. Intent Returns

### Success Response

```json
{
  "artifacts": {
    "coexistence_analysis": {
      "result_type": "coexistence_analysis",
      "semantic_payload": {
        "workflow_id": "workflow_abc123",
        "analysis_id": "analysis_xyz789",
        "status": "completed",
        "friction_points_identified": 5,
        "human_focus_areas": ["approval", "review", "decision_making"]
      },
      "renderings": {
        "coexistence_analysis": {
          "workflow_id": "workflow_abc123",
          "analysis_status": "completed",
          "coexistence_opportunities": [
            {
              "task_id": "task_1",
              "task_name": "Data Extraction",
              "opportunity_type": "friction_removal",
              "description": "Task has friction that can be removed with AI assistance",
              "current_actor": "human",
              "recommended_actor": "symphainy",
              "friction_type": "repetitive_data_processing",
              "human_value_freed": "decision_making_strategic_analysis"
            }
          ],
          "integration_points": [...],
          "conflicts": [...],
          "dependencies": [...],
          "recommendations": [...],
          "friction_removal_potential": 0.6,
          "human_tasks_count": 3,
          "ai_assisted_tasks_count": 5,
          "hybrid_tasks_count": 2
        },
        "reasoning": "Agent reasoning (if using agentic pattern)"
      },
      "metadata": {
        "artifact_id": "artifact_abc123"
      }
    }
  },
  "events": [
    {
      "type": "coexistence_analyzed",
      "workflow_id": "workflow_abc123",
      "analysis_id": "analysis_xyz789",
      "artifact_id": "artifact_abc123"
    }
  ]
}
```

### Error Response

```json
{
  "error": "workflow_id is required for analyze_coexistence intent",
  "error_code": "VALIDATION_ERROR",
  "execution_id": "exec_abc123"
}
```

---

## 4. Artifact Registration

### Artifact Plane Registration
- **Artifact Type:** `coexistence_analysis`
- **Lifecycle State:** `draft` (initial)
- **Owner:** `client`
- **Purpose:** `decision_support`
- **Source Artifacts:** `[workflow_id]`

### State Surface Updates
- Analysis artifact registered in Artifact Plane (if available)
- Execution state stored with artifacts

---

## 5. Idempotency

### Idempotency Key
`analysis_fingerprint = hash(workflow_id + tenant_id)`

### Behavior
- Same workflow + tenant = same analysis artifact returned
- Analysis may differ if workflow data changes
- Safe to retry on failure

---

## 6. Implementation Details

### Handler Location
`symphainy_platform/realms/journey/orchestrators/journey_orchestrator.py::JourneyOrchestrator._handle_analyze_coexistence`

### Key Implementation Steps
1. Validate `workflow_id` is provided
2. Check if `CoexistenceAnalysisAgent` is available
3. If agent available: Use agentic forward pattern (agent reasons, uses service as tool)
4. If agent unavailable: Fallback to `CoexistenceAnalysisService.analyze_coexistence()`
5. Extract semantic payload from result
6. Register artifact in Artifact Plane (if available)
7. Create structured artifact for execution state
8. Return artifacts and events

### Enabling Services
- **CoexistenceAnalysisService:** `symphainy_platform/realms/journey/enabling_services/coexistence_analysis_service.py`
  - `analyze_coexistence()` - Analyze workflow tasks for coexistence

### Agents (Agentic Forward Pattern)
- **CoexistenceAnalysisAgent:** `symphainy_platform/realms/journey/agents/coexistence_analysis_agent.py`
  - Uses CoexistenceAnalysisService as MCP tool
  - Provides reasoning about coexistence opportunities

### Analysis Logic
Tasks are categorized by keywords:
- **Friction removal (AI):** "data", "extract", "parse", "validate", "transform", "analyze", "process"
- **Human focus:** "approve", "review", "decide", "judge", "evaluate", "sign"
- **Hybrid:** "verify", "check", "validate", "confirm"

---

## 7. Frontend Integration

### Frontend Usage (JourneyAPIManager.ts)
```typescript
// JourneyAPIManager.analyzeCoexistence()
const result = await journeyManager.analyzeCoexistence(
  sopId,
  workflowId,
  { detailed_analysis: true }
);

if (result.success) {
  const analysis = result.coexistence_analysis;
  // Display friction points, human focus areas, recommendations
}
```

### Expected Frontend Behavior
1. User selects workflow for analysis
2. Frontend submits `analyze_coexistence` intent
3. Track execution via `trackExecution()`
4. Wait for completion
5. Extract `coexistence_analysis` from artifacts
6. Display analysis results (friction points, recommendations)
7. Store in realm state for subsequent intents

---

## 8. Error Handling

### Validation Errors
- `workflow_id` missing → `ValueError("workflow_id is required for analyze_coexistence intent")`

### Runtime Errors
- Workflow data not found → Analysis with empty opportunities
- Agent unavailable → Fallback to service (degraded confidence)
- Service error → RuntimeError with details

### Error Response Format
```json
{
  "error": "Error message",
  "error_code": "ERROR_CODE",
  "execution_id": "exec_abc123",
  "intent_type": "analyze_coexistence"
}
```

---

## 9. Testing & Validation

### Happy Path
1. User has workflow in context
2. Submit `analyze_coexistence` intent
3. Agent/service analyzes workflow
4. Return coexistence opportunities
5. Artifact registered in Artifact Plane

### Boundary Violations
- Missing `workflow_id` → Validation error
- Workflow data empty → Analysis with zero opportunities

### Failure Scenarios
- Agent fails → Fallback to service (degraded confidence)
- Service fails → RuntimeError

---

## 10. Contract Compliance

### Required Artifacts
- `coexistence_analysis` - Analysis artifact with opportunities and recommendations

### Required Events
- `coexistence_analyzed` - With `workflow_id`, `analysis_id`, `artifact_id`

### Security Requirements
- Workflow data scoped by tenant
- Analysis artifact includes lineage to source workflow

---

## 11. Cross-Reference Analysis

### Journey Contract Says
- `analyze_coexistence` - Step 1 of coexistence analysis journey
- `identify_opportunities` - Step 2 (separate intent)

### Implementation Does
- ✅ `analyze_coexistence` handles both analysis and opportunity identification
- ✅ Uses agentic forward pattern (agent + service fallback)
- ✅ Registers artifact in Artifact Plane
- ⚠️ `identify_opportunities` is integrated into `analyze_coexistence` (no separate intent)

### Frontend Expects
- ✅ Intent type: `analyze_coexistence`
- ✅ Returns `coexistence_analysis` with opportunities
- ✅ Execution tracking via `trackExecution()`

### Gaps/Discrepancies
- **NAMING:** Contract says `identify_opportunities` is separate; implementation combines it
- **Recommendation:** Remove `identify_opportunities` from contract (integrated into analysis)

---

**Last Updated:** January 27, 2026  
**Owner:** Journey Realm Solution Team  
**Status:** ✅ **COMPREHENSIVE**
