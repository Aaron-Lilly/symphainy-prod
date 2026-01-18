# Insights Pillar Frontend Refactoring Plan

**Date:** January 2026  
**Status:** 📋 **STRATEGIC REFACTORING PLAN**  
**Purpose:** Refactor Insights Pillar frontend to align with new Insights Realm backend architecture, including data lineage visualization

---

## 🎯 Executive Summary

This plan provides a **strategic, pillar-by-pillar refactoring** of the Insights Pillar frontend to:

1. **Align with Insights Realm Backend:**
   - Data Quality assessment (`assess_data_quality`)
   - Data Interpretation (`interpret_data_self_discovery`, `interpret_data_guided`)
   - Business Analysis (`analyze_structured_data`, `analyze_unstructured_data`)
   - **Lineage Visualization** (`visualize_lineage`) - NEW capability

2. **Follow New Architecture Patterns:**
   - Experience Plane Client (not direct API calls)
   - PlatformStateProvider (not GlobalSessionProvider)
   - Runtime-based intent submission
   - Unified WebSocket client

3. **Match Content Pillar Look/Feel:**
   - Consistent UI/UX patterns
   - Similar component structure
   - Same state management approach

---

## 📊 Insights Realm Backend Capabilities

### Intents Supported

**Phase 1: Data Quality**
- `assess_data_quality` - Assess data quality for parsed files

**Phase 2: Data Interpretation**
- `interpret_data_self_discovery` - Self-discovery semantic interpretation
- `interpret_data_guided` - Guided discovery using guides (fact patterns)

**Phase 3: Business Analysis**
- `analyze_structured_data` - Structured data analysis
- `analyze_unstructured_data` - Unstructured data analysis (with optional deep dive via Insights Liaison Agent)

**Lineage Visualization (NEW)**
- `visualize_lineage` - Visualize complete data lineage pipeline (File → Parsed → Embedding → Interpretation → Analysis)

**Legacy/Existing**
- `analyze_content`, `interpret_data`, `map_relationships`, `query_data`, `calculate_metrics`

### Lineage Visualization Details

**What It Shows:**
- Complete pipeline: File → Parsed → Embedding → Interpretation → Analysis
- Guide links (for guided discovery interpretations)
- Agent session links (for deep dive analyses)
- Virtual relationships (from data mash, if any)

**Data Sources:**
- Supabase lineage tables: `parsed_results`, `embeddings`, `interpretations`, `analyses`
- ArangoDB for virtual relationships
- GCS for stored visualization files

**Output:**
- Visual graph (flowchart/diagram) stored in GCS
- Lineage graph data (nodes and edges)
- Complete pipeline metadata

---

## 🏗️ Frontend Architecture

### Current State (Needs Refactoring)

```
Insights Pillar (Current)
├── Multiple API managers (direct calls)
├── GlobalSessionProvider (old pattern)
├── Multiple WebSocket implementations
├── Inconsistent component patterns
└── No lineage visualization
```

### Target State (After Refactoring)

```
Insights Pillar (Refactored)
├── Experience Plane Client (intent submission)
├── PlatformStateProvider (state management)
├── Unified WebSocket Client (real-time updates)
├── InsightsAPIManager (aligned with new architecture)
└── Three Main Sections:
    ├── Data Quality Section
    │   ├── Quality assessment display
    │   └── Semantic embeddings dropdown (userfriendlyfilename_embeddings)
    ├── Data Interpretation Section
    │   ├── Self-discovery results
    │   ├── Guided discovery (with guide selection)
    │   └── Interpretation results display
    ├── Business Analysis Section
    │   ├── Structured analysis results
    │   ├── Unstructured analysis results
    │   └── Deep dive agent integration
    └── Lineage Visualization (NEW)
        ├── Lineage graph visualization
        ├── Pipeline flow display
        └── Guide/Agent session links
```

---

## 📋 Implementation Plan

### Phase 1: Foundation & API Alignment

**1.1 Create InsightsAPIManager**
- **File:** `symphainy-frontend/shared/managers/InsightsAPIManager.ts`
- **Purpose:** API manager for Insights Realm, aligned with Experience Plane Client
- **Methods:**
  - `assessDataQuality(parsedFileId, sourceFileId, parserType)` → submit `assess_data_quality` intent
  - `interpretDataSelfDiscovery(parsedFileId, discoveryOptions)` → submit `interpret_data_self_discovery` intent
  - `interpretDataGuided(parsedFileId, guideId, matchingOptions)` → submit `interpret_data_guided` intent
  - `analyzeStructuredData(parsedFileId, analysisOptions)` → submit `analyze_structured_data` intent
  - `analyzeUnstructuredData(parsedFileId, analysisOptions)` → submit `analyze_unstructured_data` intent
  - `visualizeLineage(fileId)` → submit `visualize_lineage` intent
  - `getDataMashVisualization(fileId)` → retrieve lineage visualization from GCS

