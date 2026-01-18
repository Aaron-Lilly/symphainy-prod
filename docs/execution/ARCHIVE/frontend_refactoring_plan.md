# Frontend Refactoring Plan: Aligning with New Platform Architecture

**Date:** January 2026  
**Status:** 🎯 **COMPREHENSIVE PLAN**  
**Purpose:** Holistic frontend refactoring to align with new platform architecture, integrate new capabilities, and complete in-flight work

---

## 🎯 Executive Summary

This plan provides a **comprehensive frontend refactoring strategy** that:

1. **Integrates New Capabilities:**
   - Admin Dashboard (3-view revolutionary front door)
   - Outcomes Realm (Business Outcomes pillar)
   - Journey Realm (renamed from Operations)
   - Runtime-based architecture (Experience → Runtime → Realms)

2. **Completes In-Flight Work:**
   - Insights Realm refactoring (3-way summary UI)
   - Gap analysis remediation (Business Outcomes, Admin Dashboard)

3. **Fixes Architectural Misalignments:**
   - WebSocket consolidation (5+ implementations → 1)
   - API manager alignment (Experience Plane integration)
   - State management consolidation
   - Authentication/authorization flow

4. **Realizes MVP Vision:**
   - 4-pillar journey (Content, Insights, Journey, Outcomes)
   - Guide Agent + Liaison Agents
   - Admin Dashboard showcase
   - Complete platform integration

---

## 📊 Current State Analysis

### Backend Architecture (New Platform) ✅

```
Experience Plane (FastAPI)
├── Session Management (Traffic Cop SDK)
├── Intent Submission (Runtime Client)
├── WebSocket Streaming (Post Office SDK)
└── Admin Dashboard Service
    ├── Control Room View
    ├── Developer View
    └── Business User View

Runtime (FastAPI)
├── Intent Registry
├── Realm Registry (Content, Insights, Journey, Outcomes)
├── Execution Lifecycle Manager
├── State Surface
├── WAL (Redis Streams)
└── Transactional Outbox

Realms (Domain Services)
├── Content Realm (file upload, parsing, embeddings)
├── Insights Realm (data analysis, metrics, visualization)
├── Journey Realm (workflow optimization, SOP generation, coexistence)
└── Outcomes Realm (synthesis, roadmap, POC, solution creation)
```

### Frontend Architecture (Current - Misaligned) ❌

```
Next.js Frontend
├── Multiple WebSocket Implementations (5+)
│   ├── SimpleWebSocketService
│   ├── WebSocketService
│   ├── WebSocketManager
│   ├── SmartCityWebSocketClient
│   └── EnhancedSmartCityWebSocketClient
├── API Managers (8+)
│   ├── ContentAPIManager
│   ├── InsightsAPIManager
│   ├── OperationsAPIManager (needs rename to Journey)
│   ├── BusinessOutcomesAPIManager
│   └── ... (others)
├── State Management (Fragmented)
│   ├── GlobalSessionProvider
│   ├── SessionProvider
│   ├── AppProvider
│   └── AGUIEventProvider
└── Components (Inconsistent Patterns)
    ├── Mock data in components
    ├── Direct API calls (bypassing Experience Plane)
    └── Hardcoded authentication bypass
```

### Key Misalignments

1. **WebSocket Architecture:**
   - ❌ 5+ WebSocket implementations (should be 1)
   - ❌ Wrong endpoint (`/api/ws/agent` instead of `/ws`)
   - ❌ Message format misalignment
   - ❌ No channel-based routing

2. **API Integration:**
   - ❌ Direct backend calls (bypassing Experience Plane)
   - ❌ Inconsistent API manager patterns
   - ❌ No Runtime Client integration
   - ❌ Hardcoded endpoint paths

3. **State Management:**
   - ❌ Multiple overlapping providers
   - ❌ Context errors (AGUIEventProvider)
   - ❌ State fragmentation
   - ❌ No session state synchronization with Runtime

4. **Authentication:**
   - ❌ Hardcoded bypass (`hasSeenWelcome` localStorage)
   - ❌ No Security Guard SDK integration
   - ❌ No proper auth flow

