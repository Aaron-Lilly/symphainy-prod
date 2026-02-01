# Meet in the Middle: Takeoff Plan (Audit–Fix–Probe–Document)

**Purpose:** Takeoff’s plan to “meet Team B in the middle” at the Platform Boundary (Experience SDK and runtime contracts). We use an **audit–fix–probe–document** approach: at each layer we **audit** against the final contracts and vision, **fix** deviations, **probe** to confirm success and failure are predictable, and **document** why it works and how it fails. Order is strict: genesis → foundations → runtime → civic systems → backend E2E → Phase 2b → frontend E2E.

**References:** [INTERCEPT_ALIGNMENT_CONTRACT.md](INTERCEPT_ALIGNMENT_CONTRACT.md), [PLATFORM_SDK_REQUIREMENT_SPEC.md](PLATFORM_SDK_REQUIREMENT_SPEC.md), [SOVEREIGNTY_ARCHITECTURE.md](architecture/SOVEREIGNTY_ARCHITECTURE.md), [PLATFORM_VISION_RECONCILIATION.md](PLATFORM_VISION_RECONCILIATION.md), [HANDOFF_TO_TEAM_B.md](HANDOFF_TO_TEAM_B.md), [FOUNDATION_PLAN.md](FOUNDATION_PLAN.md), [MVP_FRONTEND_BACKEND_CONNECTIVITY.md](architecture/MVP_FRONTEND_BACKEND_CONNECTIVITY.md).

---

## 1. New Phase: Contracts in Place

The platform told us enough to define what it **should be**. We now have final architectural contracts and vision:

- **Intercept Alignment Contract** — Platform Boundary, protocol getters, Curator/registry surface, Civic surfaces, Runtime-provided resources, protocol-only rule.
- **Platform SDK Requirement Spec** — What Team B builds from; Curator/registry contract, Smart City surfaces, ctx shape.
- **Sovereignty Architecture** — Three domains, Curator as intelligence governance authority, classification schema, promotion pipeline, agent learning through Curator.
- **Curator layer target** — Adapter→abstraction→protocol pattern, infra stack, cleanup order (CURATOR_LAYER_CLEANUP_AND_TARGET_PATTERN, CURATOR_SOVEREIGNTY_VISION_AND_INFRASTRUCTURE).

So we no longer “probe to discover”; we **audit against the contract**, **fix** what doesn’t match, then **probe to confirm** that the layer succeeds and fails in predictable ways we can document.

---

## 2. Approach: Audit → Fix → Probe → Document

- **Audit:** Compare the layer to the contract and vision. List gaps: missing getters, wrong types, adapter leaks, missing protocols, behavior that violates the “should be.”
- **Fix:** Implement the fixes so the layer conforms to the contract (protocol-only boundary, correct wiring, predictable failure modes).
- **Probe:** Run tests (or manual probes) to confirm: **success paths** behave as documented; **failure paths** fail in predictable ways (e.g. Platform contract §8A, missing dependency → RuntimeError with clear message, no silent degradation).
- **Document:** Capture **“why it works and how it behaves”** and **“how it fails and when”** so the next layer and Team B can rely on it. No step is “done” without this.

Probe tests are used to **confirm** conformance, not to discover behavior. We know what “should” happen; we fix until probes pass and failure modes are documented.

---

## 2. What “meet in the middle” means

- **Boundary:** The **Experience SDK** and **runtime contracts** (IntentRegistry, ExecutionContext, state surface, artifact surface) are the handoff. Takeoff exposes them; Team B consumes them.
- **Takeoff delivers:** Genesis complete, foundations/runtime/civic systems probed and documented, backend E2E and (optionally) Phase 2b + one frontend E2E path—each with a “why it works and how it behaves” story.
- **Team B delivers:** Canonical architecture doc, capabilities/ and experience/ layout, migration map, and (over time) intent implementations and experience surfaces that call the SDK.
- **Meet:** When both sides are ready, we integrate; one critical path (session → intent → execution status → result) works end-to-end; no solution/agent/experience bypasses the SDK (hard invariant).

