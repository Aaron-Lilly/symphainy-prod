# Foundation Plan: Genesis Protocol + Blank-Canvas Hybrid Cloud

**Purpose:** Align the “blank canvas” foundation approach (config acquisition, config contract, pre-boot, init order) with the [Platform Runtime Genesis Protocol](genesis_protocol.md) (PRGP) and hybrid cloud aspiration. Then provide a concrete get-started plan so we build the right foundation without repeating past mistakes.

**Status:** Planning. This doc is the bridge between PRGP (ontological phases, gates) and the concrete specs we must define and implement.

**References:**
- [genesis_protocol.md](genesis_protocol.md) — PRGP phases (Φ0–Φ5), gates (G1–G5), mechanical model (Docker → main.py → runtime_main).
- [PLATFORM_CONTRACT.md](architecture/PLATFORM_CONTRACT.md) — Required infra, config, pre-boot, capability contract.
- [HYBRID_CLOUD_VISION.md](HYBRID_CLOUD_VISION.md) — Option C, three planes, phased evolution.
- [PATH_TO_WORKING_PLATFORM.md](testing/PATH_TO_WORKING_PLATFORM.md) — Roadmap (pre-boot → boot → first request).
- [HOW_WE_RUN_THE_PLATFORM.md](HOW_WE_RUN_THE_PLATFORM.md) — Run modes (runtime on host vs Docker), Genesis alignment, recommended local-dev path.

---

## 1. How the Genesis Protocol Affects the Blank-Canvas Approach

### 1.1 Wider Aperture from PRGP

The genesis protocol reframes startup as **ontological existence**, not “run a script”:

- **Φ0 Void** → **Φ1 Physical Viability** → **Φ2 Runtime Consciousness** → **Φ3 Operational Reality** → **Φ4 Cognitive Activation** → **Φ5 Coherent Existence**
- Each phase has **hard gates** (G1–G5). You don’t enter the next phase until the gate passes.
- **Mechanical mapping:** Docker → Φ1; main.py → Φ2; runtime_main → Φ3; agent boot → Φ4; health/invariants → Φ5.

So the blank-canvas foundation work is not “add a bootstrap module.” It is **defining and implementing what each gate actually requires**, so that:

- **Gate G2 (Enter Φ2)** explicitly includes **config acquisition** (env files, load order, who loads) and **config contract** (canonical shape, keys, provenance). Without that, “Config loads” is underspecified and we get the .env.secrets miss again.
- **Gate G3 (Enter Φ3)** explicitly requires **pre-boot validation** to pass before we run `create_runtime_services()`. So “Public Works connects to backing services” is enforced *before* we build the graph, not as a side effect of building it.
- **Φ3** then has a clear **init order** (Public Works → State Surface → WAL → Intent Registry → …) and **no hidden coupling** (e.g. registry not blocked by Arango).

The genesis protocol also says: **“Multiple runtime instances: each enact the same Genesis Protocol, each converge to the same operational reality.”** So hybrid cloud (Option C) does not change the phases or gates; it only changes *where* Φ1’s “Datastores reachable” is satisfied (e.g. Arango Oasis vs local Arango). Our foundation specs must be **phase- and gate-aware** so that Docker, main.py, and runtime_main each know their responsibility and we can later run the same protocol against managed services.

### 1.2 Where Blank-Canvas Specs Sit in the PRGP

| Blank-canvas artifact | PRGP home | Why |
|------------------------|-----------|-----|
| **Config acquisition spec** | Φ2 / Gate G2 | “Config loads” (G2) must mean: env files loaded in defined order, then canonical config built. So config acquisition is the *first* mechanical step of Φ2 (Runtime Consciousness). |
| **Config contract** | Φ2 / Gate G2 | Defines canonical shape, required/optional keys, mapping from env (and which file) to keys. Part of “configuration truth” (genesis doc: Φ2 creates “configuration truth”). |
| **Pre-boot spec** | Gate G3 entry | We do not enter Φ3 (Operational Reality) until connectivity to all required backing services is verified. Pre-boot is the enforcement of G3 *before* `create_runtime_services()`. |
| **Init-order spec** | Φ3 | Inside Φ3: Public Works, State Surface, WAL, Intent Registry, etc. in deterministic order; no hidden coupling. |
| **Discovery / open questions** | Informs G2 and G3 | “Things we don’t know” and “decisions we need” so that G2 and G3 are well-defined (e.g. which env files, who loads them, is Cobrix required at boot). |
| **Capability contract (refined §9)** | Φ3–Φ5 | What solutions/realms need; split by backing service vs library vs Civic. Informs what must exist by Φ3 vs what is “available when an intent runs.” |

