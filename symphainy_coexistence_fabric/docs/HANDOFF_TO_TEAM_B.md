# Handoff to Team B (Landing)

**Purpose:** What you receive and what you do. When this handoff is complete, Team B implements the intent contracts and uses the Experience SDK; Takeoff exposes the runtime contracts that plug into that.

**Provisional handoff:** This handoff is **provisional**. We are still completing Public Works discovery (Phases C–F: protocols, 4-layer flow, service mapping, Curator boundary). The **target shape** is: you get access via **four services** on `ctx` (Governance, Reasoning, Experience, Platform), each exposing **protocol-typed** capabilities — not raw abstractions. The doc [PLATFORM_SDK_ABSTRACTS_FOR_B_TEAM.md](PLATFORM_SDK_ABSTRACTS_FOR_B_TEAM.md) describes that target and maps Platform capabilities to **protocols** so you can build with reasonable certainty. We will finalize the handoff after Phases C–F; until then, build against the protocols and service shape described there.

**Canonical reference:** [PLATFORM_VISION_RECONCILIATION.md](PLATFORM_VISION_RECONCILIATION.md) is the canonical reference for vision ↔ implementation, boot, lifecycle, the Experience SDK boundary (hard invariant), and the architectural authority chain. Use it when aligning with the platform vision or resolving doc conflicts.

---

## What you're getting

| # | Deliverable | Location |
|---|-------------|----------|
| 1 | Experience SDK contract | [docs/architecture/EXPERIENCE_SDK_CONTRACT.md](architecture/EXPERIENCE_SDK_CONTRACT.md) |
| 2 | Runtime contracts | [docs/architecture/RUNTIME_CONTRACTS.md](architecture/RUNTIME_CONTRACTS.md) |
| 3 | Reviewed intent contracts | [docs/intent_contracts/](intent_contracts/) |
| 4 | Vision alignment summary | [docs/intent_contracts/VISION_ALIGNMENT_SUMMARY.md](intent_contracts/VISION_ALIGNMENT_SUMMARY.md) |
| 5 | Runtime obligations (per journey) | [docs/intent_contracts/RUNTIME_OBLIGATIONS_INDEX.md](intent_contracts/RUNTIME_OBLIGATIONS_INDEX.md) |
| 6 | Boot phases (Phi3 / Phi4) | [docs/architecture/BOOT_PHASES.md](architecture/BOOT_PHASES.md), [docs/architecture/INIT_ORDER_SPEC.md](architecture/INIT_ORDER_SPEC.md) |
| 7 | Vision reconciliation (canonical) | [docs/PLATFORM_VISION_RECONCILIATION.md](PLATFORM_VISION_RECONCILIATION.md) |
| 8 | Meet in the middle (Takeoff plan) | [docs/MEET_IN_THE_MIDDLE_PLAN.md](MEET_IN_THE_MIDDLE_PLAN.md) |
| 9 | Platform SDK — abstractions exposed to B-team | [docs/PLATFORM_SDK_ABSTRACTS_FOR_B_TEAM.md](PLATFORM_SDK_ABSTRACTS_FOR_B_TEAM.md) |

---

## Your remit

**Implement the intent contracts and use the Experience SDK.**

- You build capabilities and experiences that **consume** the Experience SDK (query_state, invoke_intent, trigger_journey, subscribe).
- You implement intents against the **runtime contracts** (registration, execution, state, artifacts) in RUNTIME_CONTRACTS.md.
- **Hard invariant:** No solution, agent, MCP server, or experience may directly access runtime internals, civic systems, or infrastructure. All access must flow through the Experience SDK or governed capability interfaces (see [PLATFORM_VISION_RECONCILIATION.md](PLATFORM_VISION_RECONCILIATION.md) §4).
- You do **not** change the civic system or the Runtime contract; you only add capabilities/, experience/, and solutions packaging per [LANDING_AGENT_TASKS.md](LANDING_AGENT_TASKS.md).

---

## Our remit

**We expose the runtime contracts that plug into that.**

- Takeoff owns runtime, boot, and the Experience Civic System.
- We ensure the runtime contracts (IntentRegistry, ExecutionContext, state surface, artifact surface) are stable and documented.
- We maintain the Experience SDK implementation and the Experience service that exposes it.

---

## Where to start

1. **Canonical architecture:** [LANDING_AGENT_TASKS.md](LANDING_AGENT_TASKS.md) Task 0 — read [solution_realm_refactoring_vision.md](solution_realm_refactoring_vision.md) and the canonical layout.
2. **Experience SDK:** Task 1 — adopt the contract in EXPERIENCE_SDK_CONTRACT.md; add protocol/ABC in code if not already present; build experience surfaces that call the SDK.
3. **Intent implementation:** Use RUNTIME_CONTRACTS.md and RUNTIME_OBLIGATIONS_INDEX.md for each intent: register with IntentRegistry, accept ExecutionContext, use StateSurface and ArtifactRegistry only.
4. **Capabilities and experiences:** Tasks 2–6 — create capabilities/ and experience/ namespaces, map intents to capabilities/experiences per VISION_ALIGNMENT_SUMMARY.md, implement intents and wire experience surfaces to the SDK.

---

## Summary

- **You:** Implement intent contracts; use the Experience SDK; build capabilities and experiences.
- **We:** Expose and maintain the runtime contracts and the Experience SDK.
- **Meet in the middle:** Experience SDK and runtime contracts are the handoff boundary.
- **When docs conflict:** Platform Vision → INIT_ORDER_SPEC / BOOT_PHASES → Experience SDK Contract → Runtime Contracts. Executable truth wins; reconcile back into the vision (see PLATFORM_VISION_RECONCILIATION.md §8).