**1.2 Update PlatformStateProvider**
- **File:** `symphainy-frontend/shared/state/PlatformStateProvider.tsx`
- **Purpose:** Add Insights realm state structure
- **State Structure:**
  ```typescript
  realm: {
    insights: {
      files: FileMetadata[],
      qualityAssessments: QualityAssessment[],
      interpretations: Interpretation[],
      analyses: Analysis[],
      lineageVisualizations: LineageVisualization[]
    }
  }
  ```

**1.3 Create Insights Hook**
- **File:** `symphainy-frontend/shared/hooks/useInsightsAPIManager.ts`
- **Purpose:** React hook for InsightsAPIManager
- **Pattern:** Similar to `useContentAPIManager`

---

### Phase 2: Component Refactoring

**2.1 Data Quality Section**
- **File:** `symphainy-frontend/app/(protected)/pillars/insights/components/DataQualitySection.tsx`
- **Purpose:** Display data quality assessments
- **Features:**
  - Quality assessment results display
  - Semantic embeddings dropdown (shows `userfriendlyfilename_embeddings`)
  - Quality metrics visualization
  - Integration with Content Pillar for file selection

**2.2 Data Interpretation Section**
- **File:** `symphainy-frontend/app/(protected)/pillars/insights/components/DataInterpretationSection.tsx`
- **Purpose:** Display data interpretation results
- **Features:**
  - Self-discovery results display
  - Guided discovery interface (guide selection)
  - Interpretation results visualization
  - Confidence and coverage scores

**2.3 Business Analysis Section**
- **File:** `symphainy-frontend/app/(protected)/pillars/insights/components/BusinessAnalysisSection.tsx`
- **Purpose:** Display business analysis results
- **Features:**
  - Structured analysis results
  - Unstructured analysis results
  - Deep dive agent integration (Insights Liaison Agent)
  - Analysis visualization

**2.4 Your Data Mash Component (NEW)**
- **File:** `symphainy-frontend/app/(protected)/pillars/insights/components/YourDataMash.tsx`
- **Purpose:** Display complete data lineage pipeline (reimagined "Virtual Data Mapper")
- **Features:**
  - Interactive lineage graph (using React Flow or similar)
  - Pipeline flow visualization (File → Parsed → Embedding → Interpretation → Analysis)
  - Guide links (clickable links to guides)
  - Agent session links (clickable links to agent sessions)
  - Virtual relationships display (from data mash)
  - Export lineage visualization

---

### Phase 3: Main Page Integration

**3.1 Refactor Insights Page**
- **File:** `symphainy-frontend/app/(protected)/pillars/insights/page.tsx`
- **Purpose:** Main Insights Pillar page
- **Structure:**
  ```tsx
  <InsightsPage>
    <InsightsFileSelector /> {/* Select files from Content Pillar */}
    <Tabs>
      <Tab label="Data Quality">
        <DataQualitySection />
      </Tab>
      <Tab label="Data Interpretation">
        <DataInterpretationSection />
      </Tab>
      <Tab label="Your Data Mash">
        <YourDataMash />
      </Tab>
      <Tab label="Business Analysis">
        <BusinessAnalysisSection />
      </Tab>
    </Tabs>
  </InsightsPage>
  ```
  
  **Section Order:**
  1. Data Quality Section
  2. Data Interpretation Section
  3. Your Data Mash (Lineage Visualization) - NEW
  4. Business Analysis Section

**3.2 File Selector Component**
- **File:** `symphainy-frontend/app/(protected)/pillars/insights/components/InsightsFileSelector.tsx`
- **Purpose:** Select files from Content Pillar
- **Features:**
  - Display files from Content Pillar (via PlatformStateProvider)
  - Filter by file type
  - Show parsed file status
  - Link to Content Pillar for file details

---

### Phase 4: Integration & Testing

**4.1 Intent Submission Flow**
- Use Experience Plane Client for all intent submissions
- Handle execution status updates via Unified WebSocket Client
- Update PlatformStateProvider with results

**4.2 State Synchronization**
- Sync Insights realm state with Runtime State Surface
- Handle real-time updates via WebSocket
- Persist state in PlatformStateProvider

**4.3 Error Handling**
- Handle intent submission errors
- Display user-friendly error messages
- Retry logic for failed operations

---

## 🎨 UI/UX Design

### Look & Feel Alignment

**Match Content Pillar:**
- Same card layout patterns
- Same button styles
- Same loading states
- Same error display patterns
- Same file selector UI

