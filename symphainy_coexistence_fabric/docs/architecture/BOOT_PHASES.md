# Boot Phases (Φ1–Φ4)

**Purpose:** North star for startup. After Φ3, the **Experience SDK surface is available**. Φ4 is when experience surfaces attach to that SDK.

**References:** [INIT_ORDER_SPEC.md](INIT_ORDER_SPEC.md) (Φ3 mechanical content), [EXPERIENCE_SDK_CONTRACT.md](EXPERIENCE_SDK_CONTRACT.md), [solution_realm_refactoring_vision.md](../solution_realm_refactoring_vision.md).

---

## Phase Summary

| Phase | Name | Outcome |
|-------|------|---------|
| **Φ1** | Infra | Backing services reachable (Redis, Arango, Consul, Supabase, GCS, Meilisearch, DuckDB). |
| **Φ2** | Config | Canonical config acquired; no env reads inside Public Works for platform infra. |
| **Φ3** | Runtime Graph Construction | Public Works, StateSurface, WAL, IntentRegistry, ExecutionLifecycleManager built. **Experience SDK surface is available** (Runtime API and/or Experience service exposes it). |
| **Φ4** | Experience attachment | Experience surfaces attach to the SDK (Operations UI, Outcomes UI, dashboards, portals). No-op stub acceptable until surfaces are bound. |

---

## Φ3 → SDK Ready

After Φ3 (runtime graph built and `create_runtime_services()` complete):

- The **Experience SDK surface is available**: Experience service can call Runtime (session, intent, execution status), and the contract in [EXPERIENCE_SDK_CONTRACT.md](EXPERIENCE_SDK_CONTRACT.md) is the single surface experience surfaces use.
- Startup succeeds when the runtime graph is built and the Experience service can serve SDK operations (query_state, invoke_intent, trigger_journey, subscribe).

---

## Φ4 — Attach Experience Surfaces

Φ4 is the step where **experience surfaces** (UIs, dashboards, portals) attach to the runtime as **clients** of the Experience SDK. They do not bootstrap the runtime; they:

- Attach to runtime
- Query state via SDK
- Invoke intents / trigger journeys via SDK
- Subscribe to execution updates via SDK

In code, after “runtime graph ready” / “Experience app created,” a documented step can run: **attach_experience_surfaces(sdk, config)** — no-op or log only. Real implementations will register or bind experience UIs to the SDK here.

---

---

## Service Factory Registration Checklist

This checklist defines what **must** and **must not** be registered during Φ3 (Runtime Graph Construction).

### ✅ MUST Register in Φ3 (service_factory)

| Component | Purpose | Registration |
|-----------|---------|--------------|
| **Public Works** | Infrastructure abstractions | `public_works = PublicWorksFoundationService(config)` |
| **State Surface** | Centralized state management | `state_surface = StateSurface(public_works)` |
| **WAL** | Write-ahead log for durability | `wal = WAL(public_works)` |
| **Intent Registry** | Intent → handler mapping | `intent_registry = IntentRegistry()` |
| **Execution Lifecycle Manager** | Execution management | `execution_manager = ExecutionLifecycleManager(...)` |
| **Capability Intent Services** | Atomic capability implementations | `intent_registry.register(intent_type, handler)` |
| **Journey Engine** | Workflow/saga execution | Part of capabilities registration |
| **Solution Synthesis Engine** | Outcome generation | Part of capabilities registration |
| **Security** | Auth/authz capabilities | Part of capabilities registration |
| **Control Tower** | Platform governance | Part of capabilities registration |
| **Artifact Registry** | Artifact management | `artifact_registry = ArtifactRegistry(...)` |

### ❌ MUST NOT Register in Φ3

| Component | Why Not | Where It Goes |
|-----------|---------|---------------|
| **Operations UI** | Experience surface (SDK client) | Φ4 — attach via SDK |
| **Outcomes UI** | Experience surface (SDK client) | Φ4 — attach via SDK |
| **Content Pillar UI** | Experience surface (SDK client) | Φ4 — attach via SDK |
| **Coexistence UI** | Experience surface (SDK client) | Φ4 — attach via SDK |
| **Control Tower UI** | Experience surface (SDK client) | Φ4 — attach via SDK |
| **Security UI** | Experience surface (SDK client) | Φ4 — attach via SDK |
| **Dashboards / Portals** | Experience surfaces | Φ4 — attach via SDK |

### PR Review Rule

PRs that register **experience surfaces** in service_factory should be **rejected**. Reference this document:

> "Experience surfaces attach in Φ4 as SDK clients. They do not register in service_factory (Φ3). See BOOT_PHASES.md."

---

## Φ3 vs Φ4 Decision Tree

```
Is this component a capability implementation?
├── YES → Register in Φ3 (service_factory)
│   Examples: intent services, journey engine, state surface, WAL
│
└── NO → Does it consume capabilities via Experience SDK?
    ├── YES → Attach in Φ4 (SDK client)
    │   Examples: Operations UI, Outcomes UI, dashboards
    │
    └── NO → Is it infrastructure?
        ├── YES → Φ1 (Infra) or Φ2 (Config)
        │
        └── NO → Review architecture; may not belong in boot
```

---

## Summary

- **Φ3 completion** = Runtime graph built + Experience SDK surface available.
- **Φ4** = Attach experience surfaces to that SDK (clients of the runtime, not part of boot core).
- **Rule:** Capabilities register in Φ3; experiences attach in Φ4.
