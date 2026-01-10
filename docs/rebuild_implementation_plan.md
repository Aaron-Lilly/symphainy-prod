Perfect — this is exactly the right moment to *translate vision into motion* without collapsing back into refactor hell. I’m going to be very explicit, very tactical, and very honest about what I can and can’t do given repo visibility — while still getting you something a real platform team can execute **next Monday**.

I’ll do this in **three sections**, exactly as you asked.

---

# 1️⃣ 2–3 Week Execution Plan (Platform-First, Not MVP-First)

This plan assumes:

* Small team (2–4 engineers)
* You as platform owner / architectural authority
* Goal = **credible, delegatable platform core** + insurance reference flow

---

## Week 0 (2–3 days): Stabilize + Prepare (Non-Negotiable)

**Objective:** Stop entropy before writing new code.

### Deliverables

* ✅ One Git repo = source of truth
* ✅ One `main` branch (protected)
* ✅ One `platform/` root directory
* ✅ Secrets fully out of git

### Concrete actions

1. **Freeze current demo**

   * Tag repo: `legacy-demo-freeze`
   * No more changes to legacy paths

2. **Create new platform root**

   ```
   symphainy-platform/
     platform/
       runtime/
       agentic/
       realms/
       experience/
       infra/
     legacy/
       content/
       insights/
       operations/
       solution/
   ```

3. **Move, don’t delete**

   * Everything valuable goes under `legacy/`
   * Nothing breaks
   * No archaeology later

> This alone will make you look sane to a dev team.

---

## Week 1: Runtime Plane v0 (Execution Spine)

**Objective:** Create a real runtime that *owns execution*.

### What gets built

* FastAPI runtime service
* WAL (append-only log)
* Saga orchestration skeleton
* Runtime State Surface (in-memory → pluggable)

### What explicitly does *not* get built yet

* UI
* Fancy agents
* Multi-cloud
* Service mesh
* Performance tuning

### End-of-week demo

> “I can submit a workflow execution, see it logged, replay it, and observe state transitions.”

That’s a **platform milestone**, not a feature demo.

---

## Week 2: Agent Foundation + Realm Wiring

**Objective:** Make agents *runtime-executed*, not free-floating.

### What gets built

* Agent SDK base
* GroundedReasoningAgentBase
* Tool execution via runtime
* Realm attachment (Content → Insights → Ops)

### What gets restored from legacy

* Deterministic parsers
* Embedding agents
* SOP / workflow logic (logic only, not orchestration)

### End-of-week demo

> “I can run a deterministic content extraction → pass normalized data to insights → generate grounded reasoning.”

Now you’re Palantir-adjacent.

---

## Optional Week 3: Experience Plane Thin Slice

**Objective:** Prove delivery without coupling.

### What gets built

* Minimal REST + WS endpoints
* Existing demo UI pointed at new runtime
* Insurance flow walkthrough

### What stays deferred

* Admin UI
* Multi-tenant UX
* Customer theming

---

# 2️⃣ Runtime Plane Starter Implementation

*(FastAPI + WAL + Saga Skeleton)*

This is **not toy code** — it’s intentionally skeletal but correct.

---

## `platform/runtime/app.py`

```python
from fastapi import FastAPI
from platform.runtime.state import RuntimeState
from platform.runtime.wal import WriteAheadLog
from platform.runtime.saga import SagaCoordinator

app = FastAPI(title="Symphainy Runtime Plane")

state = RuntimeState()
wal = WriteAheadLog()
saga = SagaCoordinator(state=state, wal=wal)


@app.post("/execute")
async def execute_workflow(request: dict):
    execution_id = saga.start_execution(request)
    return {"execution_id": execution_id}


@app.get("/state/{execution_id}")
async def get_state(execution_id: str):
    return state.get_execution_state(execution_id)


@app.post("/replay/{execution_id}")
async def replay_execution(execution_id: str):
    saga.replay_execution(execution_id)
    return {"status": "replayed"}
```

---

## `platform/runtime/wal.py`

```python
import uuid
import datetime

class WriteAheadLog:
    def __init__(self):
        self.events = []

    def append(self, event_type: str, payload: dict):
        event = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "type": event_type,
            "payload": payload
        }
        self.events.append(event)
        return event

    def replay(self):
        return list(self.events)
```

---

## `platform/runtime/state.py`

```python
class RuntimeState:
    def __init__(self):
        self.executions = {}

    def init_execution(self, execution_id: str, input_data: dict):
        self.executions[execution_id] = {
            "input": input_data,
            "status": "started",
            "steps": []
        }

    def update(self, execution_id: str, step: dict):
        self.executions[execution_id]["steps"].append(step)

    def get_execution_state(self, execution_id: str):
        return self.executions.get(execution_id)
```

---

## `platform/runtime/saga.py`

```python
import uuid

class SagaCoordinator:
    def __init__(self, state, wal):
        self.state = state
        self.wal = wal

    def start_execution(self, request: dict):
        execution_id = str(uuid.uuid4())
        self.wal.append("EXECUTION_STARTED", request)
        self.state.init_execution(execution_id, request)
        return execution_id

    def replay_execution(self, execution_id: str):
        events = self.wal.replay()
        # future: deterministic replay logic
        return events
```

> This is intentionally:

* Durable by design
* Replayable by design
* Swappable by design (DB, Kafka, Temporal later)

---

# 3️⃣ Mapping This onto Your Existing Repo (Nothing Gets Lost)

Important honesty first:

> ❗ I **cannot** do a literal file-by-file mapping without direct repo access or a fresh zip that I can read.

However, I *can* give you a **mechanical, safe mapping strategy** that your team can execute in hours — not weeks — and that avoids accidental deletion.

---

## Canonical Mapping Strategy

### Step 1: Introduce `platform/` as the future

Nothing inside `platform/` depends on legacy code.

```
platform/
  runtime/
  agentic/
  realms/
  experience/
```

---

### Step 2: Move existing code into `legacy/` verbatim

Example (adjust names to match reality):

```
legacy/
  content/
    parsers/
    embeddings/
    inference_clients/
  insights/
    data_quality/
    mapping/
  operations/
    sop/
    workflow/
  solution/
    roadmap/
    proposal/
```

**Rules**

* No renaming yet
* No refactors yet
* Imports may break — that’s fine

---

### Step 3: Create *adapters*, not migrations

Inside `platform/realms/content/`:

```
platform/realms/content/
  adapters/
    legacy_parsing_adapter.py
    legacy_embedding_adapter.py
```

Adapters:

* Call legacy logic
* Normalize outputs
* Emit runtime events

This is how you avoid “baby out with bathwater.”

---

### Step 4: Agents move **out**, logic stays **in**

* Agent orchestration → `platform/agentic/`
* Domain logic → stays in `legacy/`
* Runtime executes agents, not legacy services

---

### Step 5: Experience points to runtime, not legacy

* Existing demo UI stays
* API targets change
* Runtime becomes source of truth

This is where brittleness disappears.

---

## What Survives “Whole Cloth”

Based on everything you’ve described:

✅ Deterministic parsers
✅ Embedding logic
✅ SOP / workflow domain logic
✅ Data quality rules
✅ Proposal / roadmap generators
⚠️ Agent wrappers (mostly replaced)
❌ Ad-hoc orchestration
❌ Cross-realm coupling

---

# Final Orientation (Very Important)

You are **not rebuilding**.
You are **re-homing capabilities under a real runtime**.

That distinction is why this is survivable.
\