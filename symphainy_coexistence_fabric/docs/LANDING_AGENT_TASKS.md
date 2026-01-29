# Landing Agent Tasks: Solution/Realm Refactoring

**Source vision:** [solution_realm_refactoring_vision.md](./solution_realm_refactoring_vision.md)  
**Strategy:** Takeoff (current work) continues; agents build toward the landing (target architecture); we meet in the middle via **contracts** and **additive structure**.

---

## Prerequisite: Experience Civic System Refactor (Takeoff)

**Landing agents start after takeoff has completed the Experience Civic System refactor** (or at least Phase 1–2). The Experience SDK is the **inflection point**: takeoff owns runtime + all civic systems and refactors the Experience Civic System so it exposes that SDK; landing builds capabilities and experiences that consume it.

**Takeoff must do first:**

1. **Audit:** [docs/architecture/EXPERIENCE_CIVIC_SYSTEM_AUDIT.md](architecture/EXPERIENCE_CIVIC_SYSTEM_AUDIT.md) — what the civic system provides today vs what the vision requires.
2. **Refactor plan:** [docs/architecture/EXPERIENCE_CIVIC_REFACTOR_PLAN.md](architecture/EXPERIENCE_CIVIC_REFACTOR_PLAN.md) — phased plan to deliver the Experience SDK.
3. **Execute Phase 1–2:** Define and document the Experience SDK contract; align RuntimeClient with Runtime API; implement the SDK facade and wire Experience routes through it. Optionally Phase 3 (platform_sdk / orchestrator_health decisions) and Phase 4 (Φ4 stub).

**When Phase 1–2 are done:** The Experience SDK contract exists (`EXPERIENCE_SDK_CONTRACT.md`), the civic system exposes it, and boot/docs state that “startup succeeds when the Experience SDK is ready.” **Then** landing agents run the tasks below (Task 0 → Tasks 1–6 → optional Task 7). Task 1 (contract) should **adopt** the contract produced by takeoff; if the contract doc already exists, Task 1 is “add protocol/ABC in code and link to doc” rather than inventing a new contract.

---

## Is This Possible? Is It Too Risky?

**Yes, it’s possible**, if we keep a few rules:

1. **Contract-first**  
   Define “Experience SDK” and “attach to runtime” contracts on paper (and in code as interfaces) before moving behavior. Takeoff and landing both implement to the same contract.

2. **Additive-first**  
   Introduce new namespaces (`/capabilities`, clarified `/experience`) **alongside** existing `symphainy_platform/solutions`, `realms`, etc. No big-bang renames or deletes until seams are clear and tests pass.

3. **Clear seams**  
   Agents own “landing” tasks (docs, new dirs, new registries, experience-as-client pattern). Takeoff continues to own boot, service_factory wiring, and current solutions/realms. Merge points are: (a) shared architecture doc, (b) Experience SDK contract, (c) boot phases Φ3 vs Φ4.

**Risks (and how we reduce them):**

| Risk | Mitigation |
|------|-------------|
| Agents rename/delete code takeoff depends on | Tasks forbid deleting or renaming existing solution/realm modules until an explicit “migrate” phase. |
| Service factory changes break boot | “Landing” tasks that touch service_factory are limited to **adding** capability/journey-engine registration, not removing current solution registration until a later, explicit migration task. |
| Two parallel structures drift | Single “canonical architecture” doc (Task 0) and a small “platform layout” ADR that both sides must follow. |
| Experience layer assumes runtime shape that takeoff doesn’t have yet | Experience SDK is defined as an **interface** (query state, invoke intents, trigger journeys, subscribe to signals). Takeoff implements the interface; landing builds clients that depend only on the interface. |

**Verdict:** Not too risky if we stick to contracts, additive structure, and no destructive renames in early tasks. Below are tasks agents can execute so we “meet in the middle.”

---

## Canonical Layout (Reference)

From the vision; agents must align to this.

```
Platform Runtime Core
├─ Public Works
├─ State Surface
├─ WAL
├─ Intent Registry
├─ Journey Engine
├─ Solution Synthesis Engine
├─ Civic Systems
├─ Experience SDK
├─ Telemetry, Artifacts, Policy, Identity
└─ (no direct registration of “experience surfaces” in core)

Experience Surfaces (clients of runtime)
├─ experience/coexistence
├─ experience/content
├─ experience/operations   (lens into journey engine)
├─ experience/outcomes   (lens into solution synthesis)
├─ experience/control_tower
├─ experience/security
└─ dashboards / portals

Capabilities (what platform CAN DO)
├─ capabilities/content
├─ capabilities/coexistence
├─ capabilities/insights
├─ capabilities/journey_engine
├─ capabilities/solution_synthesis
├─ capabilities/security
└─ capabilities/control_tower

Solutions (packaging)
└─ solutions/insurance_migration, energy_grid_modernization, ...
```

