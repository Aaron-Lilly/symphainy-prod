# Agentic System Holistic Refactoring Plan

**Date:** January 2026  
**Status:** 📋 **COMPREHENSIVE ARCHITECTURAL REVIEW & REFACTORING PLAN**  
**Scope:** Complete agentic system SDK, configuration, telemetry, and realm integration

---

## Executive Summary

After reviewing the current implementation, the old codebase patterns, and best practices from CrewAI and LangGraph, we've identified significant gaps in our agentic system SDK. This document provides a comprehensive refactoring plan to establish a production-ready, scalable agentic system.

**Key Findings:**
1. ✅ Agent config concept exists but is underutilized (only used for structured extraction)
2. ❌ No standardized agent config registry or schema
3. ❌ Missing agentic telemetry and observability
4. ❌ MCP tool integration incomplete (placeholder implementation)
5. ❌ No agent lifecycle management (creation, health, monitoring)
6. ❌ Realm SOA APIs not properly exposed as MCP tools
7. ❌ Agent collaboration patterns incomplete

---

## Part 1: Holistic Agentic System Refactoring

### 1.1 Agent Configuration System (4-Layer Model)

#### Current State
- Agent config concept exists in old codebase (`agent_config_loader.py`)
- Only used for structured extraction agent
- No centralized registry or validation
- **Problem:** Mixing agent identity, behavioral tuning, and runtime context into one schema

#### Key Insight: Three Kinds of Agent Knowledge

The current schema collapses three different concerns:
1. **Agent Constitution** (platform-owned, stable) - Who the agent is, what it's allowed to do
2. **Agent Posture** (tenant/solution-scoped) - How it behaves in this environment
3. **Agent Context** (journey/session-scoped) - What it knows right now (ephemeral)

**Solution:** Split into 4 layers with clear boundaries.

#### Target State: 4-Layer Configuration Model

1. **Agent Definition** (Platform DNA) - Stable identity, capabilities, permissions
2. **Agent Posture** (Tenant/Solution) - Behavioral tuning, LLM defaults, compliance mode
3. **Agent Runtime Context** (Journey/Session) - Ephemeral hydration, never stored
4. **Prompt Assembly** (Derived) - Assembled at runtime from layers 1-3

#### Implementation

**1.1.1 Create AgentDefinition Model (Layer 1: Platform DNA)**
```python
# symphainy_platform/civic_systems/agentic/models/agent_definition.py

@dataclass
class AgentDefinition:
    """Agent Definition - Platform-owned, stable identity."""
    agent_id: str
    agent_type: str  # "stateless", "conversational", "specialized", "orchestrator"
    constitution: Dict[str, Any]  # role, mission, non_goals, guardrails
    capabilities: List[str]
    permissions: Dict[str, Any]  # allowed_tools, allowed_mcp_servers
    collaboration_profile: Dict[str, Any]  # can_delegate_to, can_be_invoked_by
    version: str
    created_by: Optional[str]
    
    # NO prompt prose here - this is identity, not instruction
    # NO LLM config - that's posture
    # NO runtime context - that's ephemeral
```

**1.1.2 Create AgentPosture Model (Layer 2: Tenant/Solution Scoped)**
```python
# symphainy_platform/civic_systems/agentic/models/agent_posture.py

@dataclass
class AgentPosture:
    """Agent Posture - Behavioral tuning for tenant/solution."""
    agent_id: str
    tenant_id: Optional[str]  # None = platform default
    solution_id: Optional[str]  # None = tenant default
    posture: Dict[str, Any]  # autonomy_level, risk_tolerance, compliance_mode, etc.
    llm_defaults: Dict[str, Any]  # model, temperature, max_tokens
    custom_properties: Dict[str, Any]
    version: str
    created_by: Optional[str]
```

**1.1.3 Create AgentRuntimeContext Model (Layer 3: Journey/Session)**
```python
# symphainy_platform/civic_systems/agentic/models/agent_runtime_context.py

@dataclass
class AgentRuntimeContext:
    """Agent Runtime Context - Ephemeral, never stored."""
    business_context: Dict[str, Any]  # industry, systems, constraints
    journey_goal: str
    available_artifacts: List[str]
    human_preferences: Dict[str, Any]  # detail_level, wants_visuals, etc.
    session_state: Optional[Dict[str, Any]]  # For stateful agents
    
    # This is assembled at runtime, never persisted
    # Fed by landing page questions / journey setup
```

