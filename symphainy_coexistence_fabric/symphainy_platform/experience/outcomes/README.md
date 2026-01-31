# Outcomes Experience Surface

**What it is:** Outcomes UI — the "lens" into the Solution Synthesis capability.

**What it provides:**
- Roadmap visualization and generation
- POC creation and proposal interface
- Blueprint viewing and export
- Outcome artifact management
- Solution creation workflows

**Capability lens:** `capabilities/solution_synthesis`

**Current implementation:** `solutions/outcomes_solution/`

**SDK operations used:**
- `trigger_journey("roadmap_generation_journey", ...)` — Generate roadmaps
- `invoke_intent("create_poc", ...)` — Create POC
- `invoke_intent("propose_poc", ...)` — POC proposal
- `invoke_intent("create_blueprint", ...)` — Create blueprint
- `invoke_intent("export_artifact", ...)` — Export artifacts
- `query_state(...)` — Outcome/artifact status

**Layer:** Solutions Plane (above SDK boundary) — must use Experience SDK only.

**Note:** "Outcomes" is the experience name; "Solution Synthesis" is the capability it exposes.
