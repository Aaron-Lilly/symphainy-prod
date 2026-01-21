# Enhanced Structured Extraction Framework - Implementation Plan

**Date:** January 2026  
**Status:** 📋 **Ready for Implementation**  
**Purpose:** Universal structured extraction framework with MCP tools, interactive config, and freeform discovery

---

## Vision

Create a **universal structured extraction capability** that:
1. Exposes SOA API for extraction operations
2. Provides MCP Tools for agentic consumption (via Insights Realm MCP Server)
3. Supports pre-configured patterns (VariableLifePolicyRules, AfterActionReview, PermitSemanticObject)
4. Enables custom configs via interactive chat, file upload, or target data model
5. Supports freeform analysis where agents discover extraction patterns

---

## Architecture Overview

### Layer 1: StructuredExtractionService (SOA API)

**Location:** `symphainy_platform/realms/insights/enabling_services/structured_extraction_service.py`

**Purpose:** Core extraction service with SOA API methods

**Key Methods:**
```python
class StructuredExtractionService:
    # SOA API Methods (exposed via MCP)
    async def extract_structured_data(
        self,
        pattern: str,  # "variable_life_policy_rules", "aar", "pso", "custom", "discover"
        data_source: Dict[str, Any],
        extraction_config_id: Optional[str] = None,  # For custom patterns
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Extract structured data using pattern or custom config."""
    
    async def discover_extraction_pattern(
        self,
        data_source: Dict[str, Any],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Discover extraction pattern from data (freeform analysis)."""
    
    async def create_extraction_config_from_target_model(
        self,
        target_model_file_id: str,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Generate extraction config from target data model."""
```

### Layer 2: Realm MCP Server Integration (All 4 Realms)

**Pattern:** Create MCP servers for all 4 realms following old codebase auto-register pattern

**Realms:**
1. **Content Realm** - `symphainy_platform/realms/content/mcp_server/content_mcp_server.py`
2. **Insights Realm** - `symphainy_platform/realms/insights/mcp_server/insights_mcp_server.py`
3. **Journey Realm** - `symphainy_platform/realms/journey/mcp_server/journey_mcp_server.py`
4. **Outcomes Realm** - `symphainy_platform/realms/outcomes/mcp_server/outcomes_mcp_server.py`

**Pattern (from old codebase):**
- Orchestrator defines `_define_soa_api_handlers()` method
- MCP Server automatically registers SOA APIs as MCP tools
- Agents access via MCP Client Manager (from Agentic System)

**Insights Realm SOA APIs (for extraction):**
```python
# In InsightsOrchestrator
def _define_soa_api_handlers(self) -> Dict[str, Any]:
    return {
        "extract_structured_data": {
            "handler": self._handle_extract_structured_data,
            "input_schema": {...},
            "description": "Extract structured data using pre-configured or custom pattern"
        },
        "discover_extraction_pattern": {
            "handler": self._handle_discover_extraction_pattern,
            "input_schema": {...},
            "description": "Discover extraction pattern from data"
        },
        "create_extraction_config": {
            "handler": self._handle_create_extraction_config,
            "input_schema": {...},
            "description": "Create custom extraction configuration"
        }
    }
```

**MCP Server Base Pattern:**
```python
class InsightsRealmMCPServer(MCPServerBase):
    def __init__(self, orchestrator, di_container):
        super().__init__(service_name="insights_mcp", di_container=di_container)
        self.orchestrator = orchestrator
    
    async def initialize(self):
        # Get SOA APIs from orchestrator
        soa_apis = self.orchestrator._define_soa_api_handlers()
        
        # Auto-register each SOA API as MCP tool
        for api_name, api_def in soa_apis.items():
            tool_name = f"insights_{api_name}"
            self.register_tool(
                tool_name=tool_name,
                handler=api_def["handler"],
                input_schema=api_def["input_schema"],
                description=api_def["description"]
            )
```

### Layer 3: StructuredExtractionAgent

**Location:** `symphainy_platform/civic_systems/agentic/agents/structured_extraction_agent.py`

**Purpose:** Base agent for extraction reasoning (uses MCP tools, never direct service calls)

