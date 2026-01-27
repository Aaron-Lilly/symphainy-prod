# Intent Contract: synthesize_outcome

**Intent:** synthesize_outcome  
**Intent Type:** `synthesize_outcome`  
**Journey:** Solution Synthesis (`journey_solution_synthesis`)  
**Realm:** Solution Realm (Implementation: Outcomes Realm)  
**Status:** ✅ **IMPLEMENTED**  
**Priority:** 🔴 **PRIORITY 1**

---

## 1. Intent Overview

### Purpose
Synthesize business outcomes from Content, Insights, and Journey realms into a unified solution summary. This intent aggregates pillar summaries from session state, uses OutcomesSynthesisAgent to reason about the data, and generates a comprehensive synthesis with realm-specific visualizations.

### Intent Flow
```
[Frontend: OutcomesAPIManager.synthesizeOutcome()]
    ↓
[submitIntent("synthesize_outcome", { synthesis_options })]
    ↓
[Runtime: ExecutionLifecycleManager.execute()]
    ↓
[OutcomesOrchestrator._handle_synthesize_outcome()]
    ↓
[Read pillar summaries from session state]
    ↓
[OutcomesSynthesisAgent.process_request() - synthesis]
    ↓
[OutcomesSynthesisAgent.process_request() - generate visuals]
    ↓
[ReportGeneratorService.generate_pillar_summary()]
    ↓
[VisualGenerationService.generate_summary_visual()]
    ↓
[Return structured artifact]
```

### Expected Observable Artifacts
- `solution` artifact with:
  - `result_type`: "solution"
  - `semantic_payload`: { solution_id, session_id, status }
  - `renderings`: { synthesis, content_summary, insights_summary, journey_summary, realm_visuals, summary_visual, reasoning }

---

## 2. Intent Parameters

### Required Parameters

| Parameter | Type | Description | Validation |
|-----------|------|-------------|------------|
| None | - | No required parameters | - |

### Optional Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `synthesis_options` | `object` | Options for synthesis customization | `{}` |

### Context Metadata (from ExecutionContext)

| Metadata Key | Type | Description | Source |
|--------------|------|-------------|--------|
| `session_id` | `string` | Session identifier | Runtime (required) |
| `tenant_id` | `string` | Tenant identifier | Runtime (required) |
| `state_surface` | `object` | State Surface reference | Runtime |

---

## 3. Intent Returns

### Success Response

```json
{
  "artifacts": {
    "solution": {
      "result_type": "solution",
      "semantic_payload": {
        "solution_id": "synthesis_abc123",
        "session_id": "session_xyz789",
        "status": "completed"
      },
      "renderings": {
        "synthesis": {
          "overall_synthesis": "...",
          "key_findings": ["..."],
          "recommendations": ["..."]
        },
        "content_summary": {
          "files_processed": 5,
          "total_records": 1000,
          "data_quality_score": 0.95
        },
        "insights_summary": {
          "interpretations_generated": 3,
          "quality_assessments": 2,
          "relationships_mapped": 15
        },
        "journey_summary": {
          "workflows_created": 2,
          "sops_generated": 1
        },
        "realm_visuals": {
          "content": {...},
          "insights": {...},
          "journey": {...}
        },
        "summary_visual": {
          "image_base64": "...",
          "storage_path": "gs://bucket/path/summary.png"
        },
        "reasoning": "Agent reasoning trace..."
      }
    }
  },
  "events": [
    {
      "type": "outcome_synthesized",
      "session_id": "session_xyz789"
    }
  ]
}
```

### Error Response

```json
{
  "error": "Failed to synthesize outcome: [reason]",
  "error_code": "SYNTHESIS_ERROR",
  "execution_id": "exec_abc123"
}
```

---

## 4. Artifact Registration

### State Surface Registration
- **Artifact ID:** Generated from synthesis result (`solution_id`)
- **Artifact Type:** `"solution"`
- **Lifecycle State:** `"READY"` (no intermediate states)
- **Produced By:** `{ intent: "synthesize_outcome", execution_id: "<execution_id>" }`
- **Semantic Descriptor:** `{ schema: "solution_v1", synthesis_type: "cross_pillar" }`
- **Parent Artifacts:** None (derived from session state)
- **Materializations:** Optional summary visualization in GCS

### Artifact Index Registration
- Not indexed in Supabase (stored in frontend realm state)
- Session-scoped artifact

---

## 5. Idempotency

### Idempotency Key
```
idempotency_key = hash(session_id + timestamp)
```

### Scope
- Per session
- Not idempotent - regenerates synthesis each time

