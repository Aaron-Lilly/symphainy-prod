# Journey & Solution Realms Implementation Plan

**Date:** January 2026  
**Status:** 📋 **COMPREHENSIVE IMPLEMENTATION PLAN**  
**Goal:** Rebuild Journey and Solution realms following platform-forward principles, bringing forward best working parts from `symphainy_source`, and supporting MVP showcase capabilities

---

## 🎯 Executive Summary

This plan rebuilds the **Journey Realm** (Operations Pillar) and **Solution Realm** (Business Outcomes Pillar) following the platform-forward architecture from `rebuild_implementation_plan_v2.md`. It brings forward the best working functional parts from `symphainy_source/business_enablement_old/` while ensuring all agents are built using the new Agent Foundation pattern.

**Key Principles:**
- ✅ **Platform Engineering** (not demo engineering)
- ✅ **Realm Structure** (manager, orchestrator, services, agents)
- ✅ **Agent Foundation Pattern** (AgentBase, GroundedReasoningAgentBase)
- ✅ **No Side Effects** (agents return artifacts, services execute)
- ✅ **Deterministic Services** (stateless, input → output)
- ✅ **Native Rebuild** (not legacy migration - use legacy as reference only)

**Guiding Principle:**
> **Runtime executes, agents reason, realms define domain intent, state records facts, and experience delivers outcomes.**

---

## 📊 Current State Analysis

### Journey Realm (Operations Pillar)

**Current State:**
- ❌ Empty directory (`symphainy_platform/realms/journey/`)
- ✅ Legacy implementation exists in `symphainy_source/business_enablement_old/`
- ✅ Legacy agents: `OperationsLiaisonAgent`, `OperationsSpecialistAgent`
- ✅ Legacy services: `SOPBuilderService`, `WorkflowConversionService`, `CoexistenceAnalysisService`

**MVP Requirements (from `mvp_showcase_description.md`):**
- Upload workflow/SOP files → parse and create visuals
- Generate SOP from workflow (or vice versa)
- Generate SOP from scratch via interactive chat
- Analyze workflows/SOPs for coexistence (human+AI) optimization
- Create coexistence blueprint for optimized process
- Turn blueprint into platform journey

### Solution Realm (Business Outcomes Pillar)

**Current State:**
- ❌ Empty directory (`symphainy_platform/realms/solution/`)
- ✅ Legacy implementation exists in `symphainy_source/business_enablement_old/`
- ✅ Legacy agents: `BusinessOutcomesLiaisonAgent`, `BusinessOutcomesSpecialistAgent`
- ✅ Legacy services: `RoadmapGenerationService`, `POCGenerationService`, `ReportGeneratorService`

**MVP Requirements (from `mvp_showcase_description.md`):**
- Create summary visual of outputs from other realms
- Generate roadmap from realm outputs
- Generate POC proposal from realm outputs
- Turn roadmap and POC proposal into platform solutions

### Legacy Code Reference (Not Migration)

**From `symphainy_source/business_enablement_old/agents/`:**
1. **Guide Agent** - `guide_cross_domain_agent.py` (global concierge)
2. **Liaison Agents:**
   - `operations_liaison_agent.py` (Journey realm)
   - `business_outcomes_liaison_agent.py` (Solution realm)
3. **Specialist Agents:**
   - `sop_generation_specialist.py` (SOP builder wizard)
   - `workflow_generation_specialist.py` (workflow generator)
   - `coexistence_blueprint_specialist.py` (coexistence analyzer)
   - `roadmap_proposal_specialist.py` (roadmap + POC agent)

**From `symphainy_source/business_enablement_old/enabling_services/`:**
- `SOPBuilderService` → Reference for Journey Realm Service
- `WorkflowConversionService` → Reference for Journey Realm Service
- `CoexistenceAnalysisService` → Reference for Journey Realm Service
- `RoadmapGenerationService` → Reference for Solution Realm Service
- `POCGenerationService` → Reference for Solution Realm Service
- `ReportGeneratorService` → Reference for Solution Realm Service

**⚠️ Critical:** We are **rebuilding natively**, using legacy code only as *reference* for working logic patterns.

---

## 🏗️ Architecture Pattern

### Realm Structure (Platform-Native)

Each realm follows this structure:

```
realm/
├── __init__.py
├── manager.py              # Lifecycle & registration
├── foundation_service.py   # Realm foundation (initializes services/orchestrators)
├── orchestrators/
│   └── realm_orchestrator.py  # Saga composition (thin)
├── services/               # Deterministic domain logic
│   ├── service_1.py
│   └── service_2.py
└── agents/                 # Reasoning (attached, not owned)
    ├── liaison_agent.py
    └── specialist_agent.py
```

### Agent Foundation Pattern

**Base Classes:**
- `AgentBase` - Context-in, reasoning-out, no side effects
- `GroundedReasoningAgentBase` - Fact gathering via Runtime/State Surface

**Agent Rules:**
- ✅ Return reasoned artifacts
- ✅ Use Runtime/State Surface for fact gathering
- ✅ NO database writes
- ✅ NO event emission
- ✅ NO workflow orchestration

**Agent Registration:**
- **Agents registered during realm initialization** (not platform startup)
- Realms declare which agents exist, what tools they require, what reasoning mode they use
- Agent Foundation Service exists as infrastructure
- Runtime manages agent execution

**Agent Types:**
1. **Guide Agent** - Global concierge (platform-wide, registered separately)
2. **Liaison Agents** - Realm-specific conversational guidance
3. **Specialist Agents** - AI-powered reasoning for specific capabilities

### State Surface Usage

**Canonical Rule:**
- **State Surface** stores:
  - Execution state
  - Facts
  - Lineage
  - References (URIs, IDs, metadata)
