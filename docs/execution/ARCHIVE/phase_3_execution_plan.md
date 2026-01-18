# Phase 3: Platform SDK & Experience Plane - Execution Plan

**Duration:** Week 6-7  
**Status:** Ready to Execute (after Phase 2)  
**Dependencies:** Phase 2 complete

---

## Goal

Build Platform SDK and Experience Plane. Enable frontend to submit intents and receive real-time updates.

**Success Criteria:**
- ✅ Platform SDK complete (Solution Builder + Realm SDK)
- ✅ Experience Plane complete (separate service)
- ✅ Smart City SDK + Primitives complete
- ✅ Agentic SDK complete
- ✅ Frontend can submit intents
- ✅ Real-time updates work (WebSocket streaming)
- ✅ All tests pass (no cheats)

---

## Week 6: Platform SDK & Smart City

### Day 1-2: Solution Builder

#### Task 1.1: Create Solution Model

**Goal:** Define Solution schema and binding model

**Tasks:**
1. Create `civic_systems/platform_sdk/solution_model.py`
2. Define Solution schema:
   - `solution_id` - Unique identifier
   - `solution_context` - Goals, constraints, risk
   - `domain_service_bindings` - Map of realm → external system configs
   - `sync_strategies` - How to keep systems in sync
   - `conflict_resolution` - How to handle concurrent updates
   - `supported_intents` - List of supported intent types
3. Add validation logic

**Files to Create:**
- `symphainy_platform/civic_systems/platform_sdk/solution_model.py`

**Definition of Done:**
- ✅ Solution Model created
- ✅ Validation logic implemented (no stubs)
- ✅ Tests written and passing

---

#### Task 1.2: Create Solution Builder

**Goal:** Builder for creating Solutions

**Tasks:**
1. Create `civic_systems/platform_sdk/solution_builder.py`
2. Implement builder pattern:
   - `create_solution()` - Create solution
   - `add_domain_binding()` - Add domain service binding
   - `add_sync_strategy()` - Add sync strategy
   - `register_intents()` - Register supported intents
3. Validate solution before creation

**Files to Create:**
- `symphainy_platform/civic_systems/platform_sdk/solution_builder.py`

**Definition of Done:**
- ✅ Solution Builder created
- ✅ Builder pattern implemented (no stubs)
- ✅ Tests written and passing

---

### Day 3-4: Realm SDK

#### Task 2.1: Create Realm SDK Base

**Goal:** SDK for creating domain services with Runtime Participation Contract

**Tasks:**
1. Create `civic_systems/platform_sdk/realm_sdk.py`
2. Implement base Realm class:
   - Enforces Runtime Participation Contract
   - `declare_intents()` - Declare supported intents
   - `handle_intent()` - Handle intent (returns artifacts + events)
   - Validation ensures contract compliance
3. Provide decorators for intent handlers

**Files to Create:**
- `symphainy_platform/civic_systems/platform_sdk/realm_sdk.py`

**Realm SDK Pattern:**
```python
class RealmBase:
    def declare_intents(self) -> List[str]:
        """Declare supported intents."""
        # Must be implemented by realm
        raise NotImplementedError
    
    async def handle_intent(
        self,
        intent: Intent,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Handle intent (Runtime Participation Contract).
        
        Returns:
            {"artifacts": {...}, "events": [...]}
        """
        # Must be implemented by realm
        raise NotImplementedError
```

**Definition of Done:**
- ✅ Realm SDK created
- ✅ Runtime Participation Contract enforced
- ✅ Tests written and passing

---

### Day 5: Smart City SDK + Primitives

#### Task 3.1: Create Smart City SDK

**Goal:** SDK for coordination logic (used by Experience, Solution, Realms)

**Tasks:**
1. Create `civic_systems/smart_city/smart_city_sdk.py`
2. Implement SDK methods:
   - `register_capability()` - Register domain capability
   - `get_policy()` - Get policy decision
   - `validate_execution()` - Validate execution constraints
3. Uses Smart City Primitives (via Runtime)

**Files to Create:**
- `symphainy_platform/civic_systems/smart_city/smart_city_sdk.py`

**Definition of Done:**
- ✅ Smart City SDK created
- ✅ Coordination logic implemented (no stubs)
- ✅ Tests written and passing

---

#### Task 3.2: Create Smart City Primitives

**Goal:** Primitives for policy decisions (used by Runtime only)

**Tasks:**
1. Create `civic_systems/smart_city/primitives.py`
2. Implement primitives:
   - `validate_policy()` - Validate policy
   - `check_authorization()` - Check authorization
   - `get_execution_constraints()` - Get execution constraints
