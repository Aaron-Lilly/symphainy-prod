# Archive v1 - Previous Implementation

**Date Archived:** January 2026  
**Reason:** Platform rebuild following new architecture guide (v2.0)

---

## What Was Archived

This archive contains the previous platform implementation that doesn't follow the new architecture guide.

### Archived Components

- **Runtime** (`runtime_v1/`) - Previous Runtime implementation
  - Needs rebuild per new architecture (Intent Model, Execution Context, Execution Lifecycle Manager)
  - Has scaffolding but doesn't follow architecture guide

- **Smart City** (`smart_city_v1/`) - Previous Smart City implementation
  - Needs rebuild SDK-first (SDK + Primitives separation)
  - Not following new architecture patterns

- **Realms** (`realms_v1/`) - Previous Realms implementation
  - Needs rebuild with Runtime Participation Contract
  - Doesn't use new execution contract

- **Experience** (`experience_v1/`) - Previous Experience implementation
  - Needs rebuild as separate service
  - Not following Experience → Runtime flow

- **Agentic** (`agentic_v1/`) - Previous Agentic implementation
  - Needs rebuild per new architecture
  - Not following agentic patterns

- **main.py** (`main_v1.py`) - Previous main.py
  - 465 lines, too complex
  - Needs clean rebuild (< 100 lines)

---

## Why Archived

These implementations don't follow the new architecture guide:

1. **Runtime** doesn't have:
   - Intent Model
   - Execution Context
   - Execution Lifecycle Manager
   - Transactional Outbox

2. **Smart City** isn't:
   - SDK-first
   - Separated into SDK + Primitives

3. **Realms** don't:
   - Use Runtime Participation Contract
   - Follow new execution semantics

4. **Experience** isn't:
   - A separate service
   - Following Experience → Runtime flow

5. **main.py** is:
   - Too complex (465 lines)
   - Doing too much initialization

---

## Reference Only

**This archive is for reference only, not for reuse.**

New implementations will be built following the architecture guide:
- [Architecture Guide](../docs/architecture/north_star.md)
- [Platform Rules](../docs/PLATFORM_RULES.md)
- [Execution Plans](../docs/execution/00_EXECUTION_INDEX.md)

---

## What We're Keeping

We're **keeping** the Public Works foundation:
- `foundations/public_works/protocols/` - Contracts (keep, may need updates)
- `foundations/public_works/abstractions/` - Business logic (keep, may need updates)
- `foundations/public_works/adapters/` - Technology bindings (keep, will swap some)

**Why:** Public Works pattern validates swappability. Keeping it proves the pattern works.

---

## Migration Strategy

New implementations will:
1. Follow architecture guide strictly
2. Use Public Works abstractions
3. Implement Runtime Participation Contract
4. Be built cleanly (no backwards compatibility)

---

**Archive Date:** January 2026  
**Platform Version:** 2.0 (Breaking Changes)
