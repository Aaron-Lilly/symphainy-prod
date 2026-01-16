# Comprehensive Testing Plan: Foundation Validation (UPDATED)

**Status:** Ready to Execute (Updated for Latest Platform Changes)  
**Created:** January 2026  
**Last Updated:** January 2026 (After Guide Agent, Visual Generation, Insights Realm Refactoring)  
**Goal:** Validate platform foundation before documentation

---

## Executive Summary

This plan establishes a **docker-based testing infrastructure** and a **holistic integrated test strategy** that validates:

1. **Architectural Compliance** - 5-layer architecture, Public Works pattern, Runtime Participation Contract
2. **Functional Compliance** - MVP showcase use case delivery (including all new capabilities)
3. **Extensibility Vision** - 350k insurance policies, legacy system migration
4. **Frontend Integration Readiness** - API contracts, WebSocket streaming, authentication
5. **Platform Stability** - Error handling, recovery, performance

**Key Principle:** Test against the **same infrastructure as production** (docker-compose) to avoid environment divergence.

**Recent Updates:**
- ✅ Insights Realm 3-phase flow (Data Quality, Data Interpretation, Business Analysis)
- ✅ Visual Generation Service (workflows, SOPs, summaries, roadmaps, POCs, lineage graphs)
- ✅ Lineage Visualization Service (reimagined Virtual Data Mapper)
- ✅ SOP from Interactive Chat (Journey Liaison Agent)
- ✅ Guide Agent (global concierge for user navigation)
- ✅ Complete lineage tracking (Supabase + Data Brain)

---

## Part 1: Docker-Based Testing Infrastructure

### Status: ✅ COMPLETE

**Files Created:**
- ✅ `docker-compose.test.yml` - Test-specific docker-compose configuration
- ✅ `tests/infrastructure/docker_compose_test.py` - Docker compose test utilities
- ✅ `tests/infrastructure/test_fixtures.py` - Infrastructure fixtures
- ✅ `tests/infrastructure/test_data_manager.py` - Test data management

**Validation:**
- ✅ Docker-based testing infrastructure validated
- ✅ ArangoDB Adapter tests passing (10/10)
- ✅ ArangoDB Graph Adapter tests passing
- ✅ StateAbstraction tests passing
- ✅ DataBrain tests passing

**See:** `testing_validation_results.md` for details

---

## Part 2: Holistic Integrated Test Plan

### Test Strategy: Three-Layer Testing

#### Layer 1: Unit Tests (Fast, Isolated)
- **Purpose:** Test business logic in isolation
- **Speed:** < 1 second per test
- **Infrastructure:** Mocked
- **When:** Pure functions, business logic, validation

#### Layer 2: Integration Tests (Real Infrastructure)
- **Purpose:** Test component interactions with real infrastructure
- **Speed:** ~5-10 seconds per test
- **Infrastructure:** Real (docker-compose)
- **When:** Adapter + abstraction flows, infrastructure operations

#### Layer 3: E2E Tests (Full Platform)
- **Purpose:** Test complete user journeys
- **Speed:** ~30-60 seconds per test
- **Infrastructure:** Full docker-compose stack
- **When:** Complete workflows, user scenarios

---

## Part 3: Critical Path Tests (Priority Order) - UPDATED

### Phase 1: Infrastructure Foundation (Week 1, Days 1-2) ✅ COMPLETE

#### Test 1.1: ArangoDB Adapter ✅
- **Status:** ✅ All tests passing (10/10)
- **File:** `tests/integration/infrastructure/test_arango_adapter.py`

#### Test 1.2: ArangoDB Graph Adapter ✅
- **Status:** ✅ All tests passing
- **File:** `tests/integration/infrastructure/test_arango_graph_adapter.py`

#### Test 1.3: StateAbstraction with ArangoDB ✅
- **Status:** ✅ All tests passing
- **File:** `tests/integration/infrastructure/test_state_abstraction.py`

#### Test 1.4: DataBrain with ArangoDB ✅
- **Status:** ✅ All tests passing
- **File:** `tests/integration/infrastructure/test_data_brain.py`

#### Test 1.5: Event Publishing ⏳
- **Status:** ⏳ Pending
- **File:** `tests/integration/infrastructure/test_event_publishing.py`

#### Test 1.6: TransactionalOutbox Integration ⏳
- **Status:** ⏳ Pending
- **File:** `tests/integration/infrastructure/test_transactional_outbox.py`

---

### Phase 2: Runtime Integration (Week 1, Days 3-4)