**1.1.4 Create AgentDefinitionRegistry**
```python
# symphainy_platform/civic_systems/agentic/agent_definition_registry.py

class AgentDefinitionRegistry:
    """Registry for agent definitions (Platform DNA) in Supabase."""
    # Similar pattern to ExtractionConfigRegistry
    # - register_definition()
    # - get_definition()
    # - list_definitions()
    # - update_definition()
    # - delete_definition()
    
    # Key: agent_id is unique, versioned
```

**1.1.5 Create AgentPostureRegistry**
```python
# symphainy_platform/civic_systems/agentic/agent_posture_registry.py

class AgentPostureRegistry:
    """Registry for agent postures (Tenant/Solution scoped) in Supabase."""
    # - register_posture()
    # - get_posture(agent_id, tenant_id, solution_id)  # With fallback hierarchy
    # - list_postures()
    # - update_posture()
    # - delete_posture()
    
    # Key: (agent_id, tenant_id, solution_id) with fallback to platform defaults
```

**1.1.6 Create AgentDefinition JSON Schema**
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "agent_id": {"type": "string"},
    "agent_type": {"type": "string", "enum": ["stateless", "conversational", "specialized", "orchestrator"]},
    "constitution": {
      "type": "object",
      "properties": {
        "role": {"type": "string"},
        "mission": {"type": "string"},
        "non_goals": {"type": "array", "items": {"type": "string"}},
        "guardrails": {"type": "array", "items": {"type": "string"}}
      },
      "required": ["role", "mission"]
    },
    "capabilities": {"type": "array", "items": {"type": "string"}},
    "permissions": {
      "type": "object",
      "properties": {
        "allowed_tools": {"type": "array", "items": {"type": "string"}},
        "allowed_mcp_servers": {"type": "array", "items": {"type": "string"}},
        "required_roles": {"type": "array", "items": {"type": "string"}}
      }
    },
    "collaboration_profile": {
      "type": "object",
      "properties": {
        "can_delegate_to": {"type": "array", "items": {"type": "string"}},
        "can_be_invoked_by": {"type": "array", "items": {"type": "string"}}
      }
    },
    "version": {"type": "string", "default": "1.0.0"},
    "created_by": {"type": ["string", "null"]}
  },
  "required": ["agent_id", "agent_type", "constitution", "capabilities"]
}
```

**1.1.7 Create AgentPosture JSON Schema**
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "agent_id": {"type": "string"},
    "tenant_id": {"type": ["string", "null"]},
    "solution_id": {"type": ["string", "null"]},
    "posture": {
      "type": "object",
      "properties": {
        "autonomy_level": {"type": "string", "enum": ["autonomous", "guided", "supervised"]},
        "risk_tolerance": {"type": "string", "enum": ["low", "medium", "high"]},
        "human_interaction_style": {"type": "string", "enum": ["collaborative", "delegative", "autonomous"]},
        "compliance_mode": {"type": "string", "enum": ["strict", "moderate", "permissive"]},
        "explain_decisions": {"type": "boolean"}
      }
    },
    "llm_defaults": {
      "type": "object",
      "properties": {
        "model": {"type": "string"},
        "temperature": {"type": "number", "minimum": 0.0, "maximum": 2.0},
        "max_tokens": {"type": "integer", "minimum": 1},
        "timeout": {"type": "integer", "minimum": 1}
      }
    },
    "custom_properties": {"type": "object", "additionalProperties": true},
    "version": {"type": "string", "default": "1.0"},
    "created_by": {"type": ["string", "null"]}
  },
  "required": ["agent_id", "posture", "llm_defaults"]
}
```

### 1.2 Agent Base Class Enhancement

#### Current State
- Basic `AgentBase` with `process_request()` and `_call_llm()`
- Collaboration router placeholder
- MCP tool integration placeholder

#### Target State
- **Config-driven initialization** (load from AgentConfigRegistry)
- **MCP tool integration** (via MCP Client Manager)
- **Agentic telemetry** (tracking, metrics, health)
- **State management** (for stateful agents)
- **Tool composition** (chain tools, orchestrate workflows)

#### Implementation

