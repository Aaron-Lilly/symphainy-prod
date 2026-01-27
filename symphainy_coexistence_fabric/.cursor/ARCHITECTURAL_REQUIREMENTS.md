# Architectural Requirements for SymphAIny Coexistence Fabric

**Purpose:** Define architectural requirements and constraints to ensure web agents don't introduce anti-patterns when building against contracts.

**Status:** ✅ **ACTIVE**  
**Last Updated:** January 27, 2026

---

## 1. Infrastructure Access Rules

### ✅ **REQUIRED:** Use Public Works Abstractions Only

**Rule:** No direct infrastructure access. All infrastructure interactions must go through Public Works abstractions.

**What This Means:**
- ❌ **NO** direct database connections (Supabase, PostgreSQL, etc.)
- ❌ **NO** direct storage access (GCS, S3, etc.)
- ❌ **NO** direct external API calls (OpenAI, etc.)
- ✅ **YES** use Public Works abstractions (Registry Abstraction, Storage Abstraction, etc.)

**Why:**
- Enables infrastructure swapping without code changes
- Provides consistent error handling and retry logic
- Enables testing with mocks
- Maintains architectural boundaries

---

## 2. Security Model

### ✅ **REQUIRED:** Zero Trust Architecture

**Rule:** Zero trust security model - open by policy for MVP.

**What This Means:**
- All resources are protected by default
- Authentication required for all protected resources
- Authorization based on policies (not hardcoded)
- MVP uses "open by policy" (permissive for development)

**Why:**
- Security by design
- Flexible policy management
- Easy to tighten policies for production

**Implementation:**
- Use Security Guard SDK for authentication/authorization
- Policies defined in Smart City Primitives
- Runtime enforces policies before intent execution

---

## 3. Data Consistency

### ✅ **REQUIRED:** Write-Ahead Logging (WAL)

**Rule:** All state changes must be logged before execution.

**What This Means:**
- Intent execution logged before side effects
- State changes logged in intent_executions table
- Enables replay and recovery
- Enables journey trace reconstruction

**Why:**
- Data consistency guarantees
- Audit trail
- Debugging and troubleshooting
- Recovery from failures

---

### ✅ **REQUIRED:** Saga Pattern for Distributed Transactions

**Rule:** Use Saga pattern for multi-step operations that span multiple services.

**What This Means:**
- Compensating transactions for rollback
- No two-phase commit (distributed transactions)
- Each step is independently reversible
- Journey orchestrators manage saga coordination

**Why:**
- Handles distributed system failures gracefully
- No single point of failure
- Enables partial success recovery

---

## 4. Code Organization

### ✅ **REQUIRED:** Micro-Module Architecture

**Rule:** Small, focused modules with single responsibility.

**What This Means:**
- Each module has one clear purpose
- Modules are independently testable
- Clear module boundaries
- Minimal dependencies between modules

**Why:**
- Easier to understand and maintain
- Easier to test
- Easier to replace or refactor
- Better code reusability

---

## 5. Artifact-Centric Patterns

### ✅ **REQUIRED:** Artifact-Centric Only

**Rule:** No file-centric patterns. Everything is an artifact.

**What This Means:**
- Use `artifact_id`, not `file_id`
- Use `artifact_type`, not `file_type`
- Use `lifecycle_state`, not `file_status`
- Use `parent_artifacts` for lineage

**Why:**
- Consistent data model
- Better lineage tracking
- Unified lifecycle management
- Future-proof architecture

---

## 6. Intent Services Pattern

### ✅ **REQUIRED:** Intent Services as SOA APIs

**Rule:** Intent services are SOA APIs in realms. They align to intent contracts.

**What This Means:**
- Intent services live in realms (Content, Insights, Journey, Solution)
- Intent services align to intent contracts
- Intent services return artifacts and events
- Intent services never bypass Runtime

**Why:**
- Clear service boundaries
- Contract-based development
- Testable and mockable
- Enables agentic consumption (MCP tools)

---

## 7. Orchestrators in Journey Realm

### ✅ **REQUIRED:** Orchestrators Live in Journey Realm

**Rule:** Journey orchestrators compose intent services. They live in Journey Realm.

**What This Means:**
- Orchestrators compose realm intent services
- Orchestrators expose as MCP tools for agents
- Orchestrators use agents when journeys require reasoning
- Orchestrators manage saga coordination