So: **config acquisition and config contract are part of Gate G2.** **Pre-boot is the Gate G3 entry condition.** **Init order is the mechanical content of Φ3.** We do not implement “bootstrap” in isolation; we implement **G2 and G3** in a way that satisfies the genesis protocol and prevents the sins of the past (e.g. env never loaded).

### 1.3 What We Must Not Do

- **Assume “env is already populated.”** Gate G2 must explicitly define how env is populated (which files, order, who loads). If Docker injects env_file, that’s Φ1; if the process loads .env.secrets and config/development.env, that’s the first step of Φ2.
- **Conflate “one config source” with “we read os.getenv.”** The one config source is the **canonical config object** produced after config acquisition + config contract. Public Works and pre-boot consume only that.
- **Enter Φ3 without passing G3.** Pre-boot (connectivity checks) is the gate. If it fails, we never call `create_runtime_services()`.
- **Mix foundation (G2–G3) with capability (§9)** without clarifying “backing service vs library vs Civic.” Cobrix (container) and pandas (library) are different layers; the contract and gates should reflect that.

---

## 2. Alignment: PRGP Phases and Gates vs Foundation Specs

| Phase | Gate | What must be true | Foundation spec / artifact |
|-------|------|-------------------|----------------------------|
| Φ0 | — | Void | — |
| Φ1 | G1 | Containers start; ports bind; secrets load (if Docker provides env_file); networks; volumes | Docker/compose and infra docs. “Secrets load” = either Docker injects env files or we document that Φ2 must load them. |
| Φ2 | G2 | Config loads; logging initialized; DI resolves; no circular imports; no runtime exceptions | **Config acquisition spec** (which env files, order, who loads). **Config contract** (canonical shape, keys, env→key mapping). Code: one designated “load env files then build canonical config” before any other platform code. |
| Φ3 | G3 | Public Works connects to backing services; State Surface reachable; WAL writes succeed; schema registry; Intent registry; runtime graph fully constructed | **Pre-boot spec** (what we check, order, fail-fast message). Pre-boot runs *before* create_runtime_services; it uses only canonical config. **Init-order spec** (order inside Public Works / service_factory; no hidden coupling). |
| Φ4 | G4 | Background workers; event loops; agents; websockets; schedulers | Out of scope for this foundation plan; follows after Φ3 is stable. |
| Φ5 | G5 | Health green; invariants; write→read→reconcile | Out of scope for this foundation plan; follows after Φ3. |

**Scope of this plan:** We define and implement **G2** (config acquisition + config contract) and **G3** (pre-boot + init order) so that Φ2 and Φ3 are deterministic and the platform “comes into existence” deliberately. Φ4 and Φ5 remain important but are not the focus of “foundation to prevent past sins.”

---

## 3. Get-Started Plan: Order of Work

Execute in this order so each step has a clear gate and we don’t build on sand.

### Step 0: Discovery and Open Questions (Do First)

**Goal:** Make explicit what we don’t know and what we must decide so G2 and G3 are well-defined.

**Output:** **[STEP0_FOUNDATION_OPEN_QUESTIONS.md](STEP0_FOUNDATION_OPEN_QUESTIONS.md)** — each open question answered from: (1) Genesis Protocol / north star, (2) how the platform actually behaves today, (3) recommended answer. Phase 0 ends with a list of **recommended answers for CTO review/validation**; after CTO sign-off, proceed to Step 1–2.

