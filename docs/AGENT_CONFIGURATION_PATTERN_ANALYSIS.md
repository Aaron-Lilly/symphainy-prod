# Agent Configuration Pattern Analysis

**Date:** January 2026  
**Status:** 🔍 **PATTERN GAP IDENTIFIED**

---

## Executive Summary

**CURRENT STATE**: Agents use Python files to define AgentDefinition objects  
**EXPECTED STATE**: Agents should use JSON/YAML config files + Python implementation  
**GAP**: Missing JSON/YAML config pattern and incomplete 4-layer model

---

## Current Pattern (What Exists)

### Current Implementation

**Location**: `symphainy_platform/civic_systems/agentic/agent_definitions/`

**Files**:
- `journey_liaison_agent_definition.py` - Python file defining AgentDefinition object
- `structured_extraction_agent_definition.py` - Python file defining AgentDefinition object
- `stateless_agent_definition.py` - Python file defining AgentDefinition object
- `guide_agent_definition.py` - Python file defining AgentDefinition object

**Pattern**:
```python
# journey_liaison_agent_definition.py
from symphainy_platform.civic_systems.agentic.models.agent_definition import AgentDefinition

JOURNEY_LIAISON_AGENT_DEFINITION = AgentDefinition(
    agent_id="journey_liaison_agent",
    agent_type="specialized",
    constitution={
        "role": "Journey Liaison",
        "mission": "Translate human intent into governed journeys",
        ...
    },
    capabilities=[...],
    permissions={...},
    ...
)
```

**What Works**:
- ✅ AgentDefinition model exists
- ✅ Supports JSON serialization (`to_json()`, `from_json()`)
- ✅ Python definitions work

**What's Missing**:
- ❌ No JSON/YAML config files
- ❌ Only Layer 1 (AgentDefinition) exists
- ❌ Layer 2 (AgentPosture) not implemented
- ❌ Layer 3 (AgentRuntimeContext) not implemented
- ❌ Layer 4 (Prompt Assembly) not implemented

---

## Expected Pattern (What Should Exist)

### 4-Layer Model

From `agent_definition.py` documentation:

```
Layer 1: AgentDefinition (Platform DNA - stable identity)
Layer 2: AgentPosture (Tenant/Solution - behavioral tuning)
Layer 3: AgentRuntimeContext (Journey/Session - ephemeral)
Layer 4: Prompt Assembly (derived at runtime)
```

### Expected Structure

**JSON/YAML Config File** (Layer 1):
```json
{
  "agent_id": "journey_liaison_agent",
  "agent_type": "specialized",
  "constitution": {
    "role": "Journey Liaison",
    "mission": "Translate human intent into governed journeys",
    "non_goals": [...],
    "guardrails": [...]
  },
  "capabilities": [...],
  "permissions": {
    "allowed_tools": [...],
    "allowed_mcp_servers": [...]
  },
  "collaboration_profile": {...},
  "version": "1.0.0"
}
```

**Python Implementation** (Agent Logic):
```python
# journey_liaison_agent.py
class JourneyLiaisonAgent(AgentBase):
    def __init__(self, agent_definition_id: str, ...):
        # Load AgentDefinition from JSON/YAML (Layer 1)
        # Load AgentPosture (Layer 2)
        # Initialize with 4-layer model
        ...
```

**Old System Pattern** (Reference):
From `operations_liaison.yaml`:
```yaml
agent_name: OperationsLiaisonAgent
role: Operations Management Liaison
goal: Provide conversational interface...
instructions:
  - Maintain conversation context...
allowed_mcp_servers:
  - SmartCityMCPServer
allowed_tools:
  - sop_generation_tool
capabilities:
  - conversational_guidance
llm_config:
  model: gpt-4o-mini
  temperature: 0.3
```

---

## The Gap

### What's Missing

1. **JSON/YAML Config Files**:
   - No config files in `agent_definitions/` directory
   - Only Python files exist
   - Should have both: JSON/YAML config + Python implementation

2. **Layer 2 (AgentPosture)**:
   - Not implemented
   - Should provide tenant/solution-specific behavioral tuning
   - Should be separate from Layer 1 (Platform DNA)