**Why:**
- Clear separation of concerns
- Journey logic centralized
- Enables agentic orchestration
- Better testability

---

## 8. Contract-Based Testing

### ✅ **REQUIRED:** All Code Aligns to Contracts

**Rule:** All code must align to contracts. Contract violations are bugs.

**What This Means:**
- Intent services align to intent contracts
- Journey orchestrators align to journey contracts
- Solutions align to solution contracts
- Contract-based testing required

**Why:**
- Ensures correctness
- Enables parallel development
- Clear specifications
- Better documentation

**Testing Requirements:**
- 3D testability (idempotency, payload size, direct API calls)
- Journey trace reconstruction
- Contract compliance validation

---

## 9. Anti-Patterns to Avoid

### ❌ **FORBIDDEN:** Direct Infrastructure Access
### ❌ **FORBIDDEN:** File-Centric Patterns
### ❌ **FORBIDDEN:** Bypassing Runtime
### ❌ **FORBIDDEN:** State Divergence
### ❌ **FORBIDDEN:** Direct API Calls

---

## 10. Validation Checklist

When implementing code, verify:
- [ ] No direct infrastructure access (use Public Works abstractions)
- [ ] Zero trust security model (use Security Guard SDK)
- [ ] WAL for all state changes (intent execution logging)
- [ ] Saga pattern for distributed transactions
- [ ] Micro-module architecture (small, focused modules)
- [ ] Artifact-centric patterns (no file-centric)
- [ ] Intent services align to contracts
- [ ] Orchestrators in Journey Realm
- [ ] Contract-based testing
- [ ] No anti-patterns introduced

---

**Last Updated:** January 27, 2026  
**Owner:** Architecture Team  
**Status:** ✅ **ACTIVE - ENFORCE THESE REQUIREMENTS**


---

## 11. Base Classes and Inheritance Patterns

### ✅ **REQUIRED:** Use Base Classes from `/bases/` Folder

**Rule:** Extend base classes from `symphainy_platform/bases/` for orchestrators, intent services, and other components.

**⚠️ IMPORTANT:** BaseContentHandler was an accidental pattern from refactoring and should NOT be persisted. Use proper base classes instead.

**Base Classes Location:** `symphainy_platform/bases/`

**Required Base Classes:**

#### BaseOrchestrator (`symphainy_platform/bases/orchestrator_base.py`)
**Purpose:** Base class for journey orchestrators

**Should Provide:**
- Logger and clock utilities
- Public Works access
- Intent service composition
- SOA API registration
- MCP tool exposure
- Saga coordination
- Telemetry reporting (via Nurse SDK)

**Usage:**
```python
from symphainy_platform.bases.orchestrator_base import BaseOrchestrator

class MyJourneyOrchestrator(BaseOrchestrator):
    async def compose_journey(self, journey_id: str, context: ExecutionContext) -> Dict[str, Any]:
        # Compose intent services into journey
        # Report telemetry via Nurse SDK
        pass
```

---

#### BaseIntentService (`symphainy_platform/bases/intent_service_base.py`)
**Purpose:** Base class for intent services

**Should Provide:**
- Logger and clock utilities
- Public Works access
- Execution context handling
- Artifact creation and registration
- Telemetry reporting (via Nurse SDK)
- Contract compliance validation

**Usage:**
```python
from symphainy_platform.bases.intent_service_base import BaseIntentService

class MyIntentService(BaseIntentService):
    async def execute(self, context: ExecutionContext, params: Dict) -> Artifact:
        # Execute intent service logic
        # Report telemetry via Nurse SDK
        pass
```

---

#### AgentBase (`symphainy_platform/civic_systems/agentic/agent_base.py`)
**Purpose:** Base class for all agents

**Provides:**
- 4-layer model support (AgentDefinition, AgentPosture, AgentRuntimeContext)
- Policy-governed collaboration
- MCP client manager integration
- Telemetry support
- Request processing framework

**Usage:**
```python
from symphainy_platform.civic_systems.agentic.agent_base import AgentBase

class MyAgent(AgentBase):
    async def process_request(self, request: Dict[str, Any], context: AgentRuntimeContext) -> Dict[str, Any]:
        # Implement agent logic
        # Use self.agent_definition, self.agent_posture, context
        # Use self.mcp_client_manager for tool access
        pass
```

