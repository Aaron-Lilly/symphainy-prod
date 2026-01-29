# Probe Design: Discovery, Not Assertion

**Principle:** Probes are **instruments that trace and document how the system actually operates**. They are not tests. By the end of running probes, we must be able to state **with 100% certainty** exactly how the platform operates—not "it works" (60–70% certainty) or "96% of tests pass," but a complete, evidenced map.

---

## Probes vs tests

| | **Probes** | **Tests** |
|---|------------|-----------|
| **Purpose** | Discover and document reality | Assert expected behavior |
| **Output** | Evidence, sequence, contracts, failure modes | Pass / fail |
| **Certainty** | "Here is exactly what happens, in what order, under what conditions" | "This assertion held (or not)" |
| **When** | Hop 1 (Architectural Discovery) | Hop 2 (after convergence, enforcement) |

**We do not use tests to learn how the platform operates.** We use probes to trace entry points, boot order, first request path, config-as-behavior, and order/restart failure modes. The single artifact that probes fill is the **Platform Operation Map** (see below).

---

## Where to start (in order) — from new_testing_mindset.md

### Step 1: Entry & exit points ONLY

- **What:** startup / main.py, service boot order, first request in browser, first websocket connect.
- **Why:** These define what the system really is.
- **Probe task:** Trace startup from process start → first successful browser response. Identify all implicit assumptions.
- **Artifact:** Platform Operation Map §1 (Entry point), §2 (Boot order), §3 (First request path).

### Step 2: Configuration as behavior

- **What:** Every time an env var change breaks things, a container name matters, or an order dependency exists—that’s architecture, not ops.
- **Probe task:** Identify configuration elements that change behavior or stability. Flag them as implicit contracts.
- **Artifact:** Platform Operation Map §4 (Config contracts).

### Step 3: Containers / order / restart as fault amplifiers

- **What:** Things work outside Docker but not inside → missing contracts. Order matters → hidden orchestration. Restart fixes it → state leak.
- **Probe task:** Run probes with different startup orders and restarts. Record Stability/Gravity reports.
- **Artifact:** Stability/Gravity reports; Platform Operation Map §5 (Order/restart failure modes).

---

## The artifact: Platform Operation Map

One document, filled **only** by running probes. When complete, it states with **100% certainty**:

1. **Entry point** — Exact file, function, line. What runs first.
2. **Boot order** — A → B → C → … with evidence (code path and/or runtime trace).
3. **First request path** — What code runs when the first browser request hits (e.g. GET /health or GET /docs).
4. **Config contracts** — Which env vars, ports, or names change behavior or stability; what breaks when they are missing or wrong.
5. **Order/restart failure modes** — What breaks when startup order changes; what “fixes” on restart (and what that implies).

No guesswork. No "we think." Only "we probed and observed."

---

## Probe inventory (Layer 0 only here; full platform in PROBE_LAYER_MAP)

| Probe | Step | What it traces / varies | Output |
|-------|------|-------------------------|--------|
| **probe_01_entry_exit** | 1 | Process start → boot sequence → first HTTP response | Map §1, §2, §3; implicit assumptions list |
| **probe_02_config_behavior** | 2 | Env vars, required vs optional; what fails when unset/wrong | Map §4 (config contracts) |
| **probe_03_order_restart** | 3 | Different startup orders; restart and observe | Stability/Gravity reports; Map §5 |

**Full platform (Foundations, Civic, Realms, Runtime, Solutions, Utilities):** See [PROBE_LAYER_MAP.md](PROBE_LAYER_MAP.md). Probes 04–15 trace Public Works, Curator, Smart City, Agentic, Experience, Artifact Plane, Orchestrator Health, Platform SDK, Realms, Runtime, Solutions, Utilities. Each produces a **Reality Map** so every component has a clearly explainable purpose and we know how it really works.

Probes live in `probes/`. Layer 0 output → `PLATFORM_OPERATION_MAP.md`. Layer 1+ output → `docs/testing/reality_maps/` or equivalent. Run in dependency order (see PROBE_LAYER_MAP).

---

## What we do NOT do (yet)

- Do not fix failures the probes reveal.
- Do not optimize Dockerfiles or standardize env vars yet.
- Do not use test pass rate as a measure of "how the platform operates."
- Do not say "it works" without being able to state exactly how it operates.

---

## Success criterion

**Before probes:** We can say "tests pass" or "it works" with low certainty.  
**After probes:** We can say "The platform operates as follows: entry point is X; boot order is A→B→C; first request path is P; config contracts are C1, C2, …; order/restart failure modes are F1, F2, …" with **100% certainty** (evidenced by probe output).
