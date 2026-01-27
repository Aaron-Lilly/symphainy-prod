# Intent Contract: generate_sop_from_chat

**Intent:** generate_sop_from_chat  
**Intent Type:** `generate_sop_from_chat`  
**Journey:** SOP Management (`journey_sop_management`)  
**Realm:** Journey Realm  
**Status:** ✅ **COMPREHENSIVE**  
**Priority:** 🔴 **PRIORITY 1** - Interactive SOP creation

---

## 1. Intent Overview

### Purpose
Start or complete interactive SOP generation via chat. When called without session_id, initiates a new chat session. When called with session_id, generates the final SOP from the chat session.

### Intent Flow
```
[New session: User starts SOP chat]
    ↓
[generate_sop_from_chat without session_id]
    ↓
[JourneyLiaisonAgent.initiate_sop_chat()]
    ↓
[Return chat session with initial response]

--- OR ---

[Existing session: User completes SOP]
    ↓
[generate_sop_from_chat with session_id]
    ↓
[JourneyLiaisonAgent.generate_sop_from_chat()]
    ↓
[Delegate to SOPGenerationAgent (specialist)]
    ↓
[Return generated SOP artifact]
```

### Expected Observable Artifacts
**New Session:**
- `chat_session` - Chat session object
- `status` - "chat_active"

**Completed Session:**
- `sop` - Generated SOP artifact
- `session_id` - Source chat session
- `sop_visual` - Visualization (if available)

---

## 2. Intent Parameters

### Optional Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `session_id` | `string` | Existing chat session ID | `null` (start new) |
| `initial_requirements` | `string` | Initial requirements (for new session) | `null` |

### Context Metadata (from ExecutionContext)

| Metadata Key | Type | Description | Source |
|--------------|------|-------------|--------|
| `tenant_id` | `string` | Tenant identifier | Runtime (required) |
| `session_id` | `string` | Session identifier | Runtime (required) |

---

## 3. Intent Returns

### Success Response (New Session)

```json
{
  "artifacts": {
    "chat_session": {
      "session_id": "chat_abc123",
      "agent_type": "journey_liaison",
      "status": "active",
      "capabilities": [
        "gather_requirements",
        "build_sop_structure",
        "refine_sop",
        "generate_sop"
      ],
      "initial_response": {
        "message": "I'll help you create an SOP. What process would you like to document?",
        "suggestions": [
          "Describe the process you want to document",
          "Tell me about the steps involved",
          "Share any specific requirements or checkpoints"
        ]
      },
      "sop_structure": {
        "title": null,
        "description": null,
        "steps": [],
        "checkpoints": [],
        "requirements": []
      }
    },
    "status": "chat_active"
  },
  "events": [
    {
      "type": "sop_chat_started",
      "session_id": "chat_abc123"
    }
  ]
}
```

### Success Response (Completed Session)

```json
{
  "artifacts": {
    "sop": {
      "sop_id": "sop_xyz789",
      "sop_data": {
        "id": "sop_xyz789",
        "title": "User-Defined SOP",
        "description": "SOP created via chat",
        "steps": [...],
        "checkpoints": [...],
        "prerequisites": [...],
        "expected_outcomes": [...]
      },
      "status": "generated",
      "source": "chat",
      "session_id": "chat_abc123",
      "agent_reasoning": "Generated SOP based on conversation..."
    },
    "session_id": "chat_abc123",
    "source": "chat",
    "sop_visual": {
      "image_base64": "...",
      "storage_path": "gs://bucket/sop_visual.png"
    }
  },
  "events": [
    {
      "type": "sop_generated_from_chat",
      "sop_id": "sop_xyz789",
      "session_id": "chat_abc123"
    }
  ]
}
```

---

## 4. Artifact Registration

### State Surface Updates
- Chat session state stored via `store_session_state()`
- SOP structure incrementally built during conversation
- Final SOP stored in execution state

---

## 5. Idempotency

### Idempotency Key
`chat_session_id` for existing sessions

### Behavior
- New session: Each call creates new session
- Existing session: Final generation is idempotent for same requirements
- Safe to retry

---

## 6. Implementation Details

### Handler Location
`symphainy_platform/realms/journey/orchestrators/journey_orchestrator.py::JourneyOrchestrator._handle_generate_sop_from_chat`

### Key Implementation Steps

**New Session:**
1. Check if `session_id` is missing
2. Call `JourneyLiaisonAgent.initiate_sop_chat()`
3. Process `initial_requirements` if provided
4. Return chat session artifact

**Generate SOP:**
1. Validate `session_id` exists
2. Call `JourneyLiaisonAgent.generate_sop_from_chat()`
3. Agent delegates to `SOPGenerationAgent` (specialist)
4. Optionally generate SOP visualization
5. Return SOP artifact

### Agents
- **JourneyLiaisonAgent:** `symphainy_platform/realms/journey/agents/journey_liaison_agent.py`
  - `initiate_sop_chat()` - Start new chat session
  - `generate_sop_from_chat()` - Generate final SOP
- **SOPGenerationAgent:** `symphainy_platform/realms/journey/agents/sop_generation_agent.py`
  - Specialist agent for SOP generation (delegated from Liaison)

---

## 7. Frontend Integration

### Frontend Usage (JourneyAPIManager.ts)
```typescript
// Start new chat session
const session = await journeyManager.generateSOP(
  null,
  { chat_mode: true }
);

// After chat conversation, generate final SOP
const result = await platformState.submitIntent(
  "generate_sop_from_chat",
  { session_id: session.session_id }
);
```

### Expected Frontend Behavior
1. User initiates SOP creation via chat
2. Frontend submits intent without `session_id`
3. Display chat interface with initial response
4. User converses via `sop_chat_message` intent
5. User requests final SOP generation
6. Frontend submits intent with `session_id`
7. Display generated SOP

---

## 8. Error Handling

### Validation Errors
- Session not found → `ValueError("Session not found")`
- SOP title missing → `ValueError("SOP title is required")`
- No steps → `ValueError("At least one step is required")`

### Runtime Errors
- Agent unavailable → `ValueError("SOPGenerationAgent not available")`
- Visualization fails → Continue without visual

---

## 9. Testing & Validation

### Happy Path (New Session)
1. Call without `session_id`
2. JourneyLiaisonAgent creates session
3. Return chat session with initial response

### Happy Path (Generate SOP)
1. Chat session has title and steps
2. Call with `session_id`
3. SOPGenerationAgent generates SOP
4. Return SOP artifact

---

## 10. Contract Compliance

### Required Artifacts
- `chat_session` (new) or `sop` (completed)

### Required Events
- `sop_chat_started` (new) or `sop_generated_from_chat` (completed)

---

## 11. Cross-Reference Analysis

### Journey Contract Says
- `initiate_sop_wizard` - Start SOP wizard
- `save_sop_from_chat` - Save SOP from chat

### Implementation Does
- ✅ `generate_sop_from_chat` handles both start and complete
- ✅ Uses JourneyLiaisonAgent for chat
- ✅ Delegates to SOPGenerationAgent for final generation

### Frontend Expects
- ✅ Chat-based SOP creation
- ✅ Session management

### Gaps/Discrepancies
- **NAMING:** Contract says `initiate_sop_wizard`, implementation uses `generate_sop_from_chat`
- **Recommendation:** Use `generate_sop_from_chat` (unified intent)

---

**Last Updated:** January 27, 2026  
**Owner:** Journey Realm Solution Team  
**Status:** ✅ **COMPREHENSIVE**
