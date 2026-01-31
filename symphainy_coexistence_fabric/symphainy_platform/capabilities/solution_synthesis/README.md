# Solution Synthesis Capability

**What it does:** Outcome generation — roadmaps, POCs, blueprints, and solution artifacts.

**Core functions:**
- Outcome synthesis and generation
- Roadmap generation
- POC creation and proposals
- Blueprint creation
- Artifact export
- Solution creation workflows

**MVP exposure:** `experience/outcomes` (the "Outcomes" lens into this capability)

**Current implementation:**
- `realms/outcomes/intent_services/`
- `solutions/outcomes_solution/`

**Intent types:**
- `synthesize_outcome` — Generate outcome artifacts
- `generate_roadmap` — Create implementation roadmap
- `create_poc` — Generate proof-of-concept
- `propose_poc` — POC proposal workflow
- `create_blueprint` — Architecture blueprint
- `export_artifact` — Export generated artifacts
- `create_solution` — End-to-end solution generation

**Layer:** Execution Plane (below SDK boundary) — may access Public Works and State Surface directly.

**Note:** "Solution Synthesis" is the capability name; "Outcomes" is the experience lens.
