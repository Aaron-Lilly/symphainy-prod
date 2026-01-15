# Phase 3: Civic Systems - Implementation Plan

**Date:** January 2026  
**Status:** 📋 **DETAILED IMPLEMENTATION PLAN**  
**Based on:** `symphainy_architecture_guide.md`  
**Purpose:** Build Civic Systems that define how things are allowed to participate in execution

---

## Executive Summary

Phase 3 builds the **Civic Systems** - the four systems that define how things are allowed to participate in execution. Civic Systems:

- Do **not** own business logic
- Do **not** own execution
- Define **capability by design, constrained by policy**
- Expose **SDKs, planes, and surfaces** used by Runtime and domain services

**Civic Systems may depend on each other, but Runtime remains the single execution authority.**

---

## Architecture Overview

### Civic Systems (from Architecture Guide)

There are four Civic Systems:

1. **Smart City** — governance (how execution is allowed to occur)
2. **Experience** — exposure (translates external interaction into intent)
3. **Agentic** — reasoning (agents reason under constraint)
4. **Platform SDK (Realm SDK)** — how solutions and domains are built correctly

### Smart City (Execution Governance)

> **Smart City governs *how* execution is allowed to occur.**

Smart City is purpose-agnostic. It never decides *what* should happen or *why*.

It exposes policy-aware primitives consumed by Runtime.

#### Canonical Smart City Roles

| Role           | Responsibility                         |
| -------------- | -------------------------------------- |
| City Manager   | Global policy, tenancy, escalation     |
| Security Guard | Identity, authN/Z, zero trust          |
| Curator        | Capability, agent, domain registries   |
| Data Steward   | Data boundaries, contracts, provenance |
| Librarian      | Semantic schemas & meaning             |
| Traffic Cop    | Sessions, execution IDs, correlation   |
| Post Office    | Event routing & ordering               |
| Conductor      | Workflow & saga primitives             |
| Nurse          | Telemetry, retries, self-healing       |

### Experience (Exposure & Interaction)

> **Experience translates external interaction into intent.**

Experience:
- exposes REST, WebSockets, chat, adapters
- authenticates callers
- establishes sessions via Runtime
- translates user actions into **intents**
- streams execution updates back

Experience never:
- calls domain services directly
- manages workflows
- owns state

### Agentic (Reasoning Under Constraint)

> **Agents reason. They do not execute.**

The Agentic Civic System provides:
- agent SDK
- agent registry & factory
- grounding, telemetry, policy hooks

Agents:
- consume artifacts
- produce interpretations or recommendations
- operate **only inside Runtime execution**

Agents never:
- write to databases
- call infrastructure directly
- orchestrate workflows

### Platform SDK (Realm SDK / Civic Front Door)

> **The Platform SDK defines how solutions and domain services are built correctly.**

This SDK:
- is the *front door* for building on Symphainy
- configures client-specific policies, capabilities, and integrations
- composes Civic Systems into usable building blocks

It is how:
- your team builds the MVP showcase
- external developers build their own solutions
- agentic coders generate compliant services

---

## Current State Assessment

### ✅ What Exists (Build On)

1. **Smart City Foundation** (`smart_city/foundation_service.py`)
   - ✅ Foundation service structure
   - ✅ Some Smart City services exist
   - ⚠️ Needs: Complete all 9 roles, align with Civic System pattern

2. **Experience Plane** (`experience/`)
   - ✅ Basic structure exists
   - ✅ WebSocket handlers exist
   - ✅ API handlers exist
   - ⚠️ Needs: Align with Civic System pattern, intent translation

3. **Agentic Foundation** (`agentic/foundation_service.py`)
   - ✅ Basic foundation service
   - ✅ Agent base classes exist
   - ⚠️ Needs: Complete SDK (registry, factory, MCP tool integration)

4. **Curator Foundation** (`foundations/curator/`)
   - ✅ Capability registry exists
   - ✅ Intent → capability lookup
   - ✅ Complete

### ❌ What's Missing (Build New)

1. **Complete Smart City Roles** - All 9 roles as policy-aware primitives
2. **Experience Intent Translation** - Translate user actions to intents
3. **Agentic SDK Components** - Registry, factory, MCP tool integration
4. **Platform SDK** - Front door for building solutions

---

## Implementation Plan

