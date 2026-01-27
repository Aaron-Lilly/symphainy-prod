# Platform Capability Showcase - Implementation Plan

**Date:** January 25, 2026  
**Status:** 📋 **IMPLEMENTATION PLAN**  
**Purpose:** Align frontend UI with backend platform vision to showcase Coexistence Fabric capabilities

---

## Executive Summary

This plan implements frontend enhancements to showcase the Symphainy platform's core capabilities: **Coexistence Fabric**, **Multi-Agent Collaboration**, **Artifact Plane**, and **Intent-Based Execution**. All changes build upon the solid foundation established in Phases 0-4.

**Key Principle:** Enhance the UI to showcase platform capabilities **without undermining** the architectural patterns established in Phases 0-4:
- ✅ Session-First architecture (SessionBoundaryProvider)
- ✅ Intent-based API (all operations through Runtime)
- ✅ PlatformStateProvider for state management
- ✅ Runtime as authoritative source of truth
- ✅ Policy in Civic Systems (Data Steward)

---

## Architectural Constraints & Principles

### Must Preserve (Phases 0-4 Foundation)

1. **Session-First Architecture**
   - All components use `SessionBoundaryProvider` for session state
   - Session state is hidden from users (just works)
   - No direct session manipulation in components

2. **Intent-Based API**
   - All operations use `submitIntent()` from PlatformStateProvider
   - No legacy endpoint calls in components
   - Execution flows through Runtime/ExecutionLifecycleManager

3. **PlatformStateProvider**
   - State management via `usePlatformState()`
   - Realm state via `getRealmState()` / `setRealmState()`
   - State persistence deferred to Phase 5 (frontend-only continuity for now)

4. **Runtime Authority**
   - Runtime is authoritative source of truth
   - Frontend submits to backend authority
   - No state divergence between frontend and backend

5. **Policy in Civic Systems**
   - Boundary contracts assigned by Data Steward (Civic Systems)
   - No policy definition in Public Works or Runtime
   - Governance decisions in Civic Systems

### Must Enhance (Platform Capability Showcase)

1. **Multi-Agent Collaboration**
   - Guide Agent: Persistent element on right side
   - Liaison Agents: Show when active, display domain expertise
   - Agent collaboration indicators

2. **Artifact Plane**
   - Artifact gallery on landing page
   - Artifact lifecycle (admin-only, but data mash lineage showcases it)
   - Purpose-Bound Outcomes prominently displayed

3. **Coexistence Fabric**
   - Coexistence explanation in UI (landing, journey, outcomes)
   - Boundary-crossing workflows visible
   - Integration points displayed

4. **Governance & Auditability**
   - Execution tracking (admin-only)
   - Audit trail (admin-only)
   - Lineage tracking (visible via data mash)

---

## Advanced Capabilities Recommendations

Based on platform architecture and user feedback, here are the highest-priority advanced capabilities to showcase:

### Priority 1: High-Impact, Low-Effort
1. **Lineage Visualization Enhancement** (Insights Pillar)
   - Make "Your Data Mash" more prominent and interactive
   - Show data flow from source to insights
   - Display lineage graph with exploration capabilities

2. **Process Optimization** (Journey Pillar)
   - Add "Optimize Process" button
   - Show optimization recommendations
   - Display before/after comparisons

3. **Relationship Mapping** (Insights Pillar)
   - Add relationship mapping interface
   - Show entity-relationship graphs
   - Allow relationship exploration

### Priority 2: High-Impact, Medium-Effort
1. **Artifact Library** (Landing Page)
   - Create dedicated artifact library page
   - Show all Purpose-Bound Outcomes (roadmaps, POCs, blueprints, SOPs)
   - Allow artifact filtering and search

2. **Cross-Pillar Synthesis Visibility** (Outcomes Pillar)
   - Show which pillars contributed to synthesis
   - Display synthesis inputs (files, insights, workflows)
   - Show synthesis lineage