- **Datastores** store:
  - Documents (SOPs, blueprints, roadmaps, POCs)
  - Graphs (workflows)
  - Files (binary data)
  - Domain models

**Example Artifact Storage:**

| Artifact              | Storage      | State Surface Contains                    |
| --------------------- | ------------ | ----------------------------------------- |
| SOP document          | GCS          | URI + version + confidence + metadata    |
| Workflow graph        | ArangoDB     | workflow_id + status + lineage            |
| Coexistence blueprint | GCS          | blueprint_id + readiness + facts          |
| Roadmap / POC         | GCS / Arango | summary facts + references + lineage      |

---

## 🚫 Critical Anti-Patterns to Avoid

### ❌ Anti-Pattern 1: Realm-Owned Execution

**Wrong:**
- Realms creating sessions
- Realms managing retries
- Realms persisting state directly

**Correct:**
- Realms *declare intent*
- Runtime executes
- State Surface records facts

### ❌ Anti-Pattern 2: Agents Doing Orchestration

**Wrong:**
- Agents calling other agents
- Agents controlling workflows
- Agents persisting outputs directly

**Correct:**
- Agents reason → return artifacts
- Runtime executes → orchestrator composes
- State records → realm consumes results

### ❌ Anti-Pattern 3: Embedding Business Logic in Services

**Wrong:**
- Services deciding "what should happen next"
- Services branching on business semantics

**Correct:**
- Services are **pure capability providers**
- Orchestrators make decisions
- Agents provide reasoning

### ❌ Anti-Pattern 4: Frontend-Driven Control Flow

**Wrong:**
- UI determines execution order
- UI "skips" platform phases

**Correct:**
- UI submits intents
- Runtime enforces flow
- Experience plane delivers outcomes

### ❌ Anti-Pattern 5: Big-Bang Refactors

**Wrong:**
- "Let's port everything first"
- "We'll clean it up later"

**Correct:**
- Rebuild realm-by-realm
- Runtime-first alignment
- Native patterns from day one

---

## 📋 Implementation Phases

### Phase 1: Foundation & Structure (2-3 days)

**Goal:** Create realm structure and foundation services

#### 1.1 Journey Realm Foundation

**Create:**
- `symphainy_platform/realms/journey/__init__.py`
- `symphainy_platform/realms/journey/manager.py`
- `symphainy_platform/realms/journey/foundation_service.py`
- `symphainy_platform/realms/journey/orchestrators/__init__.py`
- `symphainy_platform/realms/journey/services/__init__.py`
- `symphainy_platform/realms/journey/agents/__init__.py`

**Manager Responsibilities:**
- Register Journey Realm capabilities with Curator
- Bind realm to Runtime lifecycle
- Coordinate realm initialization
- **Register agents with Agent Foundation Service during initialization**

**Foundation Service Responsibilities:**
- Initialize Journey services
- Initialize Journey orchestrator
- Initialize Journey agents
- **Register agents with Agent Foundation Service**
- Wire everything together

#### 1.2 Solution Realm Foundation

**Create:**
- `symphainy_platform/realms/solution/__init__.py`
- `symphainy_platform/realms/solution/manager.py`
- `symphainy_platform/realms/solution/foundation_service.py`
- `symphainy_platform/realms/solution/orchestrators/__init__.py`
- `symphainy_platform/realms/solution/services/__init__.py`
- `symphainy_platform/realms/solution/agents/__init__.py`

**Manager Responsibilities:**
- Register Solution Realm capabilities with Curator
- Bind realm to Runtime lifecycle
- Coordinate realm initialization
- **Register agents with Agent Foundation Service during initialization**

**Foundation Service Responsibilities:**
- Initialize Solution services
- Initialize Solution orchestrator
- Initialize Solution agents
- **Register agents with Agent Foundation Service**
- Wire everything together

---

### Phase 2: Journey Realm Services (3-4 days)

**Goal:** Rebuild deterministic services natively (using legacy as reference)

#### 2.1 SOP Builder Service

**Reference:** `symphainy_source/business_enablement_old/enabling_services/sop_builder_service/`

**Location:** `symphainy_platform/realms/journey/services/sop_builder_service/`

**Responsibilities:**
- Build SOPs from structured data
- Validate SOP structure
- Wizard pattern for interactive SOP creation

**Key Methods:**
```python
async def start_wizard_session(
    session_id: str,
    tenant_id: str,
    initial_description: Optional[str] = None
) -> Dict[str, Any]

async def process_wizard_step(
    session_id: str,
    tenant_id: str,
    step_data: Dict[str, Any]
) -> Dict[str, Any]

async def complete_wizard(
    session_id: str,
    tenant_id: str
) -> Dict[str, Any]

async def create_sop(
    description: str,
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]

async def validate_sop(
    sop_data: Dict[str, Any]
) -> Dict[str, Any]
```

**Pattern:**
- Deterministic
- Stateless
- Input → Output
- No orchestration
- No reasoning
- **Artifacts stored in GCS, references in State Surface**

#### 2.2 Workflow Conversion Service

**Reference:** `symphainy_source/business_enablement_old/enabling_services/workflow_conversion_service/`

**Location:** `symphainy_platform/realms/journey/services/workflow_conversion_service/`

**Responsibilities:**
- Convert SOP to workflow (bidirectional)
- Convert workflow to SOP (bidirectional)
- Validate conversions

**Key Methods:**
```python
async def convert_sop_to_workflow(
    sop_file_reference: str,
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]

async def convert_workflow_to_sop(
    workflow_file_reference: str,
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]

async def validate_conversion(
    conversion_id: str
) -> Dict[str, Any]
```

**Pattern:**
- Deterministic
- Stateless
- Input → Output
- **Workflows stored in ArangoDB, references in State Surface**