---

## Task 0: Canonical Architecture Doc (Single Source of Truth)

**Owner:** One agent (or human).  
**Branch:** e.g. `cursor/landing-architecture-doc`  
**Conflict risk:** None (additive doc).

**Objective:** Turn [solution_realm_refactoring_vision.md](./solution_realm_refactoring_vision.md) into a single **canonical architecture** document the whole org (and all agents) will use.

**Subtasks:**

1. Create `docs/architecture/CANONICAL_PLATFORM_ARCHITECTURE.md` that includes:
   - The three-way separation: **Capabilities** vs **Experience** vs **Solutions** (with definitions and examples).
   - The correct folder layout above (capabilities, experience, solutions, intents, journeys, realms).
   - Boot phases: Φ1 Infra, Φ2 Config, Φ3 Runtime Graph Construction, Φ4 Experience attachment.
   - Rule: “Service factory registers capabilities, intents, journey engine, solution synthesis, security, control tower — **not** experience surfaces. Experience surfaces attach to runtime as clients.”
   - Civic/experience distinction: Experience Civic System (SDK) vs `/experience/*` product surfaces.
   - One “current state vs target state” subsection mapping existing `symphainy_platform/solutions` and `realms` to the target layout (without changing code yet).

2. Add a “Platform layout” decision to `docs/architecture/` (e.g. ADR or section in the same doc) that future PRs must respect.

**Acceptance criteria:**

- [ ] `docs/architecture/CANONICAL_PLATFORM_ARCHITECTURE.md` exists and is linked from the vision doc.
- [ ] Any agent can read it and know where new code should go (capabilities vs experience vs solutions).
- [ ] No code or renames in this task — documentation only.

---

## Task 1: Experience SDK Contract (Interface Only)

**Owner:** One agent.  
**Branch:** e.g. `cursor/landing-experience-sdk-contract`  
**Conflict risk:** Low (new module / protocol only).

**Prerequisite:** Takeoff has completed Phase 1 of [EXPERIENCE_CIVIC_REFACTOR_PLAN.md](architecture/EXPERIENCE_CIVIC_REFACTOR_PLAN.md) so that `docs/architecture/EXPERIENCE_SDK_CONTRACT.md` exists (or will exist). **Adopt that contract; do not invent a different one.**

**Objective:** Expose the **Experience SDK** as a typed interface so that (a) takeoff can implement it, (b) landing can build experience clients against it, without either side depending on the other’s internals.

**Subtasks:**

1. If `EXPERIENCE_SDK_CONTRACT.md` exists: add a Python protocol or abstract base (e.g. in `symphainy_platform/civic_systems/experience/sdk/` or `symphainy_platform/experience/`) that describes how an “experience surface” interacts with the runtime:
   - `query_state(...)` — read state for a tenant/session/context.
   - `invoke_intent(intent_type, parameters, context)` — submit an intent.
   - `trigger_journey(journey_id, params, context)` — start a journey.

2. If the contract doc does not yet exist: add a minimal `EXPERIENCE_SDK_CONTRACT.md` that lists the four interaction modes (query state, invoke intent, trigger journey, subscribe) with method names and minimal payload shapes, and add the matching protocol/ABC. Coordinate with takeoff so the contract aligns with what the civic system will implement.

**Acceptance criteria:**

- [ ] Protocol/ABC exists and is importable.
- [ ] `EXPERIENCE_SDK_CONTRACT.md` exists and describes the four interaction modes above.
- [ ] No changes to service_factory or boot order in this task.
- [ ] Existing experience/UI code continues to run (contract is additive).

---

## Task 2: Capability Namespace (Additive Layout)

**Owner:** One agent.  
**Branch:** e.g. `cursor/landing-capabilities-namespace`  
**Conflict risk:** Low (new directories only; no move of existing code).

**Objective:** Introduce the **capabilities** namespace so we can gradually map “what the platform can do” into it, without deleting or renaming current `solutions`/`realms` yet.

**Subtasks:**

1. Under `symphainy_platform/`, create directories:
   - `capabilities/content/`
   - `capabilities/coexistence/`
   - `capabilities/insights/`
   - `capabilities/journey_engine/`
   - `capabilities/solution_synthesis/`
   - `capabilities/security/`
   - `capabilities/control_tower/`

2. In each directory, add:
   - `__init__.py`
   - `README.md` (one short paragraph: “This capability is …; MVP exposure is experience/<X>.”)  
   Use the vision doc for the one-line description.

3. Do **not** move or copy existing solution/realm implementation into these dirs yet. This task is layout + READMEs only.