---

#### MCPServerBase (`symphainy_platform/civic_systems/agentic/mcp_server_base.py`)
**Purpose:** Base class for MCP servers that expose SOA APIs as MCP tools

**Provides:**
- Tool registration and management
- Tool discovery and metadata
- Tool execution with validation
- Standard MCP server lifecycle management

**Usage:**
```python
from symphainy_platform.civic_systems.agentic.mcp_server_base import MCPServerBase

class MyMCPServer(MCPServerBase):
    async def initialize(self) -> bool:
        # Get SOA APIs from orchestrator
        # Register tools from SOA API definitions
        self.register_tool("my_tool", self.handle_my_tool, input_schema, description)
        return True
    
    async def handle_my_tool(self, **params) -> Dict[str, Any]:
        # Tool handler implementation
        pass
```

---

**Base Classes to Create:**
1. ✅ `BaseOrchestrator` - For journey orchestrators
2. ✅ `BaseIntentService` - For intent services
3. ✅ `AgentBase` - Already exists (keep)
4. ✅ `MCPServerBase` - Already exists (keep)

**Location:** `symphainy_platform/bases/`

**Pattern:**
- All base classes should provide common functionality
- All base classes should integrate with Public Works
- All base classes should support telemetry reporting (via Nurse SDK)
- All base classes should support contract compliance validation


## 12. 4-Dimensional Agentic Configuration Pattern

### ✅ **REQUIRED:** Use 4-Layer Agent Model

**Rule:** All agents must use the 4-layer model for configuration and behavior.

**The 4 Layers:**

#### Layer 1: AgentDefinition (Platform DNA - Stable Identity)
**Location:** `symphainy_platform/civic_systems/agentic/models/agent_definition.py`

**What It Is:**
- Platform-owned, stable identity
- Defines who the agent is, what it's allowed to do
- Never changes (or changes very slowly)
- Stored in agent definition registry

**Contains:**
- `agent_id`: Unique identifier
- `agent_type`: Type (stateless, conversational, specialized, orchestrator)
- `constitution`: Role, mission, non_goals, guardrails
- `capabilities`: List of capabilities
- `permissions`: Allowed tools, MCP servers, required roles
- `collaboration_profile`: Collaboration rules

**Pattern:**
```python
from symphainy_platform.civic_systems.agentic.models.agent_definition import AgentDefinition

AGENT_DEFINITION = AgentDefinition(
    agent_id="my_agent",
    agent_type="specialized",
    constitution={
        "role": "My Agent Role",
        "mission": "My agent mission",
        "non_goals": [...],
        "guardrails": [...]
    },
    capabilities=["capability1", "capability2"],
    permissions={
        "allowed_tools": ["tool1", "tool2"],
        "allowed_mcp_servers": ["mcp_server1"],
        "required_roles": []
    },
    collaboration_profile={...}
)
```

**Storage:**
- JSON/YAML config files in `agent_definitions/` directory
- Loaded via `AgentDefinitionRegistry`
- Can be promoted to Platform DNA via Curator

---

#### Layer 2: AgentPosture (Tenant/Solution - Behavioral Tuning)
**Location:** `symphainy_platform/civic_systems/agentic/models/agent_posture.py`

**What It Is:**
- Tenant/solution-scoped behavioral tuning
- Defines how the agent should behave in this environment
- Changes slowly and deliberately
- Stored in agent posture registry

**Contains:**
- `agent_id`: References AgentDefinition
- `tenant_id`: Tenant identifier (None = platform default)
- `solution_id`: Solution identifier (None = tenant default)
- `posture`: Behavioral posture (autonomy_level, risk_tolerance, compliance_mode)
- `llm_defaults`: LLM configuration (model, temperature, max_tokens)

**Pattern:**
```python
from symphainy_platform.civic_systems.agentic.models.agent_posture import AgentPosture

AGENT_POSTURE = AgentPosture(
    agent_id="my_agent",
    tenant_id="tenant_123",
    solution_id="solution_456",
    posture={
        "autonomy_level": "high",
        "risk_tolerance": "medium",
        "compliance_mode": "strict"
    },
    llm_defaults={
        "model": "gpt-4o-mini",
        "temperature": 0.3,
        "max_tokens": 2000
    }
)
```