#### Test 2.1: Runtime Spine ⏳
- **File:** `tests/integration/runtime/test_runtime_spine.py`
- **Tests:**
  - ✅ Runtime initialization
  - ✅ Service discovery (Consul integration)
  - ✅ Health checks
  - ✅ Session creation
  - ✅ Intent submission
  - ✅ Execution lifecycle
  - ✅ Error handling
  - ✅ Cleanup and isolation

#### Test 2.2: Execution Lifecycle ⏳
- **File:** `tests/integration/runtime/test_execution_lifecycle.py`
- **Tests:**
  - ✅ Intent acceptance
  - ✅ Context creation
  - ✅ Handler discovery
  - ✅ Handler execution
  - ✅ Artifact handling
  - ✅ Event publishing
  - ✅ Execution completion
  - ✅ Failure handling
  - ✅ Retry logic
  - ✅ Cleanup and isolation

#### Test 2.3: State Surface ⏳
- **File:** `tests/integration/runtime/test_state_surface.py`
- **Tests:**
  - ✅ Session state management
  - ✅ Execution state management
  - ✅ File reference retrieval
  - ✅ Hot/cold state pattern
  - ✅ State persistence
  - ✅ Error handling
  - ✅ Cleanup and isolation

---

### Phase 3: Realm Integration (Week 1, Days 4-5) - UPDATED

#### Test 3.1: Content Realm ⏳
- **File:** `tests/integration/realms/test_content_realm.py`
- **Tests:**
  - ✅ Realm registration with Runtime
  - ✅ File ingestion intent
  - ✅ File parsing intent
  - ✅ File storage (GCS)
  - ✅ File metadata (Supabase)
  - ✅ Parsing results (all file types)
  - ✅ Preview generation
  - ✅ **Lineage tracking (parsed_results table)** ⭐ NEW
  - ✅ **Embedding tracking (embeddings table)** ⭐ NEW
  - ✅ Error handling
  - ✅ Cleanup and isolation

---

#### Test 3.2: Insights Realm ⏳ - MAJOR UPDATE

**File:** `tests/integration/realms/test_insights_realm.py`

**Phase 1: Data Quality** ⭐ NEW
- ✅ Realm registration with Runtime
- ✅ `assess_data_quality` intent
- ✅ Combined parsing + embedding quality assessment
- ✅ Parsing issue identification
- ✅ Data quality issue identification
- ✅ Source issue identification
- ✅ Root cause analysis
- ✅ Lineage tracking (Supabase)
- ✅ Error handling
- ✅ Cleanup and isolation

**Phase 2: Data Interpretation** ⭐ NEW
- ✅ `interpret_data_self_discovery` intent
  - ✅ Semantic self-discovery (AI determines meaning)
  - ✅ Unconstrained interpretation
  - ✅ Lineage tracking
- ✅ `interpret_data_guided` intent
  - ✅ Guided discovery with default guides (PSO, AAR, Variable Whole Life)
  - ✅ Guided discovery with user-uploaded guides
  - ✅ Guide matching (matched/unmatched/missing)
  - ✅ Suggestions for unmatched fields
  - ✅ Lineage tracking (guide_id in interpretations table)
- ✅ Guide Registry operations
  - ✅ Guide registration
  - ✅ Guide retrieval
  - ✅ Guide listing
- ✅ Error handling
- ✅ Cleanup and isolation

**Phase 3: Business Analysis** ⭐ NEW
- ✅ `analyze_structured_data` intent
  - ✅ Statistical analysis
  - ✅ Pattern analysis
  - ✅ Anomaly detection
  - ✅ Trend analysis
  - ✅ Lineage tracking
- ✅ `analyze_unstructured_data` intent
  - ✅ Semantic analysis
  - ✅ Sentiment analysis
  - ✅ Topic extraction
  - ✅ Entity extraction
  - ✅ Deep dive (Insights Liaison Agent integration)
  - ✅ Lineage tracking (agent_session_id in analyses table)
- ✅ `visualize_lineage` intent ⭐ NEW
  - ✅ Lineage graph generation
  - ✅ Complete pipeline visualization (File → Parsed → Embedding → Interpretation → Analysis)
  - ✅ Guide links visualization
  - ✅ Agent session links visualization
  - ✅ Visual generation (base64 image)
  - ✅ Storage in GCS
- ✅ Error handling
- ✅ Cleanup and isolation

---

#### Test 3.3: Journey Realm ⏳ - UPDATED

**File:** `tests/integration/realms/test_journey_realm.py`

