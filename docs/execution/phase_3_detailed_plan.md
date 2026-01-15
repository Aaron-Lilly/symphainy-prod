# Phase 3: Detailed Implementation Plan

**Date:** January 2026  
**Status:** 🎯 Ready to Execute  
**Dependencies:** Phase 2 Complete

---

## Executive Summary

This document provides a detailed implementation plan for Phase 3, addressing:

1. **Smart City SDK + Primitives** - Operational governance brain (350k policies support, MVP-lightweight)
2. **Experience Plane** - User interaction layer with Traefik integration
3. **Agentic SDK** - Extremely robust agent framework for multiple agent types

---

## Part 1: Smart City SDK + Primitives

### 1.1 Architecture Overview

**Key Principle:** Smart City is the operational governance brain. It must be:
- **Robust enough** to support 350k policies scenario
- **Lightweight enough** for MVP showcase with minimal testing overhead
- **Equivalent or better** than existing implementations in `/symphainy_source/`

**Architecture Pattern:**
```
Smart City
├── SDK (Coordination Logic)
│   ├── Used by: Experience, Solution, Realms
│   ├── Provides: Coordination, orchestration, service discovery
│   └── Pattern: Service-like APIs, but SDK-based (no direct service calls)
│
└── Primitives (Policy Decisions)
    ├── Used by: Runtime only
    ├── Provides: Policy validation, governance checks, authorization
    └── Pattern: Pure functions, no side effects, deterministic
```

### 1.2 Smart City Roles (9 Roles)

Based on `/symphainy_source/` analysis, we need to implement:

| Role | Responsibility | SDK Capabilities | Primitive Capabilities |
|------|---------------|-----------------|------------------------|
| **City Manager** | Platform lifecycle, realm activation | `bootstrap_platform()`, `activate_realm()`, `get_platform_state()` | `validate_realm_activation()`, `check_lifecycle_state()` |
| **Security Guard** | AuthN/Z, zero-trust, multi-tenancy | `authenticate()`, `authorize()`, `get_tenant_context()` | `check_permission()`, `validate_tenant_access()` |
| **Traffic Cop** | Sessions, execution IDs, correlation | `create_session()`, `get_session()`, `correlate_execution()` | `validate_session()`, `check_rate_limit()` |
| **Post Office** | Event routing, ordering, WebSocket | `route_event()`, `publish_event()`, `subscribe_to_stream()` | `validate_event_routing()`, `check_event_order()` |
| **Librarian** | Semantic schemas, knowledge discovery | `search_knowledge()`, `get_schema()`, `discover_relationships()` | `validate_schema_access()`, `check_knowledge_permission()` |
| **Data Steward** | Data boundaries, contracts, provenance | `record_provenance()`, `get_data_contract()`, `validate_data_access()` | `check_data_permission()`, `validate_provenance_chain()` |
| **Conductor** | Workflow, saga primitives | `create_workflow()`, `execute_saga_step()`, `get_workflow_state()` | `validate_workflow_transition()`, `check_saga_constraints()` |
| **Nurse** | Telemetry, retries, self-healing | `record_telemetry()`, `schedule_retry()`, `get_health_status()` | `check_retry_policy()`, `validate_telemetry_access()` |
| **Curator** | Capability, agent, domain registries | `register_capability()`, `discover_agents()`, `get_domain_registry()` | `validate_capability_registration()`, `check_registry_access()` |

**⚠️ Curator Special Constraint:**
- **Curator SDK** → Used by Solution & Smart City (registration, discovery)
- **Curator Data** → Visible to Runtime (read-only, snapshotted registry state)
- **Runtime** → Never calls Curator SDK methods, only consumes snapshotted registry state

### 1.3 Implementation Strategy

#### Phase 1: Core SDK (MVP-Lightweight)
**Goal:** Get MVP showcase working with minimal overhead

**Priority Roles (MVP):**
1. **Security Guard** - Essential for multi-tenancy and auth
2. **Traffic Cop** - Essential for session management
3. **Post Office** - Essential for event routing and WebSocket

**Implementation:**
- SDK: Simple coordination methods (no complex orchestration)
- Primitives: Basic policy checks (permission validation, rate limiting)
- Storage: Lightweight (Redis for hot data, minimal ArangoDB for durable)

#### Phase 2: Full SDK (350k Policies Support)
**Goal:** Support 350k policies scenario

