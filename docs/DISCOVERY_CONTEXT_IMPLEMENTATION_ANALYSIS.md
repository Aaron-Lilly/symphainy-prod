# Discovery Context Implementation Analysis

**Date:** January 2026  
**Status:** ✅ **PATTERN APPROVED - READY FOR IMPLEMENTATION**

---

## Executive Summary

**The suggested pattern is architecturally sound and resolves the circular reference problem elegantly.**

**Key Insight:**
> **Agents may *discover* runtime context, but they may not *own* it.**

**This pattern:**
- ✅ Aligns with "Agents reason, systems decide" principle
- ✅ Enables conversational discovery (better UX)
- ✅ Maintains determinism (execution agents see committed truth)
- ✅ Avoids circular reference (discovery ≠ execution)
- ✅ Provides explainability (can show what context was used)

---

## Architectural Alignment Check

### ✅ Aligns with Core Principles

**1. "Agents reason. Systems decide."**
- GuideAgent **reasons** about business context (discovery)
- Platform **decides** what is true (commit gate)
- Execution agents receive **decided** truth (authoritative)

**2. Liaison Agent Pattern**
- GuideAgent is a liaison/discovery agent
- It guides, infers, proposes
- It does NOT execute production workflows

**3. 4-Layer Model**
- Discovery context is **input** to Layer 3 (not Layer 3 itself)
- Committed context becomes **source** for `AgentRuntimeContext`
- Execution agents receive assembled `AgentRuntimeContext` (read-only)

**4. Agentic Forward Pattern**
- Discovery agents reason (GuideAgent)
- Execution agents execute (BusinessAnalysisAgent, etc.)
- Clear separation of concerns

---

## Current State Analysis

### ✅ What We Have

1. **GuideAgent exists** (`guide_agent.py`)
   - Currently does intent analysis
   - Routes to pillar liaison agents
   - Tracks user state
   - **Can be extended** to collect discovery context

2. **Session State Storage exists**
   - `context.state_surface.store_session_state()`
   - `context.state_surface.get_session_state()`
   - Supports namespaced storage

3. **RuntimeContextHydrationService exists**
   - Currently reads from request, metadata, session state
   - **Needs update** to read from `committed_context` (not `discovery_context`)

4. **Orchestrator Pattern exists**
   - Call site responsibility (orchestrator assembles context)
   - Agents receive read-only runtime context

### ⚠️ What We Need

1. **Discovery Context Collection**
   - GuideAgent method to infer business context from conversation
   - Store in `session.discovery_context`

2. **Commit Gate**
   - UI to show discovery summary
   - User confirmation/edit capability
   - Backend commit handler

3. **RuntimeContextHydrationService Update**
   - Read from `committed_context` (not `discovery_context`)
   - Priority: request > metadata > committed_context > intent.parameters

4. **Validation & Policy**
   - Validate discovery context structure
   - Apply policy filtering (Smart City, etc.)
   - Apply realm scoping

---

## Implementation Feasibility

### ✅ Highly Feasible

**Why:**
1. **Minimal changes to existing code**
   - GuideAgent already has conversation handling
   - Session state already supports namespacing
   - RuntimeContextHydrationService already reads from session state

2. **Clear separation of concerns**
   - Discovery phase: GuideAgent
   - Commit phase: Orchestrator/Service
   - Execution phase: Existing agents

3. **No breaking changes**
   - Execution agents already receive runtime context
   - Just need to ensure they receive from committed_context

---

## Implementation Plan

### Phase 1: Discovery Context Collection

**Task 1.1: Extend GuideAgent**
```python
# Add to GuideAgent
async def discover_business_context(
    self,
    conversation_history: List[Dict[str, str]],
    context: ExecutionContext
) -> Dict[str, Any]:
    """Discover provisional business context from conversation."""
    
    # Use LLM to infer from conversation
    # Extract: industry, systems, goals, constraints, preferences
    # Store in session.discovery_context
```

**Task 1.2: Update WelcomeJourney (Frontend)**
- Call GuideAgent for discovery
- Show discovery summary
- Allow user confirmation/edits

**Task 1.3: Store Discovery Context**
- Store in `session.discovery_context`
- Include confidence scores
- Include source (guide_agent)

---

### Phase 2: Commit Gate

**Task 2.1: Create Commit Handler**
```python
# In Orchestrator or Service
async def commit_discovery_context(
    self,
    discovery_context: Dict[str, Any],
    context: ExecutionContext
) -> Dict[str, Any]:
    """Commit discovery context to authoritative context."""
    
    # Validate
    # Apply policy
    # Apply realm scoping
    # Store in session.committed_context
    # Log commit event
```

**Task 2.2: Update Frontend**
- Show commit confirmation UI
- Allow edits before commit
- Call commit handler on confirmation

---

### Phase 3: Update Runtime Context Hydration

**Task 3.1: Update RuntimeContextHydrationService**
```python
# Change priority order:
# 1. Request dict (explicit)
# 2. ExecutionContext.metadata
# 3. session.committed_context (NOT discovery_context!)
# 4. Intent.parameters (fallback)
```

**Task 3.2: Ensure Execution Agents Never See Discovery Context**
- Verify agents only receive `AgentRuntimeContext` (from committed_context)
- Add validation/logging

---

### Phase 4: Validation & Testing

**Task 4.1: Test Discovery → Commit → Execution Flow**
- GuideAgent discovers context
- User confirms
- Context committed
- Execution agent receives authoritative context

**Task 4.2: Test Determinism**
- Same committed context → same execution outputs
- Verify replayability

---

## Benefits of This Pattern

### 1. Better UX
- Conversational discovery (natural)
- Agent-led inference (smart)
- User confirmation (trust)

### 2. Determinism
- Execution agents see committed truth
- No randomness in execution
- Replayable

### 3. Explainability
- Can show: "This is the exact context used"
- Can prove: "This is what was committed"
- Enterprise-grade credibility

### 4. Multi-Agent Safety
- All agents see same committed context
- No inference conflicts
- Consistent outputs

---

## Risks & Mitigations

### Risk 1: GuideAgent Over-Inferring
**Mitigation:**
- Include confidence scores
- Show to user for confirmation
- Allow edits

### Risk 2: Discovery Context Leaking to Execution
**Mitigation:**
- Strict separation: RuntimeContextHydrationService only reads `committed_context`
- Validation: Execution agents never see `discovery_context`
- Logging: Track context source

### Risk 3: Commit Gate Bypass
**Mitigation:**
- Require explicit commit action
- Log commit events
- Policy enforcement

---

## Recommendation

**✅ PROCEED WITH IMPLEMENTATION**

**This pattern:**
1. Resolves circular reference elegantly
2. Aligns with architecture principles
3. Improves UX (conversational discovery)
4. Maintains determinism (committed truth)
5. Provides explainability (audit trail)

**Implementation is:**
- Feasible (minimal changes)
- Low risk (clear separation)
- High value (better UX + determinism)

---

## Next Steps

1. **Review** this analysis
2. **Approve** implementation plan
3. **Implement** Phase 1 (Discovery Context Collection)
4. **Implement** Phase 2 (Commit Gate)
5. **Update** RuntimeContextHydrationService
6. **Test** end-to-end flow

---

**Status:** Pattern approved, ready for implementation
