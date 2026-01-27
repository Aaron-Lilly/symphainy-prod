# Experience Plane

**Status:** Rebuild in Progress  
**Phase:** Phase 3 (Platform SDK & Experience Plane)

---

## Purpose

Experience is a **separate service** that translates external interaction into intent.

---

## Responsibilities

Experience:
* exposes REST, WebSockets, chat, adapters
* authenticates callers
* establishes sessions via Runtime
* translates user actions into **intents**
* streams execution updates back

---

## Experience → Runtime Flow

1. Experience establishes session via Runtime (`POST /api/session/create`)
2. Experience submits intents via Runtime (`POST /api/intent/submit`)
3. Experience subscribes to execution events (WebSocket `/api/execution/stream`)
4. Experience never calls domain services directly
5. Experience never manages workflows
6. Experience never owns state

---

## What Experience Does

✅ Submit intents
✅ Stream execution updates
✅ Manage sessions (via Runtime)
✅ Authenticate users

---

## What Experience Doesn't Do

❌ Call domain services directly
❌ Manage workflows
❌ Own state
❌ Execute business logic

---

## References

- [Architecture Guide](../../docs/architecture/north_star.md) - Section 4.2 Experience
- [Phase 3 Execution Plan](../../docs/execution/phase_3_execution_plan.md)
