# Admin Dashboard & Agentic IDP Vision Alignment

**Date:** January 2026  
**Purpose:** Strategic alignment between current Admin Dashboard implementation and Agentic IDP vision

---

## Executive Summary

**Current State:**
- Admin Dashboard has **3 views** (Control Room, Developer View, Business User View)
- Well-structured backend services with clear separation of concerns
- **No frontend UI yet** (backend APIs exist, but no React components found)
- Focus on platform observability, developer tools, and solution composition

**Agentic IDP Vision:**
- **Agentic SDLC Journey UI** - treating software development as governed transformation
- 7-phase flow: Ingest → Interpret → Architecture → Build → Validate → Promote → Deploy
- Agent teams (Liaison, Architect, Planner, Builder, Validator, Promoter, Curator)
- **Not an IDE** - it's a "governed journey through intent → system → code → promotion"

**Key Insight:** The Admin Dashboard's **Developer View** is the natural home for Agentic IDP, but it needs to evolve from "documentation/playground" to "SDLC journey orchestrator."

---

## Current Admin Dashboard Architecture

### 1. Control Room (Platform Observability)
**Backend:** `ControlRoomService`  
**APIs:** `/api/admin/control-room/*`

**Current Capabilities:**
- Platform statistics (realms, solutions)
- Execution metrics (TODO: needs telemetry integration)
- Realm health status
- Solution registry status
- System health (runtime, infrastructure)

**Alignment with Agentic IDP:**
- ✅ **Perfect fit** for monitoring SDLC journeys
- ✅ Can track agent execution, build artifacts, promotion status
- ✅ Already has health monitoring structure
- **Enhancement:** Add "SDLC Journey" metrics alongside platform metrics

---

### 2. Developer View (Developer Tools)
**Backend:** `DeveloperViewService`  
**APIs:** `/api/admin/developer/*`

**Current Capabilities:**
- Platform SDK documentation
- Code examples
- Patterns & best practices
- Solution Builder Playground (gated)
- Feature submission (gated - "Coming Soon")

**Alignment with Agentic IDP:**
- ⚠️ **Needs significant evolution**
- Current: Static documentation + playground
- Vision: **Agentic SDLC Journey UI** (7-phase flow)
- **Gap:** Missing journey orchestration, agent teams, artifact lifecycle

**Strategic Decision:**
- **Option A:** Evolve Developer View into "SDLC Journey View"
- **Option B:** Create new "SDLC Journey" view, keep Developer View for docs
- **Recommendation:** **Option A** (evolve) - Developer View becomes the SDLC orchestrator

---

### 3. Business User View (Solution Composition)
**Backend:** `BusinessUserViewService`  
**APIs:** `/api/admin/business/*`

**Current Capabilities:**
- Solution composition guide
- Solution templates
- Solution Builder (advanced, gated)
- Feature request system

**Alignment with Agentic IDP:**
- ✅ **Good fit** for "Intent Capture" phase
- ✅ Solution composition aligns with "Architecture Synthesis"
- **Enhancement:** Add SDLC journey initiation from solution composition

---

## Strategic Alignment Recommendations

### Phase 1: Evolve Developer View → SDLC Journey View

**Current Developer View:**
```
Developer View
├── Documentation (static)
├── Code Examples (static)
├── Patterns (static)
├── Solution Builder Playground (gated)
└── Feature Submission (gated)
```

**Evolved SDLC Journey View:**
```
SDLC Journey View
├── Journey Selection (Modernize / Build / Extend / Replatform)
├── Intent Capture (Chat + Structured Prompts)
├── Source Intake (Optional - Git, Zip, Docs)
├── Architecture Synthesis (Visual Canvas + ADRs)
├── Build Plan (Agentic Sprint Board)
├── Code Generation & Review (Cursor/Codex integration)
├── Validation & Quality Gates
└── Promotion & Deployment
```

**Implementation Strategy:**
1. **Keep existing docs/examples** as a "Reference" tab
2. **Add new "SDLC Journey" tab** as primary interface
3. **Migrate Solution Builder Playground** into "Build Plan" phase
4. **Integrate Metrics API** for agent/orchestrator monitoring

