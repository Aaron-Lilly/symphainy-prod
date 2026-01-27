# Intent Contract Enhancement Checklist

## 📋 Per-Intent Checklist

Use this checklist for each of the 8 remaining intent contracts.

## Remaining Intents

- [ ] `intent_process_liaison_agent_message.md`
- [ ] `intent_execute_pillar_action.md`
- [ ] `intent_share_context_to_agent.md`
- [ ] `intent_get_shared_context.md`
- [ ] `intent_merge_agent_contexts.md`
- [ ] `intent_list_available_mcp_tools.md`
- [ ] `intent_validate_mcp_tool_call.md`
- [ ] `intent_call_orchestrator_mcp_tool.md`

---

## Section-by-Section Checklist

### ✅ Section 1: Intent Overview

- [ ] **Purpose:** Already filled in ✓
- [ ] **Intent Flow:**
  - [ ] Flowchart format with `↓` arrows
  - [ ] Starts with trigger event
  - [ ] Shows all key steps
  - [ ] Ends with return artifact
- [ ] **Expected Observable Artifacts:**
  - [ ] List all artifacts (bullet points)
  - [ ] Include artifact descriptions
  - [ ] Note conditional artifacts (if applicable)

### ✅ Section 2: Intent Parameters

- [ ] **Required Parameters:** Already filled in ✓
- [ ] **Optional Parameters:** Already filled in ✓
- [ ] **Context Metadata:**
  - [ ] Table format with 4 columns
  - [ ] Includes `user_id`, `tenant_id` (required)
  - [ ] Includes relevant context from previous intents
  - [ ] All sources identified (Runtime, Previous intent result, etc.)

### ✅ Section 3: Intent Returns

- [ ] **Success Response:**
  - [ ] JSON format
  - [ ] Realistic field names and values
  - [ ] Includes `artifacts` object
  - [ ] Includes `events` array
  - [ ] `semantic_payload` has all relevant fields
  - [ ] `renderings` has human-readable message
- [ ] **Error Response:**
  - [ ] JSON format
  - [ ] Includes `error`, `error_code`, `execution_id`
  - [ ] Includes `intent_type`
  - [ ] Includes `details` object (if applicable)

### ✅ Section 4: Artifact Registration

- [ ] **State Surface Registration:**
  - [ ] Either "No artifacts registered" OR full artifact details
  - [ ] If artifacts created: Artifact ID, Type, Lifecycle State, Produced By, Semantic Descriptor, Parent Artifacts, Materializations
  - [ ] If no artifacts: Explanation (retrieval-only, stateless, etc.)
- [ ] **Artifact Index Registration:**
  - [ ] Either "No artifacts indexed" OR index details
  - [ ] If indexed: Table name and indexed fields listed

### ✅ Section 5: Idempotency

- [ ] **Idempotency Key:**
  - [ ] Formula OR "N/A - [reason]"
  - [ ] If formula: Uses `hash()` function
- [ ] **Scope:**
  - [ ] Describes scope (per tenant, per session, per artifact, etc.)
  - [ ] OR "N/A" if no side effects
- [ ] **Behavior:**
  - [ ] Describes idempotent behavior
  - [ ] Explains what happens on duplicate calls

### ✅ Section 6: Implementation Details

- [ ] **Handler Location:**
  - [ ] Path: `symphainy_platform/realms/coexistence/intent_services/{intent_name}_service.py`
  - [ ] Note: "(to be created)"
- [ ] **Key Implementation Steps:**
  - [ ] Numbered list (5-8 steps typically)
  - [ ] Each step is actionable
  - [ ] Steps are in logical order
  - [ ] Includes parameter extraction, validation, processing, return
- [ ] **Dependencies:**
  - [ ] **Public Works:** List abstractions needed
  - [ ] **State Surface:** List methods needed
  - [ ] **Runtime:** ExecutionContext (always)
  - [ ] **Other Intents:** List if calls other intents
  - [ ] **Curator:** If queries MCP tools

### ✅ Section 7: Frontend Integration

- [ ] **Frontend Usage:**
  - [ ] TypeScript code example
  - [ ] Uses `platformState.submitIntent()`
  - [ ] Shows parameter passing
  - [ ] Shows result handling
  - [ ] Code is complete and runnable
- [ ] **Expected Frontend Behavior:**
  - [ ] Numbered list (3-5 items)
  - [ ] Describes what frontend does
  - [ ] Describes UI updates
  - [ ] Describes user experience

### ✅ Section 8: Error Handling

