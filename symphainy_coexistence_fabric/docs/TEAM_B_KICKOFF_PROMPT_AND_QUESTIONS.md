# Team B Kickoff: Prompt and Pre-Coding Questions

**Purpose:** Give your team a single prompt to get started cleanly, and five questions they must answer before coding so they understand the remit and build the right thing.

**What changed (CTO alignment):** If you were already locked in on the prior handoff, read [TEAM_B_UPDATED_GUIDANCE.md](TEAM_B_UPDATED_GUIDANCE.md) for **exactly what's new or evolving**: (1) PLATFORM_VISION_RECONCILIATION.md is now the **canonical reference**; (2) Experience SDK boundary is a **hard platform invariant** (no solution/agent/MCP/experience may directly access runtime, civic, or infrastructure); (3) **Architectural authority chain** when docs conflict (Vision → BOOT_PHASES → SDK Contract → Runtime Contracts; executable truth wins, reconcile back); (4) Lifecycle hooks exist as no-ops in MVP (Takeoff owns; you don't implement unless assigned). Your remit and task order are unchanged; the prompt below reflects these additions.

---

## Kickoff Prompt (copy-paste to your team)

**Use this version** (CTO-aligned). See [TEAM_B_UPDATED_GUIDANCE.md](TEAM_B_UPDATED_GUIDANCE.md) for what changed from the prior prompt.

```
You are Team B (Landing) on the Symphainy platform. Your job is to implement the intent contracts and build capabilities and experiences that use the Experience SDK. Takeoff has delivered the platform core, the Experience SDK, and the runtime contracts.

**Canonical reference:** docs/PLATFORM_VISION_RECONCILIATION.md is the canonical reference for vision ↔ implementation, boot, lifecycle, the Experience SDK boundary (hard invariant), and how to resolve doc conflicts. Use it when aligning with the platform vision or when docs conflict.

**Start here:**
1. Pull latest main. Open docs/HANDOFF_TO_TEAM_B.md — that's your entry point. It now includes deliverable #7: PLATFORM_VISION_RECONCILIATION.md. Read the reconciliation doc so you know the hard invariant and the authority chain.
2. Read docs/solution_realm_refactoring_vision.md and docs/LANDING_AGENT_TASKS.md. Task order: Task 0 (canonical architecture doc) → Task 1 (adopt Experience SDK contract) → Tasks 2–6. Additive structure only; no delete/rename of existing solutions/realms until an explicit migration.
3. Before writing any code, answer the five pre-coding questions in docs/TEAM_B_KICKOFF_PROMPT_AND_QUESTIONS.md. Your answers should reflect: (a) the handoff boundary and runtime contracts, (b) the **hard invariant** — no solution, agent, MCP server, or experience may directly access runtime internals, civic systems, or infrastructure; all access via Experience SDK or governed capability interfaces, (c) the **authority chain** when docs conflict: Platform Vision → INIT_ORDER_SPEC / BOOT_PHASES → Experience SDK Contract → Runtime Contracts; executable truth wins, reconcile back.
4. Execute in order: Task 0 → Task 1 → Tasks 2–6. For every intent: RUNTIME_CONTRACTS + RUNTIME_OBLIGATIONS_INDEX. For every experience surface: Experience SDK only (query_state, invoke_intent, trigger_journey, subscribe) — no direct Runtime, civic, or infrastructure access.

**Rules (unchanged):**
- You consume the Experience SDK; you do not change the Experience Civic System or the Runtime API contract.
- You implement to the contracts already documented; you do not redefine them.
- You add new structure; you do not remove or rename existing platform code without an explicit migration task.

**New (must follow):**
- **Hard invariant:** No solution, agent, MCP server, or experience may directly access runtime internals, civic systems, or infrastructure. All access must flow through the Experience SDK or governed capability interfaces (PLATFORM_VISION_RECONCILIATION.md §4).
- **When docs conflict:** Resolve using the authority chain (Platform Vision → BOOT_PHASES → Experience SDK Contract → Runtime Contracts). Executable truth wins; reconcile back into the vision (PLATFORM_VISION_RECONCILIATION.md §8).
```

---

## 5 Questions to Answer Before Coding

Have the team answer these in writing (e.g. in a doc or chat) before they start implementing. Use their answers to confirm understanding and alignment.

