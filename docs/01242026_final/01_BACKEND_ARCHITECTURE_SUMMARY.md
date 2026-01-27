# Backend Architecture Summary (symphainy_platform)

**Date:** January 24, 2026  
**Status:** ✅ **COMPREHENSIVE REFERENCE**  
**Purpose:** Complete guide to backend architecture, services, patterns, and how to work with them

---

## Executive Summary

The Symphainy backend (`symphainy_platform/`) is organized into **four distinct classes** that must not collapse into each other:

1. **Runtime Foundation** - Single execution authority
2. **Civic Systems** - Governance and coordination
3. **Domain Services (Realms)** - Business logic and data access
4. **Foundations (Public Works)** - Infrastructure abstractions

**Key Principle:** Only Realms touch data. Everything else governs, observes, or intends.

---

## Service Architecture

### Service Organization

```
symphainy_platform/
├── runtime/                    ← Runtime Foundation (execution authority)
│   ├── runtime_api.py          ← Runtime HTTP API
│   ├── execution_lifecycle_manager.py
│   ├── intent_model.py
│   ├── state_surface.py        ← State management
│   ├── wal.py                  ← Write-ahead log
│   └── realm_registry.py       ← Realm registration
│
├── civic_systems/              ← Civic Systems (governance)
│   ├── experience/             ← Experience Plane (user-facing APIs)
│   │   ├── api/
│   │   │   ├── auth.py         ← Authentication endpoints
│   │   │   ├── sessions.py     ← Session management
│   │   │   ├── intents.py      ← Intent submission
│   │   │   ├── runtime_agent_websocket.py  ← WebSocket endpoint
│   │   │   └── guide_agent.py  ← Guide Agent API
│   │   ├── services/
│   │   │   └── guide_agent_service.py
│   │   └── experience_service.py  ← FastAPI app
│   │
│   ├── smart_city/             ← Smart City (governance)
│   │   └── sdk/
│   │       ├── security_guard_sdk.py  ← Authentication SDK
│   │       └── traffic_cop_sdk.py     ← Intent orchestration SDK
│   │
│   ├── agentic/                ← Agentic System (reasoning)
│   │   ├── agent_base.py       ← Agent base class (4-layer model)
│   │   ├── agents/             ← Agent implementations
│   │   ├── models/
│   │   │   └── agent_runtime_context.py  ← Layer 3 (runtime context)
│   │   └── services/
│   │
│   └── artifact_plane/         ← Artifact Plane (Purpose-Bound Outcomes)
│
└── realms/                     ← Domain Services (business logic)
    ├── content/                ← Content Realm
    │   ├── orchestrators/
    │   │   └── content_orchestrator.py
    │   ├── agents/
    │   ├── enabling_services/
    │   └── mcp_server/
    │
    ├── insights/               ← Insights Realm
    ├── journey/                ← Journey Realm
    └── outcomes/                ← Outcomes Realm
```

---

## 1. Runtime Foundation

### Purpose

> **Runtime is the sole authority for committed execution and durable system state.**

Runtime owns:
- Intent acceptance
- Execution lifecycle
- Session & tenant context
- Write-ahead log (WAL)
- Saga orchestration
- Retries & failure recovery
- Deterministic replay
- State transitions
- Runtime-native data cognition (Data Brain)

**Key Principle:** If something runs and Runtime doesn't know about it, **it is a bug**.

### Service: Runtime Service (Port 8000)

**Entry Point:** `runtime_main.py`

**Responsibilities:**
- Initialize Public Works Foundation
- Register Realms
- Initialize Execution Lifecycle Manager
- Expose Runtime HTTP API

**Key Endpoints:**
- `POST /api/session/create` - Create session
- `POST /api/intent/submit` - Submit intent for execution
- `GET /api/execution/{execution_id}/status` - Get execution status
- `GET /api/artifacts/{artifact_id}` - Get artifact
- `GET /api/realms` - List registered realms

**Key Components:**
- `ExecutionLifecycleManager` - Orchestrates intent execution
- `StateSurface` - Manages session and execution state
- `RealmRegistry` - Tracks registered realms
- `WriteAheadLog` - Records all state transitions
- `TransactionalOutbox` - Publishes events

### Runtime Participation Contract

Every domain service must:
- Declare which **intents** it supports
- Accept a **runtime execution context**
- Return **artifacts and events**, not side effects
- Never bypass Runtime for state, retries, or orchestration

**Example:**
```python
async def handle_intent(
    intent: Intent,
    context: ExecutionContext
) -> Dict[str, Any]:
    # Process intent
    # Return artifacts (not side effects)
    return {
        "artifact_type": "result",
        "artifact": {...},
        "events": [...]
    }
```

