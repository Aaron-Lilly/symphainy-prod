# Journey Contract: Chat Session Management

**Journey:** Chat Session Management  
**Journey ID:** `journey_coexistence_chat_session`  
**Solution:** Coexistence Solution  
**Status:** ⏳ **IN PROGRESS**  
**Priority:** 🔴 **PRIORITY 1** - Foundation journey for Coexistence Solution

---

## 1. Journey Overview

### Intents in Journey
1. `initialize_chat_session` - Step 1: Create chat session with initial context
2. `get_chat_session` - Step 2: Retrieve active chat session (if exists)
3. `update_chat_context` - Step 3: Update shared conversation context

### Journey Flow
```
[User opens chat interface]
    ↓
[initialize_chat_session] → chat_session_artifact (session_id, active_agent: "guide", context: {})
    - Chat session created
    - Default agent: GuideAgent
    - Initial context: empty
    - Session registered in State Surface
    - Session stored in Supabase (chat_sessions table)
    ↓
[User toggles agent or sends message]
    ↓
[get_chat_session] → chat_session_artifact (if session exists)
    - Retrieve session by session_id
    - Return active agent and context
    ↓
[update_chat_context] → chat_session_artifact updated
    - Context updated with new conversation data
    - Context shared across agents
    - Session artifact updated
    ↓
[Journey Complete]
```

### Expected Observable Artifacts
- **Step 1 (initialize_chat_session):**
  - `chat_session_id` - Session identifier (UUID)
  - `active_agent` - Current active agent ("guide" or "liaison_{pillar}")
  - `context` - Shared conversation context (object)
  - `created_at` - Session creation timestamp
  - Artifact registered in State Surface
  - Session stored in Supabase (chat_sessions table)

- **Step 2 (get_chat_session):**
  - `chat_session_artifact` - Existing session (if found)
  - No new artifacts created (retrieval only)

- **Step 3 (update_chat_context):**
  - `chat_session_artifact` - Updated session with new context
  - Context merged with existing context
  - Artifact updated in State Surface
  - Session updated in Supabase

### Artifact Lifecycle State Transitions
- **Step 1:** Chat session artifact created with `lifecycle_state: "ACTIVE"`
- **Step 3:** Chat session artifact updated (context changes, lifecycle state remains ACTIVE)

### Idempotency Scope (Per Intent)

| Intent | Idempotency Key | Scope |
|--------|-----------------|-------|
| `initialize_chat_session` | `hash(user_id + tenant_id + timestamp_window)` | Per user, per tenant, per time window (1 minute) |
| `get_chat_session` | N/A (no side effects, retrieval only) | N/A |
| `update_chat_context` | `hash(chat_session_id + context_hash)` | Per session, per context state |

**Note:** Idempotency keys prevent duplicate session creation. Same user + tenant + time window = same session artifact.

### Journey Completion Definition

**Journey is considered complete when:**

* Chat session is initialized and active (`initialize_chat_session` succeeds) **OR**
* Existing chat session is retrieved (`get_chat_session` succeeds) **OR**
* Chat context is updated (`update_chat_context` succeeds)

**Journey completion = user can interact with agents via chat interface.**

---

**Last Updated:** January 27, 2026  
**Owner:** Coexistence Solution Team  
**Status:** ⏳ **IN PROGRESS**
