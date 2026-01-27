# Runtime Execution Engine

**Status:** Rebuild in Progress  
**Phase:** Phase 2 (Architecture Enhancements)

---

## Purpose

Runtime is the **single execution authority** for the platform.

**Key Principle:** If Runtime cannot see it, it did not happen.

---

## Responsibilities

Runtime owns:
- Intent acceptance and validation
- Execution lifecycle
- Session & tenant context
- Write-ahead log (WAL)
- Saga orchestration
- Retries & failure recovery
- Deterministic replay
- State transitions
- Runtime-native data cognition (Data Brain)

---

## What Will Be Built (Phase 2)

1. **Intent Model** - Formal intent schema
2. **Execution Context** - Runtime context for domain services
3. **Execution Lifecycle Manager** - Orchestrates full execution flow
4. **WAL Integration** - Redis Streams (from Phase 1)
5. **Saga Coordinator** - Enhanced with transactional outbox
6. **Data Brain** - Runtime-native data cognition scaffolding

---

## Architecture

Runtime follows the architecture guide:
- [Architecture Guide](../../docs/architecture/north_star.md)
- [Platform Rules](../../docs/PLATFORM_RULES.md)

---

## References

- [Phase 2 Execution Plan](../../docs/execution/phase_2_execution_plan.md) - Detailed build plan
- [Architecture Guide](../../docs/architecture/north_star.md) - Section 2.1 Runtime
