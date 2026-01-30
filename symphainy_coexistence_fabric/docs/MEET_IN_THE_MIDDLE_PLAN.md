# Meet in the Middle: Takeoff Plan (Probing Approach)

**Purpose:** Takeoff’s plan to “meet Team B in the middle” at the Experience SDK and runtime contracts. We use a **probing approach**: at each layer we reconcile (docs ↔ code ↔ behavior), validate (run and capture), and document **why it works and how it’s going to behave**. Order is strict: finish genesis → foundations → runtime → civic systems → backend E2E → Phase 2b → frontend E2E.

**References:** [PLATFORM_VISION_RECONCILIATION.md](PLATFORM_VISION_RECONCILIATION.md), [HANDOFF_TO_TEAM_B.md](HANDOFF_TO_TEAM_B.md), [LANDING_AGENT_TASKS.md](LANDING_AGENT_TASKS.md), [FOUNDATION_PLAN.md](FOUNDATION_PLAN.md), [PHASE0_WHAT_WE_ACTUALLY_BUILT.md](testing/PHASE0_WHAT_WE_ACTUALLY_BUILT.md), [MVP_FRONTEND_BACKEND_CONNECTIVITY.md](architecture/MVP_FRONTEND_BACKEND_CONNECTIVITY.md).

---

## 1. What “probing” means here

- **Reconcile:** Align docs, code, and observed behavior. Where they diverge, fix or document the delta and the authority (e.g. executable truth wins; reconcile back into vision).
- **Validate:** Run the system (or the layer), capture what actually happens (logs, responses, failures), and confirm invariants.
- **Deliverable per step:** A short **“why it works and how it’s going to behave”** narrative (or checklist) so the next layer and Team B can rely on it. No step is “done” without this.

Same mindset as startup probing (e.g. [PHASE0_WHAT_WE_ACTUALLY_BUILT.md](testing/PHASE0_WHAT_WE_ACTUALLY_BUILT.md)): we don’t assume; we probe, capture, and document.

---

## 2. What “meet in the middle” means

- **Boundary:** The **Experience SDK** and **runtime contracts** (IntentRegistry, ExecutionContext, state surface, artifact surface) are the handoff. Takeoff exposes them; Team B consumes them.
- **Takeoff delivers:** Genesis complete, foundations/runtime/civic systems probed and documented, backend E2E and (optionally) Phase 2b + one frontend E2E path—each with a “why it works and how it behaves” story.
- **Team B delivers:** Canonical architecture doc, capabilities/ and experience/ layout, migration map, and (over time) intent implementations and experience surfaces that call the SDK.
- **Meet:** When both sides are ready, we integrate; one critical path (session → intent → execution status → result) works end-to-end; no solution/agent/experience bypasses the SDK (hard invariant).

---

## 3. Ordered probing sequence (Takeoff)

Execute in this order. Each step ends with: **reconcile → validate → document why it works and how it’s going to behave.**

### Step 1 — Finish genesis protocol

**Goal:** Complete whatever remains of the Genesis Protocol so boot is gated, deterministic, and aligned to the vision (Φ1–Φ4 / G1–G4 as in [genesis_protocol.md](genesis_protocol.md) and [FOUNDATION_PLAN.md](FOUNDATION_PLAN.md)).

**Probe:**

- Reconcile genesis doc (phases, gates) with the actual boot path in code (e.g. `runtime_main.py`, bootstrap, `create_runtime_services()`).
- Confirm G2 (config loads), G3 (pre-boot / Public Works reachable), and Φ3 init order are enforced or explicitly deferred with a reason.
- Lifecycle hooks (startup_begin, startup_complete, shutdown_begin, shutdown_complete, crash_detected): define the five hooks and insert them in the boot/lifecycle path; MVP = no-ops. Document locations in BOOT_PHASES or a short lifecycle doc.

**Deliverable:** Genesis is “finished” to the agreed scope (e.g. G2/G3/Φ3 in code; Φ4 stub optional here or in Step 4). Written **“why genesis works and how boot behaves”** (what runs when, what fails fast, what is deferred).

**References:** [genesis_protocol.md](genesis_protocol.md), [FOUNDATION_PLAN.md](FOUNDATION_PLAN.md), [BOOT_PHASES.md](architecture/BOOT_PHASES.md), [PLATFORM_VISION_RECONCILIATION.md](PLATFORM_VISION_RECONCILIATION.md) §2.3 (lifecycle hooks).

---

### Step 2 — Probe foundations (Public Works, Curator)