3. **Lifecycle Management** (Content Pillar)
   - Add "File Lifecycle" view
   - Show archived files
   - Allow restore/purge operations

### Priority 3: Medium-Impact, High-Effort
1. **Advanced Search & Query** (All Pillars)
   - Add advanced search/query interfaces
   - Show query results with metadata
   - Allow complex queries

2. **Solution Builder** (Admin Dashboard - Business User View)
   - Visual solution composition interface
   - Solution templates
   - Solution gallery

3. **SDK Playground** (Admin Dashboard - Developer View)
   - Interactive intent testing
   - API contracts display
   - Intent registry browser

**Note:** Execution status and bulk operations are deferred per user feedback.

---

## Implementation Phases

### Phase 1: Foundation & Agent Visibility (High-Impact, Low-Effort)

**Goal:** Make agents prominent and showcase multi-agent collaboration

**Tasks:**

#### 1.1: Enhance Guide Agent Visibility
- **Location:** All pages (persistent right-side element)
- **Changes:**
  - Ensure Guide Agent is always visible on right side
  - Add "Ask me anything about the platform" prompt
  - Show quick start suggestions
  - Display agent activity indicator

**Files to Modify:**
- `shared/components/MainLayout.tsx` (or equivalent layout component)
- Agent chat component (ensure persistent positioning)

**Architectural Compliance:**
- ✅ Uses existing agent infrastructure
- ✅ No changes to Session-First or intent-based patterns
- ✅ Preserves PlatformStateProvider usage

---

#### 1.2: Enhance Liaison Agent Indicators
- **Location:** Each pillar page
- **Changes:**
  - Show which Liaison Agent is active
  - Display agent domain expertise
  - Show agent suggestions prominently
  - Add "Ask [Agent Name]" buttons

**Files to Modify:**
- `app/(protected)/pillars/content/page.tsx`
- `app/(protected)/pillars/insights/page.tsx`
- `app/(protected)/pillars/journey/page.tsx`
- `app/(protected)/pillars/business-outcomes/page.tsx`

**Architectural Compliance:**
- ✅ Uses existing `setChatbotAgentInfo` from PlatformStateProvider
- ✅ No changes to agent infrastructure
- ✅ Preserves intent-based API patterns

---

#### 1.3: Add Agent Collaboration Indicators
- **Location:** When multiple agents collaborate
- **Changes:**
  - Show when Guide Agent and Liaison Agent collaborate
  - Display collaboration activity
  - Show agent handoffs

**Files to Modify:**
- Agent chat component
- PlatformStateProvider (if needed for collaboration state)

**Architectural Compliance:**
- ✅ Uses existing agent infrastructure
- ✅ No changes to execution patterns

---

### Phase 2: Artifact Plane Showcase (High-Impact, Medium-Effort)

**Goal:** Prominently display Purpose-Bound Outcomes and artifact lifecycle

**Tasks:**

#### 2.1: Create Artifact Gallery on Landing Page
- **Location:** `app/(protected)/page.tsx`
- **Changes:**
  - Add "Artifact Gallery" section
  - Display recent artifacts (roadmaps, POCs, blueprints, SOPs)
  - Show artifact cards with status badges
  - Allow artifact filtering by type
  - Link to artifact details

**Implementation:**
- Use `getRealmState()` to retrieve artifacts from realm states
- Display artifacts from Outcomes realm (roadmaps, POCs, blueprints)
- Display artifacts from Journey realm (SOPs, workflows)
- Show artifact metadata (created date, status, type)

**Files to Create:**
- `components/landing/ArtifactGallery.tsx`
- `components/landing/ArtifactCard.tsx`

**Files to Modify:**
- `app/(protected)/page.tsx`

**Architectural Compliance:**
- ✅ Uses `getRealmState()` from PlatformStateProvider
- ✅ Artifacts retrieved from realm state (no direct API calls)
- ✅ No changes to intent-based patterns
- ✅ Preserves Session-First architecture