**Actions:**
1. **Create the Step 0 doc** with the four-part structure per question (open question; answer from genesis/north star; answer from actual behavior; recommended answer).
2. **Answer by inspection or decision:** Walk the codebase and deployment; document “how the platform actually behaves today” and then recommend an answer.
3. **Capability vs foundation:** Clarify which dependencies are “required at boot” (G3) vs “required when an intent runs” vs “library” vs “Civic.”
4. **List for CTO review:** At the end of Phase 0, list recommended answers that need CTO review or validation before locking Steps 1–2.

**Gate:** Step 0 doc exists; CTO has reviewed the “Phase 0: Recommended Answers for CTO Review” list; no more implicit assumptions about “env is there.”

---

### Step 1: Config Acquisition Spec (Define)

**Goal:** Formalize how the process gets its configuration so “Config loads” (G2) is unambiguous.

**Actions:**
1. **Document** (in a **Config Acquisition** section or small spec):
   - **Env files:** Names, paths (e.g. repo root `.env.secrets`, `config/development.env`, `.env`), and load order.
   - **Precedence:** e.g. later file overrides earlier, or “secrets override non-secrets.”
   - **Who loads:** Single designated place (e.g. “first line of Φ2 in main.py” or “bootstrap step 0”) that runs before any other platform config read. No “maybe some other import already loaded them.”
   - **When:** Before building canonical config; before any code that reads config for platform infra.
2. **Clarify Φ1 vs Φ2:** If Docker/compose injects env via `env_file`, say so (Φ1). If the process must load files itself, say so (Φ2 first step). So we know who is responsible in each deployment mode.
3. **Do not implement yet.** This step is “define the contract.”

**Output:** Written **Config Acquisition** spec → [architecture/CONFIG_ACQUISITION_SPEC.md](architecture/CONFIG_ACQUISITION_SPEC.md). Reference it from genesis_protocol (G2) and from PLATFORM_CONTRACT.

**Gate:** Anyone reading the spec can say “so when the process starts, config comes from X, Y, Z in this order.”

---

### Step 2: Config Contract Spec (Define)

**Goal:** Define the canonical config shape and provenance so “one config source” is precise.

**Actions:**
1. **Document** (in a **Config Contract** section or small spec):
   - **Canonical shape:** One structure (e.g. dict or typed object) with required and optional keys; nesting where adapters expect it (e.g. `redis`, `consul`, `duckdb` blocks).
   - **Mapping:** For each key, which env var(s) and which file(s) feed it. Include naming variants (ARANGO_USER / ARANGO_USERNAME, ARANGO_DB / ARANGO_DATABASE, ARANGO_PASS / ARANGO_ROOT_PASSWORD).
   - **Rules:** e.g. blank password valid; which keys may be absent in which environments.
2. **Align with PLATFORM_CONTRACT §3 and §4:** Required keys for Redis, Arango, Consul, Supabase, GCS, Meilisearch, DuckDB; optional keys for EDI, Cobrix, Kreuzberg, LLM, etc.
3. **Do not implement yet.** This step is “define the contract.”

**Output:** Written **Config Contract** spec → [architecture/CONFIG_CONTRACT_SPEC.md](architecture/CONFIG_CONTRACT_SPEC.md). Reference it from G2 and from PLATFORM_CONTRACT §4.

**Gate:** We have a single definition of “the” platform config. Public Works and pre-boot will consume only this.

---

### Step 3: Pre-Boot Spec (Define)

**Goal:** Define what Gate G3 checks so we never enter Φ3 with missing or unreachable backing services.

**Actions:**
1. **Document** (in a **Pre-Boot** section or small spec):
   - **Scope:** Which backing services are checked (per PLATFORM_CONTRACT §3: Redis, Arango, Consul, Supabase, GCS, Meilisearch, DuckDB).
   - **Order:** e.g. data plane first (Redis, Arango, Supabase, GCS, Meilisearch, DuckDB), then control (Consul), or as in HYBRID_CLOUD_VISION (data → control → execution).
   - **Input:** Pre-boot uses **only** the canonical config (output of config contract). No env reads inside pre-boot.
   - **Failure:** Single, clear message per service; process exits; no partial init.
   - **Placement:** Runs in the process entry path (e.g. runtime_main or main.py) **before** `create_runtime_services()`.