**All 9 Roles:**
- SDK: Full coordination logic (equivalent to `/symphainy_source/`)
- Primitives: Sophisticated policy engine (rule evaluation, policy caching)
- Storage: Optimized (Redis for hot policies, ArangoDB for policy graph, Supabase for policy metadata)

**Policy Engine Design:**
- **Policy Storage:** ArangoDB graph (policies as nodes, relationships as dependencies)
- **Policy Caching:** Redis (hot policies cached with TTL)
- **Policy Evaluation:** Deterministic, pure functions (primitives)
- **Policy Updates:** Event-driven (Post Office publishes policy change events)

### 1.4 File Structure

```
symphainy_platform/civic_systems/smart_city/
├── sdk/
│   ├── __init__.py
│   ├── city_manager_sdk.py      # Platform lifecycle coordination
│   ├── security_guard_sdk.py     # AuthN/Z coordination
│   ├── traffic_cop_sdk.py        # Session coordination
│   ├── post_office_sdk.py        # Event routing coordination
│   ├── librarian_sdk.py          # Knowledge discovery coordination
│   ├── data_steward_sdk.py       # Data governance coordination
│   ├── conductor_sdk.py          # Workflow coordination
│   ├── nurse_sdk.py              # Telemetry coordination
│   └── curator_sdk.py            # Capability registry coordination
│
└── primitives/
    ├── __init__.py
    ├── city_manager_primitives.py
    ├── security_guard_primitives.py
    ├── traffic_cop_primitives.py
    ├── post_office_primitives.py
    ├── librarian_primitives.py
    ├── data_steward_primitives.py
    ├── conductor_primitives.py
    ├── nurse_primitives.py
    └── curator_primitives.py
```

### 1.5 SDK vs Primitives Pattern

**⚠️ CRITICAL ARCHITECTURAL CONSTRAINT:**
> **SDKs must NOT depend on Runtime.**
> 
> SDKs prepare execution. Runtime validates and executes it.
> 
> If SDKs depend on Runtime, you collapse the governance → execution boundary.

**SDK Dependencies (Allowed):**
- ✅ Public Works abstractions
- ✅ Registries
- ✅ Policy libraries
- ✅ Context objects

**SDK Dependencies (Forbidden):**
- ❌ Runtime (direct dependency)
- ❌ Execution lifecycle managers
- ❌ State Surface (direct access)

**SDK Example (Coordination):**
```python
# symphainy_platform/civic_systems/smart_city/sdk/security_guard_sdk.py
class SecurityGuardSDK:
    """SDK for Security Guard coordination (used by Experience, Solution, Realms)."""
    
    def __init__(
        self,
        auth_abstraction: AuthenticationProtocol,
        tenant_abstraction: TenancyProtocol,
        policy_resolver: PolicyResolver
    ):
        """
        Initialize SDK with Public Works abstractions only.
        
        NO Runtime dependency - SDKs prepare execution, Runtime executes it.
        """
        self.auth_abstraction = auth_abstraction
        self.tenant_abstraction = tenant_abstraction
        self.policy_resolver = policy_resolver
    
    async def authenticate(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        Coordinate authentication (SDK - prepares execution contract).
        
        Returns execution-ready contract that Runtime will validate via primitives.
        """
        # 1. Call auth abstraction
        auth_result = await self.auth_abstraction.authenticate(credentials)
        
        # 2. Get tenant context
        tenant_context = await self.tenant_abstraction.get_tenant_context(auth_result.user_id)
        
        # 3. Resolve policies (preparation, not validation)
        policies = await self.policy_resolver.get_policies(tenant_context.tenant_id)
        
        # 4. Return coordination result (execution contract)
        return {
            "user_id": auth_result.user_id,
            "tenant_id": tenant_context.tenant_id,
            "permissions": tenant_context.permissions,
            "policies": policies,  # Prepared for Runtime validation
            "execution_contract": {
                "action": "authenticate",
                "tenant_id": tenant_context.tenant_id,
                "user_id": auth_result.user_id
            }
        }
```

