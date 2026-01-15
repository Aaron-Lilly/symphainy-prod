# Phase 2: Architecture Enhancements - Execution Plan

**Duration:** Week 4-5  
**Status:** Ready to Execute (after Phase 1)  
**Dependencies:** Phase 1 complete

---

## Goal

Complete Runtime Execution Engine and Data Brain scaffolding. Build the core execution authority that makes the platform vision real.

**Success Criteria:**
- ✅ Intent Model complete (formal schema, validation)
- ✅ Execution Context complete (runtime context for domain services)
- ✅ Execution Lifecycle Manager complete (orchestrates full flow)
- ✅ Transactional Outbox complete (atomic event publishing)
- ✅ Data Brain scaffolding complete (reference registration, provenance)
- ✅ Full execution flow works (intent → execution → completion)
- ✅ All tests pass (no cheats)

---

## Week 4: Core Runtime Components

### Day 1-2: Intent Model

#### Task 1.1: Create Intent Model Schema

**Goal:** Define formal intent schema and validation

**Tasks:**
1. Create `runtime/intent_model.py`
2. Define Intent schema:
   - `intent_id` - Unique identifier
   - `intent_type` - Type of intent (e.g., "ingest_file", "analyze_content")
   - `tenant_id` - Tenant identifier
   - `session_id` - Session identifier
   - `solution_id` - Solution identifier
   - `parameters` - Intent parameters (Dict[str, Any])
   - `metadata` - Intent metadata (Dict[str, Any])
3. Add validation logic
4. Add intent factory methods

**Files to Create:**
- `symphainy_platform/runtime/intent_model.py`

**Intent Schema:**
```python
@dataclass
class Intent:
    intent_id: str
    intent_type: str
    tenant_id: str
    session_id: str
    solution_id: str
    parameters: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: datetime
    
    def validate(self) -> bool:
        """Validate intent structure."""
        # Real validation logic
        # NO STUBS, NO CHEATS
```

**Tests to Write:**
- `tests/runtime/test_intent_model.py`
  - Test intent creation
  - Test intent validation
  - Test intent serialization
  - **Tests must fail if model has stubs/cheats**

**Definition of Done:**
- ✅ Intent Model created
- ✅ Validation logic implemented (no stubs)
- ✅ Tests written and passing
- ✅ Tests would fail if model had stubs

---

#### Task 1.2: Create Intent Registry

**Goal:** Track which domain services support which intents

**Tasks:**
1. Create `runtime/intent_registry.py`
2. Implement intent registration:
   - `register_intent()` - Register intent type with domain service
   - `get_intent_handlers()` - Get handlers for intent type
   - `list_supported_intents()` - List all supported intents
3. Use Public Works abstractions (no direct DB calls)

**Files to Create:**
- `symphainy_platform/runtime/intent_registry.py`

**Definition of Done:**
- ✅ Intent Registry created
- ✅ Registration logic implemented (no stubs)
- ✅ Tests written and passing

---

### Day 3-4: Execution Context

#### Task 2.1: Create Execution Context

**Goal:** Runtime context for domain services

**Tasks:**
1. Create `runtime/execution_context.py`
2. Define ExecutionContext:
   - `execution_id` - Unique execution identifier
   - `intent` - The intent being executed
   - `tenant_id` - Tenant identifier
   - `session_id` - Session identifier
   - `solution_id` - Solution identifier
   - `state_surface` - State surface reference
   - `wal` - WAL reference
   - `metadata` - Execution metadata
3. Add context factory methods

**Files to Create:**
- `symphainy_platform/runtime/execution_context.py`

**Context Schema:**
```python
@dataclass
class ExecutionContext:
    execution_id: str
    intent: Intent
    tenant_id: str
    session_id: str
    solution_id: str
    state_surface: StateSurface
    wal: WriteAheadLog
    metadata: Dict[str, Any]
    created_at: datetime
```

**Tests to Write:**
- `tests/runtime/test_execution_context.py`
  - Test context creation
  - Test context serialization
  - **Tests must fail if context has stubs/cheats**

**Definition of Done:**
- ✅ Execution Context created
- ✅ Context factory implemented (no stubs)
- ✅ Tests written and passing

---

### Day 5: Execution Lifecycle Manager

#### Task 3.1: Create Execution Lifecycle Manager

**Goal:** Orchestrate full execution flow

**Tasks:**
1. Create `runtime/execution_lifecycle_manager.py`
2. Implement lifecycle stages:
   - `accept_intent()` - Accept and validate intent
   - `create_execution()` - Create execution context
   - `execute_intent()` - Execute intent via domain service
   - `handle_artifacts()` - Process artifacts from domain service
   - `publish_events()` - Publish events via transactional outbox
   - `complete_execution()` - Mark execution complete
3. Integrate with WAL (log all lifecycle events)
4. Integrate with Saga Coordinator (for multi-step workflows)

**Files to Create:**
- `symphainy_platform/runtime/execution_lifecycle_manager.py`

**Lifecycle Flow:**
```python
class ExecutionLifecycleManager:
    async def execute(self, intent: Intent) -> ExecutionResult:
        # 1. Accept intent
        # 2. Create execution context
        # 3. Find intent handler (domain service)
        # 4. Execute intent
        # 5. Handle artifacts
        # 6. Publish events (via outbox)
        # 7. Complete execution
        # NO STUBS, NO CHEATS
```

**Tests to Write:**
- `tests/runtime/test_execution_lifecycle_manager.py`
  - Test full execution flow
  - Test error handling
  - Test WAL integration
  - **Tests must fail if manager has stubs/cheats**

**Definition of Done:**
- ✅ Execution Lifecycle Manager created
- ✅ Full lifecycle implemented (no stubs)
- ✅ WAL integration working
- ✅ Tests written and passing

