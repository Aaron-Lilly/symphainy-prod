## 1️⃣ The Key Reframe: Your Frontend Is a Platform Runtime, Not a UI

Most frontend architectures assume:

> “The backend is the platform; the frontend renders it.”

That assumption is **false for your system**.

In Symphainy (I’ll use the name generically), the frontend is:

* The **session authority consumer**
* The **agent runtime surface**
* The **journey state machine**
* The **policy boundary witness**
* The **human trust interface**

In other words:

> Your frontend is the **human-facing runtime for a governed agentic platform**.

Once you accept that, a lot of “why is this hard?” questions suddenly make sense.

Your frontend must:

* Survive session death
* Hydrate context incrementally
* Gate agent execution
* Coordinate websockets
* Handle partial truth (anonymous → authenticated)
* Present deterministic-but-explainable AI behavior

That is **not** a traditional CRUD SPA.

---

## 2️⃣ The Failure Modes You’re Already Running Into (and Will Again)

Let’s name the patterns you’ve already tripped over so we can design against them.

### A. Session/Auth Coupling

You hit this directly.

**Root cause**:
UI components assuming auth exists before session, or that session == auth.

**Prevention**:
Explicit frontend session lifecycle model.

---

### B. Hidden Global State

Early MVP frontends often accumulate:

* Implicit assumptions
* Cross-component state
* “Just grab it from context”

This works… until:

* Agents become long-lived
* Real-time enters the picture
* Recovery matters

---

### C. UI Triggering Backend Reality

Examples:

* Component mounts → API call
* Page load → websocket connect
* Button click → agent starts reasoning

These are *anti-patterns* in an agentic system.

**UI does not initiate authority actions.
State transitions do.**

---

### D. Page-Centric Thinking

Your app started as:

```
/upload
/parse
/analyze
```

But now it’s:

```
Journey → Realm → Capability → Artifact
```

Routing ≠ flow anymore.

---

### E. Agent Chat as “Just a Chat Widget”

This one will bite hard later if not addressed.

Your chat is:

* A controlled execution surface
* A policy-bound runtime
* A deterministic-ish reasoning interface

Not a toy.

---

## 3️⃣ The Frontend Architecture Guide You Want (Tailored to You)

Below is a **practical, non-academic guide structure** you can actually adopt and evolve.

You don’t need to implement all of this immediately — but having it written down will *prevent drift*.

---

# Frontend Architecture Guide (Symphainy Platform)

## 1. Frontend Architectural Principles (Non-Negotiables)

These are laws, not preferences.

### 1.1 Session-First, Auth-Second

* Sessions may exist without auth
* Auth upgrades a session
* UI must tolerate session invalidation at any time

> No component may assume `auth === true`

---

### 1.2 State Drives Actions, Not Components

* Components **react** to state
* They do not initiate authority changes
* Side effects live in boundary services, not JSX

---

### 1.3 Determinism Over Convenience

* Same journey + same context = same outcome
* UI randomness is a bug, not a feature
* Agent execution is always explainable

---

## 2. Frontend Layering Model

This is where most MVPs fall apart. Yours doesn’t have to.

### 2.1 Layer Overview

```
┌──────────────────────────────┐
│ UI Components (Dumb)         │
├──────────────────────────────┤
│ View Models / Hooks          │
├──────────────────────────────┤
│ Frontend State Providers     │
│  - SessionBoundaryProvider   │
│  - PlatformStateProvider     │
├──────────────────────────────┤
│ Client Services              │
│  - RuntimeClient             │
│  - AgentClient               │
│  - Realm Clients             │
├──────────────────────────────┤
│ Transport (HTTP / WS)        │
└──────────────────────────────┘
```

**Rule**:
UI components never talk directly to transport.

---

## 3. Session & Authentication Model (Canonical)

### 3.1 Session States

```ts
Anonymous
Initializing
Active
Invalid
Recovering
```

### 3.2 Frontend Responsibilities

* Observe session status
* React visually
* Never “fix” session itself
* Never retry auth errors silently

---

## 4. Agent Interaction Model (Frontend Side)

This is critical and often missing.

### 4.1 Agents Are Not UI Features

Agents are:

* Long-running processes
* Policy-bound
* Context-hydrated

### 4.2 UI → Agent Contract

UI provides:

* Intent
* User input
* Visibility

UI does NOT:

* Decide tools
* Retry failures
* Handle auth
* Store memory

---

### 4.3 Chat Is a Controlled Runtime Surface

Chat UI must:

* Reflect agent state (thinking, executing, blocked)
* Pause gracefully on session loss
* Resume only when session is active

---

## 5. WebSocket & Realtime Architecture

### 5.1 WebSocket Follows Session (Law)

* No session → no socket
* Invalid session → disconnect immediately
* No retries on auth errors

### 5.2 UI Expectations

* WS disconnect is *not an error*
* It’s a state transition
* UI must show narrative continuity

---

## 6. Routing & Navigation (Journey-Aware)

### 6.1 Routes Are Views, Not Workflows

Routing reflects:

* Current realm
* Current artifact
* Current journey step

Workflows live in:

* Platform state
* Orchestrators
* Agents

---

## 7. Artifact Display & Persistence

### 7.1 Artifacts Are Immutable Once Accepted

* UI treats artifacts as records
* Versioning is explicit
* Editing = new artifact

---

## 8. Error Handling Philosophy

### 8.1 Errors Are Signals, Not Exceptions

* Session errors → boundary issue
* Agent errors → reasoning surfaced
* Tool errors → capability unavailable

UI should *never mask meaning*.

---

## 9. Observability (Frontend Matters Too)

Frontend emits:

* Session transitions
* Agent start/stop
* Realm switches
* Artifact creation

This feeds:

* Admin dashboard
* Platform health
* Trust signals

---

## 10. “Red Flags” Checklist (Proactive Guardrails)

If you see any of these, stop and rethink:

* Component calling fetch directly
* Agent logic inside UI
* WebSocket created on page load
* Auth checked inside components
* “Just store it in local state”
* Retry loops in frontend

---

## Why This Will Save You Pain

This guide does three things simultaneously:

1. **Aligns frontend thinking with backend architecture**
2. **Prevents accidental reintroduction of old patterns**
3. **Makes future frontend engineers productive faster**

