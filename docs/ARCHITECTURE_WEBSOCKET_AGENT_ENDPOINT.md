# WebSocket Agent Endpoint Architecture

**Date:** January 2026  
**Status:** ✅ **CANONICAL** - Architectural Decision  
**Applies to:** All platform code, WebSocket implementations, and agent routing

---

## 🎯 TL;DR (Strong Opinion, Lightly Held)

**Choose the Hybrid model:**

> **Experience Plane owns `/api/runtime/agent`**  
> **Runtime owns agent execution, state, and orchestration**

**The endpoint name is a contract, not a locator.**

---

## 📐 First Principles

Let's restate the planes in **operational—not conceptual—terms**:

### Experience Plane = **Intent + Context Boundary**

* **User-facing**
* Knows *who* is talking, *why*, and *in what mode*
* Decides **which agent** should respond
* Owns **conversation semantics**

### Runtime = **Execution Engine**

* **Stateless or minimally stateful**
* Does not know "users"
* Does not route based on UX intent
* Executes agents when told, returns results/events

> **If Runtime routes agents, it becomes UX-aware.**  
> **If Experience executes agents, it becomes orchestration-heavy.**  
> **Both are architectural traps.**

---

## 🔌 Endpoint Ownership: Resolve the Ambiguity Cleanly

### Frontend Expects

```
/api/runtime/agent
```

This *looks* Runtime-owned, but that's a **naming illusion**.

### Correct Interpretation

* `/api/runtime/agent` means **"invoke the runtime on my behalf"**
* Not **"talk directly to the runtime subsystem"**

### Recommendation

**Experience Plane owns the endpoint**, even if the path says `runtime`.

**Why this works:**

* ✅ You preserve frontend contracts
* ✅ You keep Runtime sealed
* ✅ You avoid leaking orchestration details to clients
* ✅ You retain the ability to change Runtime internals freely

**So the real wiring is:**

```
Client WebSocket
   ↓
Experience Plane (/api/runtime/agent)
   ↓
Runtime (internal API / queue / RPC)
```

---

## 🎯 Agent Routing: Guide vs Liaison

### Rule of Thumb

> **If the decision depends on user intent or UX mode → Experience Plane**  
> **If the decision depends on execution mechanics → Runtime**

### Therefore:

**Agent selection belongs in the Experience Plane.**

#### Why?

* Guide vs Liaison is a **semantic distinction**, not a technical one
* It depends on:

  * Which UI surface the message came from
  * Conversation state
  * User role / permissions
  * Possibly project or realm context

**Runtime should never ask:**

> "Is this a guide or a liaison?"

**It should be told:**

> "Run agent `guide.content` with this payload."

---

## 🏗️ Concrete Routing Model

### 1️⃣ WebSocket Message Arrives

```json
{
  "type": "agent.message",
  "payload": {
    "text": "Summarize this file",
    "context": {
      "surface": "content_pillar",
      "project_id": "123"
    }
  }
}
```

### 2️⃣ Experience Plane Responsibilities

The Experience Plane:

1. **Authenticates the socket**
2. **Resolves conversation context**
3. **Determines:**

   * Agent class: `guide` vs `liaison`
   * Specific agent: `content_guide`, `data_liaison`, etc.
4. **Constructs a runtime invocation request**

**Example:**

```json
{
  "agent_id": "guide.content",
  "invocation_id": "uuid",
  "input": {
    "text": "Summarize this file",
    "project_id": "123"
  },
  "return_channel": "ws://client/xyz"
}
```

---

### 3️⃣ Runtime Responsibilities

Runtime:

* ✅ Accepts invocation
* ✅ Loads agent
* ✅ Executes
* ✅ Emits events:

  * `agent.started`
  * `agent.token`
  * `agent.completed`
  * `agent.failed`

**It does NOT:**

* ❌ Know which UI sent the message
* ❌ Know what a "Guide" means
* ❌ Inspect auth or user identity

---

### 4️⃣ Message Return Path

Two valid patterns (pick one intentionally):

#### Option A — Runtime → Experience → Client (Recommended Early)