**Key Methods:**
```python
class StructuredExtractionAgent(AgentBase):
    async def analyze_extraction_strategy(
        self,
        extraction_config: ExtractionConfig,
        data_source: DataSource,
        context: ExecutionContext
    ) -> ExtractionStrategy:
        """Perform critical reasoning to determine extraction strategy."""
    
    async def extract_category(
        self,
        category: ExtractionCategory,
        data: Any,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Extract a single category using LLM (governed access via _call_llm())."""
    
    async def discover_pattern(
        self,
        data_source: DataSource,
        context: ExecutionContext
    ) -> ExtractionConfig:
        """Discover extraction pattern from data structure and embeddings."""
```

### Layer 4: ExtractionConfig Models (JSON Schema)

**Location:** `symphainy_platform/realms/insights/models/extraction_config.py`

**Format:** JSON Schema (primary format - no YAML support)

**Storage:** Supabase registry (not Artifact Plane - configs are foundational to agentic pattern)

**JSON Schema Definition:**
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "config_id": {
      "type": "string",
      "description": "Unique identifier for extraction config"
    },
    "name": {
      "type": "string",
      "description": "User-facing name"
    },
    "description": {
      "type": "string",
      "description": "User-facing description"
    },
    "domain": {
      "type": "string",
      "enum": ["variable_life_policy_rules", "aar", "pso", "custom"],
      "description": "Domain/pattern type"
    },
    "categories": {
      "type": "array",
      "items": {
        "$ref": "#/definitions/ExtractionCategory"
      },
      "description": "List of extraction categories"
    },
    "extraction_order": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Order in which categories should be extracted"
    },
    "dependencies": {
      "type": "object",
      "additionalProperties": {
        "type": "array",
        "items": {"type": "string"}
      },
      "description": "Category dependencies (category_name -> [depends_on_categories])"
    },
    "output_schema": {
      "type": "object",
      "description": "JSON Schema for output validation",
      "additionalProperties": true
    },
    "custom_properties": {
      "type": "object",
      "description": "Domain-specific customizations (flexible schema)",
      "additionalProperties": true
    },
    "version": {
      "type": "string",
      "default": "1.0"
    },
    "created_by": {
      "type": ["string", "null"]
    }
  },
  "required": ["config_id", "name", "domain", "categories"],
  "definitions": {
    "ExtractionCategory": {
      "type": "object",
      "properties": {
        "name": {"type": "string"},
        "description": {"type": "string"},
        "extraction_type": {
          "type": "string",
          "enum": ["llm", "pattern", "embedding", "hybrid"]
        },
        "prompt_template": {"type": "string"},
        "validation_rules": {
          "type": "array",
          "items": {"type": "object", "additionalProperties": true}
        },
        "required": {"type": "boolean", "default": false},
        "custom_properties": {
          "type": "object",
          "additionalProperties": true,
          "description": "Category-specific customizations"
        }
      },
      "required": ["name", "extraction_type"]
    }
  }
}
```

**Python Models (for runtime):**
```python
@dataclass
class ExtractionCategory:
    name: str
    description: str
    extraction_type: str  # "llm", "pattern", "embedding", "hybrid"
    prompt_template: str
    validation_rules: List[Dict[str, Any]]
    required: bool = False
    custom_properties: Optional[Dict[str, Any]] = None  # Flexible for customizations

@dataclass
class ExtractionConfig:
    config_id: str
    name: str
    description: str
    domain: str
    categories: List[ExtractionCategory]
    extraction_order: List[str]
    dependencies: Dict[str, List[str]]
    output_schema: Dict[str, Any]
    custom_properties: Optional[Dict[str, Any]] = None  # Flexible for domain-specific needs
    version: str = "1.0"
    created_by: Optional[str] = None
```

### Layer 5: ExtractionConfigRegistry

**Location:** `symphainy_platform/civic_systems/agentic/extraction_config_registry.py`

**Purpose:** Store and manage extraction configs in Supabase (similar to GuideRegistry)

**Key Methods:**
```python
class ExtractionConfigRegistry:
    async def register_config(
        self,
        config: ExtractionConfig,
        tenant_id: str
    ) -> str:
        """Register extraction config in Supabase."""
    
    async def get_config(
        self,
        config_id: str,
        tenant_id: str
    ) -> Optional[ExtractionConfig]:
        """Get extraction config by ID."""
    
    async def list_configs(
        self,
        tenant_id: str,
        domain: Optional[str] = None
    ) -> List[ExtractionConfig]:
        """List extraction configs (optionally filtered by domain)."""