5. **New Capabilities Missing:**
   - ❌ Admin Dashboard UI (3 views)
   - ❌ Outcomes Realm integration
   - ❌ Journey Realm rename (still "Operations")
   - ❌ Runtime-based intent submission

---

## 🎯 Target Architecture

### Frontend Architecture (Target) ✅

```
Next.js Frontend (Port 3000)
├── Unified WebSocket Client
│   ├── Single WebSocket connection to `/ws`
│   ├── Channel-based routing (guide, pillar:content, etc.)
│   ├── Message format: { channel, intent, payload }
│   └── Post Office SDK integration
├── Unified API Client Layer
│   ├── Experience Plane Client
│   │   ├── Session Management (Traffic Cop SDK)
│   │   ├── Intent Submission (Runtime Client)
│   │   └── Admin Dashboard API
│   └── Realm API Clients
│       ├── Content Realm Client
│       ├── Insights Realm Client
│       ├── Journey Realm Client
│       └── Outcomes Realm Client
├── Unified State Management
│   ├── Session State (synced with Runtime)
│   ├── Execution State (from Runtime)
│   ├── Realm State (from State Surface)
│   └── UI State (local)
└── Components (Aligned with Architecture)
    ├── 4-Pillar Journey Pages
    │   ├── Content Pillar
    │   ├── Insights Pillar (3-way summary)
    │   ├── Journey Pillar (renamed from Operations)
    │   └── Outcomes Pillar
    ├── Admin Dashboard (3 views)
    │   ├── Control Room View
    │   ├── Developer View
    │   └── Business User View
    ├── Chat Interfaces
    │   ├── Guide Agent (global concierge)
    │   └── Liaison Agents (per pillar)
    └── Shared Components
        ├── File Uploader
        ├── Data Preview
        ├── Visualization Components
        └── Solution Builder
```

### Integration Flow (Target) ✅

```
Frontend Component
    ↓
Experience Plane Client
    ├── Session Management → Traffic Cop SDK → Runtime
    ├── Intent Submission → Runtime Client → Runtime
    └── Admin Dashboard → Admin Dashboard Service
    ↓
Runtime
    ├── Intent Registry → Route to Realm
    ├── Execution Lifecycle Manager → Execute Intent
    ├── State Surface → Store State
    └── WAL → Log Execution
    ↓
Realm (Content, Insights, Journey, Outcomes)
    ├── Handle Intent
    ├── Use Public Works Abstractions
    └── Return Artifacts + Events
    ↓
Runtime → Experience Plane → Frontend
```

---

## 📋 Refactoring Phases

### Phase 1: Foundation & Architecture Alignment (Week 1-2)

**Goal:** Establish foundation for new architecture

#### 1.1 Unified WebSocket Client
- **Create:** `shared/services/UnifiedWebSocketClient.ts`
  - Single WebSocket connection to `/ws`
  - Channel-based routing: `{ channel: "guide" | "pillar:content", intent: "chat", payload: {...} }`
  - Message format alignment with backend
  - Auto-reconnect logic
  - Connection state management

- **Remove:**
  - `SimpleWebSocketService`
  - `WebSocketService`
  - `WebSocketManager`
  - `SmartCityWebSocketClient`
  - `EnhancedSmartCityWebSocketClient`
  - Direct WebSocket connections in hooks

- **Update:**
  - `useUnifiedAgentChat` → Use `UnifiedWebSocketClient`
  - `GuideAgentProvider` → Use `UnifiedWebSocketClient`
  - Remove deprecated hooks: `useExperienceChat`, `useLiaisonChat`, `useAuthAwareWebSocket`

**Deliverable:** Single WebSocket client, all chat interfaces use it

#### 1.2 Experience Plane Client
- **Create:** `shared/services/ExperiencePlaneClient.ts`
  - Session management (create, get, update)
  - Intent submission (submit intent to Runtime)
  - Execution status (query execution status)
  - WebSocket streaming (via UnifiedWebSocketClient)
  - Error handling and retry logic