**Primitive Example (Policy Decision):**
```python
# symphainy_platform/civic_systems/smart_city/primitives/security_guard_primitives.py
class SecurityGuardPrimitives:
    """Primitives for Security Guard policy decisions (used by Runtime only)."""
    
    @staticmethod
    async def check_permission(
        user_id: str,
        tenant_id: str,
        action: str,
        resource: str,
        policy_store: PolicyStore
    ) -> bool:
        """Check if user has permission (Primitive - pure function, no side effects)."""
        # 1. Load policies (from cache or store)
        policies = await policy_store.get_policies(tenant_id, action, resource)
        
        # 2. Evaluate policies (deterministic)
        for policy in policies:
            if not policy.evaluate(user_id, tenant_id, action, resource):
                return False
        
        return True
```

---

## Part 2: Experience Plane

### 2.1 Architecture Overview

**Key Principle:** Experience translates external interaction into intent. It never:
- Calls domain services directly
- Manages workflows
- Owns state

**Traefik Integration:**
```
┌─────────────┐
│   Client    │
│  (Browser)  │
└──────┬──────┘
       │ HTTP/WebSocket
       ▼
┌─────────────┐
│   Traefik   │  ← Infrastructure Layer (API Gateway)
│  (Port 80)  │     - TLS termination
└──────┬──────┘     - Load balancing
       │             - Routing rules
       │             - Rate limiting (infrastructure)
       ▼
┌─────────────┐
│ Experience  │  ← Application Layer (Experience Service)
│  (Port 8001)│     - Session management
└──────┬──────┘     - Intent submission
       │             - WebSocket streaming
       │             - Authentication coordination
       ▼
┌─────────────┐
│   Runtime   │  ← Execution Layer
│  (Port 8000)│     - Intent acceptance
└─────────────┘     - Execution orchestration
```

### 2.2 Traefik Configuration

**Role:** Infrastructure concerns only
- **TLS termination** (HTTPS → HTTP internally)
- **Load balancing** (multiple Experience instances)
- **Routing rules** (path-based routing)
- **Rate limiting** (infrastructure-level, not business logic)
- **Health checks** (service discovery via Consul)

**Experience Service Role:** Application concerns
- **Session management** (via Traffic Cop SDK → Runtime)
- **Intent submission** (via Runtime)
- **WebSocket streaming** (real-time updates)
- **Authentication coordination** (via Security Guard SDK)

### 2.3 Implementation Strategy

#### Option A: Separate FastAPI Service (Recommended)
**Pros:**
- Clear separation of concerns
- Independent scaling
- Easier testing
- Aligns with microservices architecture

**Cons:**
- Additional service to manage
- More complex deployment

**Implementation:**
- Separate FastAPI service (`experience_service.py`)
- Runs on port 8001 (or configurable)
- Traefik routes `/api/*` to Experience service
- Experience service calls Runtime via HTTP (internal network)

#### Option B: Integrated into Runtime Service
**Pros:**
- Simpler deployment
- Fewer services

**Cons:**
- Mixing concerns (Experience + Runtime)
- Harder to scale independently
- Not aligned with architecture

**Recommendation:** **Option A (Separate Service)**

### 2.4 File Structure

```
symphainy_platform/civic_systems/experience/
├── __init__.py
├── experience_service.py        # FastAPI service
├── api/
│   ├── __init__.py
│   ├── sessions.py              # Session endpoints
│   ├── intents.py               # Intent submission endpoints
│   └── websocket.py             # WebSocket streaming
├── models/
│   ├── __init__.py
│   ├── session_model.py         # Session schema
│   └── intent_request_model.py  # Intent request schema
└── sdk/
    └── __init__.py
    └── runtime_client.py        # HTTP client for Runtime
```

### 2.5 Experience Service API

**Endpoints:**
```python
# POST /api/session/create
# - Coordinates session creation via Traffic Cop SDK
# - Traffic Cop SDK prepares session intent
# - Experience submits intent to Runtime
# - Runtime validates via primitives and creates session
# - Returns session_id

# POST /api/intent/submit
# - Submits intent via Runtime
# - Returns execution_id

# WebSocket /api/execution/stream
# - Streams execution updates
# - Real-time progress, events, completion
```

**⚠️ Session Creation Flow (Corrected):**
1. Experience calls **TrafficCopSDK.create_session(...)**
2. SDK prepares session intent + metadata (execution contract)
3. Experience submits that intent to Runtime
4. Runtime validates via Traffic Cop primitives
5. Runtime creates session + state surface
6. Experience receives session_id

This keeps:
- Session semantics centralized (Traffic Cop SDK)
- Experience thin (coordination only)
- Runtime authoritative (validation + execution)

