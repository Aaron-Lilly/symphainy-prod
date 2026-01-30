# Team B: Updated Guidance (CTO-Aligned)

**Purpose:** You were locked in on the prior handoff. This doc states **exactly what is new or evolving** so you can align without confusion. Your prior instructions remain in force unless explicitly overridden below.

**Canonical reference:** [PLATFORM_VISION_RECONCILIATION.md](PLATFORM_VISION_RECONCILIATION.md) is now the **canonical reference** for vision ↔ implementation, boot, lifecycle, the Experience SDK boundary, and doc conflict resolution. Use it when aligning with the platform vision or resolving conflicts.

---

## What’s changing / evolving (explicit)

### 1. New canonical doc: PLATFORM_VISION_RECONCILIATION.md

- **What it is:** A single doc that maps the high-level [updated_platform_vision.md](updated_platform_vision.md) to current implementation (BOOT_PHASES, INIT_ORDER_SPEC, Experience SDK, runtime contracts). It defines terminology, boot phase mapping (Φ1–Φ6 ↔ Φ1–Φ4), lifecycle (shutdown/recovery/integrity), and the authority chain when docs conflict.
- **What you do:** Treat it as **canonical**. When you’re unsure about vision vs implementation, boot phases, or layer names, **read PLATFORM_VISION_RECONCILIATION.md first**. HANDOFF_TO_TEAM_B.md and LANDING_AGENT_TASKS.md remain your execution entry points; the reconciliation doc is the source of truth for how they tie to the platform vision.

### 2. Experience SDK boundary is now a hard platform invariant

- **Prior:** “Experience surfaces and solutions consume only the Experience SDK; they do not call Runtime or civic internals directly.”
- **Now (unchanged in spirit, explicit and mandatory):**  
  **No solution, agent, MCP server, or experience may directly access runtime internals, civic systems, or infrastructure. All access must flow through the Experience SDK or governed capability interfaces.**

- **What you do:** Same as before—you already must not touch runtime/civic/infra. The change is that this is now a **hard platform invariant**. If you see code or a design that bypasses the SDK or governed interfaces, it is out of bounds. When in doubt, route all access through the Experience SDK (or another documented governed capability interface).

### 3. Architectural authority chain (when docs conflict)

- **New:** When docs disagree, resolve in this order:
  1. **Platform Vision** (updated_platform_vision.md)
  2. **INIT_ORDER_SPEC / BOOT_PHASES** (Φ1–Φ4)
  3. **Experience SDK Contract** (EXPERIENCE_SDK_CONTRACT.md)
  4. **Runtime Contracts** (RUNTIME_CONTRACTS.md)

- **Rule:** **Executable truth (what the code and boot spec do) always wins** in the short term. When executable truth diverges from the vision or a contract, it must be **reconciled back** (update the doc or change the code). Do not leave conflicts unresolved.

- **What you do:** If something you read in one doc contradicts another, use the order above. If your implementation would contradict a higher authority, align your implementation to the contract/vision, or flag the conflict so it can be reconciled (doc or code updated).

### 4. Lifecycle hooks (MVP: no-ops; you are not required to implement them)

- **New:** The platform defines five **lifecycle hooks**: `startup_begin`, `startup_complete`, `shutdown_begin`, `shutdown_complete`, `crash_detected`. In MVP they **must exist as no-ops** so Enterprise can add real behavior later without refactoring control flow.
- **What you do:** **Nothing new for you.** Takeoff owns boot and lifecycle. You do not implement these hooks unless explicitly assigned. You only need to know they exist so that (a) you don’t add competing hook points, and (b) if you ever touch boot/lifecycle code, you use these five hook names as no-ops in MVP.

### 5. High-level vision doc: updated_platform_vision.md

- **New:** A CTO-level north star (principles, platform scaffold, boot narrative Φ1–Φ6, shutdown/recovery, progressive capability flags). It does **not** replace HANDOFF_TO_TEAM_B or LANDING_AGENT_TASKS.
- **What you do:** Optional read for context. **Implementation and task order** still come from BOOT_PHASES (Φ1–Φ4), EXPERIENCE_SDK_CONTRACT, RUNTIME_CONTRACTS, HANDOFF_TO_TEAM_B, and LANDING_AGENT_TASKS. PLATFORM_VISION_RECONCILIATION maps the vision to those; use the reconciliation doc when you need to align with the vision.

---

## What is NOT changing

- **Your remit:** Implement intent contracts and build capabilities/experiences that **use** the Experience SDK. You do **not** change the Experience Civic System or the Runtime contract.
- **Task order:** Task 0 (canonical architecture doc) → Task 1 (adopt Experience SDK contract) → Tasks 2–6 per LANDING_AGENT_TASKS. Additive structure only; no delete/rename of existing solutions/realms until an explicit migration.
- **Entry points:** HANDOFF_TO_TEAM_B.md and LANDING_AGENT_TASKS.md remain where you start. They now point to PLATFORM_VISION_RECONCILIATION.md as the canonical reference and state the hard invariant and authority chain.
- **Runtime obligations:** Registration, execution, state, artifacts (RUNTIME_CONTRACTS, RUNTIME_OBLIGATIONS_INDEX) are unchanged.
- **Pre-coding questions:** The five questions in TEAM_B_KICKOFF_PROMPT_AND_QUESTIONS.md still apply; ideal answers now include “hard invariant” and “authority chain” where relevant (see updated prompt below).

---

## Updated kickoff prompt (use this version)

Copy-paste the following to the team or into the agent context. This **replaces** the prior kickoff prompt; it adds the canonical reference, hard invariant, and authority chain.

```
You are Team B (Landing) on the Symphainy platform. Your job is to implement the intent contracts and build capabilities and experiences that use the Experience SDK. Takeoff has delivered the platform core, the Experience SDK, and the runtime contracts.

**Canonical reference:** docs/PLATFORM_VISION_RECONCILIATION.md is the canonical reference for vision ↔ implementation, boot, lifecycle, the Experience SDK boundary (hard invariant), and how to resolve doc conflicts. Use it when aligning with the platform vision or when docs conflict.

**Start here:**
1. Pull latest main. Open docs/HANDOFF_TO_TEAM_B.md — that’s your entry point. It now includes deliverable #7: PLATFORM_VISION_RECONCILIATION.md. Read the reconciliation doc so you know the hard invariant and the authority chain.
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

## Summary

| Item | Status |
|------|--------|
| PLATFORM_VISION_RECONCILIATION.md | **New canonical reference** — read it; use it for vision alignment and conflict resolution. |
| Experience SDK boundary | **Hard platform invariant** — no direct access to runtime/civic/infra; all access via SDK or governed interfaces. |
| Authority chain | **New** — when docs conflict: Vision → BOOT_PHASES → SDK Contract → Runtime Contracts; executable truth wins, reconcile back. |
| Lifecycle hooks | **New** (MVP no-ops; Takeoff owns) — you are not required to implement; be aware they exist. |
| updated_platform_vision.md | **New** high-level vision — optional context; implementation still from HANDOFF + LANDING_AGENT_TASKS + reconciliation. |
| Your remit, task order, entry points, runtime obligations | **Unchanged** — keep doing what you were doing; add the invariant and authority chain to your mental model. |

Use this doc and the updated prompt so the team is 100% aligned on what evolved and what didn’t.