#### 2.3 Coexistence Analysis Service

**Reference:** `symphainy_source/business_enablement_old/enabling_services/coexistence_analysis_service/`

**Location:** `symphainy_platform/realms/journey/services/coexistence_analysis_service/`

**Responsibilities:**
- Analyze workflows/SOPs for human-AI coexistence opportunities
- Generate coexistence blueprints
- Optimize coexistence patterns

**Key Methods:**
```python
async def analyze_coexistence(
    current_state: Dict[str, Any],  # Workflow/SOP content
    target_state: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]

async def generate_blueprint(
    analysis_result: Dict[str, Any],
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]

async def optimize_coexistence(
    blueprint_id: str,
    optimization_criteria: Dict[str, Any]
) -> Dict[str, Any]
```

**Pattern:**
- Deterministic analysis algorithms
- Stateless
- Input → Output
- **Blueprints stored in GCS, references in State Surface**

---

### Phase 3: Solution Realm Services (2-3 days)

**Goal:** Rebuild deterministic services natively (using legacy as reference)

#### 3.1 Roadmap Generation Service

**Reference:** `symphainy_source/business_enablement_old/enabling_services/roadmap_generation_service/`

**Location:** `symphainy_platform/realms/solution/services/roadmap_generation_service/`

**Responsibilities:**
- Generate strategic roadmaps from realm outputs
- Create roadmap visualizations
- Track roadmap progress

**Key Methods:**
```python
async def generate_roadmap(
    realm_outputs: Dict[str, Any],  # Content, Insights, Journey outputs
    business_context: Dict[str, Any],
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]

async def visualize_roadmap(
    roadmap_id: str
) -> Dict[str, Any]

async def track_progress(
    roadmap_id: str
) -> Dict[str, Any]
```

**Pattern:**
- Deterministic
- Stateless
- Input → Output
- **Roadmaps stored in GCS/ArangoDB, references in State Surface**

#### 3.2 POC Generation Service

**Reference:** `symphainy_source/business_enablement_old/enabling_services/poc_generation_service/`

**Location:** `symphainy_platform/realms/solution/services/poc_generation_service/`

**Responsibilities:**
- Generate POC proposals from realm outputs
- Calculate POC financials
- Generate POC metrics

**Key Methods:**
```python
async def generate_poc_proposal(
    realm_outputs: Dict[str, Any],
    business_context: Dict[str, Any],
    poc_type: str = "hybrid",
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]

async def calculate_financials(
    poc_proposal: Dict[str, Any]
) -> Dict[str, Any]

async def generate_metrics(
    poc_proposal: Dict[str, Any]
) -> Dict[str, Any]
```

**Pattern:**
- Deterministic
- Stateless
- Input → Output
- **POC proposals stored in GCS, references in State Surface**

#### 3.3 Report Generator Service

**Reference:** `symphainy_source/business_enablement_old/enabling_services/report_generator_service/`

**Location:** `symphainy_platform/realms/solution/services/report_generator_service/`

**Responsibilities:**
- Generate summary visuals from realm outputs
- Compose reports from multiple sources
- Format reports for presentation

**Key Methods:**
```python
async def generate_summary_visual(
    realm_outputs: Dict[str, Any],
    visualization_type: str = "summary"
) -> Dict[str, Any]

async def compose_report(
    sources: List[Dict[str, Any]],
    report_template: str
) -> Dict[str, Any]
```

**Pattern:**
- Deterministic
- Stateless
- Input → Output
- **Reports stored in GCS, references in State Surface**

---

### Phase 4: Journey Realm Orchestrator (2-3 days)

**Goal:** Create orchestrator that composes saga steps and calls services/agents

**Location:** `symphainy_platform/realms/journey/orchestrators/journey_orchestrator.py`

**Responsibilities:**
- Define saga steps for Journey operations
- Route to appropriate services
- Attach agents for reasoning
- Never store state directly
- Use State Surface for state and references

**Key Capabilities:**
```python
async def create_sop_from_workflow(
    workflow_file_reference: str,
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Saga: Convert workflow → SOP
    1. Get workflow from State Surface (reference) → retrieve from ArangoDB
    2. Call WorkflowConversionService.convert_workflow_to_sop()
    3. Store SOP artifact in GCS
    4. Store SOP reference + metadata in State Surface
    5. Return SOP reference
    """

async def create_workflow_from_sop(
    sop_file_reference: str,
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Saga: Convert SOP → Workflow
    1. Get SOP from State Surface (reference) → retrieve from GCS
    2. Call WorkflowConversionService.convert_sop_to_workflow()
    3. Store workflow artifact in ArangoDB
    4. Store workflow reference + metadata in State Surface
    5. Return workflow reference
    """

async def start_sop_wizard(
    session_id: str,
    tenant_id: str,
    initial_description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Saga: Start SOP wizard session
    1. Call SOPBuilderService.start_wizard_session()
    2. Store wizard session state in State Surface
    3. Return session token
    """

async def process_sop_wizard_step(
    session_id: str,
    tenant_id: str,
    step_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Saga: Process wizard step
    1. Get wizard session from State Surface
    2. Attach SOPBuilderWizardAgent for reasoning (if needed)
    3. Call SOPBuilderService.process_wizard_step()
    4. Update session state in State Surface
    5. Return step result
    """

async def complete_sop_wizard(
    session_id: str,
    tenant_id: str
) -> Dict[str, Any]:
    """
    Saga: Complete wizard and generate SOP
    1. Get wizard session from State Surface
    2. Attach SOPBuilderWizardAgent for final reasoning
    3. Call SOPBuilderService.complete_wizard()
    4. Store SOP artifact in GCS
    5. Store SOP reference + metadata in State Surface
    6. Return SOP reference
    """

async def analyze_coexistence(
    workflow_reference: Optional[str] = None,
    sop_reference: Optional[str] = None,
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Saga: Analyze coexistence opportunities
    1. Get workflow/SOP from State Surface (references) → retrieve from storage
    2. Attach CoexistenceAnalyzerAgent for reasoning
    3. Call CoexistenceAnalysisService.analyze_coexistence() with agent's structure
    4. Store analysis in State Surface (facts + references)
    5. Return analysis reference
    """

async def generate_coexistence_blueprint(
    analysis_reference: str,
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Saga: Generate coexistence blueprint
    1. Get analysis from State Surface
    2. Attach CoexistenceAnalyzerAgent for reasoning
    3. Call CoexistenceAnalysisService.generate_blueprint() with agent's structure
    4. Store blueprint artifact in GCS
    5. Store blueprint reference + metadata in State Surface
    6. Return blueprint reference
    """

async def create_platform_journey(
    blueprint_reference: str,
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Saga: Turn blueprint into platform journey
    1. Get blueprint from State Surface (reference) → retrieve from GCS
    2. Attach JourneyGeneratorAgent for reasoning (if needed)
    3. Generate journey definition
    4. Store journey in ArangoDB
    5. Store journey reference + metadata in State Surface
    6. Return journey reference
    """
```

