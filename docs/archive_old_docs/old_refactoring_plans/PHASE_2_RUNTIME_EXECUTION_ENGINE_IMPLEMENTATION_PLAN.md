# Phase 2: Runtime Execution Engine - Implementation Plan

**Date:** January 2026  
**Status:** 📋 **DETAILED IMPLEMENTATION PLAN**  
**Based on:** `symphainy_architecture_guide.md`  
**Purpose:** Build the Runtime Execution Engine as the single execution authority

---

## Executive Summary

Phase 2 builds the **Runtime Execution Engine** - the core component that makes Symphainy a "governed execution platform." The Runtime is the **only component allowed to own execution and state**, ensuring that:

- Nothing executes without **intent**
- Nothing executes without **policy**
- Nothing executes without **attribution**
- Nothing executes **outside the Runtime**

**If Runtime cannot see it, it did not happen.**

---

## Architecture Overview

### Runtime Responsibilities (from Architecture Guide)

Runtime owns:

1. **Intent acceptance** - Receives and validates intents
2. **Execution lifecycle** - Manages execution from start to finish
3. **Session & tenant context** - Maintains isolation and context
4. **Write-ahead log (WAL)** - Records all execution events
5. **Saga orchestration** - Coordinates multi-step workflows
6. **Retries & failure recovery** - Handles failures gracefully
7. **Deterministic replay** - Enables replay of execution history
8. **State transitions** - Tracks execution state changes
9. **Runtime-native data cognition (Data Brain)** - Data participates in execution

### Runtime Execution Flow (Canonical)

```
1. Interaction enters via Experience
2. Experience emits an intent
3. Runtime validates session, tenant, policy
4. Runtime records intent in WAL
5. Runtime resolves domain capability via Curator
6. Domain service executes under runtime context
7. Artifacts & events are recorded
8. Updates stream back to Experience
```

### Runtime Participation Contract

Every domain service must:

- Declare which **intents** it supports
- Accept a **runtime execution context**
- Return **artifacts and events**, not side effects
- Never bypass Runtime for state, retries, or orchestration

```python
handle_intent(intent, runtime_context) → { artifacts, events }
```

---

## Current State Assessment

### ✅ What Exists (Build On)

1. **State Surface** (`runtime/state_surface.py`)
   - ✅ Execution state storage
   - ✅ File metadata/reference storage
   - ✅ Session state management
   - ⚠️ Needs: Integration with WAL for state transitions

2. **Write-Ahead Log** (`runtime/wal.py`)
   - ✅ Basic WAL implementation (Redis/memory)
   - ✅ Event types defined
   - ✅ Append-only log
   - ⚠️ Needs: Integration with execution lifecycle, replay capabilities

3. **Saga Coordinator** (`runtime/saga.py`)
   - ✅ Saga structure and lifecycle
   - ✅ Saga step interface
   - ⚠️ Needs: Retries, failure recovery, compensation logic

4. **Intent Executor** (`runtime/intent_executor.py`)
   - ✅ Basic intent routing
   - ✅ Curator integration
   - ⚠️ Needs: Formal intent model, execution context, WAL integration

5. **Session** (`runtime/session.py`)
   - ✅ Session structure
   - ✅ Tenant isolation
   - ✅ Active saga tracking
   - ✅ Complete

6. **Runtime Service** (`runtime/runtime_service.py`)
   - ✅ FastAPI service
   - ✅ Session lifecycle endpoints
   - ✅ Intent submission endpoints
   - ⚠️ Needs: Full execution flow integration

### ❌ What's Missing (Build New)

1. **Intent Model** - Formal schema for intents
2. **Execution Context** - Runtime context passed to domain services
3. **Execution Lifecycle Manager** - Orchestrates full execution flow
4. **Retry & Failure Recovery** - Handles failures and retries
5. **Deterministic Replay** - Replay execution from WAL
6. **Data Brain Scaffolding** - Runtime-native data cognition

---

## Implementation Plan

### Phase 2.1: Intent Model (Week 1, Days 1-2)

**Goal:** Define formal intent schema and validation

**Tasks:**

