# Coexistence Experience Surface

**What it is:** Landing page, guide agent, and human-AI collaboration interface.

**What it provides:**
- Platform landing page
- Guide agent chat interface
- Navigation assistance
- Introduction workflows
- Liaison agent coordination

**Capability lens:** `capabilities/coexistence`

**Current implementation:** `solutions/coexistence/`

**SDK operations used:**
- `invoke_intent("initiate_guide_session", ...)` — Start guide agent
- `invoke_intent("navigate_to_context", ...)` — Navigation routing
- `trigger_journey("introduction_journey", ...)` — Intro workflow
- `query_state(...)` — Session and context state

**Layer:** Solutions Plane (above SDK boundary) — must use Experience SDK only.