```

### Layer 6: Interactive Config Builder Agent

**Location:** `symphainy_platform/realms/insights/agents/extraction_config_builder_agent.py`

**Pattern:** Lightweight, mirrors SOP generator pattern

**Key Methods:**
```python
class ExtractionConfigBuilderAgent:
    async def initiate_config_chat(
        self,
        initial_requirements: Optional[str],
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Start interactive config building session."""
    
    async def process_config_message(
        self,
        session_id: str,
        message: str,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Process user message and incrementally build config."""
    
    async def finalize_config(
        self,
        session_id: str,
        context: ExecutionContext
    ) -> Dict[str, Any]:
        """Summarize config and lock it in (or allow edits)."""
```

**Conversation Flow (Lightweight):**
1. Ask: "What domain are you extracting for?" (or infer from requirements)
2. Ask: "What categories should be extracted?" (suggest common ones)
3. For each category:
   - Ask: "What extraction type?" (LLM, pattern, embedding, hybrid)
   - Ask: "Any validation rules?"
4. Ask: "Any dependencies between categories?"
5. **Summarize** config before locking in
6. User confirms or edits
7. Save to ExtractionConfigRegistry

---

## Pre-Configured Patterns

### Pattern 1: Variable Life Policy Rules
**Config ID:** `variable_life_policy_rules`  
**Name:** "Variable Life Insurance Policy Rules"  
**Description:** "Extract investment rules, cash value calculations, riders, administration rules, and compliance rules from variable life insurance policies."

**Categories:**
- `investment_rules` (hybrid: embeddings + LLM)
- `cash_value_rules` (hybrid)
- `riders_features` (LLM)
- `administration_rules` (LLM)
- `compliance_rules` (LLM)

### Pattern 2: After Action Review
**Config ID:** `after_action_review`  
**Name:** "After Action Review"  
**Description:** "Extract lessons learned, risks, recommendations, and timeline from AAR documents."

**Categories:**
- `lessons_learned` (LLM)
- `risks` (LLM)
- `recommendations` (LLM)
- `timeline` (LLM)

### Pattern 3: Permit Semantic Object
**Config ID:** `permit_semantic_object`  
**Name:** "Permit Semantic Object"  
**Description:** "Extract permit metadata, obligations, and legal citations from permit documents."

**Categories:**
- `permit_metadata` (LLM)
- `obligations` (LLM)
- `legal_citations` (pattern + LLM)

---

## Relationship: Extraction Configs vs Guides

**Extraction Configs:**
- **Purpose:** Define HOW to extract structured data
- **Storage:** Supabase registry (ExtractionConfigRegistry)
- **Ownership:** Agentic System
- **Use Case:** "Extract these categories using these methods"

**Guides (Target Data Models):**
- **Purpose:** Define WHAT the output should look like (target schema)
- **Storage:** Supabase (GuideRegistry)
- **Ownership:** Platform SDK
- **Use Case:** "Match extracted data to this target schema"

**Integration:**
- Extraction Config extracts data → Guide validates/formats output
- Can generate Extraction Config from Guide (target model → extraction config)
- They work together but are separate concerns

---

## Implementation Phases

### Phase 1: Base Framework + SOA API (10-12 hours)
1. Create `StructuredExtractionService` with SOA API methods
2. Create `StructuredExtractionAgent` base class
3. Create `ExtractionConfig` data models (YAML + JSON Schema)
4. Create `ExtractionConfigRegistry` (Supabase storage)
5. Implement basic extraction orchestration
6. Add smoke tests

### Phase 2: MCP Server Integration for All 4 Realms (16-20 hours)
1. Create MCP Server base class/pattern (if not exists)
2. Create Content Realm MCP Server
   - Add `_define_soa_api_handlers()` to ContentOrchestrator
   - Create `content_mcp_server.py`
   - Implement auto-registration pattern
3. Create Insights Realm MCP Server
   - Add `_define_soa_api_handlers()` to InsightsOrchestrator (include extraction APIs)
   - Create `insights_mcp_server.py`
   - Implement auto-registration pattern
4. Create Journey Realm MCP Server
   - Add `_define_soa_api_handlers()` to JourneyOrchestrator
   - Create `journey_mcp_server.py`
   - Implement auto-registration pattern
5. Create Outcomes Realm MCP Server
   - Add `_define_soa_api_handlers()` to OutcomesOrchestrator
   - Create `outcomes_mcp_server.py`
   - Implement auto-registration pattern
6. Test MCP tool registration for all realms
7. Test agent tool consumption (via MCP Client Manager)
8. Update AgentConfigLoader to support JSON Schema validation (if exists)

### Phase 3: Pre-Configured Patterns (8-10 hours)
1. Create `variable_life_policy_rules` config
2. Port `after_action_review` config from old codebase
3. Port `permit_semantic_object` config from old codebase
4. Register all patterns in ExtractionConfigRegistry
5. Test all patterns
6. Document patterns

### Phase 4: Interactive Config Builder (12-16 hours)
1. Create `ExtractionConfigBuilderAgent`
2. Implement lightweight chat session management
3. Build conversation flow (mirrors SOP generator)
4. Implement config building logic
5. Add config summary before locking in
6. Add config editing capability
7. Test interactive flow

### Phase 5: Config File Upload (4-6 hours)
1. Implement JSON config file parsing (JSON Schema format only)
2. Add JSON Schema validation using jsonschema library
3. Add config import endpoint (SOA API)
4. Test file upload flow
5. Validate against ExtractionConfig JSON Schema

### Phase 6: Target Data Model Support (10-12 hours)
1. Integrate with existing target model parsing (Task 4.1)
2. Create target model analyzer agent
3. Implement config generation from target model
4. Map target schema → extraction categories
5. Generate validation rules from target constraints
6. Test target model → config flow

### Phase 7: Freeform Discovery (12-16 hours)
1. Implement data structure analysis (schema, patterns)
2. Implement semantic category discovery (via embeddings)
3. Create pattern proposal logic (agent reasons about structure)
4. Add user confirmation flow (propose → confirm → extract)
5. Add constrained interactive discovery (targeted questions)
6. Test discovery flow

### Phase 8: Config Management (6-8 hours)
1. Complete ExtractionConfigRegistry (CRUD operations)
2. Add config versioning
3. Add config sharing (cross-tenant if needed)
4. Add config library/discovery
5. Test config management

---

## MVP Recommendation (For Insurance Demo)

**Phases 1-3** (40-50 hours, 4-5 weeks):
- ✅ Base framework
- ✅ MCP tools integration (all 4 realms)
- ✅ Pre-configured Variable Life Policy Rules pattern

**This provides:**
- ✅ Policy Rules extraction (demo requirement)
- ✅ Extensible framework (future value)
- ✅ Agentic consumption (MCP tools for all realms)
- ✅ Foundation for interactive/freeform (can add later)
- ✅ Platform-wide MCP infrastructure (enables all realms)

**Phases 4-8** can be added post-demo for full vision.

---

## Key Design Decisions (Based on Clarifications)

### ✅ MCP Integration
- **Pattern:** Orchestrator defines `_define_soa_api_handlers()`
- **MCP Server:** Auto-registers SOA APIs as MCP tools
- **Agent Access:** Agents use MCP Client Manager (from Agentic System)
- **Tool Access:** Defined in agent config YAML (`allowed_mcp_servers`, `allowed_tools`)

### ✅ Config Storage
- **Location:** Supabase registry (ExtractionConfigRegistry)
- **Format:** JSON Schema (primary format - no YAML support)
- **Ownership:** Agentic System (not Artifact Plane)
- **Reason:** Configs are foundational to agentic pattern (like agent configs)
- **Flexibility:** `custom_properties` field allows domain-specific customizations without breaking schema

### ✅ Interactive Builder
- **Pattern:** Lightweight, mirrors SOP generator
- **Flow:** Ask key questions → Build incrementally → Summarize → Lock in
- **Validation:** Validate key inputs during conversation
- **Editing:** Allow edits before finalizing

### ✅ Target Data Model Integration
- **Relationship:** Extraction Configs (HOW) vs Guides (WHAT)
- **Integration:** Can generate extraction config from target model
- **Workflow:** Target model → Extraction Config → Extract → Guide validates/formats
- **Keep Separate:** Different concerns, but work together

### ✅ Freeform Discovery
- **Approach:** Analyze structure first → Validate with embeddings → Propose categories
- **Interaction:** Propose config → User confirms/saves or discards
- **Constraints:** Narrow parameters, targeted questions for feedback

### ✅ Pattern Naming
- **Format:** Specific, user-facing names with descriptions
- **Examples:**
  - `variable_life_policy_rules` (not "policy_rules" or "policy_migrator")
  - `after_action_review` (not "aar")
  - `permit_semantic_object` (not "pso")

---

## Files to Create/Modify

### New Files
- `symphainy_platform/realms/insights/enabling_services/structured_extraction_service.py`
- `symphainy_platform/civic_systems/agentic/agents/structured_extraction_agent.py`
- `symphainy_platform/realms/insights/models/extraction_config.py`
- `symphainy_platform/civic_systems/agentic/extraction_config_registry.py`
- `symphainy_platform/realms/insights/agents/extraction_config_builder_agent.py`
- `symphainy_platform/realms/insights/configs/variable_life_policy_rules_config.json`
- `symphainy_platform/realms/insights/configs/after_action_review_config.json`
- `symphainy_platform/realms/insights/configs/permit_semantic_object_config.json`
- `symphainy_platform/realms/content/mcp_server/content_mcp_server.py`
- `symphainy_platform/realms/insights/mcp_server/insights_mcp_server.py`
- `symphainy_platform/realms/journey/mcp_server/journey_mcp_server.py`
- `symphainy_platform/realms/outcomes/mcp_server/outcomes_mcp_server.py`

### Modified Files
- `symphainy_platform/realms/content/orchestrators/content_orchestrator.py`
  - Add `_define_soa_api_handlers()` method
- `symphainy_platform/realms/insights/orchestrators/insights_orchestrator.py`
  - Add `_define_soa_api_handlers()` method
  - Add intent handlers for extraction
- `symphainy_platform/realms/journey/orchestrators/journey_orchestrator.py`
  - Add `_define_soa_api_handlers()` method
- `symphainy_platform/realms/outcomes/orchestrators/outcomes_orchestrator.py`
  - Add `_define_soa_api_handlers()` method
- `symphainy_platform/realms/insights/enabling_services/__init__.py`
  - Export StructuredExtractionService
- `symphainy_platform/civic_systems/agentic/agent_config_loader.py` (if exists)
  - Update to support JSON Schema validation (replace YAML-only support)

---

## Follow-Up Questions

### Q1: MCP Server Base Class
**Question:** Does MCP Server base class exist in current codebase?
- **Action:** Check for `MCPServerBase` or similar base class
- **If not:** Need to port from old codebase (`bases.mcp_server.mcp_server_base`)
- **Pattern:** All 4 realm MCP servers will extend base class

### Q2: Agent Config Loader Update
**Question:** Does AgentConfigLoader exist in current codebase?
- **Action:** Check if ported from old codebase
- **Update Required:** If exists, update to support JSON Schema validation (currently YAML)
- **Pattern:** ExtractionConfigRegistry should follow same storage pattern (Supabase registry)
- **Format:** Both agent configs and extraction configs should use JSON Schema

### Q3: Target Model Integration
**Question:** Should extraction config generation from target models integrate with Task 4.1 (Target Data Model Parsing)?
- **Recommendation:** Yes - use parsed target models to generate extraction configs
- **Workflow:** Parse target model → Generate extraction config → Extract → Use guide to validate

**Action:** Coordinate with Task 4.1 implementation

### Q4: Config Format Flexibility
**Question:** How to support customizations without creating anti-patterns?
- **Solution:** Use JSON Schema with `custom_properties` field (flexible object)
- **Pattern:** Core schema is strict, `custom_properties` allows domain-specific extensions
- **Examples:**
  - Variable Life Policy Rules: `custom_properties.policy_types`, `custom_properties.state_regulations`
  - AAR: `custom_properties.event_types`, `custom_properties.recommendation_categories`
  - PSO: `custom_properties.permit_types`, `custom_properties.compliance_frameworks`
- **Validation:** Core schema validates required fields, `custom_properties` is open-ended

---

## Next Steps

1. **Answer Follow-Up Questions Q1-Q4** (if any)
2. **Review/Approve Architecture**
3. **Begin Phase 1 Implementation** (Base Framework)

---

**Last Updated:** January 2026  
**Status:** 📋 Ready for Implementation (Pending Q1-Q4 answers if needed)