**Tests:**
- ✅ Realm registration with Runtime
- ✅ `create_workflow` intent
  - ✅ Workflow creation from embeddings
  - ✅ **Visual generation** ⭐ NEW
  - ✅ Storage in GCS
- ✅ `generate_sop` intent
  - ✅ SOP generation from workflow
  - ✅ SOP generation from embeddings
  - ✅ **Visual generation** ⭐ NEW
  - ✅ Storage in GCS
- ✅ `generate_sop_from_chat` intent ⭐ NEW
  - ✅ Interactive SOP generation via chat
  - ✅ Journey Liaison Agent integration
  - ✅ Session state management
  - ✅ SOP generation from chat session
  - ✅ **Visual generation** ⭐ NEW
- ✅ `sop_chat_message` intent ⭐ NEW
  - ✅ Chat message processing
  - ✅ Session state updates
  - ✅ Response generation
- ✅ `analyze_coexistence` intent
  - ✅ Coexistence analysis (human+AI)
  - ✅ Optimization opportunities
- ✅ `create_blueprint` intent
  - ✅ Blueprint generation from analysis
- ✅ `create_solution` intent (from blueprint)
  - ✅ Platform journey creation
- ✅ Error handling
- ✅ Cleanup and isolation

---

#### Test 3.4: Outcomes Realm ⏳ - UPDATED

**File:** `tests/integration/realms/test_outcomes_realm.py`

**Tests:**
- ✅ Realm registration with Runtime
- ✅ `synthesize_outcome` intent
  - ✅ Outcome synthesis from all realms
  - ✅ **Summary visual generation** ⭐ NEW
  - ✅ Storage in GCS
- ✅ `generate_roadmap` intent
  - ✅ Roadmap generation
  - ✅ **Roadmap visual generation** ⭐ NEW
  - ✅ Storage in GCS
- ✅ `create_poc` intent
  - ✅ POC proposal generation
  - ✅ **POC visual generation** ⭐ NEW
  - ✅ Storage in GCS
- ✅ `create_solution` intent
  - ✅ Solution creation from roadmap
  - ✅ Solution creation from POC
- ✅ Error handling
- ✅ Cleanup and isolation

---

### Phase 4: Visual Generation Service ⏳ - NEW

#### Test 4.1: Visual Generation Adapter ⏳

**File:** `tests/integration/infrastructure/test_visual_generation_adapter.py`

**Tests:**
- ✅ Workflow visual generation
- ✅ SOP visual generation
- ✅ Summary visual generation
- ✅ Roadmap visual generation
- ✅ POC visual generation
- ✅ Lineage graph visual generation
- ✅ Base64 image conversion
- ✅ Error handling
- ✅ Cleanup and isolation

---

#### Test 4.2: Visual Generation Abstraction ⏳

**File:** `tests/integration/infrastructure/test_visual_generation_abstraction.py`

**Tests:**
- ✅ Visual generation via abstraction
- ✅ Automatic GCS storage
- ✅ File path generation
- ✅ Error handling
- ✅ Cleanup and isolation

---

### Phase 5: Guide Agent & Chat Interface ⏳ - NEW

#### Test 5.1: Guide Agent Core ⏳

**File:** `tests/integration/agentic/test_guide_agent.py`

**Tests:**
- ✅ Guide Agent initialization
- ✅ Intent analysis
  - ✅ Content management intent detection
  - ✅ Data analysis intent detection
  - ✅ Process management intent detection
  - ✅ Solution planning intent detection
  - ✅ Navigation intent detection
- ✅ Journey guidance
  - ✅ Next pillar recommendation
  - ✅ Next action recommendation
  - ✅ Reasoning generation
- ✅ Chat message processing
  - ✅ Response generation
  - ✅ Intent analysis integration
  - ✅ Journey guidance integration
- ✅ Pillar routing
  - ✅ Route to Insights Liaison Agent
  - ✅ Route to Journey Liaison Agent
  - ✅ User state updates
- ✅ User state tracking
  - ✅ Session state management
  - ✅ Conversation history
  - ✅ Journey progress tracking
- ✅ Error handling
- ✅ Cleanup and isolation

---

#### Test 5.2: Guide Agent Service ⏳

**File:** `tests/integration/experience/test_guide_agent_service.py`

**Tests:**
- ✅ Guide Agent Service initialization
- ✅ Intent analysis API
- ✅ Journey guidance API
- ✅ Chat message processing API
- ✅ Conversation history API
- ✅ Pillar routing API
- ✅ Error handling
- ✅ Cleanup and isolation