**Example Implementation:**
```python
# symphainy_platform/civic_systems/experience/experience_service.py
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Symphainy Experience Service")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import SDKs (NO Runtime dependency)
from symphainy_platform.civic_systems.smart_city.sdk.security_guard_sdk import SecurityGuardSDK
from symphainy_platform.civic_systems.smart_city.sdk.traffic_cop_sdk import TrafficCopSDK
from symphainy_platform.civic_systems.experience.sdk.runtime_client import RuntimeClient

# Initialize SDKs (Public Works abstractions only, NO Runtime)
public_works = get_public_works()  # From DI container
security_guard_sdk = SecurityGuardSDK(
    auth_abstraction=public_works.get_auth_abstraction(),
    tenant_abstraction=public_works.get_tenant_abstraction(),
    policy_resolver=policy_resolver  # Policy library, not Runtime
)
traffic_cop_sdk = TrafficCopSDK(
    state_abstraction=public_works.get_state_abstraction(),
    policy_resolver=policy_resolver
)
runtime_client = RuntimeClient(runtime_url="http://runtime:8000")

@app.post("/api/session/create")
async def create_session(request: SessionCreateRequest):
    """
    Create session via Traffic Cop SDK → Runtime.
    
    Flow:
    1. Authenticate (via Security Guard SDK)
    2. Prepare session intent (via Traffic Cop SDK)
    3. Submit intent to Runtime
    4. Runtime validates via primitives and creates session
    """
    # 1. Authenticate (via Security Guard SDK)
    auth_result = await security_guard_sdk.authenticate(request.credentials)
    
    # 2. Prepare session intent (via Traffic Cop SDK)
    session_intent = await traffic_cop_sdk.create_session_intent(
        tenant_id=auth_result.tenant_id,
        user_id=auth_result.user_id,
        metadata=request.metadata
    )
    
    # 3. Submit intent to Runtime (Runtime validates via primitives)
    execution = await runtime_client.submit_intent(session_intent)
    
    # 4. Extract session_id from execution result
    return {"session_id": execution.artifacts.get("session_id")}

@app.post("/api/intent/submit")
async def submit_intent(request: IntentSubmitRequest):
    """Submit intent via Runtime."""
    # 1. Validate session (via Traffic Cop SDK - prepares validation contract)
    session_validation = await traffic_cop_sdk.validate_session(request.session_id)
    
    # 2. Prepare intent (add session context)
    intent = request.intent
    intent.session_id = session_validation.session_id
    intent.tenant_id = session_validation.tenant_id
    
    # 3. Submit intent to Runtime (Runtime validates via primitives)
    execution = await runtime_client.submit_intent(intent)
    
    return {"execution_id": execution.execution_id}

@app.websocket("/api/execution/stream")
async def stream_execution(websocket: WebSocket, execution_id: str):
    """Stream execution updates via WebSocket."""
    await websocket.accept()
    
    # Subscribe to execution events (via Runtime WebSocket)
    async for event in runtime_client.stream_execution(execution_id):
        await websocket.send_json(event)
```

### 2.6 Traefik Configuration

**docker-compose.yml:**
```yaml
traefik:
  image: traefik:v3.0
  ports:
    - "80:80"
    - "443:443"
    - "8080:8080"  # Dashboard
  command:
    - --api.dashboard=true
    - --api.insecure=true
    - --providers.docker=true
    - --providers.docker.exposedbydefault=false
    - --entrypoints.web.address=:80
    - --entrypoints.websecure.address=:443
    - --providers.consul=true
    - --providers.consul.endpoint=consul:8500
  volumes:
    - /var/run/docker.sock:/var/run/docker.sock:ro
  networks:
    - symphainy_net

experience:
  build:
    context: .
    dockerfile: Dockerfile.experience
  labels:
    - "traefik.enable=true"
    - "traefik.http.routers.experience.rule=Host(`api.symphainy.local`) && PathPrefix(`/api`)"
    - "traefik.http.routers.experience.entrypoints=web"
    - "traefik.http.services.experience.loadbalancer.server.port=8001"
  networks:
    - symphainy_net
  depends_on:
    - runtime
    - consul
```

---

## Part 3: Agentic SDK

### 3.1 Architecture Overview

**Key Principle:** Agents reason. They do not execute. Agents operate **only inside Runtime execution**.

**⚠️ CRITICAL ARCHITECTURAL CONSTRAINT:**
> **Agents may collaborate to produce proposals and reasoning artifacts, but may not orchestrate execution or commit side effects; all agent collaboration is policy-governed and ratified by Solution and Smart City.**