**1.2.1 Enhance AgentBase (4-Layer Model)**
```python
# symphainy_platform/civic_systems/agentic/agent_base.py

class AgentBase(ABC):
    def __init__(
        self,
        agent_id: str,
        agent_definition: Optional[AgentDefinition] = None,  # Layer 1: Platform DNA
        agent_definition_id: Optional[str] = None,  # Load from registry
        agent_posture: Optional[AgentPosture] = None,  # Layer 2: Tenant/Solution
        agent_posture_id: Optional[str] = None,  # Load from registry
        tenant_id: Optional[str] = None,  # For posture lookup
        solution_id: Optional[str] = None,  # For posture lookup
        collaboration_router: Optional[CollaborationRouter] = None,
        public_works: Optional[Any] = None,
        mcp_client_manager: Optional[Any] = None,  # NEW: MCP integration
        agent_registry: Optional[AgentRegistry] = None,  # NEW: Registry access
        telemetry_service: Optional[Any] = None  # NEW: Telemetry
    ):
        # Load definition if definition_id provided
        if agent_definition_id and not agent_definition:
            agent_definition = self._load_definition(agent_definition_id)
        
        # Load posture if posture_id provided (with fallback hierarchy)
        if agent_posture_id and not agent_posture:
            agent_posture = self._load_posture(
                agent_id=agent_id,
                tenant_id=tenant_id,
                solution_id=solution_id
            )
        
        # Initialize with definition (Layer 1: Identity)
        if agent_definition:
            self.agent_definition = agent_definition
            self.agent_id = agent_definition.agent_id
            self.agent_type = agent_definition.agent_type
            self.constitution = agent_definition.constitution
            self.capabilities = agent_definition.capabilities
            self.permissions = agent_definition.permissions
            self.collaboration_profile = agent_definition.collaboration_profile
        
        # Initialize with posture (Layer 2: Behavioral tuning)
        if agent_posture:
            self.agent_posture = agent_posture
            self.posture = agent_posture.posture
            self.llm_defaults = agent_posture.llm_defaults
        
        # MCP Client Manager for tool access
        self.mcp_client_manager = mcp_client_manager
        
        # Telemetry service
        self.telemetry_service = telemetry_service
    
    async def process_request(
        self,
        request: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """
        Process request with 4-layer model.
        
        Layers:
        1. Agent Definition (identity) - already loaded
        2. Agent Posture (behavior) - already loaded
        3. Runtime Context (hydration) - assembled from request/context
        4. Prompt Assembly (derived) - assembled at call time
        """
        # Layer 3: Assemble runtime context (ephemeral, never stored)
        runtime_context = AgentRuntimeContext(
            business_context=request.get("business_context", {}),
            journey_goal=request.get("journey_goal", ""),
            available_artifacts=request.get("available_artifacts", []),
            human_preferences=request.get("human_preferences", {}),
            session_state=await self._get_session_state(context) if self.is_stateful() else None
        )
        
        # Layer 4: Assemble prompt (derived from layers 1-3)
        system_message = self._assemble_system_message(runtime_context)
        user_message = self._assemble_user_message(request, runtime_context)
        
        # Process with assembled prompt
        return await self._process_with_assembled_prompt(
            system_message=system_message,
            user_message=user_message,
            runtime_context=runtime_context,
            context=context
        )
    
    def _assemble_system_message(self, runtime_context: AgentRuntimeContext) -> str:
        """
        Assemble system message from layers 1-3.
        
        This is where the magic happens - clean separation of concerns.
        """
        parts = []
        
        # Layer 1: Constitution (identity)
        if self.constitution:
            parts.append(f"You are the {self.constitution.get('role', 'Agent')}.")
            parts.append(f"Mission: {self.constitution.get('mission', '')}")
            if self.constitution.get('non_goals'):
                parts.append("Non-goals:")
                for non_goal in self.constitution['non_goals']:
                    parts.append(f"  - {non_goal}")
            if self.constitution.get('guardrails'):
                parts.append("Guardrails:")
                for guardrail in self.constitution['guardrails']:
                    parts.append(f"  - {guardrail}")
        
        # Layer 2: Posture (behavioral tuning)
        if self.posture:
            parts.append(f"\nBehavioral Posture:")
            parts.append(f"  - Autonomy: {self.posture.get('autonomy_level', 'guided')}")
            parts.append(f"  - Risk Tolerance: {self.posture.get('risk_tolerance', 'medium')}")
            parts.append(f"  - Compliance: {self.posture.get('compliance_mode', 'moderate')}")
            if self.posture.get('explain_decisions'):
                parts.append("  - Always explain your decisions")
        
        # Layer 3: Runtime Context (hydration)
        if runtime_context.business_context:
            parts.append(f"\nBusiness Context:")
            parts.append(f"  - Industry: {runtime_context.business_context.get('industry', 'unknown')}")
            if runtime_context.business_context.get('systems'):
                parts.append(f"  - Systems: {', '.join(runtime_context.business_context['systems'])}")
            if runtime_context.business_context.get('constraints'):
                parts.append("  - Constraints:")
                for constraint in runtime_context.business_context['constraints']:
                    parts.append(f"    - {constraint}")
        
        if runtime_context.journey_goal:
            parts.append(f"\nCurrent Goal: {runtime_context.journey_goal}")
        
        return "\n".join(parts)
    
    async def use_tool(
        self,
        tool_name: str,
        params: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Use MCP tool (REAL implementation)."""
        if not self.mcp_client_manager:
            raise ValueError("MCP Client Manager not available")
        
        # Validate tool access (check allowed_tools)
        if self.allowed_tools and tool_name not in self.allowed_tools:
            raise ValueError(f"Tool {tool_name} not allowed for agent {self.agent_id}")
        
        # Execute via MCP Client Manager
        result = await self.mcp_client_manager.execute_tool(
            server_name=self._resolve_server_for_tool(tool_name),
            tool_name=tool_name,
            parameters=params,
            user_context={
                "tenant_id": context.tenant_id,
                "session_id": context.session_id,
                "solution_id": context.solution_id
            }
        )
        
        # Track tool usage (telemetry)
        await self._track_tool_usage(tool_name, params, result, context)
        
        return result
    
    async def _track_tool_usage(
        self,
        tool_name: str,
        params: Dict[str, Any],
        result: Dict[str, Any],
        context: ExecutionContext
    ):
        """Track tool usage for telemetry."""
        if self.telemetry_service:
            await self.telemetry_service.record_agent_tool_usage(
                agent_id=self.agent_id,
                tool_name=tool_name,
                parameters=params,
                result=result,
                context=context
            )
```