3. Used by Runtime, not by domain services

**Files to Create:**
- `symphainy_platform/civic_systems/smart_city/primitives.py`

**Definition of Done:**
- ✅ Smart City Primitives created
- ✅ Policy primitives implemented (no stubs)
- ✅ Tests written and passing

---

## Week 7: Experience Plane & Agentic SDK

### Day 1-3: Experience Plane

#### Task 4.1: Create Experience Service

**Goal:** Separate service for user interaction

**Tasks:**
1. Create `civic_systems/experience/experience_service.py`
2. Implement Experience service:
   - `create_session()` - Create session via Runtime
   - `submit_intent()` - Submit intent via Runtime
   - `stream_execution()` - Stream execution updates (WebSocket)
3. Never calls domain services directly
4. Never manages workflows
5. Never owns state

**Files to Create:**
- `symphainy_platform/civic_systems/experience/experience_service.py`

**Definition of Done:**
- ✅ Experience Service created
- ✅ Session management implemented
- ✅ Intent submission implemented
- ✅ WebSocket streaming implemented
- ✅ Tests written and passing

---

#### Task 4.2: Create Experience API

**Goal:** FastAPI endpoints for Experience

**Tasks:**
1. Create `civic_systems/experience/experience_api.py`
2. Implement endpoints:
   - `POST /api/session/create` - Create session
   - `POST /api/intent/submit` - Submit intent
   - `WebSocket /api/execution/stream` - Stream execution updates
3. Integrate with Experience Service

**Files to Create:**
- `symphainy_platform/civic_systems/experience/experience_api.py`

**Definition of Done:**
- ✅ Experience API created
- ✅ All endpoints implemented (no stubs)
- ✅ WebSocket streaming works
- ✅ Tests written and passing

---

### Day 4-5: Agentic SDK

#### Task 5.1: Create Agentic SDK

**Goal:** SDK for agent framework (inspired by CrewAI/LangGraph, but custom)

**Tasks:**
1. Create `civic_systems/agentic/agentic_sdk.py`
2. Implement agent framework:
   - `Agent` base class
   - `AgentRegistry` - Agent registry
   - `AgentFactory` - Agent factory
   - Grounding, telemetry, policy hooks
3. Pattern adoption (not product adoption)

**Files to Create:**
- `symphainy_platform/civic_systems/agentic/agentic_sdk.py`

**Agent SDK Pattern:**
```python
class Agent:
    """Agent base class."""
    
    async def reason(
        self,
        artifacts: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Reason over artifacts (returns interpretation/recommendation).
        
        Agents never execute - they only reason.
        """
        raise NotImplementedError
```

**Definition of Done:**
- ✅ Agentic SDK created
- ✅ Agent framework implemented (no stubs)
- ✅ Pattern adoption (swappable, not dependent)
- ✅ Tests written and passing

---

## Phase 3 Checklist

Track progress with this checklist:

### Week 6: Platform SDK & Smart City
- [ ] Solution Model created
- [ ] Solution Model tests pass
- [ ] Solution Builder created
- [ ] Solution Builder tests pass
- [ ] Realm SDK created
- [ ] Realm SDK tests pass
- [ ] Smart City SDK created
- [ ] Smart City SDK tests pass
- [ ] Smart City Primitives created
- [ ] Smart City Primitives tests pass

### Week 7: Experience Plane & Agentic SDK
- [ ] Experience Service created
- [ ] Experience Service tests pass
- [ ] Experience API created
- [ ] Experience API tests pass
- [ ] WebSocket streaming works
- [ ] Agentic SDK created
- [ ] Agentic SDK tests pass
- [ ] Integration tests created
- [ ] All integration tests pass

---

## Success Criteria

**Phase 3 is complete when:**
- ✅ Platform SDK complete (Solution Builder + Realm SDK)
- ✅ Experience Plane complete (separate service)
- ✅ Smart City SDK + Primitives complete
- ✅ Agentic SDK complete
- ✅ Frontend can submit intents
- ✅ Real-time updates work (WebSocket streaming)
- ✅ All tests pass (no cheats)

**No code should have stubs, cheats, or placeholders.**

---

## Next Steps

After Phase 3, proceed to [Phase 4: Frontend Integration](phase_4_execution_plan.md).

---

## References

- [Architecture Guide](../architecture/north_star.md)
- [Platform Rules](../PLATFORM_RULES.md)
- [Roadmap](../roadmap/00_ROADMAP_INDEX.md)
- [Phase 2 Execution Plan](phase_2_execution_plan.md)