---

## 5. Ordered sequence (Takeoff): Audit → Fix → Probe → Document

Execute in this order. Each step: **audit** the layer against the contract/vision, **fix** deviations, **probe** to confirm success and failure are predictable, **document** why it works and how it fails.

### Step 1 — Finish genesis protocol

**Goal:** Complete whatever remains of the Genesis Protocol so boot is gated, deterministic, and aligned to the vision (Φ1–Φ4 / G1–G4 as in [genesis_protocol.md](genesis_protocol.md) and [FOUNDATION_PLAN.md](FOUNDATION_PLAN.md)).

**Probe:**

- Reconcile genesis doc (phases, gates) with the actual boot path in code (e.g. `runtime_main.py`, bootstrap, `create_runtime_services()`).
- Confirm G2 (config loads), G3 (pre-boot / Public Works reachable), and Φ3 init order are enforced or explicitly deferred with a reason.
- Lifecycle hooks (startup_begin, startup_complete, shutdown_begin, shutdown_complete, crash_detected): define the five hooks and insert them in the boot/lifecycle path; MVP = no-ops. Document locations in BOOT_PHASES or a short lifecycle doc.

**Deliverable:** Genesis is “finished” to the agreed scope (e.g. G2/G3/Φ3 in code; Φ4 stub optional here or in Step 4). **Audit** boot against genesis doc; **fix** gaps; **probe** boot (success path + missing config / failure path); **document** “why genesis works and how boot behaves” and “how it fails and when.”

**References:** [genesis_protocol.md](genesis_protocol.md), [FOUNDATION_PLAN.md](FOUNDATION_PLAN.md), [BOOT_PHASES.md](architecture/BOOT_PHASES.md), [PLATFORM_VISION_RECONCILIATION.md](PLATFORM_VISION_RECONCILIATION.md) §2.3 (lifecycle hooks).

---

### Step 2 — Foundations (Public Works, Curator)

**Goal:** Align foundations with the **Platform Boundary** and Curator target pattern. **Audit** against INTERCEPT_ALIGNMENT_CONTRACT (protocol getters, no adapter leak), CURATOR_LAYER_CLEANUP_AND_TARGET_PATTERN (adapter→abstraction→protocol, file_storage for list_files not registry), and SOVEREIGNTY vision. **Fix** deviations (missing getters, wrong callers, Curator stubs/unification). **Probe** to confirm: boot succeeds with expected config; missing optional adapter fails predictably (e.g. no crash, clear log); Curator/registry surface behaves per contract. **Document** “why foundations work and how they behave” and “how they fail and when.”

**Audit:**

- **Public Works:** Do all boundary getters exist and return protocol types? Any adapter leaks? Config per CONFIG_ACQUISITION_SPEC / PRE_BOOT_SPEC? Which adapters are created vs not in dev/CI/prod?
- **Curator:** Does ctx.governance.registry get a Curator implementation that matches the contract (register_capability, discover_agents, get_domain_registry, promote_to_platform_dna)? Are list_files callers using file_storage not registry? Curator backing unified (Supabase or CuratorFoundationService)?

**Deliverable:** Foundations **audit list** (gaps vs contract), **fixes** applied, **probe** results (success + failure paths). **“Why foundations work and how they behave”** and **“how they fail and when.”**

**Strategic approach:** Do not rely on "fix in context as we work up" alone. Execute Step 2 as a **Foundation Contract Pass** per [FOUNDATION_CONTRACT_PASS_STRATEGY.md](FOUNDATION_CONTRACT_PASS_STRATEGY.md): define the foundation contract, audit against it, fix all violations, probe in isolation, document "foundation contract satisfied." Only then proceed to Runtime and Civic; if we find a foundation bug above, fix it and re-run foundation probes.