**Goal:** Review **all** adapters and the **5-layer pattern** for exposing them; **validate alignment** with the current architectural vision (updated_platform_vision, PLATFORM_VISION_RECONCILIATION). This is a **multi-day, messy** job: material refactoring may emerge at every layer (e.g. removing startup logic from adapters, defining what actually gets registered and where in Curator).

**Probe:**

- **Public Works:** What adapters/abstractions actually exist at boot? What config keys drive them? Run boot, capture log (as in PHASE0_WHAT_WE_ACTUALLY_BUILT); reconcile with CONFIG_ACQUISITION_SPEC / PRE_BOOT_SPEC. Document which adapters are created vs not in dev/CI/prod.
- **Curator:** Per PLATFORM_VISION_RECONCILIATION, Curator = existing registries (e.g. IntentRegistry, schema registry). Reconcile docs with code: where do “Curator” responsibilities live? Validate that registry access and registration behave as documented.

**Deliverable:** Foundations probe report (or update to PHASE0_WHAT_WE_ACTUALLY_BUILT / FOUNDATION_PLAN). **“Why foundations work and how they behave”** — what is guaranteed at boot, what is optional, what fails and how.

**References:** [PUBLIC_WORKS_PROBE_PLAN.md](PUBLIC_WORKS_PROBE_PLAN.md) (full scope: all adapters, 5-layer pattern, vision alignment — multi-day), [PHASE0_WHAT_WE_ACTUALLY_BUILT.md](testing/PHASE0_WHAT_WE_ACTUALLY_BUILT.md), [PROBE_LAYER_MAP.md](testing/PROBE_LAYER_MAP.md), [updated_platform_vision.md](updated_platform_vision.md), [CONFIG_ACQUISITION_SPEC.md](architecture/CONFIG_ACQUISITION_SPEC.md), [PRE_BOOT_SPEC.md](architecture/PRE_BOOT_SPEC.md).

---

### Step 3 — Probe runtime (including data brain)

**Goal:** Reconcile and validate the runtime layer; confirm what is implemented vs only designed, and document why it works and how it behaves. Include the **data brain** feature: we have runtime-native data cognition (`DataBrain`, references, provenance); probe whether it’s wired into the runtime graph and integrated into execution/state/artifacts.

**Probe:**

- **Runtime graph:** Init order (StateSurface, WAL, IntentRegistry, ExecutionLifecycleManager, etc.). Run boot and execution paths; capture what is actually used on a typical intent run.
- **Data brain:** `symphainy_platform/runtime/data_brain.py` exists (DataBrain, DataReference, ProvenanceEntry). Is it constructed in the runtime graph? Is it used by StateSurface, artifact resolution, or any journey? If not, document “designed but not integrated” and either wire it or document the path to integration.
- **State surface / WAL / execution lifecycle:** Reconcile with RUNTIME_CONTRACTS; validate read/write and execution flow.

**Deliverable:** Runtime probe report. **“Why the runtime works and how it behaves”** — including a clear line on data brain: implemented and integrated vs scaffold-only and where it plugs in later.

**References:** [RUNTIME_CONTRACTS.md](architecture/RUNTIME_CONTRACTS.md), [ARCHITECTURE_NORTH_STAR.md](ARCHITECTURE_NORTH_STAR.md) (Data Brain / State Surface), `symphainy_platform/runtime/data_brain.py`, [INIT_ORDER_SPEC.md](architecture/INIT_ORDER_SPEC.md).

---

### Step 4 — Probe civic systems (Smart City, Agentic, Experience; Platform SDK & Orchestrator Health)

**Goal:** Reconcile and validate civic systems; document why they work and how they behave. This is where we **decide and document** Platform SDK and Orchestrator Health (per EXPERIENCE_CIVIC_REFACTOR_PLAN Phase 3).

**Probe:**

- **Smart City / Agentic / Experience:** What roles and APIs exist in code vs docs? Experience SDK contract is already defined; validate that Experience API and RuntimeClient behave per EXPERIENCE_SDK_CONTRACT. Smart City and Agentic: reconcile names to actual services and governance boundaries.
- **Platform SDK:** Decide (A) keep for solution/capability discovery and admin, (B) deprecate and replace with a smaller “list capabilities/solutions” API on the Experience SDK, or (C) keep internal-only. Document in `docs/architecture/PLATFORM_SDK_DECISION.md` (or section in canonical architecture). If (A) or (B), ensure Experience SDK or admin exposes “list solutions/capabilities” and “get solution/capability config” if experience surfaces need them.
- **Orchestrator Health:** Decide (A) keep as part of control-tower/observability, (B) move under dedicated control_tower API, or (C) keep as-is and document. Document in `docs/architecture/ORCHESTRATOR_HEALTH_DECISION.md` (or same doc). Ensure admin routes (control_room, developer_view, business_user_view) still work after decisions.
- **Φ4 stub (optional):** After “runtime graph ready” / “Experience app created,” call a documented step `attach_experience_surfaces(sdk, config)` — no-op or log. Document in BOOT_PHASES that real implementations will register or bind experience UIs here.

