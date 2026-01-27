# Phase 4 Systematic Migration Execution Plan

**Date:** January 25, 2026  
**Status:** ⚠️ **READY FOR EXECUTION**  
**Goal:** 100% complete and total coverage - migrate ALL frontend components

---

## Migration Strategy

**Approach:** One pillar at a time, validate after each, then move to next.

**Order:**
1. ✅ Content Pillar (COMPLETE)
2. Insights Pillar (NEXT)
3. Journey/Operations Pillar
4. Outcomes/Business Outcomes Pillar (handlers done, components pending)
5. Admin Dashboard
6. Login Page
7. Landing Pages

---

## Insights Pillar Migration Plan

### Components with Clear Intent Mappings

**Already Using Intents (via InsightsAPIManager):**
- ✅ `BusinessAnalysisSection.tsx` - Uses `analyze_structured_data` / `analyze_unstructured_data`
- ✅ `DataQualitySection.tsx` - Uses `assess_data_quality`
- ✅ `DataInterpretationSection.tsx` - Uses `interpret_data_self_discovery` / `interpret_data_guided`
- ✅ `YourDataMash.tsx` - Uses `visualize_lineage`
- ✅ `page.tsx` - Uses InsightsAPIManager (already uses intents)

**Need Migration (Using InsightsService - Legacy):**
- ⚠️ `PSOViewer.tsx` - Uses `getPSO()` → Need to determine intent or artifact retrieval
- ⚠️ `DataMappingSection.tsx` - Uses `executeDataMapping()` → May use `map_relationships` intent
- ⚠️ `PermitProcessingSection.tsx` - Uses `processPermit()` → Need to determine intent
- ⚠️ `InsightsDashboard.tsx` - Uses orchestrator, need to check for API calls

**Action Items:**
1. Migrate components using InsightsService to use intent-based API
2. For operations without clear intents, use artifact retrieval or document for future intent creation
3. Ensure all components use SessionBoundaryProvider

---

## Journey/Operations Pillar Migration Plan

### Components to Audit

**Main Files:**
- `page.tsx` - Uses JourneyAPIManager (need to check if it uses intents)
- `page-updated.tsx` - Build error fixed, need to audit

**Component Files:**
- All files in `components/` directory

**Intents Available:**
- `analyze_coexistence`
- `create_workflow`
- `optimize_process`
- `generate_sop`
- `generate_sop_from_chat`
- `sop_chat_message`
- `create_blueprint`

**Action Items:**
1. Audit JourneyAPIManager - does it use intents or legacy endpoints?
2. Migrate all components to use intent-based API
3. Ensure all components use SessionBoundaryProvider

---

## Outcomes/Business Outcomes Pillar Migration Plan

### Status
- ✅ Handlers implemented in `page.tsx`
- ⚠️ Components need audit

**Action Items:**
1. Audit all component files for API calls
2. Migrate to intent-based API or use handlers from page.tsx
3. Ensure all components use SessionBoundaryProvider

---

## Admin Dashboard Migration Plan

**Files to Audit:**
- `page.tsx`
- `components/ControlRoomView.tsx`
- `components/DeveloperView.tsx`
- `components/BusinessUserView.tsx`

**Action Items:**
1. Audit all admin components
2. Determine if admin operations need special intents or artifact retrieval
3. Migrate to intent-based API

---

## Login Page Migration Plan

**Files to Audit:**
- `app/(public)/login/page.tsx`
- `components/auth/LoginForm.tsx`
- `components/auth/RegisterForm.tsx`

**Action Items:**
1. Audit auth components
2. Determine if auth uses Experience Plane endpoints (acceptable) or needs intent migration
3. Ensure Session-First pattern

---

## Landing Pages Migration Plan

**Files to Audit:**
- `app/(protected)/page.tsx`
- `app/(protected)/pillars/page.tsx`

**Action Items:**
1. Audit landing pages
2. Migrate to artifact retrieval or intent-based API
3. Ensure Session-First pattern

---

## Execution Checklist (Per Component)

- [ ] Audit component for legacy endpoints
- [ ] Identify correct intent type (from INTENT_MAPPING.md)
- [ ] Replace `fetch()` calls with `submitIntent()`
- [ ] Add SessionBoundaryProvider usage
- [ ] Add PlatformStateProvider usage
- [ ] Implement execution status polling
- [ ] Extract artifacts from execution results
- [ ] Add proper error handling
- [ ] Remove legacy endpoint calls completely
- [ ] Validate no legacy endpoints remain

---

## Next Steps

1. **Start with Insights Pillar** - Migrate 4 components using InsightsService
2. **Continue with Journey Pillar** - Audit and migrate all components
3. **Complete Outcomes Pillar** - Finish component migrations
4. **Migrate Core Pages** - Admin, Login, Landing

---

**Prepared By:** Development Team  
**Date:** January 25, 2026  
**Status:** ⚠️ **READY FOR SYSTEMATIC EXECUTION**
