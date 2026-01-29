# Stability & Gravity Report

**Artifact Type:** Architectural Stability & Gravity Report  
**Scope:** Civic agents — Guide Agent → Liaison handoff (param contract mismatch)  
**Epoch:** 2026-01-29

---

## A. What Was Probed

- **Change introduced:** None. Discovery probe: Civic layer agents tests.
- **Trigger:** `pytest tests/3d/agents/ -v` (Civic Systems layer probe).
- **Expected impact (in human terms):** Tests that call Guide Agent journey’s liaison routing should pass if params match the journey’s contract.

---

## B. Observed Behavior

- **What broke:** `test_route_to_liaison_with_context` (in `tests/3d/agents/test_guide_agent.py`) failed with `ValueError: target_pillar is required`.
- **Root cause:** **Parameter name mismatch.**  
  - **Test** passes `params={"pillar_type": "content", "conversation_history": [...], "user_query": "..."}`.  
  - **Journey** (`GuideAgentJourney._route_to_liaison_agent`) expects `params.get("target_pillar")` and raises if missing.  
  - So: test uses `pillar_type`; implementation expects `target_pillar`. Same semantic, different key.
- **Where symptoms appeared:** pytest (3d agents).
- **Time to failure:** Immediate (at call to `_route_to_liaison_agent`).

---

## C. Stability Signals

- **Did unrelated components break?** No. Only this test path failed on this contract.
- **Did restarting "fix" it temporarily?** No.
- **Did the failure move when we changed order of startup?** N/A.
- **Did configuration changes have outsized effects?** No. Pure param-name contract drift.

---

## D. Gravity Signals

- **Did logic migrate back into a specific service/module?** No. Param naming was never aligned between test author and journey author.
- **Did agents need extra context to compensate?** N/A.
- **Did responsibilities blur across layers?** Slightly: “who owns the param names” for liaison routing is unclear—guide_agent (pillar_type) vs journey (target_pillar) vs intent service (target_pillar in route_to_liaison_agent_service).
- **Did fixes require touching many files?** Fix is local: either (a) test passes `target_pillar` instead of `pillar_type`, or (b) journey accepts both / maps `pillar_type` → `target_pillar`. One file or two.

---

## E. Hypotheses (Do NOT Resolve)

- **Suspected unstable boundary:** **Agent–journey param contract.** Guide agent and GuideAgentJourney both implement “route to liaison”; param names diverged (pillar_type vs target_pillar). Intent service `route_to_liaison_agent_service` uses `target_pillar`; test was written against a different mental model (pillar_type).
- **Suspected missing contract:** **Liaison routing params:** A single documented param set (e.g. `target_pillar` required; optional `chat_session_id`, `routing_reason`, `context_to_share`) used by journey, intent service, and all callers (tests, API, agent).
- **Suspected premature abstraction:** No.

*No fixes here. Only hypotheses.*

---

## F. Classification

- [ ] Collapsing abstraction
- [x] Leaky boundary (builder vs platform — param naming not codified)
- [ ] Stable seam
- [ ] Unknown / needs more probes

---

## G. Recommendation

- **Align and document:** Choose canonical param name (`target_pillar` is already used by intent service and journey). Update test (and any other callers) to pass `target_pillar`. Add a one-line contract note to journey or to a shared liaison-routing contract doc so future probes/callers use the same key.
- **Probe:** Add or keep a probe that calls `_route_to_liaison_agent` with only `target_pillar` (and optionally other contract params) so this contract is regression-tested.

---

## H. Resolution (2026-01-29)

- **Fixed:** Test `test_route_to_liaison_with_context` updated to pass `target_pillar` (and optional `routing_reason`, `context_to_share`) instead of `pillar_type`; assertions tightened to `success` and `liaison_agent_activation` artifact.
- **Documented:** Liaison routing params table added to `docs/journey_contracts/coexistence_solution/journey_coexistence_guide_agent.md` (canonical param `target_pillar`; no `pillar_type`).
- **Probe:** `test_route_to_liaison_requires_target_pillar` already added; all 4 liaison handoff tests pass.
