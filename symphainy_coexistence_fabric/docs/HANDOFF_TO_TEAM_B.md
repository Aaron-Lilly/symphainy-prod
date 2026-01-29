# Handoff to Team B (Landing)

**Purpose:** What you receive and what you do. When this handoff is complete, Team B implements the intent contracts and uses the Experience SDK; Takeoff exposes the runtime contracts that plug into that.

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

---

## Your remit

**Implement the intent contracts and use the Experience SDK.**

- You build capabilities and experiences that **consume** the Experience SDK (query_state, invoke_intent, trigger_journey, subscribe).
- You implement intents against the **runtime contracts** (registration, execution, state, artifacts) in RUNTIME_CONTRACTS.md.
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