1. **Create Intent Model** (`runtime/intent_model.py`)
   ```python
   @dataclass
   class Intent:
       """Formal intent structure."""
       intent_id: str
       intent_type: str  # e.g., "content.upload", "journey.create_sop"
       realm: str  # Target realm (e.g., "content", "journey")
       session_id: str
       tenant_id: str
       payload: Dict[str, Any]
       metadata: Dict[str, Any]  # Source, correlation_id, etc.
       created_at: datetime
   ```

2. **Create Intent Validator** (`runtime/intent_validator.py`)
   - Validate intent structure
   - Validate session exists
   - Validate tenant isolation
   - Validate intent type format

3. **Update Intent Executor**
   - Use formal Intent model
   - Validate intents before execution
   - Return structured errors

**Success Criteria:**
- ✅ Intents have formal schema
- ✅ Intents are validated before execution
- ✅ Invalid intents return clear errors

---

### Phase 2.2: Execution Context (Week 1, Days 3-4)

**Goal:** Define runtime execution context passed to domain services

**Tasks:**

1. **Create Execution Context** (`runtime/execution_context.py`)
   ```python
   @dataclass
   class ExecutionContext:
       """Runtime execution context passed to domain services."""
       execution_id: str
       intent: Intent
       session: Session
       tenant_id: str
       user_id: str
       state_surface: StateSurface  # Runtime-owned state
       wal: WriteAheadLog  # Runtime-owned WAL
       saga_coordinator: SagaCoordinator  # Runtime-owned saga coordinator
       policy_context: Dict[str, Any]  # Policy validation results
       correlation_id: str  # For tracing
       created_at: datetime
   ```

2. **Create Execution Context Builder** (`runtime/execution_context_builder.py`)
   - Build execution context from intent
   - Inject Runtime components (State Surface, WAL, Saga Coordinator)
   - Inject policy context (from Smart City)
   - Generate correlation IDs

3. **Update Intent Executor**
   - Build execution context
   - Pass context to domain services
   - Ensure context is immutable

**Success Criteria:**
- ✅ Execution context is formal and complete
- ✅ Domain services receive runtime context
- ✅ Context includes all Runtime components

---

### Phase 2.3: Execution Lifecycle Manager (Week 1, Days 5-7)

**Goal:** Orchestrate full execution flow from intent to completion

**Tasks:**

1. **Create Execution Lifecycle Manager** (`runtime/execution_lifecycle.py`)
   ```python
   class ExecutionLifecycleManager:
       """Orchestrates full execution lifecycle."""
       
       async def execute_intent(
           self,
           intent: Intent,
           execution_context: ExecutionContext
       ) -> ExecutionResult:
           """
           Execute intent through full lifecycle:
           1. Validate intent
           2. Record intent in WAL
           3. Resolve capability via Curator
           4. Execute domain service
           5. Record artifacts/events
           6. Update state
           7. Return result
           """
   ```

2. **Create Execution Result** (`runtime/execution_result.py`)
   ```python
   @dataclass
   class ExecutionResult:
       """Result of intent execution."""
       execution_id: str
       success: bool
       artifacts: Dict[str, Any]  # Domain service artifacts
       events: List[Dict[str, Any]]  # Domain service events
       state_changes: List[Dict[str, Any]]  # State transitions
       error: Optional[str] = None
       execution_time_ms: float
   ```

3. **Integrate with WAL**
   - Record intent received
   - Record execution started
   - Record execution completed/failed
   - Record state transitions

4. **Integrate with State Surface**
   - Store execution state
   - Store artifacts (references only)
   - Track state transitions

5. **Update Runtime Service**
   - Use Execution Lifecycle Manager
   - Handle execution flow
   - Return execution results

**Success Criteria:**
- ✅ Full execution lifecycle is orchestrated
- ✅ All execution events are recorded in WAL
- ✅ State transitions are tracked
- ✅ Artifacts and events are captured

---

### Phase 2.4: WAL Enhancements (Week 2, Days 1-2)

**Goal:** Enhance WAL for full execution tracking and replay

**Tasks:**

1. **Enhance WAL Event Types**
   - Add more event types (policy_validation, capability_resolution, etc.)
   - Add event relationships (parent/child events)
   - Add event metadata (correlation_id, execution_id)

2. **Add WAL Replay Capabilities**
   ```python
   async def replay_execution(
       self,
       execution_id: str,
       tenant_id: str
   ) -> List[WALEvent]:
       """Replay all events for an execution."""
   
   async def replay_session(
       self,
       session_id: str,
       tenant_id: str
   ) -> List[WALEvent]:
       """Replay all events for a session."""
   ```