---

#### Test 5.3: Guide Agent API ⏳

**File:** `tests/integration/experience/test_guide_agent_api.py`

**Tests:**
- ✅ `POST /api/v1/guide-agent/chat` endpoint
- ✅ `POST /api/v1/guide-agent/analyze-intent` endpoint
- ✅ `POST /api/v1/guide-agent/guidance` endpoint
- ✅ `GET /api/v1/guide-agent/history/{session_id}` endpoint
- ✅ `POST /api/v1/guide-agent/route-to-pillar` endpoint
- ✅ Request/response models
- ✅ Error handling (4xx, 5xx)
- ✅ Authentication integration
- ✅ Cleanup and isolation

---

### Phase 6: Architectural Compliance (Week 2, Days 1-2)

#### Test 6.1: 5-Layer Architecture Compliance ⏳
- **File:** `tests/e2e/architectural/test_5_layer_architecture.py`
- **Tests:** (unchanged from original plan)

#### Test 6.2: Public Works Pattern Compliance ⏳
- **File:** `tests/e2e/architectural/test_public_works_pattern.py`
- **Tests:** (unchanged from original plan)

#### Test 6.3: Runtime Participation Contract Compliance ⏳
- **File:** `tests/e2e/architectural/test_runtime_participation_contract.py`
- **Tests:** (unchanged from original plan)

---

### Phase 7: Functional Compliance - MVP Showcase (Week 2, Days 3-4) - UPDATED

#### Test 7.1: Content Pillar (MVP Showcase) ⏳
- **File:** `tests/e2e/functional/test_content_pillar.py`
- **Tests:** (unchanged, but add lineage tracking validation)

---

#### Test 7.2: Insights Pillar (MVP Showcase) ⏳ - MAJOR UPDATE

**File:** `tests/e2e/functional/test_insights_pillar.py`

**Phase 1: Data Quality** ⭐ NEW
- ✅ Quality assessment is generated
- ✅ Combined parsing + embedding analysis
- ✅ Parsing issue identification
- ✅ Data quality issue identification
- ✅ Source issue identification
- ✅ Root cause analysis
- ✅ Lineage tracking (Supabase)

**Phase 2: Data Interpretation** ⭐ NEW
- ✅ Semantic self-discovery works
- ✅ Guided discovery with default guides (PSO, AAR, Variable Whole Life)
- ✅ Guided discovery with user-uploaded guides
- ✅ Guide matching (matched/unmatched/missing)
- ✅ Suggestions for unmatched fields
- ✅ Lineage tracking (guide_id)

**Phase 3: Business Analysis** ⭐ NEW
- ✅ Structured data analysis works
- ✅ Unstructured data analysis works
- ✅ Deep dive (Insights Liaison Agent) works
- ✅ Lineage visualization works ⭐ NEW
  - ✅ Complete pipeline visualization
  - ✅ Guide links visualization
  - ✅ Agent session links visualization
  - ✅ Visual generation and storage

**Legacy Features (Still Valid)**
- ✅ Data mapping feature works (now Lineage Visualization)
- ✅ Virtual pipeline feature works (now Lineage Visualization)

---

#### Test 7.3: Operations Pillar (MVP Showcase) ⏳ - UPDATED

**File:** `tests/e2e/functional/test_operations_pillar.py`

**Tests:**
- ✅ User uploads workflow/SOP file
- ✅ Visual is generated from workflow ⭐ NEW
- ✅ Visual is generated from SOP ⭐ NEW
- ✅ SOP is generated from workflow
- ✅ Workflow is generated from SOP
- ✅ SOP is generated from scratch via chat ⭐ NEW
  - ✅ Chat session initiation
  - ✅ Chat message processing
  - ✅ SOP generation from chat
  - ✅ Visual generation for chat-generated SOP
- ✅ Coexistence analysis works
- ✅ Coexistence blueprint is generated
- ✅ Platform journey is created from blueprint
- ✅ Error handling

---

#### Test 7.4: Business Outcomes Pillar (MVP Showcase) ⏳ - UPDATED

**File:** `tests/e2e/functional/test_business_outcomes_pillar.py`

**Tests:**
- ✅ Summary visual is generated ⭐ NEW
- ✅ Roadmap is generated
- ✅ Roadmap visual is generated ⭐ NEW
- ✅ POC proposal is generated
- ✅ POC visual is generated ⭐ NEW
- ✅ Platform solution is created from roadmap
- ✅ Platform solution is created from POC proposal
- ✅ Error handling