**The Core Distinction:**
1. **Reasoning collaboration** ✅ allowed
2. **Proposal composition** ✅ allowed
3. **Execution orchestration** ❌ forbidden

**Mental Model:** Agents are in a **design studio**, not a factory.
- ✅ They can: Talk, sketch, ask for help, refine ideas, propose plans
- ❌ They cannot: Pull levers, start machines, commit changes

**Agent Types (from requirements):**
1. **Stateless Agents** - Generate deterministic/semantic meaning of client data
2. **Chat Agents** - Multiple levels, varied state awareness
3. **EDA Analysis Agents** - Pandas-based, business insights
4. **Workflow Optimization Agents** - Review workflows, suggest Coexistence optimizations
5. **Roadmap/POC Proposal Agents** - Context-aware, journey-informed

**Architecture Pattern:**
```
Agentic SDK
├── Core Framework
│   ├── AgentBase (ABC)
│   ├── AgentRegistry
│   ├── AgentFactory
│   └── CollaborationEngine (Policy-Governed)
│
├── Agent Types
│   ├── StatelessAgentBase
│   ├── ConversationalAgentBase
│   ├── AnalysisAgentBase
│   ├── OptimizationAgentBase
│   └── ProposalAgentBase
│
├── Collaboration
│   ├── AgentCollaborationPolicy (Policy-Governed)
│   ├── ContributionRequest (Non-Executing)
│   └── CollaborationRouter (Smart City Validated)
│
└── Platform Integration
    ├── Smart City MCP Tools
    ├── Runtime Execution Context
    └── Session State Management
```

### 3.2 Agent Base Design

**Inspired by `/symphainy_source/` but evolved:**
- **Pure dependency injection** (no DI container coupling)
- **Runtime execution context** (agents operate inside Runtime)
- **Smart City SDK integration** (via MCP tools, not direct calls)
- **Structured output** (AGUI schema support)
- **Policy-aware** (governance hooks)

**Key Methods:**
```python
class AgentBase(ABC):
    """Base class for all agents."""
    
    @abstractmethod
    async def process_request(
        self,
        request: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Process a request using agent capabilities.
        
        Returns: Non-executing artifacts only (proposals, blueprints, ranked options).
        """
        pass
    
    @abstractmethod
    async def get_agent_description(self) -> str:
        """Get agent description for discovery."""
        pass
    
    # Platform integration
    async def use_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Use a Smart City tool (via MCP)."""
        pass
    
    async def get_session_state(self, session_id: str) -> Dict[str, Any]:
        """Get session state (via Runtime)."""
        pass
    
    # Agent collaboration (Policy-Governed)
    async def request_contribution(
        self,
        agent_type: str,
        request: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Request a bounded contribution from another agent (Policy-Governed).
        
        This is NOT orchestration - it's reasoning collaboration.
        Returns non-executing artifacts only (proposals, blueprints).
        
        Flow:
        1. Agent emits contribution_request
        2. Runtime asks Smart City primitives: Is this allowed?
        3. If allowed, Runtime routes to target agent
        4. Target agent returns non-executing artifact
        5. No side effects, no execution, no commits
        
        Args:
            agent_type: Type of agent to request contribution from
            request: Contribution request (purpose, constraints, data)
            context: Execution context
        
        Returns:
            Non-executing artifact (proposal, blueprint, ranked options)
        """
        # Implementation validates via Smart City primitives
        # Returns policy-governed collaboration result
        pass
```

**⚠️ The "No Commit" Rule:**
Every agent output must be one of:

| Output Type        | Allowed                     | Notes                           |
| ------------------ | --------------------------- | ------------------------------- |
| Proposal           | ✅                           | Non-executing reasoning artifact |
| Blueprint          | ✅                           | Design structure, not execution  |
| Ranked options     | ✅                           | Suggestions for downstream      |
| Suggested intents  | ✅                           | Intent proposals, not execution |
| Execution plan     | ⚠️                           | Only if Solution-owned           |
| State mutation     | ❌                           | Forbidden - no side effects     |
| Service invocation | ❌                           | Forbidden - no orchestration     |

> **Agents may only emit artifacts that require downstream ratification.**

### 3.3 Agent Type Implementations

#### 3.3.1 Stateless Agent
**Purpose:** Generate deterministic/semantic meaning of client data