**Get-on-track path:** For a single contract, CTA pattern (no fallbacks, no adapter leak), and Public Works-first-then-Curator order, use [GETTING_ON_TRACK_ASSESSMENT_AND_PLAN.md](GETTING_ON_TRACK_ASSESSMENT_AND_PLAN.md), [PUBLIC_WORKS_CONTRACT.md](PUBLIC_WORKS_CONTRACT.md), and [architecture/PUBLIC_WORKS_CTA_PATTERN.md](architecture/PUBLIC_WORKS_CTA_PATTERN.md): fill the Public Works contract, audit against it and CTA, fix all gaps, probe, document; then start Curator with schema and migrations for Supabase and build adapter → abstraction → protocol.

**References:** [FOUNDATION_CONTRACT_PASS_STRATEGY.md](FOUNDATION_CONTRACT_PASS_STRATEGY.md), [CURATOR_INFRASTRUCTURE_ALIGNMENT.md](CURATOR_INFRASTRUCTURE_ALIGNMENT.md), [CURATOR_LAYER_CLEANUP_AND_TARGET_PATTERN.md](CURATOR_LAYER_CLEANUP_AND_TARGET_PATTERN.md), [PUBLIC_WORKS_PROBE_PLAN.md](PUBLIC_WORKS_PROBE_PLAN.md), [PHASE0_WHAT_WE_ACTUALLY_BUILT.md](testing/PHASE0_WHAT_WE_ACTUALLY_BUILT.md), [CONFIG_ACQUISITION_SPEC.md](architecture/CONFIG_ACQUISITION_SPEC.md), [PRE_BOOT_SPEC.md](architecture/PRE_BOOT_SPEC.md).

---

### Step 3 — Runtime (including data brain)

**Goal:** Align runtime with RUNTIME_CONTRACTS and intercept (StateSurface, WAL, ArtifactRegistry injected into PlatformContextFactory; execution lifecycle). **Audit** init order, what is wired vs scaffold-only (e.g. DataBrain). **Fix** wiring gaps. **Probe** to confirm: boot builds runtime graph; intent run uses StateSurface/WAL/ArtifactRegistry; missing dependency fails predictably (e.g. Platform contract §8A). **Document** “why runtime works and how it behaves” and “how it fails and when”; data brain: wired vs deferred and path to integration.

**References:** [RUNTIME_CONTRACTS.md](architecture/RUNTIME_CONTRACTS.md), [ARCHITECTURE_NORTH_STAR.md](ARCHITECTURE_NORTH_STAR.md) (Data Brain / State Surface), `symphainy_platform/runtime/data_brain.py`, [INIT_ORDER_SPEC.md](architecture/INIT_ORDER_SPEC.md).

---

### Step 4 — Civic systems (Smart City, Agentic, Experience; Platform SDK & Orchestrator Health)

**Goal:** Align civic systems with EXPERIENCE_SDK_CONTRACT and intercept (ctx from boundary getters). **Audit** Smart City/Agentic/Experience vs contract; Platform SDK and Orchestrator Health placement. **Fix** deviations. **Probe** to confirm: Experience API and RuntimeClient behave per contract; admin routes work; missing dependency fails predictably. **Document** PLATFORM_SDK_DECISION and ORCHESTRATOR_HEALTH_DECISION; “why civic systems work and how they behave” and “how they fail and when.”

**References:** [EXPERIENCE_SDK_CONTRACT.md](architecture/EXPERIENCE_SDK_CONTRACT.md), [EXPERIENCE_CIVIC_REFACTOR_PLAN.md](architecture/EXPERIENCE_CIVIC_REFACTOR_PLAN.md) Phase 3, [PLATFORM_VISION_RECONCILIATION.md](PLATFORM_VISION_RECONCILIATION.md).

---

### Step 5 — Backend-only E2E

**Goal:** Prove the platform and internal contracts work without the frontend. **Audit** critical path (session → intent → execution status → result) against RUNTIME_CONTRACTS and EXPERIENCE_SDK_CONTRACT. **Fix** any mismatch. **Probe** to confirm: success path works; failure paths (e.g. missing tenant, invalid intent) fail predictably. **Document** “why backend E2E works and how it behaves” and “how it fails and when.”