**Pattern:**
- Thin orchestrator (no business logic)
- Composes saga steps
- Calls services (deterministic)
- Attaches agents (reasoning)
- Uses State Surface for state and references (never stores artifacts directly)

---

### Phase 5: Solution Realm Orchestrator (2-3 days)

**Goal:** Create orchestrator that composes saga steps and calls services/agents

**Location:** `symphainy_platform/realms/solution/orchestrators/solution_orchestrator.py`

**Responsibilities:**
- Define saga steps for Solution operations
- Route to appropriate services
- Attach agents for reasoning
- Never store state directly
- Use State Surface for state and references

**Key Capabilities:**
```python
async def generate_summary_visual(
    realm_outputs: Dict[str, Any],
    visualization_type: str = "summary"
) -> Dict[str, Any]:
    """
    Saga: Generate summary visual from realm outputs
    1. Gather outputs from Content, Insights, Journey realms (via State Surface references)
    2. Retrieve actual artifacts from storage (GCS/ArangoDB)
    3. Call ReportGeneratorService.generate_summary_visual()
    4. Store visual artifact in GCS
    5. Store visual reference + metadata in State Surface
    6. Return visual reference
    """

async def generate_roadmap(
    realm_outputs: Dict[str, Any],
    business_context: Dict[str, Any],
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Saga: Generate strategic roadmap
    1. Gather realm outputs from State Surface (references)
    2. Retrieve actual artifacts from storage
    3. Attach RoadmapAgent for reasoning (analyze outputs, determine roadmap structure)
    4. Call RoadmapGenerationService.generate_roadmap() with agent's structure
    5. Store roadmap artifact in GCS/ArangoDB
    6. Store roadmap reference + metadata in State Surface
    7. Return roadmap reference
    """

async def generate_poc_proposal(
    realm_outputs: Dict[str, Any],
    business_context: Dict[str, Any],
    poc_type: str = "hybrid",
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Saga: Generate POC proposal
    1. Gather realm outputs from State Surface (references)
    2. Retrieve actual artifacts from storage
    3. Attach POCProposalAgent for reasoning (analyze outputs, determine POC structure)
    4. Call POCGenerationService.generate_poc_proposal() with agent's structure
    5. Store POC proposal artifact in GCS
    6. Store POC proposal reference + metadata in State Surface
    7. Return POC proposal reference
    """

async def create_platform_solution(
    roadmap_reference: Optional[str] = None,
    poc_reference: Optional[str] = None,
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Saga: Turn roadmap/POC into platform solution
    1. Get roadmap/POC from State Surface (references) → retrieve from storage
    2. Attach SolutionGeneratorAgent for reasoning (if needed)
    3. Generate solution definition
    4. Store solution in ArangoDB
    5. Store solution reference + metadata in State Surface
    6. Return solution reference
    """
```

**Pattern:**
- Thin orchestrator (no business logic)
- Composes saga steps
- Calls services (deterministic)
- Attaches agents (reasoning)
- Uses State Surface for state and references

---

### Phase 6: Agent Migration & Rebuild (4-5 days)

**Goal:** Rebuild agents natively using Agent Foundation pattern (using legacy as reference)

#### 6.1 Guide Agent (Platform-Wide)

**Reference:** `symphainy_source/business_enablement_old/agents/guide_cross_domain_agent.py`

**Location:** `symphainy_platform/agentic/agents/guide_agent.py` (platform-wide, not realm-specific)

**Base Class:** `GroundedReasoningAgentBase`

**Capabilities:**
- Global concierge across all realms
- Intent analysis and routing
- User profiling
- Cross-realm navigation guidance

**Key Methods:**
```python
async def reason(
    context: Dict[str, Any],
    **kwargs
) -> Dict[str, Any]:
    """
    Reason about user intent and provide guidance.
    
    Context includes:
    - user_message: str
    - session_id: str
    - tenant_id: str
    - current_realm: Optional[str]
    
    Returns:
    {
        "reasoning": "...",
        "artifacts": {
            "intent": "...",
            "recommended_realm": "...",
            "guidance": "...",
            "next_steps": [...]
        },
        "confidence": 0.0-1.0,
        "metadata": {...}
    }
    """
```

**Registration:**
- Registered with Agent Foundation Service at platform startup (platform-wide agent)
- Available platform-wide (not realm-specific)

#### 6.2 Journey Liaison Agent

**Reference:** `symphainy_source/business_enablement_old/delivery_manager/mvp_pillar_orchestrators/operations_orchestrator/agents/operations_liaison_agent.py`

