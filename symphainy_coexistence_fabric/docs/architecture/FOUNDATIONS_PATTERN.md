# Foundations Pattern: Embrace Protocol/Abstraction

**Purpose:** Clarify how foundations fit the platform—and that we **embrace** the evolution to protocol/abstraction for capabilities, with an optional minimal base for orchestrators only.

---

## 1. What Prior Code Had

- **symphainy_platform_old** and **symphainy_source** (archive_v1): Multiple **XFoundationService** classes—**PublicWorksFoundationService**, **CuratorFoundationService**, **AgentFoundationService**, **SmartCityFoundationService**, realm-level **XRealmFoundationService**. All **concrete**; **no shared BaseFoundationService** in the code we have. The “base” was the **naming** (XFoundationService) and **lifecycle** (initialize, optional shutdown), not a Python base class. If a literal base existed, it was in an earlier version.

- **Fabric** copied foundations from platform_old; same structure: PublicWorks, Curator, no shared base.

---

## 2. Embrace Protocol/Abstraction

The platform **naturally evolved** so that:

| Layer | Role | What we use |
|-------|------|-------------|
| **Capability contract** | “What must this capability do?” | **typing.Protocol** (e.g. StateManagementProtocol, FileStorageProtocol) |
| **Capability implementation** | “How does it do it?” | **Abstraction** class that implements the Protocol (e.g. StateManagementAbstraction) |
| **Orchestrator** | “Who wires adapters to abstractions and exposes them?” | **FoundationService** (PublicWorksFoundationService, CuratorFoundationService) — exposes `get_X_abstraction()` returning the Protocol type |

We **embrace** that. The “base” for **capabilities** is the **Protocol**; the “base” for the **orchestrator** is the FoundationService class that holds and exposes them. We do **not** replace protocol/abstraction with a single fat base.

---

## 3. Optional BaseFoundationService (Orchestrators Only)

If we want **type-hint consistency** with other platform bases (BaseSolution, BaseIntentService, etc.), we can add a **minimal BaseFoundationService** (concrete, no ABC, no Protocol) that **PublicWorksFoundationService** and **CuratorFoundationService** inherit from:

- Logger, optional `async initialize() -> bool`, optional config.
- Same discipline: lean, no ballooning; no capability logic in the base.

That would be for the **orchestrator** only. The protocol/abstraction pattern for capabilities stays as-is.

---

## 4. References

- [PLATFORM_BASES_REVIEW.md](./PLATFORM_BASES_REVIEW.md) — foundation section and optional BaseFoundationService.
- [PLATFORM_BASES_DISCIPLINE.md](./PLATFORM_BASES_DISCIPLINE.md) — common pattern for all bases.
