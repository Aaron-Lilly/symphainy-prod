# Public Works Probe Plan: Adapters, 4-Layer Pattern, Vision Alignment

**Purpose:** Define the **full scope** of the foundations probe (Meet in the Middle Step 2). This is **not** a one-pass report — it is a **multi-day review**: inventory every adapter and the **4-layer pattern** for exposing them (Adapter → Abstraction → Protocol → Service), then validate alignment with the current architectural vision. **Services were built for a prior architecture** — at minimum we must review how they should be updated to map to what the current platform vision actually needs.

**Expectation:** Messy. Several days. Material refactoring may emerge at every layer (e.g. removing startup logic from adapters, defining what actually needs to get registered and where in Curator, aligning to vision, **updating service exposure** to match current vision).

**References:** [MEET_IN_THE_MIDDLE_PLAN.md](MEET_IN_THE_MIDDLE_PLAN.md) Step 2, [updated_platform_vision.md](updated_platform_vision.md), [PLATFORM_VISION_RECONCILIATION.md](PLATFORM_VISION_RECONCILIATION.md), [PROBE_LAYER_MAP.md](testing/PROBE_LAYER_MAP.md), [STEP2_FOUNDATIONS_PROBE.md](testing/STEP2_FOUNDATIONS_PROBE.md) (first-pass boot snapshot).

---

## 1. What We Are Doing

1. **Review all adapters** — Every adapter in `foundations/public_works/adapters/`: purpose, config driver, wired at boot?, used on first request or later?, by whom? Align with vision: “Storage adapters (GCS, S3, FS), Compute adapters, Queue adapters, Network adapters” and “Uniform interfaces, hot-swappable backends, deterministic behavior.”
2. **Review the 4-layer pattern** — The team called it "5-layer"; in practice there are **4**: **Adapter** → **Abstraction** → **Protocol** → **Service** (foundation service). Document with evidence: how each layer works, what is bypassed, who calls what.
3. **Validate alignment with current architectural vision** — Map implementation to vision: “Public Works → Adapter → Abstraction → Platform Contract”; Foundations = “Public Works, Curator, State, Identity”; guarantees = uniform interfaces, hot-swappable backends, deterministic behavior. Gap map: what aligns, what doesn’t, what to refactor.

---

## 2. Vision (Current North Star)

From [updated_platform_vision.md](updated_platform_vision.md) and reconciliation:

- **Infrastructure Invariance:** “Public Works → Adapter → Abstraction → Platform Contract.” The platform must not care where/how infra is deployed; GCS, S3, local disk, K8s, cloud, airgapped — all appear as abstracted resources.
- **Public Works:** “Abstract all infrastructure into platform-native primitives.” Responsibilities: Storage adapters (GCS, S3, FS, etc.), Compute adapters, Queue adapters, Network adapters. Guarantees: Uniform interfaces, Hot-swappable backends, Deterministic behavior.
- **Foundations layer:** Public Works, Curator, State Surface + WAL, Identity.

So we must validate: Do we have a clear Adapter → Abstraction → (Protocol?) → Platform Contract flow? Do we have uniform interfaces and hot-swappable backends in practice? Is startup/connection logic in the right place (e.g. pre-boot vs adapter init)?

---

## 3. 4-Layer Pattern (Adapter → Abstraction → Protocol → Service)

The team called it "5-layer"; in practice there are **4** named layers. From code:

| Layer | Name | What it is in code | Evidence to gather |
|-------|------|--------------------|--------------------|
| **Layer 0** | Adapters | Raw technology clients in `adapters/` (Redis, Arango, GCS, Supabase, CSV, PDF, etc.) | List every adapter; config driver; wired at boot? used? callers. |
| **Layer 1** | Abstractions | Business-logic / infra abstractions in `abstractions/` (StateManagement, FileStorage, Registry, etc.) | List every abstraction; which adapters it uses; who gets it (foundation_service, runtime, realms). |
| **Layer 2** | Protocols | Interfaces in `protocols/` (state_protocol, file_storage_protocol, auth_protocol, etc.) | Which abstractions implement which protocols? Are protocols the actual contract, or are callers bound to concrete abstractions? |
| **Layer 3** | (TBD) | Not clearly named in code; may be “aggregation” or “foundation API” | Is there a distinct Layer 3, or does the foundation service (Layer 4) sit directly on 0+1+2? |
| **Layer 4** | Foundation Service | `PublicWorksFoundationService` — owns adapters and abstractions, exposes them to runtime/realms | Who receives PublicWorks or its members? What methods are called on a typical boot and first request? |

**Probe questions (from PROBE_LAYER_MAP):**

- What are our **adapters** actually doing? Which are wired at boot? Which are used on first request vs never?
- How does the **4-layer pattern** actually work in code? Are any layers empty, duplicated, or bypassed?
- Who **calls** PublicWorks? What methods are invoked on a typical boot and first request?
- **Service mapping:** Services were built for a prior architecture. What does the foundation service expose today? What does the **current platform vision** actually need? What should be updated?

---

## 4. Work Breakdown (Multi-Day)

Work is organized so it can be done incrementally; each phase can take time and surface refactors.

### Phase A — Adapter inventory

- **Per adapter** (in `adapters/`): name, purpose, config keys that create it, wired at boot? (from foundation_service._create_adapters), used by which abstraction(s), used by which caller(s) outside Public Works (realms, runtime, civic). Note: startup/connection behavior — does it connect in __init__, in connect(), or elsewhere? Should that align with pre-boot vs Φ3?
- **Output:** Public Works Reality Map — Adapters section (list, wired?, used?, callers). **Started:** [PUBLIC_WORKS_REALITY_MAP.md](testing/PUBLIC_WORKS_REALITY_MAP.md) Phase A.
- **Vision check:** For each: does it fit “Storage / Compute / Queue / Network” or another explicit foundation concern? If not, document as gap or legacy.

