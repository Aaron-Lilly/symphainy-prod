# Phase 2.6: Backend AGUI Support Assessment

**Date:** January 22, 2026  
**Status:** Assessment Complete - No Backend Changes Needed for MVP  
**Decision:** Frontend compiles AGUI → Intent, Backend validates Intent only

---

## Executive Summary

**✅ MVP Decision: No backend changes needed**

The backend already supports the required pattern:
- ✅ Intent validation (already implemented)
- ✅ Intent execution (already implemented)
- ✅ Self-contained intents (already required)

AGUI is handled entirely in the frontend:
- ✅ AGUI → Intent compilation (frontend)
- ✅ AGUI state storage (frontend + session)
- ✅ AGUI schema validation (frontend TypeScript types)

---

## Canonical Answers (Architectural Decisions)

### 1. Where does AGUI → Intent compilation happen?

**✅ Answer: Frontend**

**Rationale:**
- Frontend owns **experience semantics** (AGUI)
- Backend owns **execution semantics** (Intent)
- This keeps agents + UX flexible without destabilizing execution

**Pattern:**
```
Frontend:
AGUI State
  → IntentCompiler (ServiceLayerAPI)
      → Intent (fully specified, typed)

Backend:
IntentValidator (Experience Service)
  → Realm Orchestrator (Runtime Service)
```

**MVP Choice:** ✅ Compile in frontend, backend validates Intent shape only

---

### 2. Does backend need AGUI schema validation?

**✅ Answer: No (Intent validation only)**

**Rationale:**
- AGUI is **not authoritative**, Intent is authoritative
- Backend should never need AGUI to execute
- Backend validates Intent shape (already implemented)

**Optional (Later):**
- Backend may validate AGUI if stored/audited (for replay, forensics)
- Not required for execution

**MVP Choice:** ❌ No backend AGUI validation, Intent validation only

---

### 3. Does backend need AGUI state storage?

**✅ Answer: No (session only)**

**Rationale:**
- AGUI is **session-scoped experience state**, not platform state
- Frontend + session state provides UX continuity and reload/recovery

**Storage Responsibilities:**

| Layer         | Stores AGUI?  | Why                    |
| ------------- | ------------- | ---------------------- |
| Frontend      | ✅             | UX continuity          |
| Session State | ✅             | Reloads / recovery     |
| Backend DB    | ❌ (MVP)       | Not execution-critical |

**When Backend Storage Makes Sense (Future):**
- Cross-device resume
- Multi-user collaboration
- Historical replay
- Regulatory audit

**MVP Choice:** ✅ Frontend + session state, ❌ No backend persistence

---

### 4. Does backend need AGUI context for execution?

**✅ Answer: Absolutely not**

**Rationale:**
- Backend execution must be:
  - Deterministic
  - Replayable
  - Auditable
  - Headless
- AGUI is experience-specific, not execution-critical
- If execution needs AGUI, you've leaked UX concerns into platform core

**Correct Contract:**
> **Intent must be fully self-contained.**

That means:
- All required parameters
- All references resolved
- No implied UI state

**MVP Choice:** ✅ Intent is self-contained, ❌ No AGUI dependency in backend

---

### 5. Does backend need AGUI audit trail?

**✅ Answer: Optional, not MVP**

**Rationale:**
- Audit the **decision** (Intent), not the UI (AGUI)
- AGUI can help explain user intent evolution, but not authoritative

**Correct Audit Stack:**

| Layer             | Audit                        | MVP Required? |
| ----------------- | ---------------------------- | ------------- |
| AGUI              | Optional (experience replay) | ❌ No          |
| Intent            | ✅ Required                   | ✅ Yes         |
| Policy Evaluation | ✅ Required                   | ✅ Yes         |
| Realm Execution   | ✅ Required                   | ✅ Yes         |

**Best Practice:**
- Store AGUI snapshots **only if** you want:
  - Experience replay
  - Debugging UX issues
  - Demonstrations

