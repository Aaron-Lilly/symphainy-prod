# Discovery vs Execution Context Pattern

**Date:** January 2026  
**Status:** ✅ **ARCHITECTURAL PATTERN APPROVED**

---

## Executive Summary

**This pattern resolves the "circular reference" problem by separating discovery (provisional) from execution (authoritative) context.**

**Core Principle:**
> **Agents may *discover* runtime context, but they may not *own* it.**

This enables:
- ✅ Conversational discovery (better UX)
- ✅ Deterministic execution (replayable, auditable)
- ✅ No circular reference (discovery agents don't execute, execution agents don't discover)
- ✅ Multi-agent safety (all agents see same committed truth)

---

## The Problem It Solves

### The Circular Reference Issue

**Original Concern:**
- Agents need runtime context to work
- But if agents collect their own runtime context, we get circular reference
- Solution: UI collects → Backend stores → Orchestrator extracts → Agent uses

**Limitation of Pure UI Collection:**
- Less conversational
- Less flexible
- Doesn't leverage agent reasoning for discovery

### The Discovery → Execution Separation

**Two Distinct Phases:**

1. **Discovery Phase (Provisional)**
   - GuideAgent (or discovery agents) collect provisional context
   - Conversational, editable, human-in-the-loop
   - Stored in `session.discovery_context`
   - NOT authoritative

2. **Execution Phase (Authoritative)**
   - User confirms/commits discovery context
   - Platform validates and applies policy
   - Stored in `session.committed_context`
   - Execution agents receive immutable `AgentRuntimeContext`

---

## The Pattern

### Phase Separation Flow

```
GuideAgent (Discovery)
   ↓
Provisional Context (session.discovery_context)
   ↓
User Confirmation / System Validation
   ↓
Context Commit Event
   ↓
RuntimeContextHydrationService (reads committed_context)
   ↓
Execution Agents (deterministic, receive AgentRuntimeContext)
```

### Key Rule

> **No execution agent ever sees provisional context.**

---

## Two Kinds of Context

### 1. Provisional Context (Discovery Phase)

**Who owns it?**
- GuideAgent (or other discovery agents)

**What it is:**
- Hypotheses
- Inferred business facts
- User-stated preferences
- Candidate constraints
- Example: "It sounds like you're in healthcare, mid-market, using Salesforce..."

**Properties:**
- ❌ Not authoritative
- ❌ Not guaranteed complete
- ❌ Not replay-safe
- ✅ Conversational
- ✅ Editable
- ✅ Human-in-the-loop

**Where it lives:**
- `session.discovery_context.*`
- NOT in `AgentRuntimeContext`

**Structure:**
```json
{
  "discovery_context": {
    "industry": "Insurance",
    "systems": ["Mainframe", "Salesforce"],
    "goals": ["Policy migration", "Operational efficiency"],
    "constraints": ["Regulatory", "Zero downtime"],
    "confidence": {
      "industry": 0.9,
      "systems": 0.7
    },
    "source": "guide_agent",
    "discovered_at": "2026-01-XX...",
    "status": "provisional"
  }
}
```

---

### 2. Authoritative Runtime Context (Execution Phase)

**Who owns it?**
- Platform (via orchestration + policy)

**What it is:**
- Validated
- Policy-filtered
- Realm-scoped
- Deterministic
- Immutable

**Properties:**
- ✅ Replayable
- ✅ Logged
- ✅ Traceable
- ✅ Contractual

**Where it lives:**
- `AgentRuntimeContext` (ephemeral, assembled at call time)
- Created from `session.committed_context`

**Structure:**
```python
AgentRuntimeContext(
    business_context={
        "industry": "Insurance",  # Validated
        "systems": ["Mainframe", "Salesforce"],  # Policy-filtered
        "constraints": ["Regulatory", "Zero downtime"]  # Realm-scoped
    },
    journey_goal="Policy migration",  # Committed
    human_preferences={
        "detail_level": "detailed",  # User-confirmed
        "wants_visuals": True
    },
    available_artifacts=[...],
    session_state={...}
)
```

---

## Implementation

### Step 1: GuideAgent Builds Discovery Context