**Storage:**
- Stored in agent posture registry
- Loaded via `AgentPostureRegistry`
- Hierarchical lookup: solution → tenant → platform default

---

#### Layer 3: AgentRuntimeContext (Journey/Session - Ephemeral)
**Location:** `symphainy_platform/civic_systems/agentic/models/agent_runtime_context.py`

**What It Is:**
- Ephemeral, session-scoped information
- Assembled at runtime from request/context
- Never persisted to storage
- Replaced for each new request

**Contains:**
- `business_context`: Industry, systems, constraints
- `journey_goal`: Current journey goal
- `available_artifacts`: List of available artifact IDs
- `human_preferences`: Detail level, wants visuals, etc.
- `session_state`: Optional session state (for stateful agents)

**Pattern:**
```python
from symphainy_platform.civic_systems.agentic.models.agent_runtime_context import AgentRuntimeContext

# Create from request and execution context
context = await AgentRuntimeContext.from_request(
    request={"text": "user message", "context": {...}},
    context=execution_context
)
```

**Sources (Priority Order):**
1. Request dict (explicit parameters) - highest priority
2. ExecutionContext.metadata
3. Session state (via context.state_surface)
4. Intent.parameters (via context.intent)

---

#### Layer 4: Prompt Assembly (Derived at Runtime)
**What It Is:**
- Derived from Layers 1-3 at runtime
- Never stored
- Assembled for each request

**Pattern:**
- AgentBase assembles prompt from:
  - Layer 1: Constitution, capabilities, permissions
  - Layer 2: Posture, LLM defaults
  - Layer 3: Business context, journey goal, available artifacts
- Prompt assembly happens in `AgentBase.process_request()`

---

**Why 4 Layers:**
- **Layer 1 (Identity):** Stable, platform-owned, reusable
- **Layer 2 (Behavior):** Tenant/solution-specific, changes slowly
- **Layer 3 (Context):** Ephemeral, request-specific
- **Layer 4 (Prompt):** Derived, never stored

**Anti-Pattern:**
- ❌ Hardcoding prompts in agent code
- ❌ Mixing identity and behavior
- ❌ Persisting runtime context

---

## 13. Smart City System Usage

### ✅ **REQUIRED:** Use Smart City SDK and Primitives for Platform Capabilities

**Rule:** Use Smart City SDKs to prepare execution contracts. Runtime uses Primitives to validate them.

**Smart City Primitives Available:**

#### Security Guard (`symphainy_platform/civic_systems/smart_city/primitives/security_guard_primitives.py`)
**Purpose:** Policy validation and permission checks

**SDK:** `SecurityGuardSDK` (`symphainy_platform/civic_systems/smart_city/sdk/security_guard_sdk.py`)

**Usage:**
```python
from symphainy_platform.civic_systems.smart_city.sdk.security_guard_sdk import SecurityGuardSDK

# Prepare execution contract
security_guard = SecurityGuardSDK(...)
contract = await security_guard.check_permission(
    user_id=user_id,
    tenant_id=tenant_id,
    action="execute_intent",
    resource="content.parse_file"
)

# Runtime validates contract using SecurityGuardPrimitives
```

**⚠️ CRITICAL:** 
- SDKs prepare execution contracts (used by Solution & Smart City)
- Primitives validate contracts (used by Runtime only)
- Runtime never calls SDK methods, only consumes snapshotted registry state

---

#### Data Steward (`symphainy_platform/civic_systems/smart_city/primitives/data_steward_primitives.py`)
**Purpose:** Data governance and policy enforcement

**SDK:** `DataStewardSDK` (`symphainy_platform/civic_systems/smart_city/sdk/data_steward_sdk.py`)

**Usage:**
```python
from symphainy_platform.civic_systems.smart_city.sdk.data_steward_sdk import DataStewardSDK

data_steward = DataStewardSDK(...)
contract = await data_steward.validate_data_policy(
    tenant_id=tenant_id,
    artifact_id=artifact_id,
    operation="read"
)
```

---

#### Traffic Cop (`symphainy_platform/civic_systems/smart_city/primitives/traffic_cop_primitives.py`)
**Purpose:** Rate limiting and traffic management

**SDK:** `TrafficCopSDK` (`symphainy_platform/civic_systems/smart_city/sdk/traffic_cop_sdk.py`)