3. **Add WAL Query Capabilities**
   - Query by execution_id
   - Query by session_id
   - Query by intent_type
   - Query by time range
   - Query by event type

4. **Integrate with Execution Lifecycle**
   - Record all execution events
   - Record state transitions
   - Record policy validations
   - Record capability resolutions

**Success Criteria:**
- ✅ WAL records all execution events
- ✅ WAL supports replay
- ✅ WAL supports querying
- ✅ WAL is integrated with execution lifecycle

---

### Phase 2.5: Saga Orchestration Enhancements (Week 2, Days 3-5)

**Goal:** Add retries, failure recovery, and compensation logic

**Tasks:**

1. **Add Retry Logic** (`runtime/saga_retry.py`)
   ```python
   class SagaRetryManager:
       """Manages saga step retries."""
       
       async def retry_step(
           self,
           saga: Saga,
           step: SagaStep,
           max_retries: int = 3,
           backoff_strategy: str = "exponential"
       ) -> bool:
           """Retry a failed saga step."""
   ```

2. **Add Failure Recovery** (`runtime/saga_recovery.py`)
   ```python
   class SagaRecoveryManager:
       """Manages saga failure recovery."""
       
       async def recover_saga(
           self,
           saga: Saga,
           recovery_strategy: str = "compensate"
       ) -> bool:
           """Recover from saga failure."""
   ```

3. **Add Compensation Logic** (`runtime/saga_compensation.py`)
   ```python
   class SagaCompensationManager:
       """Manages saga compensation."""
       
       async def compensate_saga(
           self,
           saga: Saga
       ) -> bool:
           """Compensate a failed saga (reverse order)."""
   ```

4. **Add Deterministic Replay** (`runtime/saga_replay.py`)
   ```python
   class SagaReplayManager:
       """Manages saga replay."""
       
       async def replay_saga(
           self,
           saga_id: str,
           tenant_id: str
       ) -> Saga:
           """Replay a saga from WAL."""
   ```

5. **Update Saga Coordinator**
   - Integrate retry logic
   - Integrate failure recovery
   - Integrate compensation logic
   - Integrate replay capabilities

**Success Criteria:**
- ✅ Saga steps can be retried
- ✅ Saga failures can be recovered
- ✅ Sagas can be compensated
- ✅ Sagas can be replayed deterministically

---

### Phase 2.6: Data Brain Scaffolding (Week 2, Days 6-7)

**Goal:** Build scaffolding for runtime-native data cognition

**Tasks:**

1. **Create Data Brain Structure** (`runtime/data_brain.py`)
   ```python
   class DataBrain:
       """
       Runtime-native data cognition.
       
       Owns:
       - Data references & provenance
       - Semantic projection (deterministic + expert)
       - Virtualization & hydration
       - Mutation governance
       - Execution-level attribution
       """
       
       async def register_data_reference(
           self,
           execution_id: str,
           data_reference: str,
           metadata: Dict[str, Any]
       ) -> str:
           """Register data reference with provenance."""
       
       async def get_data_provenance(
           self,
           data_reference: str
       ) -> Dict[str, Any]:
           """Get data provenance."""
       
       async def project_semantic_meaning(
           self,
           data_reference: str,
           projection_type: str = "deterministic"
       ) -> Dict[str, Any]:
           """Project semantic meaning (deterministic or expert)."""
   ```

2. **Integrate with Execution Lifecycle**
   - Register data references during execution
   - Track data provenance
   - Enable data mash without ingestion

3. **Integrate with State Surface**
   - Store data references
   - Store provenance metadata
   - Enable data virtualization

**Success Criteria:**
- ✅ Data Brain structure exists
- ✅ Data references are registered
- ✅ Data provenance is tracked
- ✅ Data Brain is integrated with execution lifecycle

---

### Phase 2.7: Runtime Service Integration (Week 3, Days 1-2)

**Goal:** Integrate all components into Runtime Service

**Tasks:**

1. **Update Runtime Service**
   - Use Execution Lifecycle Manager
   - Use Intent Model
   - Use Execution Context
   - Integrate with WAL
   - Integrate with Saga Coordinator
   - Integrate with Data Brain