---

#### 2.2: Create Dedicated Artifact Library Page
- **Location:** New page `/artifacts` or section in landing page
- **Changes:**
  - Show all Purpose-Bound Outcomes
  - Allow filtering by type (roadmap, POC, blueprint, SOP)
  - Allow search by name/description
  - Show artifact status (draft, active, archived)
  - Link to artifact details

**Implementation:**
- Aggregate artifacts from all realms
- Use `getRealmState()` for each realm
- Display in organized grid/list view
- Add filtering and search UI

**Files to Create:**
- `app/(protected)/artifacts/page.tsx`
- `components/artifacts/ArtifactLibrary.tsx`
- `components/artifacts/ArtifactFilter.tsx`

**Architectural Compliance:**
- ✅ Uses PlatformStateProvider for state
- ✅ No direct API calls
- ✅ Preserves intent-based patterns

---

#### 2.3: Enhance Artifact Display in Outcomes Pillar
- **Location:** `app/(protected)/pillars/business-outcomes/page.tsx`
- **Changes:**
  - Make artifact gallery more prominent
  - Show artifact lifecycle (draft → active → archived)
  - Display artifact relationships
  - Show which pillars contributed to synthesis

**Implementation:**
- Enhance existing artifact display components
- Add lifecycle status badges
- Show synthesis inputs from other pillars
- Display artifact metadata

**Files to Modify:**
- `app/(protected)/pillars/business-outcomes/page.tsx`
- `app/(protected)/pillars/business-outcomes/components/GeneratedArtifactsDisplay.tsx`

**Architectural Compliance:**
- ✅ Uses existing artifact retrieval patterns
- ✅ No changes to intent-based API
- ✅ Preserves Session-First architecture

---

### Phase 3: Coexistence Fabric Showcase (High-Impact, Medium-Effort)

**Goal:** Explain and showcase the Coexistence Fabric concept

**Tasks:**

#### 3.1: Add Coexistence Explanation to Landing Page
- **Location:** `app/(protected)/page.tsx`
- **Changes:**
  - Add "What is Coexistence?" section
  - Explain how platform coordinates boundary-crossing work
  - Show visual diagram of coexistence fabric
  - Link to journey pillar for coexistence analysis

**Implementation:**
- Create informational component
- Add visual diagram (can be static or interactive)
- Explain key concepts: boundary-crossing, coordination, governance

**Files to Create:**
- `components/landing/CoexistenceExplanation.tsx`
- `components/landing/CoexistenceDiagram.tsx`

**Files to Modify:**
- `app/(protected)/page.tsx`

**Architectural Compliance:**
- ✅ Informational only (no API calls)
- ✅ No changes to execution patterns

---

#### 3.2: Enhance Coexistence Analysis in Journey Pillar
- **Location:** `app/(protected)/pillars/journey/page.tsx`
- **Changes:**
  - Make coexistence analysis more prominent
  - Explain coexistence concept in context
  - Show how SOP and workflow coexist
  - Display coexistence analysis results prominently

**Implementation:**
- Add explanation section before coexistence analysis
- Enhance coexistence analysis results display
- Show dual views (SOP ↔ Workflow)
- Display boundary-crossing indicators

**Files to Modify:**
- `app/(protected)/pillars/journey/page.tsx`
- `app/(protected)/pillars/journey/components/CoexistenceBlueprint/index.tsx`

**Architectural Compliance:**
- ✅ Uses existing `analyze_coexistence` intent
- ✅ No changes to intent-based patterns
- ✅ Preserves Session-First architecture

---

#### 3.3: Add Coexistence Context to Outcomes Pillar
- **Location:** `app/(protected)/pillars/business-outcomes/page.tsx`
- **Changes:**
  - Show how synthesis crosses boundaries
  - Display integration points
  - Show cross-pillar coordination

**Implementation:**
- Add visual showing cross-pillar synthesis
- Display which pillars contributed
- Show boundary-crossing in synthesis flow