**Usage:**
```python
from symphainy_platform.civic_systems.smart_city.sdk.traffic_cop_sdk import TrafficCopSDK

traffic_cop = TrafficCopSDK(...)
contract = await traffic_cop.check_rate_limit(
    tenant_id=tenant_id,
    action="execute_intent",
    resource="content.parse_file"
)
```

---

#### Other Smart City Primitives:
- **City Manager:** Platform coordination
- **Conductor:** Orchestration coordination
- **Curator:** Registry coordination
- **Librarian:** Knowledge management
- **Nurse:** Health monitoring
- **Post Office:** Event publishing
- **Materialization Policy:** Materialization policy enforcement

**Pattern:**
1. Use SDK to prepare execution contract
2. Runtime validates contract using Primitives
3. Runtime never calls SDK methods directly

---



---

## 14. Telemetry and Observability

### ✅ **REQUIRED:** Report Telemetry via Nurse SDK

**Rule:** All components must report telemetry via Nurse SDK. Control Tower uses Nurse SDK to pull telemetry together.

**What This Means:**
- All orchestrators report telemetry
- All intent services report telemetry
- All agents report telemetry
- All MCP servers report telemetry
- Control Tower intents use Nurse SDK to aggregate telemetry

**Nurse SDK Location:** `symphainy_platform/civic_systems/smart_city/sdk/nurse_sdk.py`

**Usage:**
```python
from symphainy_platform.civic_systems.smart_city.sdk.nurse_sdk import NurseSDK

nurse_sdk = NurseSDK(telemetry_abstraction=public_works.telemetry_abstraction)

# Report telemetry
telemetry_record = await nurse_sdk.record_telemetry(
    telemetry_data={
        "component": "content_orchestrator",
        "intent": "parse_file",
        "execution_id": execution_id,
        "status": "success",
        "duration_ms": 1234,
        "metrics": {...}
    },
    tenant_id=tenant_id
)
```

**Control Tower Pattern:**
```python
# Control Tower intents use Nurse SDK to pull telemetry together
health_status = await nurse_sdk.get_health_status(
    component_id="content_realm",
    tenant_id=tenant_id
)

# Aggregate telemetry from all components
# Display in Control Tower dashboard
```

**Why:**
- Centralized observability
- Health monitoring
- Performance tracking
- Debugging and troubleshooting

**Components That Must Report Telemetry:**
- Journey Orchestrators
- Intent Services
- Agents
- MCP Servers
- Runtime Execution Engine
- State Surface
- Artifact Registry

---

## 14. Civic Systems Interaction

### ✅ **REQUIRED:** Understand Civic Systems Boundaries

**Rule:** Civic Systems (Experience, Agentic, Smart City) have clear boundaries and responsibilities.

#### Experience Plane
**Location:** `symphainy_platform/civic_systems/experience/`

**Responsibilities:**
- User-facing interfaces
- Intent + Context boundary
- Knows who is talking, why, and in what mode
- Decides which agent should respond
- Owns conversation semantics
- Owns REST API and WebSocket endpoints

**Endpoints:**
- `/api/runtime/agent` (WebSocket) - Agent conversations
- `/api/runtime/intent` (REST) - Intent submission
- `/api/runtime/state` (REST) - State queries

**Pattern:**
```python
# Experience Plane owns endpoints
# Experience Plane routes to Runtime for execution
# Experience Plane streams events back to client
```

---

#### Agentic Framework
**Location:** `symphainy_platform/civic_systems/agentic/`

**Responsibilities:**
- Agent lifecycle management
- Agent registry (definitions, postures)
- MCP server management
- Agent collaboration
- Agent telemetry

**Components:**
- `AgentBase`: Base class for all agents
- `AgentDefinitionRegistry`: Registry for agent definitions
- `AgentPostureRegistry`: Registry for agent postures
- `MCPClientManager`: MCP client management
- `MCPServerBase`: Base class for MCP servers

---

#### Smart City System
**Location:** `symphainy_platform/civic_systems/smart_city/`

**Responsibilities:**
- Policy enforcement
- Service coordination
- Registry management
- Health monitoring

**Components:**
- **Primitives:** Pure functions for policy validation (used by Runtime)
- **SDKs:** Prepare execution contracts (used by Solution & Smart City)
- **Services:** Coordination services (CuratorService, etc.)