---

#### Test 7.5: Admin Dashboard (MVP Showcase) ⏳
- **File:** `tests/e2e/functional/test_admin_dashboard.py`
- **Tests:** (unchanged from original plan)

---

#### Test 7.6: Chat Interface (MVP Showcase) ⏳ - MAJOR UPDATE

**File:** `tests/e2e/functional/test_chat_interface.py`

**Guide Agent (Global Concierge)** ⭐ NEW
- ✅ Guide agent works
- ✅ Platform navigation guidance
- ✅ User intent analysis
- ✅ Journey guidance
- ✅ Pillar routing
- ✅ User onboarding
- ✅ Solution context understanding

**Pillar Liaison Agents**
- ✅ Insights Liaison Agent works (deep dive analysis)
- ✅ Journey Liaison Agent works (SOP generation via chat)
- ✅ Pillar-specific interactions work
- ✅ Deep dives on analysis (Insights pillar)
- ✅ SOP generation (Operations pillar)

**Chat Flow**
- ✅ Guide Agent → Pillar Liaison Agent routing
- ✅ Conversation history persistence
- ✅ User state tracking
- ✅ Error handling

---

### Phase 8: Extensibility Vision (Week 2, Days 4-5)
- **Tests:** (unchanged from original plan)

---

### Phase 9: Frontend Integration (Week 2, Days 5-6) - UPDATED

#### Test 9.1: API Contracts ⏳
- **File:** `tests/e2e/frontend/test_api_contracts.py`
- **Tests:** (add new endpoints)
  - ✅ Guide Agent API endpoints ⭐ NEW
  - ✅ Lineage visualization API endpoints ⭐ NEW
  - ✅ Visual generation API endpoints ⭐ NEW

#### Test 9.2: WebSocket Streaming ⏳
- **File:** `tests/e2e/frontend/test_websocket_streaming.py`
- **Tests:** (unchanged from original plan)

#### Test 9.3: Authentication Integration ⏳
- **File:** `tests/e2e/frontend/test_authentication.py`
- **Tests:** (unchanged from original plan)

#### Test 9.4: Frontend E2E ⏳
- **File:** `tests/e2e/frontend/test_frontend_e2e.py`
- **Tests:** (add new features)
  - ✅ Guide Agent chat interface ⭐ NEW
  - ✅ Visual generation display ⭐ NEW
  - ✅ Lineage visualization display ⭐ NEW
  - ✅ SOP from chat flow ⭐ NEW

---

### Phase 10: Platform Stability (Week 2, Days 6-7)
- **Tests:** (unchanged from original plan)

---

## Part 4: Test Execution Strategy

### Test Execution Order (UPDATED)

1. **Infrastructure Tests** (Phase 1) ✅ COMPLETE
2. **Runtime Integration Tests** (Phase 2) ⏳ NEXT
3. **Realm Integration Tests** (Phase 3) ⏳ (Updated for new capabilities)
4. **Visual Generation Tests** (Phase 4) ⏳ NEW
5. **Guide Agent Tests** (Phase 5) ⏳ NEW
6. **Architectural Compliance Tests** (Phase 6) ⏳
7. **Functional Compliance Tests** (Phase 7) ⏳ (Updated for new capabilities)
8. **Extensibility Vision Tests** (Phase 8) ⏳
9. **Frontend Integration Tests** (Phase 9) ⏳ (Updated for new endpoints)
10. **Platform Stability Tests** (Phase 10) ⏳

---

## Part 5: Success Criteria (UPDATED)

### Infrastructure Foundation (Phase 1) ✅
- ✅ All infrastructure adapters work with real services
- ✅ StateAbstraction hot/cold pattern works
- ✅ DataBrain persistence works
- ✅ All tests pass reliably

### Runtime Integration (Phase 2) ⏳
- ⏳ Runtime initializes correctly
- ⏳ Execution lifecycle works
- ⏳ State Surface works
- ⏳ All tests pass reliably

### Realm Integration (Phase 3) ⏳
- ⏳ All realms work end-to-end
- ⏳ All intents are handled correctly
- ⏳ **Insights Realm 3-phase flow works** ⭐ NEW
- ⏳ **Lineage tracking works** ⭐ NEW
- ⏳ All tests pass reliably

### Visual Generation (Phase 4) ⏳ NEW
- ⏳ Visual generation works for all types
- ⏳ GCS storage works
- ⏳ All tests pass reliably