---

## 2. Civic Systems

### 2.1 Experience Plane

**Purpose:** Translate user actions into intents.

**Service:** Experience Service (Port 8001)

**Entry Point:** `experience_main.py` → `experience_service.py`

**Responsibilities:**
- User-facing APIs
- Session management
- Authentication
- WebSocket endpoints
- Guide Agent Service
- Intent submission interface

**Key Endpoints:**
- `POST /api/auth/login` - Authenticate user
- `POST /api/auth/register` - Register user
- `POST /api/sessions/create` - Create session
- `GET /api/sessions/{session_id}` - Get session
- `POST /api/intent/submit` - Submit intent
- `WebSocket /api/runtime/agent` - Agent communication

**Key Principle:** Experience never calls domain services directly. Experience never manages workflows. Experience never owns state.

### 2.2 Smart City

**Purpose:** Govern how execution is allowed to occur.

**Components:**
- **Security Guard SDK** - Authentication abstraction
- **Traffic Cop SDK** - Intent orchestration, session coordination
- **Data Steward SDK** - Data boundaries, materialization
- **Curator** - Capability promotion
- **Librarian** - Semantic schemas
- **Post Office** - Event routing
- **Conductor** - Workflow & saga primitives
- **Nurse** - Telemetry, retries, self-healing

**Key Principle:** Smart City is purpose-agnostic. It never decides *what* should happen or *why*.

### 2.3 Agentic System

**Purpose:** Enable reasoning under constraint.

**Components:**
- **AgentBase** - Base class for all agents (4-layer model)
- **Agent Registry** - Agent definitions and postures
- **MCP Client Manager** - Tool integration
- **Telemetry Service** - Agent execution tracking

**4-Layer Agent Model:**
1. **Layer 1: AgentDefinition** - Stable identity, constitution, capabilities
2. **Layer 2: AgentPosture** - Behavioral tuning, LLM defaults, compliance mode
3. **Layer 3: AgentRuntimeContext** - Ephemeral context, assembled at runtime
4. **Layer 4: Prompt Assembly** - Derived from layers 1-3

**Key Principle:** Agents reason. They do not execute. Agents never write to databases, call infrastructure directly, or orchestrate workflows.

### 2.4 Artifact Plane

**Purpose:** Manage Purpose-Bound Outcomes (roadmaps, POCs, blueprints, SOPs).

**Components:**
- Artifact registry (Supabase)
- Artifact storage (GCS)
- Lifecycle state management
- Versioning
- Dependency tracking

---

## 3. Domain Services (Realms)

### Purpose

> **Only Realm domain services perform data access and mutation, always via Public Works abstractions.**

Realms:
- Implement rich internal logic
- Can be complex and opinionated
- **Do not own execution or state**
- **Do not orchestrate workflows**
- **Do not persist authoritative data**

They participate in execution **only via Runtime contracts**.

### Realm Structure

Each realm follows this structure:

```
realm_name/
├── {realm_name}_realm.py       ← Realm registration
├── orchestrators/
│   └── {realm}_orchestrator.py ← Intent handlers
├── agents/
│   └── {realm}_liaison_agent.py
├── enabling_services/          ← Domain-specific services
└── mcp_server/                 ← MCP server for agent tools
```

### Content Realm

**Purpose:** Ingest, parse, embeddings, canonical facts.

**Key Services:**
- `FileParserService` - Parse files (PDF, Excel, binary, etc.)
- `DeterministicEmbeddingService` - Generate deterministic embeddings
- `EmbeddingService` - Generate semantic embeddings

**Key Intents:**
- `upload_file`
- `parse_file`
- `generate_embeddings`

### Insights Realm

**Purpose:** Interpretation, analysis, mapping, querying.

**Key Services:**
- `DataQualityService` - Assess data quality
- `SemanticMatchingService` - Semantic matching
- `StructuredExtractionService` - Extract structured data
- `LineageVisualizationService` - Track data lineage

**Key Intents:**
- `analyze_data`
- `extract_structured_data`
- `assess_quality`

### Journey Realm

**Purpose:** SOPs, workflows, optimization recommendations.

**Key Services:**
- `WorkflowConversionService` - Convert BPMN to workflows
- `CoexistenceAnalysisService` - Analyze coexistence opportunities
- `VisualGenerationService` - Generate workflow visuals

**Key Intents:**
- `create_sop`
- `analyze_coexistence`
- `generate_workflow`

### Outcomes Realm

**Purpose:** Synthesis, roadmaps, POCs, proposals.