### Phase 3.1: Smart City Primitives (Week 1-2)

**Goal:** Build all 9 Smart City roles as policy-aware primitives consumed by Runtime

**Tasks:**

1. **Define Smart City Role Protocol** (`smart_city/protocols/smart_city_role_protocol.py`)
   ```python
   class SmartCityRole(Protocol):
       """Protocol for all Smart City roles."""
       
       async def enforce_policy(
           self,
           execution_context: ExecutionContext
       ) -> PolicyValidationResult:
           """Enforce policy for execution context."""
       
       async def provide_primitive(
           self,
           primitive_type: str,
           context: Dict[str, Any]
       ) -> Dict[str, Any]:
           """Provide policy-aware primitive."""
   ```

2. **Implement All 9 Smart City Roles** (Week 1)
   - City Manager - Global policy, tenancy, escalation
   - Security Guard - Identity, authN/Z, zero trust
   - Curator - Capability, agent, domain registries (already exists, enhance)
   - Data Steward - Data boundaries, contracts, provenance
   - Librarian - Semantic schemas & meaning
   - Traffic Cop - Sessions, execution IDs, correlation
   - Post Office - Event routing & ordering
   - Conductor - Workflow & saga primitives
   - Nurse - Telemetry, retries, self-healing

3. **Integrate with Runtime** (Week 2)
   - Runtime calls Smart City roles for policy validation
   - Runtime uses Smart City primitives (sessions, events, workflows)
   - Smart City roles observe Runtime execution (via observer pattern)

**Success Criteria:**
- ✅ All 9 Smart City roles implemented
- ✅ Roles provide policy-aware primitives
- ✅ Roles integrate with Runtime
- ✅ Roles do not contain business logic

---

### Phase 3.2: Experience Intent Translation (Week 3)

**Goal:** Experience translates external interaction into intent

**Tasks:**

1. **Build Intent Translator** (`experience/intent_translator.py`)
   ```python
   class IntentTranslator:
       """Translates user actions to intents."""
       
       async def translate_user_action(
           self,
           user_action: Dict[str, Any],
           session: Session
       ) -> Intent:
           """Translate user action to intent."""
   ```

2. **Build REST Intent Adapter** (`experience/adapters/rest_intent_adapter.py`)
   - Accepts REST requests
   - Authenticates callers (via Security Guard)
   - Establishes sessions (via Runtime)
   - Translates requests to intents
   - Submits intents to Runtime
   - Returns execution results

3. **Build WebSocket Intent Adapter** (`experience/adapters/websocket_intent_adapter.py`)
   - Accepts WebSocket connections
   - Authenticates callers (via Security Guard)
   - Establishes sessions (via Runtime)
   - Translates messages to intents
   - Submits intents to Runtime
   - Streams execution updates back

4. **Build Chat Intent Adapter** (`experience/adapters/chat_intent_adapter.py`)
   - Accepts chat messages
   - Routes to appropriate agent (Guide or Liaison)
   - Translates chat to intents
   - Submits intents to Runtime
   - Streams agent responses back

5. **Update Experience Foundation** (`experience/foundation_service.py`)
   - Initialize all adapters
   - Wire adapters to Runtime
   - Wire adapters to Smart City (Security Guard, Traffic Cop)

**Success Criteria:**
- ✅ Experience translates user actions to intents
- ✅ Experience never calls domain services directly
- ✅ Experience streams execution updates back
- ✅ All adapters authenticate and establish sessions

---

### Phase 3.3: Agentic SDK (Week 4-5)

**Goal:** Build complete Agentic SDK (registry, factory, MCP tool integration)

**Tasks:**

1. **Build Agent Registry** (`foundations/agentic/agent_registry.py`)
   ```python
   class AgentRegistry:
       """Registry for agent discovery and lifecycle."""
       
       async def register_agent(
           self,
           agent: AgentBase,
           capabilities: List[str]
       ) -> bool:
           """Register agent with registry."""
       
       async def discover_agent(
           self,
           capability: str,
           context: Dict[str, Any]
       ) -> Optional[AgentBase]:
           """Discover agent by capability."""
   ```