---

## Week 5: Transactional Outbox & Data Brain

### Day 1-2: Transactional Outbox

#### Task 4.1: Create Transactional Outbox

**Goal:** Guarantee atomic event publishing within saga steps

**Tasks:**
1. Create `runtime/transactional_outbox.py`
2. Implement outbox pattern:
   - `add_event()` - Add event to outbox (atomic with state change)
   - `publish_events()` - Publish events from outbox
   - `mark_published()` - Mark events as published
   - `get_pending_events()` - Get pending events
3. Integrate with WAL (events logged before publishing)
4. Use Redis Streams for outbox storage

**Files to Create:**
- `symphainy_platform/runtime/transactional_outbox.py`

**Outbox Pattern:**
```python
class TransactionalOutbox:
    async def add_event(
        self,
        execution_id: str,
        event_type: str,
        event_data: Dict[str, Any]
    ) -> bool:
        # Add to outbox atomically with state change
        # NO STUBS, NO CHEATS
    
    async def publish_events(self, execution_id: str) -> int:
        # Publish pending events
        # Mark as published
        # NO STUBS, NO CHEATS
```

**Tests to Write:**
- `tests/runtime/test_transactional_outbox.py`
  - Test atomic event addition
  - Test event publishing
  - Test failure recovery
  - **Tests must fail if outbox has stubs/cheats**

**Definition of Done:**
- ✅ Transactional Outbox created
- ✅ Atomic operations implemented (no stubs)
- ✅ WAL integration working
- ✅ Tests written and passing

---

### Day 3-4: Data Brain Scaffolding

#### Task 5.1: Create Data Brain Core

**Goal:** Runtime-native data cognition scaffolding

**Tasks:**
1. Create `runtime/data_brain.py`
2. Implement data reference registration:
   - `register_reference()` - Register data reference
   - `get_reference()` - Get data reference
   - `list_references()` - List references by criteria
3. Implement provenance tracking:
   - `track_provenance()` - Track data lineage
   - `get_provenance()` - Get provenance chain
4. Use Public Works abstractions (ArangoDB for storage)

**Files to Create:**
- `symphainy_platform/runtime/data_brain.py`

**Data Brain Interface:**
```python
class DataBrain:
    async def register_reference(
        self,
        reference_id: str,
        reference_type: str,
        metadata: Dict[str, Any],
        execution_id: str
    ) -> bool:
        # Register data reference
        # Track provenance
        # NO STUBS, NO CHEATS
    
    async def get_reference(
        self,
        reference_id: str
    ) -> Optional[DataReference]:
        # Get reference (returns reference, not data)
        # NO STUBS, NO CHEATS
```

**Tests to Write:**
- `tests/runtime/test_data_brain.py`
  - Test reference registration
  - Test provenance tracking
  - Test reference retrieval
  - **Tests must fail if Data Brain has stubs/cheats**

**Definition of Done:**
- ✅ Data Brain scaffolding created
- ✅ Reference registration implemented (no stubs)
- ✅ Provenance tracking implemented (no stubs)
- ✅ Tests written and passing

---

### Day 5: Integration & Testing

#### Task 6.1: End-to-End Integration

**Goal:** Verify all Phase 2 components work together

**Tasks:**
1. Create integration tests:
   - Test intent → execution → completion flow
   - Test transactional outbox integration
   - Test Data Brain integration
   - Test WAL integration
2. Run all tests
3. Verify no stubs/cheats

**Files to Create:**
- `tests/integration/phase_2/test_runtime_execution_engine.py`

**Test Scenarios:**
1. **Full Execution Flow:**
   - Create intent
   - Execute intent
   - Verify artifacts
   - Verify events published
   - Verify WAL entries

2. **Transactional Outbox:**
   - Add event to outbox
   - Verify atomicity
   - Publish events
   - Verify published

3. **Data Brain:**
   - Register reference
   - Track provenance
   - Retrieve reference
   - Verify provenance chain

**Definition of Done:**
- ✅ Integration tests created
- ✅ All tests pass
- ✅ No stubs/cheats found
- ✅ Full execution flow works

---

## Phase 2 Checklist

Track progress with this checklist:

### Week 4: Core Runtime Components
- [ ] Intent Model created
- [ ] Intent Model tests pass
- [ ] Intent Registry created
- [ ] Intent Registry tests pass
- [ ] Execution Context created
- [ ] Execution Context tests pass
- [ ] Execution Lifecycle Manager created
- [ ] Execution Lifecycle Manager tests pass

### Week 5: Transactional Outbox & Data Brain
- [ ] Transactional Outbox created
- [ ] Transactional Outbox tests pass
- [ ] Data Brain scaffolding created
- [ ] Data Brain tests pass
- [ ] Integration tests created
- [ ] All integration tests pass
- [ ] No stubs/cheats found

---

## Success Criteria

**Phase 2 is complete when:**
- ✅ Intent Model complete (formal schema, validation)
- ✅ Execution Context complete (runtime context for domain services)
- ✅ Execution Lifecycle Manager complete (orchestrates full flow)
- ✅ Transactional Outbox complete (atomic event publishing)
- ✅ Data Brain scaffolding complete (reference registration, provenance)
- ✅ Full execution flow works (intent → execution → completion)
- ✅ All tests pass (no cheats)

**No code should have stubs, cheats, or placeholders.**

---

## Next Steps

After Phase 2, proceed to [Phase 3: Platform SDK & Experience Plane](phase_3_execution_plan.md).

---

## References

- [Architecture Guide](../architecture/north_star.md)
- [Platform Rules](../PLATFORM_RULES.md)
- [Roadmap](../roadmap/00_ROADMAP_INDEX.md)
- [Phase 1 Execution Plan](phase_1_execution_plan.md)