### 1.3 MCP Client Manager Integration

#### Current State
- MCP Client Manager exists in old codebase
- Not integrated into current agentic system
- MCP servers created but not connected

#### Target State
- **MCP Client Manager** integrated into AgentBase
- **Tool discovery** from realm MCP servers
- **Tool execution** with proper context
- **Tool access control** (allowed_tools per agent)

#### Implementation

**1.3.1 Create MCP Client Manager**
```python
# symphainy_platform/civic_systems/agentic/mcp_client_manager.py

class MCPClientManager:
    """Manages MCP client connections to realm MCP servers."""
    
    def __init__(self, public_works: Optional[Any] = None):
        self.public_works = public_works
        self._servers: Dict[str, Any] = {}  # server_name -> MCP Server
    
    async def discover_servers(self) -> List[str]:
        """Discover available MCP servers."""
        # Discover realm MCP servers:
        # - insights_mcp
        # - content_mcp
        # - journey_mcp
        # - outcomes_mcp
        pass
    
    async def connect_to_server(self, server_name: str) -> bool:
        """Connect to an MCP server."""
        pass
    
    async def get_tool_list(self, server_name: str) -> List[str]:
        """Get list of tools from a server."""
        pass
    
    async def execute_tool(
        self,
        server_name: str,
        tool_name: str,
        parameters: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a tool via MCP."""
        pass
```

### 1.4 Agentic Telemetry System

#### Current State
- No agentic-specific telemetry
- Basic logging in agents
- No cost tracking, performance metrics, or health monitoring

#### Target State
- **Agent execution tracking** (prompts, responses, tokens, costs)
- **Tool usage tracking** (which tools, how often, success/failure)
- **Performance metrics** (latency, throughput, error rates)
- **Health monitoring** (agent availability, resource usage)
- **Cost tracking** (LLM costs per agent, per tenant)

#### Implementation

**1.4.1 Create Agentic Telemetry Service**
```python
# symphainy_platform/civic_systems/agentic/telemetry/agentic_telemetry_service.py

class AgenticTelemetryService:
    """Telemetry service for agentic system."""
    
    async def record_agent_execution(
        self,
        agent_id: str,
        agent_name: str,
        prompt: str,
        response: str,
        model_name: str,
        tokens: Dict[str, int],
        cost: float,
        latency_ms: float,
        context: ExecutionContext
    ):
        """Record agent execution for telemetry."""
        pass
    
    async def record_agent_tool_usage(
        self,
        agent_id: str,
        tool_name: str,
        parameters: Dict[str, Any],
        result: Dict[str, Any],
        context: ExecutionContext
    ):
        """Record tool usage."""
        pass
    
    async def record_agent_health(
        self,
        agent_id: str,
        health_status: Dict[str, Any]
    ):
        """Record agent health metrics."""
        pass
    
    async def get_agent_metrics(
        self,
        agent_id: str,
        time_range: Optional[Tuple[datetime, datetime]] = None
    ) -> Dict[str, Any]:
        """Get agent metrics for time range."""
        pass
```