**References:** [RUNTIME_CONTRACTS.md](architecture/RUNTIME_CONTRACTS.md), [MVP_FRONTEND_BACKEND_CONNECTIVITY.md](architecture/MVP_FRONTEND_BACKEND_CONNECTIVITY.md) §3.3.

---

### Step 6 — Phase 2b: Experience proxy

**Goal:** Frontend uses one base URL. Auth, session, intent live on Experience (8001); execution status, artifact resolve/list, intent/pending live only on Runtime (8000). Add proxy so the frontend can point at Experience and all needed calls succeed. Probe and document **why it works and how it’s going to behave**.

**Probe:**

- Add proxy routes on the Experience app for: `GET /api/execution/{execution_id}/status`, `POST /api/artifact/resolve`, `POST /api/artifact/list`, `GET /api/artifacts/{artifact_id}` (if used), `POST /api/intent/pending/list`, `POST /api/intent/pending/create`. Forward to Runtime (e.g. via RuntimeClient or HTTP forwarder); pass tenant_id and required params.
- Document in EXPERIENCE_SDK_CONTRACT or MVP_FRONTEND_BACKEND_CONNECTIVITY that Experience is the single gateway for the frontend; proxy list is source of truth.
- Validate: set frontend `NEXT_PUBLIC_API_URL` to Experience (8001); confirm all needed calls succeed.

**Deliverable:** Phase 2b implemented and documented. **“Why the proxy works and how it behaves”** — which routes are proxied, how errors and timeouts are handled, and any limits.

**References:** [MVP_FRONTEND_BACKEND_CONNECTIVITY.md](architecture/MVP_FRONTEND_BACKEND_CONNECTIVITY.md) §3.1, [EXPERIENCE_SDK_CONTRACT.md](architecture/EXPERIENCE_SDK_CONTRACT.md).

---

### Step 7 — One frontend E2E path

**Goal:** One user-visible path works end-to-end (e.g. open site → create session → submit intent → see result). **Audit** path against Phase 2b proxy and frontend spec. **Fix** broken links (proxy, params, response shape). **Probe** to confirm: success path works; failure paths (e.g. network error, invalid session) fail predictably. **Document** “why this frontend path works and how it behaves” and “how it fails and when.”

**References:** [MVP_FRONTEND_BACKEND_CONNECTIVITY.md](architecture/MVP_FRONTEND_BACKEND_CONNECTIVITY.md) §3.3.

---

## 5. Execution order and checklist

| Order | Step | Dependency | Deliverable |
|-------|------|------------|-------------|
| 1 | **Genesis** (audit → fix → probe → document) | None | Genesis complete; “why genesis works and how boot behaves” and “how it fails and when” |
| 2 | **Foundations** (Public Works, Curator) | Step 1 | Audit list + fixes; probe results; “why foundations work and how they behave” and “how they fail and when” |
| 3 | **Runtime** (incl. data brain) | Step 2 | Audit list + fixes; probe results; “why runtime works and how it behaves” and “how it fails and when” |
| 4 | **Civic systems** (Smart City, Agentic, Experience; Platform SDK & Orchestrator Health) | Step 3 | Civic audit + fixes; PLATFORM_SDK_DECISION + ORCHESTRATOR_HEALTH_DECISION; “why civic systems work and how they behave” and “how they fail and when” |
| 5 | **Backend-only E2E** | Steps 1–4 | Backend E2E path doc; “why backend E2E works and how it behaves” and “how it fails and when” |
| 6 | **Phase 2b** (Experience proxy) | Step 4 (Experience SDK stable) | Proxy implemented and documented; “why proxy works and how it behaves” and “how it fails and when” |
| 7 | **One frontend E2E path** | Step 6 | One user-visible path doc; “why this frontend path works and how it behaves” and “how it fails and when” |

