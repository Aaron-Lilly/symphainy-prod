# Platform Evolution Roadmap

**Status:** Active  
**Last Updated:** January 2026  
**Total Duration:** 10 weeks

---

## Overview

This roadmap outlines the complete platform evolution from current state to MVP Showcase Solution.

**Key Principle:** All infrastructure changes via Public Works (adapter swaps), all architecture changes follow the north star, all features build on existing abstractions.

---

## Roadmap Phases

### [Phase 0: Foundation & Assessment](phase_0_foundation.md) (Week 1)
**Goal:** Establish baseline and validate Public Works pattern

- Archive current implementations
- Audit Public Works (what to keep/update)
- Identify tech stack gaps
- Create execution plans

**Deliverables:**
- Archive structure created
- Public Works inventory complete
- Tech stack gaps documented
- Execution plans ready

---

### [Phase 1: Tech Stack Evolution](phase_1_tech_stack.md) (Week 2-3)
**Goal:** Migrate infrastructure through adapter swaps

- Redis Graph → ArangoDB (adapter swap)
- WAL Lists → Streams (adapter enhancement)
- Remove Celery (cleanup)
- Add metrics export (OTEL config)

**Deliverables:**
- All infrastructure migrated
- Public Works pattern validated
- Tech stack ready for scale

---

### [Phase 2: Architecture Enhancements](phase_2_architecture.md) (Week 4-5)
**Goal:** Complete Runtime Execution Engine and Data Brain

- Intent Model
- Execution Context
- Execution Lifecycle Manager
- Transactional Outbox
- Data Brain scaffolding

**Deliverables:**
- Runtime Execution Engine complete
- Data Brain scaffolding complete
- Full execution flow works

---

### [Phase 3: Platform SDK & Experience Plane](phase_3_civic_systems.md) (Week 6-7)
**Goal:** Build Platform SDK and Experience Plane

- Platform SDK (Solution Builder + Realm SDK)
- Experience Plane (separate service)
- Smart City SDK + Primitives
- Agentic SDK

**Deliverables:**
- Platform SDK complete
- Experience Plane complete
- Frontend can submit intents

---

### [Phase 4: Frontend Integration](phase_4_frontend.md) (Week 8)
**Goal:** Refactor frontend to use new architecture

- Experience SDK integration
- Multi-tenancy support
- WebSocket streaming
- Intent-based interactions

**Deliverables:**
- Frontend uses Experience SDK
- Multi-tenancy works
- Real-time updates work

---

### [Phase 5: MVP Solution](phase_5_mvp_solution.md) (Week 9-10)
**Goal:** Build MVP Showcase Solution

- Solution creation
- All pillars work
- Chat interfaces work
- Admin dashboard works

**Deliverables:**
- MVP Showcase Solution deployed
- All use cases work
- Ready for investors/customers

---

## Timeline Summary

| Phase | Duration | Focus | Key Deliverable |
|-------|----------|-------|-----------------|
| Phase 0 | Week 1 | Assessment | Baseline established |
| Phase 1 | Week 2-3 | Tech Stack | Infrastructure migrated |
| Phase 2 | Week 4-5 | Architecture | Runtime + Data Brain complete |
| Phase 3 | Week 6-7 | Platform SDK | SDK + Experience complete |
| Phase 4 | Week 8 | Frontend | Frontend integrated |
| Phase 5 | Week 9-10 | MVP Solution | MVP Showcase deployed |

**Total:** 10 weeks to complete platform evolution

---

## Dependencies

```
Phase 0 (Foundation)
  ↓
Phase 1 (Tech Stack) → Validates Public Works pattern
  ↓
Phase 2 (Architecture) → Builds on Phase 1 infrastructure
  ↓
Phase 3 (Platform SDK) → Builds on Phase 2 Runtime
  ↓
Phase 4 (Frontend) → Builds on Phase 3 Experience
  ↓
Phase 5 (MVP Solution) → Builds on all previous phases
```

---

## Success Criteria

### Phase 0 Success
- ✅ Archive structure created
- ✅ Public Works inventory complete
- ✅ Tech stack gaps documented
- ✅ Execution plans ready

### Phase 1 Success
- ✅ Redis Graph → ArangoDB complete
- ✅ WAL using Streams
- ✅ Celery removed
- ✅ Metrics exported
- ✅ Public Works pattern validated

### Phase 2 Success
- ✅ Runtime Execution Engine complete
- ✅ Data Brain scaffolding complete
- ✅ Full execution flow works
- ✅ All infrastructure via Public Works

### Phase 3 Success
- ✅ Platform SDK complete
- ✅ Experience Plane complete
- ✅ Frontend can submit intents
- ✅ Real-time updates work

### Phase 4 Success
- ✅ Frontend uses Experience SDK
- ✅ Multi-tenancy works
- ✅ All existing features work
- ✅ Tests pass

### Phase 5 Success
- ✅ MVP Showcase Solution deployed
- ✅ All use cases work
- ✅ Multi-tenant isolation verified
- ✅ Ready for investors/customers

---

## Risk Mitigation

1. **Public Works Pattern Validation**
   - Each migration validates the pattern
   - If migration is hard, pattern needs improvement
   - If migrations are easy, pattern is validated

2. **Incremental Delivery**
   - Each phase delivers value
   - Can stop at any phase
   - Can deploy incrementally

3. **Rollback Strategy**
   - All changes via adapters = easy rollback
   - Keep old adapters until new ones validated
   - Can swap back if needed

---

## References

- [Architecture Guide](../architecture/north_star.md)
- [Platform Rules](../PLATFORM_RULES.md)
- [Execution Plans](../execution/00_EXECUTION_INDEX.md)
- [Current State](../current_state/00_CURRENT_STATE_INDEX.md)