**Files to Modify:**
- `app/(protected)/pillars/business-outcomes/page.tsx`
- `app/(protected)/pillars/business-outcomes/components/SummaryVisualization.tsx`

**Architectural Compliance:**
- ✅ Uses existing synthesis intents
- ✅ No changes to execution patterns

---

### Phase 4: Advanced Capabilities (Priority 1)

**Goal:** Showcase high-impact advanced capabilities

**Tasks:**

#### 4.1: Enhance Lineage Visualization (Insights Pillar)
- **Location:** `app/(protected)/pillars/insights/components/YourDataMash.tsx`
- **Changes:**
  - Make "Your Data Mash" more prominent
  - Add interactive lineage graph
  - Show data flow from source to insights
  - Allow exploration of lineage paths
  - Display lineage metadata

**Implementation:**
- Enhance existing lineage visualization component
- Use `visualize_lineage` intent results
- Add interactive graph library (e.g., D3.js, vis.js)
- Show data flow animations

**Files to Modify:**
- `app/(protected)/pillars/insights/components/YourDataMash.tsx`
- `app/(protected)/pillars/insights/page.tsx` (make tab more prominent)

**Architectural Compliance:**
- ✅ Uses existing `visualize_lineage` intent
- ✅ No changes to intent-based patterns
- ✅ Preserves Session-First architecture

---

#### 4.2: Add Process Optimization (Journey Pillar)
- **Location:** `app/(protected)/pillars/journey/page.tsx`
- **Changes:**
  - Add "Optimize Process" button
  - Show optimization recommendations
  - Display before/after comparisons
  - Allow applying optimizations

**Implementation:**
- Use `optimize_process` intent
- Display optimization results
- Show metrics (efficiency gain, time savings, cost reduction)
- Allow user to apply optimizations

**Files to Modify:**
- `app/(protected)/pillars/journey/page.tsx`
- Create: `app/(protected)/pillars/journey/components/ProcessOptimization.tsx`

**Architectural Compliance:**
- ✅ Uses existing `optimize_process` intent
- ✅ No changes to intent-based patterns
- ✅ Preserves Session-First architecture

---

#### 4.3: Add Relationship Mapping (Insights Pillar)
- **Location:** `app/(protected)/pillars/insights/page.tsx`
- **Changes:**
  - Add "Relationship Mapping" tab or section
  - Show entity-relationship graphs
  - Allow relationship exploration
  - Display relationship metadata

**Implementation:**
- Use `map_relationships` intent
- Create relationship graph visualization
- Allow interactive exploration
- Show relationship types and confidence scores

**Files to Create:**
- `app/(protected)/pillars/insights/components/RelationshipMapping.tsx`
- `app/(protected)/pillars/insights/components/RelationshipGraph.tsx`

**Files to Modify:**
- `app/(protected)/pillars/insights/page.tsx`

**Architectural Compliance:**
- ✅ Uses existing `map_relationships` intent
- ✅ No changes to intent-based patterns
- ✅ Preserves Session-First architecture

---

### Phase 5: Admin Dashboard Enhancements (Admin-Only)

**Goal:** Showcase governance and platform observability (admin-only)

**Tasks:**

#### 5.1: Enhance Control Room (Admin Dashboard)
- **Location:** `app/(protected)/admin/components/ControlRoomView.tsx`
- **Changes:**
  - Show real-time execution tracking
  - Display intent submission rates
  - Show realm activity
  - Display session state (admin view)
  - Show audit trail

**Implementation:**
- Create execution monitoring components
- Use admin-only API endpoints (if available)
- Display real-time metrics
- Show execution logs

**Files to Modify:**
- `app/(protected)/admin/components/ControlRoomView.tsx`
- Create: `app/(protected)/admin/components/ExecutionMonitor.tsx`
- Create: `app/(protected)/admin/components/AuditTrail.tsx`