**1.4.2 Create Agentic Telemetry Registry**
```sql
-- migrations/014_create_agentic_telemetry_registry.sql

CREATE TABLE agentic_execution_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    tenant_id TEXT NOT NULL,
    session_id TEXT,
    execution_id TEXT,
    prompt_hash TEXT,
    prompt_tokens INTEGER,
    completion_tokens INTEGER,
    total_tokens INTEGER,
    cost DECIMAL(10, 6),
    latency_ms INTEGER,
    model_name TEXT,
    success BOOLEAN,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE agentic_tool_usage_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id TEXT NOT NULL,
    tool_name TEXT NOT NULL,
    server_name TEXT,
    parameters JSONB,
    result JSONB,
    success BOOLEAN,
    latency_ms INTEGER,
    tenant_id TEXT NOT NULL,
    session_id TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE agentic_health_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    health_status JSONB,
    tenant_id TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 1.5 Agent Registry Enhancement

#### Current State
- Basic in-memory registry
- No persistence
- No health monitoring

#### Target State
- **Persistent registry** (Supabase)
- **Health monitoring** (agent availability, performance)
- **Agent lifecycle management** (create, update, delete, disable)
- **Agent discovery** (by type, capability, realm)

#### Implementation

**1.5.1 Enhance AgentRegistry**
```python
# symphainy_platform/civic_systems/agentic/agent_registry.py

class AgentRegistry:
    """Enhanced agent registry with persistence and health monitoring."""
    
    def __init__(self, supabase_adapter: Optional[Any] = None):
        self.supabase_adapter = supabase_adapter
        self._agents: Dict[str, AgentBase] = {}
        self._health_monitor: Optional[AgentHealthMonitor] = None
    
    async def register_agent(
        self,
        agent: AgentBase,
        persist: bool = True
    ) -> bool:
        """Register agent (with optional persistence)."""
        # Register in memory
        self._agents[agent.agent_id] = agent
        
        # Persist to Supabase if adapter available
        if persist and self.supabase_adapter:
            await self._persist_agent(agent)
        
        # Start health monitoring
        if self._health_monitor:
            await self._health_monitor.start_monitoring(agent.agent_id)
        
        return True
    
    async def get_agent_health(self, agent_id: str) -> Dict[str, Any]:
        """Get agent health status."""
        if self._health_monitor:
            return await self._health_monitor.get_health(agent_id)
        return {"status": "unknown"}
```

**1.5.2 Create Agent Health Monitor**
```python
# symphainy_platform/civic_systems/agentic/health/agent_health_monitor.py

class AgentHealthMonitor:
    """Monitor agent health and performance."""
    
    async def start_monitoring(self, agent_id: str):
        """Start monitoring an agent."""
        pass
    
    async def get_health(self, agent_id: str) -> Dict[str, Any]:
        """Get agent health status."""
        pass
    
    async def record_health_metric(
        self,
        agent_id: str,
        metric_name: str,
        value: float
    ):
        """Record health metric."""
        pass
```

---

## Part 2: Realm-Specific Refactoring

### 2.1 Insights Realm

#### Current State
- ✅ Structured extraction SOA APIs defined
- ✅ MCP server created
- ✅ Tools auto-registered

#### Required Updates
- ✅ **Already complete** - serves as reference implementation

### 2.2 Content Realm

#### Current State
- ❌ No SOA API definitions
- ✅ MCP server created (empty)

#### Required Updates

**2.2.1 Define Content Orchestrator SOA APIs**
```python
# symphainy_platform/realms/content/orchestrators/content_orchestrator.py

def _define_soa_api_handlers(self) -> Dict[str, Any]:
    """Define Content Orchestrator SOA APIs."""
    return {
        "ingest_file": {
            "handler": self._handle_ingest_file,
            "input_schema": {
                "type": "object",
                "properties": {
                    "file_data": {"type": "object"},
                    "file_type": {"type": "string"},
                    "metadata": {"type": "object"}
                },
                "required": ["file_data"]
            },
            "description": "Ingest a file for processing"
        },
        "parse_content": {
            "handler": self._handle_parse_content,
            "input_schema": {
                "type": "object",
                "properties": {
                    "parsed_file_id": {"type": "string"},
                    "parse_options": {"type": "object"}
                },
                "required": ["parsed_file_id"]
            },
            "description": "Parse content from ingested file"
        },
        "extract_embeddings": {
            "handler": self._handle_extract_embeddings,
            "input_schema": {
                "type": "object",
                "properties": {
                    "parsed_file_id": {"type": "string"},
                    "embedding_options": {"type": "object"}
                },
                "required": ["parsed_file_id"]
            },
            "description": "Extract embeddings from parsed content"
        }
    }