**MVP Choice:** ❌ No AGUI audit trail, ✅ Intent + execution audit only

---

## Backend Assessment Results

### Current Backend Support

**✅ Experience Service:**
- ✅ Intent submission endpoint (`POST /api/intent/submit`)
- ✅ Intent validation (via Traffic Cop SDK)
- ✅ Intent forwarding to Runtime Service
- ✅ No AGUI dependencies (correct)

**✅ Runtime Service:**
- ✅ Intent execution
- ✅ Self-contained intents (required)
- ✅ No AGUI dependencies (correct)

**✅ Architecture:**
- ✅ Frontend → Experience Service → Runtime Service flow
- ✅ Intent is contract between layers
- ✅ No experience semantics in backend (correct)

---

### Required Backend Changes

**✅ MVP: None**

The backend already supports the required pattern:
- Intent validation (already implemented)
- Intent execution (already implemented)
- Self-contained intents (already required)

**Future (Optional, Not MVP):**
- Backend may store AGUI snapshots for experience replay (if needed)
- Backend may validate AGUI schema if stored/audited (for forensics)
- Backend may support AGUI endpoints for cross-device sync (if needed)

---

## Implementation Impact

### Frontend Responsibilities (Phase 2.5)

1. **AGUI State Management**
   - Store AGUI state in frontend + session
   - Clear AGUI state on session invalidation
   - AGUI state is session-scoped

2. **AGUI → Intent Compilation**
   - Compile AGUI state to Intent in frontend
   - IntentCompiler in ServiceLayerAPI
   - Fully specify Intent (all parameters, all references)

3. **AGUI Schema Validation**
   - TypeScript types for AGUI schema
   - Frontend validation before compilation
   - AGUI validation errors → user feedback

4. **Intent Submission**
   - Submit compiled Intent to Experience Service
   - Backend validates Intent shape (already implemented)
   - Backend executes Intent (already implemented)

### Backend Responsibilities (No Changes Needed)

1. **Intent Validation**
   - ✅ Already implemented (Traffic Cop SDK)
   - ✅ Validates Intent shape
   - ✅ Validates session/tenant

2. **Intent Execution**
   - ✅ Already implemented (Runtime Service)
   - ✅ Self-contained intents
   - ✅ No AGUI dependencies

3. **Audit Trail**
   - ✅ Intent audit (already implemented)
   - ✅ Execution audit (already implemented)
   - ❌ AGUI audit (not needed for MVP)

---

## Architectural Principle

> **AGUI is how humans think. Intent is what the platform promises. Execution is what actually happens.**

The architecture correctly keeps these separate:
- **Frontend:** AGUI (experience semantics) → Intent compilation
- **Backend:** Intent validation → Execution (execution semantics)

This separation is **architecturally sound** and enables:
- ✅ Flexible UX without destabilizing execution
- ✅ Deterministic, replayable execution
- ✅ Headless execution (no UI dependencies)
- ✅ Clear separation of concerns

---

## Success Criteria

- ✅ Backend audit complete
- ✅ Canonical answers documented
- ✅ Decision: No backend changes needed for MVP
- ✅ Frontend responsibilities clear
- ✅ Backend responsibilities confirmed (already implemented)
- ✅ Architectural principle validated

---

## Next Steps

1. **Proceed with Phase 2.5** (Frontend AGUI implementation)
   - No backend blockers
   - Frontend compiles AGUI → Intent
   - Backend validates Intent (already works)

2. **Future Considerations** (Optional, Not MVP)
   - AGUI snapshot storage (if experience replay needed)
   - AGUI schema validation in backend (if stored/audited)
   - Cross-device AGUI sync (if multi-device needed)

---

## Conclusion

**✅ Phase 2.6 Assessment: Complete**

**Result:** No backend changes needed for MVP. The backend already supports the required pattern (Intent validation and execution). AGUI is handled entirely in the frontend, maintaining proper separation of concerns.

**Status:** Ready to proceed with Phase 2.5 (Frontend AGUI implementation)
