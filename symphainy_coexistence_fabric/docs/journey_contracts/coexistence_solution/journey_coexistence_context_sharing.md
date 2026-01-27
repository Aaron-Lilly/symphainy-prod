# Journey Contract: Agent Context Sharing

**Journey:** Agent Context Sharing  
**Journey ID:** `journey_coexistence_context_sharing`  
**Solution:** Coexistence Solution  
**Status:** ⏳ **IN PROGRESS**  
**Priority:** 🔴 **PRIORITY 1** - Foundation journey for Coexistence Solution

---

## 1. Journey Overview

### Intents in Journey
1. `share_context_to_agent` - Step 1: Share conversation context when switching agents
2. `get_shared_context` - Step 2: Retrieve shared context for agent
3. `merge_agent_contexts` - Step 3: Merge contexts from multiple agents

### Journey Flow
```
[User toggles from GuideAgent to Liaison Agent OR vice versa]
    ↓
[share_context_to_agent] → context_shared_artifact
    - Source agent context extracted (conversation history, intent, state)
    - Context formatted for target agent
    - Context stored in shared context store
    - Context linked to chat session
    ↓
[get_shared_context] → shared_context_artifact
    - Target agent retrieves shared context
    - Context loaded into agent's conversation state
    - Agent can use context in responses
    ↓
[Optionally: merge_agent_contexts] → merged_context_artifact
    - Multiple agent contexts merged (if user toggled multiple times)
    - Context deduplicated and prioritized
    - Merged context available to active agent
    ↓
[Journey Complete]
```

### Expected Observable Artifacts
- **Step 1 (share_context_to_agent):**
  - `context_shared_artifact` - Context sharing artifact
  - `source_agent` - Source agent identifier (guide or liaison_{pillar})
  - `target_agent` - Target agent identifier
  - `shared_context` - Context data shared
  - `context_timestamp` - When context was shared

- **Step 2 (get_shared_context):**
  - `shared_context_artifact` - Retrieved context artifact
  - `context_data` - Context data for agent
  - `context_metadata` - Context metadata (source, timestamp, etc.)

- **Step 3 (merge_agent_contexts):**
  - `merged_context_artifact` - Merged context artifact
  - `merged_context` - Merged context data
  - `context_sources` - List of source agents for merged context

### Artifact Lifecycle State Transitions
- **Step 1:** Context shared artifact created with `lifecycle_state: "ACTIVE"`
- **Step 3:** Merged context artifact created with `lifecycle_state: "ACTIVE"`

### Idempotency Scope (Per Intent)

| Intent | Idempotency Key | Scope |
|--------|-----------------|-------|
| `share_context_to_agent` | `hash(chat_session_id + source_agent + target_agent + context_hash)` | Per session, per agent pair, per context state |
| `get_shared_context` | N/A (no side effects, retrieval only) | N/A |
| `merge_agent_contexts` | `hash(chat_session_id + context_sources_hash)` | Per session, per context source combination |

### Journey Completion Definition

**Journey is considered complete when:**

* Context is successfully shared from source agent to target agent **OR**
* Shared context is retrieved by target agent **OR**
* Multiple agent contexts are merged successfully

**Journey completion = target agent has access to shared context for seamless conversation continuity.**

---

**Last Updated:** January 27, 2026  
**Owner:** Coexistence Solution Team  
**Status:** ⏳ **IN PROGRESS**