**Deliverable:** Civic systems probe report + **PLATFORM_SDK_DECISION** and **ORCHESTRATOR_HEALTH_DECISION**. **“Why civic systems work and how they behave”** — including Platform SDK and Orchestrator Health placement and Φ4 hook.

**References:** [EXPERIENCE_SDK_CONTRACT.md](architecture/EXPERIENCE_SDK_CONTRACT.md), [EXPERIENCE_CIVIC_REFACTOR_PLAN.md](architecture/EXPERIENCE_CIVIC_REFACTOR_PLAN.md) Phase 3, [PLATFORM_VISION_RECONCILIATION.md](PLATFORM_VISION_RECONCILIATION.md).

---

### Step 5 — Backend-only E2E (with probing)

**Goal:** Prove the platform and internal contracts work without the frontend. Probe the path; document **why it works and how it’s going to behave**.

**Probe:**

- Start Runtime + Experience.
- Run: create session (e.g. anonymous or auth via Experience API) → submit intent (e.g. compose_journey or content parse) → get execution status (via Experience or Runtime) → resolve artifact or read result.
- Capture successes and failures; reconcile with RUNTIME_CONTRACTS and EXPERIENCE_SDK_CONTRACT. Fix or document any mismatch.

**Deliverable:** Backend-only E2E path documented (e.g. “MVP critical path (backend-only)”). **“Why backend E2E works and how it behaves”** — sequence, assumptions, and known limits.

**References:** [RUNTIME_CONTRACTS.md](architecture/RUNTIME_CONTRACTS.md), [MVP_FRONTEND_BACKEND_CONNECTIVITY.md](architecture/MVP_FRONTEND_BACKEND_CONNECTIVITY.md) §3.3.

---

### Step 6 — Phase 2b: Experience proxy (with probing)

**Goal:** Frontend uses one base URL. Auth, session, intent live on Experience (8001); execution status, artifact resolve/list, intent/pending live only on Runtime (8000). Add proxy so the frontend can point at Experience and all needed calls succeed. Probe and document **why it works and how it’s going to behave**.

**Probe:**

- Add proxy routes on the Experience app for: `GET /api/execution/{execution_id}/status`, `POST /api/artifact/resolve`, `POST /api/artifact/list`, `GET /api/artifacts/{artifact_id}` (if used), `POST /api/intent/pending/list`, `POST /api/intent/pending/create`. Forward to Runtime (e.g. via RuntimeClient or HTTP forwarder); pass tenant_id and required params.
- Document in EXPERIENCE_SDK_CONTRACT or MVP_FRONTEND_BACKEND_CONNECTIVITY that Experience is the single gateway for the frontend; proxy list is source of truth.
- Validate: set frontend `NEXT_PUBLIC_API_URL` to Experience (8001); confirm all needed calls succeed.

**Deliverable:** Phase 2b implemented and documented. **“Why the proxy works and how it behaves”** — which routes are proxied, how errors and timeouts are handled, and any limits.

**References:** [MVP_FRONTEND_BACKEND_CONNECTIVITY.md](architecture/MVP_FRONTEND_BACKEND_CONNECTIVITY.md) §3.1, [EXPERIENCE_SDK_CONTRACT.md](architecture/EXPERIENCE_SDK_CONTRACT.md).

---

### Step 7 — One frontend E2E path (with probing)

**Goal:** One user-visible path works end-to-end (e.g. open site → create session → submit intent → see result). Probe and document **why it works and how it’s going to behave**.

**Probe:**

- With Phase 2b and frontend env pointing at Experience: drive one path (e.g. anonymous session → submit one intent → get execution status → show result or artifact).
- Fix broken links (missing proxy, wrong params, response shape). Capture the exact flow and assumptions.

**Deliverable:** One frontend E2E path documented and regression-testable. **“Why this frontend path works and how it behaves”** — steps, env, and known caveats.

**References:** [MVP_FRONTEND_BACKEND_CONNECTIVITY.md](architecture/MVP_FRONTEND_BACKEND_CONNECTIVITY.md) §3.3.

---

## 4. Execution order and checklist