**Location:** `symphainy_platform/realms/journey/agents/journey_liaison_agent.py`

**Base Class:** `GroundedReasoningAgentBase`

**Capabilities:**
- Conversational guidance for Journey realm
- SOP creation guidance
- Workflow conversion guidance
- Coexistence analysis guidance

**Key Methods:**
```python
async def reason(
    context: Dict[str, Any],
    **kwargs
) -> Dict[str, Any]:
    """
    Reason about user's Journey realm questions and provide guidance.
    
    Context includes:
    - user_message: str
    - session_id: str
    - tenant_id: str
    - current_artifacts: Dict (workflows, SOPs, blueprints - references from State Surface)
    
    Returns:
    {
        "reasoning": "...",
        "artifacts": {
            "guidance": "...",
            "recommended_action": "...",
            "capabilities": [...]
        },
        "confidence": 0.0-1.0
    }
    """
```

**Integration:**
- Attached to Journey Orchestrator
- Registered with Agent Foundation Service during Journey Realm initialization
- Can trigger orchestrator methods (via Runtime intents)

#### 6.3 Solution Liaison Agent

**Reference:** `symphainy_source/business_enablement_old/delivery_manager/mvp_pillar_orchestrators/business_outcomes_orchestrator/agents/business_outcomes_liaison_agent.py`

**Location:** `symphainy_platform/realms/solution/agents/solution_liaison_agent.py`

**Base Class:** `GroundedReasoningAgentBase`

**Capabilities:**
- Conversational guidance for Solution realm
- Roadmap generation guidance
- POC proposal guidance
- Strategic planning guidance

**Key Methods:**
```python
async def reason(
    context: Dict[str, Any],
    **kwargs
) -> Dict[str, Any]:
    """
    Reason about user's Solution realm questions and provide guidance.
    
    Context includes:
    - user_message: str
    - session_id: str
    - tenant_id: str
    - realm_outputs: Dict (from Content, Insights, Journey - references from State Surface)
    
    Returns:
    {
        "reasoning": "...",
        "artifacts": {
            "guidance": "...",
            "recommended_action": "...",
            "capabilities": [...]
        },
        "confidence": 0.0-1.0
    }
    """
```

**Integration:**
- Attached to Solution Orchestrator
- Registered with Agent Foundation Service during Solution Realm initialization

#### 6.4 SOP Builder Wizard Agent

**Reference:** `symphainy_source/business_enablement_old/agents/sop_generation_specialist.py`

**Location:** `symphainy_platform/realms/journey/agents/sop_builder_wizard_agent.py`

**Base Class:** `GroundedReasoningAgentBase`

**Capabilities:**
- AI-powered SOP generation from natural language
- Interactive wizard guidance
- Best practice identification
- SOP structure reasoning

**Key Methods:**
```python
async def reason(
    context: Dict[str, Any],
    **kwargs
) -> Dict[str, Any]:
    """
    Reason about SOP creation requirements and generate SOP structure.
    
    Context includes:
    - process_description: str (natural language)
    - wizard_session: Optional[Dict] (if in wizard mode)
    - user_context: Dict
    
    Returns:
    {
        "reasoning": "...",
        "artifacts": {
            "sop_structure": {...},
            "steps": [...],
            "guidelines": [...],
            "recommendations": [...]
        },
        "confidence": 0.0-1.0
    }
    """
```

**Integration:**
- Attached to Journey Orchestrator
- Registered with Agent Foundation Service during Journey Realm initialization
- Called by orchestrator during SOP wizard flow
- Provides reasoning, orchestrator calls service

#### 6.5 Workflow Generator Agent

**Reference:** `symphainy_source/business_enablement_old/agents/workflow_generation_specialist.py`

**Location:** `symphainy_platform/realms/journey/agents/workflow_generator_agent.py`

**Base Class:** `GroundedReasoningAgentBase`

**Capabilities:**
- AI-powered workflow generation from SOP
- Workflow optimization reasoning
- Process flow analysis

**Key Methods:**
```python
async def reason(
    context: Dict[str, Any],
    **kwargs
) -> Dict[str, Any]:
    """
    Reason about workflow generation and optimization.
    
    Context includes:
    - sop_content: Dict (SOP structure - retrieved from GCS via State Surface reference)
    - optimization_goals: Optional[Dict]
    
    Returns:
    {
        "reasoning": "...",
        "artifacts": {
            "workflow_structure": {...},
            "optimization_opportunities": [...],
            "recommendations": [...]
        },
        "confidence": 0.0-1.0
    }
    """
```

**Integration:**
- Attached to Journey Orchestrator
- Registered with Agent Foundation Service during Journey Realm initialization

#### 6.6 Coexistence Analyzer Agent

**Reference:** `symphainy_source/business_enablement_old/agents/coexistence_blueprint_specialist.py`

**Location:** `symphainy_platform/realms/journey/agents/coexistence_analyzer_agent.py`

**Base Class:** `GroundedReasoningAgentBase`

**Capabilities:**
- AI-powered coexistence analysis
- Human-AI collaboration pattern identification
- Blueprint generation reasoning

**Key Methods:**
```python
async def reason(
    context: Dict[str, Any],
    **kwargs
) -> Dict[str, Any]:
    """
    Reason about coexistence opportunities and generate blueprint structure.
    
    Context includes:
    - workflow_content: Dict (retrieved from ArangoDB via State Surface reference)
    - sop_content: Dict (retrieved from GCS via State Surface reference)
    - current_state: Dict
    - target_state: Optional[Dict]
    
    Returns:
    {
        "reasoning": "...",
        "artifacts": {
            "coexistence_opportunities": [...],
            "blueprint_structure": {...},
            "optimization_recommendations": [...],
            "migration_strategy": {...}
        },
        "confidence": 0.0-1.0
    }
    """
```