2. **Add Execution Status Endpoint**
   ```python
   @app.get("/execution/{execution_id}/status")
   async def get_execution_status(
       execution_id: str,
       tenant_id: str = Query(...)
   ) -> GetExecutionStatusResponse:
       """Get execution status."""
   ```

3. **Add Execution Replay Endpoint**
   ```python
   @app.post("/execution/{execution_id}/replay")
   async def replay_execution(
       execution_id: str,
       tenant_id: str = Query(...)
   ) -> ReplayExecutionResponse:
       """Replay execution from WAL."""
   ```

4. **Add Saga Management Endpoints**
   - Get saga status
   - Retry saga step
   - Compensate saga
   - Replay saga

**Success Criteria:**
- ✅ Runtime Service integrates all components
- ✅ All execution flows through Runtime
- ✅ Execution status is queryable
- ✅ Execution replay works

---

### Phase 2.8: Testing & Validation (Week 3, Days 3-5)

**Goal:** Comprehensive testing of Runtime Execution Engine

**Tasks:**

1. **Unit Tests**
   - Intent Model validation
   - Execution Context building
   - Execution Lifecycle Manager
   - WAL operations
   - Saga operations
   - Data Brain operations

2. **Integration Tests**
   - Full execution flow (intent → completion)
   - Saga orchestration
   - Retry logic
   - Failure recovery
   - Compensation logic
   - Replay capabilities

3. **End-to-End Tests**
   - Intent submission → execution → completion
   - Saga execution with retries
   - Saga failure with compensation
   - Execution replay

**Success Criteria:**
- ✅ All unit tests pass
- ✅ All integration tests pass
- ✅ All end-to-end tests pass
- ✅ Runtime Execution Engine is production-ready

---

## Component Dependencies

### Runtime Components

```
Runtime Service
  ├── Execution Lifecycle Manager
  │   ├── Intent Model
  │   ├── Intent Validator
  │   ├── Execution Context Builder
  │   └── Execution Result
  ├── Write-Ahead Log (WAL)
  ├── Saga Coordinator
  │   ├── Saga Retry Manager
  │   ├── Saga Recovery Manager
  │   ├── Saga Compensation Manager
  │   └── Saga Replay Manager
  ├── State Surface
  ├── Data Brain
  └── Session Manager
```

### External Dependencies

- **Curator Foundation** - Capability lookup (intent → capability)
- **Smart City** - Policy validation (Security Guard, City Manager)
- **Public Works** - State management abstraction, file storage abstraction
- **Domain Services** - Implement Runtime Participation Contract

---

## Runtime Participation Contract (For Domain Services)

### Contract Interface

```python
class RuntimeParticipant(ABC):
    """Interface for domain services participating in Runtime execution."""
    
    @abstractmethod
    async def handle_intent(
        self,
        intent: Intent,
        execution_context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Handle intent execution.
        
        Returns:
            {
                "artifacts": {...},  # Domain service artifacts
                "events": [...],     # Domain service events
                "state_changes": [...]  # State transitions
            }
        """
        pass
    
    @abstractmethod
    def get_supported_intents(self) -> List[str]:
        """Return list of supported intent types."""
        pass
```

### Contract Rules

1. **No Side Effects** - Domain services return artifacts/events, Runtime persists them
2. **No Direct State Access** - Use ExecutionContext.state_surface
3. **No Direct Retries** - Runtime handles retries
4. **No Direct Orchestration** - Runtime handles orchestration
5. **Idempotent** - Same intent + context = same result

---

## Success Criteria (Phase 2 Complete)

### Functional Requirements

- ✅ **Intent Model** - Formal intent schema and validation
- ✅ **Execution Context** - Runtime context passed to domain services
- ✅ **Execution Lifecycle** - Full execution flow orchestrated
- ✅ **WAL Integration** - All execution events recorded
- ✅ **Saga Orchestration** - Retries, recovery, compensation, replay
- ✅ **Data Brain** - Runtime-native data cognition scaffolding
- ✅ **Runtime Service** - All components integrated

### Non-Functional Requirements

- ✅ **Performance** - Execution latency < 100ms (excluding domain service execution)
- ✅ **Reliability** - 99.9% execution success rate
- ✅ **Observability** - All execution events queryable
- ✅ **Replayability** - All executions replayable from WAL
- ✅ **Testability** - Comprehensive test coverage (>80%)

