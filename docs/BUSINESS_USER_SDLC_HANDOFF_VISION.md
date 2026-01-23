# Business User → SDLC Handoff Vision

**Date:** January 2026  
**Purpose:** Bridge between business outcomes (Roadmap, POC Proposal) and SDLC execution

---

## Executive Summary

**The Vision:**
After users complete the MVP journey and receive **Roadmap** and **POC Proposal** artifacts, the **Business User View** should create everything necessary to handoff to the Developer/SDLC world for actual implementation.

**Key Insight:** Business artifacts (Roadmap, POC Proposal) contain structured information that can be translated into SDLC journey configurations, but this translation needs to happen in **business-friendly language** with guided workflows.

**Key Principles:**
1. **Platform as Black Box:** Business users don't need to know our SDLC vocabulary or technical details
2. **Suggest, Don't Ask:** Analyze artifacts and suggest answers, get user validation (not configuration from scratch)
3. **Client Environment Context:** Journey types are relative to **client's environment**, NOT our SymphAIny platform
4. **Business-Friendly Language:** All UI text uses business language, no technical jargon

**Starting Point:** POC Proposal (easier to scope and execute than full Roadmap)

---

## The Flow: MVP Journey → Business Handoff → SDLC Execution

### Phase 1: MVP Journey Completion
```
User completes MVP journey
  ↓
Receives artifacts:
  - Roadmap (implementation strategy)
  - POC Proposal (testing/validation)
  - Coexistence Blueprint (workflow optimization)
  ↓
These artifacts translate into platform solutions
```

### Phase 2: Business User Handoff Configuration
```
Business User View
  ↓
"Prepare for Implementation" workflow
  ↓
Guided configuration (business-friendly language):
  - Which SDLC journeys are "in play"?
  - What intents need to be composed vs built?
  - What artifacts are created?
  - How are artifacts governed/promoted?
  ↓
Generates SDLC Journey Configuration
```

### Phase 3: SDLC Journey Launch
```
SDLC Journey Configuration
  ↓
[Launch SDLC Journey] button
  ↓
SDLC Journey View (Developer View)
  ↓
7-phase execution (Intent → Architecture → Build → Validate → Promote)
```

---

## POC Proposal → SDLC Journey Translation

### What's in a POC Proposal?
Based on Outcomes Realm structure, a POC Proposal likely contains:
- **POC Scope:** What capabilities/features to test
- **Success Criteria:** How to measure success
- **Timeline:** Expected duration
- **Resources:** What's needed (systems, data, people)
- **Risks:** Known risks and mitigation
- **Dependencies:** What must be in place first

### How to Translate to SDLC Journey?

**Business User View Workflow (Suggest → Validate → Confirm):**

**Key Principle:** Platform/SDLC vocabulary is a "black box" to business users. We analyze artifacts and suggest answers, users validate.

1. **Journey Type Selection** (Relative to Client Environment, NOT our platform)
   - **We analyze:** POC Proposal scope, objectives, language
   - **We suggest:** Journey type (Build, Modernize, Extend, Replatform) with explanation
   - **User validates:** "Does this match your understanding?" [Yes] [No - clarify]

2. **Intent Composition vs. Creation**
   - **We analyze:** POC Proposal requirements, match to platform capabilities
   - **We suggest:** "We'll use existing platform capabilities for X, build custom for Y"
   - **User validates:** "Is this correct?" [Yes] [No - add/remove custom requirements]

3. **Artifact Definition**
   - **We analyze:** POC Proposal deliverables, success criteria
   - **We suggest:** "We'll create: Source code, Tests, Documentation"
   - **User validates:** "Does this match what you expect?" [Yes] [No - adjust]

4. **Governance & Promotion**
   - **We analyze:** POC Proposal risk level, timeline, success criteria
   - **We suggest:** "We suggest: Code review, Security review, Dev + Staging environments"
   - **User validates:** "Does this work for your organization?" [Yes] [No - adjust]

