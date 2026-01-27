# Phase 2.5: AGUI Native Integration - Detailed Plan

**Date:** January 22, 2026  
**Status:** Ready to Execute  
**Approach:** Native Integration - AGUI becomes part of platform "language"

---

## Philosophy

> **AGUI is not a feature we're adding. It's the native interaction model for our platform.**

As we refactor components (Phases 3-8), we integrate AGUI patterns where they make sense, making it the natural way to express user intent and platform state.

---

## Core Principles

1. **AGUI is First-Class** - Like `useSessionBoundary()`, AGUI hooks are native primitives
2. **Integrated, Not Additive** - AGUI patterns integrated as we refactor, not added separately
3. **Judgment-Based** - Use AGUI where it makes sense (complex journeys), not everywhere
4. **Backward Compatible** - Existing patterns work, AGUI enhances them
5. **Session-Scoped** - AGUI state follows session lifecycle

---

## Implementation Tasks

### 1. Create AGUI State Layer (Native Foundation)

**Location:** `shared/state/AGUIStateProvider.tsx`

**Responsibilities:**
- Store AGUI state per session
- Enforce allowed journey steps
- Validate AGUI schema
- Persist AGUI in session state
- Clear AGUI state on session invalidation

**AGUI Schema Structure:**
```typescript
interface AGUIState {
  journey: {
    id: string;
    name: string;
    current_step: string;
    steps: JourneyStep[];
  };
  inputs: {
    artifacts: Artifact[];
    parameters: Record<string, any>;
  };
  workflows: Workflow[];
  outputs: {
    artifacts: Artifact[];
    results: Record<string, any>;
  };
  metadata: {
    created_at: string;
    updated_at: string;
    session_id: string;
  };
}
```

**Integration:**
- AGUI state stored in `SessionBoundaryProvider` session state
- AGUI state cleared when session becomes `Invalid`
- AGUI state persisted in session storage (client-side)

---

### 2. Create AGUI Hooks (Native Platform Language)

**Location:** `shared/hooks/useAGUIState.ts`, `shared/hooks/useJourneyStep.ts`, etc.

**Hooks:**
- `useAGUIState()` - Main AGUI state hook (like `useSessionBoundary()`)
- `useJourneyStep()` - Current journey step from AGUI state
- `useAGUIValidator()` - Schema validation
- `useAGUIMutation()` - Update AGUI state (triggers intent compilation)

**Usage Pattern:**
```typescript
// Native platform language
const { state: aguiState, updateState, submitIntent } = useAGUIState();
const currentStep = useJourneyStep();
const isValid = useAGUIValidator(aguiState);
```

---

### 3. Integrate AGUI into Service Layer (Native Pattern)

**Location:** `shared/services/ServiceLayerAPI.ts`, `shared/hooks/useServiceLayerAPI.ts`

**New Functions:**
- `updateAGUI(aguiMutation: AGUIMutation)` - Primary way to mutate platform state
- `compileIntentFromAGUI(aguiState: AGUIState)` - Compiles AGUI → Intent (frontend compilation)
- `submitIntentFromAGUI(aguiState: AGUIState)` - Compiles AGUI → Intent and submits

**Pattern:**
```typescript
// Native pattern
const { updateAGUI, compileIntentFromAGUI, submitIntentFromAGUI } = useServiceLayerAPI();

// Update AGUI state
await updateAGUI({
  inputs: { artifacts: [newArtifact] }
});

// Compile AGUI → Intent (frontend compilation)
const intent = await compileIntentFromAGUI(aguiState);

// Or compile and submit in one call
await submitIntentFromAGUI(aguiState);
```

**Architectural Principle:**
> **Frontend owns experience semantics (AGUI → Intent compilation). Backend owns execution semantics (Intent validation → Execution).**

**Service Layer Preference:**
- Service layer **prefers** AGUI pattern
- Falls back to direct intent for legacy
- AGUI → Intent compilation happens in **frontend** (ServiceLayerAPI)
- Backend validates Intent shape only (already implemented)

---

### 4. Refactor Guide Agent (Native AGUI Pattern)

**Location:** `shared/agui/GuideAgentProvider.tsx`

