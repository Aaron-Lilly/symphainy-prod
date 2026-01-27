# Phase 4 Comprehensive Migration Plan - 100% Frontend Coverage

**Date:** January 25, 2026  
**Status:** ⚠️ **IN PROGRESS**  
**Goal:** Migrate ALL frontend components to intent-based API

---

## Executive Summary

Phase 4 requires **100% complete and total coverage** of everything in the frontend. This document provides a comprehensive plan to migrate all components across all pillars, admin dashboard, login, and landing pages.

**Scope:**
- ✅ Content Pillar (COMPLETE)
- ⚠️ Insights Pillar (PENDING)
- ⚠️ Journey/Operations Pillar (PENDING)
- ⚠️ Outcomes/Business Outcomes Pillar (PARTIAL - handlers done, components pending)
- ⚠️ Admin Dashboard (PENDING)
- ⚠️ Login Page (PENDING)
- ⚠️ Landing Page (PENDING)

---

## Migration Status by Area

### ✅ Content Pillar - COMPLETE
**Status:** ✅ **100% COMPLETE**

**Files Migrated:**
- ✅ ContentPillarUpload.tsx
- ✅ FileDashboard.tsx
- ✅ DataMash.tsx
- ✅ ParsePreview.tsx
- ✅ MetadataExtractor.tsx
- ✅ file-processing.ts
- ✅ ContentAPIManager.ts

**Validation:** No legacy endpoints remain in Content pillar components

---

### ⚠️ Insights Pillar - PENDING
**Status:** ⚠️ **NEEDS MIGRATION**

**Files to Migrate:**
1. `app/(protected)/pillars/insights/page.tsx`
2. `app/(protected)/pillars/insights/components/InsightsDashboard.tsx`
3. `app/(protected)/pillars/insights/components/BusinessAnalysisSection.tsx`
4. `app/(protected)/pillars/insights/components/DataQualitySection.tsx`
5. `app/(protected)/pillars/insights/components/DataInterpretationSection.tsx`
6. `app/(protected)/pillars/insights/components/StructuredDataInsightsSection.tsx`
7. `app/(protected)/pillars/insights/components/UnstructuredDataInsightsSection.tsx`
8. `app/(protected)/pillars/insights/components/InsightsFileSelector.tsx`
9. `app/(protected)/pillars/insights/components/YourDataMash.tsx`
10. `app/(protected)/pillars/insights/components/QualityDashboard.tsx`
11. `app/(protected)/pillars/insights/components/InsightsSummaryDisplay.tsx`
12. `app/(protected)/pillars/insights/components/AARAnalysisSection.tsx`
13. `app/(protected)/pillars/insights/components/CleanupActionsPanel.tsx`
14. `app/(protected)/pillars/insights/components/DataMappingSection.tsx`
15. `app/(protected)/pillars/insights/components/MappingResultsDisplay.tsx`
16. `app/(protected)/pillars/insights/components/PermitProcessingSection.tsx`
17. `app/(protected)/pillars/insights/components/PSOViewer.tsx`

**Intents to Use (from INTENT_MAPPING.md):**
- `analyze_structured_data` - For structured data analysis
- `analyze_unstructured_data` - For unstructured data analysis
- `assess_data_quality` - For data quality assessment
- `interpret_data_self_discovery` - For self-discovery interpretation
- `interpret_data_guided` - For guided interpretation
- `list_files` - For file listing (already migrated pattern)

**Legacy Endpoints to Replace:**
- `/api/v1/insights-solution/analyze` → `analyze_structured_data`
- `/api/v1/insights-solution/get-business-summary` → `analyze_structured_data`
- `/api/v1/insights-solution/analyze-unstructured` → `analyze_unstructured_data`

---

### ⚠️ Journey/Operations Pillar - PENDING
**Status:** ⚠️ **NEEDS MIGRATION**