---

### Phase 2: Enhance Control Room for SDLC Observability

**Current Control Room:**
- Platform statistics
- Execution metrics (needs telemetry)
- Realm health
- Solution registry

**Enhanced Control Room:**
- ✅ **Keep existing** platform observability
- ➕ **Add SDLC Journey metrics:**
  - Active journeys (by type: Modernize, Build, Extend, Replatform)
  - Journey phase distribution (Intent → Architecture → Build → Validate → Promote)
  - Agent team performance (Liaison, Architect, Planner, Builder, Validator, Promoter)
  - Artifact lifecycle tracking (Ephemeral → Working Material → Record of Fact)
  - Promotion pipeline status
  - Code generation stats (via Cursor/Codex adapters)

**Integration Points:**
- Use **Metrics API** (`/api/v1/metrics/agents`, `/api/v1/metrics/orchestrators`)
- Add **SDLC-specific metrics** to telemetry service
- Track **artifact promotions** in Control Room

---

### Phase 3: Connect Business User View to SDLC Journey

**Current Business User View:**
- Solution composition
- Templates
- Feature requests

**Enhanced Business User View:**
- ✅ **Keep existing** solution composition
- ➕ **Add "Start SDLC Journey" button** from composed solutions
- ➕ **Template → SDLC Journey** flow:
  - Select template → Customize → **Launch SDLC Journey**
  - Journey starts at "Architecture Synthesis" phase (solution already composed)

**Flow:**
```
Business User View
  └── Compose Solution
      └── [Launch SDLC Journey] → SDLC Journey View (Phase 3: Architecture)
```

---

## UI/UX Alignment

### Agentic IDP Vision UI Elements:
1. **Entry Point:** Journey selection tiles (Modernize, Build, Extend, Replatform)
2. **Intent Capture:** Chat + Structured prompts panel
3. **Architecture Canvas:** Visual boxes + arrows (PowerPoint-level)
4. **Build Plan:** Agentic Sprint Board (columns: Intent → Planned → Generated → Validated → Ready)
5. **Code Review:** Read-only diff + test results + risk flags
6. **Promotion:** Explicit promotion with environment selection

### Admin Dashboard Current Structure:
- **3-view architecture** (Control Room, Developer, Business)
- **Gated features** (access control service)
- **Service-based backend** (clean separation)

### Recommended UI Evolution:

**Option 1: Tabbed Interface (Recommended)**
```
Admin Dashboard
├── Control Room Tab
│   ├── Platform Metrics (existing)
│   └── SDLC Journey Metrics (new)
├── SDLC Journey Tab (evolved from Developer View)
│   ├── Journey Selection
│   ├── Active Journeys
│   └── Journey Builder (7-phase flow)
└── Business User Tab (existing)
    ├── Solution Composition (existing)
    └── Launch SDLC Journey (new)
```

**Option 2: Separate "SDLC Journey" View**
```
Admin Dashboard
├── Control Room (existing)
├── Developer View (keep for docs)
├── SDLC Journey (new, separate)
└── Business User (existing)
```

**Recommendation:** **Option 1** - Evolve Developer View into SDLC Journey View, keep docs as reference tab.

---

## Backend Architecture Alignment

### Current Admin Dashboard Services:
```
AdminDashboardService
├── ControlRoomService (observability)
├── DeveloperViewService (docs, playground)
├── BusinessUserViewService (composition)
└── AccessControlService (gating)
```

### Proposed SDLC Journey Services:
```
AdminDashboardService
├── ControlRoomService (enhanced with SDLC metrics)
├── SDLCJourneyService (NEW - replaces DeveloperViewService)
│   ├── Journey orchestration
│   ├── Agent team coordination
│   ├── Artifact lifecycle management
│   └── Cursor/Codex adapter integration
├── BusinessUserViewService (enhanced with journey launch)
└── AccessControlService (existing)
```

**Key Services to Add:**
1. **SDLCJourneyService:**
   - `create_journey(intent_type, source_data)` → Journey ID
   - `get_journey_phase(journey_id)` → Current phase
   - `advance_phase(journey_id, artifacts)` → Next phase
   - `get_agent_team_status(journey_id)` → Agent statuses
   - `promote_artifact(journey_id, artifact_id, environment)` → Promotion