**Integration:**
- Attached to Journey Orchestrator
- Registered with Agent Foundation Service during Journey Realm initialization

#### 6.7 Roadmap Agent

**Reference:** `symphainy_source/business_enablement_old/agents/roadmap_proposal_specialist.py`

**Location:** `symphainy_platform/realms/solution/agents/roadmap_agent.py`

**Base Class:** `GroundedReasoningAgentBase`

**Capabilities:**
- AI-powered roadmap generation from realm outputs
- Strategic planning reasoning
- Phase and milestone identification

**Key Methods:**
```python
async def reason(
    context: Dict[str, Any],
    **kwargs
) -> Dict[str, Any]:
    """
    Reason about roadmap structure and generate roadmap specification.
    
    Context includes:
    - realm_outputs: Dict (Content, Insights, Journey outputs - retrieved from storage via State Surface references)
    - business_context: Dict (objectives, constraints, timeline)
    
    Returns:
    {
        "reasoning": "...",
        "artifacts": {
            "roadmap_structure": {
                "phases": [...],
                "milestones": [...],
                "dependencies": [...],
                "timeline": {...}
            },
            "strategic_recommendations": [...]
        },
        "confidence": 0.0-1.0
    }
    """
```

**Integration:**
- Attached to Solution Orchestrator
- Registered with Agent Foundation Service during Solution Realm initialization

#### 6.8 POC Proposal Agent

**Reference:** `symphainy_source/business_enablement_old/agents/roadmap_proposal_specialist.py` (shared with roadmap)

**Location:** `symphainy_platform/realms/solution/agents/poc_proposal_agent.py`

**Base Class:** `GroundedReasoningAgentBase`

**Capabilities:**
- AI-powered POC proposal generation from realm outputs
- POC structure reasoning
- Value proposition identification

**Key Methods:**
```python
async def reason(
    context: Dict[str, Any],
    **kwargs
) -> Dict[str, Any]:
    """
    Reason about POC structure and generate POC specification.
    
    Context includes:
    - realm_outputs: Dict (Content, Insights, Journey outputs - retrieved from storage via State Surface references)
    - business_context: Dict (objectives, budget, timeline)
    - poc_type: str (hybrid, data_focused, analytics_focused, process_focused)
    
    Returns:
    {
        "reasoning": "...",
        "artifacts": {
            "poc_structure": {
                "scope": {...},
                "objectives": [...],
                "success_criteria": [...],
                "ai_value_propositions": [...],
                "recommended_focus": str
            },
            "value_maximization_strategy": "...",
            "recommendations": [...]
        },
        "confidence": 0.0-1.0
    }
    """
```

**Integration:**
- Attached to Solution Orchestrator
- Registered with Agent Foundation Service during Solution Realm initialization

**Rebuild Pattern:**
1. Extract reasoning logic from legacy agent (use as reference)
2. Rebuild natively extending `GroundedReasoningAgentBase`
3. Implement `reason()` method returning artifacts
4. Use `gather_facts()` for fact gathering from State Surface
5. Remove all side effects (DB writes, event emission)
6. Register with Agent Foundation Service during realm initialization

---

### Phase 7: Runtime Intent Integration (1-2 days)

**Goal:** Wire orchestrators to Runtime intents

#### 7.1 Journey Realm Intents

**Intents to Register:**
- `journey.create_sop_from_workflow`
- `journey.create_workflow_from_sop`
- `journey.start_sop_wizard`
- `journey.process_sop_wizard_step`
- `journey.complete_sop_wizard`
- `journey.analyze_coexistence`
- `journey.generate_blueprint`
- `journey.create_platform_journey`

**Registration:**
- Journey Manager registers capabilities with Curator
- Curator maps intents → capabilities
- Runtime routes intents → Journey Orchestrator

#### 7.2 Solution Realm Intents

**Intents to Register:**
- `solution.generate_summary_visual`
- `solution.generate_roadmap`
- `solution.generate_poc_proposal`
- `solution.create_platform_solution`

**Registration:**
- Solution Manager registers capabilities with Curator
- Curator maps intents → capabilities
- Runtime routes intents → Solution Orchestrator

---

### Phase 8: Experience Plane Integration (1-2 days)

**Goal:** Document intent schemas and response patterns (frontend changes out of scope)

#### 8.1 Intent Schema Documentation

**Location:** `symphainy_platform/experience/docs/journey_intent_schemas.md`

**Document:**
- Intent names and parameters
- Request/response patterns
- Sync vs async behavior
- State query patterns

**Example:**
```markdown
## Journey Realm Intents

### journey.create_sop_from_workflow

**Request:**
```json
{
  "intent": "journey.create_sop_from_workflow",
  "workflow_reference": "workflow:tenant:session:workflow_id",
  "options": {
    "format": "standard",
    "include_metadata": true
  }
}
```

**Response (Async):**
```json
{
  "execution_id": "exec:tenant:session:exec_id",
  "status": "pending",
  "sop_reference": "sop:tenant:session:sop_id"
}
```

**State Query:**
- Query State Surface for execution status
- Query State Surface for SOP reference
- Retrieve SOP artifact from GCS using reference
```

#### 8.2 Response Pattern Documentation

**Location:** `symphainy_platform/experience/docs/solution_response_patterns.md`

**Document:**
- Response formats
- Error handling
- Progress tracking
- Result retrieval

#### 8.3 Future REST Endpoints (Stubbed)

**Location:** `symphainy_platform/experience/journey_handlers.py` (stubbed)

**Note:** Full implementation deferred until Experience Plane phase. For now, document contracts.