**Key Services:**
- `SolutionSynthesisService` - Synthesize solutions
- `POCGenerationService` - Generate POC proposals
- `RoadmapGenerationService` - Generate roadmaps
- `ExportService` - Export artifacts

**Key Intents:**
- `synthesize_solution`
- `generate_poc`
- `generate_roadmap`

---

## 4. Foundations (Public Works)

### Purpose

> **Public Works is a governance boundary, not a convenience layer.**

Public Works provides:
- Infrastructure abstractions (swappable)
- Adapter pattern (Layer 0: Adapters, Layer 1: Abstractions)
- Dependency injection
- Governance enforcement

### Key Abstractions

**State Management:**
- `StateManagementAbstraction` - Redis-backed state

**File Storage:**
- `FileStorageAbstraction` - GCS/S3 file storage
- `ArtifactStorageAbstraction` - Artifact storage

**Data Access:**
- `SemanticDataAbstraction` - ArangoDB semantic data
- `DeterministicComputeAbstraction` - DuckDB deterministic compute
- `RegistryAbstraction` - Supabase registries

**Authentication:**
- `AuthAbstraction` - Supabase authentication
- `TenantAbstraction` - Tenant management

**Processing:**
- `PdfProcessingAbstraction`, `ExcelProcessingAbstraction`, etc.
- `MainframeProcessingAbstraction` - Mainframe file processing

**Key Principle:** All infrastructure access must go through Public Works abstractions. No direct Redis, ArangoDB, GCS, or Supabase calls in business logic.

---

## Service Communication Patterns

### Experience Plane → Runtime

**Pattern:** HTTP API calls

**Examples:**
- `POST /api/session/create` - Create session
- `POST /api/intent/submit` - Submit intent
- `GET /api/execution/{id}/status` - Get execution status

**Key Principle:** Experience submits intents. Runtime orchestrates execution.

### Runtime → Realms

**Pattern:** Direct invocation via orchestrators

**Flow:**
1. Runtime receives intent
2. Runtime routes to appropriate realm orchestrator
3. Orchestrator handles intent
4. Orchestrator returns artifacts
5. Runtime records execution in WAL

**Key Principle:** Runtime orchestrates. Realms execute.

### Realms → Public Works

**Pattern:** Dependency injection via `public_works` parameter

**Example:**
```python
class ContentOrchestrator:
    def __init__(self, public_works: PublicWorksFoundationService):
        self.file_storage = public_works.get_file_storage_abstraction()
        self.semantic_data = public_works.get_semantic_data_abstraction()
```

**Key Principle:** Realms use abstractions, not adapters directly.

---

## Data Classification Framework

### Four Classes of Data

1. **Working Materials** - Temporary, time-bound (FMS, GCS)
   - TTL enforced by policy
   - Purged when expired
   - Examples: Raw uploaded files, parsed results (temporary)

2. **Records of Fact** - Persistent meaning (Supabase + ArangoDB)
   - Must persist (auditable, reproducible)
   - Do NOT require original file to persist
   - Examples: Deterministic embeddings, semantic embeddings, interpretations

3. **Purpose-Bound Outcomes** - Intentional deliverables (Artifact Plane)
   - Owner, purpose, lifecycle states
   - Examples: Roadmaps, POCs, blueprints, SOPs

4. **Platform DNA** - Generalized capability (Supabase registries)
   - De-identified, generalizable, policy-approved
   - Examples: Promoted intents, realms, solutions

**Key Principle:** Classification by purpose, not format.

---

## Agent Architecture (4-Layer Model)

### Layer 1: AgentDefinition (Platform DNA)

**Location:** Supabase registry (`agent_definitions`)

**Contains:**
- Stable identity
- Constitution
- Capabilities
- Permissions

**Example:**
```json
{
  "agent_id": "guide_agent",
  "constitution": "You are a helpful guide...",
  "capabilities": ["platform_navigation", "intent_analysis"],
  "permissions": ["read_session", "submit_intent"]
}
```

### Layer 2: AgentPosture (Tenant/Solution)

**Location:** Supabase registry (`agent_postures`)

**Contains:**
- Behavioral tuning
- LLM defaults
- Compliance mode

**Example:**
```json
{
  "posture_id": "insurance_guide_posture",
  "agent_id": "guide_agent",
  "llm_model": "gpt-4o-mini",
  "temperature": 0.3,
  "compliance_mode": "strict"
}
```

### Layer 3: AgentRuntimeContext (Journey/Session)

**Location:** Assembled at runtime (never stored)