**Files to Migrate:**
1. `app/(protected)/pillars/journey/page.tsx`
2. `app/(protected)/pillars/journey/page-updated.tsx` (has build error - fix first)
3. `app/(protected)/pillars/journey/components/WizardActive/index.tsx`
4. `app/(protected)/pillars/journey/components/WizardActive/components.tsx`
5. `app/(protected)/pillars/journey/components/WizardActive/core.tsx`
6. `app/(protected)/pillars/journey/components/ProcessBlueprint/index.tsx`
7. `app/(protected)/pillars/journey/components/ProcessBlueprint/core.tsx`
8. `app/(protected)/pillars/journey/components/ProcessBlueprint/components.tsx`
9. `app/(protected)/pillars/journey/components/FileSelector/index.tsx`
10. `app/(protected)/pillars/journey/components/FileSelector/hooks.tsx`
11. `app/(protected)/pillars/journey/components/FileSelector/core.tsx`
12. `app/(protected)/pillars/journey/components/FileSelector/components.tsx`
13. `app/(protected)/pillars/journey/components/CoexistenceBlueprint/index.tsx`
14. `app/(protected)/pillars/journey/components/CoexistenceBlueprint/core.tsx`
15. `app/(protected)/pillars/journey/components/CoexistenceBlueprint/components.tsx`
16. `components/operations/CoexistenceBluprint.tsx` (already uses PlatformState, but check for API calls)

**Intents to Use (from INTENT_MAPPING.md):**
- `analyze_coexistence` - For coexistence analysis
- `create_workflow` - For workflow creation
- `optimize_process` - For process optimization
- `generate_sop` - For SOP generation
- `generate_sop_from_chat` - For SOP from chat
- `sop_chat_message` - For SOP chat
- `create_blueprint` - For blueprint creation

**Legacy Endpoints to Replace:**
- `/api/v1/journey/guide-agent/analyze-user-intent` → `analyze_coexistence` (if coexistence-related)
- `/api/v1/journey/guide-agent/get-journey-guidance` → Check if new intent needed
- `/api/v1/journey/guide-agent/get-conversation-history/{sessionId}` → Use session state retrieval

---

### ⚠️ Outcomes/Business Outcomes Pillar - PARTIAL
**Status:** ⚠️ **HANDLERS DONE, COMPONENTS PENDING**

**Files Migrated:**
- ✅ `app/(protected)/pillars/business-outcomes/page.tsx` (handlers implemented)

**Files to Migrate:**
1. `app/(protected)/pillars/business-outcomes/components/InsightsTab/index.tsx`
2. `app/(protected)/pillars/business-outcomes/components/InsightsTab/components.tsx`
3. `app/(protected)/pillars/business-outcomes/components/InsightsTab/core.tsx`
4. `app/(protected)/pillars/business-outcomes/components/SummaryVisualization.tsx`
5. `app/(protected)/pillars/business-outcomes/components/ArtifactGenerationOptions.tsx`
6. `app/(protected)/pillars/business-outcomes/components/GeneratedArtifactsDisplay.tsx`
7. `app/(protected)/pillars/business-outcomes/components/InsightsEcosystem.tsx`
8. `app/(protected)/pillars/business-outcomes/components/JourneyFrictionRemoval.tsx`
9. `app/(protected)/pillars/business-outcomes/components/DataMashTutorial.tsx`

**Intents to Use (from INTENT_MAPPING.md):**
- `synthesize_outcome` - For outcome synthesis
- `generate_roadmap` - For roadmap generation (✅ handlers done)
- `create_poc` - For POC creation (✅ handlers done)
- `create_blueprint` - For blueprint creation (✅ handlers done)
- `create_solution` - For solution creation

**Legacy Endpoints to Replace:**
- `/api/v1/business-outcomes-solution/pillar-summaries` → `synthesize_outcome` or artifact retrieval
- `/api/v1/business-outcomes-pillar/get-pillar-summaries` → `synthesize_outcome` or artifact retrieval
- `/api/v1/business-outcomes-pillar/get-journey-visualization` → Artifact retrieval

---

### ⚠️ Admin Dashboard - PENDING
**Status:** ⚠️ **NEEDS MIGRATION**

**Files to Migrate:**
1. `app/(protected)/admin/page.tsx`

**Intents to Use:**
- Check admin-specific intents or use artifact retrieval
- May need to use direct API calls for admin operations (to be determined)

**Legacy Endpoints to Replace:**
- TBD - Need to audit admin endpoints