3. **Layer 3 (AgentRuntimeContext)**:
   - Not implemented
   - Should provide journey/session-specific context
   - Should be ephemeral

4. **Layer 4 (Prompt Assembly)**:
   - Not implemented
   - Should derive prompts from Layers 1-3 at runtime

5. **Config Loading Pattern**:
   - Agents should load from JSON/YAML files
   - Not hardcoded in Python

---

## What Needs to Be Done

### Option 1: JSON Config Files (Recommended)

**Structure**:
```
symphainy_platform/civic_systems/agentic/agent_definitions/
  ├── journey_liaison_agent.json          # Layer 1: Platform DNA
  ├── journey_liaison_agent.py           # Agent implementation
  ├── business_analysis_agent.json        # Layer 1: Platform DNA
  ├── business_analysis_agent.py         # Agent implementation
  └── ...
```

**Pattern**:
1. JSON file defines AgentDefinition (Layer 1)
2. Python file implements agent logic
3. Agent loads definition from JSON at initialization
4. AgentPosture (Layer 2) loaded separately (tenant-specific)
5. AgentRuntimeContext (Layer 3) provided at runtime
6. Prompt Assembly (Layer 4) derived from all layers

### Option 2: YAML Config Files (Alternative)

Same structure, but use YAML instead of JSON (like old system).

### Option 3: Hybrid (Current + JSON)

Keep Python definitions but also generate/load from JSON:
- Python files can generate JSON
- JSON files can be loaded into Python
- Both patterns supported

---

## Implementation Plan

### Step 1: Create JSON Config Files

For each agent, create a JSON file:

**File**: `journey_liaison_agent.json`
```json
{
  "agent_id": "journey_liaison_agent",
  "agent_type": "specialized",
  "constitution": {
    "role": "Journey Liaison",
    "mission": "Translate human intent into governed journeys and workflows",
    "non_goals": [
      "Do not execute actions directly",
      "Do not persist client data",
      "Do not bypass workflow governance"
    ],
    "guardrails": [
      "All actions must be expressed as intents",
      "Escalate ambiguity to Runtime",
      "Validate workflow definitions before creation",
      "Respect tenant-specific workflow constraints"
    ],
    "authority": {
      "can_access": ["journey_realm", "outcomes_realm"],
      "can_read": ["workflows", "sops", "blueprints"],
      "can_write": ["workflows", "sops"]
    }
  },
  "capabilities": [
    "journey_composition",
    "workflow_explanation",
    "human_guidance",
    "sop_generation"
  ],
  "permissions": {
    "allowed_tools": [
      "journey_optimize_process",
      "journey_generate_sop",
      "journey_create_workflow"
    ],
    "allowed_mcp_servers": ["journey_mcp"],
    "required_roles": []
  },
  "collaboration_profile": {
    "can_delegate_to": ["workflow_optimization_agent"],
    "can_be_invoked_by": ["guide_agent", "user"],
    "collaboration_style": "specialized"
  },
  "version": "1.0.0",
  "created_by": "platform"
}
```

### Step 2: Update Agent Implementation

**File**: `journey_liaison_agent.py`
```python
class JourneyLiaisonAgent(AgentBase):
    def __init__(
        self,
        agent_definition_id: str = "journey_liaison_agent",
        agent_definition_path: Optional[str] = None,
        agent_posture_id: Optional[str] = None,
        ...
    ):
        # Load AgentDefinition from JSON (Layer 1)
        if agent_definition_path:
            with open(agent_definition_path, 'r') as f:
                definition_data = json.load(f)
                agent_definition = AgentDefinition.from_dict(definition_data)
        else:
            # Load from registry or default path
            definition_path = f"agent_definitions/{agent_definition_id}.json"
            agent_definition = self._load_definition_from_json(definition_path)
        
        # Load AgentPosture (Layer 2) - if provided
        agent_posture = None
        if agent_posture_id:
            agent_posture = self._load_posture(agent_posture_id)
        
        # Initialize with 4-layer model
        super().__init__(
            agent_id=agent_definition_id,
            agent_definition=agent_definition,
            agent_posture=agent_posture,
            ...
        )
```