**Pros:**

* ✅ Centralized logging
* ✅ Easier policy enforcement
* ✅ Cleaner audit trail

**Cons:**

* ⚠️ Slight latency

#### Option B — Runtime → Client Directly

**Pros:**

* ✅ Lower latency
* ✅ Cleaner streaming

**Cons:**

* ❌ Harder security model
* ❌ Harder observability
* ❌ Runtime must know about sockets

💡 **For MVP and demos:** Option A is the right call.

---

## 🔄 How Agents Get Invoked from WebSocket Messages

Here's the clean mental model:

```
WebSocket ≠ Agent channel
WebSocket = Intent transport
```

**So:**

1. WebSocket message arrives
2. Experience Plane interprets it
3. Experience Plane *invokes agents asynchronously*
4. WebSocket is just how results flow back

**Think of agents as jobs, not chatbots.**

---

## 📝 Naming Conventions That Reduce Confusion

To avoid future bikeshedding:

### External (Client-Facing)

```
/api/runtime/agent
```

### Internal (Service-to-Service)

```
runtime.invokeAgent()
runtime.streamAgent()
```

### Agent Identity

```
guide.content
guide.operations
liaison.data
liaison.experience
```

**This makes logs and traces instantly readable.**

---

## ✅ Final Recommendation

* ✅ **Hybrid model**
* ✅ Experience Plane owns WebSocket + routing
* ✅ Runtime executes agents, emits events
* ❌ Runtime should never choose agents
* ❌ Frontend should never talk to Runtime directly

---

## 🚫 Anti-Patterns (Forbidden)

### ❌ Runtime Routing Agents

**Bad:**
```python
# Runtime decides which agent to use
if message.get("agent_type") == "guide":
    agent = get_guide_agent()
else:
    agent = get_liaison_agent(message.get("pillar"))
```

**Why:** Runtime becomes UX-aware, violating separation of concerns.

---

### ❌ Experience Plane Executing Agents Directly

**Bad:**
```python
# Experience Plane directly executes agent
result = await agent.execute(message)
```

**Why:** Experience Plane becomes orchestration-heavy, duplicating Runtime logic.

---

### ❌ Frontend Talking to Runtime Directly

**Bad:**
```typescript
// Frontend connects directly to Runtime
const ws = new WebSocket('ws://runtime:8000/api/runtime/agent');
```

**Why:** Bypasses Experience Plane, loses context, breaks security model.

---

## ✅ What Good Looks Like

### Good: Experience Plane Routing

```python
# Experience Plane determines agent
agent_type, agent_id = determine_agent_routing(
    surface=context.get("surface"),
    conversation_state=conversation_context,
    user_role=user_context.roles
)

# Experience Plane invokes Runtime
invocation = {
    "agent_id": agent_id,
    "input": message,
    "session_id": session_id
}
await runtime_client.invoke_agent(invocation)
```

### Good: Runtime Execution

```python
# Runtime receives invocation, executes agent
async def invoke_agent(invocation: Dict[str, Any]):
    agent = load_agent(invocation["agent_id"])
    result = await agent.execute(invocation["input"])
    emit_event("agent.completed", result)
```

---

## 📋 Checklist for Every WebSocket Implementation

Before implementing WebSocket endpoints, verify:

- [ ] Experience Plane owns user-facing WebSocket endpoints
- [ ] Experience Plane handles authentication
- [ ] Experience Plane determines agent routing
- [ ] Experience Plane constructs runtime invocations
- [ ] Runtime only executes agents (no routing logic)
- [ ] Runtime emits events (not direct WebSocket sends)
- [ ] Frontend never talks to Runtime directly
- [ ] Naming conventions follow platform standards

---

## 🎯 Remember

> **Experience Plane = Intent + Context Boundary**  
> **Runtime = Execution Engine**
>
> **The endpoint name is a contract, not a locator.**
>
> **Agent routing is a semantic decision → Experience Plane**  
> **Agent execution is a mechanical operation → Runtime**

---

**If you're unsure about routing or endpoint ownership, ask. Don't guess. Don't "just this once".**