---



---

## 15. Deterministic Embeddings Storage

### ✅ **REQUIRED:** Store Deterministic Embeddings in DuckDB

**Rule:** Deterministic embeddings must be stored in DuckDB (via Public Works abstraction), not ArangoDB.

**What This Means:**
- Deterministic embeddings use DuckDB adapter (via Public Works)
- Semantic embeddings (interpretations) can use ArangoDB
- Storage decision is made at intent/journey level
- Public Works abstraction enables storage swapping

**DuckDB Adapter Location:** `symphainy_platform/foundations/public_works/adapters/duckdb_adapter.py`

**Deterministic Compute Abstraction:** `symphainy_platform/foundations/public_works/abstractions/deterministic_compute_abstraction.py`

**Usage:**
```python
from symphainy_platform.foundations.public_works.abstractions.deterministic_compute_abstraction import DeterministicComputeAbstraction

# Deterministic embeddings stored in DuckDB
deterministic_abstraction = DeterministicComputeAbstraction(
    duckdb_adapter=public_works.duckdb_adapter
)

# Store deterministic embeddings
await deterministic_abstraction.store_embeddings(
    artifact_id=artifact_id,
    embeddings=embeddings,
    metadata={...}
)
```

**Intent/Journey Level Decision:**
- `create_deterministic_embeddings` intent → DuckDB storage
- `create_semantic_embeddings` intent → ArangoDB storage (for semantic search)

**Why:**
- DuckDB optimized for analytical workloads
- Deterministic embeddings are analytical data
- Semantic embeddings need graph capabilities (ArangoDB)
- Separation of concerns

---

## 15. Curator and Experience Registration Patterns

### ✅ **REQUIRED:** Register Services with Curator

**Rule:** All services, capabilities, agents, and SOA APIs must be registered with Curator.

**Curator Owns Registries:**
- **Service Registry:** Service instance registration
- **Capability Registry:** Capability registration
- **SOA API Registry:** SOA API endpoint registration
- **Tool Registry:** MCP tool registration
- **Agent Registry:** Agent registration (via Agentic framework)

---

#### Service Registration
**Location:** `symphainy_platform/foundations/curator/registry/service_registry.py`

**Pattern:**
```python
from symphainy_platform.foundations.curator.registry.service_registry import ServiceRegistry

service_registry = ServiceRegistry(service_discovery_abstraction=public_works.service_discovery)

result = await service_registry.register_service(
    service_instance=my_service,
    service_metadata={
        "service_name": "my_service",
        "service_type": "intent_service",
        "address": "localhost",
        "port": 8000,
        "capabilities": ["capability1", "capability2"],
        "realm": "content",
        "tags": ["content", "parsing"]
    }
)
```

**What Happens:**
1. Registers with Consul (via Public Works service discovery abstraction)
2. Registers in local cache (for fast lookups)
3. Returns service_id and registration result

---

#### Capability Registration
**Location:** `symphainy_platform/foundations/curator/registry/capability_registry.py`

**Pattern:**
```python
from symphainy_platform.foundations.curator.registry.capability_registry import CapabilityRegistry
from symphainy_platform.foundations.curator.models.capability_definition import CapabilityDefinition

capability_registry = CapabilityRegistry()

capability = CapabilityDefinition(
    capability_name="parse_file",
    service_name="content_service",
    realm="content",
    description="Parse file content",
    parameters={...},
    returns={...}
)

result = await capability_registry.register_capability(capability)
```

---

#### SOA API Registration
**Location:** `symphainy_platform/foundations/curator/registry/soa_api_registry.py`

**Pattern:**
```python
from symphainy_platform.foundations.curator.registry.soa_api_registry import SOAAPIRegistry

soa_api_registry = SOAAPIRegistry()

result = await soa_api_registry.register_soa_api(
    api_name="parse_file",
    service_name="content_service",
    handler=my_handler_function,
    metadata={
        "description": "Parse file content",
        "parameters": {...},
        "returns": {...}
    }
)
```

**Full API Name:**
- Format: `{service_name}.{api_name}`
- Example: `content_service.parse_file`

---

#### MCP Tool Registration
**Location:** `symphainy_platform/foundations/curator/registry/tool_registry.py`

