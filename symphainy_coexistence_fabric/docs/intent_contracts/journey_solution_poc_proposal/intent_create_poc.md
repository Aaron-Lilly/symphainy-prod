# Intent Contract: create_poc

**Intent:** create_poc  
**Intent Type:** `create_poc`  
**Journey:** POC Proposal Creation (`journey_solution_poc_proposal`)  
**Realm:** Solution Realm (Implementation: Outcomes Realm)  
**Status:** ✅ **IMPLEMENTED**  
**Priority:** 🔴 **PRIORITY 1**

---

## 1. Intent Overview

### Purpose
Create a Proof of Concept (POC) proposal from a user-provided description. The POC proposal includes objectives, scope, deliverables, timeline, and optional visualization. The generated POC is stored in the Artifact Plane for retrieval and can be used as a source for platform solution creation.

### Intent Flow
```
[Frontend: OutcomesAPIManager.createPOC(description)]
    ↓
[submitIntent("create_poc", { description, poc_options })]
    ↓
[Runtime: ExecutionLifecycleManager.execute()]
    ↓
[OutcomesOrchestrator._handle_create_poc()]
    ↓
[Validate description (non-empty)]
    ↓
[POCGenerationAgent.process_request() OR POCGenerationService.generate_poc_proposal()]
    ↓
[Generate poc_id/proposal_id (UUID)]
    ↓
[VisualGenerationService.generate_poc_visual() - optional]
    ↓
[Store artifact in Artifact Plane]
    ↓
[Return structured artifact with poc_id]
```

### Expected Observable Artifacts
- `poc` artifact stored in Artifact Plane with:
  - `poc_id` / `proposal_id`: Unique identifier
  - `description`: User-provided description
  - `status`: Generation status
  - `objectives`: Array of objectives
  - `scope`: Scope definition
  - `deliverables`: Array of deliverables
  - `estimated_duration_weeks`: Timeline estimate
  - `poc_visual`: Optional { image_base64, storage_path }

---

## 2. Intent Parameters

### Required Parameters

| Parameter | Type | Description | Validation |
|-----------|------|-------------|------------|
| `description` | `string` | POC description | Non-empty string |

### Optional Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `poc_options` | `object` | Options for POC generation | `{}` |

### Context Metadata (from ExecutionContext)

| Metadata Key | Type | Description | Source |
|--------------|------|-------------|--------|
| `session_id` | `string` | Session identifier | Runtime (required) |
| `tenant_id` | `string` | Tenant identifier | Runtime (required) |
| `execution_id` | `string` | Execution identifier | Runtime |

---

## 3. Intent Returns

### Success Response

```json
{
  "artifacts": {
    "proposal_id": "poc_abc123",
    "poc_id": "poc_abc123",
    "poc": {
      "result_type": "poc",
      "semantic_payload": {
        "proposal_id": "poc_abc123",
        "poc_id": "poc_abc123",
        "execution_id": "exec_xyz789",
        "session_id": "session_456"
      },
      "renderings": {}
    }
  },
  "events": [
    {
      "type": "poc_proposal_created",
      "proposal_id": "poc_abc123",
      "session_id": "session_456"
    }
  ]
}
```

### Full Artifact (in Artifact Plane)

```json
{
  "poc_proposal": {
    "poc_id": "poc_abc123",
    "proposal_id": "poc_abc123",
    "description": "Migrate legacy insurance system to cloud",
    "status": "completed",
    "objectives": [
      "Validate cloud migration feasibility",
      "Assess performance impact",
      "Identify integration challenges"
    ],
    "scope": "Core policy management module",
    "deliverables": [
      "Migration assessment report",
      "Proof of concept application",
      "Performance benchmarks"
    ],
    "estimated_duration_weeks": 8,
    "generated_at": "2026-01-27T10:00:00Z"
  },
  "proposal": {
    "executive_summary": "...",
    "technical_approach": "...",
    "risk_factors": ["..."]
  },
  "poc_visual": {
    "image_base64": "...",
    "storage_path": "gs://bucket/path/poc.png"
  }
}
```

### Error Response

```json
{
  "error": "Description is required for POC creation",
  "error_code": "VALIDATION_ERROR",
  "execution_id": "exec_abc123"
}
```

---

## 4. Artifact Registration

### Artifact Plane Registration
- **Artifact ID:** Generated UUID (`poc_{uuid}`)
- **Artifact Type:** `"poc"`
- **Lifecycle State:** `"READY"`
- **Produced By:** `{ intent: "create_poc", execution_id: "<execution_id>" }`
- **Metadata:** `{ regenerable: true, retention_policy: "session" }`
- **Payload:** Full POC data with proposal and visual

### Fallback (if Artifact Plane unavailable)
- Stored in execution state (logged as warning)
- Returns full artifact in response (not just reference)

---

## 5. Idempotency

### Idempotency Key
```
idempotency_key = hash(description + session_id)
```

### Scope
- Per description input per session
- Not idempotent - generates new POC each time