- **Integration:**
  - Use Runtime Client for Runtime communication
  - Use Traffic Cop SDK for session coordination
  - Use Post Office SDK for WebSocket coordination

**Deliverable:** Unified Experience Plane client

#### 1.3 State Management Consolidation
- **Create:** `shared/state/PlatformStateProvider.tsx`
  - Session state (synced with Runtime)
  - Execution state (from Runtime)
  - Realm state (from State Surface)
  - UI state (local)

- **Remove:**
  - `GlobalSessionProvider` (consolidate into PlatformStateProvider)
  - `SessionProvider` (consolidate)
  - `AppProvider` (consolidate)
  - Fix `AGUIEventProvider` context errors

- **Integration:**
  - Sync session state with Runtime via Experience Plane Client
  - Sync execution state from Runtime
  - Sync realm state from State Surface

**Deliverable:** Single state provider, no context errors

#### 1.4 Authentication Flow
- **Create:** `shared/auth/AuthProvider.tsx`
  - Login/signup pages
  - Security Guard SDK integration
  - Session management
  - Authorization guards

- **Remove:**
  - `hasSeenWelcome` localStorage bypass
  - Hardcoded authentication bypass

- **Integration:**
  - Use Security Guard SDK for authentication
  - Use Traffic Cop SDK for session coordination
  - Proper auth flow (login → session → access)

**Deliverable:** Proper authentication flow

**Phase 1 Success Criteria:**
- ✅ Single WebSocket client (no duplicates)
- ✅ Experience Plane client created
- ✅ State management consolidated (no context errors)
- ✅ Authentication flow working (no bypass)

---

### Phase 2: Realm Integration & API Alignment (Week 3-4)

**Goal:** Integrate all realms with new architecture

**Note:** This phase refactors existing pillars to align with new backend architecture - we're not rebuilding from scratch, just aligning with the new Runtime-based flow.

#### 2.1 Content Realm Integration
- **Update:** `shared/managers/ContentAPIManager.ts`
  - Use Experience Plane Client
  - Use Runtime-based intent submission
  - Remove direct backend calls
  - Align with Content Realm intents:
    - `ingest_file`
    - `parse_content`
    - `extract_embeddings`
    - `get_parsed_file`
    - `get_semantic_interpretation`

- **Update:** `app/(protected)/pillars/content/page.tsx`
  - Remove mock data
  - Use ContentAPIManager
  - Integrate with Runtime via Experience Plane
  - Show parsed results and semantic interpretation

**Deliverable:** Content Pillar fully integrated with new architecture

#### 2.2 Insights Realm Integration
- **Refactor:** Insights Pillar to match Content Pillar look/feel
  - **Section 1: Data Quality**
    - Dropdown to select file from available semantic embeddings
    - Format: `userfriendlyfilename_embeddings` (e.g., `my_data_file_embeddings`)
    - Query semantic embeddings from Content Realm (via State Surface)
    - Display data quality metrics and recommendations
  - **Section 2: Data Interpretation**
    - Show interpreted data from selected semantic embeddings
    - Display structured/unstructured interpretation results
    - Visualizations and insights
  - **Section 3: Business Analysis**
    - Business-level analysis and recommendations
    - Key insights and actionable recommendations
    - Metrics and KPIs

- **Update:** `shared/managers/InsightsAPIManager.ts`
  - Use Experience Plane Client
  - Use Runtime-based intent submission
  - Align with Insights Realm intents:
    - `analyze_content`
    - `interpret_data`
    - `map_relationships`
    - `query_data`
    - `calculate_metrics`
  - Add method to list available semantic embeddings (from Content Realm)

- **Update:** `app/(protected)/pillars/insights/page.tsx`
  - Refactor to 3-section layout (Data Quality, Data Interpretation, Business Analysis)
  - Match Content Pillar look/feel (similar card structure, layout)
  - Remove complex sections (DataMappingSection, PermitProcessingSection) - simplify
  - Move Insights Liaison Agent to side panel
  - Semantic embeddings dropdown in Data Quality section