**Implementation:**
```python
class StatelessAgentBase(AgentBase):
    """Base for stateless agents (no session state)."""
    
    async def process_request(
        self,
        request: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Process request without session state."""
        # 1. Extract data from request
        data = request.get("data")
        
        # 2. Generate semantic meaning (deterministic)
        semantic_meaning = await self.generate_semantic_meaning(data)
        
        # 3. Return structured output
        return {
            "semantic_meaning": semantic_meaning,
            "deterministic": True
        }
```

#### 3.3.2 Conversational Agent
**Purpose:** Chat agents with varied state awareness

**Implementation:**
```python
class ConversationalAgentBase(AgentBase):
    """Base for conversational agents (session-aware)."""
    
    def __init__(self, state_awareness: str = "full"):
        """
        Args:
            state_awareness: "full", "partial", "none"
        """
        self.state_awareness = state_awareness
    
    async def process_request(
        self,
        request: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Process conversational request with state awareness."""
        # 1. Get session state (if state_awareness != "none")
        session_state = None
        if self.state_awareness != "none":
            session_state = await self.get_session_state(context.session_id)
        
        # 2. Process conversation
        response = await self.generate_response(
            message=request.get("message"),
            session_state=session_state,
            context=context
        )
        
        # 3. Update session state (if state_awareness == "full")
        if self.state_awareness == "full":
            await self.update_session_state(context.session_id, response)
        
        return response
```

#### 3.3.3 EDA Analysis Agent
**Purpose:** Pandas-based EDA, business insights

**Implementation:**
```python
class EDAAnalysisAgentBase(AgentBase):
    """Base for EDA analysis agents (pandas-based)."""
    
    async def process_request(
        self,
        request: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Perform EDA analysis and generate business insights."""
        # 1. Get data (via Runtime State Surface)
        data = await context.get_state("data")
        
        # 2. Load into pandas DataFrame
        df = pd.DataFrame(data)
        
        # 3. Perform EDA
        eda_results = await self.perform_eda(df)
        
        # 4. Generate business insights
        insights = await self.generate_insights(eda_results)
        
        return {
            "eda_results": eda_results,
            "business_insights": insights
        }
```

#### 3.3.4 Workflow Optimization Agent
**Purpose:** Review workflows, suggest Coexistence optimizations

**Implementation:**
```python
class WorkflowOptimizationAgentBase(AgentBase):
    """Base for workflow optimization agents."""
    
    async def process_request(
        self,
        request: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Review workflow and suggest optimizations."""
        # 1. Get workflow (via Conductor SDK)
        workflow = await self.use_tool("conductor_get_workflow", {
            "workflow_id": request.get("workflow_id")
        })
        
        # 2. Analyze workflow for Coexistence opportunities
        analysis = await self.analyze_workflow(workflow)
        
        # 3. Generate optimization suggestions
        suggestions = await self.generate_suggestions(analysis)
        
        return {
            "workflow_analysis": analysis,
            "optimization_suggestions": suggestions
        }
```

#### 3.3.5 Roadmap/POC Proposal Agent
**Purpose:** Context-aware, journey-informed proposals

**Implementation:**
```python
class ProposalAgentBase(AgentBase):
    """Base for roadmap/POC proposal agents."""
    
    async def process_request(
        self,
        request: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Generate roadmap/POC proposal based on user journey."""
        # 1. Get user journey (via Runtime State Surface)
        journey = await context.get_state("user_journey")
        
        # 2. Get platform context (via Smart City SDK)
        platform_context = await self.use_tool("city_manager_get_platform_state", {})
        
        # 3. Generate proposal
        proposal = await self.generate_proposal(
            journey=journey,
            platform_context=platform_context,
            request=request
        )
        
        return {
            "proposal": proposal,
            "context_aware": True
        }
```

### 3.5 File Structure