### Architectural Requirements

- ✅ **Single Execution Authority** - Runtime is the only component that owns execution
- ✅ **Explicit Execution** - All execution is explicit and recorded
- ✅ **Governed Execution** - All execution is governed by policy
- ✅ **Attributed Execution** - All execution is attributed to intent/session/tenant

---

## Next Steps (Phase 3)

After Phase 2 is complete:

1. **Phase 3: Civic Systems** - Build Smart City, Experience, Agentic, Platform SDK
2. **Phase 4: Domain Services** - Wrap existing services with Runtime Participation Contract
3. **Phase 5: MVP Showcase Solution** - Build MVP using Platform SDK

---

## Recommendations for Architecture Team Review

Based on platform use cases (`/docs/platform_use_cases/`), here are our recommendations for Phase 2 implementation:

### 1. Intent Schema Recommendation

**Based on Use Cases:**
- **MVP Showcase**: Content upload/parse, Insights analysis, Operations SOP/workflow creation, Solution roadmap/POC
- **Insurance Migration**: Content parse (binary + copybook), Insights quality/mapping, Operations migration workflows, Solution coexistence blueprint
- **Permit Data Mash**: Content PDF ingestion, Insights semantic interpretation, Operations compliance workflows, Runtime async updates
- **T&E Enablement**: Content parse documents/AARs, Insights extract metrics/gaps, Operations test workflows, Solution roadmap

**Recommended Intent Schema:**
```python
@dataclass
class Intent:
    """Formal intent structure."""
    intent_id: str  # UUID
    intent_type: str  # Format: "{realm}.{action}" (e.g., "content.upload", "journey.create_sop")
    realm: str  # Target realm: "content", "insights", "journey", "solution"
    session_id: str  # Required session
    tenant_id: str  # Required tenant (mandatory isolation)
    payload: Dict[str, Any]  # Realm-specific payload
    metadata: Dict[str, Any] = field(default_factory=dict)  # Source, correlation_id, solution_context
    solution_context: Optional[Dict[str, Any]] = None  # Solution-level context (for MVP showcase)
    created_at: datetime
```

**Intent Type Format:**
- `{realm}.{action}` - Single realm intent (e.g., `content.upload`, `insights.analyze`)
- `cross_realm.{action}` - Cross-realm intent (e.g., `cross_realm.data_mash`)
- `solution.{action}` - Solution-level intent (e.g., `solution.create_roadmap`)

**Critical Clarification:**
> **Intent names do NOT imply execution order or orchestration.**

An intent like `solution.generate_poc` does **not** mean Runtime knows how to "generate a POC."
It only means Runtime knows **who is allowed to try** and **how to supervise it**.

**Key Principles:**
- Intents declare *what is being attempted*
- They do not encode workflow, sequencing, or control flow
- Orchestration (if any) happens via saga primitives, not intent chaining
- Runtime is a *strict supervisor*, not a smart orchestrator

**Rationale:**
- Supports all use cases (single realm, cross-realm, solution-level)
- Clear realm routing
- Solution context propagation (MVP showcase needs this)
- Tenant isolation mandatory (enterprise requirement)
- Prevents Runtime from becoming a god-orchestrator

---

### 2. Policy Validation Integration Recommendation

**Based on Use Cases:**
- **Multi-tenant isolation**: All use cases require strict tenant isolation
- **Data access controls**: Permit data, insurance policies need access control
- **Audit requirements**: T&E use case requires full auditability
- **Compliance workflows**: Permit compliance needs policy enforcement

**Recommended Policy Validation Flow:**
```python
class PolicyValidator:
    """Validates policy before execution."""
    
    async def validate_intent(
        self,
        intent: Intent,
        session: Session
    ) -> PolicyValidationResult:
        """
        Validate intent against policy.
        
        Steps:
        1. Security Guard: Validate authN/Z (user can execute intent)
        2. City Manager: Validate tenant policy (tenant allowed for intent)
        3. Data Steward: Validate data access (user can access payload data)
        4. Return validation result with policy context
        
        Critical Invariant:
        - Policy is evaluated at intent acceptance, not mid-execution
        - Policy context is immutable once execution starts
        - Execution can be aborted later, but policy is not renegotiated mid-flight
        """
```