- **Create/Update:** `app/(protected)/pillars/insights/components/`
  - `DataQualitySection.tsx` - Update to use semantic embeddings dropdown
  - `DataInterpretationSection.tsx` - New component for data interpretation
  - `BusinessAnalysisSection.tsx` - New component for business analysis
  - Remove or archive: `DataMappingSection.tsx`, `PermitProcessingSection.tsx` (if not needed)

**Deliverable:** Insights Pillar refactored to 3-section layout matching Content Pillar

#### 2.3 Journey Realm Integration (Rename from Operations)
- **Rename:** Operations → Journey
  - `OperationsAPIManager.ts` → `JourneyAPIManager.ts`
  - `app/(protected)/pillars/operation/` → `app/(protected)/pillars/journey/`
  - All references to "Operations" → "Journey"

- **Update:** `shared/managers/JourneyAPIManager.ts`
  - Use Experience Plane Client
  - Use Runtime-based intent submission
  - Align with Journey Realm intents:
    - `optimize_process`
    - `generate_sop`
    - `create_workflow`
    - `analyze_coexistence`
    - `create_blueprint`

- **Update:** `app/(protected)/pillars/journey/page.tsx`
  - Remove mock data
  - Use JourneyAPIManager
  - Show workflow/SOP visualization
  - Show coexistence blueprint
  - Journey Liaison Agent in side panel

**Deliverable:** Journey Pillar renamed and integrated

#### 2.4 Outcomes Realm Integration (Refactor Existing Business Outcomes)
- **Note:** Business Outcomes pillar already exists at `/pillars/business-outcomes/` - refactor, don't rebuild

- **Update:** `shared/managers/BusinessOutcomesAPIManager.ts` (or rename to `OutcomesAPIManager.ts`)
  - Use Experience Plane Client
  - Use Runtime-based intent submission
  - Align with Outcomes Realm intents:
    - `synthesize_outcome`
    - `generate_roadmap`
    - `create_poc`
    - `create_solution`
  - Remove direct backend calls
  - Use Runtime-based intent submission flow

- **Refactor:** `app/(protected)/pillars/business-outcomes/page.tsx`
  - Keep existing structure (tabs, roadmap, POC proposal)
  - Update to use Experience Plane Client
  - Update to use Runtime-based intent submission
  - Align with Outcomes Realm intents
  - Keep existing UI components (InsightsTab, roadmap visualization, etc.)
  - Update Outcomes Liaison Agent integration (use UnifiedWebSocketClient)

- **Standardize Naming:**
  - Option A: Keep "Business Outcomes" (matches existing frontend)
  - Option B: Rename to "Outcomes" (matches backend realm name)
  - **Recommendation:** Keep "Business Outcomes" for frontend consistency, but ensure backend integration uses "outcomes" realm

**Deliverable:** Business Outcomes Pillar refactored to align with Outcomes Realm architecture

**Phase 2 Success Criteria:**
- ✅ All 4 pillars integrated with new architecture
- ✅ No mock data in components
- ✅ All API calls via Experience Plane
- ✅ Journey renamed from Operations
- ✅ Insights Pillar has 3 sections (Data Quality, Data Interpretation, Business Analysis) matching Content Pillar look/feel
- ✅ Business Outcomes Pillar refactored (not rebuilt) to align with Outcomes Realm

---

### Phase 3: Admin Dashboard Implementation (Week 5-6)

**Goal:** Implement revolutionary Admin Dashboard

#### 3.1 Admin Dashboard Structure
- **Create:** `app/(protected)/admin/page.tsx`
  - Main Admin Dashboard page
  - 3-view navigation (Control Room, Developer, Business User)
  - Access control (gated access)

#### 3.2 Control Room View
- **Create:** `app/(protected)/admin/control-room/page.tsx`
  - Platform statistics card
  - Execution metrics card
  - Realm health card
  - Solution registry card
  - System health card

- **Create:** `components/admin/ControlRoom/`
  - `PlatformStatisticsCard.tsx`
  - `ExecutionMetricsCard.tsx`
  - `RealmHealthCard.tsx`
  - `SolutionRegistryCard.tsx`
  - `SystemHealthCard.tsx`