**Changes:**
- Guide Agent **proposes AGUI changes** (doesn't execute)
- Chat becomes **AGUI mutation + explanation UI**
- Agent responses include `agui_mutation` field
- Frontend applies AGUI mutations, then submits intents
- Removes non-determinism at UI layer

**Agent Response Format:**
```typescript
interface AgentResponse {
  message: string; // Explanation
  agui_mutation?: AGUIMutation; // Proposed state change
  reasoning?: string; // Why this mutation
}
```

**Frontend Flow:**
1. User sends message
2. Agent proposes AGUI mutation
3. Frontend applies mutation (updates AGUI state)
4. Frontend compiles AGUI → Intent
5. Frontend submits intent
6. Frontend displays explanation + state change

---

### 5. Integrate AGUI into Component Refactoring (As We Go)

**Strategy:** As we refactor components (Phases 3-8), use AGUI where it makes sense

**Integration Points:**

#### ✅ Use AGUI For:
- **Complex Multi-Step Journeys** - Agentic SDLC, Content Processing
- **State That Needs Validation** - Journey steps, artifact states
- **Agent-Driven Workflows** - Guide Agent interactions
- **Workflow Orchestration** - Multi-step processes
- **Journey Navigation** - Step transitions

#### ❌ Don't Use AGUI For:
- **Simple CRUD Operations** - Direct service calls (for now)
- **One-Off Actions** - Simple button clicks
- **UI State** - Component-local state
- **Non-Journey State** - Auth, session (already handled)

**Examples:**

**File Upload (Simple CRUD):**
```typescript
// ❌ Don't use AGUI
const { uploadFile } = useFileAPI();
await uploadFile(file);

// ✅ Keep direct service call
```

**Content Processing Journey (Complex):**
```typescript
// ✅ Use AGUI
const { updateAGUI } = useAGUIState();
await updateAGUI({
  inputs: { artifacts: [uploadedFile] },
  journey: { step: 'parsing' }
});
await submitIntentFromAGUI(aguiState);
```

---

### 6. Implement One Journey End-to-End (Proof of Concept)

**Journey:** Agentic SDLC

**Why This Journey:**
- Net-new (no legacy UX debt)
- Exercises every layer
- Becomes flagship pattern
- Validates AGUI approach

**Implementation:**
1. Define AGUI schema for Agentic SDLC
2. Create AGUI views for each step
3. Guide Agent proposes AGUI mutations
4. Frontend applies mutations
5. Frontend compiles AGUI → Intent
6. Frontend submits intent
7. Frontend tracks execution status
8. Frontend updates AGUI state with results

**Success:**
- Full AGUI → Intent → Execution flow working
- Pattern validated
- Ready to expand to other journeys

---

## Integration with Ongoing Refactoring

### Phase 3: WebSocket Consolidation
- WebSocket follows AGUI state (if journey requires real-time updates)
- Agent responses include AGUI mutations

### Phase 4: Session-First Component Refactoring
- AGUI state follows session lifecycle
- Components check AGUI state, not just auth

### Phase 5: State Management Consolidation
- AGUI state in PlatformStateProvider (or separate AGUI provider)
- AGUI state cleared on session invalidation

### Phase 6: Error Handling Standardization
- AGUI validation errors → `AGUIError` signal
- AGUI compilation errors → `IntentError` signal

### Phase 7: Routing Refactoring
- Routes reflect AGUI journey state
- Navigation updates AGUI state

### Phase 8: AGUI Expansion
- All journeys use AGUI pattern
- Remove direct capability calls
- Full AGUI → Intent flow

---

## Success Criteria

- ✅ `useAGUIState()` hook exists and works (first-class primitive)
- ✅ AGUI state persists in session (session-scoped)
- ✅ Service layer supports AGUI mutations (`updateAGUI()`)
- ✅ Guide Agent proposes AGUI changes (not direct execution)
- ✅ One journey (Agentic SDLC) uses AGUI end-to-end
- ✅ AGUI integrated into component refactoring (as we go)
- ✅ AGUI is **native** to platform, not an add-on
- ✅ Existing functionality still works (backward compatible)
- ✅ Pattern validated before expanding

---

## Next Steps

1. **Create AGUI State Provider** - Foundation
2. **Create AGUI Hooks** - Native primitives
3. **Integrate into Service Layer** - Native pattern
4. **Refactor Guide Agent** - AGUI proposal pattern
5. **Implement Agentic SDLC** - Proof of concept
6. **Integrate into Component Refactoring** - As we go (Phases 3-8)

---

## Notes

- AGUI is **native**, not an add-on
- Use judgment - not everything needs AGUI
- Backward compatible - existing patterns work
- Integrated approach - AGUI patterns as we refactor
- Foundation first, expansion after validation
