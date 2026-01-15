# Current State Index

**Last Updated:** January 2026  
**Status:** Baseline Assessment

---

## Overview

This directory documents the current state of the platform before rebuild.

**Key Principle:** We're doing a clean rebuild. Current state is documented for reference, not for reuse.

---

## Current State Documents

### Inventories

- [Adapter Inventory](adapter_inventory.md) - All adapters (what exists, what to keep/update)
- [Abstraction Inventory](abstraction_inventory.md) - All abstractions (what exists, what to keep/update)
- [Protocol Inventory](protocol_inventory.md) - All protocols (what exists, what to keep/update)

### Assessments

- [Platform Assessment](platform_assessment.md) - Current platform state (what exists, what's missing)
- [Tech Stack Gaps](tech_stack_gaps.md) - What's missing for 350k policies and new architecture
- [Frontend Assessment](frontend_assessment.md) - Current frontend state (what exists, what needs refactoring)

### Audits

- [Public Works Audit](public_works_audit.md) - Comprehensive audit of adapters, abstractions, protocols
- [Tech Stack Gap Analysis](tech_stack_gap_analysis.md) - Technology gaps and recommendations
- [Celery Audit](celery_audit.md) - Celery usage audit (remove or integrate)

---

## What We're Keeping

### Public Works Foundation
- ✅ **Protocols** - Contract definitions (keep, may need updates)
- ✅ **Abstractions** - Business logic layer (keep, may need updates)
- ✅ **Adapters** - Technology bindings (keep, will swap some)

**Why:** Public Works pattern validates swappability. Keeping it proves the pattern works.

### Infrastructure Setup
- ✅ `docker-compose.yml` - Container orchestration (keep, update)
- ✅ `config/` - Configuration management (keep)
- ✅ `utilities/` - Shared utilities (keep)
- ✅ `pyproject.toml`, `requirements.txt` - Dependencies (keep, update)

---

## What We're Archiving

### Current Implementations
- 📦 Runtime - Previous implementation (rebuild cleanly)
- 📦 Smart City - Previous implementation (rebuild SDK-first)
- 📦 Realms - Previous implementation (rebuild with Runtime Participation Contract)
- 📦 Experience - Previous implementation (rebuild as separate service)
- 📦 Agentic - Previous implementation (rebuild per new architecture)
- 📦 main.py - Previous main.py (465 lines, rebuild < 100 lines)

**Why:** These don't follow the new architecture guide. Rebuild cleanly.

---

## What We're Building New

### Runtime Execution Engine
- ❌ Intent Model (new)
- ❌ Execution Context (new)
- ❌ Execution Lifecycle Manager (new)
- ❌ Transactional Outbox (new)
- ⚠️ WAL (exists, needs refactor to Streams)
- ⚠️ Saga Coordinator (exists, needs enhancement)

### Data Brain
- ❌ Data Brain scaffolding (new)
- ❌ Data reference registration (new)
- ❌ Provenance tracking (new)
- ❌ Virtual query interface (new)

### Platform SDK
- ❌ Solution Builder (new)
- ❌ Realm SDK (new)
- ❌ Civic System Composition (new)

### Experience Plane
- ❌ Experience SDK (new)
- ❌ Experience Service (new, separate service)
- ❌ WebSocket streaming (new)

---

## Tech Stack Status

| Component | Current | Target | Status |
|-----------|---------|--------|--------|
| **Event Bus** | Redis Streams | Redis Streams | ✅ Good |
| **Graph Database** | Redis Graph | ArangoDB | ⚠️ Needs migration |
| **WAL** | Redis Lists | Redis Streams | ⚠️ Needs refactor |
| **Hot State** | Redis | Redis | ✅ Good |
| **Cold State** | None | ArangoDB/Supabase | ❌ Needs implementation |
| **File Storage** | GCS + Supabase | GCS + Supabase | ✅ Good |
| **Auth/Tenancy** | Supabase | Supabase | ✅ Good |
| **Semantic Data** | ArangoDB | ArangoDB | ✅ Good |
| **Lineage** | Supabase | Supabase | ✅ Good |
| **Service Discovery** | Consul | Consul | ✅ Good |
| **Observability** | OTEL + Tempo | OTEL + Tempo + Prometheus | ⚠️ Needs metrics |
| **Task Queue** | Celery (unclear) | Runtime + Saga | ⚠️ Needs removal/integration |
| **API Gateway** | Traefik | Traefik | ✅ Good |

---

## Gaps Summary

### Critical Gaps
1. **Redis Graph → ArangoDB** - Migration needed
2. **WAL Scalability** - Lists → Streams needed
3. **Cold State** - Hot/cold pattern needed
4. **Transactional Outbox** - Saga reliability needed

### Medium Gaps
5. **Metrics Export** - Prometheus needed
6. **Celery** - Remove or integrate

### Low Gaps
7. **Event Store Database** - Consider for long-term

---

## Next Steps

1. Complete Phase 0 assessment
2. Create detailed execution plans
3. Start Phase 1 (Tech Stack Evolution)

---

## References

- [Architecture Guide](../architecture/north_star.md)
- [Platform Rules](../PLATFORM_RULES.md)
- [Roadmap](../roadmap/00_ROADMAP_INDEX.md)
- [Execution Plans](../execution/00_EXECUTION_INDEX.md)