2. **Build Agent Factory** (`foundations/agentic/agent_factory.py`)
   ```python
   class AgentFactory:
       """Factory for creating agents with dependencies."""
       
       async def create_agent(
           self,
           agent_type: str,
           context: Dict[str, Any]
       ) -> AgentBase:
           """Create agent with proper dependencies."""
   ```

3. **Build MCP Tool Integration** (`foundations/agentic/mcp_tool_integration.py`)
   ```python
   class MCPToolIntegration:
       """MCP tool discovery and execution for agents."""
       
       async def discover_tools(
           self,
           realm: str,
           capability: str
       ) -> List[MCPTool]:
           """Discover MCP tools for capability."""
       
       async def execute_tool(
           self,
           tool_name: str,
           parameters: Dict[str, Any]
       ) -> Dict[str, Any]:
           """Execute MCP tool."""
   ```

4. **Build Agent SDK Components** (Week 5)
   - `tool_registry.py` - Tool registration and lookup
   - `tool_composition.py` - Tool chaining
   - `policy_integration.py` - Policy hooks for agents
   - `grounding.py` - Grounding capabilities

5. **Update Agentic Foundation** (`foundations/agentic/foundation_service.py`)
   - Initialize registry, factory, MCP tool integration
   - Register agents with Curator
   - Expose SDK components to realms

**Success Criteria:**
- ✅ Agent registry enables agent discovery
- ✅ Agent factory creates agents with dependencies
- ✅ Agents can discover and use MCP tools
- ✅ Agents operate only inside Runtime execution

---

### Phase 3.4: Platform SDK (Week 6)

**Goal:** Build Platform SDK as front door for building solutions

**Tasks:**

1. **Define Solution Model** (`platform_sdk/solution_model.py`)
   ```python
   @dataclass
   class Solution:
       """Solution definition."""
       solution_id: str
       solution_name: str
       solution_context: Dict[str, Any]  # Goals, constraints, risk
       supported_intents: List[str]
       domain_service_bindings: Dict[str, Any]  # Realm → external system bindings
   ```

2. **Build Solution Builder** (`platform_sdk/solution_builder.py`)
   ```python
   class SolutionBuilder:
       """Builder for creating solutions."""
       
       async def create_solution(
           self,
           solution_definition: SolutionDefinition
       ) -> Solution:
           """Create solution from definition."""
   ```

3. **Build Realm SDK** (`platform_sdk/realm_sdk.py`)
   ```python
   class RealmSDK:
       """SDK for building domain services."""
       
       def create_realm_service(
           self,
           realm_name: str,
           supported_intents: List[str]
       ) -> RealmServiceBase:
           """Create realm service with Runtime Participation Contract."""
   ```

4. **Build Platform SDK Foundation** (`platform_sdk/foundation_service.py`)
   - Initialize solution builder
   - Initialize realm SDK
   - Compose Civic Systems into building blocks

**Success Criteria:**
- ✅ Platform SDK enables solution creation
- ✅ Platform SDK enables realm service creation
- ✅ Platform SDK composes Civic Systems
- ✅ MVP showcase can be built using Platform SDK

---

## Recommendations for Architecture Team Review

Based on platform use cases (`/docs/platform_use_cases/`), here are our recommendations for Phase 3 implementation:

### 1. Smart City Role Integration Recommendation

**Based on Use Cases:**
- **MVP Showcase**: Multi-tenant isolation, session management, policy enforcement
- **Insurance Migration**: Data boundaries, provenance tracking, audit requirements
- **Permit Data Mash**: Compliance workflows, policy enforcement
- **T&E Enablement**: Auditability, repeatability, policy enforcement

**Recommended Smart City Role Integration:**

```python
class SmartCityRoleIntegration:
    """Integration between Runtime and Smart City roles."""
    
    async def validate_policy(
        self,
        intent: Intent,
        execution_context: ExecutionContext
    ) -> PolicyValidationResult:
        """
        Validate policy using Smart City roles.
        
        Steps:
        1. Security Guard: Validate authN/Z
        2. City Manager: Validate tenant policy
        3. Data Steward: Validate data access
        4. Return validation result
        """
    
    async def get_session(
        self,
        session_id: str,
        tenant_id: str
    ) -> Session:
        """Get session via Traffic Cop."""
    
    async def publish_event(
        self,
        event_type: str,
        event_data: Dict[str, Any],
        execution_context: ExecutionContext
    ) -> EventContext:
        """Publish event via Post Office."""
    
    async def get_saga_primitives(
        self,
        saga_type: str
    ) -> SagaPrimitives:
        """Get saga primitives via Conductor."""
```