**Pattern:**
```python
from symphainy_platform.foundations.curator.registry.tool_registry import ToolRegistry

tool_registry = ToolRegistry()

result = await tool_registry.register_mcp_tool(
    tool_name="content_parse_file",
    server_name="content_mcp",
    handler=my_tool_handler,
    input_schema={...},
    description="Parse file content"
)
```

---

#### Curator SDK Usage
**Location:** `symphainy_platform/civic_systems/smart_city/sdk/curator_sdk.py`

**Pattern:**
```python
from symphainy_platform.civic_systems.smart_city.sdk.curator_sdk import CuratorSDK

curator_sdk = CuratorSDK(registry_abstraction=public_works.registry_abstraction)

# Register capability
capability_registration = await curator_sdk.register_capability(
    capability_definition={...},
    tenant_id=tenant_id
)

# Discover agents
agent_discovery = await curator_sdk.discover_agents(
    agent_type="specialized",
    tenant_id=tenant_id
)

# Promote to Platform DNA
registry_id = await curator_sdk.promote_to_platform_dna(
    artifact_id=artifact_id,
    tenant_id=tenant_id,
    registry_type="intent",
    registry_name="parse_file",
    description="Parse file content intent"
)
```

**⚠️ CRITICAL:**
- Curator SDK → Used by Solution & Smart City (registration, discovery)
- Curator Data → Visible to Runtime (read-only, snapshotted registry state)
- Runtime → Never calls Curator SDK methods, only consumes snapshotted registry state

---

## 17. SOA API Patterns

### ✅ **REQUIRED:** Expose Intent Services as SOA APIs

**Rule:** Intent services must be exposed as SOA APIs for realm-to-realm communication.

**Pattern:**
1. **Create Intent Service** in realm
2. **Register SOA API** with SOA API Registry
3. **Expose as MCP Tool** (optional, for agentic consumption)

**Example:**
```python
# 1. Create intent service
class ParseFileIntentService:
    async def execute(self, context: ExecutionContext, params: Dict) -> Artifact:
        # Intent service logic
        pass

# 2. Register SOA API
soa_api_registry = SOAAPIRegistry()
await soa_api_registry.register_soa_api(
    api_name="parse_file",
    service_name="content_service",
    handler=parse_file_service.execute,
    metadata={
        "description": "Parse file content",
        "parameters": {...},
        "returns": {...}
    }
)

# 3. Expose as MCP Tool (optional)
mcp_server = MyMCPServer("content_mcp", "content")
await mcp_server.register_tool(
    tool_name="content_parse_file",
    handler=parse_file_service.execute,
    input_schema={...},
    description="Parse file content"
)
```

**SOA API Naming:**
- Format: `{service_name}.{api_name}`
- Example: `content_service.parse_file`
- Used for realm-to-realm communication

---

## 18. MCP Server Patterns

### ✅ **REQUIRED:** Expose SOA APIs as MCP Tools

**Rule:** MCP servers expose realm SOA APIs as MCP tools for agentic consumption.

**Pattern:**
1. **Extend MCPServerBase**
2. **Initialize MCP Server** with realm name
3. **Register Tools** from SOA API definitions
4. **Expose Tools** to agents via MCP protocol

**Example:**
```python
from symphainy_platform.civic_systems.agentic.mcp_server_base import MCPServerBase

class ContentMCPServer(MCPServerBase):
    def __init__(self, orchestrator):
        super().__init__("content_mcp", "content")
        self.orchestrator = orchestrator
    
    async def initialize(self) -> bool:
        # Get SOA APIs from orchestrator
        soa_apis = await self.orchestrator.get_soa_apis()
        
        # Register each SOA API as MCP tool
        for api in soa_apis:
            self.register_tool(
                tool_name=f"content_{api['api_name']}",
                handler=api['handler'],
                input_schema=api['metadata']['input_schema'],
                description=api['metadata']['description']
            )
        
        return True
```

**MCP Tool Naming:**
- Format: `{realm}_{api_name}`
- Example: `content_parse_file`
- Used for agentic consumption

**Tool Execution:**
```python
# Agent uses MCP tool
result = await mcp_client_manager.call_tool(
    tool_name="content_parse_file",
    parameters={"file_id": "file_123"}
)
```

---

## 19. Experience Plane Integration

### ✅ **REQUIRED:** Experience Plane Owns User-Facing Endpoints