---

**1. What is the handoff boundary between Takeoff and your team, and what are you allowed to change vs. what you must not change?**

*What you want to hear:* The handoff boundary is the **Experience SDK** and the **runtime contracts** (IntentRegistry, ExecutionContext, state surface, artifact surface). We (Team B) implement intent contracts and build capabilities/experiences that **consume** the SDK and plug into the runtime contracts. We must **not** change the Experience Civic System, the Runtime API, or the boot/service_factory core that Takeoff owns. We only **add** (capabilities/, experience/, solutions packaging) and implement intents against the documented contracts. **Hard invariant:** No solution, agent, MCP server, or experience may directly access runtime internals, civic systems, or infrastructure; all access via Experience SDK or governed capability interfaces. **When docs conflict:** Platform Vision → BOOT_PHASES → Experience SDK Contract → Runtime Contracts; executable truth wins, reconcile back (PLATFORM_VISION_RECONCILIATION.md §8).

---

**2. What is the difference between a “capability” and an “experience” in this architecture, and where does the code for each live?**

*What you want to hear:* A **capability** is what the platform *can do* (e.g. content ingestion, journey engine, security, insights). Code lives under `capabilities/<name>` (e.g. capabilities/content, capabilities/journey_engine). An **experience** is how users *touch* the platform (e.g. Operations UI, Outcomes UI, content pillar). Code lives under `experience/<name>` (e.g. experience/operations, experience/content). Experiences are **clients** of the runtime via the Experience SDK; they do not bootstrap the runtime. Operations is the experience “lens” into the journey_engine capability; Outcomes is the lens into solution_synthesis.

---

**3. When you implement an intent, what four runtime obligations must you satisfy, and where are they documented?**

*What you want to hear:* The four obligations are **registration** (register with IntentRegistry: intent_type, handler_name), **execution** (accept ExecutionContext from the runtime; return result with artifacts/events; do not create execution records), **state** (read/write only via StateSurface; no direct DB/cache), and **artifacts** (register artifacts via ArtifactRegistry/State Surface; do not write directly to storage for platform authority). They are documented in `docs/architecture/RUNTIME_CONTRACTS.md` and summarized per journey in `docs/intent_contracts/RUNTIME_OBLIGATIONS_INDEX.md`.

---

**4. What is your first task (Task 0), and why is it “no code”—what are you producing?**

*What you want to hear:* Task 0 is the **canonical architecture doc** (e.g. CANONICAL_PLATFORM_ARCHITECTURE.md). It is “no code” because we are turning the vision into a single source of truth: the three-way separation (capabilities vs experience vs solutions), folder layout, boot phases Φ1–Φ4, and the rule that the service factory registers capabilities/intents/journey engine etc.—not experience surfaces. We are also adding a “current state vs target state” mapping and a platform layout decision. This ensures everyone (and every agent) knows where new code goes before we add capabilities/ or experience/ code.

---

**5. How do experience surfaces get session state, submit an intent, or follow execution progress—what do they call and what do they not call?**

*What you want to hear:* Experience surfaces call the **Experience SDK** only: **query_state** (session_id, tenant_id, optional execution_id) for session state and execution status, **invoke_intent** to submit an intent, **trigger_journey** to start a journey, **subscribe** (execution_id, tenant_id) for execution updates (polling or stream). They do **not** call the Runtime HTTP API directly, and they do not touch RuntimeClient, service_factory, civic system internals, or infrastructure. **Hard invariant:** No solution, agent, MCP server, or experience may directly access runtime internals, civic systems, or infrastructure; all access must flow through the Experience SDK or governed capability interfaces. The Experience service exposes the SDK; experience surfaces are clients of that contract.

---

## How to Use This

1. **Share the kickoff prompt** with the team (or paste it into the agent’s context) so they know where to start and what the rules are.
2. **Ask for the five answers** before any implementation. If an answer is wrong or vague, clarify using the “What you want to hear” guidance before they code.
3. **Keep PLATFORM_VISION_RECONCILIATION.md** as the canonical reference for vision alignment and conflict resolution; **HANDOFF_TO_TEAM_B.md** and **LANDING_AGENT_TASKS.md** as execution entry points. Point the team to TEAM_B_UPDATED_GUIDANCE.md when they ask what changed from the prior handoff.
