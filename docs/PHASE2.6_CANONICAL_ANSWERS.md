# Phase 2.6: Canonical Answers - Backend AGUI Support

**Date:** January 22, 2026  
**Status:** Architectural Decisions Locked In  
**Source:** CTO Architectural Guidance

---

## Summary Table

| Question                                      | Answer                | MVP Choice            |
| --------------------------------------------- | --------------------- | --------------------- |
| Where does AGUI → Intent compilation happen?  | **Frontend**          | ✅ Compile in frontend |
| Does backend need AGUI schema validation?    | **No (Intent only)**  | ❌ Intent validation  |
| Does backend need AGUI state storage?         | **No (session only)** | ✅ Frontend + session  |
| Does backend need AGUI context for execution? | **Absolutely not**    | ✅ Intent self-contained |
| Does backend need AGUI audit trail?           | **Optional, not MVP** | ❌ Intent audit only  |

---

## Detailed Answers

### 1. Where does AGUI → Intent compilation happen?

**✅ Answer: Frontend**

**Principle:**
> **AGUI → Intent compilation belongs at the Experience Boundary.**

**Architectural Rationale:**
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

**Principle:**
> **Backend should never need AGUI to execute — but may validate it if received.**

**Key Insight:**
- AGUI is **not authoritative**
- Intent is authoritative
- Backend validates Intent shape (already implemented)

**Two Valid Models:**

**Model A (Preferred - MVP):**
- Backend **never receives AGUI**
- Backend only receives Intent
- AGUI is frontend/session concern

**Model B (Optional, later):**
- Backend receives AGUI *as metadata*
- Backend validates AGUI schema for:
  - Audit
  - Replay
  - Forensics

**MVP Choice:** ❌ No backend AGUI validation, ✅ Intent validation only

---

### 3. Does backend need AGUI state storage?

**✅ Answer: No (session only)**

**Principle:**
> **AGUI is session-scoped experience state, not platform state.**

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

**Note:** You can always *add* backend persistence later without breaking contracts.

---

### 4. Does backend need AGUI context for execution?

**✅ Answer: Absolutely not**

**Principle:**
> **The backend must not need AGUI.**

**Why This Is Non-Negotiable:**
- AGUI is **experience-specific**
- Backend execution must be:
  - Deterministic
  - Replayable
  - Auditable
  - Headless

If execution needs AGUI, you've leaked UX concerns into the platform core.

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

**Principle:**
> **Audit the decision, not the UI.**

**What Actually Matters:**
- What was requested (Intent)
- What was executed (Execution)
- Why it was executed (Policy Evaluation)
- Under what policy/context (Realm Execution)

AGUI can help explain **user intent evolution**, but it is not the authoritative record.

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

## Implementation Impact

### Frontend (Phase 2.5)
- ✅ AGUI state management (frontend + session)
- ✅ AGUI → Intent compilation (frontend)
- ✅ AGUI schema validation (frontend TypeScript)
- ✅ Intent submission (backend validates Intent only)

### Backend (No Changes Needed)
- ✅ Intent validation (already implemented)
- ✅ Intent execution (already implemented)
- ✅ Self-contained intents (already required)
- ❌ No AGUI dependencies (correct)

---

## Conclusion

**✅ MVP Decision: No backend changes needed**

The backend already supports the required pattern. AGUI is handled entirely in the frontend, maintaining proper separation of concerns.

**Status:** Ready to proceed with Phase 2.5 (Frontend AGUI implementation)