**Parallelism:** Steps 1–4 are sequential by layer. Step 5 (backend E2E) can start once Steps 1–4 are done. Step 6 (Phase 2b) can overlap with Step 5 if Experience API is stable. Step 7 requires Step 6.

---

## 5. Integration point (when both sides are ready)

### 5.1 What we need from Team B

- **Task 0:** Canonical architecture doc — Takeoff can align boot and civic docs to it using the authority chain.
- **Tasks 2–3:** capabilities/ and experience/ layout — no Takeoff code change required; we may reference in docs.
- **Task 4:** Boot phases doc — match or reconcile with BOOT_PHASES and PLATFORM_VISION_RECONCILIATION.
- **Task 6:** Migration map — Takeoff uses as the recipe for future migration.
- **Intent implementations:** As Team B implements intents against RUNTIME_CONTRACTS, they register with IntentRegistry and run on the runtime we own; we keep runtime and SDK stable.

### 6.2 Validation at “meet”

1. **Contract test:** Experience service exposes SDK operations; stub or Team B client gets expected shapes.
2. **Backend E2E:** Session → intent → execution status → result (backend-only) passes; “why it works” doc exists.
3. **Frontend E2E (if Step 6–7 done):** One path works with frontend pointing at Experience; “why it works” doc exists.
4. **Hard invariant:** No solution, agent, MCP server, or experience directly accesses runtime internals, civic systems, or infrastructure; all access via Experience SDK or governed capability interfaces.

### 5.3 Merge and doc strategy

- **Code:** Takeoff owns runtime/, civic_systems/experience (SDK implementation), boot, and proxy routes. Team B owns capabilities/, experience/ layout and additive docs. Conflicts: resolve using PLATFORM_VISION_RECONCILIATION §8 (authority chain). Executable truth wins; reconcile back.
- **Docs:** If Team B’s canonical or boot doc diverges from BOOT_PHASES or INIT_ORDER_SPEC, reconcile: update our executable docs or their doc so we do not leave two conflicting specs.

---

## 7. Success criteria (definition of “met in the middle”)

- [ ] **Genesis** is finished to agreed scope; foundations, runtime, and civic systems are **audited, fixed, and probed** and have a “why it works and how it behaves” and “how it fails and when” story.
- [ ] **Experience SDK** is the single contract; all experience/solution/agent access goes through it or governed capability interfaces (hard invariant).
- [ ] **Takeoff deliverables:** Steps 1–5 done (genesis, foundations probe, runtime probe, civic probe, backend E2E); Step 6 (Phase 2b) if frontend E2E is in scope; Step 7 (one frontend path) optional; lifecycle hooks (no-ops); Platform SDK and Orchestrator Health decisions documented.
- [ ] **One critical path works:** Session → intent → execution status → result (backend minimum; frontend E2E if Steps 6–7 done).
- [ ] **Docs aligned:** Boot and SDK contract are executable truth; canonical architecture and migration map are consistent (authority chain applied).

---

## 8. Summary

- **New phase:** We have final architectural contracts and vision (Intercept Alignment Contract, Platform SDK Requirement Spec, Sovereignty Architecture, Curator target pattern). We no longer “probe to discover”; we **audit against the contract**, **fix** deviations, **probe to confirm** success and failure are predictable, and **document** why it works and how it fails.
- **Approach:** **Audit → Fix → Probe → Document** at each layer. Probe tests **confirm** conformance; we know what “should” happen and fix until probes pass and failure modes are documented.
- **Order:** (1) Genesis → (2) Foundations (Public Works, Curator) → (3) Runtime (incl. data brain) → (4) Civic systems (Smart City, Agentic, Experience; Platform SDK & Orchestrator Health) → (5) Backend-only E2E → (6) Phase 2b (Experience proxy) → (7) One frontend E2E path.
- **We meet** when: one critical path works end-to-end (backend minimum, frontend if proxy is in), success and failure are predictable and documented, and no solution/agent/experience bypasses the SDK (hard invariant). This plan is Takeoff’s checklist to get there.
