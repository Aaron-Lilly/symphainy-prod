# Experience SDK Adoption (Task 1)

**Status:** Adopted  
**Date:** January 29, 2026  
**Owner:** Team B (Landing)

---

## Contract Reference

**Contract Document:** [EXPERIENCE_SDK_CONTRACT.md](EXPERIENCE_SDK_CONTRACT.md)  
**Implementation:** `symphainy_platform/civic_systems/experience/sdk/experience_sdk.py`

---

## Adoption Verification

### ✅ Protocol Compliance

The `ExperienceSDKProtocol` in the SDK module defines all four contract operations:

| Contract Operation | Protocol Method | Implementation |
|-------------------|-----------------|----------------|
| query_state | `query_state(session_id, tenant_id?, execution_id?)` | ✅ Implemented |
| invoke_intent | `invoke_intent(intent_type, parameters, tenant_id, session_id, solution_id?, metadata?)` | ✅ Implemented |
| trigger_journey | `trigger_journey(journey_id, parameters, tenant_id, session_id, solution_id?, metadata?)` | ✅ Implemented |
| subscribe | `subscribe(execution_id, tenant_id)` | ✅ Implemented |

### ✅ Contract Match

| Contract Requirement | Status |
|---------------------|--------|
| `query_state` returns session state + optional execution status | ✅ Matches |
| `invoke_intent` returns execution_id, status, created_at | ✅ Matches |
| `trigger_journey` is alias for invoke_intent with compose_journey | ✅ Matches |
| `subscribe` yields execution updates (polling until stream available) | ✅ Matches |

### ✅ SDK Exports

The SDK module exports:
- `ExperienceSDK` — Concrete implementation
- `ExperienceSDKProtocol` — Protocol for type checking
- `RuntimeClient` — Underlying HTTP client (internal)

**Import path:** `symphainy_platform.civic_systems.experience.sdk`

---

## Hard Invariant Compliance

Per [PLATFORM_VISION_RECONCILIATION.md](../PLATFORM_VISION_RECONCILIATION.md) §4:

> No solution, agent, MCP server, or experience may directly access runtime internals, civic systems, or infrastructure.

**Experience surfaces MUST use:**
- `ExperienceSDK.query_state()` — NOT direct Runtime HTTP calls
- `ExperienceSDK.invoke_intent()` — NOT direct RuntimeClient
- `ExperienceSDK.trigger_journey()` — NOT direct journey engine access
- `ExperienceSDK.subscribe()` — NOT direct state surface access

---

## What Team B (Landing) Adopts

1. **We consume the SDK** — All experience surfaces we build use `ExperienceSDK` or `ExperienceSDKProtocol`
2. **We do not modify the SDK** — Takeoff owns the implementation
3. **We do not bypass the SDK** — No direct RuntimeClient, no direct state surface, no direct infrastructure

---

## Files Reviewed

| File | Status |
|------|--------|
| `docs/architecture/EXPERIENCE_SDK_CONTRACT.md` | ✅ Exists, documents all four operations |
| `symphainy_platform/civic_systems/experience/sdk/experience_sdk.py` | ✅ Protocol + Implementation present |
| `symphainy_platform/civic_systems/experience/sdk/__init__.py` | ✅ Exports ExperienceSDK, ExperienceSDKProtocol |

---

## Acceptance Criteria (Task 1)

- [x] Protocol/ABC exists and is importable
- [x] `EXPERIENCE_SDK_CONTRACT.md` exists and describes the four interaction modes
- [x] No changes to service_factory or boot order
- [x] Existing experience/UI code continues to run (contract is additive)

---

**Conclusion:** The Experience SDK contract delivered by Takeoff is complete and compliant. Team B (Landing) adopts this contract for all experience surface implementations.