**Key Principles:**
- Smart City roles are **policy-aware primitives**, not business logic
- Runtime calls Smart City roles, not the other way around
- Smart City roles observe Runtime execution (via observer pattern)
- Smart City roles do not decide *what* should happen, only *how* it's allowed

**Critical Guardrails (Canonical Answers):**

| Question                                      | Correct Answer                                                                               |
| --------------------------------------------- | -------------------------------------------------------------------------------------------- |
| Can a Smart City role ever trigger an intent? | **No.** Only Experience (external) or Runtime (internal continuation) can introduce intents. |
| Where does policy failure occur?              | **Before execution begins.** Runtime performs policy checks synchronously and fails fast.    |
| Are policy checks synchronous or async?       | **Synchronous for execution gating; async for audit/telemetry only.**                        |
| Can Smart City mutate execution state?        | **No.** It can approve, deny, annotate, or observe — never mutate.                           |
| How are policy decisions recorded?            | **As execution facts/events in the Runtime WAL.**                                            |

**Additional Clarifications:**
- Smart City roles **do not orchestrate**
- Smart City roles **do not own state**
- Smart City roles **do not trigger execution**
- They answer questions; they do not cause actions

**Rationale:**
- Supports all use case requirements (multi-tenant, audit, compliance)
- Maintains clear separation (Smart City = governance, Runtime = execution)
- Enables policy enforcement before execution
- Enables observability during execution
- Prevents Smart City from becoming execution controller

---

### 2. Experience Intent Translation Recommendation

**Based on Use Cases:**
- **MVP Showcase**: REST API for file upload, WebSocket for chat, solution context propagation
- **Insurance Migration**: REST API for batch operations, async updates
- **Permit Data Mash**: REST API for permit processing, async regulation updates
- **T&E Enablement**: REST API for document upload, WebSocket for interactive queries

**Recommended Intent Translation Pattern:**

```python
class IntentTranslator:
    """Translates user actions to intents."""
    
    async def translate_rest_request(
        self,
        request: Request,
        session: Session
    ) -> Intent:
        """
        Translate REST request to intent.
        
        Pattern:
        - POST /api/content/upload → intent_type="content.upload"
        - POST /api/journey/create_sop → intent_type="journey.create_sop"
        - GET /api/insights/analyze → intent_type="insights.analyze"
        """
    
    async def translate_websocket_message(
        self,
        message: Dict[str, Any],
        session: Session
    ) -> Intent:
        """
        Translate WebSocket message to intent.
        
        Pattern:
        - Chat message → intent_type="agent.reason" (with agent context)
        - User action → intent_type="{realm}.{action}"
        """
    
    async def translate_chat_message(
        self,
        message: str,
        agent_type: str,  # "guide" or "liaison"
        session: Session
    ) -> Intent:
        """
        Translate chat message to intent.
        
        Pattern:
        - Guide agent → intent_type="agent.guide.reason"
        - Liaison agent → intent_type="agent.liaison.{realm}.reason"
        """
```

**Key Principles:**
- Experience **never calls domain services directly**
- Experience **always translates to intents**
- Experience **always submits intents to Runtime**
- Experience **streams execution updates back** (via WebSocket/SSE)

**Critical Guardrails (Canonical Answers):**

| Question                                              | Correct Answer                                                     |
| ----------------------------------------------------- | ------------------------------------------------------------------ |
| Can Experience call a Realm SDK directly?             | **No. Never.** Experience only emits intents to Runtime.           |
| Can Experience hold execution state?                  | **No.** Runtime owns all execution and session state.              |
| What happens if Experience disconnects mid-execution? | **Execution continues.** Experience can reattach via execution ID. |
| Can Experience cancel execution?                      | **Only by emitting a new, authorized intent (e.g., cancel).**      |
| Is Experience required for non-interactive execution? | **No.** Runtime can execute intents from other sources.            |

**Additional Clarifications:**
- Experience **frames intent**, it does not decide execution strategy
- Experience **subscribes**, it does not control
- Loss of Experience connectivity **must not impact execution**

