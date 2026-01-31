# Control Tower Capability

**What it does:** Platform introspection, governance, observability, and administration.

**Core functions:**
- Platform monitoring and health checks
- Solution composition and management
- Developer documentation access
- Governance and policy enforcement
- Observability and metrics

**MVP exposure:** `experience/control_tower`

**Current implementation:**
- `realms/control_tower/intent_services/`
- `solutions/control_tower/`

**Intent types:**
- `monitor_platform` — Platform health and status
- `compose_solution` — Solution composition
- `manage_solution` — Solution lifecycle management
- `get_developer_docs` — Documentation access
- `observe_metrics` — Platform observability

**Layer:** Execution Plane (below SDK boundary) — may access Public Works and State Surface directly.