**Insights-Specific:**
- Data quality metrics visualization (charts/graphs)
- Interpretation results display (structured data)
- Analysis results display (tables/charts)
- Lineage graph visualization (interactive diagram)

### Component Hierarchy

```
InsightsPage
├── InsightsFileSelector
│   └── File list from Content Pillar
└── Tabs
    ├── Data Quality Tab
    │   └── DataQualitySection
    │       ├── Quality assessment display
    │       └── Semantic embeddings dropdown
    ├── Data Interpretation Tab
    │   └── DataInterpretationSection
    │       ├── Self-discovery results
    │       ├── Guided discovery interface
    │       └── Interpretation results
    ├── Your Data Mash Tab
    │   └── YourDataMash
    │       ├── Interactive lineage graph
    │       ├── Pipeline flow display
    │       └── Guide/Agent session links
    └── Business Analysis Tab
        └── BusinessAnalysisSection
            ├── Structured analysis results
            ├── Unstructured analysis results
            └── Deep dive agent integration
```

---

## 🔧 Technical Implementation Details

### API Manager Pattern

```typescript
class InsightsAPIManager {
  constructor(
    private experienceClient: ExperiencePlaneClient,
    private platformState: PlatformStateProvider
  ) {}

  async assessDataQuality(
    parsedFileId: string,
    sourceFileId: string,
    parserType: string
  ): Promise<QualityAssessment> {
    // Submit assess_data_quality intent via Experience Plane Client
    // Wait for execution completion
    // Update PlatformStateProvider
    // Return quality assessment
  }

  // Similar pattern for other methods
}
```

### State Management Pattern

```typescript
// In PlatformStateProvider
realm: {
  insights: {
    files: FileMetadata[],
    qualityAssessments: Map<string, QualityAssessment>,
    interpretations: Map<string, Interpretation>,
    analyses: Map<string, Analysis>,
    lineageVisualizations: Map<string, LineageVisualization>
  }
}
```

### Intent Submission Pattern

```typescript
// In InsightsAPIManager
const execution = await this.experienceClient.submitIntent({
  intent_type: "assess_data_quality",
  tenant_id: state.session.tenantId,
  session_id: state.session.sessionId,
  solution_id: "default",
  parameters: {
    parsed_file_id: parsedFileId,
    source_file_id: sourceFileId,
    parser_type: parserType
  }
});

// Wait for execution completion via WebSocket
// Update state with results
```

---

## ✅ Success Criteria

1. **Architecture Alignment:**
   - ✅ All API calls go through Experience Plane Client
   - ✅ All state managed via PlatformStateProvider
   - ✅ All WebSocket communication via Unified WebSocket Client
   - ✅ No direct API calls or old patterns

2. **Functionality:**
   - ✅ Data Quality section displays quality assessments
   - ✅ Data Interpretation section supports self-discovery and guided discovery
   - ✅ Your Data Mash displays complete lineage pipeline visualization
   - ✅ Business Analysis section displays structured and unstructured analyses

3. **UI/UX:**
   - ✅ Matches Content Pillar look/feel
   - ✅ Consistent component patterns
   - ✅ Smooth user experience
   - ✅ Clear error handling

4. **Integration:**
   - ✅ Integrates with Content Pillar for file selection
   - ✅ Real-time updates via WebSocket
   - ✅ State synchronization with Runtime

---

## 📝 Implementation Checklist

### Phase 1: Foundation
- [ ] Create InsightsAPIManager
- [ ] Update PlatformStateProvider with Insights state
- [ ] Create useInsightsAPIManager hook
- [ ] Test API manager with Experience Plane Client

### Phase 2: Components
- [ ] Refactor DataQualitySection
- [ ] Refactor DataInterpretationSection
- [ ] Create YourDataMash component (lineage visualization)
- [ ] Refactor BusinessAnalysisSection
- [ ] Create/Update InsightsFileSelector

### Phase 3: Integration
- [ ] Refactor Insights page
- [ ] Integrate all sections
- [ ] Test intent submission flow
- [ ] Test WebSocket updates
- [ ] Test state synchronization

### Phase 4: Polish
- [ ] Match Content Pillar UI/UX
- [ ] Add loading states
- [ ] Add error handling
- [ ] Add user feedback (toasts, notifications)
- [ ] Test end-to-end flow

---

## 🚀 Next Steps

1. **Review this plan** with the team
2. **Start with Phase 1** (Foundation & API Alignment)
3. **Incrementally refactor** each component
4. **Test as we go** (no "break then fix" approach)
5. **Complete all phases** before integration testing

---

**This plan ensures a strategic, pillar-by-pillar refactoring that aligns with the new platform architecture!** 🎯