| Order | Step | Dependency | Deliverable |
|-------|------|------------|-------------|
| 1 | **Finish genesis protocol** | None | Genesis complete; “why genesis works and how boot behaves” |
| 2 | **Probe foundations** (Public Works, Curator) | Step 1 | Foundations probe report; “why foundations work and how they behave” |
| 3 | **Probe runtime** (incl. data brain) | Step 2 | Runtime probe report; “why runtime works and how it behaves” (+ data brain status) |
| 4 | **Probe civic systems** (Smart City, Agentic, Experience; Platform SDK & Orchestrator Health) | Step 3 | Civic probe report + PLATFORM_SDK_DECISION + ORCHESTRATOR_HEALTH_DECISION; “why civic systems work and how they behave” |
| 5 | **Backend-only E2E** (probing) | Steps 1–4 | Backend E2E path doc; “why backend E2E works and how it behaves” |
| 6 | **Phase 2b** (Experience proxy, probing) | Step 4 (Experience SDK stable) | Proxy implemented and documented; “why proxy works and how it behaves” |
| 7 | **One frontend E2E path** (probing) | Step 6 | One user-visible path doc; “why this frontend path works and how it behaves” |

**Parallelism:** Steps 1–4 are sequential by layer. Step 5 (backend E2E) can start once Steps 1–4 are done. Step 6 (Phase 2b) can overlap with Step 5 if Experience API is stable. Step 7 requires Step 6.

---

## 5. Integration point (when both sides are ready)

### 5.1 What we need from Team B

- **Task 0:** Canonical architecture doc — Takeoff can align boot and civic docs to it using the authority chain.
- **Tasks 2–3:** capabilities/ and experience/ layout — no Takeoff code change required; we may reference in docs.
- **Task 4:** Boot phases doc — match or reconcile with BOOT_PHASES and PLATFORM_VISION_RECONCILIATION.
- **Task 6:** Migration map — Takeoff uses as the recipe for future migration.
- **Intent implementations:** As Team B implements intents against RUNTIME_CONTRACTS, they register with IntentRegistry and run on the runtime we own; we keep runtime and SDK stable.

### 5.2 Validation at “meet”

1. **Contract test:** Experience service exposes SDK operations; stub or Team B client gets expected shapes.
2. **Backend E2E:** Session → intent → execution status → result (backend-only) passes; “why it works” doc exists.
3. **Frontend E2E (if Step 6–7 done):** One path works with frontend pointing at Experience; “why it works” doc exists.
4. **Hard invariant:** No solution, agent, MCP server, or experience directly accesses runtime internals, civic systems, or infrastructure; all access via Experience SDK or governed capability interfaces.

### 5.3 Merge and doc strategy

- **Code:** Takeoff owns runtime/, civic_systems/experience (SDK implementation), boot, and proxy routes. Team B owns capabilities/, experience/ layout and additive docs. Conflicts: resolve using PLATFORM_VISION_RECONCILIATION §8 (authority chain). Executable truth wins; reconcile back.
- **Docs:** If Team B’s canonical or boot doc diverges from BOOT_PHASES or INIT_ORDER_SPEC, reconcile: update our executable docs or their doc so we do not leave two conflicting specs.

---

## 6. Success criteria (definition of “met in the middle”)

- [ ] **Genesis** is finished to agreed scope; foundations, runtime, and civic systems are **probed** and have a “why it works and how it behaves” story.
- [ ] **Experience SDK** is the single contract; all experience/solution/agent access goes through it or governed capability interfaces (hard invariant).
- [ ] **Takeoff deliverables:** Steps 1–5 done (genesis, foundations probe, runtime probe, civic probe, backend E2E); Step 6 (Phase 2b) if frontend E2E is in scope; Step 7 (one frontend path) optional; lifecycle hooks (no-ops); Platform SDK and Orchestrator Health decisions documented.
- [ ] **One critical path works:** Session → intent → execution status → result (backend minimum; frontend E2E if Steps 6–7 done).
- [ ] **Docs aligned:** Boot and SDK contract are executable truth; canonical architecture and migration map are consistent (authority chain applied).

---

## 7. Summary

- **Approach:** Probing at each layer — reconcile (docs ↔ code ↔ behavior), validate (run and capture), document **why it works and how it’s going to behave**. Same mindset as startup probing (PHASE0_WHAT_WE_ACTUALLY_BUILT).
- **Order:** (1) Finish genesis → (2) Probe foundations (Public Works, Curator) → (3) Probe runtime (incl. data brain) → (4) Probe civic systems (Smart City, Agentic, Experience; Platform SDK & Orchestrator Health) → (5) Backend-only E2E → (6) Phase 2b (Experience proxy) → (7) One frontend E2E path.
- **We meet** when: one critical path works end-to-end (backend minimum, frontend if proxy is in), docs are reconciled via the authority chain, and no solution/agent/experience bypasses the SDK (hard invariant). This plan is Takeoff’s checklist to get there.