**Endpoints to Document:**
```python
POST /api/v1/journey/sop/from-workflow
POST /api/v1/journey/workflow/from-sop
POST /api/v1/journey/sop/wizard/start
POST /api/v1/journey/sop/wizard/step
POST /api/v1/journey/sop/wizard/complete
POST /api/v1/journey/coexistence/analyze
POST /api/v1/journey/blueprint/generate
POST /api/v1/journey/journey/create
```

**Location:** `symphainy_platform/experience/solution_handlers.py` (stubbed)

**Endpoints to Document:**
```python
POST /api/v1/solution/visual/summary
POST /api/v1/solution/roadmap/generate
POST /api/v1/solution/poc/generate
POST /api/v1/solution/solution/create
```

**Location:** `symphainy_platform/experience/agent_handlers.py` (stubbed)

**Endpoints to Document:**
```python
POST /api/v1/agents/guide/chat
POST /api/v1/agents/journey/chat
POST /api/v1/agents/solution/chat
```

---

### Phase 9: Testing & Validation (2-3 days)

**Goal:** Lightweight unit and functional testing (E2E deferred until Experience Plane)

#### 9.1 Unit Tests

**Services:**
- Test each service method (deterministic, stateless)
- Mock State Surface for file retrieval
- Mock FileStorageAbstraction for artifact storage
- Validate input/output contracts

**Agents:**
- Test agent reasoning (no side effects)
- Test fact gathering from State Surface
- Validate artifact structure
- Test reasoning logic in isolation

**Orchestrators:**
- Test saga composition
- Test service calls (mocked)
- Test agent attachment (mocked)
- Test State Surface usage

#### 9.2 Functional Tests

**Realm-Level Flows:**
1. Journey: Create SOP from workflow → Validate SOP structure
2. Journey: Start wizard → Process step → Complete wizard → Validate SOP
3. Journey: Analyze coexistence → Generate blueprint → Validate blueprint
4. Solution: Generate roadmap from realm outputs → Validate roadmap structure
5. Solution: Generate POC proposal → Validate POC structure

**Agent Integration:**
- Test Guide Agent routing (mocked realm outputs)
- Test Liaison Agent guidance (mocked context)
- Test Specialist Agent reasoning (mocked facts)

#### 9.3 MVP Showcase Validation

**Validate MVP Requirements:**
- ✅ Operations pillar: Workflow/SOP upload, conversion, SOP wizard, coexistence analysis, blueprint, journey creation
- ✅ Business outcomes pillar: Summary visual, roadmap, POC proposal, solution creation
- ✅ Guide agent: Global concierge
- ✅ Liaison agents: Pillar-specific guidance

**Note:** Full E2E testing deferred until Experience Plane exists.

---

## 🔄 Rebuild Strategy (Not Migration)

### Legacy Code as Reference Only

**What to Use from Legacy:**
1. **Service Logic Patterns** - Deterministic algorithms (extract patterns, not copy code)
2. **Agent Reasoning Patterns** - LLM reasoning logic (understand approach, rebuild natively)
3. **Wizard Patterns** - Interactive wizard flows (understand UX, rebuild with native patterns)
4. **Conversion Algorithms** - SOP ↔ Workflow conversion logic (extract algorithms, rebuild)

**What to Leave Behind:**
1. **Old Base Classes** - `DeclarativeAgentBase`, `BusinessLiaisonAgentBase`, etc.
2. **Direct DB Access** - All DB writes go through State Surface
3. **Event Emission** - All events go through Runtime
4. **Orchestration Logic in Services** - Services are deterministic only
5. **Realm-Owned Execution** - Runtime owns execution
6. **Agent Orchestration** - Agents reason, orchestrators orchestrate

### Rebuild Pattern

**For Services:**
1. Understand deterministic logic from legacy service (reference)
2. Rebuild natively following realm structure
3. Ensure no orchestration logic (moves to orchestrator)
4. Ensure no reasoning logic (moves to agents)
5. Use State Surface for file retrieval (references)
6. Use FileStorageAbstraction for artifact storage
7. Return structured results

**For Agents:**
1. Understand reasoning logic from legacy agent (reference)
2. Rebuild natively extending `GroundedReasoningAgentBase`
3. Implement `reason()` method returning artifacts
4. Use `gather_facts()` for fact gathering from State Surface
5. Remove all side effects
6. Register with Agent Foundation Service during realm initialization

**For Orchestrators:**
1. Understand saga composition from legacy (reference)
2. Rebuild natively following realm pattern
3. Call services (deterministic)
4. Attach agents (reasoning)
5. Use State Surface for state and references
6. Register capabilities with Curator

---

## 📋 Detailed File Structure

### Journey Realm

```
symphainy_platform/realms/journey/
├── __init__.py
├── manager.py                          # Lifecycle & registration (registers agents)
├── foundation_service.py               # Realm foundation
├── orchestrators/
│   ├── __init__.py
│   └── journey_orchestrator.py        # Saga composition
├── services/
│   ├── __init__.py
│   ├── sop_builder_service/
│   │   ├── __init__.py
│   │   └── sop_builder_service.py
│   ├── workflow_conversion_service/
│   │   ├── __init__.py
│   │   └── workflow_conversion_service.py
│   └── coexistence_analysis_service/
│       ├── __init__.py
│       └── coexistence_analysis_service.py
└── agents/
    ├── __init__.py
    ├── journey_liaison_agent.py        # Conversational guidance
    ├── sop_builder_wizard_agent.py     # SOP generation reasoning
    ├── workflow_generator_agent.py     # Workflow generation reasoning
    └── coexistence_analyzer_agent.py  # Coexistence analysis reasoning
```

### Solution Realm