```

### 2.3 Journey Realm

#### Current State
- ❌ No SOA API definitions
- ✅ MCP server created (empty)

#### Required Updates

**2.3.1 Define Journey Orchestrator SOA APIs**
```python
# symphainy_platform/realms/journey/orchestrators/journey_orchestrator.py

def _define_soa_api_handlers(self) -> Dict[str, Any]:
    """Define Journey Orchestrator SOA APIs."""
    return {
        "optimize_process": {
            "handler": self._handle_optimize_process,
            "input_schema": {
                "type": "object",
                "properties": {
                    "process_data": {"type": "object"},
                    "optimization_goals": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["process_data"]
            },
            "description": "Optimize a business process"
        },
        "generate_sop": {
            "handler": self._handle_generate_sop,
            "input_schema": {
                "type": "object",
                "properties": {
                    "process_description": {"type": "string"},
                    "sop_template": {"type": "string"}
                },
                "required": ["process_description"]
            },
            "description": "Generate Standard Operating Procedure"
        },
        "create_workflow": {
            "handler": self._handle_create_workflow,
            "input_schema": {
                "type": "object",
                "properties": {
                    "workflow_definition": {"type": "object"},
                    "workflow_name": {"type": "string"}
                },
                "required": ["workflow_definition"]
            },
            "description": "Create a workflow"
        }
    }
```

### 2.4 Outcomes Realm

#### Current State
- ❌ No SOA API definitions
- ✅ MCP server created (empty)

#### Required Updates

**2.4.1 Define Outcomes Orchestrator SOA APIs**
```python
# symphainy_platform/realms/outcomes/orchestrators/outcomes_orchestrator.py

def _define_soa_api_handlers(self) -> Dict[str, Any]:
    """Define Outcomes Orchestrator SOA APIs."""
    return {
        "synthesize_outcome": {
            "handler": self._handle_synthesize_outcome,
            "input_schema": {
                "type": "object",
                "properties": {
                    "input_data": {"type": "object"},
                    "outcome_type": {"type": "string"}
                },
                "required": ["input_data"]
            },
            "description": "Synthesize an outcome from input data"
        },
        "generate_roadmap": {
            "handler": self._handle_generate_roadmap,
            "input_schema": {
                "type": "object",
                "properties": {
                    "project_context": {"type": "object"},
                    "roadmap_type": {"type": "string"}
                },
                "required": ["project_context"]
            },
            "description": "Generate a roadmap"
        },
        "create_poc": {
            "handler": self._handle_create_poc,
            "input_schema": {
                "type": "object",
                "properties": {
                    "poc_requirements": {"type": "object"},
                    "poc_name": {"type": "string"}
                },
                "required": ["poc_requirements"]
            },
            "description": "Create a Proof of Concept"
        }
    }
```

---

## Part 3: New Artifacts and Registries

### 3.1 Agent Definition Registry (Supabase)

**Migration:** `015_create_agent_definition_registry.sql`

```sql
CREATE TABLE agent_definition_registry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id TEXT UNIQUE NOT NULL,
    agent_type TEXT NOT NULL,
    definition_data JSONB NOT NULL,  -- AgentDefinition JSON
    version TEXT DEFAULT '1.0.0',
    created_by TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_agent_definition_registry_agent_id ON agent_definition_registry(agent_id);
CREATE INDEX idx_agent_definition_registry_agent_type ON agent_definition_registry(agent_type);
```

### 3.2 Agent Posture Registry (Supabase)

**Migration:** `016_create_agent_posture_registry.sql`

```sql
CREATE TABLE agent_posture_registry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id TEXT NOT NULL,
    tenant_id TEXT,  -- NULL = platform default
    solution_id TEXT,  -- NULL = tenant default
    posture_data JSONB NOT NULL,  -- AgentPosture JSON
    version TEXT DEFAULT '1.0',
    created_by TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(agent_id, tenant_id, solution_id)
);