2. **SDLCArtifactService:**
   - `create_artifact(journey_id, type, content)` → Artifact ID
   - `promote_artifact(artifact_id, target_state)` → Promotion
   - `get_artifact_lineage(artifact_id)` → Lineage

3. **SDLCAdapterService:**
   - `generate_code(build_instructions)` → Code artifact (via Cursor/Codex)
   - `validate_code(code_artifact_id)` → Validation results
   - `run_tests(code_artifact_id)` → Test results

---

## Metrics Integration

### Current Metrics API:
- `/api/v1/metrics/agents` - Agent metrics
- `/api/v1/metrics/orchestrators` - Orchestrator metrics
- `/api/v1/metrics/platform` - Platform-wide metrics

### SDLC-Specific Metrics to Add:
- `/api/v1/metrics/sdlc/journeys` - Active journeys, phase distribution
- `/api/v1/metrics/sdlc/artifacts` - Artifact lifecycle stats
- `/api/v1/metrics/sdlc/agents` - SDLC agent team performance
- `/api/v1/metrics/sdlc/promotions` - Promotion pipeline stats

**Integration:**
- Extend `AgenticTelemetryService` with SDLC-specific events
- Add SDLC metrics to Control Room dashboard
- Track journey phases, artifact promotions, agent execution

---

## Implementation Phases

### Phase 1: Foundation (2-3 weeks)
**Goal:** Evolve Developer View structure, add SDLC journey service skeleton

**Tasks:**
1. Create `SDLCJourneyService` (replace `DeveloperViewService`)
2. Add SDLC journey APIs (`/api/admin/sdlc-journey/*`)
3. Create journey data models (Journey, Phase, Artifact, AgentTeam)
4. Integrate Metrics API into Control Room
5. Add "SDLC Journey Metrics" section to Control Room

**Deliverable:** Backend structure ready, APIs defined, no UI yet

---

### Phase 2: Journey Orchestration (3-4 weeks)
**Goal:** Implement 7-phase journey flow, agent team coordination

**Tasks:**
1. Implement journey phase state machine
2. Create agent team coordination (Liaison, Architect, Planner, Builder, Validator, Promoter)
3. Implement artifact lifecycle (Ephemeral → Working Material → Record of Fact)
4. Add journey persistence (ArangoDB)
5. Create journey APIs (create, advance, get status)

**Deliverable:** Backend journey orchestration working, can create and advance journeys

---

### Phase 3: UI Implementation (4-5 weeks)
**Goal:** Build SDLC Journey UI following Agentic IDP vision

**Tasks:**
1. Journey Selection UI (tiles: Modernize, Build, Extend, Replatform)
2. Intent Capture UI (chat + structured prompts)
3. Architecture Canvas UI (visual boxes + arrows)
4. Build Plan UI (agentic sprint board)
5. Code Review UI (read-only diff + tests)
6. Promotion UI (explicit promotion with environment)

**Deliverable:** Full SDLC Journey UI, integrated with backend

---

### Phase 4: Cursor/Codex Integration (2-3 weeks)
**Goal:** Integrate external code generation tools as adapters

**Tasks:**
1. Create `CodeGenerationAdapter` interface
2. Implement Cursor adapter (if API available)
3. Implement Codex adapter (OpenAI API)
4. Integrate into Builder agent workflow
5. Add code generation metrics

**Deliverable:** Code generation working via adapters, no architectural sin

---

### Phase 5: Self-Hosting (2-3 weeks)
**Goal:** Use SDLC Journey to evolve SDLC Journey (dogfood)

**Tasks:1. Create "Extend SymphAIny Platform" journey type
2. Use SDLC Journey to build SDLC Journey enhancements
3. Document dogfooding process
4. Validate governance works for platform evolution

**Deliverable:** Platform can evolve itself via SDLC Journey

---

## Key Architectural Decisions

### Decision 1: Evolve vs. Replace Developer View
**Decision:** **Evolve** Developer View into SDLC Journey View
**Rationale:**
- Developer View already has structure (playground, docs)
- Natural progression: docs → playground → journey orchestrator
- Keeps admin dashboard structure clean (3 views)