### Guide Agent (Phase 5) ⏳ NEW
- ⏳ Guide Agent works correctly
- ⏳ Intent analysis works
- ⏳ Journey guidance works
- ⏳ Pillar routing works
- ⏳ All tests pass reliably

### Architectural Compliance (Phase 6) ⏳
- ⏳ 5-layer architecture is followed
- ⏳ Public Works pattern is followed
- ⏳ Runtime Participation Contract is followed
- ⏳ No architectural violations

### Functional Compliance (Phase 7) ⏳
- ⏳ MVP showcase use case works
- ⏳ All pillars work correctly
- ⏳ **Chat interface works (Guide Agent + Liaison Agents)** ⭐ NEW
- ⏳ **Visual generation works** ⭐ NEW
- ⏳ **Lineage visualization works** ⭐ NEW
- ⏳ Admin dashboard works

### Extensibility Vision (Phase 8) ⏳
- ⏳ Platform handles 350k policies
- ⏳ Legacy system migration works
- ⏳ Multi-tenant isolation works

### Frontend Integration (Phase 9) ⏳
- ⏳ All API contracts match frontend
- ⏳ **Guide Agent API works** ⭐ NEW
- ⏳ **Visual generation API works** ⭐ NEW
- ⏳ WebSocket streaming works
- ⏳ Authentication works
- ⏳ Frontend E2E works

### Platform Stability (Phase 10) ⏳
- ⏳ Error handling is graceful
- ⏳ Recovery works correctly
- ⏳ Performance is acceptable

---

## Part 6: Timeline (UPDATED)

### Week 1: Infrastructure & Core Integration
- **Days 1-2:** ✅ Infrastructure tests (COMPLETE)
- **Days 3-4:** ⏳ Runtime integration tests
- **Days 4-5:** ⏳ Realm integration tests (including new capabilities)

### Week 2: New Features & Compliance
- **Days 1:** ⏳ Visual Generation tests (NEW)
- **Days 1-2:** ⏳ Guide Agent tests (NEW)
- **Days 2-3:** ⏳ Architectural compliance tests
- **Days 3-4:** ⏳ Functional compliance tests (updated for new capabilities)
- **Days 4-5:** ⏳ Extensibility vision tests
- **Days 5-6:** ⏳ Frontend integration tests (updated for new endpoints)
- **Days 6-7:** ⏳ Platform stability tests

### Week 3: Fixes & Documentation
- **Days 1-3:** Fix issues found in testing
- **Days 4-5:** Re-run all tests
- **Days 5-7:** Document what works

---

## Part 7: Key Changes from Original Plan

### New Test Phases
1. **Phase 4: Visual Generation Service** - NEW
2. **Phase 5: Guide Agent & Chat Interface** - NEW

### Updated Test Phases
1. **Phase 3: Realm Integration** - Updated for:
   - Insights Realm 3-phase flow
   - Lineage tracking
   - Visual generation integration
   - SOP from chat

2. **Phase 7: Functional Compliance** - Updated for:
   - Insights Realm new capabilities
   - Visual generation
   - Lineage visualization
   - Guide Agent
   - SOP from chat

3. **Phase 9: Frontend Integration** - Updated for:
   - Guide Agent API endpoints
   - Visual generation API endpoints
   - Lineage visualization API endpoints

### New Test Files Required
- `tests/integration/infrastructure/test_visual_generation_adapter.py`
- `tests/integration/infrastructure/test_visual_generation_abstraction.py`
- `tests/integration/agentic/test_guide_agent.py`
- `tests/integration/experience/test_guide_agent_service.py`
- `tests/integration/experience/test_guide_agent_api.py`
- `tests/e2e/functional/test_chat_interface.py` (updated)

---

## Part 8: Next Steps

1. ✅ **Docker-based testing infrastructure** (COMPLETE)
2. ✅ **Phase 1: Infrastructure tests** (COMPLETE)
3. ⏳ **Phase 2: Runtime integration tests** (NEXT)
4. ⏳ **Phase 3: Realm integration tests** (Updated for new capabilities)
5. ⏳ **Phase 4: Visual Generation tests** (NEW)
6. ⏳ **Phase 5: Guide Agent tests** (NEW)
7. ⏳ **Continue with remaining phases**

---

**Remember:** The goal is to validate the foundation before documenting. Test first, document what works.

**Key Principle:** All new capabilities (Insights Realm 3-phase flow, Visual Generation, Guide Agent, Lineage Visualization) must be tested with real infrastructure before we can confidently document the platform.