**Rule:** Experience Plane owns all user-facing endpoints (REST API, WebSocket).

**Endpoints:**
- `/api/runtime/agent` (WebSocket) - Agent conversations
- `/api/runtime/intent` (REST) - Intent submission
- `/api/runtime/state` (REST) - State queries

**Pattern:**
```python
# Experience Plane endpoint
@router.websocket("/api/runtime/agent")
async def runtime_agent_websocket(websocket: WebSocket, ...):
    # 1. Authenticate WebSocket connection
    # 2. Accept connection
    # 3. Receive agent messages
    # 4. Experience Plane routes to appropriate agent
    # 5. Experience Plane invokes Runtime for agent execution
    # 6. Runtime executes agent and emits events
    # 7. Experience Plane streams events back to client
```

**Responsibilities:**
- **Experience Plane:** User-facing, knows who is talking, routes to agents
- **Runtime:** Execution engine, stateless, executes agents when told

**⚠️ CRITICAL:**
- Experience Plane owns endpoints (even if path says "runtime")
- Path is a contract (invoke runtime on my behalf), not a locator
- Runtime never knows "users", only execution context

---

## 20. Registry Ownership

### ✅ **REQUIRED:** Curator Owns All Registries

**Rule:** Curator owns and manages all registries (services, capabilities, SOA APIs, tools, agents).

**Registries Owned by Curator:**
1. **Service Registry:** Service instance registration
2. **Capability Registry:** Capability registration
3. **SOA API Registry:** SOA API endpoint registration
4. **Tool Registry:** MCP tool registration
5. **Agent Registry:** Agent registration (via Agentic framework)

**Location:** `symphainy_platform/foundations/curator/registry/`

**Pattern:**
- All registries live in Curator
- Services register with Curator
- Runtime consumes snapshotted registry state (read-only)
- Curator SDK used for registration (Solution & Smart City)
- Primitives used for validation (Runtime)

---

## 21. Additional Patterns

### Execution Context
**Location:** `symphainy_platform/runtime/execution_context.py`

**Contains:**
- `tenant_id`: Tenant identifier
- `user_id`: User identifier
- `session_id`: Session identifier
- `intent`: Intent being executed
- `metadata`: Additional metadata
- `state_surface`: State Surface reference

**Usage:**
- Passed to all intent services
- Passed to all agents
- Used for context propagation

---

### State Surface
**Location:** `symphainy_platform/runtime/state_surface.py`

**Purpose:** Authoritative ledger for artifacts

**Usage:**
- Register artifacts
- Resolve artifacts
- Query artifacts
- Manage artifact lifecycle

---

### Artifact Registry
**Location:** `symphainy_platform/runtime/artifact_registry.py`

**Purpose:** Artifact registration and lifecycle management

**Usage:**
- Register artifacts with lineage
- Query artifacts
- Manage lifecycle states

---

## 22. Validation Checklist (Updated)

When implementing code, verify:

- [ ] No direct infrastructure access (use Public Works abstractions)
- [ ] Zero trust security model (use Security Guard SDK)
- [ ] WAL for all state changes (intent execution logging)
- [ ] Saga pattern for distributed transactions
- [ ] Micro-module architecture (small, focused modules)
- [ ] Artifact-centric patterns (no file-centric)
- [ ] Intent services align to contracts
- [ ] Orchestrators in Journey Realm
- [ ] Contract-based testing
- [ ] **Use base classes from /bases/ folder (BaseOrchestrator, BaseIntentService, AgentBase, MCPServerBase)**
- [ ] **Use 4-layer agent model (AgentDefinition, AgentPosture, AgentRuntimeContext, Prompt Assembly)**
- [ ] **Use Smart City SDKs (prepare contracts) and Primitives (validate contracts)**
- [ ] **Register services/capabilities/SOA APIs with Curator**
- [ ] **Expose SOA APIs as MCP tools for agentic consumption**
- [ ] **Experience Plane owns user-facing endpoints**
- [ ] **Curator owns all registries**
- [ ] **Report telemetry via Nurse SDK (all components)**
- [ ] **Store deterministic embeddings in DuckDB (via abstraction)**
- [ ] No anti-patterns introduced

---

**Last Updated:** January 27, 2026  
**Owner:** Architecture Team  
**Status:** ✅ **ACTIVE - ENFORCE THESE REQUIREMENTS**
