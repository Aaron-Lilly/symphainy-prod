# Coexistence Capability

**What it does:** Human-AI collaboration, agent routing, and coordination.

**Core functions:**
- Guide agent orchestration
- Navigation assistance
- Introduction workflows
- Human-AI handoffs
- Liaison coordination

**MVP exposure:** `experience/coexistence`

**Current implementation:** `realms/coexistence/intent_services/`

**Intent types:**
- `initiate_guide_session` — Start guide agent interaction
- `navigate_to_context` — Route user to appropriate context
- `introduce_capability` — Explain platform capabilities

**Layer:** Execution Plane (below SDK boundary) — may access Public Works and State Surface directly.