---

### ⚠️ Login Page - PENDING
**Status:** ⚠️ **NEEDS MIGRATION**

**Files to Migrate:**
1. `app/(public)/login/page.tsx`

**Intents to Use:**
- Session creation/authentication intents
- May use Experience Plane endpoints directly (to be determined)

**Legacy Endpoints to Replace:**
- TBD - Need to audit login/auth endpoints

---

### ⚠️ Landing Page - PENDING
**Status:** ⚠️ **NEEDS MIGRATION**

**Files to Migrate:**
1. `app/(protected)/page.tsx` (main landing/dashboard)
2. `app/(protected)/pillars/page.tsx` (pillars overview)

**Intents to Use:**
- Artifact retrieval for dashboard data
- Session state retrieval

**Legacy Endpoints to Replace:**
- TBD - Need to audit landing page endpoints

---

## Migration Pattern (Per Component)

### Step 1: Audit Component
1. Find all `fetch()` calls to `/api/v1/*`
2. Find all `getApiEndpointUrl()` usage
3. Identify which intents to use (from INTENT_MAPPING.md)
4. Check if component uses SessionBoundaryProvider
5. Check if component uses PlatformStateProvider

### Step 2: Migrate Component
1. Import `useSessionBoundary` and `usePlatformState`
2. Replace `fetch()` calls with `submitIntent()`
3. Use canonical intent types from INTENT_MAPPING.md
4. Poll execution status to get results
5. Extract artifacts from execution results
6. Update error handling (user-friendly messages)
7. Remove legacy endpoint calls completely

### Step 3: Validate Component
1. ✅ No legacy endpoints remain
2. ✅ Uses intent-based API
3. ✅ Uses Session-First pattern
4. ✅ Proper error handling
5. ✅ User-friendly error messages

---

## Migration Order (Recommended)

### Priority 1: Fix Build Errors
1. Fix `journey/page-updated.tsx` build error (blocks frontend build)

### Priority 2: Complete Pillar Migrations
2. **Insights Pillar** (17 files)
3. **Journey/Operations Pillar** (16 files)
4. **Outcomes/Business Outcomes Pillar** (9 component files)

### Priority 3: Core Pages
5. **Admin Dashboard** (1 file)
6. **Login Page** (1 file)
7. **Landing Pages** (2 files)

---

## Implementation Strategy

### Per-Pillar Approach
1. **Audit pillar** - Find all legacy endpoints
2. **Migrate pillar** - One component at a time
3. **Validate pillar** - Ensure no legacy endpoints remain
4. **Test pillar** - Functional + architectural validation
5. **Move to next pillar**

### Validation Checklist (Per Component)
- [ ] No `fetch()` calls to `/api/v1/*`
- [ ] No `getApiEndpointUrl()` usage
- [ ] Uses `submitIntent()` from PlatformStateProvider
- [ ] Uses SessionBoundaryProvider for session state
- [ ] Uses canonical intent types from INTENT_MAPPING.md
- [ ] Proper error handling (user-friendly messages)
- [ ] Execution status polling implemented
- [ ] Artifacts extracted from execution results

---

## Estimated Scope

### Files to Migrate
- **Insights Pillar:** ~17 files
- **Journey/Operations Pillar:** ~16 files
- **Outcomes/Business Outcomes Pillar:** ~9 files
- **Admin Dashboard:** ~1 file
- **Login Page:** ~1 file
- **Landing Pages:** ~2 files

**Total:** ~46 files

### Intents to Use
- **Insights:** 6 intents
- **Journey:** 7 intents
- **Outcomes:** 5 intents
- **Admin:** TBD
- **Auth:** TBD

---

## Next Steps

1. **Fix Build Error** - `journey/page-updated.tsx` (blocks frontend build)
2. **Start Insights Pillar Migration** - Begin with main page, then components
3. **Continue with Journey Pillar** - After Insights complete
4. **Complete Outcomes Pillar** - Finish component migrations
5. **Migrate Core Pages** - Admin, Login, Landing

---

**Prepared By:** Development Team  
**Date:** January 25, 2026  
**Status:** ⚠️ **READY FOR SYSTEMATIC MIGRATION**