**GuideAgent Responsibilities:**
- ✅ Ask questions
- ✅ Infer business context
- ✅ Suggest defaults
- ✅ Summarize understanding
- ✅ Propose a "working context"

**GuideAgent Limitations:**
- ❌ Cannot create `AgentRuntimeContext`
- ❌ Cannot merge context sources
- ❌ Cannot decide precedence
- ❌ Cannot execute production workflows

**Implementation:**
```python
# In GuideAgent
async def discover_business_context(self, conversation_history, context):
    """Discover provisional business context from conversation."""
    
    # Use LLM to infer from conversation
    discovery_result = await self.llm_client.chat_completion(
        messages=[
            {"role": "system", "content": "You are a discovery agent..."},
            {"role": "user", "content": conversation_history}
        ]
    )
    
    # Extract provisional context
    discovery_context = {
        "industry": discovery_result.get("industry"),
        "systems": discovery_result.get("systems", []),
        "goals": discovery_result.get("goals", []),
        "constraints": discovery_result.get("constraints", []),
        "confidence": discovery_result.get("confidence", {}),
        "source": "guide_agent",
        "discovered_at": datetime.now().isoformat(),
        "status": "provisional"
    }
    
    # Store in session state (discovery namespace)
    await context.state_surface.store_session_state(
        context.session_id,
        context.tenant_id,
        {"discovery_context": discovery_context}
    )
    
    return discovery_context
```

---

### Step 2: Commit Gate (Human or Policy)

**Before anything "real" happens:**

1. Show summary to user:
   > "Here's what I understand about your situation..."

2. Allow:
   - User confirmation
   - Edits
   - Policy checks
   - Realm scoping

**This is crucial for:**
- Trust
- Determinism
- Explainability

**Implementation:**
```python
# In Frontend (WelcomeJourney or similar)
async def show_discovery_summary(discovery_context):
    """Show discovery context summary and allow user to confirm/edit."""
    
    # Display summary
    summary = {
        "Industry": discovery_context["industry"],
        "Systems": ", ".join(discovery_context["systems"]),
        "Goals": ", ".join(discovery_context["goals"]),
        "Constraints": ", ".join(discovery_context["constraints"])
    }
    
    # User can:
    # - Confirm (commit)
    # - Edit (update discovery_context)
    # - Reject (restart discovery)
    
    return user_action  # "confirm", "edit", "reject"
```

---

### Step 3: Context Commit Event

**This is a formal transition:**

```
DISCOVERY → COMMITTED
```

**At this moment:**
- Discovery context becomes **input** (not truth)
- Platform validates
- Policy applies
- Realm scoping applies
- Committed context is created

**Implementation:**
```python
# In Orchestrator or Service
async def commit_discovery_context(
    self,
    discovery_context: Dict[str, Any],
    context: ExecutionContext
) -> Dict[str, Any]:
    """Commit discovery context to authoritative context."""
    
    # Validate discovery context
    validated_context = self._validate_discovery_context(discovery_context)
    
    # Apply policy (Smart City, etc.)
    policy_filtered = self._apply_policy(validated_context, context)
    
    # Apply realm scoping
    realm_scoped = self._apply_realm_scoping(policy_filtered, context)
    
    # Create committed context
    committed_context = {
        "business_context": {
            "industry": realm_scoped["industry"],
            "systems": realm_scoped["systems"],
            "constraints": realm_scoped["constraints"]
        },
        "journey_goal": realm_scoped["goals"][0] if realm_scoped["goals"] else "",
        "human_preferences": realm_scoped.get("preferences", {}),
        "committed_at": datetime.now().isoformat(),
        "committed_by": context.user_id,
        "source": "discovery_commit"
    }
    
    # Store in session state (committed namespace)
    await context.state_surface.store_session_state(
        context.session_id,
        context.tenant_id,
        {"committed_context": committed_context}
    )
    
    # Log commit event
    await context.wal.append_event({
        "type": "context_committed",
        "session_id": context.session_id,
        "committed_context": committed_context
    })
    
    return committed_context
```

---

### Step 4: Runtime Context Hydration (Authoritative)

**RuntimeContextHydrationService now reads from committed context:**