5. **Agent Team Configuration**
   - **We analyze:** POC Proposal scope, automatically configure team
   - **We suggest:** "We'll use: Architecture, Builder, Validator agents (auto-configured)"
   - **User validates:** "Any special requirements?" [No] [Yes - add]

---

## Business User View Enhancement

### Current Business User View:
```
Business User View
├── Solution Composition Guide
├── Solution Templates
├── Solution Builder (advanced, gated)
└── Feature Request System
```

### Enhanced Business User View:
```
Business User View
├── Solution Composition (existing)
├── Solution Templates (existing)
├── Implementation Preparation (NEW)
│   ├── View Artifacts from MVP Journey
│   │   ├── Roadmap
│   │   ├── POC Proposal
│   │   └── Coexistence Blueprint
│   ├── Prepare POC Implementation (NEW - starting point)
│   │   ├── Journey Type Selection
│   │   ├── Intent Composition vs. Creation
│   │   ├── Artifact Definition
│   │   ├── Governance & Promotion
│   │   └── Agent Team Configuration
│   ├── Prepare Roadmap Implementation (NEW - future)
│   └── Launch SDLC Journey (NEW)
└── Feature Request System (existing)
```

---

## Implementation Preparation Workflow (POC Focus)

### Step 1: View POC Proposal
**UI:** Display POC Proposal artifact from MVP journey
- Show scope, success criteria, timeline, resources
- Highlight key information that will be used to suggest SDLC configuration
- **Key Message:** "We'll use this information to prepare your implementation plan"

### Step 2: Journey Type Selection
**Business-Friendly Approach:**
> "Based on your POC Proposal, we've identified this as: **[SUGGESTED TYPE]**"
> 
> **Suggested Journey Type (from POC Proposal analysis):**
> - **Build New** - Creating new capabilities in your environment
> - **Modernize** - Updating/improving your existing systems
> - **Extend** - Adding features to your existing systems
> - **Replatform** - Moving your systems to new infrastructure
>
> **Does this match your understanding?** [Yes] [No - Let me clarify]

**How We Suggest:**
- Analyze POC Proposal scope, objectives, and context
- Infer journey type from language (e.g., "new system" → Build, "upgrade" → Modernize)
- Present suggestion with confidence score
- User validates or corrects

**Technical Mapping:**
- Build New → `build` journey type (client environment)
- Modernize → `modernize` journey type (client environment)
- Extend → `extend` journey type (client environment)
- Replatform → `replatform` journey type (client environment)

**Note:** Journey types are relative to **client's environment**, NOT our SymphAIny platform.