### Behavior
- Each invocation generates a new POC with new poc_id
- Previous POCs remain in Artifact Plane
- Useful for iterating on descriptions

---

## 6. Implementation Details

### Handler Location
`symphainy_platform/realms/outcomes/orchestrators/outcomes_orchestrator.py::_handle_create_poc`

### Key Implementation Steps
1. Validate description (non-empty)
2. Try POCGenerationAgent (if available)
3. Fallback to POCGenerationService if agent fails (with semantic contract compliance)
4. Generate poc_id/proposal_id (UUID)
5. Call VisualGenerationService.generate_poc_visual() (optional)
6. Store artifact in Artifact Plane
7. Return artifact reference (not full artifact)

### Agent Fallback Pattern
When agent fails, fallback produces same semantic contract:
```python
poc_result = {
    "generation_mode": "agent_fallback",
    "confidence": "degraded",
    "semantic_payload": poc_result.get("semantic_payload", poc_result),
    "renderings": poc_result.get("renderings", {})
}
```

### Dependencies
- **Public Works:** None directly
- **Artifact Plane:** `create_artifact()` for storage
- **Runtime:** `ExecutionContext`
- **Agents:** `POCGenerationAgent` (primary)
- **Services:** `POCGenerationService` (fallback), `VisualGenerationService`

---

## 7. Frontend Integration

### Frontend Usage
```typescript
// OutcomesAPIManager.createPOC()
async createPOC(
  description: string,
  pocOptions?: Record<string, any>
): Promise<POCCreationResponse> {
  const platformState = this.getPlatformState();
  
  // Session validation
  validateSession(platformState, "create POC");

  // Parameter validation
  if (!description) {
    throw new Error("Description is required for POC creation");
  }

  // Submit intent
  const execution = await platformState.submitIntent(
    "create_poc",
    {
      description,
      poc_options: pocOptions || {}
    }
  );

  // Wait for execution
  const result = await this._waitForExecution(execution, platformState);

  if (result.status === "completed" && result.artifacts?.poc_proposal) {
    const pocId = result.artifacts.poc_proposal.poc_id;
    
    // Ensure lifecycle state
    const pocWithLifecycle = ensureArtifactLifecycle(
      result.artifacts.poc_proposal,
      'proof_of_concept',
      'validation',
      platformState.state.session.userId || 'system'
    );
    
    // Update realm state
    platformState.setRealmState("outcomes", "pocProposals", {
      ...platformState.getRealmState("outcomes", "pocProposals") || {},
      [pocId]: pocWithLifecycle
    });

    return { success: true, poc_proposal: result.artifacts.poc_proposal };
  }
  
  throw new Error(result.error || "Failed to create POC");
}
```

### Expected Frontend Behavior
1. Collect description from user input
2. Call `createPOC(description)` when user clicks "Create POC"
3. Show loading state during generation
4. Display POC with objectives, scope, deliverables
5. Store POC reference in realm state
6. Enable "Create Solution" flow with POC as source

---

## 8. Error Handling

### Validation Errors
- Empty description → `"Description is required for POC creation"`
- No session → `"Session required to create POC"`

### Runtime Errors
- Agent failure → Fallback to service (with degraded confidence)
- Service failure → Error returned
- Artifact Plane failure → Fallback to execution state (warning logged)
- Visual generation failure → Non-blocking (warning logged)

### Error Response Format
```json
{
  "error": "Error message",
  "error_code": "ERROR_CODE",
  "execution_id": "exec_abc123",
  "intent_type": "create_poc"
}
```

---

## 9. Testing & Validation

### Happy Path
1. User provides description
2. User clicks "Create POC"
3. POC generated with objectives, scope, deliverables
4. Artifact stored in Artifact Plane
5. poc_id returned and displayed

### Boundary Violations
- Empty description → Validation error
- No session → Session validation error

### Failure Scenarios
- Agent failure → Service fallback (success with degraded confidence)
- Service failure → Error returned
- Artifact Plane failure → Execution state fallback (warning)

---

## 10. Contract Compliance

### Required Artifacts
- `poc` reference - Required
- `poc_id` / `proposal_id` - Required

### Required Events
- `poc_proposal_created` - Required

### Lifecycle State
- Artifact created with `READY` state
- Stored in Artifact Plane (not execution state)
- Retrievable via `poc_id`

### Semantic Contract Compliance
- Agent and service fallback produce same semantic contract
- Fallback includes `generation_mode` and `confidence` fields
- Frontend can distinguish between agent and fallback results

### Cross-Reference Analysis

| Source | Expectation | Implementation | Notes |
|--------|-------------|----------------|-------|
| **Journey Contract** | Create POC from description | ✅ Implemented | Via agent/service |
| **Solution Contract** | Store in Artifact Plane | ✅ Implemented | With fallback |
| **Frontend** | Return poc_id for retrieval | ✅ Implemented | Reference pattern |

---

**Last Updated:** January 27, 2026  
**Owner:** Solution Realm Solution Team  
**Status:** ✅ **IMPLEMENTED**
