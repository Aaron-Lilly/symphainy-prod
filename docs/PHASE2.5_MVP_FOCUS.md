# Phase 2.5: AGUI Native Integration - MVP Focus

**Date:** January 22, 2026  
**Status:** ✅ Foundation Complete - Ready for MVP Integration

---

## Decision: Defer Agentic SDLC Journey

**Rationale:**
- Agentic SDLC journey (even POC) could be expansive
- Risk of scope creep and moving goalposts
- MVP focus is more important than proof-of-concept journeys
- AGUI foundation is already valuable for MVP use cases

**Impact:**
- ✅ AGUI foundation is complete and ready to use
- ✅ No blocker for MVP work
- ✅ Can use AGUI for simpler, focused MVP use cases
- ✅ Agentic SDLC journey can be added later when MVP is stable

---

## What We Have (Ready for MVP)

### ✅ AGUI Foundation (Complete)
1. **AGUI Schema & Types** - `shared/types/agui.ts`
2. **AGUI State Provider** - Session-scoped state management
3. **AGUI Hooks** - Native platform primitives
4. **Service Layer Integration** - AGUI → Intent compilation
5. **Guide Agent Refactored** - Proposes AGUI mutations

### ✅ MVP-Ready Features
- **Session-scoped state** - AGUI state follows session lifecycle
- **Agent proposal pattern** - Guide Agent proposes, frontend applies
- **Intent compilation** - AGUI → Intent (frontend compilation)
- **State mutations** - Clean mutation API for complex state changes

---

## How to Use AGUI in MVP (Simpler Use Cases)

### Option 1: Use AGUI for Complex Journeys (When Needed)
- File processing workflows
- Multi-step operations
- Complex state transitions
- When direct service calls become unwieldy

### Option 2: Keep It Simple (Default)
- Use direct service layer calls for simple CRUD
- Use AGUI only when complexity warrants it
- Don't force AGUI into every interaction

### Option 3: Incremental Adoption
- Start with direct service calls
- Refactor to AGUI when patterns emerge
- Let complexity guide the decision

---

## MVP Integration Strategy

### Phase 1: Continue with Existing Refactoring (Phases 3-8)
- Complete service layer standardization
- WebSocket consolidation
- State management consolidation
- Error handling standardization
- Routing refactoring

### Phase 2: Use AGUI Where It Makes Sense
- Complex multi-step workflows
- Agent-driven interactions
- State-heavy operations
- When Guide Agent is involved

### Phase 3: Add Agentic SDLC Later (Post-MVP)
- After MVP is stable
- When we have real use cases
- When complexity warrants it
- As a natural evolution, not a requirement

---

## What This Means for MVP

### ✅ No Blocker
- AGUI foundation is complete
- Can use AGUI for MVP features if needed
- Can defer to direct service calls if simpler
- No requirement to implement Agentic SDLC journey

### ✅ Flexibility
- Use AGUI when it helps
- Use direct calls when simpler
- Incremental adoption
- No forced migration

### ✅ Focus
- MVP features first
- Stability over new patterns
- Real use cases over proof-of-concepts
- Ship, then optimize

---

## Updated Plan

### Phase 2.5 Status: ✅ Foundation Complete
- AGUI schema/types ✅
- AGUI state provider ✅
- AGUI hooks ✅
- Service layer integration ✅
- Guide Agent refactored ✅
- **Agentic SDLC Journey: DEFERRED (Post-MVP)**

### Next Steps (MVP Focus)
1. Continue with Phases 3-8 (existing refactoring plan)
2. Use AGUI where it makes sense in MVP features
3. Defer Agentic SDLC journey to post-MVP
4. Focus on stability and shipping

---

## Conclusion

✅ **AGUI Foundation: Complete and MVP-Ready**

The AGUI foundation is solid and ready to use in MVP:
- ✅ No requirement to implement Agentic SDLC journey
- ✅ Can use AGUI for complex use cases when needed
- ✅ Can use direct service calls for simple cases
- ✅ Flexibility to choose the right tool for the job

**Focus:** MVP stability and shipping, not proof-of-concept journeys.
