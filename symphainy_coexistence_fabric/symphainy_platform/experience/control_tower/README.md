# Control Tower Experience Surface

**What it is:** Admin dashboard for platform monitoring, solution management, and governance.

**What it provides:**
- Platform health monitoring
- Solution composition interface
- Solution lifecycle management
- Developer documentation access
- Observability dashboards

**Capability lens:** `capabilities/control_tower`

**Current implementation:** `solutions/control_tower/`

**SDK operations used:**
- `invoke_intent("monitor_platform", ...)` — Platform health
- `invoke_intent("compose_solution", ...)` — Solution composition
- `invoke_intent("manage_solution", ...)` — Solution management
- `invoke_intent("get_developer_docs", ...)` — Documentation
- `query_state(...)` — Platform/solution status

**Layer:** Solutions Plane (above SDK boundary) — must use Experience SDK only.