**Rationale:**
- Supports all use case patterns (REST, WebSocket, chat)
- Maintains clear boundary (Experience = exposure, Runtime = execution)
- Enables solution context propagation (MVP showcase)
- Enables async updates (permit data mash, insurance migration)
- Prevents Experience from becoming execution controller

---

### 3. Agentic SDK Scope Recommendation

**Based on Use Cases:**
- **MVP Showcase**: Guide agent (global concierge), 4 Liaison agents (one per pillar)
- **Insurance Migration**: Specialist agents for policy analysis, migration planning
- **Permit Data Mash**: Specialist agents for permit interpretation, compliance analysis
- **T&E Enablement**: Specialist agents for AAR analysis, test workflow generation

**Recommended Agentic SDK Scope:**

```python
# Agent Registry
class AgentRegistry:
    """Registry for agent discovery and lifecycle."""
    
    async def register_agent(
        self,
        agent: AgentBase,
        agent_type: str,  # "guide", "liaison", "specialist"
        capabilities: List[str],
        realm: Optional[str] = None
    ) -> bool:
        """Register agent with registry."""
    
    async def discover_agent(
        self,
        capability: str,
        agent_type: Optional[str] = None,
        realm: Optional[str] = None
    ) -> Optional[AgentBase]:
        """Discover agent by capability."""

# Agent Factory
class AgentFactory:
    """Factory for creating agents with dependencies."""
    
    async def create_guide_agent(
        self,
        context: Dict[str, Any]
    ) -> GuideAgent:
        """Create guide agent (global concierge)."""
    
    async def create_liaison_agent(
        self,
        realm: str,
        context: Dict[str, Any]
    ) -> LiaisonAgent:
        """Create liaison agent (realm-specific)."""
    
    async def create_specialist_agent(
        self,
        specialization: str,
        realm: str,
        context: Dict[str, Any]
    ) -> SpecialistAgent:
        """Create specialist agent (domain-specific reasoning)."""

# MCP Tool Integration
class MCPToolIntegration:
    """MCP tool discovery and execution for agents."""
    
    async def discover_realm_tools(
        self,
        realm: str
    ) -> List[MCPTool]:
        """Discover MCP tools for realm."""
    
    async def execute_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        execution_context: ExecutionContext
    ) -> Dict[str, Any]:
        """Execute MCP tool via Runtime."""
```

**Key Principles:**
- Agents **reason**, they do not execute
- Agents **use MCP tools** (not direct service calls)
- Agents **operate only inside Runtime execution**
- Agents **return artifacts**, not side effects

**Critical Guardrails (Canonical Answers):**

| Question                                                    | Correct Answer                                                    |
| ----------------------------------------------------------- | ----------------------------------------------------------------- |
| Can an agent change system state directly?                  | **No.** Agents only produce recommendations or intent proposals.  |
| Can an agent write to a database?                           | **No.** Ever.                                                     |
| Can multiple agents reason in one execution?                | **Yes.** Runtime may coordinate multi-agent reasoning.            |
| Are agent outputs persisted?                                | **Yes — as attributed reasoning artifacts in execution context.** |
| Who owns final responsibility for agent-influenced actions? | **Runtime. Always.**                                              |

**Additional Clarifications:**
- Agents **propose**; Runtime **decides**
- Agents **never mutate state**
- Agents **never call infrastructure**

**Rationale:**
- Supports all use case agent types (guide, liaison, specialist)
- Enables agent discovery and lifecycle management
- Enables MCP tool integration (agents use services as tools)
- Maintains clear boundary (agents = reasoning, Runtime = execution)
- Prevents agents from becoming execution controllers

---

### 4. Platform SDK Scope Recommendation

**Based on Use Cases:**
- **MVP Showcase**: Solution with 4 pillars, solution context propagation
- **Insurance Migration**: Solution for 350k policy migration
- **Permit Data Mash**: Solution for permit processing automation
- **T&E Enablement**: Solution for T&E artifact analysis

**Recommended Platform SDK Scope:**