**Acceptance criteria:**

- [ ] All seven capability directories exist with `__init__.py` and README.
- [ ] No imports from existing `symphainy_platform/solutions` or `realms` are changed.
- [ ] No code deleted or moved from current structure.

---

## Task 3: Experience Surfaces Namespace (Additive Layout)

**Owner:** One agent.  
**Branch:** e.g. `cursor/landing-experience-namespace`  
**Conflict risk:** Low (new or clarified layout; avoid overwriting existing experience entrypoints if any).

**Objective:** Make the **experience** folder structure explicit as “product surfaces that attach to runtime,” per the vision.

**Subtasks:**

1. Under `symphainy_platform/experience/` (or repo-level `experience/` if that’s where the vision expects it), ensure or create:
   - `experience/content/`
   - `experience/coexistence/`
   - `experience/operations/`
   - `experience/outcomes/`
   - `experience/control_tower/`
   - `experience/security/`

2. Add a top-level `experience/README.md` that states: “These are platform-native experience compositions built on the Experience Civic SDK. They attach to the runtime; they do not bootstrap it.”

3. Do **not** remove or replace existing UI/frontend entrypoints (e.g. Next.js pillars). This task is layout and documentation only; optional stubs (e.g. empty `__init__.py` or “Coming soon” READMEs) are fine.

**Acceptance criteria:**

- [ ] Experience subdirs exist and are documented as “clients of runtime.”
- [ ] No change to service_factory or boot.
- [ ] Existing frontend or experience entrypoints still work.

---

## Task 4: Boot Phases Doc and Φ3 vs Φ4 Checklist

**Owner:** One agent.  
**Branch:** e.g. `cursor/landing-boot-phases-doc`  
**Conflict risk:** None (doc only).

**Objective:** Document boot phases so that (a) takeoff can implement Φ3 (runtime graph) and Φ4 (experience attachment) in line with the vision, and (b) landing agents don’t register experience in the service factory.

**Subtasks:**

1. Create or update `docs/architecture/BOOT_PHASES.md`:
   - Φ1 — Infra
   - Φ2 — Config
   - Φ3 — Runtime graph: Public Works, Intent registry, Journey engine, Solution synthesis engine, State surface, WAL, Security, Control tower. **No experience surfaces registered here.**
   - Φ4 — Experience attachment: operations UI, outcomes UI, dashboards, portals attach to the runtime (e.g. via Experience SDK).

2. Add a “Service factory registration checklist”: what **must** be registered in Φ3 (capabilities, intents, journey engine, solution synthesis, security, control tower) and what **must not** (individual experience UIs). Experience surfaces “attach” after Φ3.

**Acceptance criteria:**

- [ ] `BOOT_PHASES.md` exists and matches the vision.
- [ ] No code changes to bootstrap or service_factory in this task.
- [ ] Future PRs that register “experience” in service_factory can be rejected by reference to this doc.

---

## Task 5: Journey Engine vs Operations / Solution Synthesis vs Outcomes (Naming ADR)

**Owner:** One agent.  
**Branch:** e.g. `cursor/landing-naming-adr`  
**Conflict risk:** None (doc only).

**Objective:** Lock the naming so “journey” = execution engine, “operations” = experience lens; “solution synthesis” = engine, “outcomes” = experience lens. Prevents confusion when we later map current solutions to capabilities/experience.

**Subtasks:**

1. Add a short ADR (e.g. `docs/architecture/ADR_JOURNEY_OPERATIONS_OUTCOMES_NAMING.md`) that states:
   - **Journey engine** = execution system (DAG, saga, WAL, etc.). Lives under capabilities/journey_engine (or current equivalent until migration).
   - **Operations** = experience surface that observes and interacts with journey execution. Lives under experience/operations.
   - **Solution synthesis engine** = computational generator of outcomes. Lives under capabilities/solution_synthesis.
   - **Outcomes** = experience surface for narrative/outcomes. Lives under experience/outcomes.

2. Include one “Current mapping” line: e.g. “Today, journey_solution / operations_solution map to …; outcomes_solution maps to …” (update to match repo).

**Acceptance criteria:**

- [ ] ADR exists and is linked from the canonical architecture doc.
- [ ] No code renames in this task.

---

## Task 6: Migration Map (Current → Target, No Code Yet)

**Owner:** One agent.  
**Branch:** e.g. `cursor/landing-migration-map`  
**Conflict risk:** None (doc only).

**Objective:** One document that maps every current `symphainy_platform` solution and realm to the target layout (capability + experience + solution packaging). No migrations performed; this is the “recipe” for a later migration phase.

**Subtasks:**