### Phase B — Abstraction inventory

- **Per abstraction** (in `abstractions/`): name, purpose, which adapters it uses (Layer 0), which protocol(s) it implements (Layer 2), who receives it (foundation_service attributes, passed to runtime/realms). Wired at boot? Used on first request or later?
- **Output:** Public Works Reality Map — Abstractions section (list, adapters used, protocols, callers).
- **Vision check:** Does the abstraction present a “uniform interface” and “platform contract” to callers, or do callers depend on concrete types?

### Phase C — Protocol audit

- **Per protocol** (in `protocols/`): name, intended contract, which abstractions implement it, who types against the protocol vs concrete abstraction. Are protocols the real boundary or are callers bound to implementations?
- **Output:** Public Works Reality Map — Protocols section (list, implementers, callers typed to protocol vs concrete). **Done:** [PUBLIC_WORKS_REALITY_MAP.md](testing/PUBLIC_WORKS_REALITY_MAP.md) Phase C.
- **Vision check:** “Adapter → Abstraction → Platform Contract” — is the contract the protocol? If not, where is the contract?

### Phase D — 5-layer flow (evidence)

- Trace one or more flows: e.g. “first request needs state” → StateSurface → state_abstraction → Redis/Arango adapters. Document: Layer 0 → 1 → 2 (if any) → 4 (foundation service) → caller. Is Layer 3 present? Are there bypasses (e.g. realm calling an adapter directly)?
- **Output:** 4-layer flow document with evidence (call stacks or references). **Done:** [PUBLIC_WORKS_REALITY_MAP.md](testing/PUBLIC_WORKS_REALITY_MAP.md) Phase D.
- **Vision check:** Does “Public Works → Adapter → Abstraction → Platform Contract” hold in practice?

### Phase E — Vision alignment and gap map

- Map current state to vision: Public Works = “Storage, Compute, Queue, Network” adapters + uniform interfaces + hot-swappable backends + deterministic behavior. List alignments and gaps.
- **Gap examples:** Startup logic in adapters that should be pre-boot or explicit; duplicate exposure (same capability via adapter and abstraction with different contracts); abstractions that don’t implement a protocol; callers bound to concrete types; “Curator” responsibilities mixed into Public Works or vice versa.
- **Output:** Vision alignment summary + gap map + refactor backlog (prioritized or ordered by layer).
- **Done:** [PUBLIC_WORKS_REALITY_MAP.md](testing/PUBLIC_WORKS_REALITY_MAP.md) Phase E (alignments, gap map, service mapping recommendations, refactor backlog P1–P6, summary).
- **Refactor backlog:** Items such as: “Move X from adapter init to pre-boot”; “Define protocol Y and have callers use it”; “Register Z in Curator, not in Public Works”; etc.

### Phase F — Curator boundary (foundations)

- Ensure “what gets registered and where” is clear: Curator = registries (IntentRegistry, registry_abstraction, SolutionRegistry, etc.). Public Works should not own “what gets registered” beyond providing registry_abstraction; registration of intents/solutions/capabilities belongs in Curator/runtime. Document any overlap or ambiguity.
- **Output:** Curator vs Public Works boundary note; any refactors to move registration out of adapters/abstractions into explicit registry steps.

---

## 5. Deliverables

| Deliverable | Content |
|-------------|---------|
| **Public Works Reality Map** | Adapters (list, wired?, used?, callers, vision need), Abstractions (list, adapters, protocols, callers), Protocols (list, implementers, callers), 4-layer flow (evidence), **service exposure vs current vision**. Can be one doc or several; linked from this plan. |
| **Vision alignment + gap map** | What aligns with updated_platform_vision and PLATFORM_VISION_RECONCILIATION; what doesn’t; refactor backlog. |
| **Why foundations work and how they behave** (Step 2 deliverable) | Updated after this review: what is guaranteed, what is optional, what fails, and how the 4-layer pattern and vision alignment stand. |

---

## 6. Relationship to Meet in the Middle Step 2

- **Step 2** in MEET_IN_THE_MIDDLE_PLAN is “Probe foundations (Public Works, Curator).”
- **This plan** is the **full scope** of that probe: review all adapters, review the 4-layer pattern (Adapter → Abstraction → Protocol → Service), validate alignment with current architectural vision, and **review how services should be updated** (they were built for a prior architecture). It is explicitly a **multi-day, messy** job; material refactoring may be identified at every layer.
- The existing [STEP2_FOUNDATIONS_PROBE.md](testing/STEP2_FOUNDATIONS_PROBE.md) and [WHY_FOUNDATIONS_WORK_AND_HOW_THEY_BEHAVE.md](WHY_FOUNDATIONS_WORK_AND_HOW_THEY_BEHAVE.md) are a **first pass** (boot-time snapshot, config keys, Curator = registries). They do **not** replace this plan; they are inputs. The **definitive** “why foundations work and how they behave” deliverable should be updated after Phases A–F (or after each phase, incrementally).

---

## 7. How to Use This Plan

- Run **Phases A–F** in order; each phase can take a day or more.
- Update the Public Works Reality Map and gap map as you go.
- When alignment and refactor backlog are clear, update WHY_FOUNDATIONS_WORK_AND_HOW_THEY_BEHAVE and Step 2 checklist in MEET_IN_THE_MIDDLE_PLAN.
- Do **not** block Step 3 (runtime probe) on completing every phase if the team agrees to “foundations probe in progress”; but the intent is to **finish** this review and alignment before calling Step 2 complete.
