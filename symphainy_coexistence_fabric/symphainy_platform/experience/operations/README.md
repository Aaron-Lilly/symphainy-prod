# Operations Experience Surface

**What it is:** Operations UI — the "lens" into the Journey Engine capability.

**What it provides:**
- Workflow management dashboard
- SOP viewing and management
- Process optimization interface
- Journey execution monitoring
- Coexistence analysis views

**Capability lens:** `capabilities/journey_engine`

**Current implementation:** 
- `solutions/operations_solution/`
- `solutions/journey_solution/`

**SDK operations used:**
- `trigger_journey("workflow_management_journey", ...)` — Manage workflows
- `invoke_intent("generate_sop", ...)` — Generate SOPs
- `invoke_intent("optimize_process", ...)` — Process optimization
- `query_state(...)` — Workflow/journey status
- `subscribe(execution_id, ...)` — Follow journey progress

**Layer:** Solutions Plane (above SDK boundary) — must use Experience SDK only.

**Note:** "Operations" is the experience name; "Journey Engine" is the capability it exposes.