- [ ] **Validation Errors:**
  - [ ] List of validation errors
  - [ ] Format: `**Error condition:** Description -> Returns ERROR_CODE`
  - [ ] Includes ValueError examples where applicable
- [ ] **Runtime Errors:**
  - [ ] List of runtime errors
  - [ ] Format: `**Error condition:** Description -> Returns ERROR_CODE`
  - [ ] Notes graceful degradation if applicable
- [ ] **Error Response Format:**
  - [ ] JSON example
  - [ ] Includes all required fields
  - [ ] Includes `details` object if applicable

### ✅ Section 9: Testing & Validation

- [ ] **Happy Path:**
  - [ ] Numbered list (5-8 steps)
  - [ ] Starts with initial condition
  - [ ] Shows trigger/action
  - [ ] Shows intent execution
  - [ ] Shows all key steps
  - [ ] Shows result and verification
- [ ] **Boundary Violations:**
  - [ ] List of boundary cases
  - [ ] Format: `**Violation type:** Description -> Expected behavior`
- [ ] **Failure Scenarios:**
  - [ ] List of failure cases
  - [ ] Format: `**Failure type:** Description -> Expected behavior`
  - [ ] Includes recovery/graceful degradation notes

### ✅ Section 10: Contract Compliance

- [ ] **Required Artifacts:**
  - [ ] Lists artifact type(s)
  - [ ] Notes conditions if applicable
- [ ] **Required Events:**
  - [ ] Lists event type(s)
  - [ ] Notes when emitted
- [ ] **Lifecycle State:**
  - [ ] Describes lifecycle state requirements
  - [ ] OR "No lifecycle state" if applicable
- [ ] **Contract Validation:**
  - [ ] Checklist format with ✅
  - [ ] 4-6 validation points
  - [ ] Covers key contract requirements

### ✅ Final Status Update

- [ ] **Status:** Changed to `✅ **ENHANCED** - Ready for implementation`
- [ ] **Last Updated:** Set to current date
- [ ] **Owner:** "Coexistence Solution Team"

---

## 🎯 Quick Validation

Before marking an intent as complete, verify:

- [ ] No placeholders remain (`[Describe...]`, `[List...]`, `[Step...]`)
- [ ] All JSON examples are valid JSON
- [ ] All error codes follow naming convention (UPPERCASE_WITH_UNDERSCORES)
- [ ] Handler location follows pattern
- [ ] Implementation steps are actionable
- [ ] Frontend code is complete TypeScript
- [ ] All sections are filled in
- [ ] Status is updated to ✅ **ENHANCED**

---

## 📝 Notes Per Intent

### `intent_process_liaison_agent_message.md`
- Similar to `process_guide_agent_message` but pillar-specific
- Uses pillar-specific knowledge and pillar MCP tools only
- Reference: `intent_process_guide_agent_message.md`

### `intent_execute_pillar_action.md`
- Calls pillar orchestrator MCP tool
- Validates tool is pillar-specific
- Returns tool execution results
- Reference: Journey contract for pillar action flow

### `intent_share_context_to_agent.md`
- Shares context from source agent to target agent
- Context includes conversation_history, shared_intent, pillar_context
- Stores in shared context store
- Reference: Journey contract for context sharing flow

### `intent_get_shared_context.md`
- Retrieval-only intent (no side effects)
- Gets shared context for target agent
- Returns context artifact
- Reference: `intent_get_chat_session.md` (similar pattern)

### `intent_merge_agent_contexts.md`
- Merges contexts from multiple agents
- Deduplicates and prioritizes
- Returns merged context
- Reference: Journey contract for context merging

### `intent_list_available_mcp_tools.md`
- Queries Curator for MCP tools
- Filters by agent type (GuideAgent: all, Liaison: pillar-specific)
- Returns tool metadata
- Reference: `intent_initiate_guide_agent.md` (MCP tool discovery section)

### `intent_validate_mcp_tool_call.md`
- Validates MCP tool call against governance
- Checks permissions, rate limits via Smart City Primitives
- Returns validation result
- Reference: Journey contract for validation flow

### `intent_call_orchestrator_mcp_tool.md`
- Executes orchestrator MCP tool
- Calls tool with parameters
- Returns execution results
- Reference: Journey contract for tool execution flow

---

## ✅ Completion

Once all 8 intents are complete:

1. [ ] All intents have status `✅ **ENHANCED** - Ready for implementation`
2. [ ] All checklists above are complete
3. [ ] Commit all changes
4. [ ] Update progress summary

**Total Progress: 16/16 intents complete!** 🎉