### Decision 2: Agent Team Implementation
**Decision:** Use existing agent framework (`AgentBase`, orchestrators)
**Rationale:**
- Already have agent infrastructure
- SDLC agents are just specialized agents
- Follows existing agentic forward pattern

### Decision 3: Artifact Lifecycle
**Decision:** Use existing Artifact Plane + promotion workflows
**Rationale:**
- Artifact lifecycle already defined in architecture
- Code artifacts are just another artifact type
- Promotion workflows already exist

### Decision 4: Cursor/Codex Integration
**Decision:** Use adapters, not direct integration
**Rationale:**
- Keeps architecture pure (tools are adapters, not brains)
- Allows swapping code generation backends
- Maintains governance boundaries

---

## Questions for Alignment - ANSWERS

1. **UI Structure:** Do you prefer Option 1 (evolve Developer View) or Option 2 (separate SDLC Journey view)?
   - ✅ **Answer:** Option 1 - Evolve Developer View into SDLC Journey View

2. **Journey Types:** Should we start with all 4 journey types (Modernize, Build, Extend, Replatform) or focus on one first?
   - ✅ **Answer:** Show all 4, prioritize based on client demand/payment

3. **Agent Teams:** Should SDLC agents be separate from realm agents, or can realm agents participate in SDLC journeys?
   - ✅ **Answer:** Realm agents can participate, but must be governed (SDLC orchestrators call realm orchestrators)

4. **Metrics Dashboard:** Should SDLC metrics be integrated into Control Room, or separate "SDLC Control Room"?
   - ✅ **Answer:** Separate SDLC "PMO hub", but Control Room gets summary metrics for holistic view

5. **Business User Integration:** Should solution composition automatically create a journey, or require explicit "Launch Journey" action?
   - ✅ **Answer:** Explicit "Launch Journey" button (see Business User → SDLC Handoff Vision below)

6. **Frontend Priority:** Should we build backend first (Phases 1-2) then UI (Phase 3), or build UI alongside backend?
   - ✅ **Answer:** Align on frontend UI vision first, then build backend, then frontend

---

## Business User → SDLC Handoff Vision (EXPANDED)

**See:** `BUSINESS_USER_SDLC_HANDOFF_VISION.md` for full details

**Key Concept:**
After users complete MVP journey and receive **Roadmap** and **POC Proposal** artifacts, the **Business User View** creates everything necessary to handoff to Developer/SDLC world for actual implementation.

**Flow:**
```
MVP Journey Completion
  ↓
Roadmap + POC Proposal Artifacts
  ↓
Business User View: "Implementation Preparation"
  ↓
Guided Configuration (business-friendly language):
  - Which SDLC journeys are "in play"?
  - What intents need to be composed vs built?
  - What artifacts are created?
  - How are artifacts governed/promoted?
  ↓
SDLC Journey Configuration
  ↓
[Launch SDLC Journey] → SDLC Journey View
```

**Starting Point:** POC Proposal (easier to scope than full Roadmap)

**Implementation:** New "Implementation Preparation" workflow in Business User View

---

## Updated Strategic Recommendations

### 1. Metrics Architecture
- **SDLC PMO Hub:** Separate dashboard for SDLC journey metrics
- **Control Room:** Gets summary SDLC metrics for holistic platform view
- **Integration:** SDLC PMO Hub exposes summary API → Control Room consumes

### 2. Realm Agent Participation (Governed)
- **Pattern:** SDLC Orchestrators call Realm Orchestrators (via Runtime)
- **Governance:** Both SDLC journey policy AND realm policy must be satisfied
- **Audit:** Full audit trail for cross-realm participation
- **Implementation:** SDLC Orchestrator submits intents to realm orchestrators, realm orchestrators check SDLC journey context and apply both policies

### 3. Business User View Enhancement
- **New Tab:** "Implementation Preparation"
- **Workflow:** Guided 6-step configuration (business-friendly language)
- **Source:** POC Proposal artifacts from MVP journey
- **Output:** SDLC Journey Configuration
- **Action:** [Launch SDLC Journey] button