**Architectural Compliance:**
- ✅ Admin-only features (no impact on user experience)
- ✅ Uses admin API endpoints (separate from user intents)

---

#### 5.2: Enhance Developer View (Admin Dashboard)
- **Location:** `app/(protected)/admin/components/DeveloperView.tsx`
- **Changes:**
  - Show Platform SDK documentation
  - Add SDK playground (interactive intent testing)
  - Show API contracts
  - Display intent registry
  - Show realm capabilities

**Implementation:**
- Create SDK documentation viewer
- Create interactive intent testing interface
- Display intent registry from backend
- Show API contracts

**Files to Modify:**
- `app/(protected)/admin/components/DeveloperView.tsx`
- Create: `app/(protected)/admin/components/SDKPlayground.tsx`
- Create: `app/(protected)/admin/components/IntentRegistry.tsx`

**Architectural Compliance:**
- ✅ Admin-only features
- ✅ Uses existing intent infrastructure for playground

---

#### 5.3: Enhance Business User View (Admin Dashboard)
- **Location:** `app/(protected)/admin/components/BusinessUserView.tsx`
- **Changes:**
  - Show solution composition interface
  - Display solution templates
  - Show feature requests
  - Display solution gallery

**Implementation:**
- Create solution composition UI
- Display solution templates
- Show feature request management
- Create solution gallery

**Files to Modify:**
- `app/(protected)/admin/components/BusinessUserView.tsx`
- Create: `app/(protected)/admin/components/SolutionBuilder.tsx`
- Create: `app/(protected)/admin/components/SolutionTemplates.tsx`

**Architectural Compliance:**
- ✅ Admin-only features
- ✅ Uses existing solution creation intents

---

### Phase 6: Content Pillar Enhancements (Medium-Priority)

**Goal:** Showcase advanced content capabilities (teased, not in demo flow)

**Tasks:**

#### 6.1: Add Bulk Operations Teaser (Content Pillar)
- **Location:** `app/(protected)/pillars/content/page.tsx`
- **Changes:**
  - Add "What We Need From Users" section
  - Tease bulk operations capability
  - Explain when bulk operations would be useful
  - Link to future implementation

**Implementation:**
- Create informational component
- Explain bulk operations use cases
- Show placeholder for future implementation

**Files to Create:**
- `app/(protected)/pillars/content/components/BulkOperationsTeaser.tsx`

**Files to Modify:**
- `app/(protected)/pillars/content/page.tsx`

**Architectural Compliance:**
- ✅ Informational only (no implementation)
- ✅ No changes to execution patterns

---

#### 6.2: Add Lifecycle Management (Content Pillar)
- **Location:** `app/(protected)/pillars/content/components/FileDashboard.tsx`
- **Changes:**
  - Add "File Lifecycle" view/tab
  - Show archived files
  - Allow restore/purge operations
  - Display file status (active, archived, purged)

**Implementation:**
- Use `archive_file`, `restore_file`, `purge_file` intents
- Create lifecycle management UI
- Show file status indicators
- Allow lifecycle operations

**Files to Modify:**
- `app/(protected)/pillars/content/components/FileDashboard.tsx`
- Create: `app/(protected)/pillars/content/components/FileLifecycle.tsx`

**Architectural Compliance:**
- ✅ Uses existing lifecycle intents
- ✅ No changes to intent-based patterns
- ✅ Preserves Session-First architecture

---

## Implementation Order & Dependencies

### Recommended Sequence

1. **Phase 1: Foundation & Agent Visibility** (Start here)
   - Low risk, high impact
   - Establishes multi-agent collaboration showcase
   - No architectural changes

2. **Phase 2: Artifact Plane Showcase**
   - Builds on Phase 1
   - Showcases Purpose-Bound Outcomes
   - Uses existing realm state

3. **Phase 3: Coexistence Fabric Showcase**
   - Builds on Phases 1-2
   - Explains platform concept
   - Enhances existing features