### Step 3: Intent Composition vs. Creation
**Business-Friendly Approach:**
> "Based on your POC Proposal, we've identified these capabilities:"
>
> **Suggested Capabilities (from POC Proposal analysis):**
> - [✓] Content processing - "Process uploaded documents" (from POC scope)
> - [✓] Insights generation - "Analyze business data" (from POC objectives)
> - [ ] Custom integration - "Connect to [System X]" (from POC requirements)
> - [ ] New analysis - "Specialized reporting" (from POC scope)
>
> **We believe these can use existing platform capabilities. Is that correct?**
> [Yes, that's right] [No, we need custom work for: _____]
>
> **For custom work, what specifically needs to be built?**
> [Free text or guided prompts]

**How We Suggest:**
- Parse POC Proposal to identify capability requirements
- Match requirements to existing platform capabilities (Content, Insights, Journey, Outcomes)
- Suggest "compose" for matches, "create" for gaps
- Present as checkboxes with pre-selected suggestions
- User validates or adds custom requirements

**Technical Mapping:**
- Suggested "compose" → Intent composition (use existing realm intents)
- User adds "custom" → Intent creation (define new intents, map to realm capabilities)

### Step 4: Artifact Definition
**Business-Friendly Approach:**
> "Based on your POC Proposal, we'll create:"
>
> **Suggested Deliverables (from POC Proposal):**
> - [✓] Source code - "Implementation of [feature from POC scope]"
> - [✓] Tests - "Validation of [success criteria from POC]"
> - [ ] Documentation - "User guides and technical docs"
> - [✓] Deployment configurations - "Setup for [environments from POC]"
>
> **Does this match what you expect?** [Yes] [No - Add/remove: _____]
>
> **For each deliverable, who needs to review it?**
> - Source code: [Suggested: Development team] [Change]
> - Tests: [Suggested: QA team] [Change]
> - Documentation: [Suggested: Product team] [Change]
>
> **Where should these be deployed?**
> - [✓] Development environment (internal testing)
> - [✓] Staging environment (pre-production)
> - [ ] Production environment (live)

**How We Suggest:**
- Extract deliverables from POC Proposal objectives and scope
- Suggest standard artifact types (code, tests, docs, configs)
- Pre-fill based on POC Proposal content
- Suggest review workflows based on artifact type
- User validates or adjusts

**Technical Mapping:**
- Deliverables → Artifact types
- Review workflow → Promotion gates
- Promotion target → Environment targets

### Step 5: Governance & Promotion
**Business-Friendly Approach:**
> "Based on your POC Proposal timeline and risk assessment, we suggest:"
>
> **Suggested Approval Workflow:**
> - [✓] Code review required - "Standard for all code changes"
> - [✓] Security review required - "Based on POC risk level: [Medium]"
> - [ ] Architecture review required - "Only if major changes"
> - [✓] Business stakeholder approval required - "Before production deployment"
>
> **Does this work for your organization?** [Yes] [No - Adjust: _____]
>
> **Suggested Environments:**
> - [✓] Development (internal testing) - "Standard for POC"
> - [✓] Staging (pre-production) - "For validation before production"
> - [ ] Production (live) - "Only if POC succeeds"
>
> **Does this match your deployment plan?** [Yes] [No - Adjust: _____]

**How We Suggest:**
- Analyze POC Proposal risk level, timeline, and success criteria
- Suggest standard approval workflows based on risk
- Suggest environments based on POC scope (typically dev + staging for POC)
- User validates or adjusts based on their organization's processes

**Technical Mapping:**
- Approval workflow → Promotion gates (policy rules)
- Environments → Deployment targets

### Step 6: Agent Team Configuration
**Business-Friendly Approach:**
> "Based on your POC Proposal scope, we'll use:"
>
> **Suggested Team Configuration:**
> - [✓] Architecture guidance - "For [scope item from POC]"
> - [✓] Code generation - "To build [capability from POC]"
> - [✓] Quality validation - "To meet [success criteria from POC]"
> - [✓] Deployment coordination - "For [environments from POC]"
>
> **Platform Capabilities Needed:**
> - [✓] Content processing - "For [data processing from POC]"
> - [✓] Insights generation - "For [analysis from POC]"
> - [ ] Journey optimization - "If workflow changes needed"
> - [ ] Outcomes synthesis - "If reporting needed"
>
> **This is all handled automatically. Any special requirements?**
> [No, this looks good] [Yes - Add: _____]

**How We Suggest:**
- Analyze POC Proposal to determine required expertise
- Automatically configure agent team based on journey type and scope
- Automatically identify realm agent participation based on capabilities needed
- Present as "this is what we'll use" (not asking user to configure)
- User only needs to add special requirements if any

**Technical Mapping:**
- Team roles → Agent team configuration (auto-configured)
- Realm agents → Realm orchestrator participation (governed, auto-detected)
- External tools → Adapter configuration (auto-configured)

### Step 7: Review & Launch
**UI:** Summary view of SDLC Journey Configuration
- Journey type
- Intents (composed vs. created)
- Artifacts and lifecycle
- Governance rules
- Agent team
- Estimated timeline (from POC Proposal)

**Actions:**
- [Save Configuration] - Save for later
- [Launch SDLC Journey] - Start journey execution
- [Export Configuration] - Export as JSON/YAML for review

---

## SDLC Journey Configuration Data Model

```python
class SDLCJourneyConfig:
    """SDLC Journey Configuration from Business User View."""
    
    # Source
    source_artifact_id: str  # POC Proposal artifact ID
    source_artifact_type: str  # "poc_proposal", "roadmap", "blueprint"
    
    # Journey Type
    journey_type: str  # "build", "modernize", "extend", "replatform"
    
    # Intent Configuration
    intents: Dict[str, IntentConfig]
    # {
    #   "compose": ["ingest_file", "parse_content", "analyze_content"],
    #   "create": [
    #     {
    #       "intent_name": "custom_analysis",
    #       "realm": "insights",
    #       "description": "Custom analysis for POC"
    #     }
    #   ]
    # }
    
    # Artifact Definition
    artifacts: List[ArtifactConfig]
    # [
    #   {
    #     "type": "source_code",
    #     "description": "Custom analysis service",
    #     "lifecycle": ["ephemeral", "working_material", "record_of_fact"],
    #     "promotion_gates": ["code_review", "security_review"],
    #     "deployment_targets": ["dev", "staging"]
    #   }
    # ]
    
    # Governance
    governance: GovernanceConfig
    # {
    #   "approval_workflows": ["architecture_review", "code_review"],
    #   "promotion_gates": {
    #     "working_material": ["code_review"],
    #     "record_of_fact": ["security_review", "stakeholder_approval"]
    #   },
    #   "environments": ["dev", "staging", "prod"]
    # }
    
    # Agent Team
    agent_team: AgentTeamConfig
    # {
    #   "required_agents": ["architect", "builder", "validator", "promoter"],
    #   "realm_agents": {
    #     "insights": ["business_analysis_agent"],  # Governed participation
    #     "content": ["structured_extraction_agent"]
    #   },
    #   "external_tools": ["cursor", "codex"]
    # }
    
    # Timeline (from POC Proposal)
    timeline: TimelineConfig
    # {
    #   "estimated_duration": "4 weeks",
    #   "milestones": [...]
    # }
```

---

## Backend Implementation

### New Service: `ImplementationPreparationService`

**Location:** `symphainy_platform/civic_systems/experience/admin_dashboard/services/implementation_preparation_service.py`

**Methods:**
```python
class ImplementationPreparationService:
    """Service for preparing business artifacts for SDLC execution."""
    
    async def get_artifacts_from_journey(
        self,
        session_id: str,
        journey_type: str = "mvp"
    ) -> List[Artifact]:
        """Get artifacts (Roadmap, POC Proposal, Blueprint) from MVP journey."""
    
    async def parse_poc_proposal(
        self,
        poc_proposal_artifact: Artifact
    ) -> POCProposalData:
        """Parse POC Proposal artifact to extract structured data."""
    
    async def analyze_poc_proposal(
        self,
        poc_proposal_artifact: Artifact
    ) -> POCProposalAnalysis:
        """Analyze POC Proposal to suggest SDLC configuration."""
    
    async def suggest_sdlc_config(
        self,
        source_artifact: Artifact
    ) -> SDLCJourneyConfigSuggestion:
        """Suggest SDLC Journey Configuration from artifact analysis."""
    
    async def create_sdlc_journey_config(
        self,
        source_artifact: Artifact,
        user_validations: Dict[str, Any]  # User validates/corrects suggestions
    ) -> SDLCJourneyConfig:
        """Create SDLC Journey Configuration from artifact analysis + user validations."""
    
    async def validate_sdlc_config(
        self,
        config: SDLCJourneyConfig
    ) -> ValidationResult:
        """Validate SDLC Journey Configuration."""
    
    async def launch_sdlc_journey(
        self,
        config: SDLCJourneyConfig
    ) -> SDLCJourney:
        """Launch SDLC Journey from configuration."""
```

### New API: `/api/admin/business/implementation-preparation/*`

**Endpoints:**
```python
@router.get("/artifacts")
async def get_journey_artifacts(
    session_id: str,
    journey_type: str = "mvp"
):
    """Get artifacts from MVP journey."""

@router.post("/prepare-poc")
async def prepare_poc_implementation(
    request: PreparePOCRequest
):
    """Prepare POC Proposal for SDLC execution."""

@router.post("/create-sdlc-config")
async def create_sdlc_config(
    request: CreateSDLCConfigRequest
):
    """Create SDLC Journey Configuration."""

@router.post("/launch-journey")
async def launch_sdlc_journey(
    request: LaunchJourneyRequest
):
    """Launch SDLC Journey from configuration."""
```

---

## Realm Agent Participation (Governed)

### How Realm Agents Participate in SDLC Journeys

**Pattern:** SDLC Orchestrators call Realm Orchestrators (governed)

**Example Flow:**
```
SDLC Builder Agent needs to generate code
  ↓
SDLC Orchestrator determines: "Need Insights realm capability"
  ↓
SDLC Orchestrator calls Insights Orchestrator (via Runtime)
  ↓
Insights Orchestrator delegates to BusinessAnalysisAgent
  ↓
BusinessAnalysisAgent executes (governed by SDLC journey policy)
  ↓
Results returned to SDLC Orchestrator
  ↓
SDLC Builder Agent uses results to generate code
```

**Governance:**
- SDLC Orchestrator enforces SDLC journey policy
- Realm Orchestrator enforces realm policy
- Both policies must be satisfied
- Audit trail tracks cross-realm participation

**Implementation:**
- SDLC Orchestrator uses Runtime to submit intents to realm orchestrators
- Realm orchestrators check if intent is part of SDLC journey (via ExecutionContext)
- If yes, apply SDLC journey policy in addition to realm policy
- Return results to SDLC Orchestrator

---

## UI/UX Vision

### Business User View: Implementation Preparation Tab

**Layout:**
```
┌─────────────────────────────────────────────────────────┐
│ Implementation Preparation                              │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  Your MVP Journey Artifacts                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Roadmap     │  │ POC Proposal │  │   Blueprint  │  │
│  │  [View]      │  │  [Prepare] ← │  │   [View]     │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                           │
│  POC Implementation Preparation                           │
│  ┌────────────────────────────────────────────────────┐ │
│  │ We've analyzed your POC Proposal and prepared:     │ │
│  │                                                      │ │
│  │ Step 1: Journey Type                                │ │
│  │ Suggested: ● Build New (in your environment)      │ │
│  │            ○ Modernize  ○ Extend  ○ Replatform     │ │
│  │ Does this match? [✓ Yes] [No - Let me clarify]     │ │
│  │                                                      │ │
│  │ Step 2: Capabilities                                │ │
│  │ We'll use: [✓] Content processing                  │ │
│  │          [✓] Insights generation                    │ │
│  │          [ ] Custom integration (you mentioned)    │ │
│  │ Is this correct? [✓ Yes] [No - Add/remove: ___]    │ │
│  │                                                      │ │
│  │ Step 3: Deliverables                                │ │
│  │ We'll create: [✓] Source code                       │ │
│  │            [✓] Tests                                 │ │
│  │            [ ] Documentation                          │ │
│  │ Add/remove? [✓ Looks good] [Adjust: ___]            │ │
│  │                                                      │ │
│  │ Step 4: Governance                                 │ │
│  │ Approvals: [✓] Code review                          │ │
│  │          [✓] Security review                        │ │
│  │ Environments: [✓] Dev  [✓] Staging                 │ │
│  │ Works for you? [✓ Yes] [Adjust: ___]               │ │
│  │                                                      │ │
│  │ Step 5: Team (Auto-configured)                      │ │
│  │ ✓ Architecture  ✓ Builder  ✓ Validator             │ │
│  │ Any special requirements? [No] [Yes: ___]          │ │
│  │                                                      │ │
│  │ [Save Configuration]  [Launch SDLC Journey] →      │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

---

## Implementation Phases

### Phase 1: POC Proposal Analysis (2 weeks)
**Goal:** Analyze POC Proposal artifacts to suggest SDLC configuration

**Tasks:**
1. Create `POCProposalParser` service
2. Create `POCProposalAnalyzer` service (NEW - suggests configuration)
3. Define POC Proposal data model
4. Parse POC Proposal artifacts (DOCX, JSON)
5. Extract: scope, success criteria, timeline, resources
6. **Analyze and suggest:**
   - Journey type (with confidence score)
   - Capabilities (compose vs create)
   - Deliverables (artifact types)
   - Governance (approval workflows)
   - Agent team configuration

**Deliverable:** Can analyze POC Proposal and suggest SDLC configuration

---

### Phase 2: Implementation Preparation UI (2-3 weeks)
**Goal:** Build validation workflow (suggest → validate → confirm)

**Tasks:**
1. Create "Implementation Preparation" tab in Business User View
2. Build artifact viewer (Roadmap, POC Proposal, Blueprint)
3. Build **suggestion + validation workflow** (6 steps):
   - Show suggestions from analysis
   - Allow user to validate/correct
   - Confirm final configuration
4. Create SDLC Journey Configuration data model
5. Build configuration summary and review UI
6. **Hide technical vocabulary** - use business-friendly language only

**Deliverable:** Business users can validate suggested SDLC configuration (no technical knowledge required)

---

### Phase 3: SDLC Configuration Service (2 weeks)
**Goal:** Backend service to analyze artifacts and create SDLC configurations

**Tasks:**
1. Create `ImplementationPreparationService`
2. Implement `analyze_poc_proposal()` method (suggests configuration)
3. Implement `suggest_sdlc_config()` method (returns suggestions)
4. Implement `create_sdlc_journey_config()` method (from suggestions + user validations)
5. Implement `validate_sdlc_config()` method
6. Create API endpoints
7. Integrate with SDLC Journey Service (when ready)

**Deliverable:** Backend can analyze artifacts, suggest configurations, and create from user validations

---

### Phase 4: SDLC Journey Launch (1 week)
**Goal:** Launch SDLC Journey from configuration

**Tasks:**
1. Implement `launch_sdlc_journey()` method
2. Create SDLC Journey from configuration
3. Initialize journey with proper phase (Architecture Synthesis)
4. Connect to SDLC Journey View

**Deliverable:** Can launch SDLC Journey from Business User View

---

### Phase 5: Realm Agent Participation (2 weeks)
**Goal:** Enable governed realm agent participation in SDLC journeys

**Tasks:**
1. Update SDLC Orchestrator to call realm orchestrators
2. Add SDLC journey context to ExecutionContext
3. Update realm orchestrators to check SDLC journey context
4. Apply SDLC journey policy in addition to realm policy
5. Add audit trail for cross-realm participation

**Deliverable:** Realm agents can participate in SDLC journeys (governed)

---

## Key Principles

1. **Platform as Black Box:** Business users don't need to know our SDLC vocabulary or technical details
2. **Suggest, Don't Ask:** Analyze artifacts and suggest answers, get user validation
3. **Client Environment Context:** Journey types are relative to client's environment, NOT our platform
4. **Business-Friendly Language:** All UI text uses business language, no technical jargon
5. **Validation, Not Configuration:** Users validate/correct suggestions, not configure from scratch

## Key Questions

1. **POC Proposal Structure:** What's the exact structure of POC Proposal artifacts? (Need to review actual artifact format)

2. **Roadmap Translation:** Should we also build Roadmap → SDLC Journey translation, or focus on POC first?

3. **Configuration Persistence:** Should SDLC configurations be saved as artifacts themselves?

4. **Validation Rules:** What validation rules should we apply to SDLC configurations?

5. **Timeline Integration:** How should POC Proposal timeline map to SDLC journey phases?

6. **Confidence Scores:** Should we show confidence scores for suggestions, or just present as "suggested"?

---

## Next Steps

1. **Review POC Proposal structure** - Understand actual artifact format
2. **Design data models** - SDLCJourneyConfig, POCProposalData, etc.
3. **Create implementation plan** - Detailed tasks for Phase 1
4. **Align on UI/UX** - Confirm workflow steps and language
5. **Start Phase 1** - POC Proposal parsing

---

**Status:** Vision defined, ready for implementation planning