```
symphainy_platform/realms/solution/
├── __init__.py
├── manager.py                          # Lifecycle & registration (registers agents)
├── foundation_service.py               # Realm foundation
├── orchestrators/
│   ├── __init__.py
│   └── solution_orchestrator.py       # Saga composition
├── services/
│   ├── __init__.py
│   ├── roadmap_generation_service/
│   │   ├── __init__.py
│   │   └── roadmap_generation_service.py
│   ├── poc_generation_service/
│   │   ├── __init__.py
│   │   └── poc_generation_service.py
│   └── report_generator_service/
│       ├── __init__.py
│       └── report_generator_service.py
└── agents/
    ├── __init__.py
    ├── solution_liaison_agent.py      # Conversational guidance
    ├── roadmap_agent.py                # Roadmap generation reasoning
    └── poc_proposal_agent.py           # POC proposal generation reasoning
```

### Guide Agent (Platform-Wide)

```
symphainy_platform/agentic/agents/
├── __init__.py
└── guide_agent.py                      # Global concierge (registered at platform startup)
```

---

## ✅ Success Criteria

### Platform Engineering (Not Demo)

**✅ Realm Structure:**
- Manager, orchestrator, services, agents properly separated
- No circular dependencies
- Clean layer boundaries

**✅ Agent Foundation Pattern:**
- All agents extend `AgentBase` or `GroundedReasoningAgentBase`
- Agents return artifacts (no side effects)
- Agents use Runtime/State Surface for fact gathering
- **Agents registered during realm initialization**

**✅ Service Pattern:**
- Services are deterministic, stateless
- Services use State Surface for file retrieval (references)
- Services use FileStorageAbstraction for artifact storage
- Services return structured results

**✅ Orchestrator Pattern:**
- Orchestrators compose saga steps
- Orchestrators call services
- Orchestrators attach agents
- Orchestrators never store state directly
- Orchestrators use State Surface for state and references

**✅ State Surface Usage:**
- Artifacts stored in GCS/ArangoDB
- References and metadata stored in State Surface
- No artifacts stored directly in State Surface

### MVP Capabilities

**✅ Journey Realm:**
- Upload workflow/SOP files → parse and visualize
- Convert workflow ↔ SOP (bidirectional)
- Generate SOP from scratch via wizard
- Analyze coexistence opportunities
- Generate coexistence blueprint
- Create platform journey from blueprint

**✅ Solution Realm:**
- Generate summary visual from realm outputs
- Generate strategic roadmap
- Generate POC proposal
- Create platform solution from roadmap/POC

**✅ Agents:**
- Guide Agent (global concierge)
- Journey Liaison Agent (pillar guidance)
- Solution Liaison Agent (pillar guidance)
- SOP Builder Wizard Agent
- Workflow Generator Agent
- Coexistence Analyzer Agent
- Roadmap Agent
- POC Proposal Agent

---

## 🚀 Implementation Timeline

**Total Estimated Time:** 18-25 days

**Phase Breakdown:**
- Phase 1: Foundation & Structure (2-3 days)
- Phase 2: Journey Realm Services (3-4 days)
- Phase 3: Solution Realm Services (2-3 days)
- Phase 4: Journey Realm Orchestrator (2-3 days)
- Phase 5: Solution Realm Orchestrator (2-3 days)
- Phase 6: Agent Migration & Rebuild (4-5 days)
- Phase 7: Runtime Intent Integration (1-2 days)
- Phase 8: Experience Plane Integration (1-2 days) - Documentation only
- Phase 9: Testing & Validation (2-3 days) - Lightweight testing

**Parallel Work:**
- Phases 2 & 3 can be done in parallel (different realms)
- Phases 4 & 5 can be done in parallel (different realms)
- Agent rebuild (Phase 6) can be done in parallel with orchestrator work

---

## 📝 Implementation Notes

### Agent Registration Pattern

**During Realm Initialization:**
```python
# In JourneyRealmFoundationService.initialize()
async def initialize(self):
    # ... initialize services and orchestrator ...
    
    # Initialize agents
    self.journey_liaison_agent = JourneyLiaisonAgent(...)
    self.sop_builder_wizard_agent = SOPBuilderWizardAgent(...)
    # ... other agents ...
    
    # Register agents with Agent Foundation Service
    await self.agent_foundation.register_agent(self.journey_liaison_agent)
    await self.agent_foundation.register_agent(self.sop_builder_wizard_agent)
    # ... register other agents ...
```

### Artifact Storage Pattern

**In Orchestrator:**
```python
async def generate_blueprint(...):
    # 1. Get analysis from State Surface (reference)
    analysis_ref = await self.state_surface.get_reference(analysis_id)
    
    # 2. Retrieve actual artifact from storage
    analysis_artifact = await self.file_storage.get_file(analysis_ref.storage_location)
    
    # 3. Call service
    blueprint_data = await self.coexistence_service.generate_blueprint(analysis_artifact)
    
    # 4. Store artifact in GCS
    blueprint_storage_location = await self.file_storage.upload_file(
        f"{tenant_id}/{session_id}/{blueprint_id}/blueprint.json",
        json.dumps(blueprint_data).encode()
    )
    
    # 5. Store reference + metadata in State Surface
    await self.state_surface.store_reference(
        reference_id=f"blueprint:{tenant_id}:{session_id}:{blueprint_id}",
        storage_location=blueprint_storage_location,
        metadata={
            "type": "coexistence_blueprint",
            "created_at": self.clock.now_iso(),
            "status": "ready"
        }
    )
    
    return {"blueprint_reference": f"blueprint:{tenant_id}:{session_id}:{blueprint_id}"}
```

---

**Status:** 📋 **READY FOR IMPLEMENTATION**

This plan follows platform-forward principles, rebuilds natively (not migrates), and ensures all agents use the new Agent Foundation pattern with proper registration and state management.