CREATE INDEX idx_agent_posture_registry_agent_id ON agent_posture_registry(agent_id);
CREATE INDEX idx_agent_posture_registry_tenant_id ON agent_posture_registry(tenant_id);
CREATE INDEX idx_agent_posture_registry_solution_id ON agent_posture_registry(solution_id);
-- Fallback lookup: (agent_id, tenant_id, NULL) for solution-level fallback
-- Fallback lookup: (agent_id, NULL, NULL) for platform default
```

### 3.3 Agent Registry (Supabase)

**Migration:** `017_create_agent_registry.sql`

```sql
CREATE TABLE agent_registry (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id TEXT UNIQUE NOT NULL,
    agent_name TEXT NOT NULL,
    agent_type TEXT NOT NULL,
    agent_config_id TEXT,
    capabilities JSONB,
    required_roles JSONB,
    tenant_id TEXT,
    status TEXT DEFAULT 'active',  -- 'active', 'disabled', 'error'
    health_status JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_agent_registry_agent_id ON agent_registry(agent_id);
CREATE INDEX idx_agent_registry_agent_type ON agent_registry(agent_type);
CREATE INDEX idx_agent_registry_tenant_id ON agent_registry(tenant_id);
CREATE INDEX idx_agent_registry_status ON agent_registry(status);
```

### 3.3 Agentic Telemetry Registry

**Migration:** `014_create_agentic_telemetry_registry.sql` (already defined in 1.4.2)

---

## Part 4: Implementation Phases

### Phase 1: Foundation (Week 1)
1. ✅ Create AgentDefinition model and JSON Schema (Layer 1: Platform DNA)
2. ✅ Create AgentPosture model and JSON Schema (Layer 2: Tenant/Solution)
3. ✅ Create AgentRuntimeContext model (Layer 3: Journey/Session - ephemeral)
4. ✅ Create AgentDefinitionRegistry
5. ✅ Create AgentPostureRegistry
6. ✅ Create agent definition/posture registry migrations
7. ✅ Create MCP Client Manager
8. ✅ Enhance AgentBase with 4-layer model (prompt assembly)

### Phase 2: Telemetry & Monitoring (Week 1-2)
1. ✅ Create AgenticTelemetryService
2. ✅ Create agentic telemetry registry migration
3. ✅ Integrate telemetry into AgentBase
4. ✅ Create AgentHealthMonitor
5. ✅ Enhance AgentRegistry with persistence

### Phase 3: Realm SOA APIs (Week 2)
1. ✅ Add SOA API definitions to Content Orchestrator
2. ✅ Add SOA API definitions to Journey Orchestrator
3. ✅ Add SOA API definitions to Outcomes Orchestrator
4. ✅ Test MCP tool registration for all realms

### Phase 4: Agent Definition/Posture Migration (Week 2-3)
1. ✅ Create agent definitions for existing agents (Layer 1)
2. ✅ Create agent postures for existing agents (Layer 2)
3. ✅ Migrate existing agents to use 4-layer model
4. ✅ Create pre-configured agent definitions (like extraction configs)
5. ✅ Test definition/posture-driven agent initialization
6. ✅ Update landing page to collect runtime context (Layer 3)

### Phase 5: Testing & Validation (Week 3)
1. ✅ E2E tests with real LLM calls
2. ✅ MCP tool execution tests
3. ✅ Telemetry validation
4. ✅ Health monitoring validation

---

## Part 5: Best Practices Integration

### 5.1 CrewAI Patterns
- ✅ **Externalized configs** (YAML/JSON files)
- ✅ **Role/Goal/Backstory** pattern → **Refined to Constitution (Layer 1)**
- ✅ **Dynamic placeholders** (for runtime interpolation) → **Runtime Context (Layer 3)**
- ✅ **Separation of concerns** (configs separate from code) → **4-Layer Model**

### 5.2 LangGraph Patterns
- ✅ **State management** (for stateful agents) → **Runtime Context (Layer 3)**
- ✅ **Tool composition** (chain tools, orchestrate workflows)
- ✅ **Checkpointing** (save agent state for recovery)
- ✅ **ReAct pattern** (reason, act, reflect)

### 5.3 SymphAIny Patterns
- ✅ **JSON Schema validation** (consistent with extraction configs)
- ✅ **Supabase registry** (persistent storage)
- ✅ **MCP tool integration** (agents use tools, not direct calls)
- ✅ **Governed LLM access** (via _call_llm())
- ✅ **Tenant isolation** (multi-tenant support)

### 5.4 4-Layer Model Benefits (NEW)

**What this solves:**
- ✅ **Reduces prompt entropy** - Clear separation of identity, behavior, context
- ✅ **Makes behavior predictable** - Posture is explicit, not inferred
- ✅ **Gives knobs that actually work** - LLM models respect clear boundaries
- ✅ **Aligns with LLM reality** - Models are good at following clear role boundaries
- ✅ **Prevents config overload** - Each layer has a single responsibility

**What models are good at:**
- Following clear role boundaries (Layer 1: Constitution)
- Using tools when explicitly allowed (Layer 1: Permissions)
- Operating under constraints when repeated consistently (Layer 2: Posture)
- Adapting to context when clearly provided (Layer 3: Runtime Context)

**What models are bad at:**
- Remembering long backstories reliably → **Fixed: Constitution is concise**
- Inferring governance from prose → **Fixed: Guardrails are explicit**
- Respecting "soft" instructions over time → **Fixed: Posture is declarative**
- Being consistent when configs are overloaded → **Fixed: 4-layer separation**

---

## Part 6: Migration Strategy

### 6.1 Existing Agents
1. **StructuredExtractionAgent** - Already uses config pattern (extraction config)
   - Create AgentDefinition (Layer 1: Constitution, capabilities, permissions)
   - Create AgentPosture (Layer 2: LLM defaults, behavioral tuning)
   - Migrate to use 4-layer model
   - Runtime context assembled from extraction request

2. **StatelessAgent** - Basic implementation
   - Create AgentDefinition (stateless agent identity)
   - Create AgentPosture (default posture, can be overridden per tenant)
   - Add MCP tool integration
   - Add telemetry

3. **ConversationalAgent** - Basic implementation
   - Create AgentDefinition (conversational agent identity)
   - Create AgentPosture (stateful posture, conversation history limits)
   - Add state management (Layer 3: Runtime Context)
   - Add telemetry

### 6.2 New Agents
- All new agents must:
  1. Use AgentDefinitionRegistry (Layer 1)
  2. Use AgentPostureRegistry (Layer 2)
  3. Accept AgentRuntimeContext (Layer 3)
  4. Assemble prompts from layers 1-3 (Layer 4)
  5. Integrate MCP Client Manager
  6. Use AgenticTelemetryService
  7. Follow JSON Schema validation

### 6.3 Landing Page Integration

**Instead of:** "Configure your agent"

**Ask:** "Set the working conditions"

**Example inputs:**
- What are you trying to accomplish? → `journey_goal` (Layer 3)
- How complete does the answer need to be? → `human_preferences.detail_level` (Layer 3)
- Are you exploring or preparing for execution? → `posture.autonomy_level` (Layer 2)
- What systems should we assume are in play? → `business_context.systems` (Layer 3)
- What should *not* be automated? → `business_context.constraints` (Layer 3)

**These feed Runtime Context (Layer 3), not agent config.**

---

## Part 7: Success Criteria

### 7.1 Functional Requirements
- ✅ Agents use 4-layer model (Definition, Posture, Runtime Context, Prompt Assembly)
- ✅ Agent definitions are platform-owned and stable (Layer 1)
- ✅ Agent postures are tenant/solution-scoped (Layer 2)
- ✅ Runtime context is ephemeral and never stored (Layer 3)
- ✅ Prompts are assembled at runtime from layers 1-3 (Layer 4)
- ✅ Agents can discover and use MCP tools
- ✅ Agent execution is tracked (telemetry)
- ✅ Agent health is monitored
- ✅ All realm SOA APIs exposed as MCP tools

### 7.2 Non-Functional Requirements
- ✅ **4-layer separation** (identity, behavior, context, assembly)
- ✅ **Config-driven** (no hard-coded agent behavior)
- ✅ **Observable** (telemetry, metrics, health)
- ✅ **Scalable** (registry-based, persistent)
- ✅ **Maintainable** (clear boundaries, single responsibility per layer)
- ✅ **Testable** (E2E tests with real LLM)
- ✅ **Predictable** (LLM models respect clear boundaries)
- ✅ **Aligned with LLM reality** (what models are good/bad at)

---

## Part 8: Next Steps

1. **Review this plan** with stakeholders
2. **Prioritize phases** based on demo needs
3. **Start Phase 1** (Foundation)
4. **Iterate** based on feedback

---

**Status:** 📋 **READY FOR IMPLEMENTATION**

This comprehensive refactoring plan establishes a production-ready agentic system SDK that aligns with best practices from CrewAI, LangGraph, and our own architectural principles.

## Key Refinement: 4-Layer Model

**The critical insight:** We're not building "a better agent configuration system." We're building:

> **A separation of identity, authority, posture, and context — so humans, agents, and systems can coexist without chaos.**

This 4-layer model:
- **Reduces prompt entropy** - Clear separation of concerns
- **Makes behavior predictable** - Posture is explicit, not inferred
- **Gives knobs that actually work** - LLM models respect clear boundaries
- **Aligns with LLM reality** - Models are good at following clear role boundaries, bad at inferring from prose
- **Prevents config overload** - Each layer has a single responsibility

**This is not noise.** This is the architectural foundation that will make our agentic system maintainable, predictable, and scalable.
