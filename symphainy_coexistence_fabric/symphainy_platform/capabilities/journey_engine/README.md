# Journey Engine Capability

**What it does:** Workflow/SOP orchestration, saga execution, and journey management.

**Core functions:**
- Journey composition and execution
- Workflow management (create, execute, monitor)
- SOP generation and management
- Process optimization
- Coexistence analysis for workflows
- DAG execution with WAL persistence

**MVP exposure:** `experience/operations` (the "Operations" lens into this capability)

**Current implementation:** 
- `realms/operations/intent_services/`
- `solutions/journey_solution/`
- `solutions/operations_solution/`

**Intent types:**
- `compose_journey` — Start a multi-step journey
- `create_workflow` — Define a new workflow
- `generate_sop` — Create standard operating procedure
- `optimize_process` — Process improvement analysis
- `analyze_coexistence` — Workflow collaboration analysis

**Layer:** Execution Plane (below SDK boundary) — may access Public Works and State Surface directly.

**Note:** "Journey Engine" is the capability name; "Operations" is the experience lens.