**Contains:**
- Session context
- Business context
- User journey state
- Ephemeral context

**Example:**
```python
runtime_context = AgentRuntimeContext(
    session_id="...",
    tenant_id="...",
    user_id="...",
    business_context={"current_pillar": "content"},
    journey_state={"step": "upload_file"}
)
```

### Layer 4: Prompt Assembly

**Location:** Derived from layers 1-3

**Process:**
1. Load AgentDefinition (Layer 1)
2. Load AgentPosture (Layer 2)
3. Assemble AgentRuntimeContext (Layer 3)
4. Assemble system message from layers 1-3
5. Assemble user message from request + runtime context
6. Call `_process_with_assembled_prompt()`

**Key Principle:** All agents must implement `_process_with_assembled_prompt()`.

---

## MCP (Micro-Collaboration Protocol)

### Purpose

MCP enables agents to use realm services as tools.

**Pattern:**
1. Agent calls `use_tool("realm_action", params, context)`
2. MCP Client Manager routes to appropriate realm MCP server
3. Realm MCP server calls realm service
4. Service executes and returns result
5. Result returned to agent

**Key Principle:** Agents use MCP tools. Agents never call services directly.

---

## Key Patterns

### Pattern 1: Intent Submission

```python
# Experience Plane
intent = {
    "type": "parse_file",
    "file_id": "...",
    "session_id": "..."
}
result = await runtime_client.submit_intent(intent)

# Runtime
execution = await execution_lifecycle_manager.execute_intent(intent, context)

# Realm Orchestrator
artifact = await content_orchestrator.handle_intent(intent, context)
```

### Pattern 2: State Management

```python
# Runtime manages state
await state_surface.store_session_state(session_id, tenant_id, state)

# Realms read state (metadata only)
metadata = await context.state_surface.get_file_metadata(file_id)

# Realms never write state directly
# All state changes go through Runtime
```

### Pattern 3: Public Works Usage

```python
# ✅ CORRECT: Use abstraction
file_storage = public_works.get_file_storage_abstraction()
await file_storage.store_file(file_id, file_data)

# ❌ WRONG: Direct adapter access
gcs_adapter = public_works.gcs_adapter  # Don't do this
```

---

## What to Do / What Not to Do

### ✅ DO

- Use Public Works abstractions for all infrastructure
- Return artifacts from realm orchestrators
- Use Runtime for all execution
- Implement `_process_with_assembled_prompt()` in agents
- Use MCP tools for agent-service communication
- Classify data correctly (Working Material vs Record of Fact)

### ❌ DON'T

- Call infrastructure directly (Redis, ArangoDB, GCS, Supabase)
- Put data logic in Runtime
- Execute outside Runtime
- Call services directly from agents
- Mix data classes in same storage
- Bypass Runtime for state, retries, or orchestration

---

## Common Issues & Fixes

### Issue: "Agent can't instantiate - missing _process_with_assembled_prompt"

**Fix:** Implement `_process_with_assembled_prompt()` method in agent class.

**Pattern:**
```python
async def _process_with_assembled_prompt(
    self,
    system_message: str,
    user_message: str,
    runtime_context: AgentRuntimeContext,
    context: ExecutionContext
) -> Dict[str, Any]:
    # Extract request from user_message/runtime_context
    # Route to appropriate handler
    # Return artifact
```

### Issue: "AttributeError: 'PublicWorksFoundationService' object has no attribute 'get_X'"

**Fix:** Use attribute access, not method calls.

**Pattern:**
```python
# ✅ CORRECT
semantic_data = public_works.semantic_data_abstraction

# ❌ WRONG
semantic_data = public_works.get_semantic_data_abstraction()
```

### Issue: "Realm orchestrator trying to access data directly"

**Fix:** Use Public Works abstractions.

**Pattern:**
```python
# ✅ CORRECT
file_storage = public_works.get_file_storage_abstraction()
file_data = await file_storage.retrieve_file(file_id)

# ❌ WRONG
file_data = await context.state_surface.get_file(file_id)
```

---

## Testing Patterns

### Unit Tests

Test individual components in isolation with mocked abstractions.

### Integration Tests

Test component interactions with real abstractions (but mocked adapters).

### E2E Tests

Test full flows with real infrastructure.

**Key Principle:** Tests must fail if code has cheats. No tests that pass with stubs.

---

## Next Steps

1. Review this summary
2. Understand service boundaries
3. Follow patterns when adding new features
4. Use Public Works abstractions
5. Return artifacts, not side effects

---

**Last Updated:** January 24, 2026  
**Status:** ✅ **COMPREHENSIVE REFERENCE**
