# AGUI Architecture Review & Recommendation

## Document Review: `AGUIinthefrontend.md`

### Core Proposal

The document proposes a **fundamental architectural shift**:

1. **Frontend as Reference Implementation** (not SDK consumer)
   - Frontend defines the interaction contract
   - Experience SDK follows the frontend, not leads it

2. **AGUI as First-Class Primitive**
   - New "Experience State Layer" for AGUI state
   - Hooks: `useAGUIState()`, `useJourneyStep()`, `useAGUIValidator()`
   - AGUI state persists in session

3. **Agent Role Change**
   - Guide Agent → **proposes AGUI changes** (doesn't execute)
   - Chat → **AGUI mutation + explanation UI**
   - Removes non-determinism at UI layer

4. **Capability Calls → Intent Submission**
   - ❌ `parseFile()` → ✅ `updateAGUI()` + `submitIntent()`
   - ❌ `analyzeData()` → ✅ `updateAGUI()` + `submitIntent()`
   - Frontend stops calling capabilities directly

5. **Pillar Pages → AGUI Views**
   - Pages render AGUI steps
   - Same UI, different contract

## Assessment: Is This "Too Clever"?

### ✅ **Strong Arguments FOR**

1. **Aligns with Existing Patterns**
   - Matches "agentic forward" pattern (agent reasons, services execute)
   - Matches Session Boundary pattern (state-driven, not action-driven)
   - Matches Intent submission pattern (already using `submitIntent`)

2. **Solves Real Problems**
   - Removes non-determinism from UI layer
   - Creates clean separation: agents plan, platform executes
   - Makes frontend deterministic and auditable

3. **Strategic Value**
   - Frontend becomes the "reference implementation"
   - Experience SDK follows proven patterns
   - External clients get stable contract

4. **Timing**
   - We're in breaking change phase
   - Service layer refactoring is happening
   - Now is the time to make architectural shifts

### ⚠️ **Concerns / Risks**

1. **Scope Creep**
   - This is a major architectural change
   - Could derail Phase 2 (service layer standardization)
   - Might be premature optimization

2. **Complexity**
   - Adds new abstraction layer (AGUI State Layer)
   - More moving parts
   - Learning curve for team

3. **Current State**
   - We're already using `submitIntent` in some places
   - Guide Agent might already be proposing vs executing?
   - Need to audit current implementation

4. **MVP Risk**
   - Document says "don't break MVP demos"
   - But this is a fundamental shift
   - Could break existing functionality

## Recommendation: **Hybrid Approach** ✅

### Phase 2.5: AGUI Foundation (Incremental)

**Don't rebuild everything, but lay the foundation:**

1. **Create AGUI State Layer (Minimal)**
   - Add `useAGUIState()` hook
   - Store AGUI state in session (via SessionBoundaryProvider)
   - Keep it simple - just state management for now

2. **Refactor Guide Agent (Incremental)**
   - Keep current functionality working
   - Add AGUI proposal pattern alongside existing pattern
   - Gradually shift from execution → proposal

3. **Update One Journey (Agentic SDLC)**
   - As document suggests: implement AGUI for one journey end-to-end
   - Use as proof of concept
   - Learn from it before expanding

4. **Keep Service Layer Work**
   - Continue Phase 2 (service layer standardization)
   - Service layer can support both patterns initially
   - Gradually shift to AGUI + Intent pattern

### What We Have vs What We Need

**Current State:**
- ✅ `AGUIEventProvider` - sends events
- ✅ `GuideAgentProvider` - manages guide agent
- ✅ `submitIntent()` - already exists
- ✅ Session state management

**What's Missing:**
- ❌ AGUI state management layer
- ❌ `useAGUIState()` hook
- ❌ AGUI schema validation
- ❌ Journey step enforcement
- ❌ Pattern: AGUI mutation → Intent submission

**What We Archived (Phase 1):**
- Session providers (not AGUI-related)
- Auth providers (not AGUI-related)
- No AGUI-specific code was archived

## Implementation Strategy

### Option A: Full AGUI Integration (Risky)
- Implement full AGUI State Layer now
- Refactor all journeys to AGUI
- High risk, high reward
- **Recommendation: ❌ Too risky for current phase**

### Option B: Hybrid Approach (Recommended) ✅
- Add AGUI foundation (hooks, state layer)
- Keep existing patterns working
- Implement one journey (Agentic SDLC) as proof of concept
- Gradually expand
- **Recommendation: ✅ Balanced approach**

### Option C: Defer (Conservative)
- Finish Phase 2 (service layer)
- Revisit AGUI in Phase 3+
- **Recommendation: ⚠️ Might miss the "hall pass" window**

## Final Recommendation

**Go with Option B (Hybrid Approach):**

1. **Add AGUI Foundation** (this phase)
   - Create `useAGUIState()` hook
   - Add AGUI state to session
   - Keep it minimal

2. **Refactor Guide Agent** (incremental)
   - Add AGUI proposal pattern
   - Keep existing functionality
   - Gradually shift

3. **Implement One Journey** (proof of concept)
   - Agentic SDLC as suggested
   - Learn from it
   - Validate the pattern

4. **Continue Service Layer** (parallel)
   - Don't stop Phase 2
   - Service layer supports both patterns
   - Gradually shift to AGUI + Intent

**Why This Works:**
- ✅ Lays foundation without breaking everything
- ✅ Validates pattern before full commitment
- ✅ Doesn't derail Phase 2
- ✅ Takes advantage of "breaking change" window
- ✅ Can always expand later

**What to Avoid:**
- ❌ Rebuilding everything at once
- ❌ Breaking existing functionality
- ❌ Premature optimization
- ❌ Scope creep

## Questions to Answer

Before proceeding, we should answer:

1. **Current Guide Agent Behavior**
   - Does it execute actions or propose changes?
   - How does it interact with capabilities?
   - What's the current flow?

2. **Intent Submission Pattern**
   - Where are we using `submitIntent()`?
   - Are we already doing AGUI → Intent in some places?
   - What's working vs what's not?

3. **AGUI Schema**
   - Do we have an AGUI schema defined?
   - What does AGUI state look like?
   - How does it map to journeys?

4. **Journey Definitions**
   - What journeys exist?
   - Which one should be "Agentic SDLC"?
   - How are journeys currently defined?

## Next Steps

1. **Audit Current State**
   - Review Guide Agent implementation
   - Review intent submission usage
   - Review capability calls

2. **Design AGUI Foundation**
   - Define AGUI state structure
   - Design `useAGUIState()` hook
   - Plan integration with SessionBoundaryProvider

3. **Implement Incrementally**
   - Add foundation
   - Refactor one journey
   - Learn and iterate