```python
# Solution Model
@dataclass
class Solution:
    """Solution definition."""
    solution_id: str
    solution_name: str
    solution_context: Dict[str, Any]  # Goals, constraints, risk
    supported_intents: List[str]
    domain_service_bindings: Dict[str, Any]  # Realm → external system bindings
    policy_overrides: Optional[Dict[str, Any]] = None  # Solution-specific policies

# Solution Builder
class SolutionBuilder:
    """Builder for creating solutions."""
    
    async def create_solution(
        self,
        solution_definition: SolutionDefinition
    ) -> Solution:
        """
        Create solution from definition.
        
        Steps:
        1. Validate solution definition
        2. Register solution with Curator
        3. Configure policy overrides (if any)
        4. Bind domain services to external systems
        5. Return solution
        """
    
    async def get_solution(
        self,
        solution_id: str
    ) -> Optional[Solution]:
        """Get solution by ID."""

# Realm SDK
class RealmSDK:
    """SDK for building domain services."""
    
    def create_realm_service(
        self,
        realm_name: str,
        supported_intents: List[str],
        handler_method: Callable
    ) -> RealmServiceBase:
        """
        Create realm service with Runtime Participation Contract.
        
        Returns service that:
        - Implements handle_intent(intent, execution_context) → artifacts/events
        - Declares supported intents
        - Never bypasses Runtime
        """
```

**Key Principles:**
- Platform SDK is the **front door** for building on Symphainy
- Solutions define **solution context** (goals, constraints, risk)
- Solutions **bind domain services to external systems**
- Realm SDK ensures **Runtime Participation Contract** compliance

**Critical Guardrails (Canonical Answers):**

| Question                                            | Correct Answer                               |
| --------------------------------------------------- | -------------------------------------------- |
| Does the Platform SDK ever execute code?            | **No.** Execution only happens in Runtime.   |
| Can a Solution exist without being executed?        | **Yes.** Solutions are deployable artifacts. |
| Are Solutions versioned?                            | **Yes.** Versioning is mandatory.            |
| Can Platform SDK outputs be statically validated?   | **Yes.** That's a core purpose of the SDK.   |
| Can agents use the Platform SDK to build solutions? | **Yes — under governance.**                  |

**Additional Clarifications:**
- Platform SDK ≠ Runtime API
- Platform SDK outputs **artifacts**, not executions
- SDK enforces *correct construction*, not behavior

**Rationale:**
- Supports all use case solution patterns
- Enables solution context propagation (MVP showcase)
- Enables external system integration (all use cases)
- Ensures architectural compliance (Runtime Participation Contract)
- Prevents Platform SDK from becoming execution engine

---

### 5. Civic System Integration Recommendation

**Based on Use Cases:**
- All use cases require: Smart City governance, Experience exposure, Agentic reasoning, Platform SDK composition

**Recommended Civic System Integration:**

```python
class CivicSystemIntegration:
    """Integration between Civic Systems."""
    
    # Smart City → Runtime
    async def validate_policy_via_smart_city(
        self,
        intent: Intent,
        execution_context: ExecutionContext
    ) -> PolicyValidationResult:
        """Runtime calls Smart City for policy validation."""
    
    # Experience → Runtime
    async def submit_intent_via_experience(
        self,
        intent: Intent,
        session: Session
    ) -> ExecutionResult:
        """Experience submits intent to Runtime."""
    
    # Agentic → Runtime
    async def execute_agent_reasoning(
        self,
        agent: AgentBase,
        context: Dict[str, Any],
        execution_context: ExecutionContext
    ) -> Dict[str, Any]:
        """Runtime executes agent reasoning."""
    
    # Platform SDK → All
    async def create_solution_via_platform_sdk(
        self,
        solution_definition: SolutionDefinition
    ) -> Solution:
        """Platform SDK composes all Civic Systems."""
```

**Key Principles:**
- Civic Systems **may depend on each other**
- **Runtime remains the single execution authority**
- Civic Systems provide **SDKs, planes, and surfaces**
- Platform SDK **composes Civic Systems** into building blocks

**Critical Guardrails (Canonical Answers):**

| Question                                               | Correct Answer                                                            |
| ------------------------------------------------------ | ------------------------------------------------------------------------- |
| Can one Civic System call another directly?            | **No.** Only via SDK composition at build time.                           |
| Can Civic Systems bypass Runtime?                      | **No.** That is a platform violation.                                     |
| Where are boundaries enforced?                         | **Both compile-time (SDK contracts) and runtime (execution validation).** |
| Can Civic Systems depend on Public Works abstractions? | **Yes.** Public Works underpins infrastructure portability.               |
| Who coordinates cross-system concerns like telemetry?  | **Runtime, with Smart City observation.**                                 |