1. Create `docs/architecture/MIGRATION_MAP_CURRENT_TO_TARGET.md`:
   - Table: Current module (e.g. `solutions/content_solution`, `realms/content`) → Target capability (e.g. `capabilities/content`) and target experience (e.g. `experience/content`).
   - For operations/outcomes: current `operations_solution` / `outcomes_solution` → `capabilities/journey_engine` + `experience/operations`, and `capabilities/solution_synthesis` + `experience/outcomes`.
   - Note any “solution packaging” (e.g. future `solutions/insurance_migration`) as a separate column.
   - Add a “Phase” column: Phase A = layout only (done in Tasks 2–3), Phase B = implement Experience SDK (Task 1), Phase C = migrate registration (service_factory), Phase D = move/copy code (later).

**Acceptance criteria:**

- [ ] Every current solution and realm has a target capability and experience in the table.
- [ ] No code or renames in this task.
- [ ] Document is the single reference for “where does X go when we migrate?”

---

## Task 7 (Optional, Higher Risk): Stub “Experience Attach” in Boot

**Owner:** One agent, after Tasks 0–6 are merged.  
**Branch:** e.g. `cursor/landing-experience-attach-stub`  
**Conflict risk:** Medium (touches boot/entrypoint).

**Objective:** After Φ3 runtime graph is built, call a single “attach_experience_surfaces()” (or similar) that, for now, does nothing or only logs. This reserves the Φ4 hook so takeoff can later plug real experience binding there.

**Subtasks:**

1. In the main boot path (e.g. `runtime_main.py` or wherever the runtime graph is built), after “runtime graph ready,” add a documented step: “Φ4 — attach experience surfaces.”
2. Implement it as a no-op or a loop over an empty list of “experience surface” descriptors. Document that real implementations will use the Experience SDK contract (Task 1).
3. Do **not** register any existing UI or solution in service_factory as part of this task.

**Acceptance criteria:**

- [ ] Φ4 step exists in code and is documented in `BOOT_PHASES.md`.
- [ ] Current behavior unchanged (no new registrations, no removed registrations).
- [ ] Tests and platform startup still pass.

---

## Execution Order and “Meet in the Middle”

**Order of work (mandatory):**

1. **Takeoff: Experience Civic refactor first.** Execute [EXPERIENCE_CIVIC_REFACTOR_PLAN.md](architecture/EXPERIENCE_CIVIC_REFACTOR_PLAN.md) Phase 1–2 (contract + alignment, SDK facade + route wiring). Phase 3 (platform_sdk / orchestrator_health) and Phase 4 (Φ4 stub) as needed. This delivers the Experience SDK as the single, named contract and proves the civic system is ready for experience clients.
2. **Landing agents: then run the tasks below.** Start only after the Experience SDK contract exists and the civic system exposes it (or in parallel with Phase 2 if contract is already documented).

**Recommended order for landing agents:**

1. **Task 0** (canonical doc) — do first; reference the refactored Experience SDK and boot phases from takeoff.  
2. **Task 1** (Experience SDK contract) — **adopt** the contract from takeoff: if `EXPERIENCE_SDK_CONTRACT.md` already exists, add the protocol/ABC in code and link to it; do not invent a different contract.  
3. **Tasks 2, 3, 4, 5, 6** — can be parallelized; additive doc/layout and migration map.  
4. **Task 7** — only after 0–6 are in and reviewed; optional (takeoff may already have added Φ4 stub in Phase 4).

**Meet in the middle:**

- **Takeoff** owns: runtime, all civic systems (including Experience Civic System), platform_sdk and orchestrator_health decisions, and the Experience Civic refactor. Delivers the Experience SDK contract and implementation; optionally Φ4 stub.
- **Landing** agents: build capabilities and experiences (Tasks 0–6, optional 7) that **consume** the Experience SDK. They do not change the civic system or runtime contract.
- **Proof:** The holistic refactor of the Experience Civic System (takeoff) proves the two worlds meet; landing’s experience surfaces and capabilities use the same SDK.
- **Merge point:** Shared docs (canonical architecture, boot phases, migration map) + Experience SDK contract (from takeoff) + capabilities/experience layout (from landing). Later “migration” phase moves code per `MIGRATION_MAP_CURRENT_TO_TARGET.md` in small PRs.

---

## Summary for Cursor Agents

- **You may:** Add new directories, READMEs, protocols, and docs. Implement the Experience SDK contract (interface only) and the Φ4 stub if assigned.
- **You may not (in these tasks):** Delete or rename existing `symphainy_platform/solutions` or `realms` modules; remove or change existing service_factory registrations; or break current boot/startup.
- **When in doubt:** Prefer adding over changing; prefer documenting over refactoring; and link to `docs/architecture/CANONICAL_PLATFORM_ARCHITECTURE.md` once it exists.