- **Integration:**
  - Use Admin Dashboard API (`/api/admin/control-room/*`)
  - Real-time updates (WebSocket for Phase 2)
  - Query Runtime for realm registry

**Deliverable:** Control Room View complete

#### 3.3 Developer View
- **Create:** `app/(protected)/admin/developer/page.tsx`
  - Platform SDK documentation
  - Code examples
  - Patterns & best practices
  - Solution Builder Playground (gated)
  - Feature submission (gated)

- **Create:** `components/admin/Developer/`
  - `PlatformSDKDocs.tsx`
  - `CodeExamples.tsx`
  - `PatternsBestPractices.tsx`
  - `SolutionBuilderPlayground.tsx` (gated)
  - `FeatureSubmission.tsx` (gated)

- **Integration:**
  - Use Admin Dashboard API (`/api/admin/developer/*`)
  - Gated access for playground and feature submission

**Deliverable:** Developer View complete

#### 3.4 Business User View
- **Create:** `app/(protected)/admin/business/page.tsx`
  - Solution composition guide
  - Solution templates (gated)
  - Advanced solution builder (gated)
  - Feature request system

- **Create:** `components/admin/Business/`
  - `SolutionCompositionGuide.tsx`
  - `SolutionTemplates.tsx` (gated)
  - `AdvancedSolutionBuilder.tsx` (gated)
  - `FeatureRequestSystem.tsx`

- **Integration:**
  - Use Admin Dashboard API (`/api/admin/business/*`)
  - Gated access for templates and advanced builder

**Deliverable:** Business User View complete

**Phase 3 Success Criteria:**
- ✅ Admin Dashboard 3 views implemented
- ✅ All API endpoints integrated
- ✅ Gated access working
- ✅ Solution Builder Playground functional

---

### Phase 4: Chat Interfaces & Agent Integration (Week 7)

**Goal:** Integrate Guide Agent and Liaison Agents

#### 4.1 Guide Agent (Global Concierge)
- **Update:** `components/chat/GuideAgentChat.tsx`
  - Use UnifiedWebSocketClient
  - Channel: `"guide"`
  - Intent: `"chat"`
  - Message format: `{ channel: "guide", intent: "chat", payload: { message, conversation_id } }`

- **Integration:**
  - Landing page integration
  - Global navigation integration
  - Session context awareness

**Deliverable:** Guide Agent fully integrated

#### 4.2 Liaison Agents (Per Pillar)
- **Update:** `components/chat/LiaisonAgentChat.tsx`
  - Use UnifiedWebSocketClient
  - Channel: `"pillar:content" | "pillar:insights" | "pillar:journey" | "pillar:outcomes"`
  - Intent: `"chat"`
  - Message format: `{ channel: "pillar:content", intent: "chat", payload: { message, conversation_id } }`

- **Integration:**
  - Content Pillar side panel
  - Insights Pillar side panel
  - Journey Pillar side panel
  - Outcomes Pillar side panel

**Deliverable:** All Liaison Agents integrated

**Phase 4 Success Criteria:**
- ✅ Guide Agent working on landing page
- ✅ All 4 Liaison Agents working in side panels
- ✅ WebSocket messages correctly formatted
- ✅ Channel-based routing working

---

### Phase 5: Shared Components & Polish (Week 8)

**Goal:** Complete shared components and polish

#### 5.1 Shared Components
- **Update:** `components/shared/FileUploader.tsx`
  - Support all file types (CSV, Excel, PDF, Word, HTML, Image, JSON, Binary)
  - Mainframe binary/copybook support
  - Progress tracking
  - Error handling

- **Update:** `components/shared/DataPreview.tsx`
  - Preview parsed data (parquet, JSON, CSV, etc.)
  - Table view
  - JSON view
  - Chart view (for structured data)

- **Create:** `components/shared/VisualizationComponents.tsx`
  - Chart components (bar, line, pie, etc.)
  - Workflow visualization
  - SOP visualization
  - Roadmap visualization
  - POC proposal display