4. **Phase 4: Advanced Capabilities (Priority 1)**
   - Builds on Phases 1-3
   - Showcases high-impact capabilities
   - Uses existing intents

5. **Phase 5: Admin Dashboard Enhancements**
   - Can be done in parallel with other phases
   - Admin-only, no impact on user experience

6. **Phase 6: Content Pillar Enhancements**
   - Lower priority
   - Can be done incrementally

---

## Testing Strategy

### Per-Phase Validation

**After Each Phase:**
1. ✅ **Functional Testing**: Does the feature work as intended?
2. ✅ **Architectural Testing**: Does it follow platform principles?
3. ✅ **Regression Testing**: Re-run Phase 3 E2E tests

### Validation Checklist

**Architectural Compliance:**
- [ ] Uses SessionBoundaryProvider for session state
- [ ] Uses PlatformStateProvider for state management
- [ ] Uses `submitIntent()` for all operations
- [ ] No legacy endpoint calls in components
- [ ] Runtime is authoritative source of truth
- [ ] No policy definition in Public Works or Runtime

**Platform Capability Showcase:**
- [ ] Agents prominently featured
- [ ] Artifacts prominently displayed
- [ ] Coexistence concept explained
- [ ] Advanced capabilities showcased
- [ ] Governance visible (admin-only)

---

## Success Criteria

### Phase 1 Success
- ✅ Guide Agent always visible on right side
- ✅ Liaison Agents show when active
- ✅ Agent collaboration indicators visible
- ✅ No regressions in existing functionality

### Phase 2 Success
- ✅ Artifact gallery on landing page
- ✅ Artifact library page created
- ✅ Artifacts prominently displayed in Outcomes pillar
- ✅ No regressions in existing functionality

### Phase 3 Success
- ✅ Coexistence explanation on landing page
- ✅ Coexistence analysis prominent in Journey pillar
- ✅ Coexistence context in Outcomes pillar
- ✅ No regressions in existing functionality

### Phase 4 Success
- ✅ Lineage visualization enhanced
- ✅ Process optimization exposed
- ✅ Relationship mapping added
- ✅ No regressions in existing functionality

### Overall Success
- ✅ Platform capabilities prominently showcased
- ✅ No architectural patterns undermined
- ✅ All Phase 3 E2E tests still passing
- ✅ User experience enhanced
- ✅ Platform vision clearly communicated

---

## Risk Mitigation

### Architectural Risks

**Risk:** Changes might undermine Session-First architecture
**Mitigation:** All changes use existing SessionBoundaryProvider patterns

**Risk:** Changes might introduce legacy endpoint calls
**Mitigation:** All operations use `submitIntent()` from PlatformStateProvider

**Risk:** Changes might break Runtime authority
**Mitigation:** No direct state manipulation, all state via PlatformStateProvider

### Implementation Risks

**Risk:** Agent visibility changes might break existing agent infrastructure
**Mitigation:** Use existing agent infrastructure, no changes to agent logic

**Risk:** Artifact gallery might not have data
**Mitigation:** Use `getRealmState()` to retrieve artifacts, handle empty state gracefully

**Risk:** Coexistence explanation might be too technical
**Mitigation:** Use clear, user-friendly language with visual aids

---

## Implementation Decisions

**Confirmed Decisions:**

1. **Agent Positioning**: Fixed right-side panel with toggle between Guide and Liaison (keep current pattern)
2. **Artifact Gallery Size**: Start with 6 artifacts, with "Show All" option
3. **Coexistence Diagram**: Static diagram for MVP
4. **Lineage Visualization**: **react-flow** (recommended - React-native, well-suited for flow/lineage diagrams, easy to integrate)
5. **Process Optimization**: User-initiated (user clicks to start optimization/coexistence analysis/blueprint)

---

**Prepared By:** Development Team  
**Date:** January 25, 2026  
**Status:** 📋 **READY FOR IMPLEMENTATION - DECISIONS CONFIRMED**