### Behavior
- Each invocation generates a fresh synthesis
- Previous syntheses are overwritten in frontend state
- Useful for refreshing synthesis after pillar work updates

---

## 6. Implementation Details

### Handler Location
`symphainy_platform/realms/outcomes/orchestrators/outcomes_orchestrator.py::_handle_synthesize_outcome`

### Key Implementation Steps
1. Read pillar summaries from session state via `context.state_surface.get_session_state()`
2. Extract `content_pillar_summary`, `insights_pillar_summary`, `journey_pillar_summary`
3. Call `OutcomesSynthesisAgent.process_request()` for synthesis
4. Call `OutcomesSynthesisAgent.process_request()` for realm visuals
5. Call `ReportGeneratorService.generate_pillar_summary()` for report
6. Call `VisualGenerationService.generate_summary_visual()` for visualization
7. Construct structured artifact with `create_structured_artifact()`
8. Return artifact with events

### Dependencies
- **Public Works:** None directly (uses session state)
- **State Surface:** `get_session_state()` for pillar summaries
- **Runtime:** `ExecutionContext` with session_id, tenant_id
- **Agents:** `OutcomesSynthesisAgent`
- **Services:** `ReportGeneratorService`, `VisualGenerationService`

---

## 7. Frontend Integration

### Frontend Usage
```typescript
// OutcomesAPIManager.synthesizeOutcome()
async synthesizeOutcome(
  synthesisOptions?: Record<string, any>
): Promise<OutcomeSynthesisResponse> {
  const platformState = this.getPlatformState();
  
  // Session validation
  validateSession(platformState, "synthesize outcome");

  // Submit intent
  const execution = await platformState.submitIntent(
    "synthesize_outcome",
    {
      synthesis_options: synthesisOptions || {}
    }
  );

  // Wait for execution
  const result = await this._waitForExecution(execution, platformState);

  if (result.status === "completed" && result.artifacts?.synthesis_summary) {
    // Update realm state
    platformState.setRealmState("outcomes", "syntheses", {
      ...platformState.getRealmState("outcomes", "syntheses") || {},
      [result.artifacts.synthesis_summary.synthesis_id || "latest"]: result.artifacts.synthesis_summary
    });

    return { success: true, synthesis: result.artifacts.synthesis_summary };
  }
  
  throw new Error(result.error || "Failed to synthesize outcome");
}
```

### Expected Frontend Behavior
1. Call `synthesizeOutcome()` when user clicks "Generate Artifacts"
2. Show loading state during synthesis
3. Display synthesis result with:
   - Overall synthesis summary
   - Content pillar summary
   - Insights pillar summary
   - Journey pillar summary
   - Realm-specific visuals
   - Summary visualization image
4. Store synthesis in realm state for later retrieval

---

## 8. Error Handling

### Validation Errors
- No session → `"Session required to synthesize outcome"`

### Runtime Errors
- State Surface unavailable → Synthesis proceeds with empty pillar summaries
- OutcomesSynthesisAgent failure → Logged error, may return partial result
- Visual generation failure → Non-blocking (logged as warning)

### Error Response Format
```json
{
  "error": "Error message",
  "error_code": "ERROR_CODE",
  "execution_id": "exec_abc123",
  "intent_type": "synthesize_outcome"
}
```

---

## 9. Testing & Validation

### Happy Path
1. User completes work in Content, Insights, Journey pillars
2. User navigates to Business Outcomes
3. User clicks "Generate Artifacts"
4. Synthesis completes with all pillar summaries
5. Visualization displayed

### Boundary Violations
- No session → Session validation error
- Empty pillar summaries → Synthesis proceeds with empty data

### Failure Scenarios
- LLM timeout → Agent failure, error returned
- Visual generation failure → Non-blocking, synthesis succeeds without visual

---

## 10. Contract Compliance

### Required Artifacts
- `solution` - Required (synthesis result)

### Required Events
- `outcome_synthesized` - Required

### Lifecycle State
- Artifact created with `READY` state (no intermediate states)
- Session-scoped (not persisted to Artifact Plane)

### Cross-Reference Analysis

| Source | Expectation | Implementation | Notes |
|--------|-------------|----------------|-------|
| **Journey Contract** | Synthesize outcomes from all realms | ✅ Implemented | Reads pillar summaries from session state |
| **Solution Contract** | Generate summary visualization | ✅ Implemented | Via VisualGenerationService |
| **Frontend** | Return synthesis with renderings | ✅ Implemented | Structured artifact format |

---

**Last Updated:** January 27, 2026  
**Owner:** Solution Realm Solution Team  
**Status:** ✅ **IMPLEMENTED**