- **Create:** `components/shared/SolutionBuilder.tsx`
  - Interactive solution builder
  - Solution validation
  - Solution preview
  - Solution registration

**Deliverable:** All shared components complete

#### 5.2 Navigation & Routing
- **Update:** `app/layout.tsx`
  - 4-pillar navigation (Content, Insights, Journey, Outcomes)
  - Admin Dashboard link (gated)
  - Guide Agent access (global)

- **Update:** `app/(protected)/layout.tsx`
  - Side panel for Liaison Agents
  - Session state display
  - Execution status display

**Deliverable:** Navigation and routing complete

#### 5.3 Error Handling & Loading States
- **Create:** `components/shared/ErrorBoundary.tsx`
  - Global error boundary
  - Error display
  - Recovery options

- **Update:** All components
  - Loading states
  - Error states
  - Empty states
  - Success states

**Deliverable:** Error handling and loading states complete

**Phase 5 Success Criteria:**
- ✅ All shared components functional
- ✅ Navigation and routing complete
- ✅ Error handling and loading states implemented
- ✅ MVP showcase ready

---

## 🎯 Integration Points

### Experience Plane → Runtime → Realms

```
Frontend Component
    ↓
Experience Plane Client
    ├── createSession() → Traffic Cop SDK → Runtime /api/session/create
    ├── submitIntent() → Runtime Client → Runtime /api/intent/submit
    └── getExecutionStatus() → Runtime Client → Runtime /api/execution/{id}/status
    ↓
Runtime
    ├── Intent Registry → Route to Realm
    ├── Execution Lifecycle Manager → Execute Intent
    ├── State Surface → Store State
    └── WAL → Log Execution
    ↓
Realm (Content, Insights, Journey, Outcomes)
    ├── handle_intent(intent, context)
    ├── Use Public Works Abstractions
    └── Return { artifacts, events }
    ↓
Runtime → Experience Plane → Frontend
```

### WebSocket Flow

```
Frontend Component
    ↓
UnifiedWebSocketClient
    ├── Connect to /ws
    ├── Send: { channel: "guide" | "pillar:content", intent: "chat", payload: {...} }
    └── Receive: { type, message, agent_type, pillar, conversation_id, data, timestamp }
    ↓
Post Office SDK (Backend)
    ├── Route by channel
    ├── Guide Agent → Guide Agent
    └── Pillar:Content → Content Liaison Agent
    ↓
Agent Response → Post Office SDK → UnifiedWebSocketClient → Frontend
```

### Admin Dashboard Flow

```
Frontend Component
    ↓
Admin Dashboard API Client
    ├── GET /api/admin/control-room/statistics
    ├── GET /api/admin/control-room/execution-metrics
    ├── GET /api/admin/control-room/realm-health
    └── GET /api/admin/control-room/solution-registry
    ↓
Admin Dashboard Service (Experience Plane)
    ├── Control Room Service → Query Runtime, Solution Registry
    ├── Developer View Service → Platform SDK docs
    └── Business User View Service → Solution composition
    ↓
Data Sources
    ├── Runtime (execution metrics, realm registry)
    ├── Solution Registry (solution status)
    ├── State Surface (session/execution state)
    └── Public Works (infrastructure health)
```

---

## 📊 Success Metrics

### Phase 1: Foundation
- ✅ Single WebSocket client (0 duplicates)
- ✅ Experience Plane client created
- ✅ State management consolidated (0 context errors)
- ✅ Authentication flow working (0 bypasses)

### Phase 2: Realm Integration
- ✅ All 4 pillars integrated (Content, Insights, Journey, Outcomes)
- ✅ 0 mock data in components
- ✅ 100% API calls via Experience Plane
- ✅ Journey renamed from Operations

### Phase 3: Admin Dashboard
- ✅ 3 views implemented (Control Room, Developer, Business User)
- ✅ All API endpoints integrated
- ✅ Gated access working
- ✅ Solution Builder Playground functional