2. **Reference G3:** “Gate G3 (Enter Φ3) is satisfied only after pre-boot passes.”

**Output:** Written **Pre-Boot** spec → [architecture/PRE_BOOT_SPEC.md](architecture/PRE_BOOT_SPEC.md). Reference it from genesis_protocol (G3) and from PLATFORM_CONTRACT §5.

**Gate:** We know exactly what “Public Works connects to backing services” means mechanically: run these checks with this config; if any fail, we do not enter Φ3.

---

### Step 4: Init-Order Spec (Define)

**Goal:** Document the deterministic order inside Φ3 so there is no hidden coupling.

**Actions:**
1. **Document** (in an **Init Order** section or small spec, or extend PLATFORM_CONTRACT §6):
   - **Sequence:** Public Works (adapters then abstractions) → State Surface → WAL → Intent Registry → … (match current service_factory and runtime_services).
   - **No hidden coupling:** e.g. registry_abstraction must not depend on Arango; if Arango fails, pre-boot already failed so we never reach partial init. If we ever decouple (e.g. create registry even when Arango fails), document it.
   - **Public Works contract:** Receives only canonical config; does not read env or config_helper; produces adapters/abstractions in this order.
2. **Reference Φ3:** “This is the mechanical content of Φ3 — Runtime Graph Construction.”

**Output:** Written **Init Order** spec → [architecture/INIT_ORDER_SPEC.md](architecture/INIT_ORDER_SPEC.md). Reference it from genesis_protocol (Φ3) and from PLATFORM_CONTRACT §6.

**Gate:** We have a single definition of “how the runtime graph is built.” No “continuing anyway” with missing abstractions.

---

### Step 5: Implement G2 (Config Acquisition + Config Contract)

**Goal:** Code that enacts the config acquisition spec and config contract so G2 passes deterministically.

**Actions:**
1. **Implement config acquisition:** In the designated place (e.g. first step of “bootstrap” or main.py before anything else), load env files in the specified order (e.g. .env.secrets, config/development.env, .env) from the specified paths (e.g. repo root). Use a single function or small module; no scattering of load_dotenv.
2. **Implement config contract:** One function that builds the canonical config from the environment (after acquisition). Output is the single dict/object defined in the config contract spec. Include all required keys and nested blocks (redis, consul, duckdb, etc.) and naming variants (ARANGO_USER, ARANGO_DB, ARANGO_PASS).
3. **Wire entry point:** Ensure the process entry (main.py or runtime_main) calls “load env files” then “build canonical config” before any other platform code that reads config. So G2 “Config loads” is literally “we ran acquisition then contract.”
4. **Test:** With only .env.secrets (or config/development.env) and no env vars set in the shell, does the canonical config contain the expected values? This would have caught the .env.secrets miss.

**Output:** Working G2 implementation. Gate G2 passes when “config loads” means “acquisition ran + canonical config built.”

---

### Step 6: Implement G3 (Pre-Boot + Init Order)

**Goal:** Code that enacts the pre-boot spec and respects init order so G3 passes before Φ3 and Φ3 is deterministic.

**Actions:**
1. **Implement pre-boot:** One function that takes the canonical config and runs connectivity/readiness checks for Redis, Arango, Consul, Supabase, GCS, Meilisearch, DuckDB (per pre-boot spec). No Public Works or adapters; minimal clients. On first failure: clear message, exit. Place it in the entry path **after** canonical config is built and **before** `create_runtime_services(config)`.
2. **Pass config only:** `create_runtime_services(canonical_config)`. Public Works (and downstream) receive only this config; remove or bypass any internal get_env_contract() / config_helper for platform infra so there is a single path from env to config (acquisition → contract → graph).
3. **Init order:** Already in service_factory; ensure it matches the init-order spec. If “continuing anyway” exists when Public Works init fails, remove it or make it impossible (pre-boot guarantees backing services, so Public Works init should succeed when G3 passed).
4. **Test:** With one backing service down, does pre-boot exit with a clear message and do we never call create_runtime_services?

