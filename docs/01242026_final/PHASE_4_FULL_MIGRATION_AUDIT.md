# Phase 4 Full Migration Audit - 100% Frontend Coverage

**Date:** January 25, 2026  
**Status:** ⚠️ **AUDIT IN PROGRESS**  
**Goal:** Identify ALL components that need migration to intent-based API

---

## Executive Summary

This document provides a comprehensive audit of ALL frontend components to identify what needs migration. The goal is **100% complete and total coverage** - no component should use legacy endpoints.

---

## Audit Methodology

1. **Search for Legacy Patterns:**
   - `fetch()` calls to `/api/v1/*`
   - `getApiEndpointUrl()` usage
   - Direct API manager calls that use legacy endpoints

2. **Check Intent Usage:**
   - Components using `submitIntent()` directly ✅
   - Components using API managers that use intents ✅
   - Components using API managers that use legacy endpoints ⚠️

3. **Validate Session-First:**
   - Components using `useSessionBoundary()` ✅
   - Components using `state.session` from PlatformStateProvider ⚠️ (should use SessionBoundary)

---

## Audit Results by Area

### ✅ Content Pillar - COMPLETE
**Status:** ✅ **100% COMPLETE**

**Files Migrated:** 7 files
- All components use intent-based API
- All components use SessionBoundaryProvider
- No legacy endpoints remain

---

### ⚠️ Insights Pillar - AUDIT NEEDED
**Status:** ⚠️ **AUDIT IN PROGRESS**

**Components Using InsightsAPIManager:**
- `page.tsx` - Uses InsightsAPIManager (✅ already uses intents)
- `BusinessAnalysisSection.tsx` - Uses InsightsAPIManager (✅ already uses intents)
- `DataQualitySection.tsx` - Uses InsightsAPIManager (✅ already uses intents)
- `DataInterpretationSection.tsx` - Uses InsightsAPIManager (✅ already uses intents)
- `YourDataMash.tsx` - Uses InsightsAPIManager (✅ already uses intents)

**Components Using InsightsService (Legacy):**
- Need to check if any components use `InsightsService` from `shared/services/insights/core.ts`

**Action Items:**
1. Audit all Insights components for direct API calls
2. Replace InsightsService usage with InsightsAPIManager (if any)
3. Ensure all components use SessionBoundaryProvider
4. Validate no legacy endpoints remain

---

### ⚠️ Journey/Operations Pillar - AUDIT NEEDED
**Status:** ⚠️ **AUDIT IN PROGRESS**

**Files to Audit:**
- `page.tsx` - Uses JourneyAPIManager (need to check if it uses intents)
- `page-updated.tsx` - Build error fixed, need to audit for API calls
- All component files in `components/` directory

**Action Items:**
1. Audit JourneyAPIManager - does it use intents or legacy endpoints?
2. Audit all Journey components for direct API calls
3. Migrate to intent-based API
4. Ensure all components use SessionBoundaryProvider

---

### ⚠️ Outcomes/Business Outcomes Pillar - PARTIAL
**Status:** ⚠️ **HANDLERS DONE, COMPONENTS NEED AUDIT**

**Files Migrated:**
- ✅ `page.tsx` - Handlers implemented using intents

**Files to Audit:**
- All component files in `components/` directory
- Check if they use BusinessOutcomesAPIManager (which uses legacy endpoints)

**Action Items:**
1. Audit all Outcomes components for direct API calls
2. Replace BusinessOutcomesAPIManager usage with direct intent submission (if needed)
3. Ensure all components use SessionBoundaryProvider

---

### ⚠️ Admin Dashboard - AUDIT NEEDED
**Status:** ⚠️ **AUDIT NEEDED**

**Files to Audit:**
- `page.tsx` - Main admin page
- `components/ControlRoomView.tsx` - Control room view
- `components/DeveloperView.tsx` - Developer view
- `components/BusinessUserView.tsx` - Business user view

**Action Items:**
1. Audit all admin components for API calls
2. Determine if admin operations need special intents or can use artifact retrieval
3. Migrate to intent-based API or artifact retrieval

---

### ⚠️ Login Page - AUDIT NEEDED
**Status:** ⚠️ **AUDIT NEEDED**

**Files to Audit:**
- `app/(public)/login/page.tsx` - Login page
- `components/auth/LoginForm.tsx` - Login form component
- `components/auth/RegisterForm.tsx` - Register form component

**Action Items:**
1. Audit auth components for API calls
2. Determine if auth uses Experience Plane endpoints (acceptable) or needs intent migration
3. Ensure Session-First pattern is used

---

### ⚠️ Landing Pages - AUDIT NEEDED
**Status:** ⚠️ **AUDIT NEEDED**

**Files to Audit:**
- `app/(protected)/page.tsx` - Main landing/dashboard
- `app/(protected)/pillars/page.tsx` - Pillars overview

**Action Items:**
1. Audit landing pages for API calls
2. Migrate to artifact retrieval or intent-based API
3. Ensure Session-First pattern is used

---

## Next Steps

1. **Complete Audit** - Systematically check each area for legacy endpoints
2. **Create Migration Tasks** - Break down into manageable tasks per pillar
3. **Execute Migration** - One pillar at a time, validate after each
4. **Holistic Testing** - Test each pillar across 3 dimensions after migration

---

**Prepared By:** Development Team  
**Date:** January 25, 2026  
**Status:** ⚠️ **AUDIT IN PROGRESS**