**Integration Points:**
- **Security Guard** (Smart City): AuthN/Z validation before execution
- **City Manager** (Smart City): Tenant policy validation
- **Data Steward** (Smart City): Data access validation
- **Policy Context**: Pass validation results to Execution Context (immutable)

**Critical Invariant:**
> **Policy is evaluated at intent acceptance, not mid-execution.**

This prevents:
- Agents re-evaluating permissions
- Services making ad-hoc decisions
- Partial execution with changing rules

You can always *abort* execution later — but you don't renegotiate policy mid-flight.

**Rationale:**
- Supports enterprise requirements (multi-tenant, audit, compliance)
- Policy validation before execution (fail fast)
- Policy context available to domain services (for conditional logic)
- Prevents policy drift during execution

---

### 3. Capability Resolution Recommendation

**Based on Use Cases:**
- **Single realm capabilities**: Content upload → content realm
- **Cross-realm capabilities**: Data mash → content + insights realms
- **Solution-level capabilities**: MVP showcase → orchestrates multiple realms
- **Intent → capability mapping**: Need to resolve intent to specific capability

**Recommended Capability Resolution Flow:**
```python
class CapabilityResolver:
    """Resolves intent to capability via Curator."""
    
    async def resolve_capability(
        self,
        intent: Intent
    ) -> CapabilityDefinition:
        """
        Resolve intent to capability.
        
        Steps:
        1. Query Curator: intent_type → capability
        2. Validate capability exists and is available
        3. Return capability definition (realm, handler, contracts)
        4. Handle cross-realm intents (resolve multiple capabilities)
        
        Critical Clarification:
        - Curator maps intent → authorized execution entry point
        - Curator does NOT decide execution strategy, sequencing, or coordination
        - That decision belongs to Solution/Realm logic, under Runtime supervision
        """
```

**Curator Integration:**
- **Intent → Capability Lookup**: `curator.lookup_capability_by_intent(intent_type)`
- **Capability Definition**: Includes realm, handler method, input/output contracts
- **Cross-Realm Support**: Resolve multiple capabilities for cross-realm intents
- **Solution-Level Support**: Resolve solution orchestrator for solution-level intents

**Critical Clarification:**
> **Curator maps intent → authorized execution entry point, not execution strategy.**

Curator resolves:
- **Who may respond to this intent**
- **What execution adapter should be used**

Curator does *not* decide:
- which realm runs first
- how cross-realm logic is coordinated
- whether agents or deterministic code is "better"

That decision belongs to the **Solution / Realm logic**, under Runtime supervision.

**Capability Definition Format:**
```python
@dataclass
class CapabilityDefinition:
    """Capability definition from Curator."""
    capability_name: str
    realm: str
    handler_method: str  # e.g., "ContentOrchestrator.handle_upload_intent"
    input_contract: Dict[str, Any]  # Expected payload structure
    output_contract: Dict[str, Any]  # Expected result structure
    determinism: str  # "deterministic" or "non-deterministic" (uses agents)
```

**Rationale:**
- Supports all use case patterns (single, cross-realm, solution-level)
- Clear intent → capability mapping
- Enables capability discovery and routing
- Supports both deterministic and agent-based capabilities

---

### 4. Data Brain Scope Recommendation

**Based on Use Cases:**
- **Data mash without ingestion**: Permit data mash use case requires this
- **Semantic interpretation**: All use cases need semantic embeddings/interpretation
- **Provenance tracking**: T&E use case requires full auditability
- **Virtualization**: Data mash feature needs data virtualization

**Recommended Minimum Viable Data Brain:**
```python
class DataBrain:
    """Runtime-native data cognition (Phase 2 MVP)."""
    
    # Phase 2 MVP (Required)
    async def register_data_reference(
        self,
        execution_id: str,
        data_reference: str,  # File reference, content reference, etc.
        metadata: Dict[str, Any]  # Source, type, realm, etc.
    ) -> str:
        """Register data reference with provenance."""
    
    async def get_data_provenance(
        self,
        data_reference: str
    ) -> Dict[str, Any]:
        """Get data provenance (execution_id, source, lineage)."""
    
    async def query_data_mash(
        self,
        content_refs: List[str],
        query_type: str = "semantic"
    ) -> Dict[str, Any]:
        """Query data mash (virtual pipeline - no ingestion)."""
    
    # Phase 3+ (Future)
    # - Semantic projection (deterministic + expert)
    # - Virtualization & hydration
    # - Mutation governance
    # - Execution-level attribution
```