**Output:** Working G3 enforcement and Φ3 construction. Gate G3 passes when “pre-boot passed”; then Φ3 runs with canonical config only.

---

### Step 7: Refine Capability Contract (§9) and Document Phase Boundaries

**Goal:** Clarify “foundation vs capability” and “backing service vs library vs Civic” so we don’t conflate Cobrix (container) with pandas (library) and so Φ3 vs Φ4/Φ5 boundaries are clear.

**Actions:**
1. **Refine PLATFORM_CONTRACT §9** (or a companion doc): Group requirements by:
   - **Backing services** (Redis, Arango, Consul, Supabase, GCS, Meilisearch, DuckDB; later Cobrix, LLM endpoints): require config + connectivity at G3 or “when intent runs.”
   - **Libraries** (pandas, openpyxl, PyYAML): require importable at G2 or first use; no connectivity check.
   - **Civic surfaces** (Artifact Plane, Telemetry): require injection or exposure via Public Works / Runtime; document who provides them.
2. **Document phase boundaries:** What “must exist by Φ3” vs “must exist by Φ4” vs “required when an intent runs.” So we know what pre-boot must check (G3) vs what we validate later.
3. **Optional:** Add a “Discovery backlog” or “Contract open questions” section that references the list from Step 0 and is updated as we resolve items.

**Output:** Refined capability contract and clear phase boundaries. No implementation required in this step beyond docs.

---

## 4. Summary: What We Create and In What Order

| Order | What | Type | PRGP hook |
|-------|------|------|-----------|
| 0 | Discovery / open questions | Doc (living list) | Informs G2, G3 |
| 1 | Config acquisition spec | Doc | G2 |
| 2 | Config contract spec | Doc | G2 |
| 3 | Pre-boot spec | Doc | G3 |
| 4 | Init-order spec | Doc | Φ3 |
| 5 | Implement G2 (acquisition + contract) | Code | G2 |
| 6 | Implement G3 (pre-boot + init) | Code | G3, Φ3 |
| 7 | Refine §9 + phase boundaries | Doc | Φ3–Φ5 |

**Principle:** Define the gates and contracts first (Steps 0–4), then implement (Steps 5–6), then refine capability and phase boundaries (Step 7). This order prevents “we built bootstrap but forgot to define where config comes from.”

---

## 5. How This Plan Relates to Existing Docs

- **genesis_protocol.md:** This plan **implements** G2 and G3 and makes Φ2 and Φ3 deterministic. The genesis protocol gives the phases and gates; this plan gives the concrete specs and implementation order.
- **PLATFORM_CONTRACT.md:** Config acquisition and config contract extend §4 (one config source); pre-boot and init order align with §5 and §6. We may add a “Config acquisition” subsection and reference this plan.
- **HYBRID_CLOUD_VISION.md:** Unchanged. Option C (managed services) still means “same protocol, different endpoints”; G2 and G3 stay the same.
- **PATH_TO_WORKING_PLATFORM.md:** Step 0 (infra) and Step 1 (boot to first request) are now explicitly “G2 passes then G3 passes then Φ3 runs.” We can reference this plan from there.
- **Current bootstrap code** (symphainy_platform/bootstrap/): Once this plan is executed, that code should be **reviewed and refactored** to match the specs (config acquisition first, then config contract, then pre-boot, then create_runtime_services). The existing bootstrap is a draft; the specs from Steps 1–4 are the source of truth.

---

## 6. Next Step to Get Started

**Steps 0–7 complete.** Discovery (Step 0) through Refine §9 (Step 7) are done. G2 and G3 are implemented: config acquisition and canonical config in `symphainy_platform/bootstrap/`; pre-boot order (Data Plane then Consul) and fail-fast; Public Works uses only canonical config; init fails fast if Public Works init fails; §9.9 Phase Boundaries and enforcement checklist updated. **Next:** Run runtime (e.g. `python runtime_main.py` with env or `.env.secrets`) to verify boot; add probes/tests as needed.