### Phase 4: Chat Interfaces
- ✅ Guide Agent working on landing page
- ✅ All 4 Liaison Agents working in side panels
- ✅ WebSocket messages correctly formatted
- ✅ Channel-based routing working

### Phase 5: Polish
- ✅ All shared components functional
- ✅ Navigation and routing complete
- ✅ Error handling and loading states implemented
- ✅ MVP showcase ready

---

## 🚀 Implementation Strategy

### Incremental Approach
1. **Phase 1** → Foundation (no breaking changes to existing features)
2. **Phase 2** → Realm integration (one pillar at a time)
3. **Phase 3** → Admin Dashboard (new feature, no breaking changes)
4. **Phase 4** → Chat interfaces (update existing, no breaking changes)
5. **Phase 5** → Polish (enhancements, no breaking changes)

### Testing Strategy
- **Unit Tests:** Each component/service
- **Integration Tests:** Experience Plane → Runtime → Realm flow
- **E2E Tests:** Complete user journeys (4-pillar journey, Admin Dashboard)
- **WebSocket Tests:** Message format, channel routing, reconnection

### Rollback Plan
- Keep old implementations until new ones are tested
- Feature flags for new features
- Gradual migration (one pillar at a time)

---

## 📝 Dependencies

### Backend Dependencies
- ✅ Experience Plane API endpoints (already implemented)
- ✅ Runtime API endpoints (already implemented)
- ✅ Admin Dashboard API endpoints (already implemented)
- ✅ Realm intents (already implemented)
- ✅ WebSocket gateway (`/ws` endpoint)

### Frontend Dependencies
- ✅ Next.js framework
- ✅ React hooks
- ✅ TypeScript
- ✅ WebSocket client library
- ✅ HTTP client library (fetch or axios)

---

## 🎉 Expected Outcomes

### User Experience
- **Seamless 4-Pillar Journey:** Content → Insights → Journey → Outcomes
- **Revolutionary Admin Dashboard:** 3 views with gated access
- **Intelligent Chat:** Guide Agent + 4 Liaison Agents
- **Real-time Updates:** WebSocket streaming for execution status

### Technical Excellence
- **Single WebSocket Client:** No duplicates, consistent message format
- **Unified API Layer:** All calls via Experience Plane
- **Consolidated State:** Single source of truth, no context errors
- **Proper Authentication:** Security Guard SDK integration

### Platform Showcase
- **Complete MVP:** All requirements from `mvp_showcase_description.md`
- **Admin Dashboard:** Revolutionary 3-view front door
- **Realm Integration:** All 4 realms fully integrated
- **Agent Integration:** Guide + 4 Liaison Agents

---

## 📚 Reference Documents

### New Capabilities
- `docs/execution/admin_dashboard_vision.md` - Admin Dashboard vision
- `docs/execution/admin_dashboard_complete.md` - Admin Dashboard implementation
- `docs/execution/realm_implementation_plan.md` - Realm implementation plan
- `docs/execution/mvp_gap_analysis_business_outcomes_admin_dashboard.md` - Gap analysis

### In-Flight Work
- `symphainy_source/docs/11-11/INSIGHTS_PILLAR_INTEGRATED_REFACTORING_PLAN.md` - Insights refactoring
- `symphainy_source/docs/FRONTEND_ARCHITECTURAL_REVIEW.md` - Frontend review

### Original Work
- `z_docs/FRONTEND_REFACTORING_PLAN.md` - Original refactoring plan
- `z_docs/FRONTEND_ARCHITECTURAL_ANALYSIS.md` - Architectural analysis
- `docs/platform_use_cases/mvp_showcase_description.md` - MVP requirements

---

## 🎯 Next Steps

1. **Review & Approve:** This comprehensive plan
2. **Start Phase 1:** Foundation & Architecture Alignment
3. **Incremental Implementation:** One phase at a time
4. **Continuous Testing:** Test each phase thoroughly
5. **MVP Showcase:** Complete all phases for MVP

---

**This plan brings together all the pieces to create a revolutionary frontend that fully showcases our new platform architecture!** 🚀