**Phase 2 Scope (MVP):**
- ✅ **Data Reference Registration**: Track all data references during execution
- ✅ **Provenance Tracking**: Track data lineage (source, execution, transformations)
- ✅ **Data Mash Queries**: Enable data mash without ingestion (permit use case)
- ⏳ **Semantic Projection**: Defer to Phase 3 (Librarian integration)
- ⏳ **Virtualization**: Defer to Phase 3 (advanced feature)
- ⏳ **Mutation Governance**: Defer to Phase 3 (advanced feature)

**Critical Rule:**
> **Phase 2 Data Brain never returns raw data by default — only references.**

That single rule preserves:
- scalability
- governance
- replayability

You can always add "hydration" later.

**Rationale:**
- Supports critical use cases (data mash, provenance tracking)
- Keeps Phase 2 focused on execution engine
- Defers advanced features to Phase 3 (when Librarian is available)
- Enables data mash feature (permit use case requirement)
- Prevents over-centralizing data

---

### 5. Execution Replay Strategy Recommendation

**Based on Use Cases:**
- **Auditability**: T&E use case requires full audit trail
- **Debugging**: All use cases need debugging capabilities
- **Compliance verification**: Permit compliance needs verification
- **Migration validation**: Insurance migration needs validation

**Recommended Replay Strategy:**
```python
class ExecutionReplayManager:
    """Manages execution replay from WAL."""
    
    async def replay_execution(
        self,
        execution_id: str,
        tenant_id: str,
        replay_mode: str = "full"  # "full", "state_only", "events_only"
    ) -> ExecutionReplayResult:
        """
        Replay execution from WAL.
        
        Modes:
        - "full": Full replay (reconstruct state + re-execute)
        - "state_only": Reconstruct state only (no re-execution)
        - "events_only": Return events only (audit trail)
        """
    
    async def replay_session(
        self,
        session_id: str,
        tenant_id: str
    ) -> List[WALEvent]:
        """Replay all events for a session (chronological order)."""
    
    async def validate_execution(
        self,
        execution_id: str,
        tenant_id: str
    ) -> ValidationResult:
        """Validate execution (compliance, correctness)."""
```

**Replay Modes:**
1. **Full Replay**: Reconstruct state + re-execute (for debugging)
2. **State-Only Replay**: Reconstruct state only (for state inspection)
3. **Events-Only Replay**: Return events only (for audit trail)

**Replay Capabilities:**
- ✅ **Execution Replay**: Replay single execution from WAL
- ✅ **Session Replay**: Replay all events for a session
- ✅ **State Reconstruction**: Reconstruct execution state from WAL
- ✅ **Validation**: Validate execution (compliance, correctness)

**Critical Framing:**
> **Replay is a Runtime feature, not a debugging tool.**

That framing matters. It keeps replay:
- deterministic
- policy-aware
- safe to expose later (e.g., compliance views)

If replay is treated as "just logs," it will rot.

**Rationale:**
- Supports all use case requirements (audit, debug, compliance, validation)
- Multiple replay modes (full, state-only, events-only)
- Enables compliance verification (permit use case)
- Enables migration validation (insurance use case)
- First-class Runtime capability, not an afterthought

---

## Summary of Recommendations

| Component | Recommendation | Rationale |
|-----------|---------------|-----------|
| **Intent Schema** | `{realm}.{action}` format, solution context support | Supports all use cases (single, cross-realm, solution-level) |
| **Policy Validation** | Security Guard + City Manager + Data Steward integration | Enterprise requirements (multi-tenant, audit, compliance) |
| **Capability Resolution** | Curator lookup, capability definition format | Supports all use case patterns, enables discovery |
| **Data Brain Scope** | MVP: Reference registration, provenance, data mash | Supports critical use cases, defers advanced features |
| **Execution Replay** | Full/state-only/events-only modes | Supports audit, debug, compliance, validation requirements |

**All recommendations are based on platform use cases and support:**
- ✅ MVP Showcase (multi-realm orchestration)
- ✅ Insurance Migration (enterprise-grade, auditability)
- ✅ Permit Data Mash (data mash without ingestion)
- ✅ T&E Enablement (auditability, repeatability)