```
symphainy_platform/civic_systems/agentic/
├── __init__.py
├── agent_base.py                 # Core AgentBase (ABC)
├── agent_registry.py             # Agent registration and discovery
├── agent_factory.py              # Agent factory (creates agents)
├── collaboration_engine.py       # Policy-governed agent collaboration
├── memory_manager.py             # Memory management (session state)
├── tool_registry.py              # Tool registry (Smart City MCP tools)
├── evaluator.py                  # Agent output evaluation
├── observability.py              # Agent observability (tracing, metrics)
│
├── collaboration/
│   ├── __init__.py
│   ├── collaboration_policy.py  # Agent collaboration policy (from Curator)
│   ├── contribution_request.py  # Contribution request model
│   └── collaboration_router.py  # Routes requests (validated by Smart City)
│
├── agents/
│   ├── __init__.py
│   ├── stateless_agent.py        # StatelessAgentBase
│   ├── conversational_agent.py   # ConversationalAgentBase
│   ├── eda_analysis_agent.py    # EDAAnalysisAgentBase
│   ├── workflow_optimization_agent.py  # WorkflowOptimizationAgentBase
│   └── proposal_agent.py         # ProposalAgentBase
│
└── integrations/
    ├── __init__.py
    ├── smart_city_mcp_client.py  # MCP client for Smart City tools
    └── runtime_context_adapter.py # Adapter for Runtime ExecutionContext
```

---

## Part 4: Implementation Order

### Week 6: Smart City SDK + Experience Plane

**Day 1-2: Smart City SDK (MVP Core)**
- ✅ Security Guard SDK + Primitives
- ✅ Traffic Cop SDK + Primitives
- ✅ Post Office SDK + Primitives

**Day 3-4: Experience Plane**
- ✅ Experience Service (FastAPI)
- ✅ Session API endpoints
- ✅ Intent submission API endpoints
- ✅ WebSocket streaming
- ✅ Traefik configuration

**Day 5: Integration Testing**
- ✅ Experience → Runtime integration
- ✅ WebSocket streaming end-to-end
- ✅ Traefik routing validation

### Week 7: Smart City SDK (Full) + Agentic SDK

**Day 1-2: Smart City SDK (Remaining Roles)**
- ✅ City Manager SDK + Primitives
- ✅ Librarian SDK + Primitives
- ✅ Data Steward SDK + Primitives
- ✅ Conductor SDK + Primitives
- ✅ Nurse SDK + Primitives
- ✅ Curator SDK + Primitives

**Day 3-4: Agentic SDK (Core Framework)**
- ✅ AgentBase (ABC)
- ✅ AgentRegistry
- ✅ AgentFactory
- ✅ CollaborationEngine (Policy-Governed)
- ✅ MemoryManager
- ✅ ToolRegistry (Smart City MCP integration)
- ✅ CollaborationPolicy (from Curator)
- ✅ ContributionRequest (Non-Executing)
- ✅ CollaborationRouter (Smart City Validated)

**Day 5: Agentic SDK (Agent Types)**
- ✅ StatelessAgentBase
- ✅ ConversationalAgentBase
- ✅ EDAAnalysisAgentBase
- ✅ WorkflowOptimizationAgentBase
- ✅ ProposalAgentBase

**Day 6-7: Integration & Testing**
- ✅ Agent → Runtime integration
- ✅ Agent → Smart City SDK integration
- ✅ End-to-end agent execution
- ✅ All tests passing

---

## Part 5: Success Criteria

### Smart City SDK + Primitives
- ✅ All 9 roles implemented (SDK + Primitives)
- ✅ Equivalent or better functionality than `/symphainy_source/`
- ✅ Supports 350k policies scenario (policy engine optimized)
- ✅ MVP-lightweight mode (minimal overhead for showcase)
- ✅ All tests passing

### Experience Plane
- ✅ Separate FastAPI service
- ✅ Session management (via Runtime)
- ✅ Intent submission (via Runtime)
- ✅ WebSocket streaming (real-time updates)
- ✅ Traefik integration (infrastructure routing)
- ✅ All tests passing

### Agentic SDK
- ✅ Extremely robust framework
- ✅ All 5 agent types implemented
- ✅ Runtime execution context integration
- ✅ Smart City MCP tools integration
- ✅ Structured output (AGUI schema)
- ✅ Policy-aware (governance hooks)
- ✅ Policy-governed agent collaboration (no orchestration)
- ✅ "No Commit" rule enforced (proposals only, no side effects)
- ✅ All tests passing

---

## Part 6: Next Steps

1. **Review this plan** with CTO
2. **Start with Smart City SDK (MVP Core)** - Security Guard, Traffic Cop, Post Office
3. **Build Experience Plane** - Separate service with Traefik integration
4. **Complete Smart City SDK (Full)** - All 9 roles
5. **Build Agentic SDK** - Extremely robust framework
6. **Integration testing** - End-to-end validation

