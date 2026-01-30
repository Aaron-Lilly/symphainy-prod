# Experience Surfaces

**Status:** Canonical (January 2026)  
**Purpose:** Platform-native experience compositions built on the Experience SDK.

---

## What Are Experience Surfaces?

Experience surfaces are **clients of the runtime** that attach via the Experience SDK.
They do **not** bootstrap the runtime — they consume it.

**Key rule:** Experience surfaces interact with capabilities **only** through the Experience SDK.

---

## Experience Surfaces

| Surface | Capability Lens | Description |
|---------|-----------------|-------------|
| `content/` | Content | Content pillar UI |
| `coexistence/` | Coexistence | Landing page, guide agent, liaison agents |
| `operations/` | Journey Engine | Operations UI — workflow/SOP management |
| `outcomes/` | Solution Synthesis | Outcomes UI — roadmaps, POCs, blueprints |
| `control_tower/` | Control Tower | Admin dashboard, platform monitoring |
| `security/` | Security | Login, registration, account management |

---

## Experience SDK Contract

Experience surfaces use the **Experience SDK** exclusively:

| Operation | Purpose |
|-----------|---------|
| `query_state(session_id, tenant_id?, execution_id?)` | Get session state and execution status |
| `invoke_intent(intent_type, parameters, ...)` | Submit an intent |
| `trigger_journey(journey_id, parameters, ...)` | Start a journey |
| `subscribe(execution_id, tenant_id)` | Follow execution progress |

**Import:** `from symphainy_platform.civic_systems.experience.sdk import ExperienceSDK, ExperienceSDKProtocol`

See: [EXPERIENCE_SDK_CONTRACT.md](../../docs/architecture/EXPERIENCE_SDK_CONTRACT.md)

---

## Hard Platform Invariant

> **No solution, agent, MCP server, or experience may directly access runtime internals, civic systems, or infrastructure. All access must flow through the Experience SDK.**

Experience surfaces are **above** the SDK boundary.

**Forbidden:**
- Direct RuntimeClient calls
- Direct state surface access
- Direct Public Works access
- Direct infrastructure access (Redis, Arango, GCS, etc.)

---

## Boot Phase

Experience surfaces attach in **Φ4** (Experience Attachment).

They do **not** register in service_factory (Φ3). They attach to the runtime as SDK clients after the runtime graph is ready.

---

## What Experience Does

✅ Submit intents via SDK  
✅ Query state via SDK  
✅ Trigger journeys via SDK  
✅ Subscribe to execution updates via SDK  
✅ Render UI / user interactions

---

## What Experience Doesn't Do

❌ Call runtime internals directly  
❌ Access civic systems directly  
❌ Access Public Works or infrastructure  
❌ Execute business logic  
❌ Own state  
❌ Register in service_factory

---

## References

- [CANONICAL_PLATFORM_ARCHITECTURE.md](../../docs/architecture/CANONICAL_PLATFORM_ARCHITECTURE.md)
- [EXPERIENCE_SDK_CONTRACT.md](../../docs/architecture/EXPERIENCE_SDK_CONTRACT.md)
- [EXPERIENCE_SDK_ADOPTION.md](../../docs/architecture/EXPERIENCE_SDK_ADOPTION.md)
- [BOOT_PHASES.md](../../docs/architecture/BOOT_PHASES.md)