---

### 6. Runtime Boundaries Recommendation (Critical)

**Question:** What is Runtime explicitly NOT allowed to do?

**Recommended Answer:**

Runtime is a **strict supervisor**, not a smart orchestrator. Runtime explicitly does NOT:

- ❌ **Contain domain logic** - Domain logic belongs in domain services
- ❌ **Interpret data meaning** - Data interpretation belongs in domain services/agents
- ❌ **Decide business outcomes** - Business decisions belong in domain services/agents
- ❌ **Call external systems directly** - External systems are accessed through Solutions
- ❌ **Orchestrate workflows** - Orchestration happens via saga primitives, not Runtime logic
- ❌ **Make routing decisions** - Routing is determined by Curator capability lookup

**Runtime's Role:**
- ✅ Accepts intents
- ✅ Validates policy
- ✅ Records execution
- ✅ Supervises execution
- ✅ Manages state transitions
- ✅ Coordinates retries/recovery
- ✅ Enables replay

**Rationale:**
- Prevents Runtime from becoming a god-engine
- Maintains clear separation of concerns
- Keeps Runtime focused on execution governance
- Enables domain services to evolve independently

---

### 7. Failure Handling Recommendation (Critical)

**Question:** What happens when something goes wrong mid-execution?

**Recommended Answer:**

When something goes wrong mid-execution:

1. **WAL Already Recorded Intent**
   - Intent was recorded in WAL before execution started
   - Execution failure is also recorded in WAL
   - Full audit trail is preserved

2. **Saga Tracks Partial Progress**
   - Saga state reflects which steps completed
   - Saga state reflects which steps failed
   - Saga state is persisted in State Surface

3. **State Surface Reflects Last Known Good State**
   - State Surface stores execution state
   - Last known good state is queryable
   - State transitions are tracked

4. **Nurse + Conductor Coordinate Retry / Compensation**
   - Nurse (Smart City) monitors execution health
   - Conductor (Smart City) provides saga primitives
   - Runtime coordinates retry/compensation via Nurse + Conductor

5. **Replay is Possible Without Re-execution Side Effects**
   - WAL enables deterministic replay
   - Replay does not trigger side effects
   - Replay can reconstruct state without re-execution

**Failure Handling Flow:**
```python
# Execution fails mid-flight
1. Record failure in WAL
2. Update saga state (mark failed step)
3. Persist state in State Surface (last known good state)
4. Nurse detects failure (via telemetry)
5. Runtime coordinates with Nurse + Conductor:
   - Retry (if retryable)
   - Compensate (if compensation needed)
   - Abort (if non-recoverable)
6. Replay available (from WAL, no side effects)
```

**Rationale:**
- Ensures execution failures are handled gracefully
- Preserves audit trail and state
- Enables retry/compensation/replay
- Maintains execution integrity

---

## Summary of All Recommendations

| Component | Recommendation | Rationale |
|-----------|---------------|-----------|
| **Intent Schema** | `{realm}.{action}` format, solution context support | Supports all use cases, prevents Runtime from becoming orchestrator |
| **Policy Validation** | Security Guard + City Manager + Data Steward integration | Enterprise requirements, policy immutable once execution starts |
| **Capability Resolution** | Curator maps intent → entry point, not strategy | Prevents Curator from becoming god-router |
| **Data Brain Scope** | MVP: Reference registration, provenance, data mash (references only) | Supports critical use cases, prevents over-centralization |
| **Execution Replay** | Full/state-only/events-only modes (Runtime feature, not debug tool) | Supports audit, debug, compliance, validation requirements |
| **Runtime Boundaries** | Runtime is strict supervisor, not smart orchestrator | Prevents Runtime from becoming god-engine |
| **Failure Handling** | WAL + Saga + State Surface + Nurse + Conductor coordination | Ensures graceful failure handling with replay capability |

---

## Conclusion

Phase 2 builds the **Runtime Execution Engine** - the core component that makes Symphainy a "governed execution platform." Once complete, the Runtime will:

- Own all execution
- Record all execution events
- Govern all execution via policy
- Enable deterministic replay
- Provide runtime-native data cognition

**This is the foundation for everything else.**