### Step 3: Implement Layer 2 (AgentPosture)

**File**: `models/agent_posture.py` (NEW)
```python
@dataclass
class AgentPosture:
    """
    Agent Posture - Layer 2: Tenant/Solution behavioral tuning.
    
    Provides tenant or solution-specific behavioral adjustments
    to the base AgentDefinition (Layer 1).
    """
    posture_id: str
    agent_id: str
    tenant_id: Optional[str] = None
    solution_id: Optional[str] = None
    behavioral_tuning: Dict[str, Any] = field(default_factory=dict)
    custom_instructions: Optional[str] = None
    tool_budgets: Dict[str, int] = field(default_factory=dict)
    cost_limits: Dict[str, float] = field(default_factory=dict)
    safety_rails: List[str] = field(default_factory=list)
    version: str = "1.0.0"
```

### Step 4: Implement Layer 3 (AgentRuntimeContext)

**File**: `models/agent_runtime_context.py` (NEW)
```python
@dataclass
class AgentRuntimeContext:
    """
    Agent Runtime Context - Layer 3: Journey/Session ephemeral context.
    
    Provides journey or session-specific context that is ephemeral
    and not persisted.
    """
    journey_id: Optional[str] = None
    session_id: Optional[str] = None
    user_context: Optional[Dict[str, Any]] = None
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    temporary_state: Dict[str, Any] = field(default_factory=dict)
```

### Step 5: Implement Layer 4 (Prompt Assembly)

**File**: `prompt_assembly.py` (NEW)
```python
class PromptAssembler:
    """
    Prompt Assembler - Layer 4: Runtime prompt derivation.
    
    Assembles prompts from:
    - Layer 1: AgentDefinition (constitution, guardrails)
    - Layer 2: AgentPosture (behavioral tuning, custom instructions)
    - Layer 3: AgentRuntimeContext (journey context, conversation history)
    """
    
    def assemble_prompt(
        self,
        agent_definition: AgentDefinition,
        agent_posture: Optional[AgentPosture],
        runtime_context: AgentRuntimeContext,
        user_message: str
    ) -> Dict[str, str]:
        """
        Assemble system and user prompts from all layers.
        """
        # System message from Layer 1 + Layer 2
        system_message = self._build_system_message(
            agent_definition, agent_posture
        )
        
        # User message with Layer 3 context
        user_message_with_context = self._build_user_message(
            user_message, runtime_context
        )
        
        return {
            "system_message": system_message,
            "user_message": user_message_with_context
        }
```

---

## Migration Strategy

### Phase 1: Generate JSON from Python

1. Use existing Python definitions to generate JSON files
2. Keep Python files for backward compatibility
3. Test loading from JSON

### Phase 2: Implement Layers 2-4

1. Create AgentPosture model
2. Create AgentRuntimeContext model
3. Create PromptAssembler
4. Update agents to use 4-layer model

### Phase 3: Update All Agents

1. Create JSON configs for all agents
2. Update agent implementations to load from JSON
3. Add Layer 2-4 support
4. Test end-to-end

---

## Recommendation

**Use JSON Config Files** (Option 1):
- ✅ Aligns with expected pattern
- ✅ Separates config from code
- ✅ Easy to version and manage
- ✅ Can be loaded at runtime
- ✅ Supports 4-layer model

**Structure**:
```
agent_definitions/
  ├── journey_liaison_agent.json
  ├── journey_liaison_agent.py
  ├── business_analysis_agent.json
  ├── business_analysis_agent.py
  └── ...
```

**Pattern**:
- JSON = Layer 1 (Platform DNA) - stable identity
- Python = Agent implementation - logic
- AgentPosture = Layer 2 (Tenant/Solution) - loaded separately
- AgentRuntimeContext = Layer 3 (Journey/Session) - provided at runtime
- PromptAssembler = Layer 4 - derives prompts from all layers

---

**Status:** Pattern gap identified, implementation plan ready