---

## Part 7: CTO Feedback & Corrections Applied

**Date:** January 2026  
**Status:** ✅ Corrections Applied

### 7.1 CTO Verdict Summary

- **Smart City:** 85-90% correct → **Critical corrections applied**
- **Experience Plane:** 90-95% correct → **Minor clarification applied**
- **Agentic SDK:** 80-85% correct → **Awaiting user guidance** (CTO feedback deferred per user request)

### 7.2 Critical Corrections Applied

#### ✅ Correction #1: SDKs Must NOT Depend on Runtime

**Problem:** Original plan had SDKs depending on Runtime directly:
```python
# ❌ WRONG
class SecurityGuardSDK:
    def __init__(self, runtime: Runtime, public_works: PublicWorksFoundationService):
        self.runtime = runtime
```

**Solution:** SDKs now depend only on Public Works abstractions:
```python
# ✅ CORRECT
class SecurityGuardSDK:
    def __init__(
        self,
        auth_abstraction: AuthenticationProtocol,
        tenant_abstraction: TenancyProtocol,
        policy_resolver: PolicyResolver
    ):
        # NO Runtime dependency
```

**Rationale:**
- SDKs prepare execution contracts
- Runtime validates and executes them
- This maintains the governance → execution boundary

#### ✅ Correction #2: Session Creation via Traffic Cop SDK

**Problem:** Original plan had Experience creating sessions directly via Runtime.

**Solution:** Session creation now flows through Traffic Cop SDK:
1. Experience calls `TrafficCopSDK.create_session_intent(...)`
2. SDK prepares session intent + metadata
3. Experience submits intent to Runtime
4. Runtime validates via Traffic Cop primitives
5. Runtime creates session

**Rationale:**
- Session semantics centralized in Traffic Cop SDK
- Experience remains thin (coordination only)
- Runtime remains authoritative (validation + execution)

#### ✅ Correction #3: Curator Runtime Visibility

**Problem:** Original plan didn't clarify Curator's relationship with Runtime.

**Solution:** Explicitly documented:
- **Curator SDK** → Used by Solution & Smart City (registration, discovery)
- **Curator Data** → Visible to Runtime (read-only, snapshotted registry state)
- **Runtime** → Never calls Curator SDK methods, only consumes snapshotted registry state

**Rationale:**
- Runtime needs registry visibility for execution validation
- Runtime should not have orchestration authority (no SDK calls)

#### ✅ Correction #4: Agent Collaboration (Policy-Governed)

**Problem:** Original plan didn't address agent-to-agent interaction clearly.

**Solution:** Implemented policy-governed agent collaboration pattern:
- **Agents may collaborate** to produce proposals and reasoning artifacts
- **Agents may not orchestrate** execution or commit side effects
- **All agent collaboration** is policy-governed and ratified by Solution and Smart City

**Key Distinctions:**
1. **Reasoning collaboration** ✅ allowed
2. **Proposal composition** ✅ allowed
3. **Execution orchestration** ❌ forbidden

**Mechanism:**
- Agent Collaboration Policy (stored in Curator/Policy Registry)
- Evaluated by Smart City primitives
- `request_contribution()` method (not `invoke_agent()`)
- Returns non-executing artifacts only (proposals, blueprints, ranked options)

**The "No Commit" Rule:**
- Agents can emit: proposals, blueprints, ranked options, suggested intents
- Agents cannot emit: state mutations, service invocations
- Execution plans only if Solution-owned

**Rationale:**
- Agents are in a "design studio," not a factory
- They can talk, sketch, ask for help, refine ideas, propose plans
- They cannot pull levers, start machines, commit changes
- Only Solution + Smart City + Runtime do that

### 7.3 What's Locked (Per CTO)

✅ **Locked Immediately:**
- Smart City roles and file structure
- SDK vs Primitives split
- Experience as a separate service
- Traefik as infra-only
- Agent types and base abstractions
- MVP-lightweight vs full policy engine approach

### 7.4 What Was Adjusted

✅ **Adjusted Before Execution:**
1. ✅ Removed Runtime dependency from all SDKs
2. ✅ Routed session creation through Traffic Cop SDK
3. ✅ Made Curator runtime-visible but SDK-inaccessible
4. ✅ Implemented policy-governed agent collaboration (no orchestration)

---

**Status:** ✅ Ready to execute (all corrections applied, policy-governed agent collaboration implemented)