---

## Updated Implementation Phases

### Phase 0: UI Vision Alignment (1 week)
**Goal:** Align on frontend UI vision before building backend

**Tasks:**
1. Design SDLC Journey View UI (7-phase flow)
2. Design Business User Implementation Preparation UI (6-step workflow)
3. Design SDLC PMO Hub UI (metrics dashboard)
4. Create UI mockups/wireframes
5. Get stakeholder approval

**Deliverable:** UI vision documented and approved

---

### Phase 1: Foundation (2-3 weeks)
**Goal:** Evolve Developer View structure, add SDLC journey service skeleton

**Tasks:**
1. Create `SDLCJourneyService` (replace `DeveloperViewService`)
2. Add SDLC journey APIs (`/api/admin/sdlc-journey/*`)
3. Create journey data models (Journey, Phase, Artifact, AgentTeam)
4. Integrate Metrics API into Control Room (summary metrics)
5. Create SDLC PMO Hub service skeleton

**Deliverable:** Backend structure ready, APIs defined, no UI yet

---

### Phase 2: Journey Orchestration (3-4 weeks)
**Goal:** Implement 7-phase journey flow, agent team coordination

**Tasks:**
1. Implement journey phase state machine
2. Create agent team coordination (Liaison, Architect, Planner, Builder, Validator, Promoter)
3. Implement artifact lifecycle (Ephemeral → Working Material → Record of Fact)
4. Add journey persistence (ArangoDB)
5. Create journey APIs (create, advance, get status)
6. **Implement realm agent participation (governed)**

**Deliverable:** Backend journey orchestration working, can create and advance journeys, realm agents can participate

---

### Phase 3: Business User Handoff (2-3 weeks)
**Goal:** Build Implementation Preparation workflow

**Tasks:**
1. Create `ImplementationPreparationService`
2. Build POC Proposal parser
3. Create guided configuration workflow (6 steps)
4. Build SDLC Journey Configuration data model
5. Create API endpoints
6. **Build UI** (Implementation Preparation tab)

**Deliverable:** Business users can prepare POC for SDLC execution

---

### Phase 4: UI Implementation (4-5 weeks)
**Goal:** Build SDLC Journey UI following Agentic IDP vision

**Tasks:**
1. Journey Selection UI (tiles: Modernize, Build, Extend, Replatform)
2. Intent Capture UI (chat + structured prompts)
3. Architecture Canvas UI (visual boxes + arrows)
4. Build Plan UI (agentic sprint board)
5. Code Review UI (read-only diff + tests)
6. Promotion UI (explicit promotion with environment)
7. **SDLC PMO Hub UI** (metrics dashboard)

**Deliverable:** Full SDLC Journey UI, integrated with backend

---

### Phase 5: Cursor/Codex Integration (2-3 weeks)
**Goal:** Integrate external code generation tools as adapters

**Tasks:**
1. Create `CodeGenerationAdapter` interface
2. Implement Cursor adapter (if API available)
3. Implement Codex adapter (OpenAI API)
4. Integrate into Builder agent workflow
5. Add code generation metrics

**Deliverable:** Code generation working via adapters, no architectural sin

---

### Phase 6: Self-Hosting (2-3 weeks)
**Goal:** Use SDLC Journey to evolve SDLC Journey (dogfood)

**Tasks:**
1. Create "Extend SymphAIny Platform" journey type
2. Use SDLC Journey to build SDLC Journey enhancements
3. Document dogfooding process
4. Validate governance works for platform evolution

**Deliverable:** Platform can evolve itself via SDLC Journey

---

## Next Steps

1. ✅ **Test Metrics API** - Verify endpoints work (done - requires auth)
2. ✅ **Align on UI structure** - Option 1 confirmed
3. ✅ **Align on frontend priority** - UI vision first, then backend, then frontend
4. **Create UI vision documents** - Mockups/wireframes for all three views
5. **Define journey data models** - What does a Journey, Phase, Artifact look like?
6. **Create implementation plan** - Detailed tasks for Phase 0 (UI Vision Alignment)

---

**Status:** ✅ Aligned on strategy, ready for UI vision alignment (Phase 0)
