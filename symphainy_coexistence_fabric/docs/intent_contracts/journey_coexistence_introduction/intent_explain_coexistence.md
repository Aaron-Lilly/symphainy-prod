# Intent Contract: explain_coexistence

**Intent:** explain_coexistence  
**Intent Type:** `explain_coexistence`  
**Journey:** Platform Introduction (`journey_coexistence_introduction`)  
**Solution:** Coexistence Solution  
**Status:** ENHANCED  
**Priority:** PRIORITY 1

---

## 1. Intent Overview

### Purpose
Explains the core concept of "Coexistence" - how the Symphainy platform enables legacy systems, modern tools, and human teams to work together without requiring full replacement. This intent provides educational content about boundary-crossing work, coordination, and governance.

### Intent Flow
```
[User requests coexistence explanation]
    ↓
[Determine explanation depth based on context]
    ↓
[Generate tailored explanation with examples]
    ↓
[Create explanation artifact with diagrams/concepts]
    ↓
[Return educational content with CTAs]
```

### Expected Observable Artifacts
- `coexistence_explanation` - Educational content about coexistence concepts

---

## 2. Intent Parameters

### Required Parameters

| Parameter | Type | Description | Validation |
|-----------|------|-------------|------------|
| `user_context` | `object` | User context information | Must include session_id |

### Optional Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `depth` | `string` | Explanation depth: "overview", "detailed", "technical" | "overview" |
| `focus_area` | `string` | Specific area: "boundary_crossing", "coordination", "governance" | null |
| `include_examples` | `boolean` | Include real-world examples | true |
| `user_industry` | `string` | User's industry for relevant examples | null |

### Context Metadata (from ExecutionContext)

| Metadata Key | Type | Description | Source |
|--------------|------|-------------|--------|
| `tenant_id` | `string` | Tenant identifier | Runtime |
| `session_id` | `string` | Session identifier | Runtime |

---

## 3. Intent Returns

### Success Response

```json
{
  "artifacts": {
    "explanation": {
      "result_type": "coexistence_explanation",
      "semantic_payload": {
        "depth": "overview",
        "focus_area": null,
        "includes_examples": true
      },
      "renderings": {
        "headline": "What is Coexistence?",
        "tagline": "Systems working together, not replacing each other",
        "core_definition": "The Coexistence Fabric is Symphainy's approach to coordinating work that spans multiple systems, tools, and people. Instead of replacing existing systems, the platform enables them to coexist and work together seamlessly.",
        "key_concepts": [
          {
            "concept": "Boundary-Crossing",
            "icon": "link",
            "description": "Workflows that span legacy systems, modern tools, and human teams require coordination across boundaries.",
            "example": "An invoice approval that starts in SAP, routes through Slack, and completes in a modern approval app."
          },
          {
            "concept": "Coordination",
            "icon": "git-branch",
            "description": "The platform orchestrates work across systems, translating between formats, validating operations, and ensuring consistency.",
            "example": "Automatically converting data formats when moving between legacy databases and cloud APIs."
          },
          {
            "concept": "Governance",
            "icon": "shield",
            "description": "Policy enforcement, data boundaries, and compliance are managed centrally while respecting system autonomy.",
            "example": "Ensuring PII data never leaves the EU region even when workflows span global systems."
          }
        ],
        "real_world_example": {
          "title": "SOP ↔ Workflow Coexistence",
          "description": "A Standard Operating Procedure (SOP) defines how work should be done. A workflow defines how work is done in practice. The platform analyzes how these coexist, identifying gaps, overlaps, and opportunities for alignment.",
          "visual_type": "diagram"
        },
        "benefits": [
          "Preserve investments in existing systems",
          "Gradual modernization without disruption",
          "Unified governance across heterogeneous systems",
          "AI-powered optimization of cross-boundary workflows"
        ],
        "call_to_action": {
          "primary": "Analyze Coexistence in Your Organization",
          "primary_action": "navigate_to_solution",
          "primary_params": { "solution_id": "journey_solution" },
          "secondary": "Start with Content Upload",
          "secondary_action": "navigate_to_solution",
          "secondary_params": { "solution_id": "content_solution" }
        }
      }
    }
  },
  "events": [
    {
      "type": "coexistence_explained",
      "depth": "overview",
      "focus_area": null
    }
  ]
}
```

---

## 4. Artifact Registration

### State Surface Registration
- **Artifact ID:** `coex_explain_{session_id}_{depth}`
- **Artifact Type:** `"coexistence_explanation"`
- **Lifecycle State:** `"READY"`
- **Produced By:** `{ intent: "explain_coexistence", execution_id: "<execution_id>" }`
- **Materializations:** In-memory (static content)

---

## 5. Idempotency

### Idempotency Key
```
idempotency_key = hash(session_id + depth + focus_area + "explain_coexistence")
```

### Scope
- Per session + depth + focus_area

### Behavior
- Cacheable content (same parameters return same explanation)

---

## 6. Implementation Details

### Handler Location
`symphainy_platform/solutions/coexistence/journeys/introduction_journey.py`

### Key Implementation Steps
1. Determine explanation depth from parameters
2. Load appropriate content template
3. Customize examples based on user_industry if provided
4. Generate call-to-action based on user journey stage
5. Return structured educational content

### Dependencies
- **Public Works:** content templates (static)
- **State Surface:** None (static content)
- **Runtime:** ExecutionContext

---

## 7. Frontend Integration

### Frontend Usage
```typescript
// From CoexistenceExplanation.tsx
const explanation = await platformState.submitIntent({
  intent_type: "explain_coexistence",
  parameters: {
    user_context: { session_id },
    depth: "overview",
    include_examples: true
  }
});

const content = explanation.artifacts?.explanation?.renderings;
// Display key concepts as cards
// Show real-world example with diagram
// Enable CTA buttons
```

### Expected Frontend Behavior
1. Display headline and core definition
2. Render key concepts as info cards with icons
3. Show interactive diagram for real-world example
4. Present CTA buttons for next actions

---

## 8. Error Handling

### Validation Errors
- Invalid depth → Default to "overview"
- Unknown focus_area → Show all concepts

### Runtime Errors
- Content template missing → Return default explanation

---

## 9. Testing & Validation

### Happy Path
1. Request coexistence explanation
2. Verify all key concepts present
3. Verify examples are included
4. Verify CTAs are actionable

### Boundary Violations
- Invalid depth value → Use default "overview"

---

## 10. Contract Compliance

### Required Artifacts
- `explanation` - Required (coexistence_explanation type)

### Required Events
- `coexistence_explained` - Required

### Lifecycle State
- Always READY (static educational content)

---

**Last Updated:** January 27, 2026  
**Owner:** Coexistence Solution Team  
**Status:** ENHANCED