**Priority Order:**
1. Request dict (explicit parameters) - highest priority
2. ExecutionContext.metadata
3. **Session committed_context** (not discovery_context!)
4. Intent.parameters (fallback)

**Implementation:**
```python
# In RuntimeContextHydrationService
async def create_runtime_context(
    self,
    request: Dict[str, Any],
    context: ExecutionContext
) -> AgentRuntimeContext:
    """Create authoritative runtime context from committed sources."""
    
    # Extract from session state (committed_context only)
    session_state = await context.state_surface.get_session_state(
        context.session_id,
        context.tenant_id
    )
    
    committed_context = session_state.get("committed_context", {})
    
    # Priority order:
    # 1. Request dict (explicit)
    business_context = request.get("business_context") or \
                      context.metadata.get("business_context") or \
                      committed_context.get("business_context", {})
    
    journey_goal = request.get("journey_goal") or \
                   context.metadata.get("journey_goal") or \
                   committed_context.get("journey_goal", "")
    
    human_preferences = request.get("human_preferences") or \
                       context.metadata.get("human_preferences") or \
                       committed_context.get("human_preferences", {})
    
    # Create AgentRuntimeContext (immutable, authoritative)
    return AgentRuntimeContext(
        business_context=business_context,
        journey_goal=journey_goal,
        human_preferences=human_preferences,
        available_artifacts=session_state.get("available_artifacts", []),
        session_state=session_state
    )
```

---

### Step 5: Execution Agents Run Cleanly

**Execution agents:**
- ✅ Receive `AgentRuntimeContext` (read-only)
- ✅ Never see the conversation
- ✅ Never infer business facts
- ✅ Never ask "what kind of company is this?"

**This ensures:**
- Repeatability
- Replay
- Auditing
- Consistent outputs

**Implementation:**
```python
# In Orchestrator (call site)
async def _handle_interpret_data(self, intent, context):
    # Assemble runtime context (from committed_context)
    runtime_context = await self.runtime_context_service.create_runtime_context(
        request={"type": "interpret_data", "parsed_file_id": ...},
        context=context
    )
    
    # Pass to agent (read-only)
    agent_result = await self.business_analysis_agent.process_request(
        request={"type": "interpret_data", "parsed_file_id": ...},
        context=context,
        runtime_context=runtime_context  # Authoritative, read-only
    )
```

---

## Why This Is Actually a Strength

### 1. Determinism Without Killing UX

**You get:**
- ✅ Rich conversational onboarding
- ✅ Agent-led discovery
- ✅ Zero randomness in execution

**Most platforms sacrifice one for the other. You don't.**

---

### 2. Explainability & Trust

**You can say to clients:**
> "This is the exact context used to generate your blueprint."

**And prove it.**

**That's enterprise-grade credibility.**

---

### 3. Multi-Agent Safety

**You avoid the classic agent failure mode:**
> "Agent A inferred X, Agent B inferred Y, outputs don't match."

**Here:**
- ✅ Inference happens once (discovery)
- ✅ Commitment happens once (commit gate)
- ✅ Everyone else consumes the same truth (execution)

---

## Simple Rule to Put in Architecture Guide

> **Agents may reason about the world.
> The platform decides what is true.**

**You've already built a platform that *wants* this rule.**
**This pattern makes it explicit.**

---

## Implementation Checklist

### Discovery Phase:
- [ ] GuideAgent collects provisional context
- [ ] Store in `session.discovery_context`
- [ ] Show summary to user
- [ ] Allow user confirmation/edits

### Commit Phase:
- [ ] Create commit gate (UI + backend)
- [ ] Validate discovery context
- [ ] Apply policy filtering
- [ ] Apply realm scoping
- [ ] Store in `session.committed_context`
- [ ] Log commit event

### Execution Phase:
- [ ] Update RuntimeContextHydrationService to read from `committed_context` (not `discovery_context`)
- [ ] Ensure execution agents never see provisional context
- [ ] Test determinism (same committed context → same outputs)

---

## Next Steps

1. **Validate** current GuideAgent implementation
2. **Implement** discovery context collection
3. **Implement** commit gate
4. **Update** RuntimeContextHydrationService
5. **Test** end-to-end flow

---

**Status:** Pattern approved, ready for implementation