**Additional Clarifications:**
- Civic Systems **do not call each other directly**
- Integration happens through **composition**, not invocation
- Runtime is the only system that *activates* behavior

**Rationale:**
- Supports all use case integration patterns
- Maintains clear boundaries (Civic Systems = governance, Runtime = execution)
- Enables solution composition (Platform SDK)
- Enables architectural compliance (all systems work together)
- Prevents circular dependencies and execution leakage

---

## Summary of Recommendations

| Component | Recommendation | Rationale |
|-----------|---------------|-----------|
| **Smart City Roles** | 9 roles as policy-aware primitives, Runtime calls roles | Supports governance requirements, maintains separation |
| **Experience Intent Translation** | Translate all user actions to intents, never call domain services | Supports all exposure patterns, maintains boundary |
| **Agentic SDK** | Registry, factory, MCP tool integration, agents reason only | Supports all agent types, enables tool integration |
| **Platform SDK** | Solution builder, realm SDK, composes Civic Systems | Supports solution creation, ensures compliance |
| **Civic System Integration** | Civic Systems provide SDKs/planes/surfaces, Runtime executes | Supports all integration patterns, maintains boundaries |

**All recommendations are based on platform use cases and support:**
- ✅ MVP Showcase (multi-pillar solution, guide/liaison agents)
- ✅ Insurance Migration (enterprise solution, specialist agents)
- ✅ Permit Data Mash (compliance solution, async updates)
- ✅ T&E Enablement (audit solution, interactive queries)

---

## Success Criteria (Phase 3 Complete)

### Functional Requirements

- ✅ **Smart City Primitives** - All 9 roles provide policy-aware primitives
- ✅ **Experience Intent Translation** - All user actions translate to intents
- ✅ **Agentic SDK** - Registry, factory, MCP tool integration complete
- ✅ **Platform SDK** - Solution builder and realm SDK complete

### Non-Functional Requirements

- ✅ **Performance** - Intent translation latency < 50ms
- ✅ **Reliability** - 99.9% intent translation success rate
- ✅ **Observability** - All Civic System operations observable
- ✅ **Testability** - Comprehensive test coverage (>80%)

### Architectural Requirements

- ✅ **Clear Boundaries** - Civic Systems do not own business logic or execution
- ✅ **Runtime Authority** - Runtime remains single execution authority
- ✅ **SDK Exposure** - Civic Systems expose SDKs/planes/surfaces
- ✅ **Solution Composition** - Platform SDK composes Civic Systems

---

## Next Steps (Phase 4)

After Phase 3 is complete:

1. **Phase 4: Domain Services** - Wrap existing services with Runtime Participation Contract
2. **Phase 5: MVP Showcase Solution** - Build MVP using Platform SDK

---

## Conclusion

Phase 3 builds the **Civic Systems** - the four systems that define how things are allowed to participate in execution. Once complete, the Civic Systems will:

- Provide governance primitives (Smart City)
- Translate external interaction to intents (Experience)
- Enable agent reasoning under constraint (Agentic)
- Compose solutions and domain services (Platform SDK)

**This enables the platform to govern execution while remaining flexible and extensible.**

---

## Critical Guardrails Summary

**Non-Negotiable Principles (Must Preserve):**

1. **Single Execution Authority** - Runtime is the only system that activates behavior
2. **Explicit Intent** - Nothing executes without intent
3. **No Hidden State** - All state is explicit and Runtime-owned
4. **No Autonomous Action** - All actions are attributed to intent/session/tenant

**Why These Guardrails Matter:**

- **Prevents Architectural Drift** - Keeps systems in their lanes
- **Enables Governance** - All execution is explicit and attributable
- **Enables Replay** - Deterministic execution from WAL
- **Enables Safety** - Policy gates execution, not business logic

**During Implementation:**

- ✅ **Stay anchored in *why* each answer is correct**
- ✅ **Reference guardrails when making design decisions**
- ✅ **Challenge any pattern that violates guardrails**
- ✅ **Test guardrails are enforced (compile-time and runtime)**

**If we stay anchored in these guardrails, Symphainy will stay on track.**
